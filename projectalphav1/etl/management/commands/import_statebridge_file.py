from __future__ import annotations

import json
import hashlib
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Tuple, Type
from collections import Counter

import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction

from etl.models import (
    SBDailyArmData,
    SBDailyBankruptcyData,
    SBDailyCommentData,
    SBDailyForeclosureData,
    SBDailyLoanData,
    SBDailyPayHistoryData,
    SBDailyTransactionData,
    EOMTrialBalanceData,
    EOMTrustTrackingData,
)


@dataclass(frozen=True)
class ImportResult:
    model_name: str
    rows_read: int
    rows_inserted: int
    skipped_due_to_duplicates: bool = False
    skip_report: Optional[Dict[str, Any]] = None


def _normalize_header(value: str) -> str:
    s = str(value or "").strip()
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    s = re.sub(r"[^a-zA-Z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s)
    return s.strip("_").lower()


def _to_str_or_none(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None
    if pd.isna(value):
        return None
    return str(value)


def _read_statebridge_dataframe(file_path: Path) -> pd.DataFrame:
    suffix = file_path.suffix.lower()
    if suffix in {".xlsx", ".xls"}:
        # Use openpyxl for .xlsx, xlrd for .xls (older Excel format)
        engine = "openpyxl" if suffix == ".xlsx" else "xlrd"
        return pd.read_excel(
            file_path,
            sheet_name=0,
            dtype=str,
            engine=engine,
            keep_default_na=False,
            na_values=[],
        )

    if suffix == ".csv":
        return pd.read_csv(
            file_path,
            dtype=str,
            keep_default_na=False,
            na_values=[],
        )

    raise ValueError(f"Unsupported StateBridge file extension: {suffix}")


def _extract_file_date_iso(filename: str) -> Optional[str]:
    # Try YYYYMMDD format first (e.g., 20240131)
    m = re.search(r"(\d{8})", filename)
    if m:
        yyyymmdd = m.group(1)
        return f"{yyyymmdd[0:4]}-{yyyymmdd[4:6]}-{yyyymmdd[6:8]}"
    
    # Try M.D.YYYY or D.M.YYYY format (e.g., 1.1.2026 or 01.01.2026)
    # This handles files like "Trial Balance1.1.2026.xls"
    m = re.search(r"(\d{1,2})\.(\d{1,2})\.(\d{4})", filename)
    if m:
        month = m.group(1).zfill(2)
        day = m.group(2).zfill(2)
        year = m.group(3)
        return f"{year}-{month}-{day}"
    
    return None


def _infer_kind_from_filename(filename: str) -> str:
    name = filename.lower()
    if "_loandata_" in name:
        return "loan"
    if "_foreclosuredata_" in name:
        return "foreclosure"
    if "_bankruptcydata_" in name:
        return "bankruptcy"
    if "_commentdata_" in name:
        return "comment"
    if "_payhistoryreport_" in name:
        return "pay_history"
    if "_transactiondata_" in name:
        return "transaction"
    if "_armdata_" in name:
        return "arm"
    if "_trialbalancedata_" in name or "_eomtrialbalance_" in name or "trial balance" in name:
        return "eom_trial_balance"
    if "_trusttrackingdata_" in name or "_eomtrusttracking_" in name:
        return "eom_trust_tracking"
    raise ValueError(f"Unsupported StateBridge file name: {filename}")


def _model_for_kind(kind: str) -> Type[Any]:
    return {
        "loan": SBDailyLoanData,
        "foreclosure": SBDailyForeclosureData,
        "bankruptcy": SBDailyBankruptcyData,
        "comment": SBDailyCommentData,
        "pay_history": SBDailyPayHistoryData,
        "transaction": SBDailyTransactionData,
        "arm": SBDailyArmData,
        "eom_trial_balance": EOMTrialBalanceData,
        "eom_trust_tracking": EOMTrustTrackingData,
    }[kind]


def _unique_key_fields_for_model(model: Type[Any]) -> Tuple[str, ...]:
    if model is SBDailyLoanData:
        return ("date", "loan_number")
    if model is SBDailyArmData:
        return ("file_date", "loan_id")
    if model is SBDailyForeclosureData:
        return ("file_date", "loan_id")
    if model is SBDailyBankruptcyData:
        return ("file_date", "loan_id", "case_number")
    if model is SBDailyCommentData:
        return ("file_date", "loan_number", "comment_date", "department", "row_hash")
    if model is SBDailyPayHistoryData:
        return ("file_date", "loan_number")
    if model is SBDailyTransactionData:
        return ("file_date", "loan_transaction_id")
    if model is EOMTrialBalanceData:
        return ("file_date", "loan_id")
    if model is EOMTrustTrackingData:
        return ("file_date", "loan_id", "received_date")
    return tuple()


def _instance_key(instance: Any, key_fields: Tuple[str, ...]) -> Optional[Tuple[str, ...]]:
    values: list[str] = []
    for f in key_fields:
        v = getattr(instance, f, None)
        if v is None:
            return None
        s = str(v)
        if s == "":
            return None
        values.append(s)
    return tuple(values)


def _existing_keys_in_db(
    *,
    model: Type[Any],
    key_fields: Tuple[str, ...],
    file_date_iso: Optional[str],
    keys_in_file_unique: set[Tuple[str, ...]],
) -> set[Tuple[str, ...]]:
    if not file_date_iso or not key_fields:
        return set()

    if model is SBDailyLoanData:
        loan_numbers = {k[1] for k in keys_in_file_unique}
        existing = model.objects.filter(date=file_date_iso, loan_number__in=loan_numbers).values_list("date", "loan_number")
        return set(tuple(row) for row in existing)

    if model in {SBDailyArmData, SBDailyForeclosureData}:
        loan_ids = {k[1] for k in keys_in_file_unique}
        existing = model.objects.filter(file_date=file_date_iso, loan_id__in=loan_ids).values_list("file_date", "loan_id")
        return set(tuple(row) for row in existing)

    if model is SBDailyBankruptcyData:
        loan_ids = {k[1] for k in keys_in_file_unique}
        existing = model.objects.filter(file_date=file_date_iso, loan_id__in=loan_ids).values_list("file_date", "loan_id", "case_number")
        return set(tuple(row) for row in existing)

    if model is SBDailyCommentData:
        loan_numbers = {k[1] for k in keys_in_file_unique}
        existing = model.objects.filter(file_date=file_date_iso, loan_number__in=loan_numbers).values_list(
            "file_date",
            "loan_number",
            "comment_date",
            "department",
            "row_hash",
        )
        return set(tuple(row) for row in existing)

    if model is SBDailyPayHistoryData:
        loan_numbers = {k[1] for k in keys_in_file_unique}
        existing = model.objects.filter(file_date=file_date_iso, loan_number__in=loan_numbers).values_list("file_date", "loan_number")
        return set(tuple(row) for row in existing)

    if model is SBDailyTransactionData:
        txn_ids = {k[1] for k in keys_in_file_unique}
        existing = model.objects.filter(file_date=file_date_iso, loan_transaction_id__in=txn_ids).values_list(
            "file_date",
            "loan_transaction_id",
        )
        return set(tuple(row) for row in existing)

    if model is EOMTrialBalanceData:
        loan_ids = {k[1] for k in keys_in_file_unique}
        existing = model.objects.filter(file_date=file_date_iso, loan_id__in=loan_ids).values_list("file_date", "loan_id")
        return set(tuple(row) for row in existing)

    if model is EOMTrustTrackingData:
        loan_ids = {k[1] for k in keys_in_file_unique}
        existing = model.objects.filter(file_date=file_date_iso, loan_id__in=loan_ids).values_list(
            "file_date",
            "loan_id",
            "received_date",
        )
        return set(tuple(row) for row in existing)

    return set()


def _build_model_field_map(model: Type[Any]) -> Dict[str, str]:
    field_map: Dict[str, str] = {}
    for field in model._meta.fields:
        if getattr(field, "auto_created", False):
            continue
        field_map[_normalize_header(field.name)] = field.name
    return field_map


def _df_to_model_instances(
    df: pd.DataFrame,
    model: Type[Any],
    filename: str,
) -> Tuple[list[Any], int]:
    normalized_to_model_field = _build_model_field_map(model)
    column_map = {
        _normalize_header(col): col for col in df.columns.tolist() if isinstance(col, str)
    }

    file_date_iso = _extract_file_date_iso(filename)
    instances: list[Any] = []
    rows_read = 0

    for _, row in df.iterrows():
        rows_read += 1
        kwargs: Dict[str, Any] = {}

        for norm_key, original_col in column_map.items():
            model_field = normalized_to_model_field.get(norm_key)
            if not model_field:
                continue
            kwargs[model_field] = _to_str_or_none(row.get(original_col))

        if file_date_iso:
            if "file_date" in normalized_to_model_field.values() and not kwargs.get("file_date"):
                kwargs["file_date"] = file_date_iso
            if model is SBDailyLoanData and not kwargs.get("date"):
                kwargs["date"] = file_date_iso

        if model is SBDailyCommentData and not kwargs.get("row_hash"):
            hash_source = {
                "investor_id": kwargs.get("investor_id") or "",
                "file_date": kwargs.get("file_date") or "",
                "loan_number": kwargs.get("loan_number") or "",
                "investor_loan_number": kwargs.get("investor_loan_number") or "",
                "prior_servicer_loan_number": kwargs.get("prior_servicer_loan_number") or "",
                "comment_date": kwargs.get("comment_date") or "",
                "department": kwargs.get("department") or "",
                "comment": kwargs.get("comment") or "",
                "additional_notes": kwargs.get("additional_notes") or "",
            }
            payload = json.dumps(hash_source, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
            kwargs["row_hash"] = hashlib.sha256(payload.encode("utf-8")).hexdigest()

        instances.append(model(**kwargs))

    return instances, rows_read


def import_statebridge_file(
    file_path: Path,
    *,
    dry_run: bool,
    batch_size: int,
    report_skips: bool = False,
    max_skip_samples: int = 25,
) -> ImportResult:
    if not file_path.exists():
        raise FileNotFoundError(str(file_path))

    filename = file_path.name
    kind = _infer_kind_from_filename(filename)
    model = _model_for_kind(kind)

    df = _read_statebridge_dataframe(file_path)

    instances, rows_read = _df_to_model_instances(df, model, filename)

    file_date_iso = _extract_file_date_iso(filename)
    partition_filter: Dict[str, Any] = {}
    if file_date_iso:
        if model is SBDailyLoanData:
            partition_filter = {"date": file_date_iso}
        elif any(getattr(f, "name", None) == "file_date" for f in model._meta.fields):
            partition_filter = {"file_date": file_date_iso}

    skip_report: Optional[Dict[str, Any]] = None
    key_fields = _unique_key_fields_for_model(model)
    keys_in_file: list[Tuple[str, ...]] = []
    if report_skips and key_fields:
        for inst in instances:
            k = _instance_key(inst, key_fields)
            if k is not None:
                keys_in_file.append(k)

    counts: Optional[Counter] = None
    unique_keys_in_file: set[Tuple[str, ...]] = set()
    existing_keys_before: set[Tuple[str, ...]] = set()
    if report_skips and key_fields and keys_in_file:
        counts = Counter(keys_in_file)
        unique_keys_in_file = {k for k, c in counts.items() if c >= 1}
        existing_keys_before = _existing_keys_in_db(
            model=model,
            key_fields=key_fields,
            file_date_iso=file_date_iso,
            keys_in_file_unique=unique_keys_in_file,
        )

    if dry_run:
        if report_skips and key_fields and keys_in_file and counts is not None:
            duplicates_in_file = sum(c - 1 for c in counts.values() if c > 1)
            duplicates_in_db = len(unique_keys_in_file.intersection(existing_keys_before))

            duplicates_in_file_keys = [
                {"key": {f: k[i] for i, f in enumerate(key_fields)}, "count": counts[k]}
                for k, c in counts.items()
                if c > 1
            ]
            duplicates_in_file_keys.sort(key=lambda d: d["count"], reverse=True)

            duplicates_in_db_keys = [
                {"key": {f: k[i] for i, f in enumerate(key_fields)}}
                for k in sorted(unique_keys_in_file.intersection(existing_keys_before))
            ]

            skip_report = {
                "key_fields": list(key_fields),
                "duplicates_in_file": duplicates_in_file,
                "duplicates_in_db": duplicates_in_db,
                "duplicate_in_file_samples": duplicates_in_file_keys[: max(0, int(max_skip_samples))],
                "duplicate_in_db_samples": duplicates_in_db_keys[: max(0, int(max_skip_samples))],
            }

        return ImportResult(
            model_name=model.__name__,
            rows_read=rows_read,
            rows_inserted=0,
            skipped_due_to_duplicates=False,
            skip_report=skip_report,
        )

    before_count: Optional[int] = None
    if partition_filter:
        before_count = model.objects.filter(**partition_filter).count()

    try:
        with transaction.atomic():
            for start in range(0, len(instances), batch_size):
                chunk = instances[start : start + batch_size]
                model.objects.bulk_create(chunk, batch_size=len(chunk), ignore_conflicts=True)
    except IntegrityError:
        return ImportResult(
            model_name=model.__name__,
            rows_read=rows_read,
            rows_inserted=0,
            skipped_due_to_duplicates=True,
            skip_report=None,
        )

    if before_count is not None and partition_filter:
        after_count = model.objects.filter(**partition_filter).count()
        total_inserted = max(0, after_count - before_count)
    else:
        total_inserted = len(instances)

    if report_skips and key_fields and keys_in_file and counts is not None:
        duplicates_in_file = sum(c - 1 for c in counts.values() if c > 1)
        duplicates_in_db = len(unique_keys_in_file.intersection(existing_keys_before))

        duplicates_in_file_keys = [
            {"key": {f: k[i] for i, f in enumerate(key_fields)}, "count": counts[k]}
            for k, c in counts.items()
            if c > 1
        ]
        duplicates_in_file_keys.sort(key=lambda d: d["count"], reverse=True)

        duplicates_in_db_keys = [
            {"key": {f: k[i] for i, f in enumerate(key_fields)}}
            for k in sorted(unique_keys_in_file.intersection(existing_keys_before))
        ]

        skip_report = {
            "key_fields": list(key_fields),
            "duplicates_in_file": duplicates_in_file,
            "duplicates_in_db": duplicates_in_db,
            "duplicate_in_file_samples": duplicates_in_file_keys[: max(0, int(max_skip_samples))],
            "duplicate_in_db_samples": duplicates_in_db_keys[: max(0, int(max_skip_samples))],
        }

    return ImportResult(
        model_name=model.__name__,
        rows_read=rows_read,
        rows_inserted=total_inserted,
        skipped_due_to_duplicates=(rows_read > 0 and total_inserted == 0),
        skip_report=skip_report,
    )


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--file", dest="file_path", required=True)
        parser.add_argument("--batch-size", dest="batch_size", type=int, default=2000)
        parser.add_argument("--dry-run", dest="dry_run", action="store_true")
        parser.add_argument("--report-skips", dest="report_skips", action="store_true")
        parser.add_argument("--max-skip-samples", dest="max_skip_samples", type=int, default=25)

    def handle(self, *args, **options):
        file_path = Path(options["file_path"])
        batch_size = int(options["batch_size"])
        dry_run = bool(options["dry_run"])
        report_skips = bool(options.get("report_skips"))
        max_skip_samples = int(options.get("max_skip_samples") or 25)

        try:
            result = import_statebridge_file(
                file_path,
                dry_run=dry_run,
                batch_size=batch_size,
                report_skips=report_skips,
                max_skip_samples=max_skip_samples,
            )
        except Exception as exc:
            raise CommandError(str(exc))

        payload = {
            "file": str(file_path),
            "model": result.model_name,
            "rows_read": result.rows_read,
            "rows_inserted": result.rows_inserted,
            "skipped_due_to_duplicates": result.skipped_due_to_duplicates,
            "skip_report": result.skip_report,
            "dry_run": dry_run,
        }
        self.stdout.write(json.dumps(payload, indent=2))
