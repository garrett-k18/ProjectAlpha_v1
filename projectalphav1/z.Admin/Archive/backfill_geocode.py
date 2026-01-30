"""
Backfill geocoding for existing assets.

This command geocodes all assets that don't have geocode data yet
in their LlDataEnrichment records. It uses the Geocodio API to fetch lat/lng
coordinates for each asset's address.

Usage:
    python manage.py backfill_geocode [--limit N] [--dry-run]

Options:
    --limit N       Process only N assets (default: all)
    --dry-run       Show what would be geocoded without making API calls
    --chunk-size N  Number of addresses per batch (default: 1000)

Examples:
    # Dry run to see what would be geocoded
    python manage.py backfill_geocode --dry-run --limit 10
    
    # Geocode first 100 assets
    python manage.py backfill_geocode --limit 100
"""
from __future__ import annotations

import logging
from typing import Optional

from django.core.management.base import BaseCommand
from django.db.models import Q

from acq_module.models.model_acq_seller import SellerRawData
from core.services.serv_co_geocoding import batch_geocode_row_ids

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Backfill geocoding data for existing assets using Geocodio API"

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit the number of assets to process',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be geocoded without making API calls',
        )
        parser.add_argument(
            '--chunk-size',
            type=int,
            default=1000,
            help='Number of addresses to process per batch (default: 1000)',
        )

    def handle(self, *args, **options):
        limit: Optional[int] = options.get('limit')
        dry_run: bool = options.get('dry_run', False)
        chunk_size: int = options.get('chunk_size', 1000)

        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('GEOCODE BACKFILL'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('[DRY RUN] No API calls will be made'))
        
        # WHAT: Find assets that need geocoding
        # WHY: We want to geocode assets that don't have lat/lng data yet
        # HOW: Query SellerRawData with missing enrichment data
        
        assets_qs = SellerRawData.objects.filter(
            Q(asset_hub__enrichment__isnull=True)
            | Q(asset_hub__enrichment__geocode_lat__isnull=True)
            | Q(asset_hub__enrichment__geocode_lng__isnull=True)
        ).select_related('asset_hub')
        
        if limit:
            assets_qs = assets_qs[:limit]
        
        total_count = assets_qs.count()
        
        if total_count == 0:
            self.stdout.write(self.style.SUCCESS('[SUCCESS] No assets need geocoding'))
            return
        
        self.stdout.write(f'[INFO] Found {total_count} assets to geocode')
        self.stdout.write(f'[INFO] Chunk size: {chunk_size} addresses per batch')
        self.stdout.write('[INFO] Geocodio fields: none (lat/lng only)')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n[DRY RUN] Showing first 10 assets that would be geocoded:'))
            for i, seller in enumerate(assets_qs[:10], 1):
                address = f"{seller.city or ''}, {seller.state or ''} {seller.zip or ''}".strip()
                asset_id = seller.asset_hub_id if seller.asset_hub_id else 'N/A'
                self.stdout.write(f"  {i}. Asset {asset_id}: {address}")
            
            if total_count > 10:
                self.stdout.write(f"  ... and {total_count - 10} more")
            
            self.stdout.write(self.style.SUCCESS('\n[SUCCESS] Dry run complete'))
            return
        
        self.stdout.write(f'\n[INFO] Starting geocoding for {total_count} assets...')
        self.stdout.write(f'[INFO] Using Geocodio API key from environment')
        
        try:
            row_ids = list(assets_qs.values_list('pk', flat=True))
            result = batch_geocode_row_ids(row_ids, chunk_size=chunk_size, fields=None)
            
            requested_rows = result.get('requested_rows', 0)
            unique_addresses = result.get('unique_addresses', 0)
            updated_rows = result.get('updated_rows', 0)
            api_calls = result.get('api_calls', 0)
            skipped_count = result.get('skipped_count', 0)
            
            self.stdout.write(self.style.SUCCESS('\n' + '=' * 80))
            self.stdout.write(self.style.SUCCESS('GEOCODING COMPLETE'))
            self.stdout.write(self.style.SUCCESS('=' * 80))
            self.stdout.write(f'[STATS] Requested rows: {requested_rows}')
            self.stdout.write(f'[STATS] Skipped (already geocoded): {skipped_count}')
            self.stdout.write(f'[STATS] Unique addresses to geocode: {unique_addresses}')
            self.stdout.write(f'[STATS] Updated rows: {updated_rows}')
            self.stdout.write(f'[STATS] API calls made: {api_calls}')
            
            if skipped_count > 0:
                self.stdout.write(self.style.SUCCESS(f'\n[INFO] Saved {skipped_count} API calls by skipping already-geocoded records'))
            
            if updated_rows < requested_rows:
                self.stdout.write(self.style.WARNING(
                    f'\n[WARNING] {requested_rows - updated_rows} assets could not be geocoded. Check logs for details.'
                ))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n[ERROR] Geocoding failed: {str(e)}'))
            logger.exception('Geocode backfill failed')
            raise
