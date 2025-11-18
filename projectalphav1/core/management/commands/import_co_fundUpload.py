"""
WHAT: Django management command to import fund/entity assignments from CSV to AssetDetails
WHY: Bulk update AssetDetails records with fund_legal_entity assignments based on servicer_id
HOW: Reads CSV, matches servicer_id to AssetIdHub, standardizes entity names, updates AssetDetails
WHERE: Run via: python manage.py import_co_fundUpload
         (Uses DATABASE_URL from .env - set to production URL for prod imports)

Docs reviewed:
- Django management commands: https://docs.djangoproject.com/en/stable/howto/custom-management-commands/
- CSV reading: https://docs.python.org/3/library/csv.html
- Database routing: https://docs.djangoproject.com/en/stable/topics/db/multi-db/
"""

import csv
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings
import dj_database_url
from core.models import AssetIdHub, AssetDetails, Entity, FundLegalEntity


class Command(BaseCommand):
    """
    WHAT: Management command class for importing fund assignments from CSV
    WHY: Provides CLI interface for bulk updating AssetDetails with fund_legal_entity
    HOW: Reads CSV, matches servicer_id, standardizes entity names, updates records
    """
    
    help = 'Import fund/entity assignments from fundUpload.csv to AssetDetails model using servicer_id'

    def add_arguments(self, parser):
        """
        WHAT: Define command-line arguments for the import command
        WHY: Allow flexible control over import behavior
        HOW: Uses argparse to define optional arguments
        """
        parser.add_argument(
            '--csv-file',
            type=str,
            default='z.Admin/NonGitIgonore/fundUpload.csv',
            help='Path to CSV file relative to project root (default: z.Admin/NonGitIgonore/fundUpload.csv)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without actually updating records',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of records to process per batch (default: 100)',
        )
        parser.add_argument(
            '--database',
            dest='database',
            default='default',
            help='Database alias to use (default: default, uses DATABASE_URL from .env). For production, set DATABASE_URL to production URL or use --database-url',
        )
        parser.add_argument(
            '--database-url',
            dest='database_url',
            type=str,
            default=None,
            help='Override DATABASE_URL with a specific connection string (e.g., production database URL)',
        )

    def handle(self, *args, **options):
        """
        WHAT: Main command handler that imports fund assignments
        WHY: Processes CSV and updates AssetDetails records
        HOW: Reads CSV, matches servicer_id, standardizes names, updates in batches
        """
        # WHAT: Get CSV file path
        # WHY: Need to locate the file to read
        csv_file = options['csv_file']
        # WHAT: Flag to determine if we're in dry-run mode
        # WHY: Allows previewing changes without committing to database
        dry_run = options['dry_run']
        # WHAT: Number of records to process per batch
        # WHY: Prevents memory issues with large datasets
        batch_size = options['batch_size']

        # WHAT: Build full path to CSV file
        # WHY: Need absolute path to read the file
        # HOW: Use BASE_DIR from settings (which is projectalphav1) and join with relative path
        base_dir = Path(settings.BASE_DIR)  # WHAT: BASE_DIR is projectalphav1, CSV is inside it
        csv_path = base_dir / csv_file  # WHAT: Full path to CSV file

        # WHAT: Check if CSV file exists
        # WHY: Fail early if file is missing
        if not csv_path.exists():
            self.stdout.write(
                self.style.ERROR(f'CSV file not found: {csv_path}')
            )
            return

        self.stdout.write(f'Reading CSV file: {csv_path}')

        # WHAT: Read and parse CSV file
        # WHY: Extract servicer_id and entity name pairs
        # HOW: Use csv.DictReader to parse rows
        csv_data = []
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # WHAT: Extract servicer_id and entity from CSV row
                    # WHY: These are the key fields we need to match
                    servicer_id = row.get('Servicer ID', '').strip()
                    entity_name = row.get('Entity', '').strip()
                    
                    # WHAT: Skip empty rows
                    # WHY: Don't process invalid data
                    if not servicer_id or not entity_name:
                        continue
                    
                    csv_data.append({
                        'servicer_id': servicer_id,
                        'entity_name': entity_name,
                    })
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error reading CSV file: {str(e)}')
            )
            return

        self.stdout.write(f'Found {len(csv_data)} records in CSV')

        # WHAT: Handle database URL override if provided
        # WHY: Allow pointing to production database even if DATABASE_URL points to dev
        database_url_override = options.get('database_url')
        if database_url_override:
            # WHAT: Temporarily override DATABASE_URL environment variable
            # WHY: Let Django's settings.py handle the configuration properly
            # HOW: Save original, set override, then restore after
            original_db_url = os.environ.get('DATABASE_URL')
            os.environ['DATABASE_URL'] = database_url_override
            
            # WHAT: Force Django to reload database settings
            # WHY: Settings have already been loaded, need to reconfigure
            from django.db import connections
            
            # WHAT: Re-parse DATABASE_URL using same logic as settings.py
            # WHY: Ensure exact same configuration structure
            db_config = dj_database_url.parse(
                database_url_override,
                conn_max_age=600,
                ssl_require=True,
            )
            
            # WHAT: Check if this is a Neon database
            is_neon = 'neon.tech' in db_config.get('HOST', '')
            if is_neon:
                db_config['HOST'] = db_config['HOST'].replace('-pooler', '')
            
            # WHAT: Update default database connection with override config
            # WHY: Use default alias but with production URL
            settings.DATABASES['default'] = {
                **db_config,
                'OPTIONS': {
                    'options': '-c search_path=core,seller_data,public'
                },
            }
            
            # WHAT: Close existing connections to force reconnection
            # WHY: Ensure we connect to the new database
            connections['default'].close()
            
            db_alias = 'default'
            self.stdout.write(self.style.WARNING(f'Using override database URL (production)'))
        else:
            # WHAT: Use default database alias
            # WHY: Standard behavior using DATABASE_URL from .env
            db_alias = options['database']
        
        # WHAT: Show which database we're using
        # WHY: Help user understand which database is being queried
        db_config = settings.DATABASES.get(db_alias, {})
        db_name = db_config.get('NAME', 'unknown')
        db_host = db_config.get('HOST', 'unknown')
        self.stdout.write(f'Using database: {db_alias} (Name: {db_name}, Host: {db_host})')

        # WHAT: Get all entities from database to create name mapping
        # WHY: Need to standardize CSV entity names to match stored Entity names
        # HOW: Query Entity model using specified database and create mapping dictionary
        # NOTE: Convert to list to ensure we iterate through all entities
        entities = list(Entity.objects.using(db_alias).all())
        self.stdout.write(f'Found {len(entities)} entities in database')
        # WHAT: Debug output to show entity names
        # WHY: Help diagnose matching issues
        if len(entities) <= 10:  # Only show if small number of entities
            for entity in entities:
                self.stdout.write(f'  - Entity: "{entity.name}" (ID: {entity.id})')
        # WHAT: Helper function to normalize entity names for flexible matching
        # WHY: Handle variations like "AFL Mortgage 2, LLC" vs "AFL 2 Mortgage, LLC"
        # HOW: Remove all punctuation/spaces, sort words alphabetically for word-order independence
        def normalize_entity_name(name: str) -> str:
            """Normalize entity name for flexible matching."""
            import re
            # WHAT: Remove all non-alphanumeric characters and convert to lowercase
            # WHY: Handle punctuation and spacing variations
            cleaned = re.sub(r'[^a-z0-9]', '', name.lower())
            # WHAT: Sort characters alphabetically for word-order independence
            # WHY: "AFL Mortgage 2" and "AFL 2 Mortgage" become the same
            return ''.join(sorted(cleaned))
        
        # WHAT: Create mapping from various name formats to Entity ID
        # WHY: CSV might have "WFL Homes LLC" but Entity has "WFL Homes, LLC"
        # HOW: Store multiple name variations for flexible matching (exact -> simple -> character-sorted)
        entity_name_map = {}
        for entity in entities:
            # WHAT: Store multiple variations of the name for flexible matching
            # WHY: CSV names might not exactly match Entity names
            entity_lower = entity.name.lower().strip()  # WHAT: Exact match (case-insensitive, trimmed)
            simple_normalized = entity.name.replace(',', '').replace(' ', '').lower()  # WHAT: Remove punctuation/spaces
            normalized_name = normalize_entity_name(entity.name)  # WHAT: Character-sorted (word-order independent)
            
            # WHAT: Store all variations in the map
            # WHY: Allow matching at different levels of specificity
            entity_name_map[entity_lower] = entity.id
            entity_name_map[simple_normalized] = entity.id
            entity_name_map[normalized_name] = entity.id

        # WHAT: Get or create FundLegalEntity records for each entity
        # WHY: AssetDetails.fund_legal_entity requires FundLegalEntity, not Entity directly
        # HOW: Check if FundLegalEntity exists, create if missing (skip in dry-run)
        fund_legal_entity_map = {}
        for entity in entities:
            # WHAT: Get or create FundLegalEntity for this Entity
            # WHY: AssetDetails links to FundLegalEntity, not Entity
            # HOW: Use get_or_create to avoid duplicates, using specified database
            if dry_run:
                # WHAT: In dry-run, just check if it exists
                # WHY: Don't create records during dry-run
                try:
                    fle = FundLegalEntity.objects.using(db_alias).get(fund=entity)
                except FundLegalEntity.DoesNotExist:
                    self.stdout.write(f'Would create FundLegalEntity for {entity.name}')
                    # WHAT: Use a placeholder ID for dry-run
                    # WHY: Need to continue processing even if record doesn't exist
                    fle_id = None
                else:
                    fle_id = fle.id
            else:
                # WHAT: Actually get or create FundLegalEntity
                # WHY: Need the record to exist for updates
                fle, created = FundLegalEntity.objects.using(db_alias).get_or_create(
                    fund=entity,
                    defaults={
                        'nickname_name': entity.name,  # WHAT: Use entity name as nickname
                        'entity_role': FundLegalEntity.EntityRole.OTHER,  # WHAT: Default role
                        'is_active': True,  # WHAT: Mark as active
                    }
                )
                if created:
                    self.stdout.write(f'Created FundLegalEntity for {entity.name}')
                fle_id = fle.id
            
            # WHAT: Store mapping from normalized entity name to FundLegalEntity ID
            # WHY: Need to quickly look up FundLegalEntity ID from CSV entity name
            if fle_id:
                entity_lower = entity.name.lower().strip()
                simple_normalized = entity.name.replace(',', '').replace(' ', '').lower()
                normalized_name = normalize_entity_name(entity.name)
                # WHAT: Store all variations for quick lookup
                # WHY: Match at different levels of specificity
                fund_legal_entity_map[entity_lower] = fle_id
                fund_legal_entity_map[simple_normalized] = fle_id
                fund_legal_entity_map[normalized_name] = fle_id

        # WHAT: Process CSV data in batches
        # WHY: Handle large datasets efficiently
        updated_count = 0
        not_found_count = 0
        entity_not_found_count = 0

        for i in range(0, len(csv_data), batch_size):
            # WHAT: Get current batch of CSV records
            # WHY: Process manageable chunks at a time
            batch = csv_data[i:i + batch_size]
            
            # WHAT: Use transaction to ensure atomicity
            # WHY: If one record fails, we can rollback the batch
            # HOW: Wrap batch updates in a transaction block
            try:
                with transaction.atomic():
                    # WHAT: Iterate through each CSV record in the batch
                    # WHY: Need to update each AssetDetails record
                    for record in batch:
                        servicer_id = record['servicer_id']
                        csv_entity_name = record['entity_name']
                        
                        # WHAT: Normalize CSV entity name for matching
                        # WHY: Handle variations like "WFL Homes LLC" vs "WFL Homes, LLC"
                        # HOW: Try multiple normalization strategies, from most specific to most flexible
                        csv_lower = csv_entity_name.lower().strip()  # WHAT: Exact match (case-insensitive, trimmed)
                        simple_csv_normalized = csv_entity_name.replace(',', '').replace(' ', '').lower()  # WHAT: Remove punctuation/spaces
                        normalized_csv_name = normalize_entity_name(csv_entity_name)  # WHAT: Character-sorted (word-order independent)
                        
                        # WHAT: Find matching FundLegalEntity ID
                        # WHY: Need to link AssetDetails to FundLegalEntity
                        # HOW: Try multiple matching strategies from most specific to most flexible
                        fle_id = (
                            fund_legal_entity_map.get(csv_lower) or  # WHAT: Try exact lowercase match first (most specific)
                            fund_legal_entity_map.get(simple_csv_normalized) or  # WHAT: Try simple normalized match
                            fund_legal_entity_map.get(normalized_csv_name) or  # WHAT: Try word-order-independent match
                            None  # WHAT: Will be handled below if not found
                        )
                        
                        # WHAT: Track if we found the Entity (even if FundLegalEntity doesn't exist yet)
                        # WHY: Distinguish between "Entity not found" vs "FundLegalEntity needs creation"
                        entity_found = False
                        
                        # WHAT: If still not found, try fuzzy matching with existing entities
                        # WHY: Handle slight variations in entity names (e.g., "AFL 2 Mortgage, LLC" vs "AFL Mortgage 2, LLC")
                        # HOW: Compare normalized names using same normalization function, trying most specific first
                        if not fle_id:
                            for entity in entities:
                                entity_lower = entity.name.lower().strip()
                                entity_simple_normalized = entity.name.replace(',', '').replace(' ', '').lower()
                                entity_normalized = normalize_entity_name(entity.name)
                                # WHAT: Try multiple normalization methods for matching (most specific to most flexible)
                                # WHY: Handle different name variations (exact, punctuation, word order)
                                if (csv_lower == entity_lower or 
                                    simple_csv_normalized == entity_simple_normalized or
                                    normalized_csv_name == entity_normalized):
                                    # WHAT: Found a match! Entity exists in database
                                    entity_found = True
                                    # WHY: Now we need to get or create FundLegalEntity for this Entity
                                    # HOW: Handle both dry-run and actual modes
                                    if dry_run:
                                        # WHAT: In dry-run, check if FundLegalEntity exists
                                        # WHY: Don't create records during dry-run
                                        try:
                                            fle = FundLegalEntity.objects.using(db_alias).get(fund=entity)
                                            fle_id = fle.id
                                        except FundLegalEntity.DoesNotExist:
                                            # WHAT: Would create FundLegalEntity in real run
                                            # WHY: Log this for user awareness
                                            self.stdout.write(f'Would create FundLegalEntity for {entity.name}')
                                            fle_id = None  # WHAT: Skip this record in dry-run
                                    else:
                                        # WHAT: Actually get or create FundLegalEntity
                                        # WHY: Need the record to exist for updates
                                        fle, created = FundLegalEntity.objects.using(db_alias).get_or_create(
                                            fund=entity,
                                            defaults={
                                                'nickname_name': entity.name,
                                                'entity_role': FundLegalEntity.EntityRole.OTHER,
                                                'is_active': True,
                                            }
                                        )
                                        if created:
                                            self.stdout.write(f'Created FundLegalEntity for {entity.name}')
                                        fle_id = fle.id
                                    
                                    # WHAT: Add to map for future lookups (if we have an ID)
                                    # WHY: Avoid repeated database queries
                                    if fle_id:
                                        fund_legal_entity_map[normalized_csv_name] = fle_id
                                    break
                        
                        if not fle_id:
                            if entity_found:
                                # WHAT: Entity was found but FundLegalEntity doesn't exist (and we're in dry-run)
                                # WHY: In dry-run mode, we can't create FundLegalEntity, so skip this record
                                # NOTE: This is expected behavior in dry-run - the Entity exists, just needs FundLegalEntity
                                continue
                            else:
                                # WHAT: Entity name from CSV doesn't match any Entity in database
                                # WHY: Log warning but continue processing
                                # NOTE: This means the Entity doesn't exist in the Entity table at all
                                entity_not_found_count += 1
                                if entity_not_found_count <= 10:  # WHAT: Only show first 10 warnings
                                    # WHAT: Debug output to help diagnose matching issues
                                    # WHY: Show what we're looking for vs what's in database
                                    self.stdout.write(
                                        self.style.WARNING(
                                            f'Entity not found in database: "{csv_entity_name}" (servicer_id: {servicer_id})'
                                        )
                                    )
                                    # WHAT: Show normalized versions for debugging
                                    # WHY: Help identify why matching failed
                                    if entity_not_found_count <= 3:  # Only for first few
                                        self.stdout.write(
                                            f'    CSV normalized: "{csv_lower}" | "{simple_csv_normalized}" | "{normalized_csv_name}"'
                                        )
                                        # WHAT: Show similar entity names from database
                                        # WHY: Help identify potential matches
                                        similar = [e.name for e in entities if 
                                                  csv_lower in e.name.lower() or 
                                                  e.name.lower() in csv_lower or
                                                  'reliant' in e.name.lower() and 'reliant' in csv_lower]
                                        if similar:
                                            self.stdout.write(f'    Similar entities in DB: {similar}')
                                continue
                        
                        # WHAT: Find AssetIdHub by servicer_id
                        # WHY: Need to get the asset hub to update its AssetDetails
                        # HOW: Query AssetIdHub using servicer_id and specified database
                        try:
                            asset_hub = AssetIdHub.objects.using(db_alias).get(servicer_id=servicer_id)
                        except AssetIdHub.DoesNotExist:
                            # WHAT: No AssetIdHub found with this servicer_id
                            # WHY: Log warning but continue processing
                            not_found_count += 1
                            if not_found_count <= 10:  # WHAT: Only show first 10 warnings
                                self.stdout.write(
                                    self.style.WARNING(
                                        f'AssetIdHub not found for servicer_id: {servicer_id}'
                                    )
                                )
                            continue
                        
                        # WHAT: Skip actual updates if in dry-run mode
                        # WHY: Allow previewing changes without committing
                        if dry_run:
                            updated_count += 1
                            continue
                        
                        # WHAT: Get or create AssetDetails for this asset hub
                        # WHY: AssetDetails might not exist yet
                        # HOW: Use get_or_create to handle both cases, using specified database
                        asset_details, created = AssetDetails.objects.using(db_alias).get_or_create(
                            asset=asset_hub,
                            defaults={
                                'fund_legal_entity_id': fle_id,  # WHAT: Set fund_legal_entity
                                'asset_status': AssetDetails.AssetStatus.ACTIVE,  # WHAT: Default status
                            }
                        )
                        
                        # WHAT: Update fund_legal_entity if AssetDetails already existed
                        # WHY: Ensure the assignment is set even if record was pre-existing
                        if not created:
                            asset_details.fund_legal_entity_id = fle_id
                            asset_details.save(update_fields=['fund_legal_entity_id'], using=db_alias)
                        
                        updated_count += 1
                    
                    # WHAT: Progress message for user
                    # WHY: Keep user informed during long-running operations
                    if not dry_run:
                        self.stdout.write(
                            f'Processed {min(i + batch_size, len(csv_data))}/{len(csv_data)} records...',
                            ending='\r'
                        )
            except Exception as e:
                # WHAT: Handle errors during batch processing
                # WHY: Don't fail completely if one batch has issues
                # HOW: Log error and continue with next batch
                self.stdout.write(
                    self.style.ERROR(
                        f'\nError processing batch starting at {i}: {str(e)}'
                    )
                )

        # WHAT: Final summary message
        # WHY: Inform user of operation results
        self.stdout.write('')  # WHAT: New line after progress indicator
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE: No records were updated.')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'SUCCESS: Updated {updated_count} AssetDetails records.'
                )
            )
            if not_found_count > 0:
                self.stdout.write(
                    self.style.WARNING(
                        f'WARNING: {not_found_count} servicer_ids not found in AssetIdHub.'
                    )
                )
            if entity_not_found_count > 0:
                self.stdout.write(
                    self.style.WARNING(
                        f'WARNING: {entity_not_found_count} entity names not found in Entity model.'
                    )
                )

