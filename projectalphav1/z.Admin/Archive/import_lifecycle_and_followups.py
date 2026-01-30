"""
WHAT: Django management command to import lifecycle status and follow-up dates from CSV
WHY: Bulk update AssetDetails.asset_status and CalendarEvent follow-ups based on servicer_id
HOW: Reads CSV, matches servicer_id to AssetIdHub, updates AssetDetails and creates CalendarEvents
WHERE: Run via: python manage.py import_lifecycle_and_followups --csv-file path/to/file.csv

Expected CSV columns:
- servicer_id: Servicer ID to match AssetIdHub.servicer_id
- lifecycle_status: ACTIVE or LIQUIDATED (maps to AssetDetails.asset_status)
- follow_up_date: Date for follow-up (creates CalendarEvent if provided)

Docs reviewed:
- Django management commands: https://docs.djangoproject.com/en/stable/howto/custom-management-commands/
- CSV reading: https://docs.python.org/3/library/csv.html
"""

import csv
import os
from pathlib import Path
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import AssetIdHub, AssetDetails
from core.models.model_co_calendar import CalendarEvent
from core.management.utils.prod_db_helper import add_prod_db_args, setup_prod_db, check_db_connection


class Command(BaseCommand):
    """
    WHAT: Management command to import lifecycle status and follow-up dates
    WHY: Provides CLI interface for bulk updating AssetDetails and creating follow-up events
    HOW: Reads CSV, matches servicer_id, updates lifecycle status, creates calendar events
    """
    
    help = 'Import lifecycle status and follow-up dates from CSV using servicer_id'

    def add_arguments(self, parser):
        """Define command-line arguments"""
        parser.add_argument(
            '--csv-file',
            type=str,
            required=True,
            help='Path to CSV file relative to project root',
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
        add_prod_db_args(parser)

    def handle(self, *args, **options):
        """Main command execution"""
        csv_file = options['csv_file']
        dry_run = options['dry_run']
        batch_size = options['batch_size']
        
        # Setup database connection - default to NEWDEV if no override specified
        if not options.get('prod') and not options.get('dev'):
            # Use NEWDEV database from .env by default
            os.environ['DATABASE_URL'] = os.getenv('DB_NEWDEV')
            db_alias = 'default'
        else:
            db_alias = setup_prod_db(options)
        
        check_db_connection(options, self)
        
        # Resolve CSV file path (relative to projectalphav1 directory)
        project_root = Path(__file__).resolve().parents[3]
        csv_path = project_root / csv_file
        
        if not csv_path.exists():
            self.stdout.write(
                self.style.ERROR(f'CSV file not found: {csv_path}')
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS(f'Reading CSV from: {csv_path}')
        )
        
        # Read CSV file
        csv_data = []
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                csv_data.append(row)
        
        self.stdout.write(f'Found {len(csv_data)} rows in CSV')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE: No records will be updated.')
            )
        
        # Process records
        updated_lifecycle_count = 0
        created_followup_count = 0
        not_found_count = 0
        error_count = 0
        
        for i in range(0, len(csv_data), batch_size):
            batch = csv_data[i:i + batch_size]
            
            try:
                with transaction.atomic(using=db_alias):
                    for row in batch:
                        # Handle column names with spaces and different casing
                        servicer_id = (row.get('ServicerID') or row.get('servicer_id') or '').strip()
                        lifecycle_status = (row.get('Lifecylce Status') or row.get('lifecycle_status') or '').strip().upper()
                        follow_up_date_str = (row.get('Follow Up') or row.get('follow_up_date') or '').strip()
                        
                        if not servicer_id:
                            continue
                        
                        # Find AssetIdHub by servicer_id
                        try:
                            asset_hub = AssetIdHub.objects.using(db_alias).get(servicer_id=servicer_id)
                        except AssetIdHub.DoesNotExist:
                            not_found_count += 1
                            if not_found_count <= 10:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f'AssetIdHub not found for servicer_id: {servicer_id}'
                                    )
                                )
                            continue
                        except AssetIdHub.MultipleObjectsReturned:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'Multiple AssetIdHub found for servicer_id: {servicer_id} - skipping'
                                )
                            )
                            error_count += 1
                            continue
                        
                        if dry_run:
                            if lifecycle_status in ['ACTIVE', 'LIQUIDATED']:
                                updated_lifecycle_count += 1
                            if follow_up_date_str:
                                created_followup_count += 1
                            continue
                        
                        # Update lifecycle status in AssetDetails
                        if lifecycle_status in ['ACTIVE', 'LIQUIDATED']:
                            asset_details, created = AssetDetails.objects.using(db_alias).get_or_create(
                                asset=asset_hub,
                                defaults={
                                    'asset_status': lifecycle_status,
                                }
                            )
                            
                            if not created and asset_details.asset_status != lifecycle_status:
                                asset_details.asset_status = lifecycle_status
                                asset_details.save(using=db_alias, update_fields=['asset_status', 'updated_at'])
                            
                            updated_lifecycle_count += 1
                        
                        # Create follow-up CalendarEvent if date provided
                        if follow_up_date_str:
                            try:
                                # Parse date (supports multiple formats)
                                follow_up_date = None
                                for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%m-%d-%Y', '%Y/%m/%d']:
                                    try:
                                        follow_up_date = datetime.strptime(follow_up_date_str, fmt).date()
                                        break
                                    except ValueError:
                                        continue
                                
                                if follow_up_date:
                                    # Create calendar event (is_public=True for firm-wide visibility)
                                    # WHAT: Set completed=False so task appears in task modals
                                    # WHY: All imported follow-ups start as active (not completed)
                                    CalendarEvent.objects.using(db_alias).create(
                                        title=f'Follow-up: {servicer_id}',
                                        date=follow_up_date,
                                        time='All Day',
                                        description='Imported follow-up',
                                        task_type='follow_up',
                                        asset_hub=asset_hub,
                                        completed=False,
                                        is_public=True,
                                    )
                                    created_followup_count += 1
                                else:
                                    self.stdout.write(
                                        self.style.WARNING(
                                            f'Invalid date format for servicer_id {servicer_id}: {follow_up_date_str}'
                                        )
                                    )
                            except Exception as e:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f'Error creating follow-up for {servicer_id}: {str(e)}'
                                    )
                                )
                                error_count += 1
                    
                    # Progress message
                    if not dry_run:
                        self.stdout.write(
                            f'Processed {min(i + batch_size, len(csv_data))}/{len(csv_data)} records...',
                            ending='\r'
                        )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'\nError processing batch starting at {i}: {str(e)}'
                    )
                )
                error_count += 1

        # Final summary
        self.stdout.write('')
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE: No records were updated.')
            )
            self.stdout.write(f'Would update lifecycle status: {updated_lifecycle_count}')
            self.stdout.write(f'Would create follow-up events: {created_followup_count}')
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'SUCCESS: Updated {updated_lifecycle_count} lifecycle statuses.'
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'SUCCESS: Created {created_followup_count} follow-up events.'
                )
            )
        
        if not_found_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'WARNING: {not_found_count} servicer_ids not found in AssetIdHub.'
                )
            )
        
        if error_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'WARNING: {error_count} errors occurred during processing.'
                )
            )
