from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Tuple, Type

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
)


@dataclass(frozen=True)
class ImportResult:
    model_name: str
    rows_read: int
    rows_inserted: int
    skipped_due_to_duplicates: bool = False


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
    m = re.search(r"(\d{8})", filename)
    if not m:
        return None
    yyyymmdd = m.group(1)
    return f"{yyyymmdd[0:4]}-{yyyymmdd[4:6]}-{yyyymmdd[6:8]}"


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
    }[kind]


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

        instances.append(model(**kwargs))

    return instances, rows_read


def import_statebridge_file(
    file_path: Path,
    *,
    dry_run: bool,
    batch_size: int,
) -> ImportResult:
    if not file_path.exists():
        raise FileNotFoundError(str(file_path))

    filename = file_path.name
    kind = _infer_kind_from_filename(filename)
    model = _model_for_kind(kind)

    df = _read_statebridge_dataframe(file_path)

    instances, rows_read = _df_to_model_instances(df, model, filename)

    if dry_run:
        return ImportResult(model_name=model.__name__, rows_read=rows_read, rows_inserted=0)

    total_inserted = 0
    try:
        with transaction.atomic():
            for start in range(0, len(instances), batch_size):
                chunk = instances[start : start + batch_size]
                model.objects.bulk_create(chunk, batch_size=len(chunk))
                total_inserted += len(chunk)
    except IntegrityError:
        return ImportResult(
            model_name=model.__name__,
            rows_read=rows_read,
            rows_inserted=0,
            skipped_due_to_duplicates=True,
        )

    return ImportResult(
        model_name=model.__name__,
        rows_read=rows_read,
        rows_inserted=total_inserted,
    )


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--file", dest="file_path", required=True)
        parser.add_argument("--batch-size", dest="batch_size", type=int, default=2000)
        parser.add_argument("--dry-run", dest="dry_run", action="store_true")

    def handle(self, *args, **options):
        file_path = Path(options["file_path"])
        batch_size = int(options["batch_size"])
        dry_run = bool(options["dry_run"])

        try:
            result = import_statebridge_file(file_path, dry_run=dry_run, batch_size=batch_size)
        except Exception as exc:
            raise CommandError(str(exc))

        payload = {
            "file": str(file_path),
            "model": result.model_name,
            "rows_read": result.rows_read,
            "rows_inserted": result.rows_inserted,
            "skipped_due_to_duplicates": result.skipped_due_to_duplicates,
            "dry_run": dry_run,
        }
        self.stdout.write(json.dumps(payload, indent=2))
