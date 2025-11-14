"""Management command to import ZIP code reference data from CSV file.

WHAT: Imports ZIP code data and populates ZIPReference table with ZIP codes,
      cities, states, counties, and MSA mappings.
WHY:  Provides authoritative ZIP→MSA mapping for broker assignments and geocoding.
WHERE: Command lives under `core/management/commands/` for Django auto-discovery.
HOW:  Reads from local CSV file with ZIP code data (similar to import_state_reference).

CSV Format Expected (flexible column names):
    zip,city,state_id,county_fips,cbsa
    OR
    ZIP,USPS_ZIP_PREF_CITY,USPS_ZIP_PREF_STATE,COUNTY,CBSA
    
Example Row:
    90210,Beverly Hills,CA,06037,31080
    
Free ZIP Database Sources:
    1. SimpleMaps.com: https://simplemaps.com/data/us-zips (free basic version)
    2. HUD USPS Crosswalk: https://www.huduser.gov/portal/datasets/usps_crosswalk.html
    3. Download to: ProjectAlpha_v1/z.Admin/DataUploads/zip_database.csv
    
Required CSV Columns (flexible names):
    - zip/ZIP: 5-digit ZIP code
    - city/USPS_ZIP_PREF_CITY: City name
    - state_id/state/USPS_ZIP_PREF_STATE: State abbreviation (2 letters)
    - county_fips/COUNTY: 5-digit county FIPS code (optional)
    - cbsa/CBSA: 5-digit CBSA/MSA code (optional)
"""

import csv
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings

from core.models.model_co_geoAssumptions import ZIPReference, StateReference, CountyReference, MSAReference


class Command(BaseCommand):
    """Django management command to import ZIP code data from CSV file."""

    help = (
        "Import or update ZIPReference data from CSV file. "
        "Fetches ZIP codes with city, state, county, and MSA mappings."
    )

    def add_arguments(self, parser):
        """
        WHAT: Register CLI flags for command options
        WHY: Provide flexibility for CSV path, dry-run, purge, and database selection
        """
        
        # WHAT: CSV file path
        # WHY: Allow specifying custom CSV location
        default_csv = str((Path(settings.BASE_DIR).parent / "z.Admin" / "DataUploads" / "zip_database.csv").resolve())
        
        parser.add_argument(
            "--csv",
            dest="csv_path",
            default=default_csv,
            help="Path to ZIP code CSV file (defaults to z.Admin/DataUploads/zip_database.csv)",
        )
        
        # WHAT: Toggle dry-run mode
        # WHY: Validate CSV without writing to database
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Parse and validate CSV without writing to DB.",
        )

        # WHAT: Optional purge of existing ZIP records
        # WHY: Clean slate for full refresh
        parser.add_argument(
            "--purge",
            action="store_true",
            help="Delete all existing ZIPReference records before importing.",
        )

        # WHAT: Database alias selection
        # WHY: Support multi-database setups (dev vs prod)
        parser.add_argument(
            "--database",
            dest="database",
            default="default",
            help="Database alias to use (e.g., 'default').",
        )
        
        # WHAT: Limit number of ZIPs to import
        # WHY: Allow testing with smaller dataset
        parser.add_argument(
            "--limit",
            dest="limit",
            type=int,
            default=None,
            help="Limit number of ZIP codes to import (for testing).",
        )
        
        # WHAT: Batch size for commit intervals
        # WHY: Show progress and prevent long-running transactions
        parser.add_argument(
            "--batch-size",
            dest="batch_size",
            type=int,
            default=1000,
            help="Number of records to process before committing (default: 1000).",
        )

    def handle(self, *args, **options):
        """
        WHAT: Main execution flow to import ZIP code data from CSV
        WHY: Entry point invoked by Django when command runs
        """
        
        # Extract runtime options
        csv_path = options["csv_path"]
        dry_run = options["dry_run"]
        purge = options["purge"]
        db_alias = options["database"]
        limit = options["limit"]
        batch_size = options["batch_size"]

        # WHAT: Log import configuration and start timer
        # WHY: User wants detailed logging to track progress
        import_start_time = time.time()
        self.stdout.write(self.style.HTTP_INFO("=" * 80))
        self.stdout.write(self.style.HTTP_INFO("ZIP CODE IMPORT STARTED"))
        self.stdout.write(self.style.HTTP_INFO("=" * 80))
        self.stdout.write(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.stdout.write(f"CSV Path: {csv_path}")
        self.stdout.write(f"Database: {db_alias}")
        self.stdout.write(f"Batch Size: {batch_size}")
        self.stdout.write(f"Dry Run: {dry_run}")
        self.stdout.write(f"Purge Existing: {purge}")
        self.stdout.write(f"Limit: {limit if limit else 'No limit'}")
        self.stdout.write(self.style.HTTP_INFO("-" * 80))

        # Fail fast if CSV doesn't exist
        if not os.path.exists(csv_path):
            raise CommandError(
                f"CSV not found at: {csv_path}\n\n"
                f"Please download ZIP database from:\n"
                f"  1. SimpleMaps: https://simplemaps.com/data/us-zips (free)\n"
                f"  2. HUD: https://www.huduser.gov/portal/datasets/usps_crosswalk.html\n\n"
                f"Save to: {csv_path}"
            )

        # Optionally purge existing data
        if purge and not dry_run:
            existing_count = ZIPReference.objects.using(db_alias).count()
            ZIPReference.objects.using(db_alias).all().delete()
            self.stdout.write(
                self.style.WARNING(
                    f"Purged {existing_count} existing ZIPReference records from '{db_alias}'"
                )
            )

        # WHAT: Pre-fetch all reference data for efficient FK lookups
        # WHY: Avoid N+1 queries when linking ZIPs
        self.stdout.write(self.style.WARNING("📊 Loading reference data..."))
        
        states_dict = {
            state.state_code: state 
            for state in StateReference.objects.using(db_alias).all()
        }
        self.stdout.write(f"  ✓ Loaded {len(states_dict)} states")
        
        counties_dict = {
            county.county_fips: county 
            for county in CountyReference.objects.using(db_alias).all()
        }
        self.stdout.write(f"  ✓ Loaded {len(counties_dict)} counties")
        
        msas_dict = {
            msa.msa_code: msa 
            for msa in MSAReference.objects.using(db_alias).all()
        }
        self.stdout.write(f"  ✓ Loaded {len(msas_dict)} MSAs")
        
        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Reference data loaded: {len(states_dict)} states, "
                f"{len(counties_dict)} counties, {len(msas_dict)} MSAs"
            )
        )
        self.stdout.write(self.style.HTTP_INFO("-" * 80))

        # Counters for telemetry
        created = 0
        updated = 0
        errors = 0
        skipped = 0
        rowno = 1

        # WHAT: Parse CSV file
        # WHY: Import ZIP data from local file
        self.stdout.write(self.style.WARNING("📁 Opening CSV file..."))
        self.stdout.write(f"  File: {csv_path}")
        
        # WHAT: Try multiple encodings to handle different CSV formats
        # WHY: CSVs may have different encodings (UTF-8, Latin-1, etc.)
        encodings_to_try = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        csv_file = None
        for encoding in encodings_to_try:
            try:
                csv_file = open(csv_path, newline="", encoding=encoding)
                # Try to read header to validate encoding
                _ = csv_file.readline()
                csv_file.seek(0)  # Reset to beginning
                self.stdout.write(self.style.SUCCESS(f"  ✓ Successfully opened CSV with encoding: {encoding}"))
                break
            except UnicodeDecodeError:
                if csv_file:
                    csv_file.close()
                continue
        
        if not csv_file:
            raise CommandError(f"Could not open CSV with any supported encoding")
        
        with csv_file:
            reader = csv.DictReader(csv_file)
            
            # WHAT: Detect column names (flexible mapping)
            # WHY: Different data sources use different column names
            fieldnames = reader.fieldnames or []
            
            self.stdout.write(self.style.WARNING("🔍 Detecting CSV columns..."))
            self.stdout.write(f"  Available columns: {', '.join(fieldnames)}")
            
            # Map column names to our expected format
            col_map = self._detect_columns(fieldnames)
            
            if not col_map['zip']:
                raise CommandError(
                    f"Could not find ZIP code column in CSV. "
                    f"Available columns: {', '.join(fieldnames)}"
                )
            
            self.stdout.write(self.style.SUCCESS("  ✓ Column mapping detected:"))
            for key, value in col_map.items():
                if value:
                    self.stdout.write(f"    - {key}: '{value}'")
            self.stdout.write(self.style.HTTP_INFO("-" * 80))
            self.stdout.write(self.style.WARNING("🚀 Starting import..."))
            
            # WHAT: Process CSV in batches for better progress visibility
            # WHY: Show incremental progress for large imports, prevent long transactions
            batch_records = []
            
            for row in reader:
                rowno += 1
                
                # Apply limit if specified
                if limit and (created + updated) >= limit:
                    break
                
                try:
                    # WHAT: Extract data using column mapping
                    zip_code = str(row.get(col_map['zip'], '')).strip().zfill(5)
                    city_name = str(row.get(col_map['city'], '') if col_map['city'] else '').strip()
                    state_code = str(row.get(col_map['state'], '')).strip().upper()
                    county_fips = str(row.get(col_map['county'], '') if col_map['county'] else '').strip().zfill(5)
                    cbsa_code = str(row.get(col_map['cbsa'], '') if col_map['cbsa'] else '').strip()
                    
                    # WHAT: Extract multi-county data from SimpleMaps CSV
                    # WHY: Some ZIPs span multiple counties - valuable for accurate geocoding
                    county_fips_all = str(row.get('county_fips_all', '')).strip()
                    county_weights = str(row.get('county_weights', '')).strip()
                    
                    if not zip_code or len(zip_code) != 5:
                        skipped += 1
                        continue
                    
                    # WHAT: Get FK objects
                    state_obj = states_dict.get(state_code)
                    if not state_obj:
                        # WHAT: Skip territories (VI, PR, GU, AS, MP) silently
                        # WHY: These are US territories not included in our state reference
                        territories = ['VI', 'PR', 'GU', 'AS', 'MP']
                        if state_code in territories:
                            skipped += 1
                        else:
                            errors += 1
                            if errors <= 10:  # Only show first 10 errors
                                self.stderr.write(f"Row {rowno}: State '{state_code}' not found for ZIP {zip_code}")
                        continue
                    
                    county_obj = counties_dict.get(county_fips) if county_fips and len(county_fips) == 5 else None
                    msa_obj = msas_dict.get(cbsa_code) if cbsa_code else None
                    
                    # WHAT: Add to batch instead of immediate save
                    batch_records.append({
                        'zip_code': zip_code,
                        'defaults': {
                            "city_name": city_name if city_name else None,
                            "state": state_obj,
                            "county": county_obj,
                            "msa": msa_obj,
                            "county_fips_all": county_fips_all if county_fips_all else None,
                            "county_weights": county_weights if county_weights else None,
                            "zip_type": "STANDARD",
                        }
                    })
                    
                    # WHAT: Process batch when it reaches batch_size
                    # WHY: Commit in chunks for progress visibility
                    if len(batch_records) >= batch_size:
                        # Log batch start with timing
                        batch_num = (created + updated) // batch_size + 1
                        batch_start = time.time()
                        self.stdout.write(
                            self.style.HTTP_INFO(
                                f"⏳ Processing batch #{batch_num} ({len(batch_records)} records)..."
                            )
                        )
                        
                        processed = self._process_batch(batch_records, dry_run, db_alias)
                        created += processed['created']
                        updated += processed['updated']
                        
                        batch_time = time.time() - batch_start
                        
                        # Calculate progress percentage (estimate 33,000 total)
                        total_processed = created + updated
                        progress_pct = (total_processed / 33000) * 100 if not limit else (total_processed / limit) * 100
                        
                        # Estimate time remaining
                        elapsed_time = time.time() - import_start_time
                        avg_time_per_record = elapsed_time / total_processed if total_processed > 0 else 0
                        estimated_total = 33000 if not limit else limit
                        remaining_records = estimated_total - total_processed
                        eta_seconds = remaining_records * avg_time_per_record
                        eta = str(timedelta(seconds=int(eta_seconds)))
                        
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"✅ Batch #{batch_num} complete in {batch_time:.2f}s! "
                                f"Progress: {total_processed:,}/{estimated_total:,} ZIPs ({progress_pct:.1f}%)"
                            )
                        )
                        self.stdout.write(
                            f"   Created: {created:,} | Updated: {updated:,} | "
                            f"Errors: {errors} | Skipped: {skipped} | ETA: {eta}"
                        )
                        self.stdout.write(self.style.HTTP_INFO("-" * 80))
                        batch_records = []
                
                except Exception as exc:
                    errors += 1
                    if errors <= 10:  # Only show first 10 errors
                        self.stderr.write(f"Row {rowno}: Error processing ZIP '{zip_code}': {exc}")
            
            # WHAT: Process any remaining records in final batch
            # WHY: Handle records that didn't fill a complete batch
            if batch_records:
                self.stdout.write(
                    self.style.WARNING(
                        f"⏳ Processing final batch ({len(batch_records)} records)..."
                    )
                )
                
                processed = self._process_batch(batch_records, dry_run, db_alias)
                created += processed['created']
                updated += processed['updated']
                
                total_processed = created + updated
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Final batch complete! Total: {total_processed:,} ZIPs processed"
                    )
                )

        # WHAT: Emit summary statistics
        # WHY: Provide feedback on import success/failures
        total_time = time.time() - import_start_time
        total_time_str = str(timedelta(seconds=int(total_time)))
        avg_per_record = (total_time / (created + updated)) if (created + updated) > 0 else 0
        
        self.stdout.write(self.style.HTTP_INFO("=" * 80))
        self.stdout.write(self.style.SUCCESS("🎉 ZIP CODE IMPORT COMPLETE!"))
        self.stdout.write(self.style.HTTP_INFO("=" * 80))
        self.stdout.write(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.stdout.write(f"Total Duration: {total_time_str} ({total_time:.2f} seconds)")
        self.stdout.write(f"Average Speed: {avg_per_record:.4f}s per record ({(created + updated) / total_time:.1f} records/sec)")
        self.stdout.write(self.style.HTTP_INFO("-" * 80))
        self.stdout.write(f"Total Processed: {created + updated:,}")
        self.stdout.write(f"  ✓ Created: {created:,}")
        self.stdout.write(f"  ✓ Updated: {updated:,}")
        self.stdout.write(f"  ⚠ Skipped: {skipped:,}")
        self.stdout.write(f"  ✗ Errors: {errors:,}")
        self.stdout.write(self.style.HTTP_INFO("-" * 80))
        self.stdout.write(f"Database: {db_alias}")
        self.stdout.write(f"Dry Run: {dry_run}")
        self.stdout.write(self.style.HTTP_INFO("=" * 80))

    def _process_batch(self, batch_records, dry_run, db_alias):
        """
        WHAT: Process a batch of ZIP records
        WHY: Commit in chunks for progress visibility and transaction safety
        HOW: Use transaction.atomic for each batch
        
        Args:
            batch_records: List of dicts with 'zip_code' and 'defaults' keys
            dry_run: Boolean for dry-run mode
            db_alias: Database alias to use
            
        Returns:
            dict with 'created' and 'updated' counts
        """
        batch_created = 0
        batch_updated = 0
        
        with transaction.atomic(using=db_alias) if not dry_run else nullcontext():
            for record in batch_records:
                zip_code = record['zip_code']
                defaults = record['defaults']
                
                if dry_run:
                    _ = ZIPReference(zip_code=zip_code, **defaults)
                    batch_updated += 1
                else:
                    _, created_flag = ZIPReference.objects.using(db_alias).update_or_create(
                        zip_code=zip_code,
                        defaults=defaults,
                    )
                    
                    if created_flag:
                        batch_created += 1
                    else:
                        batch_updated += 1
        
        return {'created': batch_created, 'updated': batch_updated}
    
    def _detect_columns(self, fieldnames):
        """
        WHAT: Detect column names from CSV header
        WHY: Different data sources use different column names
        HOW: Map common variations to our standard format
        
        Returns:
            dict with keys: zip, city, state, county, cbsa
        """
        fieldnames_lower = [f.lower() for f in fieldnames]
        
        col_map = {
            'zip': None,
            'city': None,
            'state': None,
            'county': None,
            'cbsa': None,
        }
        
        # ZIP column variants
        for variant in ['zip', 'zipcode', 'zip_code', 'postal_code']:
            if variant in fieldnames_lower:
                col_map['zip'] = fieldnames[fieldnames_lower.index(variant)]
                break
        
        # City column variants
        for variant in ['city', 'usps_zip_pref_city', 'city_name', 'primary_city']:
            if variant in fieldnames_lower:
                col_map['city'] = fieldnames[fieldnames_lower.index(variant)]
                break
        
        # State column variants
        for variant in ['state', 'state_id', 'usps_zip_pref_state', 'state_code', 'state_abbr']:
            if variant in fieldnames_lower:
                col_map['state'] = fieldnames[fieldnames_lower.index(variant)]
                break
        
        # County column variants
        for variant in ['county', 'county_fips', 'countyfips', 'fips']:
            if variant in fieldnames_lower:
                col_map['county'] = fieldnames[fieldnames_lower.index(variant)]
                break
        
        # CBSA/MSA column variants
        for variant in ['cbsa', 'cbsa_code', 'msa', 'msa_code', 'metro']:
            if variant in fieldnames_lower:
                col_map['cbsa'] = fieldnames[fieldnames_lower.index(variant)]
                break
        
        return col_map


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
