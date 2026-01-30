"""
Management command: Bulk import HUD ZIP-to-CBSA crosswalk CSV.

WHY:
    - Fast, simple import of entire HUD crosswalk file into raw table
    - No FK validation overhead = blazing fast bulk insert
    - Preserves all HUD data including micro areas and ratios

HOW:
    - Read CSV in chunks
    - Build model instances
    - Bulk create in batches of 1000
    - Truncate old data first (fresh quarterly reload)

DOCS REVIEWED:
    - Django bulk_create: https://docs.djangoproject.com/en/5.2/ref/models/querysets/#bulk-create
    - Python csv module: https://docs.python.org/3/library/csv.html
"""
from __future__ import annotations

import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import List

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models.model_co_geoAssumptions import HUDZIPCBSACrosswalk


class Command(BaseCommand):
    """Bulk import HUD ZIP-CBSA crosswalk CSV into HUDZIPCBSACrosswalk table."""

    help = "Fast bulk import of HUD ZIP_CBSA CSV (truncates existing data)"

    def add_arguments(self, parser) -> None:
        """Accept command-line options for CSV location and batch sizing."""

        default_csv = (
            Path(settings.BASE_DIR) / "z.Admin" / "DataUploads" / "ZIP_CBSA_062025.csv"
        )
        parser.add_argument(
            "--csv-path",
            default=str(default_csv),
            help="Path to the HUD ZIP_CBSA CSV file.",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=1000,
            help="How many rows to insert per batch (default 1000).",
        )
        parser.add_argument(
            "--skip-truncate",
            action="store_true",
            help="Skip truncating existing data (append mode).",
        )

    def handle(self, *args, **options) -> None:
        """Main entry point: truncate old data, read CSV, bulk insert."""

        csv_path = Path(options["csv_path"])
        batch_size = int(options["batch_size"])
        skip_truncate = options["skip_truncate"]

        if not csv_path.exists():
            raise CommandError(f"CSV file not found: {csv_path}")

        self.stdout.write(
            self.style.NOTICE(
                f"Starting HUD ZIP-CBSA import from {csv_path} (batch size {batch_size})"
            )
        )
        self.stdout.flush()

        # WHAT: Clear existing data for fresh quarterly reload
        # WHY: HUD releases full snapshots, not incremental updates
        # HOW: Delete all rows unless --skip-truncate flag is set
        if not skip_truncate:
            old_count = HUDZIPCBSACrosswalk.objects.count()
            self.stdout.write(self.style.WARNING(f"Truncating {old_count} existing records..."))
            self.stdout.flush()
            HUDZIPCBSACrosswalk.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Truncate complete."))
            self.stdout.flush()

        # WHAT: Read CSV and bulk insert in batches
        # WHY: Memory-efficient processing of large files
        # HOW: Accumulate records, bulk_create when batch is full
        total_created = 0
        batch_num = 0
        pending: List[HUDZIPCBSACrosswalk] = []

        self.stdout.write(self.style.NOTICE("Reading CSV and importing..."))
        self.stdout.flush()

        with csv_path.open("r", newline="", encoding="utf-8-sig") as infile:
            reader = csv.DictReader(infile)
            
            for line_num, row in enumerate(reader, start=2):
                # WHAT: Parse CSV row into model instance
                # WHY: Build objects for bulk_create
                # HOW: Read fields directly from CSV columns
                try:
                    obj = HUDZIPCBSACrosswalk(
                        zip_code=(row.get("ZIP") or "").strip(),
                        cbsa_code=(row.get("CBSA") or "").strip() or None,
                        city=(row.get("USPS_ZIP_PREF_CITY") or "").strip() or None,
                        state_code=(row.get("USPS_ZIP_PREF_STATE") or "").strip().upper(),
                        res_ratio=self._safe_decimal(row.get("RES_RATIO", "0")),
                        bus_ratio=self._safe_decimal(row.get("BUS_RATIO", "0")),
                        oth_ratio=self._safe_decimal(row.get("OTH_RATIO", "0")),
                        tot_ratio=self._safe_decimal(row.get("TOT_RATIO", "0")),
                    )
                    
                    # WHAT: Skip rows with missing critical data
                    # WHY: ZIP and state are required for useful records
                    # HOW: Check if zip_code and state_code are non-empty
                    if not obj.zip_code or not obj.state_code:
                        self.stdout.write(
                            self.style.WARNING(
                                f"[Line {line_num}] Missing ZIP or state; skipping."
                            )
                        )
                        continue
                    
                    pending.append(obj)
                    
                    # WHAT: Bulk insert when batch is full
                    # WHY: Efficient database writes in chunks
                    # HOW: bulk_create and clear pending list
                    if len(pending) >= batch_size:
                        batch_num += 1
                        self._insert_batch(pending, batch_num)
                        total_created += len(pending)
                        pending.clear()
                
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"[Line {line_num}] Error parsing row: {e}"
                        )
                    )
                    continue

        # WHAT: Insert any remaining records in final partial batch
        # WHY: Don't lose last <batch_size rows
        # HOW: Same bulk_create logic
        if pending:
            batch_num += 1
            self._insert_batch(pending, batch_num)
            total_created += len(pending)

        self.stdout.write(
            self.style.SUCCESS(
                f"\nImport complete! Created {total_created} records in {batch_num} batches."
            )
        )

    # ------------------------------------------------------------------ helpers --

    def _safe_decimal(self, value: str | None) -> Decimal:
        """
        WHAT: Convert CSV string to Decimal, default to 0 on error
        WHY: HUD ratio columns can have formatting issues
        RETURNS: Decimal value or Decimal('0.0')
        """
        try:
            return Decimal(value or "0")
        except (InvalidOperation, TypeError, ValueError):
            return Decimal("0.0")

    @transaction.atomic
    def _insert_batch(self, batch: List[HUDZIPCBSACrosswalk], batch_num: int) -> None:
        """
        WHAT: Bulk insert a batch of records
        WHY: Fast atomic database write
        HOW: Django bulk_create with ignore_conflicts for safety
        """
        HUDZIPCBSACrosswalk.objects.bulk_create(
            batch,
            batch_size=len(batch),
            ignore_conflicts=False,  # Fail loudly on issues
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Batch {batch_num}: Inserted {len(batch)} records"
            )
        )
        self.stdout.flush()

