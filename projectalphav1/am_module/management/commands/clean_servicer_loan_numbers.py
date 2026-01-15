"""
Django management command to clean loan_number fields in all Servicer models.

WHAT:
- Removes leading zeros from loan_number fields in all ServicerXxxData models
- Updates records in-place to match the cleaned format

WHY:
- Loan numbers should be stored without leading zeros for consistency
- Ensures matching with AssetIdHub.servicer_id which is already cleaned

HOW:
- Iterates through all Servicer models with loan_number fields
- Strips leading zeros from each loan_number
- Updates records in batches for efficiency
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

from am_module.models.servicers import (
    ServicerCommentData,
    ServicerPayHistoryData,
    ServicerTransactionData,
)


def _normalize_loan_number(loan_number: str) -> str:
    """Strip leading zeros from loan number, keeping at least one digit."""
    if not loan_number:
        return loan_number
    trimmed = loan_number.lstrip('0')
    return trimmed if trimmed else '0'


class Command(BaseCommand):
    help = 'Clean loan_number fields by removing leading zeros from all Servicer models'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview changes without updating database'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=500,
            help='Number of records to update per batch (default: 500)'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        batch_size = options['batch_size']

        if dry_run:
            self.stdout.write(self.style.WARNING('[DRY RUN MODE] No changes will be saved'))

        # Define models to clean
        models_to_clean = [
            ('ServicerCommentData', ServicerCommentData),
            ('ServicerPayHistoryData', ServicerPayHistoryData),
            ('ServicerTransactionData', ServicerTransactionData),
        ]

        total_updated = 0

        for model_name, model_class in models_to_clean:
            self.stdout.write(f"\n{'='*60}")
            self.stdout.write(f"Processing {model_name}...")
            self.stdout.write(f"{'='*60}")

            # Find records with leading zeros in loan_number
            # Use regex to find loan_numbers that start with '0' followed by more digits
            records_with_leading_zeros = model_class.objects.filter(
                Q(loan_number__regex=r'^0[0-9]+')
            )

            total_count = records_with_leading_zeros.count()
            
            if total_count == 0:
                self.stdout.write(self.style.SUCCESS(f"  ✓ No records need cleaning in {model_name}"))
                continue

            self.stdout.write(f"  Found {total_count} records with leading zeros")

            updated_count = 0
            batch = []

            for record in records_with_leading_zeros.iterator(chunk_size=batch_size):
                original = record.loan_number
                cleaned = _normalize_loan_number(original)
                
                if original != cleaned:
                    if dry_run:
                        self.stdout.write(
                            f"    Would update: '{original}' → '{cleaned}' (ID: {record.id})"
                        )
                        updated_count += 1
                    else:
                        record.loan_number = cleaned
                        batch.append(record)
                        
                        if len(batch) >= batch_size:
                            with transaction.atomic():
                                model_class.objects.bulk_update(batch, ['loan_number'])
                            updated_count += len(batch)
                            self.stdout.write(f"    Updated {updated_count}/{total_count} records...")
                            batch = []

            # Update remaining batch
            if batch and not dry_run:
                with transaction.atomic():
                    model_class.objects.bulk_update(batch, ['loan_number'])
                updated_count += len(batch)

            if dry_run:
                self.stdout.write(
                    self.style.WARNING(f"  [DRY RUN] Would update {updated_count} records in {model_name}")
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f"  ✓ Updated {updated_count} records in {model_name}")
                )
            
            total_updated += updated_count

        # Final summary
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(self.style.SUCCESS(f"SUMMARY"))
        self.stdout.write(f"{'='*60}")
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f"[DRY RUN] Would update {total_updated} total records")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"✓ Successfully updated {total_updated} total records")
            )
