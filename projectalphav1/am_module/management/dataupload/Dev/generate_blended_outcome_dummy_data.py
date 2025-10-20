"""
Management command to generate dummy BlendedOutcomeModel data for testing.

WHAT: Creates BlendedOutcomeModel records with realistic dummy P&L data
WHY: Populate performance summary data for frontend testing without real data
HOW: Generates random values for all P&L fields for asset_hub IDs 1-148
WHERE: Run from manage.py directory

Usage:
  python manage.py generate_blended_outcome_dummy_data
  python manage.py generate_blended_outcome_dummy_data --start 1 --end 50
  python manage.py generate_blended_outcome_dummy_data --dry-run

Docs reviewed:
- Django management commands: https://docs.djangoproject.com/en/stable/howto/custom-management-commands/
- Decimal handling: https://docs.python.org/3/library/decimal.html
"""

import random
from decimal import Decimal
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models.asset_id_hub import AssetIdHub
from am_module.models.boarded_data import BlendedOutcomeModel


class Command(BaseCommand):
    """
    Generate dummy BlendedOutcomeModel data for testing Performance Summary frontend.
    
    Creates 1:1 BlendedOutcomeModel records for AssetIdHub IDs 1-148 with realistic
    random P&L values for all legal fees, property expenses, and other metrics.
    """
    
    help = "Generate dummy BlendedOutcomeModel data for asset_hub IDs 1-148"
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--start',
            type=int,
            default=1,
            help='Starting asset_hub_id (default: 1)'
        )
        parser.add_argument(
            '--end',
            type=int,
            default=148,
            help='Ending asset_hub_id (default: 148)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without writing to DB'
        )
        parser.add_argument(
            '--purge',
            action='store_true',
            help='Delete all existing BlendedOutcomeModel records before generating new ones'
        )
    
    def handle(self, *args, **options):
        start_id = options['start']
        end_id = options['end']
        dry_run = options['dry_run']
        purge = options['purge']
        
        if start_id > end_id:
            raise CommandError(f"Start ID ({start_id}) must be <= end ID ({end_id})")
        
        # Purge existing records if requested
        if purge and not dry_run:
            existing_count = BlendedOutcomeModel.objects.count()
            if existing_count > 0:
                self.stdout.write(self.style.WARNING(f"Purging {existing_count} existing BlendedOutcomeModel records..."))
                BlendedOutcomeModel.objects.all().delete()
                self.stdout.write(self.style.SUCCESS(f"✓ Deleted {existing_count} records"))
            else:
                self.stdout.write("No existing records to purge")
        elif purge and dry_run:
            existing_count = BlendedOutcomeModel.objects.count()
            self.stdout.write(self.style.WARNING(f"Would purge {existing_count} existing BlendedOutcomeModel records"))
        
        self.stdout.write(f"\nGenerating BlendedOutcomeModel data for asset_hub IDs {start_id}-{end_id}")
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN - No data will be written"))
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        # Process in transaction unless dry-run
        with transaction.atomic() if not dry_run else self._null_context():
            for hub_id in range(start_id, end_id + 1):
                try:
                    # Check if hub exists
                    try:
                        hub = AssetIdHub.objects.get(id=hub_id)
                    except AssetIdHub.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(f"  Skipped hub {hub_id}: AssetIdHub does not exist")
                        )
                        skipped_count += 1
                        continue
                    
                    if dry_run:
                        # Check if would create or update
                        exists = BlendedOutcomeModel.objects.filter(asset_hub_id=hub_id).exists()
                        if exists:
                            self.stdout.write(f"  Would update BlendedOutcomeModel for hub {hub_id}")
                            updated_count += 1
                        else:
                            self.stdout.write(f"  Would create BlendedOutcomeModel for hub {hub_id}")
                            created_count += 1
                        continue
                    
                    # Generate dummy data
                    dummy_data = self._generate_dummy_data()
                    
                    # Create or update BlendedOutcomeModel
                    outcome, was_created = BlendedOutcomeModel.objects.update_or_create(
                        asset_hub=hub,
                        defaults=dummy_data
                    )
                    
                    if was_created:
                        created_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f"  ✓ Created BlendedOutcomeModel for hub {hub_id}")
                        )
                    else:
                        updated_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f"  ✓ Updated BlendedOutcomeModel for hub {hub_id}")
                        )
                
                except Exception as e:
                    self.stderr.write(
                        self.style.ERROR(f"  ✗ Error processing hub {hub_id}: {e}")
                    )
                    skipped_count += 1
        
        # Summary
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS(f"Summary:"))
        self.stdout.write(f"  Created: {created_count}")
        self.stdout.write(f"  Updated: {updated_count}")
        self.stdout.write(f"  Skipped: {skipped_count}")
        self.stdout.write(f"  Total processed: {created_count + updated_count + skipped_count}")
        if dry_run:
            self.stdout.write(self.style.WARNING("\nDRY RUN - No changes were made to the database"))
    
    def _generate_dummy_data(self):
        """
        WHAT: Generate realistic dummy P&L data for ALL BlendedOutcomeModel fields
        WHY: Provide complete test data for Performance Summary frontend
        HOW: Random values within realistic ranges for distressed real estate
        
        Returns:
            dict: Field values for BlendedOutcomeModel (all fields)
        """
        from datetime import date, timedelta
        
        # Helper to generate random decimal in range
        def rand_dec(min_val, max_val, decimals=2):
            return Decimal(str(round(random.uniform(min_val, max_val), decimals)))
        
        # Generate base purchase price for calculations
        purchase_price = rand_dec(50000, 500000)
        gross_proceeds = rand_dec(float(purchase_price) * 0.8, float(purchase_price) * 1.5)
        
        # Generate purchase date (random date in past 1-3 years)
        days_ago = random.randint(365, 1095)  # 1-3 years ago
        purchase_date = date.today() - timedelta(days=days_ago)
        
        return {
            # ------------------------------
            # Purchase Information
            # ------------------------------
            'purchase_price': purchase_price,
            'purchase_date': purchase_date,
            
            # ------------------------------
            # Timeline Durations (months)
            # ------------------------------
            'servicing_transfer_duration': random.randint(1, 6),
            'performing_duration': random.randint(0, 24),
            'pre_mod_duration': random.randint(0, 12),
            'mod_duration': random.randint(0, 18),
            'pre_fc_duration': random.randint(0, 12),
            'fc_progress_duration': random.randint(3, 18),
            'fc_left_duration': random.randint(0, 6),
            'fc_duration_state_avg': random.randint(6, 24),
            'dil_duration': random.randint(2, 12),
            'bk_duration': random.randint(6, 36),
            'eviction_duration': random.randint(1, 6),
            'renovation_duration': random.randint(1, 6),
            'reo_marketing_duration': random.randint(1, 12),
            'local_market_ext_duration': random.randint(0, 6),
            'rural_ext_duration': random.randint(0, 12),
            
            # ------------------------------
            # Legal Fees
            # ------------------------------
            'fc_expenses': rand_dec(1000, 5000),
            'fc_legal_fees': rand_dec(2000, 8000),
            'other_fc_fees': rand_dec(500, 3000),
            'dil_fees': rand_dec(1000, 4000),
            'cfk_fees': rand_dec(500, 5000),
            'bk_legal_fees': rand_dec(1500, 6000),
            'eviction_fees': rand_dec(800, 3000),
            
            # ------------------------------
            # Property Expenses
            # ------------------------------
            'reconciled_rehab_cost': rand_dec(5000, 50000),
            'trashout_cost': rand_dec(500, 2000),
            'property_preservation_cost': rand_dec(500, 3000),
            'total_insurance': rand_dec(100, 300),
            'total_property_tax': rand_dec(200, 800),
            'total_hoa': rand_dec(50, 300),
            'total_utility': rand_dec(100, 400),
            'total_other': rand_dec(50, 200),
            
            # ------------------------------
            # Income Fields
            # ------------------------------
            'principal_collect': rand_dec(0, 5000),
            'interest_collect': rand_dec(0, 3000),
            'mod_down_payment': rand_dec(0, 10000),
            'rental_income': rand_dec(0, 2000),
            'cam_income': rand_dec(0, 500),
            'other_income': rand_dec(0, 1000),
            
            # ------------------------------
            # Purchase Price
            # ------------------------------
            'purchase_price': rand_dec(50000, 500000),
            
            # ------------------------------
            # Fund Expenses
            # ------------------------------
            'acq_costs': rand_dec(2000, 15000),
            'am_fees': rand_dec(1000, 10000),
            
            # ------------------------------
            # Closing Costs
            # ------------------------------
            'tax_title_transfer_cost': rand_dec(500, 3000),
            'broker_fees': rand_dec(2000, 15000),
            
            # ------------------------------
            # Servicing Costs
            # ------------------------------
            'servicing_board_fee': rand_dec(100, 500),
            'servicing_current': rand_dec(50, 200),
            'servicing_30d': rand_dec(75, 250),
            'servicing_60d': rand_dec(100, 300),
            'servicing_90d': rand_dec(125, 350),
            'servicing_120d': rand_dec(150, 400),
            'servicing_fc': rand_dec(200, 600),
            'servicing_bk': rand_dec(250, 700),
            'servicing_liq_fee': rand_dec(300, 1000),
            
            # ------------------------------
            # Exit / Proceeds
            # ------------------------------
            'expected_exit_date': date.today() + timedelta(days=random.randint(30, 730)),
            'expected_gross_proceeds': gross_proceeds,
            'expected_net_proceeds': gross_proceeds * Decimal('0.92'),  # Net = Gross - ~8% closing costs
            
            # ------------------------------
            # Performance Metrics
            # ------------------------------
            'expected_pl': rand_dec(-50000, 150000),
            'expected_cf': rand_dec(-10000, 50000),
            'expected_irr': rand_dec(0.05, 9.99, 4),
            'expected_moic': rand_dec(0.5, 9.99, 5),
            'expected_npv': rand_dec(-20000, 100000),
            'expected_pv': rand_dec(float(purchase_price) * 0.7, float(purchase_price) * 1.2),
            
            # ------------------------------
            # Outcome Weights
            # ------------------------------
            'outcome_perf': rand_dec(0, 30),
            'outcome_mod': rand_dec(0, 20),
            'outcome_fcsale': rand_dec(0, 25),
            'outcome_dil_asis': rand_dec(0, 15),
            'outcome_dil_arv': rand_dec(0, 15),
            'outcome_reo_asis': rand_dec(0, 20),
            'outcome_reo_arv': rand_dec(0, 30),
            
            # ------------------------------
            # Bid Percentages
            # ------------------------------
            'bid_pct_upb': rand_dec(60, 95),
            'bid_pct_td': rand_dec(50, 90),
            'bid_pct_sellerasis': rand_dec(65, 100),
            'bid_pct_pv': rand_dec(70, 105),
            
            # ------------------------------
            # Cash Flow Periods (P0-P30)
            # ------------------------------
            'cf_p0': rand_dec(float(-purchase_price) * 1.1, float(-purchase_price) * 0.9),
            'cf_p1': rand_dec(-5000, 10000),
            'cf_p2': rand_dec(-5000, 10000),
            'cf_p3': rand_dec(-5000, 10000),
            'cf_p4': rand_dec(-5000, 10000),
            'cf_p5': rand_dec(-5000, 10000),
            'cf_p6': rand_dec(-5000, 10000),
            'cf_p7': rand_dec(-5000, 10000),
            'cf_p8': rand_dec(-5000, 10000),
            'cf_p9': rand_dec(-5000, 10000),
            'cf_p10': rand_dec(-5000, 10000),
            'cf_p11': rand_dec(-5000, 10000),
            'cf_p12': rand_dec(-5000, 10000),
            'cf_p13': rand_dec(-5000, 10000),
            'cf_p14': rand_dec(-5000, 10000),
            'cf_p15': rand_dec(-5000, 10000),
            'cf_p16': rand_dec(-5000, 10000),
            'cf_p17': rand_dec(-5000, 10000),
            'cf_p18': rand_dec(-5000, 10000),
            'cf_p19': rand_dec(-5000, 10000),
            'cf_p20': rand_dec(-5000, 10000),
            'cf_p21': rand_dec(-5000, 10000),
            'cf_p22': rand_dec(-5000, 10000),
            'cf_p23': rand_dec(-5000, 10000),
            'cf_p24': rand_dec(-5000, 10000),
            'cf_p25': rand_dec(-5000, 10000),
            'cf_p26': rand_dec(-5000, 10000),
            'cf_p27': rand_dec(-5000, 10000),
            'cf_p28': rand_dec(-5000, 10000),
            'cf_p29': rand_dec(-5000, 10000),
            'cf_p30': rand_dec(float(gross_proceeds) * 0.5, float(gross_proceeds) * 1.2),
        }
    
    def _null_context(self):
        """
        WHAT: No-op context manager for dry-run mode
        WHY: Allow unified code path without opening real transaction
        HOW: Returns self with __enter__ and __exit__ methods
        """
        class NullContext:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
        return NullContext()
