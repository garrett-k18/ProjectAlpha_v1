from django.core.management.base import BaseCommand
from acq_module.models.model_acq_seller import AcqAsset

class Command(BaseCommand):
    help = 'Backfill acq_status for all AcqAsset records to KEEP'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        status = AcqAsset.AcquisitionStatus.KEEP
        dry_run = options['dry_run']
        # Validate status is valid
        valid_statuses = [choice[0] for choice in AcqAsset.AcquisitionStatus.choices]
        if status not in valid_statuses:
            self.stderr.write(f'Invalid status: {status}. Valid choices: {valid_statuses}')
            return

        if dry_run:
            count = AcqAsset.objects.all().count()
            self.stdout.write(f'DRY RUN: Would update {count} records to acq_status={status}')
        else:
            count = AcqAsset.objects.all().update(acq_status=status)
            self.stdout.write(f'Updated {count} records to acq_status={status}')
