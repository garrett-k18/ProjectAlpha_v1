"""Simplified SellerRawData CSV importer with one-to-one header mappings. This is used to import csvs that match
model headers for sellerrawdata

Docs reviewed:
- Django custom commands: https://docs.djangoproject.com/en/stable/howto/custom-management-commands/
- Django model field conversion semantics: https://docs.djangoproject.com/en/stable/ref/models/instances/#assigning-to-fields
- Python csv reader: https://docs.python.org/3/library/csv.html
- Django transactions: https://docs.djangoproject.com/en/stable/topics/db/transactions/
"""

from __future__ import annotations

import csv  # WHAT: Built-in CSV parsing used to read the import file.
from datetime import datetime  # WHAT: Supports date parsing via datetime.strptime when needed.
from decimal import Decimal, InvalidOperation  # WHAT: Safely handle currency/decimal inputs.
from pathlib import Path  # WHAT: Provides filesystem path utilities with explicit typing.
from typing import Any, Dict, List, Optional  # WHAT: Static typing annotations for clarity.

from django.core.management.base import BaseCommand, CommandError  # WHAT: Base infrastructure for management commands.
from django.db import transaction  # WHAT: Ensure database writes occur atomically per row.
from django.utils.dateparse import parse_date  # WHAT: Gracefully parse ISO formatted dates.

from acq_module.models.model_acq_seller import Seller, Trade, SellerRawData  # WHAT: Domain models targeted by the import.
from core.models import AssetIdHub  # WHAT: Master hub model required for SellerRawData primary keys.


# WHAT: Tokens that should be interpreted as null/empty when cleaning string inputs.
NULL_TOKENS = {"", "na", "n/a", "null", "none", "nil"}
# WHAT: Truthy tokens for boolean conversions.
TRUTHY_TOKENS = {"true", "t", "yes", "y", "1"}
# WHAT: Falsy tokens for boolean conversions.
FALSY_TOKENS = {"false", "f", "no", "n", "0"}


def _is_blank(value: Any) -> bool:
    """Return True when the incoming CSV cell should be considered empty."""

    # WHAT: Treat Python None as blank immediately.
    if value is None:
        return True
    # WHAT: Normalize to lowercase stripped string for comparison against the NULL_TOKENS set.
    return str(value).strip().lower() in NULL_TOKENS


def _clean_numeric_token(raw: Any) -> str:
    """Normalize numeric strings by stripping formatting such as commas or currency symbols."""

    token = str(raw).strip()  # WHAT: Convert to string and trim whitespace.
    token = token.replace("$", "")  # WHY: Remove currency symbols that block Decimal conversion.
    token = token.replace(",", "")  # WHY: Remove thousands separators to avoid parse errors.
    token = token.replace("%", "")  # WHY: Remove percent signs; scaling handled later if necessary.
    token = token.replace("(", "-")  # WHY: Interpret accounting negatives wrapped in parentheses.
    token = token.replace(")", "")  # WHAT: Drop closing parenthesis after converting to minus sign.
    return token  # WHAT: Return cleaned token for downstream conversion helpers.


def _convert_decimal(value: Any) -> Optional[Decimal]:
    """Convert an incoming value into a Decimal, returning None when blank or invalid."""

    if _is_blank(value):  # WHAT: Respect nullable decimal fields.
        return None
    token = _clean_numeric_token(value)  # WHAT: Normalize formatting before Decimal conversion.
    try:
        return Decimal(token)  # HOW: Use Decimal to avoid floating-point drift.
    except (InvalidOperation, ValueError, TypeError):
        return None  # WHY: Gracefully ignore malformed numeric tokens.


def _convert_integer(value: Any) -> Optional[int]:
    """Cast the incoming value to an integer, handling floats like "123.0"."""

    if _is_blank(value):
        return None
    token = _clean_numeric_token(value)
    try:
        return int(float(token))  # WHY: float() handles values like "1200.0" which int() alone rejects.
    except (ValueError, TypeError, OverflowError):
        return None


def _convert_boolean(value: Any) -> Optional[bool]:
    """Interpret a CSV token as a boolean, supporting common truthy/falsy representations."""

    if _is_blank(value):
        return None
    token = str(value).strip().lower()
    if token in TRUTHY_TOKENS:
        return True
    if token in FALSY_TOKENS:
        return False
    # WHAT: Fall back to numeric interpretation when token not in explicit truthy/falsy sets.
    try:
        numeric = float(_clean_numeric_token(token))
    except (ValueError, TypeError):
        return None
    return numeric != 0.0  # WHAT: Treat nonzero numbers as truthy.


def _convert_date(value: Any) -> Optional[datetime.date]:
    """Parse date tokens supporting ISO strings and common US formats."""

    if _is_blank(value):
        return None
    token = str(value).strip()
    iso_candidate = parse_date(token)  # WHAT: Django helper that covers YYYY-MM-DD plus time-insensitive ISO.
    if iso_candidate:
        return iso_candidate
    # WHAT: Fallback manual parsing for MM/DD/YYYY or MM-DD-YYYY.
    for fmt in ("%m/%d/%Y", "%m-%d-%Y", "%m/%d/%y", "%Y%m%d"):
        try:
            return datetime.strptime(token, fmt).date()
        except ValueError:
            continue
    return None  # WHY: Unparseable tokens are treated as null.


def _convert_value(field, raw: Any) -> Any:
    """Route raw CSV cell values to appropriate converters based on Django field metadata."""

    if raw is None:
        return None
    internal = field.get_internal_type()
    if internal in {"DecimalField"}:
        return _convert_decimal(raw)
    if internal in {"IntegerField", "PositiveIntegerField", "SmallIntegerField"}:
        return _convert_integer(raw)
    if internal in {"BooleanField", "NullBooleanField"}:
        return _convert_boolean(raw)
    if internal == "DateField":
        return _convert_date(raw)
    if internal == "DateTimeField":
        date_value = _convert_date(raw)
        if date_value is None:
            return None
        return datetime.combine(date_value, datetime.min.time())  # WHAT: Promote date to midnight datetime.
    return str(raw).strip() or None  # WHAT: Default to trimmed string, honoring null semantics.


class Command(BaseCommand):
    """Minimal CSV importer when headers already match `SellerRawData` fields exactly."""

    help = (
        "Import SellerRawData rows from a CSV whose headers exactly match model fields. "
        "No AI mapping is performed; only direct field matches are loaded."
    )

    def add_arguments(self, parser) -> None:
        """Register command-line arguments for the simplified importer."""

        parser.add_argument(
            "--file",
            dest="file_path",
            required=True,
            help="Path to the CSV file with SellerRawData columns.",
        )  # WHAT: Primary input file argument.
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Parse and validate without persisting any database changes.",
        )  # WHAT: Supports validation passes identical to production imports.
        parser.add_argument(
            "--batch-size",
            type=int,
            default=100,
            help="Number of rows processed per transaction batch (default: 100).",
        )  # WHAT: Provide control over transaction chunking for large files.
        parser.add_argument(
            "--skip-rows",
            type=int,
            default=0,
            help="Number of header rows to skip before the actual header line (default: 0).",
        )  # WHY: Some vendor files include intro text that must be skipped.
        parser.add_argument(
            "--encoding",
            type=str,
            default="utf-8-sig",
            help="Text encoding used to read the CSV file (default: utf-8-sig).",
        )  # WHAT: Allow manual override when files use Windows-1252 or other codecs.
        parser.set_defaults(update_existing=True)  # WHAT: Overwrite by default when duplicates encountered.
        parser.add_argument(
            "--skip-update-existing",
            action="store_false",
            dest="update_existing",
            help="Skip updates for existing sellertape_id rows (they will be left unchanged).",
        )  # WHAT: Optional flag to disable the default overwrite behavior.

    def handle(self, *args, **options) -> None:
        """Command entry point: validate inputs, load CSV, and persist rows."""

        file_path = Path(options["file_path"])  # WHAT: Convert CLI string to Path for convenience.
        dry_run = options.get("dry_run", False)  # WHAT: Flag controlling side effects.
        batch_size = options.get("batch_size") or 100  # WHAT: Batch size with fallback to default.
        skip_rows = options.get("skip_rows") or 0  # WHAT: Header offset used during CSV read.
        encoding = options.get("encoding", "utf-8-sig")  # WHAT: Text encoding for file read.
        update_existing = options.get("update_existing", True)  # WHAT: Toggle for upsert behavior, defaults to True.

        if not file_path.exists():  # WHAT: Ensure import file is present before proceeding.
            raise CommandError(f"CSV file '{file_path}' does not exist.")

        rows = self._read_csv(file_path, skip_rows, encoding)  # WHAT: Load all CSV rows into memory for processing.
        if not rows:
            self.stdout.write(self.style.WARNING("CSV contained no data rows."))
            return

        field_state = self._introspect_fields()  # WHAT: Cache model field metadata for conversions.
        prepared, errors = self._prepare_records(rows, field_state)  # WHAT: Convert raw dicts to ORM payloads.

        self.stdout.write(self.style.SUCCESS(
            f"Parsed rows: {len(rows)}. Valid: {len(prepared)}. Errors: {len(errors)}."
        ))  # WHAT: Provide quick summary before persistence.

        if errors:
            for row_number, message in errors[:5]:  # WHAT: Display first five validation issues.
                self.stderr.write(self.style.ERROR(f"Row {row_number}: {message}"))
            if len(errors) > 5:
                remaining = len(errors) - 5
                self.stderr.write(self.style.ERROR(f"... {remaining} additional errors suppressed."))

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run requested; no database changes were made."))
            return

        if not prepared:
            self.stdout.write(self.style.WARNING("No valid rows available for import."))
            return

        created, updated, skipped, hubs_created = self._persist_records(
            prepared,
            batch_size,
            update_existing,
        )  # WHAT: Execute database writes with conflict handling.

        self.stdout.write(self.style.SUCCESS(
            f"Import complete. Created: {created}. Updated: {updated}. Skipped: {skipped}. AssetIdHub created: {hubs_created}."
        ))  # WHAT: Final outcome summary for operators.

    def _get_seller(self, seller_id: int) -> Seller:
        """Fetch existing Seller or auto-create a placeholder when absent."""

        seller, _created = Seller.objects.get_or_create(
            pk=seller_id,
            defaults={
                "name": f"Imported Seller {seller_id}",
                "broker": "",
                "email": "",
                "poc": "",
            },
        )
        return seller

    def _get_trade(self, trade_id: int, seller: Seller) -> Trade:
        """Fetch existing Trade or create a placeholder bound to the provided Seller."""

        trade, created = Trade.objects.get_or_create(
            pk=trade_id,
            defaults={"seller": seller},
        )
        if not created and trade.seller_id != seller.id:
            trade.seller = seller
            trade.save(update_fields=["seller"])
        return trade

    def _read_csv(self, file_path: Path, skip_rows: int, encoding: str) -> List[Dict[str, Any]]:
        """Read the CSV file into a list of dictionaries keyed by header names."""

        with file_path.open("r", newline="", encoding=encoding) as handle:
            # WHAT: Skip preliminary rows before the header if requested.
            for _ in range(skip_rows):
                next(handle, None)
            reader = csv.DictReader(handle)  # WHAT: Map headers to values for each row.
            return list(reader)

    def _introspect_fields(self) -> Dict[str, Any]:
        """Collect model field metadata needed for conversions and updates."""

        field_map: Dict[str, Any] = {}  # WHAT: Dictionary mapping field names to Django Field objects.
        for field in SellerRawData._meta.get_fields():
            if getattr(field, "auto_created", False):
                continue  # WHY: Skip reverse relations and implicit fields.
            if field.name in {"asset_hub", "seller", "trade"}:
                continue  # WHY: Managed separately within import logic.
            field_map[field.name] = field
        return field_map

    def _prepare_records(
        self,
        rows: List[Dict[str, Any]],
        field_state: Dict[str, Any],
    ) -> tuple[List[Dict[str, Any]], List[tuple[int, str]]]:
        """Transform raw CSV rows into validated ORM payload dictionaries."""

        prepared: List[Dict[str, Any]] = []  # WHAT: Accumulates successfully converted rows.
        errors: List[tuple[int, str]] = []  # WHAT: Captures row-level validation errors.

        normalized_headers = {name.lower(): name for name in field_state.keys()}  # WHAT: Case-insensitive header mapping.
        header_keys = set()  # WHAT: Track unique lower-cased headers for per-row FK detection.
        for row in rows:
            header_keys.update({(key or "").strip().lower() for key in row.keys()})

        seller_header_key = "seller_id"
        trade_header_key = "trade_id"
        if seller_header_key not in header_keys or trade_header_key not in header_keys:
            raise CommandError(
                "CSV must contain 'seller_id' and 'trade_id' columns to resolve per-row ownership."
            )

        # WHAT: Map lowercase header names back to their original casing for value extraction.
        header_lookup = {}
        for row in rows:
            for key in row.keys():
                if key is None:
                    continue
                header_lookup.setdefault(key.strip().lower(), key)
        seller_header = header_lookup[seller_header_key]
        trade_header = header_lookup[trade_header_key]

        seller_cache: Dict[int, Seller] = {}  # WHAT: Avoid redundant Seller queries.
        trade_cache: Dict[int, Trade] = {}  # WHAT: Avoid redundant Trade lookups.

        for idx, row in enumerate(rows, start=1):
            seller_val_raw = row.get(seller_header)
            trade_val_raw = row.get(trade_header)

            try:
                seller_id = int(str(seller_val_raw).strip()) if seller_val_raw not in (None, "") else None
            except ValueError:
                seller_id = None
            try:
                trade_id = int(str(trade_val_raw).strip()) if trade_val_raw not in (None, "") else None
            except ValueError:
                trade_id = None

            if not seller_id or not trade_id:
                errors.append((idx, "Missing or invalid seller_id/trade_id values."))
                continue

            seller_instance = seller_cache.get(seller_id)
            if seller_instance is None:
                try:
                    seller_instance = self._get_seller(seller_id)
                except CommandError as exc:
                    errors.append((idx, str(exc)))
                    continue
                seller_cache[seller_id] = seller_instance

            trade_instance = trade_cache.get(trade_id)
            if trade_instance is None:
                trade_instance = self._get_trade(trade_id, seller_instance)
                trade_cache[trade_id] = trade_instance

            record: Dict[str, Any] = {"seller": seller_instance, "trade": trade_instance}
            sellertape_value = None  # WHAT: Track sellertape_id to ensure presence after processing.

            for header, raw_value in row.items():
                if header is None:
                    continue  # WHY: DictReader can yield None keys when rows shorter than header list.
                header_key = header.strip().lower()
                field_name = normalized_headers.get(header_key)
                if not field_name:
                    continue  # WHY: Skip columns that do not align with SellerRawData fields.
                field = field_state[field_name]
                converted = _convert_value(field, raw_value)
                if converted is not None:
                    record[field_name] = converted
                if field_name == "sellertape_id":
                    sellertape_value = converted or raw_value

            if not sellertape_value:
                errors.append((idx, "Missing required sellertape_id column."))
                continue

            prepared.append(record)

        return prepared, errors

    def _persist_records(
        self,
        records: List[Dict[str, Any]],
        batch_size: int,
        update_existing: bool,
    ) -> tuple[int, int, int, int]:
        """Persist prepared records into the database with conflict handling."""

        created = 0  # WHAT: Counter for newly inserted SellerRawData rows.
        updated = 0  # WHAT: Counter for rows updated when duplicates encountered.
        skipped = 0  # WHAT: Counter for rows skipped due to errors or conflicts.
        hubs_created = 0  # WHAT: Counter for new AssetIdHub rows created.

        for start in range(0, len(records), batch_size):
            chunk = records[start : start + batch_size]
            self.stdout.write(
                self.style.NOTICE(
                    f"Persisting batch {(start // batch_size) + 1} of {((len(records) - 1) // batch_size) + 1}"
                )
            )  # WHAT: Provide live progress feedback so Railway logs show forward movement.
            with transaction.atomic():
                for payload in chunk:
                    sellertape_id = payload.get("sellertape_id")
                    if sellertape_id is None:
                        skipped += 1
                        continue

                    existing = SellerRawData.objects.filter(sellertape_id=sellertape_id).select_related("asset_hub").first()
                    if existing:
                        if update_existing:
                            for field_name, value in payload.items():
                                if field_name in {"seller", "trade"}:
                                    continue
                                setattr(existing, field_name, value)
                            existing.seller = payload["seller"]
                            existing.trade = payload["trade"]
                            existing.save()  # WHAT: Allow auto_now timestamps (updated_at) to refresh automatically.
                            updated += 1
                        else:
                            skipped += 1
                        continue

                    asset_hub = AssetIdHub.objects.create(sellertape_id=sellertape_id)
                    hubs_created += 1

                    payload_copy = payload.copy()
                    payload_copy["asset_hub"] = asset_hub

                    SellerRawData.objects.create(**payload_copy)
                    created += 1

        return created, updated, skipped, hubs_created
