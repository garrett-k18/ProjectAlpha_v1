"""
Management command: import_fc_timelines_csv

What:
- Imports/Upserts foreclosure timelines from a CSV in the same format as
  the API export `matrix_csv` in `core/views/views_assumptions.py`.

Usage:
  python manage.py import_fc_timelines_csv <csv_path> [--strict]

Args:
- csv_path: Path to CSV file. Columns required: state_code,status_code
- Optional columns: duration_days,cost_avg,notes
- --strict: If provided, duration_days must be an integer; otherwise values
            with decimals will be rounded to the nearest integer.

Notes:
- cost_avg allows decimals.
- Unknown state_code or status_code will cause the row to be skipped and reported.
- status_code will be created if it matches FCStatus.STATUS_CHOICES but doesn't exist yet (with correct order).

Related:
- View importer: `FCTimelinesViewSet.import_matrix_csv()`
  Path: projectalphav1/core/views/views_assumptions.py
"""
from __future__ import annotations

import csv
import os
from typing import Optional

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import StateReference, FCStatus, FCTimelines


class Command(BaseCommand):
    help = "Import/Upsert foreclosure timelines from a matrix CSV file"

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str, help="Path to the matrix CSV file")
        parser.add_argument(
            "--strict",
            action="store_true",
            help="Require duration_days to be an integer; otherwise round floats",
        )

    def handle(self, *args, **options):
        csv_path: str = options["csv_path"]
        strict: bool = options["strict"]

        if not os.path.exists(csv_path):
            raise CommandError(f"CSV file not found: {csv_path}")

        created = 0
        updated = 0
        errors = []
        processed = 0

        def get_or_create_status_by_code(code: str) -> FCStatus:
            fc = FCStatus.objects.filter(status=code).first()
            if fc:
                return fc
            for idx, (c, display) in enumerate(FCStatus.STATUS_CHOICES, start=1):
                if c == code:
                    return FCStatus.objects.create(
                        status=code,
                        order=idx,
                        notes=f"Autocreated from CSV import ({display})",
                    )
            raise ValueError(f"Unknown status_code '{code}'")

        self.stdout.write(self.style.NOTICE(f"Reading: {csv_path}"))
        try:
            with open(csv_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                required_cols = {"state_code", "status_code"}
                missing = required_cols - set(reader.fieldnames or [])
                if missing:
                    raise CommandError(
                        f"CSV missing required columns: {', '.join(sorted(missing))}"
                    )

                with transaction.atomic():
                    for i, row in enumerate(reader, start=2):  # header is line 1
                        processed += 1
                        try:
                            state_code = (row.get("state_code") or "").strip()
                            status_code = (row.get("status_code") or "").strip()
                            if not state_code or not status_code:
                                raise ValueError("Missing required state_code or status_code")

                            try:
                                st = StateReference.objects.get(state_code=state_code)
                            except StateReference.DoesNotExist:
                                raise ValueError(f"Unknown state_code '{state_code}'")

                            fc = get_or_create_status_by_code(status_code)

                            # Parse duration_days (int or rounded float if non-strict)
                            duration_days_raw: Optional[str] = row.get("duration_days")
                            duration_days: Optional[int]
                            if duration_days_raw is None or str(duration_days_raw).strip() == "":
                                duration_days = None
                            else:
                                s = str(duration_days_raw).strip()
                                if strict:
                                    # require pure integer
                                    if not s.isdigit() and not (s.startswith("-") and s[1:].isdigit()):
                                        raise ValueError(
                                            f"duration_days must be integer in strict mode, got '{s}'"
                                        )
                                    duration_days = int(s)
                                else:
                                    # be forgiving: convert to float then round
                                    try:
                                        duration_days = int(round(float(s)))
                                    except Exception:
                                        raise ValueError(
                                            f"Invalid duration_days value '{s}' (cannot parse as number)"
                                        )

                            # Parse cost_avg (optional float)
                            cost_avg_raw = row.get("cost_avg")
                            cost_avg = (
                                float(cost_avg_raw)
                                if (cost_avg_raw is not None and str(cost_avg_raw).strip() != "")
                                else None
                            )

                            notes = (row.get("notes") or "").strip()

                            timeline, created_flag = FCTimelines.objects.get_or_create(
                                state=st, fc_status=fc
                            )
                            timeline.duration_days = duration_days
                            timeline.cost_avg = cost_avg
                            timeline.notes = notes
                            timeline.save()
                            if created_flag:
                                created += 1
                            else:
                                updated += 1
                        except Exception as row_err:
                            errors.append({"row": i, "error": str(row_err), "data": row})

                    if errors:
                        # Surface first few errors, but still roll back to avoid partial import
                        sample = ", ".join(
                            [f"row {e['row']}: {e['error']}" for e in errors[:5]]
                        )
                        raise CommandError(
                            f"Import aborted with {len(errors)} row error(s). Examples: {sample}"
                        )
        except CommandError:
            raise
        except Exception as e:
            raise CommandError(str(e))

        self.stdout.write(
            self.style.SUCCESS(
                f"Import successful. processed={processed}, created={created}, updated={updated}"
            )
        )
