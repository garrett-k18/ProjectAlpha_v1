"""
Management command to import EOM Trial Balance files from FTPS server.

WHAT: Dedicated command for monthly trial balance imports (separate from daily servicer data).
WHY: Trial balance is monthly, not daily; needs separate cron schedule and filename filtering.
HOW: Filters FTPS files by "trial balance" in filename, downloads, and imports with header detection.

USAGE:
    # Import all trial balance files
    python manage.py import_trial_balance_from_ftps --batch-size 2000

    # Import latest only (typical for monthly cron)
    python manage.py import_trial_balance_from_ftps --latest-only --batch-size 2000

    # Force reprocess (ignores manifest)
    python manage.py import_trial_balance_from_ftps --force --batch-size 2000

    # Date filters
    python manage.py import_trial_balance_from_ftps --since-date 2026-01-01 --until-date 2026-01-31

CRON SETUP:
    # Run monthly on the 5th at 2 AM (after month-end files arrive)
    0 2 5 * * cd /path/to/project && python manage.py import_trial_balance_from_ftps --latest-only --batch-size 2000
"""

from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, Optional

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from etl.management.commands.import_statebridge_file import import_statebridge_file


class ImplicitFTP_TLS:
    """Implicit FTPS client that wraps socket in TLS before FTP handshake."""
    def __init__(self):
        from ftplib import FTP_TLS
        import ssl
        self._ftp = FTP_TLS()
        self._ftp.context = ssl.create_default_context()
        self._implicit = True
        self._host = None

    def connect(self, host: str, port: int):
        import socket
        import ssl
        # Create raw TCP socket
        sock = socket.create_connection((host, port), timeout=30)
        # Wrap in TLS immediately (implicit FTPS)
        context = ssl.create_default_context()
        # Store host for later use
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
        # Override to ensure SSL context has server_hostname for data channel
        import ssl
        self._ftp.context = ssl.create_default_context()
        # Monkey-patch the wrap_socket to include server_hostname
        original_wrap = self._ftp.context.wrap_socket
        def wrap_with_hostname(sock, **kwargs):
            kwargs['server_hostname'] = self._host
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
    """Connect to FTPS server (implicit or explicit TLS)."""
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


def _download_one(ftp, remote_name: str, local_path: Path):
    """Download a single file from FTPS."""
    import hashlib
    
    hasher = hashlib.sha256()
    bytes_written = 0
    
    with open(local_path, "wb") as f:
        def callback(data):
            nonlocal bytes_written
            f.write(data)
            hasher.update(data)
            bytes_written += len(data)
        
        ftp.retrbinary(f"RETR {remote_name}", callback)
    
    from dataclasses import dataclass
    
    @dataclass
    class DownloadResult:
        local_path: Path
        sha256: str
        bytes_written: int
    
    return DownloadResult(
        local_path=local_path,
        sha256=hasher.hexdigest(),
        bytes_written=bytes_written,
    )


def _load_manifest(staging_dir: Path) -> Dict[str, Any]:
    """Load manifest of previously processed files."""
    manifest_path = staging_dir / "manifest.json"
    if not manifest_path.exists():
        return {}
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_manifest(staging_dir: Path, manifest: Dict[str, Any]):
    """Save manifest of processed files."""
    manifest_path = staging_dir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)


def _is_processed(manifest: Dict[str, Any], remote_name: str) -> bool:
    """Check if file has been processed."""
    return remote_name in manifest


def _record_processed(manifest: Dict[str, Any], remote_name: str, metadata: Dict[str, Any]):
    """Record file as processed."""
    manifest[remote_name] = metadata


def _pick_latest_by_mtime(ftp, candidates: list[str]) -> Optional[str]:
    """Pick the file with the latest modification time."""
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


def _extract_file_date_from_name(filename: str) -> Optional[str]:
    """Extract date from filename in YYYY-MM-DD format."""
    # Try YYYYMMDD format first
    m = re.search(r"(\d{8})", filename)
    if m:
        yyyymmdd = m.group(1)
        return f"{yyyymmdd[0:4]}-{yyyymmdd[4:6]}-{yyyymmdd[6:8]}"
    
    # Try M.D.YYYY format (e.g., "Trial Balance1.1.2026.xls")
    m = re.search(r"(\d{1,2})\.(\d{1,2})\.(\d{4})", filename)
    if m:
        month = m.group(1).zfill(2)
        day = m.group(2).zfill(2)
        year = m.group(3)
        return f"{year}-{month}-{day}"
    
    return None


def _is_railway_runtime() -> bool:
    """Check if running in Railway environment."""
    return bool(
        os.getenv("RAILWAY_ENVIRONMENT")
        or os.getenv("RAILWAY_SERVICE_ID")
        or os.getenv("RAILWAY_PROJECT_ID")
    )


class Command(BaseCommand):
    help = "Import EOM Trial Balance files from FTPS server (monthly workflow)"

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
        
        if not quiet and _is_railway_runtime():
            quiet = True

        # Parse date filters
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
        staging_dir = Path(staging_dir_opt) if staging_dir_opt else (Path(settings.MEDIA_ROOT) / "statebridge" / "trial_balance")
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

            # FILTER: Only files with "trial balance" in the name (case-insensitive)
            candidates = [
                n for n in names
                if n.lower().endswith((".xls", ".xlsx")) and "trial balance" in n.lower()
            ]
            candidates.sort()

            # Filter by date range if specified
            if since_date or until_date:
                filtered = []
                for name in candidates:
                    file_date_str = _extract_file_date_from_name(name)
                    if file_date_str:
                        try:
                            file_date = datetime.datetime.strptime(file_date_str, "%Y-%m-%d").date()
                            include = True
                            if since_date and file_date < since_date:
                                include = False
                            if until_date and file_date > until_date:
                                include = False
                            if include:
                                filtered.append(name)
                        except ValueError:
                            pass
                candidates = filtered

            if latest_only and candidates:
                latest_by_mtime = _pick_latest_by_mtime(ftp, candidates)
                if latest_by_mtime:
                    candidates = [latest_by_mtime]
                else:
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
