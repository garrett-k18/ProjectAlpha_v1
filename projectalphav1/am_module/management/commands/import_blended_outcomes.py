"""Django management command for importing `BlendedOutcomeModel` rows from CSV.

Docs reviewed:
- Custom management commands: https://docs.djangoproject.com/en/stable/howto/custom-management-commands/
- Model field value conversion: https://docs.djangoproject.com/en/stable/ref/models/instances/#django.db.models.Model
"""

from __future__ import annotations

import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple
import logging  # WHAT: Logging module used for debug-level runtime visibility.

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Field

from am_module.models.boarded_data import BlendedOutcomeModel
from core.models.model_co_assetIdHub import AssetIdHub

logger = logging.getLogger(__name__)  # WHAT: Module-level logger for structured logging support.


NULL_TOKENS = {"", "na", "n/a", "null", "none", "nil"}  # WHAT: Accepted blank tokens for CSV values.
TRUTHY_TOKENS = {"true", "t", "yes", "y", "1"}  # WHAT: Tokens that map to boolean True.
FALSY_TOKENS = {"false", "f", "no", "n", "0"}  # WHAT: Tokens that map to boolean False.
DATE_FORMATS = (
    "%Y-%m-%d",  # WHAT: ISO format.
    "%m/%d/%Y",  # WHAT: US format with four-digit year.
    "%m-%d-%Y",  # WHAT: US hyphen format.
    "%Y/%m/%d",  # WHAT: ISO with slashes.
    "%m/%d/%y",  # WHAT: US format with two-digit year.
    "%Y%m%d",  # WHAT: Compact ISO format.
)
ASSET_ID_COLUMNS = (
    "asset_hub_id",  # WHAT: Primary header used internally.
    "asset_hub",  # WHAT: Alternate header used in legacy exports.
    "assetid",  # WHAT: Common shorthand header.
    "asset_id",  # WHAT: Snake case alternate header.
    "assetidhub",  # WHAT: Alias used in FLC33_36_38 Model.csv exports.
)


def _is_blank(value: Any) -> bool:
    """Check whether a CSV token should be treated as null."""

    # WHAT: None always qualifies as blank.
    if value is None:
        return True
    # WHAT: Normalize string and compare against null token set.
    return str(value).strip().lower() in NULL_TOKENS


def _clean_numeric_token(raw: str) -> str:
    """Remove currency/percent formatting to stabilize numeric parsing."""

    token = str(raw).strip()  # WHAT: Normalize whitespace.
    token = token.replace("$", "")  # WHY: Strip currency symbol.
    token = token.replace(",", "")  # WHY: Remove thousands separators.
    token = token.replace("%", "")  # WHY: Percent symbol not parseable by Decimal.
    token = token.replace("(", "-")  # WHY: Parenthesis denotes negative numbers in accounting exports.
    token = token.replace(")", "")  # WHAT: Remove closing parenthesis after negation.
    return token  # WHERE: Returned value feeds numeric converters below.


def _convert_integer(value: Any) -> Optional[int]:
    """Convert raw token into Python int (fault-tolerant)."""

    if _is_blank(value):  # WHAT: Blank values stay None for nullable fields.
        return None
    token = _clean_numeric_token(value)  # WHAT: Normalize formatting before parsing.
    try:
        return int(float(token))  # WHY: float() gracefully handles "123.0" or scientific notation.
    except (TypeError, ValueError, OverflowError):
        return None  # HOW: Swallow conversion errors to keep import resilient.


def _convert_decimal(value: Any) -> Optional[Decimal]:
    """Convert raw token into Decimal (precision-safe for money fields)."""

    if _is_blank(value):  # WHAT: Preserve null semantics for empty cells.
        return None
    token = _clean_numeric_token(value)  # WHY: Remove formatting prior to Decimal conversion.
    try:
        return Decimal(token)  # HOW: Use Decimal to avoid floating point rounding issues.
    except (InvalidOperation, ValueError, TypeError):
        return None  # WHAT: Any invalid numeric string yields None.


def _convert_boolean(value: Any) -> Optional[bool]:
    """Convert raw token into boolean, tolerant of numbers/text."""

    if _is_blank(value):  # WHAT: Null stays None for optional booleans.
        return None
    token = str(value).strip().lower()  # WHAT: Normalize to lowercase string.
    if token in TRUTHY_TOKENS:  # WHY: Recognize standard truthy tokens.
        return True
    if token in FALSY_TOKENS:  # WHY: Recognize standard falsy tokens.
        return False
    try:
        numeric = float(_clean_numeric_token(token))  # WHAT: Interpret numeric strings like "0" / "1".
    except (TypeError, ValueError):
        return None  # HOW: Unknown tokens fall back to None.
    return numeric != 0.0  # WHY: Non-zero numeric values considered True.


def _convert_date(value: Any) -> Optional[datetime.date]:
    """Convert raw token into `date`, supporting multiple vendor formats."""

    if _is_blank(value):  # WHAT: Null values remain None to satisfy nullable fields.
        return None
    token = str(value).strip()  # WHAT: Cleanup whitespace before parsing.
    for fmt in DATE_FORMATS:  # WHY: Try each known date format sequentially.
        try:
            return datetime.strptime(token, fmt).date()  # HOW: Convert to `date` instance.
        except ValueError:
            continue  # WHAT: Try next format if parsing fails.
    return None  # WHY: Unrecognized formats skip import with safe None.


def _convert_string(value: Any) -> Optional[str]:
    """Trim whitespace and return string token or None."""

    if _is_blank(value):  # WHAT: Maintain null semantics for blanks.
        return None
    return str(value).strip()  # HOW: Trim whitespace to avoid trailing spaces.


def _convert_value(field: Field, raw: Any) -> Any:
    """Route raw CSV data to the appropriate converter based on model field type."""

    if raw is None:  # WHAT: Handle DictReader missing columns gracefully.
        return None
    internal_type = field.get_internal_type()  # WHAT: Determine Django field type string.
    if internal_type in {"DecimalField"}:
        return _convert_decimal(raw)  # WHERE: All currency/percent fields.
    if internal_type in {"IntegerField", "PositiveIntegerField", "SmallIntegerField"}:
        return _convert_integer(raw)  # WHERE: Duration and other integer metrics.
    if internal_type in {"BooleanField", "NullBooleanField"}:
        return _convert_boolean(raw)  # WHERE: Boolean toggles.
    if internal_type == "DateField":
        return _convert_date(raw)  # WHERE: Date-only fields.
    if internal_type == "DateTimeField":
        date_value = _convert_date(raw)  # WHAT: Parse date component first.
        if date_value is None:
            return None  # WHY: Skip if date parsing failed.
        return datetime.combine(date_value, datetime.min.time())  # HOW: Promote to midnight datetime.
    return _convert_string(raw)  # WHAT: Fallback for CharField/TextField values.


def _read_csv_rows(file_path: Path) -> List[Dict[str, Any]]:
    """Load CSV rows with encoding fallbacks to support varied vendor exports."""

    encodings = ["utf-8-sig", "utf-8", "cp1252", "latin-1", "iso-8859-1"]  # WHAT: Ordered by likelihood.
    for encoding in encodings:  # HOW: Attempt each encoding sequentially.
        try:
            with file_path.open(newline="", encoding=encoding) as handle:
                reader = csv.DictReader(handle)  # WHAT: Use DictReader to map headers to values.
                return list(reader)  # WHY: Materialize rows for further processing.
        except UnicodeDecodeError:
            continue  # WHAT: Try next encoding if decoding fails.
    # HOW: Final fallback uses UTF-8 ignore errors to salvage partial data.
    with file_path.open(newline="", encoding="utf-8", errors="ignore") as handle:
        reader = csv.DictReader(handle)
        return list(reader)


class Command(BaseCommand):
    help = "Import blended outcome model data from CSV keyed by asset hub ID."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--file", dest="file_path", required=True, help="Path to the CSV file containing blended outcome data.")  # WHAT: Input CSV path argument.
        parser.add_argument("--batch-size", type=int, default=500, help="Number of rows to process per bulk operation.")  # WHY: Control chunk size for bulk_create.
        parser.add_argument("--dry-run", action="store_true", help="Parse the CSV without writing to the database.")  # WHAT: Allow validation without mutation.

    def handle(self, *args, **options) -> None:
        file_path = Path(options["file_path"])  # WHAT: Normalize string path into Path object.
        self.stdout.write(self.style.NOTICE(f"Resolved CSV path: {file_path}"))  # WHY: Surface which file is being processed.
        if not file_path.exists():
            raise CommandError(f"CSV file '{file_path}' does not exist.")  # WHY: Fail fast when file missing.
        self.stdout.write(self.style.NOTICE("Reading CSV rows...") )  # WHY: Inform operator that file I/O is underway.
        rows = _read_csv_rows(file_path)  # WHAT: Load CSV rows using tolerant reader.
        self.stdout.write(self.style.NOTICE(f"Total raw rows loaded (including header): {len(rows)}"))  # WHY: Provide visibility into CSV payload size.
        if not rows:
            self.stdout.write(self.style.WARNING("CSV contained no data rows."))  # WHY: Surface empty CSV scenario.
            return
        self.stdout.write(self.style.NOTICE("Parsing CSV rows into model payloads..."))  # WHY: Announce conversion phase start.
        parsed_rows, duplicate_counts = self._prepare_rows(rows)  # WHAT: Convert CSV payload into model-ready dicts.
        self.stdout.write(self.style.NOTICE(f"Parsed payload count (unique assets): {len(parsed_rows)}"))  # WHY: Show resulting unique asset count.
        if not parsed_rows:
            self.stdout.write(self.style.WARNING("No rows were eligible for import."))  # WHY: No valid rows to process.
            return
        asset_ids = list(parsed_rows.keys())  # WHAT: Collect AssetIdHub IDs referenced by CSV.
        self.stdout.write(self.style.NOTICE(f"Fetching {len(asset_ids)} asset hub records from database..."))  # WHY: Indicate database lookup step.
        asset_map = AssetIdHub.objects.in_bulk(asset_ids)  # HOW: Fetch existing hubs in one query.
        missing_assets = sorted(set(asset_ids) - set(asset_map.keys()))  # WHAT: IDs absent in DB.
        for missing in missing_assets:
            self.stderr.write(self.style.ERROR(f"Missing AssetIdHub with pk={missing}; skipping row."))  # WHY: Alert operator about missing hubs.
            parsed_rows.pop(missing, None)  # HOW: Drop rows referencing missing hubs.
        if not parsed_rows:
            self.stdout.write(self.style.WARNING("No rows left after filtering missing asset hubs."))  # WHAT: Nothing to import after filtering.
            return
        self.stdout.write(self.style.NOTICE("Introspecting model fields for upsert configuration..."))  # WHY: Explain metadata preparation step.
        field_state = self._introspect_fields()  # WHAT: Gather editable field metadata once.
        existing_ids = set(
            BlendedOutcomeModel.objects.filter(asset_hub_id__in=parsed_rows.keys()).values_list("asset_hub_id", flat=True)
        )  # WHY: Determine create vs update split.
        self.stdout.write(self.style.NOTICE(f"Existing records detected: {len(existing_ids)}"))  # WHY: Show how many rows will update versus create.
        instances: List[BlendedOutcomeModel] = []  # WHAT: Accumulate model instances for bulk_create.
        for asset_id, payload in parsed_rows.items():
            asset = asset_map[asset_id]  # WHAT: Resolved AssetIdHub instance.
            instances.append(BlendedOutcomeModel(asset_hub=asset, **payload))  # HOW: Instantiate model with payload.
        created_candidates = set(parsed_rows.keys()) - existing_ids  # WHAT: IDs that will insert.
        updated_candidates = set(parsed_rows.keys()) & existing_ids  # WHAT: IDs that will update.
        self.stdout.write(self.style.NOTICE(f"Rows to create: {len(created_candidates)} | Rows to update: {len(updated_candidates)}"))  # WHY: Provide summary before persistence.
        if options.get("dry_run"):
            self.stdout.write(self.style.SUCCESS(f"Dry run complete. Rows parsed: {len(rows)}. To create: {len(created_candidates)}. To update: {len(updated_candidates)}."))  # WHY: Report dry-run summary.
            if duplicate_counts:
                self.stdout.write(self.style.WARNING(f"Duplicate asset hub rows encountered: {duplicate_counts}"))  # WHAT: Inform on duplicates overwritten.
            if missing_assets:
                self.stdout.write(self.style.WARNING(f"Missing asset hub IDs skipped: {missing_assets}"))  # WHAT: Remind operator about missing IDs.
            return
        fields_to_update = field_state["updatable_fields"]  # WHAT: Fields allowed in update_conflicts.
        batch_size = options.get("batch_size") or 500  # WHY: Fallback to default batch size when None.
        total_persisted = 0  # WHAT: Running count of processed records.
        with transaction.atomic():  # HOW: Ensure all-or-nothing persistence per run.
            for start in range(0, len(instances), batch_size):
                chunk = instances[start : start + batch_size]  # WHAT: Slice chunk for bulk_create.
                self.stdout.write(self.style.NOTICE(f"Persisting chunk starting at index {start} with {len(chunk)} records..."))  # WHY: Display chunk progress for long imports.
                BlendedOutcomeModel.objects.bulk_create(
                    chunk,
                    batch_size=len(chunk),
                    update_conflicts=True,
                    update_fields=fields_to_update,
                    unique_fields=["asset_hub"],
                )  # HOW: Upsert rows keyed by asset_hub.
                total_persisted += len(chunk)  # WHAT: Track persisted chunk size.
                logger.debug("Chunk persisted", extra={"chunk_start": start, "chunk_size": len(chunk)})  # WHY: Provide structured debug log for deeper diagnostics.
                self.stdout.write(self.style.NOTICE(f"Chunk persisted; total processed so far: {total_persisted}"))  # WHY: Keep operator informed on cumulative progress.
        self.stdout.write(
            self.style.SUCCESS(
                f"Import complete. Processed rows: {len(rows)}. Created: {len(created_candidates)}. Updated: {len(updated_candidates)}. Persisted: {total_persisted}."
            )
        )
        if duplicate_counts:
            self.stdout.write(self.style.WARNING(f"Duplicate asset hub rows encountered: {duplicate_counts}"))  # WHAT: Report duplicate overwrites.
        if missing_assets:
            self.stdout.write(self.style.WARNING(f"Missing asset hub IDs skipped: {missing_assets}"))  # WHAT: Final reminder about missing IDs.

    def _prepare_rows(self, rows: Sequence[Dict[str, Any]]) -> Tuple[Dict[int, Dict[str, Any]], Dict[int, int]]:
        prepared: Dict[int, Dict[str, Any]] = {}  # WHAT: Maps asset hub ID to field payload.
        duplicates: Dict[int, int] = {}  # WHAT: Track duplicate CSV entries per asset for logging.
        field_state = self._introspect_fields()  # WHY: Reuse field metadata for conversions.
        for row in rows:
            asset_token = self._extract_asset_id(row)  # WHAT: Resolve asset hub identifier from row.
            if asset_token is None:
                self.stderr.write(self.style.ERROR("Row missing asset hub identifier; skipping."))  # WHY: Asset hub is mandatory join key.
                continue
            values: Dict[str, Any] = {}  # WHAT: Holds converted field values for this asset.
            for field_name, field in field_state["field_map"].items():
                raw_value = row.get(field_name)  # WHAT: Raw string from CSV column.
                converted = _convert_value(field, raw_value)  # HOW: Normalize according to field type.
                if field_name == "expected_irr" and isinstance(raw_value, str) and "%" in raw_value and isinstance(converted, Decimal):
                    converted = converted / Decimal("100")
                values[field_name] = converted  # WHERE: Store final value for upsert.
            if asset_token in prepared:
                duplicates[asset_token] = duplicates.get(asset_token, 1) + 1  # WHY: Increment duplicate counter when later rows override earlier ones.
            prepared[asset_token] = values  # HOW: Latest row wins for duplicate asset IDs.
        return prepared, duplicates  # WHAT: Provide parsed data plus duplicate stats.

    def _extract_asset_id(self, row: Dict[str, Any]) -> Optional[int]:
        for column in ASSET_ID_COLUMNS:  # WHAT: Check each alias for hub ID.
            token = row.get(column)  # WHAT: Pull raw token if column exists.
            if token is None:
                continue  # WHY: Skip when column absent.
            asset_id = _convert_integer(token)  # HOW: Reuse integer converter for safe parsing.
            if asset_id is not None:
                return asset_id  # WHAT: Return first successfully parsed hub ID.
        return None  # WHY: Signal missing/invalid hub identifier.

    def _introspect_fields(self) -> Dict[str, Any]:
        field_map: Dict[str, Field] = {}  # WHAT: Lookup of field name to model field object.
        updatable_fields: List[str] = []  # WHAT: Editable field names for bulk update_conflicts.
        for field in BlendedOutcomeModel._meta.get_fields():  # HOW: Iterate over model metadata.
            if not getattr(field, "concrete", False):
                continue  # WHY: Skip reverse relations/m2m fields.
            if getattr(field, "auto_created", False):
                continue  # WHY: Ignore implicit fields like OneToOne reverse relations.
            if field.name in {"asset_hub", "created_at", "updated_at"}:
                continue  # WHY: Exclude primary key and audit timestamps from upserts.
            field_map[field.name] = field  # WHAT: Track field for conversion mapping.
            if getattr(field, "editable", True):
                updatable_fields.append(field.name)  # WHY: Only editable fields should update on conflicts.
        return {"field_map": field_map, "updatable_fields": updatable_fields}  # WHAT: Cached metadata for consumers.
