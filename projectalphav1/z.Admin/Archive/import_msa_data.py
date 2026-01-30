"""Management command to import MSA reference data from Census Bureau API.

WHAT: Fetches all Metropolitan Statistical Areas (MSAs) from Census Bureau API
      and populates the MSAReference table with CBSA codes, names, and state links.
WHY:  Provides authoritative MSA data for broker assignments and market analysis.
WHERE: Command lives under `core/management/commands/` for Django auto-discovery.
HOW:  Calls Census Bureau ACS Flows API to get all MSAs, parses state codes from
      MSA names, and performs upsert operations with transaction safety.

API Endpoint:
    https://api.census.gov/data/2021/acs/flows?get=METRO1,METRO1_NAME&for=metropolitan+statistical+areas:*

Response Format:
    [
      ["METRO1", "METRO1_NAME", "metropolitan statistical areas"],
      ["35620", "New York-Newark-Jersey City, NY-NJ-PA", "35620"],
      ["31080", "Los Angeles-Long Beach-Anaheim, CA", "31080"],
      ...
    ]
"""

import requests
import re
import os
from pathlib import Path
from dotenv import load_dotenv
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings

from core.models.model_co_geoAssumptions import MSAReference, StateReference


class Command(BaseCommand):
    """Django management command to import MSA data from Census Bureau API."""

    help = (
        "Import or update MSAReference data from Census Bureau API. "
        "Fetches all Metropolitan Statistical Areas with CBSA codes and names."
    )

    def add_arguments(self, parser):
        """
        WHAT: Register CLI flags for command options
        WHY: Provide flexibility for dry-run, purge, and database selection
        """
        
        # WHAT: Toggle dry-run mode
        # WHY: Validate API response without writing to database
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Parse and validate API response without writing to DB.",
        )

        # WHAT: Optional purge of existing MSA records
        # WHY: Clean slate for full refresh
        parser.add_argument(
            "--purge",
            action="store_true",
            help="Delete all existing MSAReference records before importing.",
        )

        # WHAT: Database alias selection
        # WHY: Support multi-database setups (dev vs prod)
        parser.add_argument(
            "--database",
            dest="database",
            default="default",
            help="Database alias to use (e.g., 'default').",
        )
        
        # WHAT: Optional Census API key override
        # WHY: Allow using different key than .env
        parser.add_argument(
            "--api-key",
            dest="api_key",
            default=None,
            help="Census API key (defaults to CENSUS_API_KEY from settings).",
        )

    def handle(self, *args, **options):
        """
        WHAT: Main execution flow to fetch and import MSA data
        WHY: Entry point invoked by Django when command runs
        """
        
        # WHAT: Load environment variables from .env file
        # WHY: Keep API keys in .env, not in Django settings
        # HOW: Load from project root .env
        env_path = Path(settings.BASE_DIR).parent / '.env'
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)
        
        # Extract runtime options
        dry_run = options["dry_run"]
        purge = options["purge"]
        db_alias = options["database"]
        api_key = options["api_key"] or os.getenv('CENSUS_API_KEY')

        if not api_key:
            raise CommandError(
                "Census API key not found. Set CENSUS_API_KEY in .env file or use --api-key flag."
            )

        # Optionally purge existing data
        if purge and not dry_run:
            existing_count = MSAReference.objects.using(db_alias).count()
            MSAReference.objects.using(db_alias).all().delete()
            self.stdout.write(
                self.style.WARNING(
                    f"Purged {existing_count} existing MSAReference records from '{db_alias}'"
                )
            )

        # WHAT: Fetch MSA data from Census Bureau API
        # WHY: Get all current MSAs with official codes and names
        # HOW: Use ACS 5-year estimates with metropolitan statistical area geography
        # NOTE: Try multiple API endpoints as Census API structure varies by year
        
        # Try different API endpoints (Census API can be finicky with availability)
        api_urls = [
            # 2022 ACS 5-year
            f"https://api.census.gov/data/2022/acs/acs5?get=NAME&for=metropolitan+statistical+area/micropolitan+statistical+area:*&key={api_key}",
            # 2021 ACS 5-year
            f"https://api.census.gov/data/2021/acs/acs5?get=NAME&for=metropolitan+statistical+area/micropolitan+statistical+area:*&key={api_key}",
            # 2020 ACS 5-year
            f"https://api.census.gov/data/2020/acs/acs5?get=NAME&for=metropolitan+statistical+area/micropolitan+statistical+area:*&key={api_key}",
        ]

        self.stdout.write(f"Fetching MSA data from Census Bureau API...")
        
        data = None
        successful_url = None
        
        for api_url in api_urls:
            self.stdout.write(f"Trying: {api_url[:80]}...")
            try:
                response = requests.get(api_url, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    successful_url = api_url
                    self.stdout.write(self.style.SUCCESS(f"✓ Success with this endpoint"))
                    break
                else:
                    self.stdout.write(f"  Status {response.status_code}, trying next...")
            except Exception as e:
                self.stdout.write(f"  Error: {e}, trying next...")
                continue
        
        if not data:
            raise CommandError(
                "Failed to fetch MSA data from all available Census API endpoints. "
                "Check your API key or try again later."
            )

        if not data or len(data) < 2:
            raise CommandError("API returned no data or invalid format")

        # WHAT: Skip header row (first row contains column names)
        # WHY: Census API returns header as first element
        header = data[0]
        msa_rows = data[1:]
        
        self.stdout.write(f"Received {len(msa_rows)} MSAs from Census API")

        # Counters for telemetry
        created = 0
        updated = 0
        errors = 0
        skipped = 0

        # WHAT: Pre-fetch all states for efficient FK lookups
        # WHY: Avoid N+1 queries when linking MSAs to states
        states_dict = {
            state.state_code: state 
            for state in StateReference.objects.using(db_alias).all()
        }

        # WHAT: Process each MSA row from API response
        # WHY: Transform Census data into Django model instances
        with transaction.atomic(using=db_alias) if not dry_run else nullcontext():
            for row_data in msa_rows:
                try:
                    # WHAT: Extract MSA name and code from API response
                    # HOW: Response format is [NAME, msa_code]
                    #      Example: ["New York-Newark-Jersey City, NY-NJ-PA", "35620"]
                    if len(row_data) < 2:
                        errors += 1
                        self.stderr.write(f"Invalid row format: {row_data}")
                        continue
                    
                    msa_name = str(row_data[0]).strip()
                    msa_code = str(row_data[1]).strip()
                    
                    if not msa_code or not msa_name:
                        skipped += 1
                        continue
                    
                    # WHAT: Parse state code from MSA name
                    # WHY: MSA names contain state abbreviations (e.g., "Los Angeles, CA")
                    # HOW: Extract last 2-letter state code before commas or end of string
                    state_obj = self._parse_state_from_msa_name(msa_name, states_dict)
                    
                    # Prepare model data
                    defaults = {
                        "msa_name": msa_name,
                        "state": state_obj,
                    }
                    
                    if dry_run:
                        # WHAT: Validate model instance without saving
                        # WHY: Catch validation errors before actual import
                        _ = MSAReference(msa_code=msa_code, **defaults)
                        updated += 1
                    else:
                        # WHAT: Create or update MSA record
                        # WHY: Upsert pattern ensures idempotent imports
                        _, created_flag = MSAReference.objects.using(db_alias).update_or_create(
                            msa_code=msa_code,
                            defaults=defaults,
                        )
                        
                        if created_flag:
                            created += 1
                        else:
                            updated += 1
                
                except Exception as exc:
                    errors += 1
                    self.stderr.write(
                        f"Error processing MSA code='{msa_code}': {exc}"
                    )

        # WHAT: Emit summary statistics
        # WHY: Provide feedback on import success/failures
        self.stdout.write(
            self.style.SUCCESS(
                f"MSA import complete. "
                f"created={created}, updated={updated}, skipped={skipped}, "
                f"errors={errors}, dry_run={dry_run}, database='{db_alias}'"
            )
        )

    def _parse_state_from_msa_name(self, msa_name: str, states_dict: dict) -> StateReference | None:
        """
        WHAT: Extract state code from MSA name
        WHY: MSA names include state abbreviations (e.g., "New York-Newark, NY-NJ-PA")
        HOW: Use regex to find 2-letter state codes, return first valid match
        
        Examples:
            "Los Angeles-Long Beach-Anaheim, CA" → CA
            "New York-Newark-Jersey City, NY-NJ-PA" → NY (first state)
            "Washington-Arlington-Alexandria, DC-VA-MD-WV" → DC (first state)
        
        Args:
            msa_name: Full MSA name from Census API
            states_dict: Dictionary of state_code → StateReference objects
            
        Returns:
            StateReference object or None if no valid state found
        """
        # WHAT: Find all 2-letter uppercase codes after comma
        # WHY: State codes appear after city names, separated by commas
        # HOW: Match pattern like ", CA" or "-NY-NJ"
        pattern = r'\b([A-Z]{2})\b'
        matches = re.findall(pattern, msa_name)
        
        # WHAT: Return first valid state from matches
        # WHY: Use primary state for MSA (first listed state)
        for state_code in matches:
            if state_code in states_dict:
                return states_dict[state_code]
        
        return None


# WHAT: Python 3.7+ compatibility for nullcontext
# WHY: Older Python versions don't have contextlib.nullcontext
try:
    from contextlib import nullcontext
except ImportError:
    class nullcontext:
        """Fallback context manager that does nothing."""
        def __init__(self, enter_result=None):
            self.enter_result = enter_result
        def __enter__(self):
            return self.enter_result
        def __exit__(self, *excinfo):
            return False


__all__ = ["Command"]

