from __future__ import annotations

import hashlib
import json
import os
import ssl
import time
import datetime
from dataclasses import dataclass
from ftplib import FTP_TLS
from pathlib import Path
import socket
from typing import Any, Dict, Optional

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from etl.management.commands.import_statebridge_file import import_statebridge_file


class ImplicitFTP_TLS(FTP_TLS):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._implicit = True

    def connect(self, host: str = "", port: int = 0, timeout: Any = -999):
        if host:
            self.host = host
        if port:
            self.port = port
        if timeout != -999:
            self.timeout = timeout

        # Implicit FTPS requires TLS negotiation immediately after TCP connect,
        # before the server sends the FTP welcome banner.
        self.sock = socket.create_connection((self.host, self.port), self.timeout)
        self.af = self.sock.family

        if self._implicit:
            self.sock = self.context.wrap_socket(self.sock, server_hostname=self.host)

        self.file = self.sock.makefile("r", encoding=self.encoding)
        self.welcome = self.getresp()
        return self.welcome


@dataclass
class DownloadedFile:
    local_path: Path
    remote_name: str
    sha256: str
    bytes_written: int


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _manifest_path(staging_dir: Path) -> Path:
    return staging_dir / "processed_manifest.json"


def _load_manifest(staging_dir: Path) -> Dict[str, Any]:
    path = _manifest_path(staging_dir)
    if not path.exists():
        return {"files": {}}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_manifest(staging_dir: Path, manifest: Dict[str, Any]) -> None:
    path = _manifest_path(staging_dir)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)


def _is_processed(manifest: Dict[str, Any], remote_name: str) -> bool:
    return remote_name in (manifest.get("files") or {})


def _record_processed(manifest: Dict[str, Any], remote_name: str, info: Dict[str, Any]) -> None:
    manifest.setdefault("files", {})[remote_name] = info


def _connect_ftps(
    *,
    host: str,
    port: int,
    username: str,
    password: str,
    implicit: bool,
) -> FTP_TLS:
    context = ssl.create_default_context()
    ftp: FTP_TLS
    if implicit:
        ftp = ImplicitFTP_TLS(context=context)
    else:
        ftp = FTP_TLS(context=context)

    ftp.connect(host=host, port=port, timeout=60)
    ftp.login(user=username, passwd=password)
    ftp.prot_p()
    return ftp


def _download_one(ftp: FTP_TLS, remote_name: str, dest: Path) -> DownloadedFile:
    dest.parent.mkdir(parents=True, exist_ok=True)
    bytes_written = 0

    with open(dest, "wb") as f:
        def _write(chunk: bytes):
            nonlocal bytes_written
            bytes_written += len(chunk)
            f.write(chunk)

        ftp.retrbinary(f"RETR {remote_name}", _write)

    sha256 = _sha256_file(dest)
    return DownloadedFile(local_path=dest, remote_name=remote_name, sha256=sha256, bytes_written=bytes_written)


def _ftps_mtime_epoch_seconds(ftp: FTP_TLS, remote_name: str) -> Optional[int]:
    """Return remote modified time in epoch seconds using MDTM.

    Many FTPS servers expose the "upload date" shown in FTP clients via MDTM.
    If the server doesn't support MDTM, return None.
    """
    try:
        resp = ftp.sendcmd(f"MDTM {remote_name}")
    except Exception:
        return None

    # Expected: "213 YYYYMMDDHHMMSS" (UTC)
    try:
        parts = (resp or "").strip().split()
        if len(parts) < 2:
            return None
        ts = parts[1]
        dt = datetime.datetime.strptime(ts, "%Y%m%d%H%M%S")
        dt = dt.replace(tzinfo=datetime.timezone.utc)
        return int(dt.timestamp())
    except Exception:
        return None


def _pick_latest_by_mtime(ftp: FTP_TLS, candidates: list[str]) -> Optional[str]:
    """Pick the newest remote file by server modified time."""
    best_name: Optional[str] = None
    best_ts: Optional[int] = None

    for name in candidates:
        ts = _ftps_mtime_epoch_seconds(ftp, name)
        if ts is None:
            continue
        if best_ts is None or ts > best_ts:
            best_ts = ts
            best_name = name
    return best_name


def _matches_kind(remote_name: str, kind: str) -> bool:
    name = (remote_name or "").lower()
    kind_norm = (kind or "").strip().lower()

    kind_aliases = {
        "loan": {"loan", "loandata"},
        "foreclosure": {"foreclosure", "foreclosuredata"},
        "bankruptcy": {"bankruptcy", "bankruptcydata"},
        "comment": {"comment", "commentdata"},
        "pay_history": {"pay_history", "payhistory", "pay_history_report", "payhistoryreport"},
        "transaction": {"transaction", "transactiondata"},
        "arm": {"arm", "armdata"},
    }

    kind_key = None
    for canonical, aliases in kind_aliases.items():
        if kind_norm in aliases:
            kind_key = canonical
            break

    if not kind_key:
        return False

    return {
        "loan": "_loandata_" in name,
        "foreclosure": "_foreclosuredata_" in name,
        "bankruptcy": "_bankruptcydata_" in name,
        "comment": "_commentdata_" in name,
        "pay_history": "_payhistoryreport_" in name,
        "transaction": "_transactiondata_" in name,
        "arm": "_armdata_" in name,
    }[kind_key]


def _is_railway_runtime() -> bool:
    return bool(
        os.getenv("RAILWAY_ENVIRONMENT")
        or os.getenv("RAILWAY_SERVICE_ID")
        or os.getenv("RAILWAY_PROJECT_ID")
    )


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--batch-size", dest="batch_size", type=int, default=2000)
        parser.add_argument("--dry-run", dest="dry_run", action="store_true")
        parser.add_argument("--max-files", dest="max_files", type=int, default=0)
        parser.add_argument("--force", dest="force", action="store_true")
        parser.add_argument("--staging-dir", dest="staging_dir", default="")
        parser.add_argument("--keep-local", dest="keep_local", action="store_true")
        parser.add_argument("--kind", dest="kind", default="")
        parser.add_argument("--latest-only", dest="latest_only", action="store_true")
        parser.add_argument("--report-skips", dest="report_skips", action="store_true")
        parser.add_argument("--max-skip-samples", dest="max_skip_samples", type=int, default=25)
        parser.add_argument("--quiet", dest="quiet", action="store_true")

    def handle(self, *args, **options):
        batch_size = int(options["batch_size"])
        dry_run = bool(options["dry_run"])
        max_files = int(options["max_files"])
        force = bool(options["force"])
        keep_local = bool(options.get("keep_local"))
        kind = str(options.get("kind") or "").strip()
        latest_only = bool(options.get("latest_only"))
        report_skips = bool(options.get("report_skips"))
        max_skip_samples = int(options.get("max_skip_samples") or 25)
        quiet = bool(options.get("quiet"))
        if not quiet and _is_railway_runtime():
            quiet = True

        staging_dir_opt = str(options.get("staging_dir") or "").strip()
        staging_dir = Path(staging_dir_opt) if staging_dir_opt else (Path(settings.MEDIA_ROOT) / "statebridge" / "ftps")
        staging_dir.mkdir(parents=True, exist_ok=True)

        host = os.getenv("STATEBRIDGE_FTPS_HOST", "").strip()
        username = os.getenv("STATEBRIDGE_FTPS_USERNAME", "").strip()
        password = os.getenv("STATEBRIDGE_FTPS_PASSWORD", "").strip()
        remote_dir = os.getenv("STATEBRIDGE_FTPS_REMOTE_DIR", "/FirstLienCapital/To_FirstLienCapital").strip()

        port = int(os.getenv("STATEBRIDGE_FTPS_PORT", "990").strip() or "990")
        implicit = os.getenv("STATEBRIDGE_FTPS_IMPLICIT", "true").strip().lower() in {"1", "true", "yes"}

        if not host or not username or not password:
            raise CommandError("Missing STATEBRIDGE_FTPS_HOST/STATEBRIDGE_FTPS_USERNAME/STATEBRIDGE_FTPS_PASSWORD")

        if "your_username_here" in username or "your_password_here" in password:
            raise CommandError("StateBridge credentials in .env are still placeholders. Please update them with real values.")

        manifest = _load_manifest(staging_dir)

        try:
            ftp = _connect_ftps(host=host, port=port, username=username, password=password, implicit=implicit)
        except Exception as exc:
            import traceback
            self.stderr.write(traceback.format_exc())
            raise CommandError(f"FTPS connect failed: {repr(exc)}")

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
                if n.lower().startswith("firstliencapital_") and n.lower().endswith(".xlsx")
            ]
            candidates.sort()

            if kind:
                candidates = [n for n in candidates if _matches_kind(n, kind)]

            if latest_only and candidates:
                latest_by_mtime = _pick_latest_by_mtime(ftp, candidates)
                if latest_by_mtime:
                    candidates = [latest_by_mtime]
                else:
                    # Fallback: filename sort (works well when suffix includes YYYYMMDD)
                    candidates = [candidates[-1]]

            processed = []
            skipped = []
            errors = []

            count_processed = 0
            for remote_name in candidates:
                if max_files and count_processed >= max_files:
                    break

                if not force and _is_processed(manifest, remote_name):
                    local_existing = staging_dir / remote_name
                    deleted_local = False
                    if not keep_local and local_existing.exists():
                        try:
                            local_existing.unlink(missing_ok=True)
                            deleted_local = True
                        except Exception:
                            deleted_local = False
                    skipped.append(
                        {
                            "remote": remote_name,
                            "reason": "already_processed",
                            "deleted_local": deleted_local,
                        }
                    )
                    continue

                local_path = staging_dir / remote_name

                if dry_run:
                    processed.append({"remote": remote_name, "local": str(local_path), "dry_run": True})
                    count_processed += 1
                    continue

                try:
                    downloaded = _download_one(ftp, remote_name, local_path)
                    import_result = import_statebridge_file(
                        downloaded.local_path,
                        dry_run=False,
                        batch_size=batch_size,
                        report_skips=report_skips,
                        max_skip_samples=max_skip_samples,
                    )
                    if import_result.skipped_due_to_duplicates:
                        _record_processed(
                            manifest,
                            remote_name,
                            {
                                "remote_dir": remote_dir,
                                "downloaded_at": int(time.time()),
                                "sha256": downloaded.sha256,
                                "bytes": downloaded.bytes_written,
                                "model": import_result.model_name,
                                "rows_read": import_result.rows_read,
                                "rows_inserted": import_result.rows_inserted,
                                "skipped_due_to_duplicates": True,
                                "skip_report": import_result.skip_report if report_skips else None,
                            },
                        )
                        _save_manifest(staging_dir, manifest)
                        skipped.append(
                            {
                                "remote": remote_name,
                                "local": str(downloaded.local_path),
                                "sha256": downloaded.sha256,
                                "reason": "duplicate_in_db",
                                "model": import_result.model_name,
                                "skip_report": import_result.skip_report if report_skips else None,
                            }
                        )
                        if not keep_local:
                            try:
                                downloaded.local_path.unlink(missing_ok=True)
                            except Exception:
                                pass
                        count_processed += 1
                        continue
                    _record_processed(
                        manifest,
                        remote_name,
                        {
                            "remote_dir": remote_dir,
                            "downloaded_at": int(time.time()),
                            "sha256": downloaded.sha256,
                            "bytes": downloaded.bytes_written,
                            "model": import_result.model_name,
                            "rows_read": import_result.rows_read,
                            "rows_inserted": import_result.rows_inserted,
                            "skipped_due_to_duplicates": False,
                            "skip_report": import_result.skip_report if report_skips else None,
                        },
                    )
                    _save_manifest(staging_dir, manifest)
                    processed.append(
                        {
                            "remote": remote_name,
                            "local": str(downloaded.local_path),
                            "sha256": downloaded.sha256,
                            "model": import_result.model_name,
                            "rows_read": import_result.rows_read,
                            "rows_inserted": import_result.rows_inserted,
                            "skip_report": import_result.skip_report if report_skips else None,
                        }
                    )
                    if not keep_local:
                        try:
                            downloaded.local_path.unlink(missing_ok=True)
                        except Exception:
                            pass
                    count_processed += 1
                except Exception as exc:
                    errors.append({"remote": remote_name, "error": str(exc)})

        if quiet:
            payload = {
                "remote_dir": remote_dir,
                "dry_run": dry_run,
                "force": force,
                "max_files": max_files,
                "kind": kind or None,
                "latest_only": latest_only,
                "counts": {
                    "processed": len(processed),
                    "skipped": len(skipped),
                    "errors": len(errors),
                },
                "error_samples": errors[:5],
            }
            self.stdout.write(json.dumps(payload, separators=(",", ":")))
        else:
            payload = {
                "remote_dir": remote_dir,
                "staging_dir": str(staging_dir),
                "dry_run": dry_run,
                "force": force,
                "max_files": max_files,
                "processed": processed,
                "skipped": skipped,
                "errors": errors,
            }
            self.stdout.write(json.dumps(payload, indent=2))
