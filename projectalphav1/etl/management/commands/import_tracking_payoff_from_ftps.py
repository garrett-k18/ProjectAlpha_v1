"""
Import Tracking Payoff files from FTPS (monthly).

- Filters files containing "tracking payoff" (case-insensitive) with extensions csv/xls/xlsx
- Extracts file_date from filename (YYYYMMDD or M.D.YYYY patterns)
- Skips already-processed files via manifest.json in staging dir
- Loads into raw landing table EOMTrackingPayoffData (all fields as strings)
- bulk_create(ignore_conflicts=True) to skip dup rows (unique on file_date+loan_id)
"""

from __future__ import annotations

import os
import re
import json
import hashlib
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from etl.models import EOMTrackingPayoffData


class ImplicitFTP_TLS:
    """Implicit FTPS client that wraps socket in TLS before FTP handshake."""

    def __init__(self):
        from ftplib import FTP_TLS
        import ssl

        self._ftp = FTP_TLS()
        self._ftp.context = ssl.create_default_context()
        self._host = None

    def connect(self, host: str, port: int):
        import socket
        import ssl

        sock = socket.create_connection((host, port), timeout=30)
        context = ssl.create_default_context()
        self._host = host
        self._ftp.host = host
        self._ftp.sock = context.wrap_socket(sock, server_hostname=host)
        self._ftp.af = self._ftp.sock.family
        self._ftp.file = self._ftp.sock.makefile("r", encoding="utf-8")
        self._ftp.welcome = self._ftp.getresp()
        return self._ftp.welcome

    def login(self, user: str, passwd: str):
        return self._ftp.login(user, passwd)

    def prot_p(self):
        import ssl

        self._ftp.context = ssl.create_default_context()
        original_wrap = self._ftp.context.wrap_socket

        def wrap_with_hostname(sock, **kwargs):
            kwargs["server_hostname"] = self._host
            return original_wrap(sock, **kwargs)

        self._ftp.context.wrap_socket = wrap_with_hostname
        return self._ftp.prot_p()

    def cwd(self, path: str):
        return self._ftp.cwd(path)

    def nlst(self):
        return self._ftp.nlst()

    def sendcmd(self, cmd: str):
        return self._ftp.sendcmd(cmd)

    def retrbinary(self, cmd: str, callback):
        return self._ftp.retrbinary(cmd, callback)

    def quit(self):
        return self._ftp.quit()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        try:
            self.quit()
        except Exception:
            pass


def _connect_ftps(*, host: str, port: int, username: str, password: str, implicit: bool):
    from ftplib import FTP_TLS

    if implicit:
        ftp = ImplicitFTP_TLS()
        ftp.connect(host, port)
    else:
        ftp = FTP_TLS()
        ftp.connect(host, port)
        ftp.auth()

    ftp.login(username, password)
    ftp.prot_p()
    return ftp


def _load_manifest(staging_dir: Path) -> Dict[str, Any]:
    path = staging_dir / "manifest.json"
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_manifest(staging_dir: Path, manifest: Dict[str, Any]):
    path = staging_dir / "manifest.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)


def _is_processed(manifest: Dict[str, Any], remote_name: str) -> bool:
    return remote_name in manifest


def _record_processed(manifest: Dict[str, Any], remote_name: str, metadata: Dict[str, Any]):
    manifest[remote_name] = metadata


def _extract_file_date_from_name(filename: str) -> Optional[str]:
    name = filename.lower()
    m = re.search(r"(\d{8})", name)
    if m:
        yyyymmdd = m.group(1)
        return f"{yyyymmdd[0:4]}-{yyyymmdd[4:6]}-{yyyymmdd[6:8]}"
    m = re.search(r"(\d{1,2})\.(\d{1,2})\.(\d{4})", name)
    if m:
        month = m.group(1).zfill(2)
        day = m.group(2).zfill(2)
        year = m.group(3)
        return f"{year}-{month}-{day}"
    return None


def _download_one(ftp, remote_name: str, local_path: Path):
    hasher = hashlib.sha256()
    bytes_written = 0
    with open(local_path, "wb") as f:
        def callback(data):
            nonlocal bytes_written
            f.write(data)
            hasher.update(data)
            bytes_written += len(data)
        ftp.retrbinary(f"RETR {remote_name}", callback)
    return hasher.hexdigest(), bytes_written


def _find_header_row(df: pd.DataFrame) -> Optional[int]:
    expected = {"loan id", "investor loan id", "received date", "due date"}
    for idx, row in df.iterrows():
        normalized = {str(v).strip().lower() for v in row.tolist() if isinstance(v, str)}
        if len(expected.intersection(normalized)) >= 3:
            return idx
    return None


def _parse_file(local_path: Path, file_date_hint: Optional[str]) -> list[EOMTrackingPayoffData]:
    suffix = local_path.suffix.lower()
    if suffix in {".xlsx", ".xls"}:
        engine = "openpyxl" if suffix == ".xlsx" else "xlrd"
        df = pd.read_excel(local_path, sheet_name=0, dtype=str, engine=engine, keep_default_na=False, na_values=[], header=None)
    else:
        df = pd.read_csv(local_path, dtype=str, keep_default_na=False, na_values=[], header=None)

    header_idx = _find_header_row(df)
    if header_idx is None:
        return []
    columns = [c if isinstance(c, str) else "" for c in df.iloc[header_idx].tolist()]
    data = df.iloc[header_idx + 1 :].copy()
    data.columns = columns
    data = data.reset_index(drop=True)

    records: list[EOMTrackingPayoffData] = []
    for _, row in data.iterrows():
        if all((not str(v).strip()) for v in row.tolist()):
            continue
        kwargs = {
            "file_date": file_date_hint,
            "loan_id": row.get("Loan ID"),
            "investor_loan_id": row.get("Investor Loan ID"),
            "received_date": row.get("Received Date"),
            "due_date": row.get("Due Date"),
            "principal_paid_off": row.get("Principal Paid Off"),
            "interest_collected": row.get("Interest Collected"),
            "sf_collected": row.get("SF Collected"),
            "net_interest": row.get("Net Interest"),
            "description": row.get("Description"),
            "payoff_reason": row.get("Payoff Reason"),
        }
        records.append(EOMTrackingPayoffData(**kwargs))
    return records


class Command(BaseCommand):
    help = "Import Tracking Payoff files from FTPS server (monthly workflow)"

    def add_arguments(self, parser):
        parser.add_argument("--batch-size", dest="batch_size", type=int, default=2000)
        parser.add_argument("--dry-run", dest="dry_run", action="store_true")
        parser.add_argument("--max-files", dest="max_files", type=int, default=0)
        parser.add_argument("--force", dest="force", action="store_true")
        parser.add_argument("--staging-dir", dest="staging_dir", default="")
        parser.add_argument("--keep-local", dest="keep_local", action="store_true")
        parser.add_argument("--latest-only", dest="latest_only", action="store_true")
        parser.add_argument("--report-skips", dest="report_skips", action="store_true")
        parser.add_argument("--max-skip-samples", dest="max_skip_samples", type=int, default=25)
        parser.add_argument("--quiet", dest="quiet", action="store_true")
        parser.add_argument("--since-date", dest="since_date", default="", help="Filter files from this date onwards (YYYY-MM-DD)")
        parser.add_argument("--until-date", dest="until_date", default="", help="Filter files up to this date (YYYY-MM-DD)")

    def handle(self, *args, **options):
        import datetime

        batch_size = int(options["batch_size"])
        dry_run = bool(options["dry_run"])
        max_files = int(options["max_files"])
        force = bool(options["force"])
        keep_local = bool(options.get("keep_local"))
        latest_only = bool(options.get("latest_only"))
        report_skips = bool(options.get("report_skips"))
        max_skip_samples = int(options.get("max_skip_samples") or 25)
        quiet = bool(options.get("quiet"))
        since_date_str = str(options.get("since_date") or "").strip()
        until_date_str = str(options.get("until_date") or "").strip()

        since_date = None
        until_date = None
        if since_date_str:
            try:
                since_date = datetime.datetime.strptime(since_date_str, "%Y-%m-%d").date()
            except ValueError:
                raise CommandError(f"Invalid --since-date format. Use YYYY-MM-DD, got: {since_date_str}")
        if until_date_str:
            try:
                until_date = datetime.datetime.strptime(until_date_str, "%Y-%m-%d").date()
            except ValueError:
                raise CommandError(f"Invalid --until-date format. Use YYYY-MM-DD, got: {until_date_str}")

        staging_dir_opt = str(options.get("staging_dir") or "").strip()
        staging_dir = Path(staging_dir_opt) if staging_dir_opt else (Path(settings.MEDIA_ROOT) / "statebridge" / "tracking_payoff")
        staging_dir.mkdir(parents=True, exist_ok=True)

        host = os.getenv("STATEBRIDGE_FTPS_HOST", "").strip()
        username = os.getenv("STATEBRIDGE_FTPS_USERNAME", "").strip()
        password = os.getenv("STATEBRIDGE_FTPS_PASSWORD", "").strip()
        remote_dir = os.getenv("STATEBRIDGE_FTPS_REMOTE_DIR", "/FirstLienCapital/To_FirstLienCapital").strip()

        port = int(os.getenv("STATEBRIDGE_FTPS_PORT", "990").strip() or "990")
        implicit = os.getenv("STATEBRIDGE_FTPS_IMPLICIT", "true").strip().lower() in {"1", "true", "yes"}

        if not host or not username or not password:
            raise CommandError("Missing STATEBRIDGE_FTPS_HOST/STATEBRIDGE_FTPS_USERNAME/STATEBRIDGE_FTPS_PASSWORD")

        manifest = _load_manifest(staging_dir)

        try:
            ftp = _connect_ftps(host=host, port=port, username=username, password=password, implicit=implicit)
        except Exception as exc:
            import traceback
            self.stderr.write(traceback.format_exc())
            raise CommandError(f"FTPS connect failed: {repr(exc)}")

        processed = 0
        skipped = []

        with ftp:
            try:
                ftp.cwd(remote_dir)
            except Exception as exc:
                raise CommandError(f"FTPS cwd failed: {exc}")

            try:
                names = ftp.nlst()
            except Exception as exc:
                raise CommandError(f"FTPS list failed: {exc}")

            candidates = [
                n for n in names
                if any(n.lower().endswith(ext) for ext in (".csv", ".xlsx", ".xls"))
                and "tracking payoff" in n.lower()
            ]
            candidates.sort()

            if since_date or until_date:
                filtered = []
                for name in candidates:
                    file_date_str = _extract_file_date_from_name(name)
                    if file_date_str:
                        try:
                            file_date = datetime.datetime.strptime(file_date_str, "%Y-%m-%d").date()
                            if since_date and file_date < since_date:
                                continue
                            if until_date and file_date > until_date:
                                continue
                            filtered.append(name)
                        except ValueError:
                            continue
                candidates = filtered

            if latest_only and candidates:
                latest = self._pick_latest_by_mtime(ftp, candidates)
                candidates = [latest] if latest else []

            if max_files and max_files > 0:
                candidates = candidates[:max_files]

            for remote_name in candidates:
                if not force and _is_processed(manifest, remote_name):
                    skipped.append(remote_name)
                    continue

                local_path = staging_dir / remote_name
                sha256, bytes_written = _download_one(ftp, remote_name, local_path)
                file_date_hint = _extract_file_date_from_name(remote_name)

                if dry_run:
                    processed += 1
                    if not keep_local:
                        local_path.unlink(missing_ok=True)
                    _record_processed(manifest, remote_name, {"sha256": sha256, "bytes": bytes_written})
                    continue

                records = _parse_file(local_path, file_date_hint)
                if not records:
                    skipped.append(remote_name)
                else:
                    EOMTrackingPayoffData.objects.bulk_create(records, batch_size=batch_size, ignore_conflicts=True)
                    processed += 1
                    _record_processed(manifest, remote_name, {"sha256": sha256, "bytes": bytes_written, "rows": len(records)})

                if not keep_local:
                    local_path.unlink(missing_ok=True)

        _save_manifest(staging_dir, manifest)

        if not quiet:
            self.stdout.write(self.style.SUCCESS(f"Processed files: {processed}"))
            if skipped and report_skips:
                sample = skipped[:max_skip_samples]
                self.stdout.write(self.style.WARNING(f"Skipped (already processed or empty): {len(skipped)}"))
                for name in sample:
                    self.stdout.write(f"  - {name}")

    def _pick_latest_by_mtime(self, ftp, candidates: list[str]) -> Optional[str]:
        latest = None
        latest_mtime = None
        for name in candidates:
            try:
                mtime_str = ftp.sendcmd(f"MDTM {name}")
                mtime = mtime_str.split()[-1]
                if latest_mtime is None or mtime > latest_mtime:
                    latest_mtime = mtime
                    latest = name
            except Exception:
                continue
        return latest
