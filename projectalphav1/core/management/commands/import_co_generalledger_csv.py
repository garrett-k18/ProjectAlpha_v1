"""
WHAT: Django management command to import General Ledger entries from CSV files
WHY: Efficiently bulk-load GL entries from CSV exports into the database
HOW: Uses Python csv module to read CSV, creates Django model objects, and bulk inserts
WHERE: Run via: python manage.py import_co_generalledger_csv
"""
import os
import csv
from decimal import Decimal, InvalidOperation
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models.model_co_generalLedger import GeneralLedgerEntries


class Command(BaseCommand):
    """
    WHAT: Management command class for importing General Ledger entries from CSV
    WHY: Provides CLI interface for bulk importing GL data from CSV files
    HOW: Parses CSV files and creates GeneralLedgerEntries objects using Django ORM
    """
    
    help = 'Import General Ledger entries from CSV files in z.Admin directory'

    def add_arguments(self, parser):
        """
        WHAT: Define command-line arguments for the import command
        WHY: Allow flexible control over import behavior
        HOW: Uses argparse to define optional arguments
        """
        # Optional argument to specify a single file to import
        parser.add_argument(
            '--file',
            type=str,
            help='Specific CSV file to import (just the filename, not full path)',
        )
        
        # Optional argument to specify batch size for bulk_create
        parser.add_argument(
            '--batch-size',
            type=int,
            default=500,
            help='Number of records to insert per batch (default: 500)',
        )
        
        # Optional flag to skip confirmation prompt
        parser.add_argument(
            '--no-confirm',
            action='store_true',
            help='Skip confirmation prompt and proceed with import',
        )
        
        # Optional flag for dry-run mode
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Parse CSV and show what would be imported without actually inserting data',
        )

    def handle(self, *args, **options):
        """
        WHAT: Main entry point for the management command
        WHY: Orchestrates the entire import process
        HOW: Reads CSV files, parses data, and bulk creates database records
        """
        # Get the path to the z.Admin directory
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        csv_dir = os.path.join(base_dir, 'z.Admin')
        
        # Get all CSV files matching the pattern
        if options['file']:
            # Import a specific file
            csv_files = [options['file']]
        else:
            # Import all GeneralLedgerDetails CSV files
            all_files = os.listdir(csv_dir)
            csv_files = sorted([
                f for f in all_files 
                if f.startswith('GeneralLedgerDetails_') and f.endswith('.csv')
            ])
        
        # Display files to be imported
        if options['dry_run']:
            self.stdout.write(self.style.WARNING(f'\n*** DRY RUN MODE - No data will be inserted ***'))
        
        self.stdout.write(self.style.WARNING(f'\nFound {len(csv_files)} CSV file(s) to import:'))
        for csv_file in csv_files:
            self.stdout.write(f'  - {csv_file}')
        
        # Get confirmation unless --no-confirm or --dry-run is set
        if not options['no_confirm'] and not options['dry_run']:
            confirm = input('\nProceed with import? (yes/no): ')
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.ERROR('Import cancelled.'))
                return
        
        # Process each CSV file
        total_imported = 0
        total_errors = 0
        batch_size = options['batch_size']
        
        for csv_file in csv_files:
            file_path = os.path.join(csv_dir, csv_file)
            
            self.stdout.write(self.style.NOTICE(f'\nProcessing: {csv_file}'))
            
            try:
                # Parse and import the records
                imported_count, error_count = self._import_from_csv(file_path, batch_size, options['dry_run'])
                total_imported += imported_count
                total_errors += error_count
                
                if options['dry_run']:
                    self.stdout.write(self.style.SUCCESS(f'  [OK] Would import {imported_count} records'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'  [OK] Imported {imported_count} records'))
                
                if error_count > 0:
                    self.stdout.write(self.style.WARNING(f'  [WARNING] Skipped {error_count} invalid records'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  [ERROR] Error processing {csv_file}: {str(e)}'))
                # Continue with next file instead of stopping
                continue
        
        # Display final summary
        if options['dry_run']:
            self.stdout.write(self.style.SUCCESS(f'\n[SUCCESS] DRY RUN COMPLETE: Would import {total_imported} total records'))
            if total_errors > 0:
                self.stdout.write(self.style.WARNING(f'           Would skip {total_errors} invalid records'))
            self.stdout.write(self.style.NOTICE(f'           Run without --dry-run to actually insert data'))
        else:
            self.stdout.write(self.style.SUCCESS(f'\n[SUCCESS] Total records imported: {total_imported}'))
            if total_errors > 0:
                self.stdout.write(self.style.WARNING(f'           Total records skipped: {total_errors}'))

    def _import_from_csv(self, file_path, batch_size, dry_run=False):
        """
        WHAT: Parse CSV file and import records into database
        WHY: Convert CSV format to Django ORM objects for database insertion
        HOW: Uses csv.DictReader to read CSV, creates objects, and bulk inserts
        
        ARGS:
            file_path (str): Full path to the CSV file
            batch_size (int): Number of records to insert per batch
            dry_run (bool): If True, parse only without inserting data
            
        RETURNS:
            tuple: (imported_count, error_count)
        """
        # List to store all GeneralLedgerEntries objects
        entries_to_create = []
        error_count = 0
        
        # Open and read the CSV file
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            # Use DictReader to automatically map column names to values
            reader = csv.DictReader(csvfile)
            
            # Process each row
            for row_num, row in enumerate(reader, start=2):  # Start at 2 because row 1 is header
                try:
                    entry_obj = self._create_entry_from_row(row)
                    entries_to_create.append(entry_obj)
                except Exception as e:
                    error_count += 1
                    if error_count <= 5:  # Only show first 5 errors to avoid spam
                        self.stdout.write(self.style.WARNING(f'  Warning: Row {row_num} skipped: {str(e)}'))
                    continue
        
        # Bulk create all entries in batches (or just count in dry-run mode)
        total_created = 0
        
        if dry_run:
            # In dry-run mode, just count the records without inserting
            total_created = len(entries_to_create)
            
            # Show sample of first 3 records that would be imported
            if entries_to_create:
                self.stdout.write(self.style.NOTICE(f'  Sample records (first 3):'))
                for idx, entry in enumerate(entries_to_create[:3]):
                    self.stdout.write(f'    {idx + 1}. Entry: {entry.entry}, Company: {entry.company_name}, '
                                    f'Account: {entry.account_number} - {entry.account_name}, '
                                    f'Debit: {entry.debit_amount}, Credit: {entry.credit_amount}')
        else:
            # Actually insert the data
            with transaction.atomic():
                # Split into batches for efficient insertion
                for i in range(0, len(entries_to_create), batch_size):
                    batch = entries_to_create[i:i + batch_size]
                    GeneralLedgerEntries.objects.bulk_create(batch, ignore_conflicts=True)
                    total_created += len(batch)
                    
                    # Show progress for large imports
                    if total_created % 1000 == 0:
                        self.stdout.write(f'  ... {total_created} records processed')
        
        return total_created, error_count

    def _create_entry_from_row(self, row):
        """
        WHAT: Create a GeneralLedgerEntries object from a CSV row
        WHY: Convert CSV string values to appropriate Python types for Django model
        HOW: Maps each CSV column to corresponding model field with type conversion
        
        ARGS:
            row (dict): Dictionary with CSV column names as keys
            
        RETURNS:
            GeneralLedgerEntries: Django model instance ready for insertion
        """
        # Helper function to parse values safely
        def parse_value(value, field_type='str'):
            """
            WHAT: Convert CSV string value to appropriate Python type
            WHY: Django models need proper Python types (Decimal, date, etc.)
            HOW: Handles empty strings, None, and type conversions
            """
            # Handle None or empty string
            if value is None or value == '' or value == '""':
                return None
            
            # Remove quotes if present
            value = value.strip().strip('"')
            
            # Return None for empty strings after cleanup
            if value == '':
                return None
            
            # Type-specific conversions
            if field_type == 'decimal':
                try:
                    return Decimal(value) if value else Decimal('0.00')
                except (InvalidOperation, ValueError):
                    return Decimal('0.00')
            elif field_type == 'date':
                # Parse date from format '2025-11-03'
                try:
                    return datetime.strptime(value, '%Y-%m-%d').date() if value else None
                except ValueError:
                    return None
            elif field_type == 'datetime':
                # Parse datetime from format '2025-11-01 00:00:00'
                try:
                    # Handle both date and datetime formats
                    if ' ' in value:
                        # Full datetime
                        parsed_dt = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                    else:
                        # Just date
                        parsed_dt = datetime.strptime(value, '%Y-%m-%d')
                    return parsed_dt.date()  # Return date only since entry_date is DateField
                except ValueError:
                    return None
            else:
                return value if value else None
        
        # Create the GeneralLedgerEntries object with all fields from CSV
        entry_obj = GeneralLedgerEntries(
            entry=parse_value(row.get('entry')),  # Required field
            company_name=parse_value(row.get('company_name')),  # Required field
            loan_number=parse_value(row.get('loan_number')),  # Optional field
            borrower_name=parse_value(row.get('borrower_name')),  # Optional field
            document_number=parse_value(row.get('document_number')),  # Optional field
            external_document_number=parse_value(row.get('external_document_number')),  # Optional field
            document_type=parse_value(row.get('document_type')),  # Optional field
            loan_type=parse_value(row.get('loan_type')),  # Optional field
            date_funded=parse_value(row.get('date_funded'), 'date'),  # Optional date field
            amount=parse_value(row.get('amount'), 'decimal'),  # Optional decimal field
            credit_amount=parse_value(row.get('credit_amount'), 'decimal'),  # Required decimal field
            debit_amount=parse_value(row.get('debit_amount'), 'decimal'),  # Required decimal field
            account_number=parse_value(row.get('account_number')),  # Required field
            account_name=parse_value(row.get('account_name')),  # Required field
            description=parse_value(row.get('description')),  # Optional text field
            reason_code=parse_value(row.get('reason_code')),  # Optional field
            comment=parse_value(row.get('comment')),  # Optional text field
            posting_date=parse_value(row.get('posting_date'), 'date'),  # Required date field
            cost_center=parse_value(row.get('cost_center')),  # Optional field
            cost_center_name=parse_value(row.get('cost_center_name')),  # Optional field
            entry_date=parse_value(row.get('entry_date'), 'datetime'),  # Required date field (stored as datetime in CSV)
        )
        
        # Note: created_at and updated_at will be auto-populated by database defaults
        
        return entry_obj

