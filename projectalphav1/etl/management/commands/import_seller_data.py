"""
Django management command for intelligent ETL of Excel/CSV files into SellerRawData model.

WHAT: Imports seller data from Excel/CSV files into SellerRawData model
      Supports FILE MODE (single file) or OUTLOOK MODE (scan inbox for attachments)
WHY: Automates data import with AI-powered column mapping and Outlook integration
WHERE: Run via `python manage.py import_seller_data --file data.xlsx` or `--scan-outlook`
HOW: Uses modular ETL pipeline with specialized components

USAGE - FILE MODE:
    python manage.py import_seller_data --file data.xlsx --seller-name "ABC" --auto-create

USAGE - OUTLOOK MODE:
    python manage.py import_seller_data --scan-outlook --auto-create --outlook-unread-only --outlook-mark-read

DEPENDENCIES: pip install pandas openpyxl anthropic msal requests msoffcrypto-tool
"""

from pathlib import Path
from typing import Optional

from django.core.management.base import BaseCommand, CommandError

# Import ETL modules
from etl.services import (
    OutlookScanner,
    SellerIdentifier,
    AIColumnMapper,
    FileProcessor,
    DataImporter,
)


class Command(BaseCommand):
    """Django management command for ETL of seller data files."""

    help = 'Import seller data from Excel or CSV files with AI-powered column mapping'

    def add_arguments(self, parser):
        """Define command-line arguments."""
        # MODE SELECTION
        parser.add_argument('--file', type=str, help='Path to Excel/CSV file')
        parser.add_argument('--scan-outlook', action='store_true', help='Scan Outlook inbox')

        # OUTLOOK OPTIONS
        parser.add_argument('--outlook-subject-filter', type=str, help='Filter by subject (comma-separated)')
        parser.add_argument('--outlook-sender-filter', type=str, help='Filter by sender (comma-separated)')
        parser.add_argument('--outlook-days', type=int, default=7, help='Days to look back (default: 7)')
        parser.add_argument('--outlook-unread-only', action='store_true', help='Only unread emails')
        parser.add_argument('--outlook-mark-read', action='store_true', help='Mark as read after processing')
        parser.add_argument('--outlook-folder', type=str, help='Outlook folder to scan')

        # SELLER/TRADE
        parser.add_argument('--seller-id', type=int, help='Existing seller ID')
        parser.add_argument('--trade-id', type=int, help='Existing trade ID')
        parser.add_argument('--seller-name', type=str, help='Seller name')
        parser.add_argument('--trade-name', type=str, help='Trade name')
        parser.add_argument('--auto-create', action='store_true', help='Auto-create seller/trade')

        # FILE PROCESSING
        parser.add_argument('--config', type=str, help='JSON config with column mappings')
        parser.add_argument('--sheet', type=str, default=0, help='Excel sheet (default: 0)')
        parser.add_argument('--skip-rows', type=int, default=0, help='Rows to skip (default: 0)')
        parser.add_argument('--limit-rows', type=int, help='Limit to first N rows (for testing)')
        parser.add_argument('--dry-run', action='store_true', help='Preview without saving')
        parser.add_argument('--no-ai', action='store_true', help='Disable AI mapping')
        parser.add_argument('--batch-size', type=int, default=100, help='Batch size (default: 100)')
        parser.add_argument('--save-mapping', type=str, help='Save mapping to JSON file')
        parser.add_argument('--update-existing', action='store_true', help='Update existing records')

    def handle(self, *args, **options):
        """Main execution method."""
        if options.get('scan_outlook'):
            self._handle_outlook_mode(options)
        elif options.get('file'):
            self._handle_file_mode(options['file'], options)
        else:
            raise CommandError('Must provide either --file or --scan-outlook')

    def _handle_outlook_mode(self, options):
        """Handle Outlook inbox scanning mode."""
        self.stdout.write(self.style.SUCCESS('\n=== OUTLOOK INBOX SCANNING MODE ===\n'))

        # Initialize scanner
        scanner = OutlookScanner(folder_name=options.get('outlook_folder'), stdout=self.stdout)

        # Scan emails
        emails = scanner.scan(
            days_back=options.get('outlook_days', 7),
            unread_only=options.get('outlook_unread_only', False),
            subject_filter=options.get('outlook_subject_filter'),
            sender_filter=options.get('outlook_sender_filter')
        )

        if not emails:
            self.stdout.write(self.style.WARNING('[WARNING] No emails found\n'))
            return

        # Process each email
        total_files = 0
        total_records = 0
        identifier = SellerIdentifier()

        for idx, email in enumerate(emails, 1):
            subject = email.get('subject', 'No Subject')
            sender = email.get('from', {}).get('emailAddress', {}).get('address', 'Unknown')

            self.stdout.write(f'\n--- Email {idx}/{len(emails)} ---')
            self.stdout.write(f'Subject: {subject}')
            self.stdout.write(f'From: {sender}')

            # Identify seller
            seller_rule = identifier.identify(email)
            if seller_rule:
                self.stdout.write(f'   Identified as: {seller_rule.name}')

            # Download attachments
            files = scanner.download_attachments(email, seller_rule)
            if not files:
                self.stdout.write(self.style.WARNING('   [WARNING] No Excel attachments\n'))
                continue

            # Process files
            for file_path, password in files:
                try:
                    self.stdout.write(f'\n   Processing: {file_path.name}')
                    # Pass email data for AI seller matching
                    options_with_email = options.copy()
                    options_with_email['email_data'] = email
                    records = self._process_single_file(file_path, password, options_with_email)
                    total_files += 1
                    total_records += records
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'   [ERROR] {str(e)}'))

            # Mark as read
            if options.get('outlook_mark_read'):
                scanner.mark_as_read(email['id'])

        # Summary
        self.stdout.write(self.style.SUCCESS(f'\n\n=== COMPLETE ==='))
        self.stdout.write(self.style.SUCCESS(f'Emails: {len(emails)}, Files: {total_files}, Records: {total_records}\n'))

    def _handle_file_mode(self, file_path_str: str, options):
        """Handle single file import mode."""
        file_path = Path(file_path_str)
        if not file_path.exists():
            raise CommandError(f'File not found: {file_path}')

        self.stdout.write(self.style.SUCCESS(f'\n=== FILE IMPORT MODE ==='))
        self.stdout.write(f'   File: {file_path}\n')
        self._process_single_file(file_path, None, options)

    def _process_single_file(self, file_path: Path, password: Optional[str], options: dict) -> int:
        """Process a single file through ETL pipeline."""
        # Initialize importer with AI seller matching
        importer = DataImporter(
            seller_id=options.get('seller_id'),
            trade_id=options.get('trade_id'),
            seller_name=options.get('seller_name'),
            trade_name=options.get('trade_name'),
            auto_create=options.get('auto_create', False),
            update_existing=options.get('update_existing', False),
            use_ai_seller_matching=not options.get('no_ai', False),  # Enable AI seller matching unless --no-ai
            email_data=options.get('email_data'),  # Pass email data for AI context
            stdout=self.stdout
        )

        # Get/create seller and trade
        seller, trade = importer.get_or_create_seller_trade(file_path)

        # Read file
        processor = FileProcessor(file_path, password=password, stdout=self.stdout)
        df = processor.read(sheet=options.get('sheet', 0), skip_rows=options.get('skip_rows', 0))
        
        # Limit rows if requested (for testing)
        limit_rows = options.get('limit_rows')
        if limit_rows and limit_rows > 0:
            original_count = len(df)
            df = df.head(limit_rows)
            self.stdout.write(self.style.WARNING(f'      [LIMIT] Processing only {len(df)} of {original_count} rows (testing mode)'))
        
        self.stdout.write(self.style.SUCCESS(f'      [OK] Loaded {len(df)} rows, {len(df.columns)} columns'))

        # Map columns
        if options.get('config'):
            mapper = AIColumnMapper.from_config(options['config'], stdout=self.stdout)
            column_mapping = mapper.map()
        else:
            mapper = AIColumnMapper(df.columns, stdout=self.stdout)
            column_mapping = mapper.map(use_ai=not options.get('no_ai', False))

            # Save mapping if requested
            if options.get('save_mapping'):
                mapper.save_mapping(column_mapping, options['save_mapping'])

        # Import data
        if options.get('dry_run'):
            self.stdout.write(self.style.WARNING(f'      [DRY RUN] Would import {len(df)} records'))
            return 0

        records_imported = importer.import_data(
            df=df,
            column_mapping=column_mapping,
            seller=seller,
            trade=trade,
            batch_size=options.get('batch_size', 100),
            file_path=file_path
        )
        return records_imported
