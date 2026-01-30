import csv
import logging
import os
from typing import Dict, List

from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.utils import timezone

from core.models import AssetIdHub


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Import AssetIdHub master backfill CSV into AssetIdHub (upsert by id / sellertape_id)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            required=True,
            help="Path to CSV file (relative to manage.py or absolute)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Run import without saving to database",
        )

    def handle(self, *args, **options):
        file_path = options["file"]
        dry_run = options["dry_run"]

        if not os.path.exists(file_path):
            raise CommandError(f"File not found: {file_path}")

        prefix = "[DRY RUN] " if dry_run else ""
        self.stdout.write(self.style.SUCCESS(f"{prefix}Starting AssetIdHub master import"))
        self.stdout.write(f"Reading from: {file_path}")

        rows = self._read_csv(file_path)
        if not rows:
            self.stdout.write(self.style.WARNING("No rows found in CSV file"))
            return

        self.stdout.write(f"Found {len(rows)} rows to process")

        stats = {
            "processed": 0,
            "created": 0,
            "updated": 0,
            "unchanged": 0,
            "skipped_invalid": 0,
            "errors": 0,
        }

        for row in rows:
            try:
                result = self._process_row(row, dry_run)
                if result not in stats:
                    result = "errors"
                stats[result] += 1
                stats["processed"] += 1
            except Exception as exc:
                stats["errors"] += 1
                logger.exception("Error processing AssetIdHub row id=%s", row.get("id"))
                self.stdout.write(
                    self.style.ERROR(
                        f"  ERROR: id={row.get('id')} sellertape_id={row.get('sellertape_id')}: {exc}"
                    )
                )

        self.stdout.write(self.style.SUCCESS("\n=== AssetIdHub Master Import Complete ==="))
        self.stdout.write(f"Processed:        {stats['processed']}")
        self.stdout.write(f"Created:          {stats['created']}")
        self.stdout.write(f"Updated:          {stats['updated']}")
        self.stdout.write(f"Unchanged:        {stats['unchanged']}")
        self.stdout.write(f"Skipped (invalid): {stats['skipped_invalid']}")
        self.stdout.write(f"Errors:           {stats['errors']}")

        if dry_run:
            self.stdout.write(self.style.WARNING("\n[DRY RUN] No changes were saved to database"))
        else:
            if stats["created"] > 0:
                try:
                    self._sync_pk_sequence()
                except Exception as exc:
                    logger.exception("Failed to sync AssetIdHub PK sequence: %s", exc)
                    self.stdout.write(
                        self.style.WARNING(
                            "Warning: Failed to sync AssetIdHub PK sequence; future inserts may need attention."
                        )
                    )

    def _read_csv(self, file_path: str) -> List[Dict[str, str]]:
        encodings = ["utf-8", "utf-8-sig", "cp1252", "latin1"]

        last_error = None
        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding, newline="") as csvfile:
                    reader = csv.DictReader(csvfile)
                    if not reader.fieldnames:
                        raise CommandError("CSV file has no header row")

                    required = {"id", "sellertape_id", "servicer_id"}
                    missing = required - set(reader.fieldnames)
                    if missing:
                        raise CommandError(
                            f"CSV must include columns {sorted(required)}; missing {sorted(missing)}. "
                            f"Found: {reader.fieldnames}"
                        )

                    rows: List[Dict[str, str]] = []
                    for row in reader:
                        rows.append(row)

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Successfully read {len(rows)} rows using {encoding} encoding"
                        )
                    )
                    return rows
            except UnicodeDecodeError as exc:
                last_error = exc
                continue
            except Exception as exc:
                last_error = exc
                continue

        if last_error:
            raise CommandError(f"Failed to read CSV: {last_error}")
        return []

    def _parse_int_id(self, raw_id: str):
        if raw_id is None:
            return None
        value = str(raw_id).strip()
        if not value:
            return None
        try:
            return int(value)
        except ValueError:
            logger.warning("Invalid id value in CSV: %r", raw_id)
            return None

    def _process_row(self, row: Dict[str, str], dry_run: bool) -> str:
        raw_id = row.get("id")
        pk = self._parse_int_id(raw_id)

        sellertape_id = (row.get("sellertape_id") or "").strip() or None
        servicer_id = (row.get("servicer_id") or "").strip() or None

        if pk is None and sellertape_id is None:
            logger.warning("Skipping row with no id and no sellertape_id: %s", row)
            return "skipped_invalid"

        if pk is not None:
            try:
                hub = AssetIdHub.objects.get(pk=pk)
            except AssetIdHub.DoesNotExist:
                if dry_run:
                    logger.info(
                        "[DRY RUN] Would create AssetIdHub(id=%s, sellertape_id=%r, servicer_id=%r)",
                        pk,
                        sellertape_id,
                        servicer_id,
                    )
                    return "created"

                hub = AssetIdHub(
                    id=pk,
                    sellertape_id=sellertape_id,
                    servicer_id=servicer_id,
                )
                hub.save(force_insert=True)
                logger.info(
                    "Created AssetIdHub(id=%s, sellertape_id=%r, servicer_id=%r)",
                    pk,
                    sellertape_id,
                    servicer_id,
                )
                return "created"
            except AssetIdHub.MultipleObjectsReturned:
                logger.warning("Multiple AssetIdHub rows found for id=%s; skipping", pk)
                return "skipped_invalid"

            changed_fields = []

            if sellertape_id and hub.sellertape_id != sellertape_id:
                hub.sellertape_id = sellertape_id
                changed_fields.append("sellertape_id")

            if servicer_id and hub.servicer_id != servicer_id:
                hub.servicer_id = servicer_id
                changed_fields.append("servicer_id")

            if not changed_fields:
                return "unchanged"

            hub.updated_at = timezone.now()
            changed_fields.append("updated_at")

            if dry_run:
                logger.info(
                    "[DRY RUN] Would update AssetIdHub(id=%s) fields %s",
                    hub.id,
                    ",".join(changed_fields),
                )
                return "updated"

            hub.save(update_fields=changed_fields)
            logger.info(
                "Updated AssetIdHub(id=%s) fields %s",
                hub.id,
                ",".join(changed_fields),
            )
            return "updated"

        try:
            hub = AssetIdHub.objects.get(sellertape_id=sellertape_id)
        except AssetIdHub.DoesNotExist:
            if dry_run:
                logger.info(
                    "[DRY RUN] Would create AssetIdHub(sellertape_id=%r, servicer_id=%r)",
                    sellertape_id,
                    servicer_id,
                )
                return "created"

            hub = AssetIdHub.objects.create(
                sellertape_id=sellertape_id,
                servicer_id=servicer_id,
            )
            logger.info(
                "Created AssetIdHub(id=%s, sellertape_id=%r, servicer_id=%r)",
                hub.id,
                sellertape_id,
                servicer_id,
            )
            return "created"
        except AssetIdHub.MultipleObjectsReturned:
            logger.warning(
                "Multiple AssetIdHub rows found for sellertape_id=%r; skipping", sellertape_id
            )
            return "skipped_invalid"

        changed_fields = []

        if servicer_id and hub.servicer_id != servicer_id:
            hub.servicer_id = servicer_id
            changed_fields.append("servicer_id")

        if not changed_fields:
            return "unchanged"

        hub.updated_at = timezone.now()
        changed_fields.append("updated_at")

        if dry_run:
            logger.info(
                "[DRY RUN] Would update AssetIdHub(id=%s) fields %s",
                hub.id,
                ",".join(changed_fields),
            )
            return "updated"

        hub.save(update_fields=changed_fields)
        logger.info(
            "Updated AssetIdHub(id=%s) fields %s",
            hub.id,
            ",".join(changed_fields),
        )
        return "updated"

    def _sync_pk_sequence(self) -> None:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT setval(pg_get_serial_sequence(%s, %s), (SELECT COALESCE(MAX(id), 1) FROM core_assetidhub))",
                ["core_assetidhub", "id"],
            )
