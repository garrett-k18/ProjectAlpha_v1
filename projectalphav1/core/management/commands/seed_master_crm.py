"""
Django management command to seed dummy MasterCRM records.

Usage examples:
- python manage.py seed_master_crm                     # default: 4 per tag
- python manage.py seed_master_crm --per-tag 10        # 10 per tag
- python manage.py seed_master_crm --dry-run           # plan only
- python manage.py seed_master_crm --reset             # delete all then seed

Docs: https://docs.djangoproject.com/en/stable/howto/custom-management-commands/
"""
from __future__ import annotations

import random
import string
from typing import Dict, List, Tuple

from django.core.management.base import BaseCommand, CommandParser
from django.db import transaction

from core.models.crm import MasterCRM


class Command(BaseCommand):
    """Seeds the MasterCRM table with randomly generated contacts.

    Options:
    - --per-tag: how many records to create per tag (default 4)
    - --dry-run: print the plan without writing to the database
    - --reset: delete all MasterCRM rows before seeding

    Implementation notes:
    - Uses built-in Python `random` (no external deps) to generate dummy data.
    - Idempotency: we key `get_or_create` on unique-looking email addresses so re-runs won't duplicate.
    - All writes are wrapped in a transaction for safety; dry-run performs no DB mutations.
    """

    help = (
        "Seed MasterCRM with random records across all tags (broker, trading_partner, legal, vendor)."
    )

    # Predefined small pools for randomization (kept small for readability). These are not exhaustive.
    FIRST_NAMES: List[str] = [
        "Alex",
        "Jordan",
        "Taylor",
        "Casey",
        "Morgan",
        "Riley",
        "Jamie",
        "Quinn",
        "Avery",
        "Cameron",
    ]
    LAST_NAMES: List[str] = [
        "Smith",
        "Johnson",
        "Williams",
        "Brown",
        "Jones",
        "Miller",
        "Davis",
        "Garcia",
        "Rodriguez",
        "Wilson",
    ]
    FIRMS: List[str] = [
        "Alpha Capital",
        "Summit Partners",
        "Pioneer Realty",
        "Vector Legal",
        "Beacon Advisors",
        "Harbor Finance",
        "Cobalt Investments",
        "NorthStar Group",
        "Atlas Holdings",
        "Crescent Ventures",
    ]
    CITIES: List[str] = [
        "New York",
        "Los Angeles",
        "Chicago",
        "Houston",
        "Phoenix",
        "Philadelphia",
        "San Antonio",
        "San Diego",
        "Dallas",
        "San Jose",
    ]
    STATES: List[str] = [
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DE",
        "FL",
        "GA",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "ME",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VT",
        "VA",
        "WA",
        "WV",
        "WI",
        "WY",
    ]

    def add_arguments(self, parser: CommandParser) -> None:
        """Register command-line arguments for the management command."""
        parser.add_argument(
            "--per-tag",
            type=int,
            default=4,
            help="Number of records to create per tag (default: 4)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print what would be created without writing to the database.",
        )
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete all MasterCRM rows before seeding.",
        )

    def handle(self, *args, **options) -> None:
        """Entry point executed by Django when running the command."""
        per_tag: int = options["per_tag"]
        dry_run: bool = options["dry_run"]
        reset: bool = options["reset"]

        # Collect all tag constants/labels from the model.
        tag_choices: List[Tuple[str, str]] = list(MasterCRM.TAG_CHOICES)
        tags_only: List[str] = [t for (t, _label) in tag_choices]

        # Print plan summary header.
        self.stdout.write(self.style.NOTICE("Seeding plan for MasterCRM:"))
        self.stdout.write(f"  Tags: {', '.join(tags_only)}")
        self.stdout.write(f"  Records per tag: {per_tag}")
        self.stdout.write(f"  Dry run: {'YES' if dry_run else 'NO'}")
        self.stdout.write(f"  Reset first: {'YES' if reset else 'NO'}")

        if dry_run:
            existing = MasterCRM.objects.count()
            self.stdout.write(self.style.WARNING(f"[dry-run] Existing rows: {existing}"))
            if reset:
                self.stdout.write(self.style.WARNING("[dry-run] Would delete all existing MasterCRM rows."))
            total_to_create = per_tag * len(tags_only)
            self.stdout.write(self.style.WARNING(f"[dry-run] Would create {total_to_create} rows (≈{per_tag} per tag)."))
            for tag in tags_only:
                # Show a couple example rows that would be created per tag.
                example_count = min(per_tag, 2)
                self.stdout.write(self.style.NOTICE(f"[dry-run] Examples for tag='{tag}':"))
                for i in range(example_count):
                    sample = self._generate_contact(tag=tag, index=i)
                    self.stdout.write(
                        f"    {sample['contact_name']} | {sample['firm']} | {sample['city']}, {sample['state']} | {sample['email']}"
                    )
            return

        # Execute mutations inside a transaction.
        with transaction.atomic():
            if reset:
                deleted, _map = MasterCRM.objects.all().delete()  # deletes in a single query
                self.stdout.write(self.style.WARNING(f"Deleted {deleted} existing MasterCRM rows."))

            created_count = 0
            for tag in tags_only:
                for i in range(per_tag):
                    payload = self._generate_contact(tag=tag, index=i)
                    obj, created = MasterCRM.objects.get_or_create(
                        email=payload["email"],  # using email as a unique-like key for idempotency
                        defaults={
                            "firm": payload["firm"],
                            "contact_name": payload["contact_name"],
                            "state": payload["state"],
                            "city": payload["city"],
                            "phone": payload["phone"],
                            "tag": payload["tag"],
                            "alt_contact_name": payload["alt_contact_name"],
                            "alt_contact_email": payload["alt_contact_email"],
                            "alt_contact_phone": payload["alt_contact_phone"],
                            "notes": payload["notes"],
                        },
                    )
                    if created:
                        created_count += 1

            self.stdout.write(self.style.SUCCESS(f"Seeding complete. Created {created_count} new MasterCRM rows."))

    # ----------------------------
    # Internal helpers
    # ----------------------------
    def _rand_first(self) -> str:
        """Return a random first name from the pool."""
        return random.choice(self.FIRST_NAMES)

    def _rand_last(self) -> str:
        """Return a random last name from the pool."""
        return random.choice(self.LAST_NAMES)

    def _rand_firm(self) -> str:
        """Return a random firm from the pool."""
        return random.choice(self.FIRMS)

    def _rand_city(self) -> str:
        """Return a random city from the pool."""
        return random.choice(self.CITIES)

    def _rand_state(self) -> str:
        """Return a random 2-letter US state code from the pool."""
        return random.choice(self.STATES)

    def _rand_phone(self) -> str:
        """Return a random US-like phone number string (not guaranteed real)."""
        # Simple pattern: (AAA) BBB-CCCC
        area = random.randint(200, 989)
        mid = random.randint(200, 989)
        last = random.randint(1000, 9999)
        return f"({area}) {mid}-{last}"

    def _rand_email(self, first: str, last: str, domain_hint: str | None = None) -> str:
        """Return a random-ish email using first/last and a small domain pool.

        We add a random suffix to improve uniqueness across multiple runs.
        """
        domains = [
            "example.com",
            "sample.io",
            "demo.org",
            "mail.test",
        ]
        domain = domain_hint or random.choice(domains)
        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
        handle = f"{first}.{last}.{suffix}".lower()
        return f"{handle}@{domain}"

    def _generate_contact(self, tag: str, index: int) -> Dict[str, str]:
        """Generate a single contact payload for the given tag.

        The index is used only for variability; no guaranteed uniqueness.
        """
        first = self._rand_first()
        last = self._rand_last()
        contact_name = f"{first} {last}"
        firm = self._rand_firm()
        city = self._rand_city()
        state = self._rand_state()
        email = self._rand_email(first, last)
        phone = self._rand_phone()

        # Alternate contact fields (optional)
        alt_first = self._rand_first()
        alt_last = self._rand_last()
        alt_name = f"{alt_first} {alt_last}"
        alt_email = self._rand_email(alt_first, alt_last)
        alt_phone = self._rand_phone()

        # Simple tag-specific note for flavor
        notes = f"Auto-seeded contact (tag={tag}, batch_index={index})."

        return {
            "firm": firm,
            "contact_name": contact_name,
            "state": state,
            "city": city,
            "email": email,
            "phone": phone,
            "tag": tag,
            "alt_contact_name": alt_name,
            "alt_contact_email": alt_email,
            "alt_contact_phone": alt_phone,
            "notes": notes,
        }
