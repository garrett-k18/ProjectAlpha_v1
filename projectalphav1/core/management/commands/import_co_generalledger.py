"""
WHAT: Django management command to import General Ledger entries from SQL files
WHY: Efficiently bulk-load GL entries from exported SQL files into the database
HOW: Reads SQL INSERT statements, parses values, and uses Django ORM bulk_create
WHERE: Run via: python manage.py import_co_generalledger
"""
import os
import re
from decimal import Decimal
from datetime import datetime, date
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models.model_co_generalLedger import GeneralLedgerEntries


class Command(BaseCommand):
    """
    WHAT: Management command class for importing General Ledger entries
    WHY: Provides CLI interface for bulk importing GL data from SQL files
    HOW: Parses SQL INSERT statements and creates GeneralLedgerEntries objects
    """
    
    help = 'Import General Ledger entries from SQL files in z.Admin directory'

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
            help='Specific SQL file to import (just the filename, not full path)',
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
            help='Parse files and show what would be imported without actually inserting data',
        )

    def handle(self, *args, **options):
        """
        WHAT: Main entry point for the management command
        WHY: Orchestrates the entire import process
        HOW: Reads files, parses data, and bulk creates database records
        """
        # Get the path to the z.Admin directory
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        sql_dir = os.path.join(base_dir, 'z.Admin')
        
        # Get all SQL files matching the pattern
        if options['file']:
            # Import a specific file
            sql_files = [options['file']]
        else:
            # Import all GeneralLedgerDetails SQL files
            all_files = os.listdir(sql_dir)
            sql_files = sorted([
                f for f in all_files 
                if f.startswith('GeneralLedgerDetails_') and f.endswith('.sql')
            ])
        
        # Display files to be imported
        if options['dry_run']:
            self.stdout.write(self.style.WARNING(f'\n*** DRY RUN MODE - No data will be inserted ***'))
        
        self.stdout.write(self.style.WARNING(f'\nFound {len(sql_files)} SQL file(s) to import:'))
        for sql_file in sql_files:
            self.stdout.write(f'  - {sql_file}')
        
        # Get confirmation unless --no-confirm or --dry-run is set
        if not options['no_confirm'] and not options['dry_run']:
            confirm = input('\nProceed with import? (yes/no): ')
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.ERROR('Import cancelled.'))
                return
        
        # Process each SQL file
        total_imported = 0
        batch_size = options['batch_size']
        
        for sql_file in sql_files:
            file_path = os.path.join(sql_dir, sql_file)
            
            self.stdout.write(self.style.NOTICE(f'\nProcessing: {sql_file}'))
            
            try:
                # Read the SQL file
                with open(file_path, 'r', encoding='utf-8') as f:
                    sql_content = f.read()
                
                # Parse and import the records
                imported_count = self._import_from_sql(sql_content, batch_size, options['dry_run'])
                total_imported += imported_count
                
                if options['dry_run']:
                    self.stdout.write(self.style.SUCCESS(f'  [OK] Would import {imported_count} records'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'  [OK] Imported {imported_count} records'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  [ERROR] Error processing {sql_file}: {str(e)}'))
                # Continue with next file instead of stopping
                continue
        
        # Display final summary
        if options['dry_run']:
            self.stdout.write(self.style.SUCCESS(f'\n[SUCCESS] DRY RUN COMPLETE: Would import {total_imported} total records'))
            self.stdout.write(self.style.NOTICE(f'           Run without --dry-run to actually insert data'))
        else:
            self.stdout.write(self.style.SUCCESS(f'\n[SUCCESS] Total records imported: {total_imported}'))

    def _import_from_sql(self, sql_content, batch_size, dry_run=False):
        """
        WHAT: Parse SQL INSERT statements and import records into database
        WHY: Convert SQL format to Django ORM objects for database insertion
        HOW: Uses regex to extract values, creates objects, and bulk inserts
        
        ARGS:
            sql_content (str): The SQL file content to parse
            batch_size (int): Number of records to insert per batch
            dry_run (bool): If True, parse only without inserting data
            
        RETURNS:
            int: Number of records successfully imported (or would be imported in dry-run)
        """
        # Pattern to match the VALUES section of INSERT statements
        # This captures all the data rows in the SQL
        values_pattern = r"VALUES\s*\n\s*(.*?)(?=INSERT|$)"
        
        # Find all VALUES sections in the SQL file
        values_sections = re.findall(values_pattern, sql_content, re.DOTALL)
        
        # List to store all GeneralLedgerEntries objects
        entries_to_create = []
        
        # Process each VALUES section
        for values_section in values_sections:
            # Parse individual record tuples from the VALUES section
            # Each record is a tuple like ('value1','value2',...)
            records = self._parse_values_section(values_section)
            
            # Convert each record to a GeneralLedgerEntries object
            for record_values in records:
                try:
                    entry_obj = self._create_entry_object(record_values)
                    entries_to_create.append(entry_obj)
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'  Warning: Skipped invalid record: {str(e)}'))
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
        
        return total_created

    def _parse_values_section(self, values_section):
        """
        WHAT: Parse the VALUES section to extract individual record tuples
        WHY: Need to extract each row of data from the SQL VALUES clause
        HOW: Uses regex to match tuples and split them properly
        
        ARGS:
            values_section (str): The VALUES section from the SQL statement
            
        RETURNS:
            list: List of tuples, each containing field values for one record
        """
        # Pattern to match individual record tuples
        # Handles quoted strings, NULLs, numbers, and dates
        record_pattern = r"\(([^)]+(?:\([^)]*\))?[^)]*)\)"
        
        # Find all record tuples
        record_matches = re.findall(record_pattern, values_section)
        
        records = []
        for record_match in record_matches:
            # Skip if this looks like a nested function call rather than data
            if 'INSERT INTO' in record_match:
                continue
                
            # Parse the individual values within the tuple
            values = self._parse_tuple_values(record_match)
            
            # Only add if we have the expected number of fields (21 fields)
            if len(values) == 21:
                records.append(values)
        
        return records

    def _parse_tuple_values(self, tuple_content):
        """
        WHAT: Parse individual values from a SQL tuple
        WHY: Extract each field value handling quotes, NULLs, and special characters
        HOW: Uses regex and string manipulation to split on commas correctly
        
        ARGS:
            tuple_content (str): Content inside parentheses like 'val1','val2',NULL,...
            
        RETURNS:
            list: List of parsed values
        """
        values = []
        current_value = ''
        in_quotes = False
        
        # Iterate through each character to handle quoted strings properly
        i = 0
        while i < len(tuple_content):
            char = tuple_content[i]
            
            # Handle quotes
            if char == "'":
                if in_quotes:
                    # Check if this is an escaped quote
                    if i + 1 < len(tuple_content) and tuple_content[i + 1] == "'":
                        current_value += "'"
                        i += 1  # Skip the next quote
                    else:
                        # End of quoted string
                        in_quotes = False
                else:
                    # Start of quoted string
                    in_quotes = True
            
            # Handle commas (field separators)
            elif char == ',' and not in_quotes:
                # End of current value
                values.append(current_value.strip())
                current_value = ''
            
            # Regular character
            else:
                current_value += char
            
            i += 1
        
        # Add the last value
        if current_value.strip():
            values.append(current_value.strip())
        
        return values

    def _create_entry_object(self, values):
        """
        WHAT: Create a GeneralLedgerEntries object from parsed SQL values
        WHY: Convert string values to appropriate Python types for Django model
        HOW: Maps each value to corresponding model field with type conversion
        
        ARGS:
            values (list): List of 21 string values from SQL tuple
            
        RETURNS:
            GeneralLedgerEntries: Django model instance ready for insertion
        """
        # Helper function to convert SQL value to Python value
        def parse_value(val, field_type='str'):
            """
            WHAT: Convert SQL string value to appropriate Python type
            WHY: Django models need proper Python types (Decimal, date, etc.)
            HOW: Handles NULL, empty strings, and type conversions
            """
            if val == 'NULL' or val == '':
                return None
            
            # Remove quotes if present
            if val.startswith("'") and val.endswith("'"):
                val = val[1:-1]
            
            # Return None for empty strings after quote removal
            if val == '':
                return None
            
            # Type-specific conversions
            if field_type == 'decimal':
                return Decimal(val) if val else Decimal('0.00')
            elif field_type == 'date':
                # Parse date from format '2025-11-03'
                return datetime.strptime(val, '%Y-%m-%d').date() if val else None
            elif field_type == 'datetime':
                # Parse datetime from format '2025-11-01 00:00:00'
                return datetime.strptime(val, '%Y-%m-%d %H:%M:%S') if val else None
            else:
                return val if val else None
        
        # Map the 21 values to model fields in order
        # Order: entry, company_name, loan_number, borrower_name, document_number,
        #        external_document_number, document_type, loan_type, date_funded,
        #        amount, credit_amount, debit_amount, account_number, account_name,
        #        description, reason_code, comment, posting_date, cost_center,
        #        cost_center_name, entry_date
        
        entry_obj = GeneralLedgerEntries(
            entry=parse_value(values[0]),  # entry - required field
            company_name=parse_value(values[1]),  # company_name - required
            loan_number=parse_value(values[2]),  # loan_number - optional
            borrower_name=parse_value(values[3]),  # borrower_name - optional
            document_number=parse_value(values[4]),  # document_number - optional
            external_document_number=parse_value(values[5]),  # external_document_number - optional
            document_type=parse_value(values[6]),  # document_type - optional
            loan_type=parse_value(values[7]),  # loan_type - optional
            date_funded=parse_value(values[8], 'date'),  # date_funded - optional date
            amount=parse_value(values[9], 'decimal'),  # amount - optional decimal
            credit_amount=parse_value(values[10], 'decimal'),  # credit_amount - required decimal
            debit_amount=parse_value(values[11], 'decimal'),  # debit_amount - required decimal
            account_number=parse_value(values[12]),  # account_number - required
            account_name=parse_value(values[13]),  # account_name - required
            description=parse_value(values[14]),  # description - optional text
            reason_code=parse_value(values[15]),  # reason_code - optional
            comment=parse_value(values[16]),  # comment - optional text
            posting_date=parse_value(values[17], 'date'),  # posting_date - required date
            cost_center=parse_value(values[18]),  # cost_center - optional
            cost_center_name=parse_value(values[19]),  # cost_center_name - optional
            entry_date=parse_value(values[20], 'datetime'),  # entry_date - required datetime (but model uses DateField)
        )
        
        # Note: created_at and updated_at will be auto-populated by database defaults
        
        return entry_obj

    def _get_sql_files_info(self, sql_dir):
        """
        WHAT: Get information about available SQL files
        WHY: Provide user with overview of what will be imported
        HOW: Scans directory and counts records in each file
        
        ARGS:
            sql_dir (str): Path to directory containing SQL files
            
        RETURNS:
            dict: Dictionary mapping filename to record count
        """
        files_info = {}
        
        all_files = os.listdir(sql_dir)
        sql_files = sorted([
            f for f in all_files 
            if f.startswith('GeneralLedgerDetails_') and f.endswith('.sql')
        ])
        
        # Count records in each file (rough estimate by counting opening parens)
        for sql_file in sql_files:
            file_path = os.path.join(sql_dir, sql_file)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Count record tuples (rough estimate)
                record_count = content.count('\n\t (')
                files_info[sql_file] = record_count
        
        return files_info

