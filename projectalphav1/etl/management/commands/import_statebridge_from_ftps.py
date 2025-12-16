from __future__ import annotations

import hashlib
import json
import os
import ssl
import time
from dataclasses import dataclass
from ftplib import FTP_TLS
from pathlib import Path
from typing import Any, Dict, Optional

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from etl.management.commands.import_statebridge_file import import_statebridge_file


class ImplicitFTP_TLS(FTP_TLS):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._implicit = True

    def connect(self, host: str = "", port: int = 0, timeout: Any = -999):
        super().connect(host=host, port=port, timeout=timeout)
        if self._implicit:
            self.sock = self.context.wrap_socket(self.sock, server_hostname=self.host)
            self.file = self.sock.makefile("r", encoding=self.encoding)
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


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--batch-size", dest="batch_size", type=int, default=2000)
        parser.add_argument("--dry-run", dest="dry_run", action="store_true")
        parser.add_argument("--max-files", dest="max_files", type=int, default=0)
        parser.add_argument("--force", dest="force", action="store_true")
        parser.add_argument("--staging-dir", dest="staging_dir", default="")

    def handle(self, *args, **options):
        batch_size = int(options["batch_size"])
        dry_run = bool(options["dry_run"])
        max_files = int(options["max_files"])
        force = bool(options["force"])

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

        manifest = _load_manifest(staging_dir)

        try:
            ftp = _connect_ftps(host=host, port=port, username=username, password=password, implicit=implicit)
        except Exception as exc:
            raise CommandError(f"FTPS connect failed: {exc}")

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

            processed = []
            skipped = []
            errors = []

            count_processed = 0
            for remote_name in candidates:
                if max_files and count_processed >= max_files:
                    break

                if not force and _is_processed(manifest, remote_name):
                    skipped.append({"remote": remote_name, "reason": "already_processed"})
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
                    )
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
                        },
                    )
                    _save_manifest(staging_dir, manifest)
                    processed.append({"remote": remote_name, "local": str(downloaded.local_path), "sha256": downloaded.sha256})
                    count_processed += 1
                except Exception as exc:
                    errors.append({"remote": remote_name, "error": str(exc)})

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
