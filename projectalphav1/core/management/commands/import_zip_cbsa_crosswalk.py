"""
Management command: Load HUD ZIP→CBSA (MSA) crosswalk CSV into ZIPReference.

WHY:
    - Broker assignment + reporting flows need every ZIP tied to its MSA so we can
      aggregate assets by market. HUD publishes a quarterly CSV (ZIP_CBSA_*.csv).
    - This command ingests that CSV, resolves State + MSA foreign keys, and writes
      or updates `ZIPReference` records in manageable batches.

DOCS REVIEWED:
    - Django bulk operations: https://docs.djangoproject.com/en/5.2/topics/db/queries/#bulk-operations
    - Python csv module: https://docs.python.org/3/library/csv.html
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Dict, Iterable, List
import csv

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models.model_co_geoAssumptions import (
    ZIPReference,
    MSAReference,
    StateReference,
)


@dataclass
class ZipCrosswalkRow:
    """Structured view of the single “best” row for a ZIP code.

    Fields:
        zip_code: Canonical 5-digit ZIP.
        cbsa_code: Five digit CBSA / MSA code (string to preserve leading zeros).
        city: Preferred USPS city name.
        state_code: Two-letter postal abbreviation.
        tot_ratio: Decimal share of the ZIP assigned to this CBSA (for logging/debug).
    """

    zip_code: str
    cbsa_code: str | None
    city: str | None
    state_code: str
    tot_ratio: Decimal


class Command(BaseCommand):
    """Import HUD ZIP→CBSA crosswalk CSV into ZIPReference."""

    help = (
        "Load the HUD ZIP_CBSA CSV, resolve State/MSA FKs, "
        "and bulk update ZIPReference in batches."
    )

    def add_arguments(self, parser) -> None:
        """Accept command-line options for CSV location and batch sizing."""

        default_csv = (
            Path(settings.BASE_DIR) / "z.Admin" / "DataUploads" / "ZIP_CBSA_062025.csv"
        )
        parser.add_argument(
            "--csv-path",
            default=str(default_csv),
            help="Path to the HUD ZIP→CBSA CSV export.",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=500,
            help="How many ZIP rows to persist per DB batch (default 500).",
        )

    def handle(self, *args, **options) -> None:
        """Main entry point: parse CSV, resolve references, and persist batches."""

        csv_path = Path(options["csv_path"])
        batch_size = int(options["batch_size"])
        if not csv_path.exists():
            raise CommandError(f"CSV file not found: {csv_path}")

        self.stdout.write(
            self.style.NOTICE(
                f"Loading ZIP→CBSA crosswalk from {csv_path} (batch size {batch_size})"
            )
        )

        best_rows = self._collect_best_rows(csv_path)
        self.stdout.write(
            self.style.NOTICE(
                f"Best-row selection complete: {len(best_rows)} unique ZIPs discovered."
            )
        )

        state_map = self._build_state_map()
        msa_map = self._build_msa_map(best_rows.values())

        stats = defaultdict(int)
        pending: List[ZipCrosswalkRow] = []

        for row in best_rows.values():
            pending.append(row)
            if len(pending) >= batch_size:
                self._process_batch(pending, state_map, msa_map, stats)
                pending.clear()

        if pending:
            self._process_batch(pending, state_map, msa_map, stats)

        self.stdout.write(
            self.style.SUCCESS(
                (
                    "Import complete — "
                    f"created {stats['created']} ZIPs, "
                    f"updated {stats['updated']} ZIPs, "
                    f"skipped {stats['skipped']} (missing refs), "
                    f"{stats['missing_state']} missing states, "
                    f"{stats['missing_msa']} missing MSAs."
                )
            )
        )

    # ------------------------------------------------------------------ helpers --

    def _collect_best_rows(self, csv_path: Path) -> Dict[str, ZipCrosswalkRow]:
        """Read the CSV once and keep only the dominant CBSA record per ZIP."""

        best_rows: Dict[str, ZipCrosswalkRow] = {}

        with csv_path.open("r", newline="", encoding="utf-8-sig") as infile:
            reader = csv.DictReader(infile)
            for line_number, raw in enumerate(reader, start=2):
                zip_code = (raw.get("ZIP") or "").strip()
                cbsa_code = (raw.get("CBSA") or "").strip() or None
                city = (raw.get("USPS_ZIP_PREF_CITY") or "").strip() or None
                state_code = (raw.get("USPS_ZIP_PREF_STATE") or "").strip().upper()
                ratio = self._safe_decimal(raw.get("TOT_RATIO", "0"))

                if not zip_code or not state_code:
                    self.stdout.write(
                        self.style.WARNING(
                            f"[line {line_number}] Missing ZIP or state; skipping row."
                        )
                    )
                    continue

                # HUD files already present 5-digit ZIPs; keep exactly as provided.
                row = ZipCrosswalkRow(
                    zip_code=zip_code,
                    cbsa_code=cbsa_code,
                    city=city,
                    state_code=state_code,
                    tot_ratio=ratio,
                )

                previous = best_rows.get(zip_code)
                if previous is None or ratio > previous.tot_ratio:
                    best_rows[zip_code] = row

        return best_rows

    def _safe_decimal(self, value: str | None) -> Decimal:
        """Convert CSV ratio strings into Decimal, defaulting to 0 on failure."""

        try:
            return Decimal(value or "0")
        except (InvalidOperation, TypeError):
            return Decimal("0")

    def _build_state_map(self) -> Dict[str, StateReference]:
        """Preload all StateReference rows keyed by their postal code."""

        states = StateReference.objects.all()
        return {state.state_code.upper(): state for state in states}

    def _build_msa_map(
        self, rows: Iterable[ZipCrosswalkRow]
    ) -> Dict[str, MSAReference]:
        """Prefetch the MSAReference rows needed for this import."""

        cbsa_codes = {row.cbsa_code for row in rows if row.cbsa_code}
        if not cbsa_codes:
            return {}

        msa_qs = MSAReference.objects.filter(msa_code__in=cbsa_codes)
        return {msa.msa_code: msa for msa in msa_qs}

    @transaction.atomic
    def _process_batch(
        self,
        batch: List[ZipCrosswalkRow],
        state_map: Dict[str, StateReference],
        msa_map: Dict[str, MSAReference],
        stats: Dict[str, int],
    ) -> None:
        """Insert or update a slice of ZIP rows in a single atomic transaction."""

        zip_codes = [row.zip_code for row in batch]
        existing = ZIPReference.objects.select_related("state", "msa").filter(
            zip_code__in=zip_codes
        )
        existing_map = {zip_ref.zip_code: zip_ref for zip_ref in existing}

        to_create: List[ZIPReference] = []
        to_update: List[ZIPReference] = []

        for row in batch:
            state = state_map.get(row.state_code)
            if not state:
                stats["missing_state"] += 1
                stats["skipped"] += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"[{row.zip_code}] State '{row.state_code}' not found; skipping."
                    )
                )
                continue

            msa = msa_map.get(row.cbsa_code) if row.cbsa_code else None
            if row.cbsa_code and not msa:
                stats["missing_msa"] += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"[{row.zip_code}] CBSA '{row.cbsa_code}' missing in MSAReference."
                    )
                )

            current = existing_map.get(row.zip_code)
            if current:
                if self._apply_changes(current, state, msa, row.city):
                    to_update.append(current)
            else:
                to_create.append(
                    ZIPReference(
                        zip_code=row.zip_code,
                        state=state,
                        msa=msa,
                        city_name=row.city,
                    )
                )

        if to_create:
            ZIPReference.objects.bulk_create(to_create, batch_size=len(to_create))
        if to_update:
            ZIPReference.objects.bulk_update(
                to_update, ["msa", "state", "city_name"], batch_size=len(to_update)
            )

        stats["created"] += len(to_create)
        stats["updated"] += len(to_update)

        self.stdout.write(
            self.style.SUCCESS(
                (
                    f"Batch processed — created {len(to_create)}, "
                    f"updated {len(to_update)}, cumulative "
                    f"{stats['created']} created / {stats['updated']} updated."
                )
            )
        )

    def _apply_changes(
        self,
        zip_obj: ZIPReference,
        state: StateReference,
        msa: MSAReference | None,
        city: str | None,
    ) -> bool:
        """Apply field updates to an existing ZIPReference, returning True if mutated."""

        changed = False
        if zip_obj.state_id != state.id:
            zip_obj.state = state
            changed = True
        if zip_obj.msa_id != (msa.id if msa else None):
            zip_obj.msa = msa
            changed = True
        if city and zip_obj.city_name != city:
            zip_obj.city_name = city
            changed = True
        return changed

