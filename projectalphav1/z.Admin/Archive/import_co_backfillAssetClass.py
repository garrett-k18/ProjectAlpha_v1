import csv
import logging
import os
from typing import Dict, List

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from core.models.model_co_assetIdHub import AssetIdHub, AssetDetails

# WHAT: Setup logging for the import command
# WHY: Track progress and errors during the backfill process
# HOW: Use the standard logging library with a module-level logger
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """
    WHAT: Management command to backfill Asset Class field from a CSV file.
    WHY: User needs to update Asset Class for existing assets in the hub.
    HOW: Reads CSV with Asset Hub ID and Asset Class, updates core.AssetDetails.
    """
    
    help = "Import Asset Class backfill CSV into AssetDetails (mapped by AssetIdHub ID)."

    def add_arguments(self, parser):
        # WHAT: CSV file path argument
        # WHY: User specifies the source of truth for the backfill
        parser.add_argument(
            "--file",
            type=str,
            required=True,
            help="Path to CSV file (relative to manage.py or absolute)",
        )
        # WHAT: Dry-run flag
        # WHY: Allow testing the import without committing changes to the DB
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Run import without saving to database",
        )

    def handle(self, *args, **options):
        """Main execution logic for the command."""
        file_path = options["file"]
        dry_run = options["dry_run"]

        # WHAT: Validate file existence
        # WHY: Fail early if the provided path is incorrect
        if not os.path.exists(file_path):
            raise CommandError(f"File not found: {file_path}")

        prefix = "[DRY RUN] " if dry_run else ""
        self.stdout.write(self.style.SUCCESS(f"{prefix}Starting Asset Class backfill import"))
        self.stdout.write(f"Reading from: {file_path}")

        # WHAT: Read and parse the CSV
        # HOW: Use helper method _read_csv to handle encoding and header validation
        rows = self._read_csv(file_path)
        if not rows:
            self.stdout.write(self.style.WARNING("No rows found in CSV file"))
            return

        self.stdout.write(f"Found {len(rows)} rows to process")

        stats = {
            "processed": 0,
            "updated": 0,
            "created": 0,
            "unchanged": 0,
            "skipped_invalid": 0,
            "errors": 0,
        }

        # WHAT: Process each row in the CSV
        # WHY: Update AssetDetails records individually while tracking statistics
        for row in rows:
            try:
                result = self._process_row(row, dry_run)
                if result not in stats:
                    result = "errors"
                stats[result] += 1
                stats["processed"] += 1
            except Exception as exc:
                stats["errors"] += 1
                logger.exception("Error processing row for asset_id=%s", row.get("Asset Hub ID"))
                self.stdout.write(
                    self.style.ERROR(
                        f"  ERROR: Asset Hub ID={row.get('Asset Hub ID')}: {exc}"
                    )
                )

        # WHAT: Final summary report
        # WHY: Provide feedback on the operation's outcome
        self.stdout.write(self.style.SUCCESS("\n=== Asset Class Backfill Complete ==="))
        self.stdout.write(f"Processed:        {stats['processed']}")
        self.stdout.write(f"Created Details:  {stats['created']}")
        self.stdout.write(f"Updated:          {stats['updated']}")
        self.stdout.write(f"Unchanged:        {stats['unchanged']}")
        self.stdout.write(f"Skipped (invalid): {stats['skipped_invalid']}")
        self.stdout.write(f"Errors:           {stats['errors']}")

        if dry_run:
            self.stdout.write(self.style.WARNING("\n[DRY RUN] No changes were saved to database"))

    def _read_csv(self, file_path: str) -> List[Dict[str, str]]:
        """Reads CSV file and validates headers."""
        # WHAT: Handle common CSV encodings
        # WHY: CSVs from Excel or different OSs might have different encodings
        encodings = ["utf-8", "utf-8-sig", "cp1252", "latin1"]

        last_error = None
        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding, newline="") as csvfile:
                    reader = csv.DictReader(csvfile)
                    if not reader.fieldnames:
                        raise CommandError("CSV file has no header row")

                    # WHAT: Map possible headers (flexible for SQL output vs manual CSV)
                    # WHY: SQL query used "Asset Hub ID", manual CSV might use "asset_id"
                    fieldnames = [f.strip() for f in reader.fieldnames]
                    
                    # Target required columns
                    hub_id_col = next((f for f in fieldnames if f.lower() in ["asset hub id", "asset_id", "assetidhub"]), None)
                    class_col = next((f for f in fieldnames if f.lower() in ["asset class", "asset_class", "class"]), None)

                    if not hub_id_col or not class_col:
                        raise CommandError(
                            f"CSV must include columns for 'Asset Hub ID' and 'Asset Class'. "
                            f"Found: {reader.fieldnames}"
                        )

                    rows: List[Dict[str, str]] = []
                    for row in reader:
                        # Normalize keys for processing
                        normalized_row = {
                            "asset_id": row[hub_id_col].strip(),
                            "asset_class": row[class_col].strip().upper()
                        }
                        rows.append(normalized_row)

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

    def _process_row(self, row: Dict[str, str], dry_run: bool) -> str:
        """Processes a single row and updates the AssetDetails model."""
        raw_id = row.get("asset_id")
        raw_class = row.get("asset_class")

        # WHAT: Validate asset_id
        # WHY: Must be an integer to look up AssetIdHub
        if not raw_id:
            return "skipped_invalid"
        
        try:
            asset_id = int(raw_id)
        except ValueError:
            logger.warning("Invalid Asset Hub ID: %s", raw_id)
            return "skipped_invalid"

        # WHAT: Validate asset_class against model choices
        # WHY: Ensure data integrity in the database
        # HOW: Map common abbreviations like 'PERF' to canonical 'PERFORMING'
        class_mapping = {
            "PERF": "PERFORMING",
            "PERF.": "PERFORMING",
            "PERFORMING": "PERFORMING",
            "NPL": "NPL",
            "REO": "REO",
        }
        
        normalized_class = class_mapping.get(raw_class)

        valid_classes = {choice[0] for choice in AssetDetails.AssetClass.choices}
        if not normalized_class or normalized_class not in valid_classes:
            logger.warning("Invalid Asset Class '%s' for ID %s. Skipping.", raw_class, asset_id)
            return "skipped_invalid"

        # Use the mapped canonical name
        final_class = normalized_class

        # WHAT: Lookup or Create AssetDetails
        # WHY: Some hubs might not have a details row yet
        try:
            hub = AssetIdHub.objects.get(id=asset_id)
        except AssetIdHub.DoesNotExist:
            logger.warning("AssetIdHub ID %s does not exist; skipping", asset_id)
            return "skipped_invalid"

        try:
            details = AssetDetails.objects.get(asset=hub)
            created = False
        except AssetDetails.DoesNotExist:
            details = AssetDetails(asset=hub)
            created = True

        # WHAT: Check if change is needed
        # WHY: Avoid redundant database writes
        if not created and details.asset_class == final_class:
            return "unchanged"

        # WHAT: Perform the update/save
        # HOW: Set the field and save (unless dry-run)
        if not dry_run:
            details.asset_class = final_class
            details.save()
            
            if created:
                logger.info("Created AssetDetails for ID %s with class %s", asset_id, final_class)
                return "created"
            else:
                logger.info("Updated AssetDetails for ID %s: asset_class=%s", asset_id, final_class)
                return "updated"
        else:
            if created:
                logger.info("[DRY RUN] Would create AssetDetails for ID %s with class %s", asset_id, final_class)
                return "created"
            else:
                logger.info("[DRY RUN] Would update AssetDetails for ID %s to class %s", asset_id, final_class)
                return "updated"
