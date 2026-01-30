"""Django management command for importing `Valuation` rows from CSV files.

Docs reviewed:
- Custom management commands: https://docs.djangoproject.com/en/stable/howto/custom-management-commands/
- Field value assignment semantics: https://docs.djangoproject.com/en/stable/ref/models/instances/#assigning-to-fields
- bulk_create with conflict handling: https://docs.djangoproject.com/en/stable/ref/models/querysets/#bulk-create
"""

from __future__ import annotations

import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Set

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Field

from core.models.model_co_assetIdHub import AssetIdHub
from core.models.model_co_valuations import Valuation

# WHAT: Null tokens accepted across all converters to treat common CSV placeholders as empty.
NULL_TOKENS = {"", "na", "n/a", "null", "none", "nil"}
# WHAT: Truthy tokens recognized by `_convert_boolean`.
TRUTHY_TOKENS = {"true", "t", "yes", "y", "1"}
# WHAT: Falsy tokens recognized by `_convert_boolean`.
FALSY_TOKENS = {"false", "f", "no", "n", "0"}
# WHAT: Date formats frequently seen in vendor exports.
DATE_FORMATS = (
    "%Y-%m-%d",  # WHAT: ISO format (YYYY-MM-DD).
    "%m/%d/%Y",  # WHAT: US format with four-digit year.
    "%m-%d-%Y",  # WHAT: US format with hyphen separators.
    "%Y/%m/%d",  # WHAT: ISO with slashes.
    "%m/%d/%y",  # WHAT: US format with two-digit year.
    "%Y%m%d",  # WHAT: Compact ISO string without separators.
)
# WHAT: Acceptable column headers for the asset hub join key to maximize compatibility.
ASSET_ID_COLUMNS = (
    "asset_hub_id",  # WHAT: Preferred snake_case header.
    "asset_hub",  # WHAT: Legacy export header.
    "assetid",  # WHAT: Shorthand header used in some spreadsheets.
    "asset_id",  # WHAT: Alternate snake_case header.
)
# WHAT: Valid source codes from `Valuation.Source`, normalized to lowercase for comparison.
VALID_SOURCE_CODES = {member.value.lower(): member.value for member in Valuation.Source}
# WHAT: Mapping of display labels to codes (lowercased) so CSVs may use display strings.
SOURCE_DISPLAY_LOOKUP = {member.label.lower(): member.value for member in Valuation.Source}


def _is_blank(value: Any) -> bool:
    """Check whether a CSV token should be treated as null."""

    # WHAT: None should always short-circuit to blank.
    if value is None:
        return True
    # WHAT: Normalize tokens for comparison against the null sentinel set.
    return str(value).strip().lower() in NULL_TOKENS


def _clean_numeric_token(raw: Any) -> str:
    """Remove currency/percent formatting to stabilize numeric parsing."""

    token = str(raw).strip()  # WHAT: Convert to string and remove surrounding whitespace.
    token = token.replace("$", "")  # WHY: Remove currency symbols.
    token = token.replace(",", "")  # WHY: Remove thousand separators.
    token = token.replace("%", "")  # WHY: Percent signs block numeric parsing.
    token = token.replace("(", "-")  # WHY: Accounting exports wrap negatives in parentheses.
    token = token.replace(")", "")  # WHAT: Remove closing parenthesis after negation.
    return token  # WHERE: Token feeds the numeric converters below.


def _convert_integer(value: Any) -> Optional[int]:
    """Convert raw token into Python `int` (fault-tolerant)."""

    if _is_blank(value):  # WHAT: Preserve `None` for blank CSV cells.
        return None
    token = _clean_numeric_token(value)  # WHAT: Normalize numeric formatting.
    try:
        return int(float(token))  # WHY: `float` gracefully handles tokens such as "123.0".
    except (TypeError, ValueError, OverflowError):
        return None  # HOW: Silently drop invalid numeric tokens to keep the import resilient.


def _convert_decimal(value: Any) -> Optional[Decimal]:
    """Convert raw token into `Decimal` (precision-safe for money fields)."""

    if _is_blank(value):  # WHAT: Maintain `None` for blank values.
        return None
    token = _clean_numeric_token(value)  # WHY: Remove formatting before Decimal conversion.
    try:
        return Decimal(token)  # HOW: Use Decimal instead of float to avoid precision loss.
    except (InvalidOperation, ValueError, TypeError):
        return None  # WHAT: Invalid numeric strings are ignored.


def _convert_boolean(value: Any) -> Optional[bool]:
    """Convert raw token into boolean, tolerant of numeric and text inputs."""

    if _is_blank(value):  # WHAT: Permit nullable boolean fields.
        return None
    token = str(value).strip().lower()  # WHAT: Normalize token for matching.
    if token in TRUTHY_TOKENS:  # WHY: Recognize standard truthy literals.
        return True
    if token in FALSY_TOKENS:  # WHY: Recognize standard falsy literals.
        return False
    try:
        numeric = float(_clean_numeric_token(token))  # WHAT: Support numeric flags such as "0" or "1".
    except (TypeError, ValueError):
        return None  # HOW: Fallback to None when token cannot be interpreted.
    return numeric != 0.0  # WHY: Non-zero numeric values imply truthy.


def _convert_date(value: Any) -> Optional[datetime.date]:
    """Convert raw token into `date`, supporting multiple vendor formats."""

    if _is_blank(value):  # WHAT: Date fields remain nullable.
        return None
    token = str(value).strip()  # WHAT: Remove whitespace before parsing.
    for fmt in DATE_FORMATS:  # WHY: Attempt each accepted format sequentially.
        try:
            return datetime.strptime(token, fmt).date()  # HOW: Convert to `date`.
        except ValueError:
            continue  # WHAT: Try the next format when parsing fails.
    return None  # WHY: Tokens that do not match any format are treated as null.


def _convert_string(value: Any) -> Optional[str]:
    """Trim whitespace and return string token or `None`."""

    if _is_blank(value):  # WHAT: Preserve `None` for blank strings.
        return None
    return str(value).strip()  # HOW: Normalize by stripping whitespace.


def _convert_source(value: Any) -> Optional[str]:
    """Normalize valuation source codes using model choices."""

    if _is_blank(value):  # WHAT: Source is required later; return None for now to flag missing data.
        return None
    token = str(value).strip().lower()  # WHAT: Normalize case for lookup.
    if token in VALID_SOURCE_CODES:  # WHY: Accept canonical codes as-is.
        return VALID_SOURCE_CODES[token]
    if token in SOURCE_DISPLAY_LOOKUP:  # WHY: Accept display labels from the UI.
        return SOURCE_DISPLAY_LOOKUP[token]
    return None  # WHAT: Unknown source values are handled by caller.


def _convert_value(field: Field, raw: Any) -> Any:
    """Route raw CSV data to the correct converter based on Django field type."""

    if raw is None:  # WHAT: DictReader missing columns return `None`.
        return None
    internal_type = field.get_internal_type()  # WHAT: Use Django metadata to pick converter.
    if internal_type in {"DecimalField"}:
        return _convert_decimal(raw)  # WHERE: Money/percentage fields.
    if internal_type in {"IntegerField", "PositiveIntegerField", "SmallIntegerField"}:
        return _convert_integer(raw)  # WHERE: Rehab detail estimates (integers).
    if internal_type in {"BooleanField", "NullBooleanField"}:
        return _convert_boolean(raw)  # WHERE: Any boolean toggles (none in this model yet but future-proof).
    if internal_type == "DateField":
        return _convert_date(raw)  # WHERE: `value_date`.
    if internal_type == "DateTimeField":
        date_value = _convert_date(raw)  # WHAT: Parse date portion first.
        if date_value is None:
            return None  # WHY: Avoid constructing datetimes when date missing.
        return datetime.combine(date_value, datetime.min.time())  # HOW: Promote to midnight datetime.
    return _convert_string(raw)  # WHAT: Default for `CharField`, `TextField`, `URLField`.


def _read_csv_rows(file_path: Path) -> List[Dict[str, Any]]:
    """Load CSV rows with encoding fallbacks to support varied vendor exports."""

    encodings = ["utf-8-sig", "utf-8", "cp1252", "latin-1", "iso-8859-1"]  # WHAT: Ordered list of likely encodings.
    for encoding in encodings:  # HOW: Try each encoding until one succeeds.
        try:
            with file_path.open(newline="", encoding=encoding) as handle:
                reader = csv.DictReader(handle)  # WHAT: Map headers to values for each row.
                return list(reader)  # WHY: Materialize rows for subsequent processing.
        except UnicodeDecodeError:
            continue  # WHAT: Retry with the next encoding on decode failure.
    # HOW: Final fallback uses UTF-8 while ignoring decode errors to salvage as much data as possible.
    with file_path.open(newline="", encoding="utf-8", errors="ignore") as handle:
        reader = csv.DictReader(handle)
        return list(reader)


class Command(BaseCommand):
    """Management command to import valuation records keyed by `AssetIdHub`."""

    help = "Import valuation data from CSV keyed by asset hub ID and valuation source."  # WHAT: Django help string.

    def add_arguments(self, parser) -> None:
        """Register CLI arguments for the management command."""

        parser.add_argument(
            "--file",
            dest="file_path",
            required=True,
            help="Path to the CSV file containing valuation rows.",
        )  # WHAT: Required path to the import CSV file.
        parser.add_argument(
            "--batch-size",
            type=int,
            default=500,
            help="Number of rows to process per bulk insert batch (default: 500).",
        )  # WHY: Allow tuning batch size for large files.
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Parse the CSV without writing any database changes.",
        )  # WHAT: Supports validation runs without side effects.

    def handle(self, *args, **options) -> None:
        """Entry point: parse CSV, validate, and upsert valuation rows."""

        file_path = Path(options["file_path"])  # WHAT: Convert string argument to `Path`.
        if not file_path.exists():
            raise CommandError(f"CSV file '{file_path}' does not exist.")  # WHY: Fail fast when file is missing.

        rows = _read_csv_rows(file_path)  # WHAT: Load all CSV rows using tolerant encoding handling.
        if not rows:
            self.stdout.write(self.style.WARNING("CSV contained no data rows."))  # WHY: Early exit for empty files.
            return

        parsed_rows, duplicate_counts, invalid_sources = self._prepare_rows(rows)  # WHAT: Convert raw data into model payloads.
        if not parsed_rows:
            self.stdout.write(self.style.WARNING("No rows were eligible for import."))  # WHY: Nothing to insert/update.
            return

        asset_ids = list(parsed_rows.keys())  # WHAT: Collect all referenced asset hub IDs.
        asset_map = AssetIdHub.objects.in_bulk(asset_ids)  # HOW: Fetch `AssetIdHub` instances in one query.
        missing_assets = sorted(set(asset_ids) - set(asset_map.keys()))  # WHAT: IDs present in CSV but absent in DB.

        for missing in missing_assets:  # WHAT: Report missing asset hubs to the operator.
            self.stderr.write(self.style.ERROR(f"Missing AssetIdHub with pk={missing}; skipping row."))
            parsed_rows.pop(missing, None)  # HOW: Drop rows referencing unknown assets.

        if not parsed_rows:
            self.stdout.write(self.style.WARNING("No rows left after filtering missing asset hubs."))  # WHY: All rows invalid.
            return

        field_state = self._introspect_fields()  # WHAT: Gather editable field metadata once per run.
        existing_ids = set(
            Valuation.objects.filter(asset_hub_id__in=parsed_rows.keys()).values_list("asset_hub_id", "source", "value_date")
        )  # WHY: Determine which rows will update vs. insert.

        instances: List[Valuation] = []  # WHAT: List of model instances ready for bulk_create.
        for asset_id, payloads in parsed_rows.items():
            asset = asset_map[asset_id]  # WHAT: Resolved `AssetIdHub` instance.
            for payload in payloads:
                payload_copy = payload.copy()  # WHAT: Work on a shallow copy to avoid mutating cache.
                payload_copy["asset_hub"] = asset  # HOW: Attach FK instance.
                instances.append(Valuation(**payload_copy))  # HOW: Instantiate `Valuation` object with payload.

        created_candidates = []  # WHAT: Track composite keys slated for creation.
        updated_candidates = []  # WHAT: Track composite keys slated for update.
        for asset_id, payloads in parsed_rows.items():
            for payload in payloads:
                key = (asset_id, payload.get("source"), payload.get("value_date"))  # WHAT: Composite unique key.
                if key in existing_ids:
                    updated_candidates.append(key)
                else:
                    created_candidates.append(key)

        if options.get("dry_run"):
            self.stdout.write(
                self.style.SUCCESS(
                    f"Dry run complete. Rows parsed: {len(rows)}. To create: {len(created_candidates)}. To update: {len(updated_candidates)}."
                )
            )  # WHY: Provide summary and exit without DB writes.
            if duplicate_counts:
                self.stdout.write(self.style.WARNING(f"Duplicate asset/source/date rows encountered: {duplicate_counts}"))
            if missing_assets:
                self.stdout.write(self.style.WARNING(f"Missing asset hub IDs skipped: {missing_assets}"))
            if invalid_sources:
                self.stdout.write(self.style.WARNING(f"Rows skipped due to invalid source codes: {sorted(invalid_sources)}"))
            return

        updatable_fields = field_state["updatable_fields"]  # WHAT: Fields allowed during upsert updates.
        batch_size = options.get("batch_size") or 500  # WHY: Fallback to default batch size when option omitted.
        total_persisted = 0  # WHAT: Counter for rows processed in DB.

        with transaction.atomic():  # HOW: Ensure all rows persist atomically.
            for start in range(0, len(instances), batch_size):
                chunk = instances[start : start + batch_size]  # WHAT: Slice chunk for bulk_create.
                Valuation.objects.bulk_create(
                    chunk,
                    batch_size=len(chunk),
                    update_conflicts=True,
                    update_fields=updatable_fields,
                    unique_fields=["asset_hub", "source", "value_date"],
                )  # HOW: Upsert valuations based on the unique constraint.
                total_persisted += len(chunk)

        self.stdout.write(
            self.style.SUCCESS(
                f"Import complete. Processed rows: {len(rows)}. Created: {len(created_candidates)}. Updated: {len(updated_candidates)}. Persisted: {total_persisted}."
            )
        )  # WHAT: Report final summary after successful import.
        if duplicate_counts:
            self.stdout.write(self.style.WARNING(f"Duplicate asset/source/date rows encountered: {duplicate_counts}"))
        if missing_assets:
            self.stdout.write(self.style.WARNING(f"Missing asset hub IDs skipped: {missing_assets}"))
        if invalid_sources:
            self.stdout.write(self.style.WARNING(f"Rows skipped due to invalid source codes: {sorted(invalid_sources)}"))

    def _prepare_rows(
        self, rows: Sequence[Dict[str, Any]]
    ) -> Tuple[Dict[int, List[Dict[str, Any]]], Dict[Tuple[int, Optional[str], Optional[datetime.date]], int], Set[str]]:
        """Convert raw CSV rows into valuation payloads grouped by asset hub."""

        prepared_by_key: Dict[Tuple[int, Optional[str], Optional[datetime.date]], Dict[str, Any]] = {}  # WHAT: Cache latest payload per unique key.
        duplicates: Dict[Tuple[int, Optional[str], Optional[datetime.date]], int] = {}  # WHAT: Track duplicate composite keys for logging.
        invalid_sources: Set[str] = set()  # WHAT: Collect invalid source tokens for operator feedback.
        field_state = self._introspect_fields()  # WHY: Obtain field metadata for conversion.

        for row in rows:
            asset_token = self._extract_asset_id(row)  # WHAT: Resolve asset hub ID from the row.
            if asset_token is None:
                self.stderr.write(self.style.ERROR("Row missing asset hub identifier; skipping."))
                continue  # WHY: Cannot join to hub without identifier.

            source_value = _convert_source(row.get("source"))  # WHAT: Normalize source code.
            if source_value is None:
                invalid_sources.add(str(row.get("source")))  # WHY: Log invalid source for summary output.
                self.stderr.write(self.style.ERROR(f"Invalid valuation source '{row.get('source')}' for asset {asset_token}; skipping."))
                continue

            payload: Dict[str, Any] = {}  # WHAT: Stores converted field values for this valuation.
            for field_name, field in field_state["field_map"].items():
                if field_name == "source":
                    payload[field_name] = source_value  # WHAT: Already normalized above.
                    continue
                raw_value = row.get(field_name)
                converted = _convert_value(field, raw_value)  # HOW: Convert according to field type.
                payload[field_name] = converted

            payload["source"] = source_value  # WHAT: Ensure source included.
            payload_key = (
                asset_token,
                payload.get("source"),
                payload.get("value_date"),
            )  # WHAT: Composite uniqueness key (matches DB constraint).

            if payload_key in prepared_by_key:
                duplicates[payload_key] = duplicates.get(payload_key, 0) + 1  # WHY: Log duplicate rows overriding earlier payload.
            prepared_by_key[payload_key] = payload  # HOW: Latest occurrence wins.

        prepared: Dict[int, List[Dict[str, Any]]] = {}  # WHAT: Maps asset hub ID to final payload list.
        for (asset_id, _source, _date), payload in prepared_by_key.items():
            prepared.setdefault(asset_id, []).append(payload)

        return prepared, duplicates, invalid_sources

    def _extract_asset_id(self, row: Dict[str, Any]) -> Optional[int]:
        """Extract the asset hub identifier from possible column headers."""

        for column in ASSET_ID_COLUMNS:  # WHAT: Iterate through accepted header variants.
            token = row.get(column)
            if token is None:
                continue  # WHY: Skip missing columns.
            asset_id = _convert_integer(token)  # HOW: Convert token to integer ID.
            if asset_id is not None:
                return asset_id  # WHAT: Return first successfully parsed asset ID.
        return None  # WHY: Signal missing/invalid asset hub identifier.

    def _introspect_fields(self) -> Dict[str, Any]:
        """Collect concrete, editable fields for conversion and updates."""

        field_map: Dict[str, Field] = {}  # WHAT: Maps field name to Django field instance.
        updatable_fields: List[str] = []  # WHAT: Tracks editable field names for conflict updates.

        for field in Valuation._meta.get_fields():  # HOW: Iterate over model metadata.
            if not getattr(field, "concrete", False):
                continue  # WHY: Ignore reverse relations and virtual fields.
            if getattr(field, "auto_created", False):
                continue  # WHY: Skip implicit fields such as reverse OneToOne relations.
            if field.name in {"asset_hub", "created_at", "updated_at"}:
                continue  # WHY: Exclude join key (handled separately) and audit timestamps from updates.
            field_map[field.name] = field  # WHAT: Register field for conversion.
            if getattr(field, "editable", True):
                updatable_fields.append(field.name)  # WHY: Only editable fields participate in conflict updates.

        return {"field_map": field_map, "updatable_fields": updatable_fields}
