"""Management command to import county reference data from Census Bureau API.

WHAT: Fetches all US counties from Census Bureau API and populates CountyReference table
      with FIPS codes, county names, and state links.
WHY:  Provides authoritative county data for legal jurisdiction and tax calculations.
WHERE: Command lives under `core/management/commands/` for Django auto-discovery.
HOW:  Calls Census Bureau ACS API to get all counties for each state, extracts FIPS codes,
      and performs upsert operations with transaction safety.

API Endpoint:
    https://api.census.gov/data/2021/acs/acs5?get=NAME&for=county:*&in=state:*

Response Format:
    [
      ["NAME", "state", "county"],
      ["Autauga County, Alabama", "01", "001"],
      ["Baldwin County, Alabama", "01", "003"],
      ...
    ]
"""

import requests
import os
from pathlib import Path
from dotenv import load_dotenv
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings

from core.models.model_co_geoAssumptions import CountyReference, StateReference


class Command(BaseCommand):
    """Django management command to import county data from Census Bureau API."""

    help = (
        "Import or update CountyReference data from Census Bureau API. "
        "Fetches all US counties with FIPS codes and names."
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

        # WHAT: Optional purge of existing county records
        # WHY: Clean slate for full refresh
        parser.add_argument(
            "--purge",
            action="store_true",
            help="Delete all existing CountyReference records before importing.",
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
        WHAT: Main execution flow to fetch and import county data
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
            existing_count = CountyReference.objects.using(db_alias).count()
            CountyReference.objects.using(db_alias).all().delete()
            self.stdout.write(
                self.style.WARNING(
                    f"Purged {existing_count} existing CountyReference records from '{db_alias}'"
                )
            )

        # WHAT: Pre-fetch all states for efficient FK lookups
        # WHY: Avoid N+1 queries when linking counties to states
        states_dict = {
            state.state_code: state 
            for state in StateReference.objects.using(db_alias).all()
        }
        
        # WHAT: Also create FIPS state code mapping (2-digit codes)
        # WHY: Census API returns 2-digit FIPS codes, need to map to state_code
        state_fips_mapping = {
            '01': 'AL', '02': 'AK', '04': 'AZ', '05': 'AR', '06': 'CA',
            '08': 'CO', '09': 'CT', '10': 'DE', '11': 'DC', '12': 'FL',
            '13': 'GA', '15': 'HI', '16': 'ID', '17': 'IL', '18': 'IN',
            '19': 'IA', '20': 'KS', '21': 'KY', '22': 'LA', '23': 'ME',
            '24': 'MD', '25': 'MA', '26': 'MI', '27': 'MN', '28': 'MS',
            '29': 'MO', '30': 'MT', '31': 'NE', '32': 'NV', '33': 'NH',
            '34': 'NJ', '35': 'NM', '36': 'NY', '37': 'NC', '38': 'ND',
            '39': 'OH', '40': 'OK', '41': 'OR', '42': 'PA', '44': 'RI',
            '45': 'SC', '46': 'SD', '47': 'TN', '48': 'TX', '49': 'UT',
            '50': 'VT', '51': 'VA', '53': 'WA', '54': 'WV', '55': 'WI',
            '56': 'WY', '72': 'PR',
        }

        # WHAT: Fetch county data from Census Bureau API
        # WHY: Get all current counties with official FIPS codes
        # HOW: Use ACS 5-year API with wildcard for all counties
        api_url = (
            "https://api.census.gov/data/2021/acs/acs5"
            "?get=NAME"
            "&for=county:*"
            "&in=state:*"
            f"&key={api_key}"
        )

        self.stdout.write(f"Fetching county data from Census Bureau API...")
        
        try:
            response = requests.get(api_url, timeout=60)  # Longer timeout for larger dataset
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            raise CommandError(f"Failed to fetch data from Census API: {e}")
        except ValueError as e:
            raise CommandError(f"Failed to parse JSON response: {e}")

        if not data or len(data) < 2:
            raise CommandError("API returned no data or invalid format")

        # WHAT: Skip header row (first row contains column names)
        # WHY: Census API returns header as first element
        header = data[0]
        county_rows = data[1:]
        
        self.stdout.write(f"Received {len(county_rows)} counties from Census API")

        # Counters for telemetry
        created = 0
        updated = 0
        errors = 0
        skipped = 0

        # WHAT: Process each county row from API response
        # WHY: Transform Census data into Django model instances
        with transaction.atomic(using=db_alias) if not dry_run else nullcontext():
            for row_data in county_rows:
                try:
                    # WHAT: Extract county name, state FIPS, and county FIPS from API response
                    # HOW: Response format is [NAME, state_fips, county_fips]
                    if len(row_data) < 3:
                        errors += 1
                        self.stderr.write(f"Invalid row format: {row_data}")
                        continue
                    
                    county_full_name = str(row_data[0]).strip()
                    state_fips = str(row_data[1]).strip()
                    county_fips_3digit = str(row_data[2]).strip()
                    
                    # WHAT: Construct full 5-digit FIPS code
                    # HOW: Concatenate 2-digit state + 3-digit county
                    county_fips = state_fips + county_fips_3digit
                    
                    if not county_fips or len(county_fips) != 5:
                        skipped += 1
                        continue
                    
                    # WHAT: Extract county name (remove state name from full name)
                    # HOW: "Los Angeles County, California" → "Los Angeles County"
                    county_name = county_full_name.split(',')[0].strip()
                    
                    # WHAT: Get StateReference object from FIPS code
                    # WHY: Need FK to state for each county
                    state_code = state_fips_mapping.get(state_fips)
                    state_obj = states_dict.get(state_code) if state_code else None
                    
                    if not state_obj:
                        errors += 1
                        self.stderr.write(
                            f"State not found for FIPS {state_fips} (county: {county_name})"
                        )
                        continue
                    
                    # Prepare model data
                    defaults = {
                        "county_name": county_name,
                        "state": state_obj,
                    }
                    
                    if dry_run:
                        # WHAT: Validate model instance without saving
                        # WHY: Catch validation errors before actual import
                        _ = CountyReference(county_fips=county_fips, **defaults)
                        updated += 1
                    else:
                        # WHAT: Create or update county record
                        # WHY: Upsert pattern ensures idempotent imports
                        _, created_flag = CountyReference.objects.using(db_alias).update_or_create(
                            county_fips=county_fips,
                            defaults=defaults,
                        )
                        
                        if created_flag:
                            created += 1
                        else:
                            updated += 1
                
                except Exception as exc:
                    errors += 1
                    self.stderr.write(
                        f"Error processing county FIPS='{county_fips}': {exc}"
                    )

        # WHAT: Emit summary statistics
        # WHY: Provide feedback on import success/failures
        self.stdout.write(
            self.style.SUCCESS(
                f"County import complete. "
                f"created={created}, updated={updated}, skipped={skipped}, "
                f"errors={errors}, dry_run={dry_run}, database='{db_alias}'"
            )
        )


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

