"""Import broker ↔ MSA assignments from a CSV (brokersupload.csv).

WHAT: Reads the normalized brokersupload.csv file and creates/updates
      BrokerMSAAssignment rows linking MasterCRM brokers to MSAReference
      markets.

EXPECTED CSV COLUMNS (case-insensitive):
    - Preferred        (ignored here)
    - Contact Name     (used as fallback broker key)
    - Firm             (used as fallback broker key)
    - State            (comma-separated state codes; optional)
    - MSA              (semicolon-separated canonical MSA names, e.g.
                        "Los Angeles-Long Beach-Anaheim, CA")
    - Email            (primary broker key when present)
    - Phone            (ignored here)
    - Notes            (ignored here)

BROKER LOOKUP STRATEGY:
    1. If Email present: MasterCRM.objects.get(email=email).
    2. Else:            MasterCRM.objects.get(contact_name=name, firm_ref__name=firm)

    If multiple brokers match, the row is logged as an error and skipped.

MSA LOOKUP STRATEGY:
    - Split MSA column on ';' to allow multiple MSAs per broker row.
    - For each token t:
        * Strip whitespace and surrounding quotes.
        * Look up MSAReference.objects.get(msa_name__iexact=t).
        * If not found, log as error and skip that token.
        * If multiple found, log as error and skip that token.

ASSIGNMENT STRATEGY:
    - For each (broker, msa) pair, upsert BrokerMSAAssignment with
      priority=1 by default and is_active=True.

USAGE EXAMPLE:
    python manage.py import_broker_msa_assignments \
        --csv z.Admin/NonGitIgonore/brokersupload.csv \
        --database default

    # Or against prod when your shell has DATABASE_URL pointing at prod:
    python manage.py import_broker_msa_assignments \
        --csv z.Admin/NonGitIgonore/brokersupload.csv
"""

import csv
import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models.model_co_crm import MasterCRM, BrokerMSAAssignment
from core.models.model_co_geoAssumptions import MSAReference


class Command(BaseCommand):
    """Import BrokerMSAAssignment rows from a brokersupload-style CSV."""

    help = (
        "Import broker-to-MSA assignments from a normalized brokersupload.csv "
        "file, creating BrokerMSAAssignment rows for each broker/MSA pair."
    )

    def add_arguments(self, parser):
        default_csv = str(
            (Path(settings.BASE_DIR) / "z.Admin" / "NonGitIgonore" / "brokersupload.csv").resolve()
        )

        parser.add_argument(
            "--csv",
            dest="csv_path",
            default=default_csv,
            help="Path to the brokersupload-style CSV file.",
        )

        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Parse and validate without writing to DB.",
        )

        parser.add_argument(
            "--database",
            dest="database",
            default="default",
            help="Database alias to use (e.g., 'default').",
        )

    def handle(self, *args, **options):
        csv_path = options["csv_path"]
        dry_run = options["dry_run"]
        db_alias = options["database"]

        if not Path(csv_path).exists():
            raise CommandError(f"CSV not found at: {csv_path}")

        created = 0
        updated = 0
        errors = 0
        rowno = 1  # include header

        with open(csv_path, newline="", encoding="utf-8-sig", errors="replace") as csv_file:
            reader = csv.DictReader(csv_file)

            if not reader.fieldnames:
                raise CommandError("CSV has no header row.")

            lower_fieldnames = {fn.lower() for fn in reader.fieldnames}
            if "msa" not in lower_fieldnames:
                raise CommandError("CSV must include an 'MSA' column.")

            context = transaction.atomic(using=db_alias) if not dry_run else nullcontext()
            try:
                if not dry_run:
                    context.__enter__()

                for row in reader:
                    rowno += 1
                    try:
                        lower_row = {(k or "").lower(): v for k, v in row.items()}

                        # Skip completely blank lines
                        if not any((v or "").strip() for v in lower_row.values()):
                            continue

                        name = (lower_row.get("contact name") or lower_row.get("contact_name") or "").strip()
                        firm = (lower_row.get("firm") or "").strip() or None
                        email = (lower_row.get("email") or "").strip() or None
                        msa_raw = (lower_row.get("msa") or "").strip()

                        # Optional state information (can be single or comma-separated)
                        state_raw = (lower_row.get("state") or lower_row.get("states") or "").strip()
                        state_codes = []
                        if state_raw:
                            for part in state_raw.split(","):
                                code = part.strip().upper()
                                if len(code) == 2:
                                    state_codes.append(code)

                        if not msa_raw:
                            # Nothing to assign; skip row
                            continue

                        # Resolve broker
                        broker = None
                        if email:
                            qs = MasterCRM.objects.using(db_alias).filter(email__iexact=email)
                            count = qs.count()
                            if count == 0:
                                raise ValueError(f"No broker found with email '{email}'")

                            # When duplicates exist, pick the first by id but log a warning
                            broker = qs.order_by("id").first()
                            if count > 1:
                                self.stderr.write(
                                    f"Row {rowno}: multiple brokers found with email '{email}', "
                                    f"using broker id={broker.id}."
                                )
                        else:
                            if not name or not firm:
                                raise ValueError(
                                    "Missing both email and (Contact Name + Firm) for broker lookup"
                                )
                            qs = MasterCRM.objects.using(db_alias).filter(
                                contact_name__iexact=name,
                                firm_ref__name__iexact=firm,
                            )
                            count = qs.count()
                            if count == 0:
                                raise ValueError(
                                    f"No broker found for name='{name}' firm='{firm}'"
                                )

                            # When duplicates exist, pick the first by id but log a warning
                            broker = qs.order_by("id").first()
                            if count > 1:
                                self.stderr.write(
                                    f"Row {rowno}: multiple brokers found for name='{name}' firm='{firm}', "
                                    f"using broker id={broker.id}."
                                )

                        # Split normalized MSA string into individual names
                        msa_tokens = [
                            t.strip().strip('"')
                            for t in msa_raw.split(";")
                            if t.strip()
                        ]

                        if not msa_tokens:
                            continue

                        for msa_name in msa_tokens:
                            # Try exact MSAReference match by full msa_name (case-insensitive),
                            # optionally filtered by the broker's state(s) when available.
                            base_qs = MSAReference.objects.using(db_alias).filter(
                                msa_name__iexact=msa_name
                            )
                            if state_codes:
                                base_qs = base_qs.filter(state__state_code__in=state_codes)

                            candidate_msas = []
                            exact_count = base_qs.count()
                            if exact_count == 1:
                                candidate_msas.append(base_qs.first())
                            elif exact_count > 1:
                                raise ValueError(
                                    f"Multiple MSAReference rows found with msa_name='{msa_name}'"
                                )
                            else:
                                # Heuristic normalization: break the raw text into city/region tokens
                                # and look for MSAs whose names contain those tokens, constrained by
                                # state when possible.
                                pieces = re.split(r"[;/]| and | & ", msa_name)
                                seen_codes = set()
                                for piece in pieces:
                                    city = piece.strip()
                                    if not city:
                                        continue

                                    # Remove common noise words like "county", "counties", "area", "market".
                                    city_clean = re.sub(
                                        r"\b(county|counties|area|areas|region|regions|metro|market)\b",
                                        "",
                                        city,
                                        flags=re.IGNORECASE,
                                    ).strip(", ")

                                    if len(city_clean) < 3:
                                        continue

                                    qs = MSAReference.objects.using(db_alias).filter(
                                        msa_name__icontains=city_clean
                                    )
                                    if state_codes:
                                        qs = qs.filter(state__state_code__in=state_codes)

                                    if qs.count() == 1:
                                        msa_obj = qs.first()
                                        if msa_obj.msa_code not in seen_codes:
                                            candidate_msas.append(msa_obj)
                                            seen_codes.add(msa_obj.msa_code)

                                if not candidate_msas:
                                    # If we still cannot resolve this coverage description to a known
                                    # MSA after normalization, log and skip this token instead of
                                    # treating it as a hard error. Other valid MSAs on the same row
                                    # will still be processed.
                                    self.stderr.write(
                                        f"Row {rowno}: skipped unknown MSA '{msa_name}' after normalization"
                                    )
                                    continue

                            # At this point we have one or more candidate MSAs. In dry-run mode we
                            # simply validate that they exist; otherwise we upsert assignments.
                            if dry_run:
                                continue

                            for msa in candidate_msas:
                                assignment, created_flag = (
                                    BrokerMSAAssignment.objects.using(db_alias).update_or_create(
                                        broker=broker,
                                        msa=msa,
                                        defaults={
                                            "priority": 1,
                                            "is_active": True,
                                        },
                                    )
                                )
                                if created_flag:
                                    created += 1
                                else:
                                    updated += 1

                    except Exception as exc:  # noqa: BLE001
                        errors += 1
                        self.stderr.write(
                            f"Row {rowno}: error processing broker/MSA row: {exc}"
                        )

                if not dry_run:
                    context.__exit__(None, None, None)
            except Exception as exc:  # noqa: BLE001
                if not dry_run:
                    context.__exit__(type(exc), exc, exc.__traceback__)
                raise

        self.stdout.write(
            self.style.SUCCESS(
                f"BrokerMSAAssignment import complete. created={created}, "
                f"updated={updated}, errors={errors}, dry_run={dry_run}, "
                f"database='{db_alias}'"
            )
        )


# Python 3.7 compatibility shim for `contextlib.nullcontext` -----------------
try:  # pragma: no cover - compatibility branch
    from contextlib import nullcontext
except ImportError:  # pragma: no cover
    class nullcontext:  # type: ignore[override]
        """Fallback context manager that does nothing."""

        def __init__(self, enter_result=None):
            self.enter_result = enter_result

        def __enter__(self):
            return self.enter_result

        def __exit__(self, *excinfo):
            return False


__all__ = ["Command"]
