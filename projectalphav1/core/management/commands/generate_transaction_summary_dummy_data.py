"""
WHAT: Management command to generate dummy LLTransactionSummary data
WHY: Test realized P&L functionality and populate "Realized" column in Performance Summary
HOW: Creates transaction summary records for existing AssetIdHub records with random realized values
WHERE: Run via `python manage.py generate_transaction_summary_dummy_data`
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import AssetIdHub, LLTransactionSummary
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Generate dummy LLTransactionSummary data for testing realized P&L'

    def add_arguments(self, parser):
        # WHAT: Optional argument to purge existing data before generating
        parser.add_argument(
            '--purge',
            action='store_true',
            help='Delete all existing LLTransactionSummary records before generating new ones',
        )
        parser.add_argument(
            '--count',
            type=int,
            default=50,
            help='Number of transaction summaries to create (default: 50)',
        )

    def handle(self, *args, **options):
        purge = options['purge']
        count = options['count']

        # WHAT: Purge existing data if requested
        if purge:
            existing_count = LLTransactionSummary.objects.count()
            LLTransactionSummary.objects.all().delete()
            self.stdout.write(f"Purging {existing_count} existing LLTransactionSummary records...")
            self.stdout.write(self.style.SUCCESS(f"✓ Deleted {existing_count} records\n"))

        # WHAT: Get asset hubs 1-148 (matching BlendedOutcomeModel range)
        # WHY: Ensure transaction summaries exist for all assets with blended outcome data
        target_hub_ids = list(range(1, 149))  # IDs 1 through 148
        available_hubs = AssetIdHub.objects.filter(id__in=target_hub_ids).order_by('id')

        if not available_hubs.exists():
            self.stdout.write(self.style.WARNING("No AssetIdHub records found for IDs 1-148"))
            return

        actual_count = available_hubs.count()
        self.stdout.write(f"Generating LLTransactionSummary data for asset_hub IDs 1-148 ({actual_count} assets)")

        created = 0
        updated = 0
        skipped = 0

        # WHAT: Generate transaction summary for each hub
        for hub in available_hubs:
            try:
                with transaction.atomic():
                    # WHAT: Generate realistic realized values (80-120% of typical underwritten values)
                    summary_data = self._generate_realized_data()
                    
                    # WHAT: Create or update transaction summary
                    summary, was_created = LLTransactionSummary.objects.update_or_create(
                        asset_hub=hub,
                        defaults=summary_data
                    )
                    
                    if was_created:
                        created += 1
                        self.stdout.write(f"  ✓ Created LLTransactionSummary for hub {hub.id}")
                    else:
                        updated += 1
                        self.stdout.write(f"  ✓ Updated LLTransactionSummary for hub {hub.id}")
                        
            except Exception as e:
                skipped += 1
                self.stdout.write(
                    self.style.ERROR(f"  ✗ Error processing hub {hub.id}: {str(e)}")
                )

        # WHAT: Summary output
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("Summary:")
        self.stdout.write(f"  Created: {created}")
        self.stdout.write(f"  Updated: {updated}")
        self.stdout.write(f"  Skipped: {skipped}")
        self.stdout.write(f"  Total processed: {created + updated + skipped}")

    def _generate_realized_data(self):
        """
        WHAT: Generate realistic realized transaction data
        WHY: Simulate actual income/expenses for testing
        HOW: Random values within realistic ranges, some fields null to simulate incomplete data
        
        Returns:
            dict: Field values for LLTransactionSummary
        """
        
        # WHAT: Helper to generate random decimal in range
        def rand_dec(min_val, max_val, decimals=2):
            return Decimal(str(round(random.uniform(min_val, max_val), decimals)))
        
        # WHAT: Helper to randomly return None (30% chance) or value
        def maybe_none(value):
            return None if random.random() < 0.3 else value
        
        # WHAT: Generate base purchase price for calculations
        purchase_price = rand_dec(50000, 500000)
        gross_proceeds = rand_dec(float(purchase_price) * 0.8, float(purchase_price) * 1.5)
        
        return {
            # ------------------------------
            # Purchase Cost
            # ------------------------------
            'purchase_price_realized': maybe_none(purchase_price),
            
            # ------------------------------
            # Acquisition Costs
            # ------------------------------
            'acq_due_diligence_realized': maybe_none(rand_dec(500, 2000)),
            'acq_legal_realized': maybe_none(rand_dec(1000, 3000)),
            'acq_title_realized': maybe_none(rand_dec(500, 1500)),
            'acq_other_realized': maybe_none(rand_dec(300, 1000)),
            
            # ------------------------------
            # Income
            # ------------------------------
            'income_principal_realized': maybe_none(rand_dec(0, 5000)),
            'income_interest_realized': maybe_none(rand_dec(0, 3000)),
            'income_rent_realized': maybe_none(rand_dec(0, 2000)),
            'income_cam_realized': maybe_none(rand_dec(0, 500)),
            'income_mod_down_payment_realized': maybe_none(rand_dec(0, 10000)),
            
            # ------------------------------
            # Operating Expenses
            # ------------------------------
            'expense_servicing_realized': maybe_none(rand_dec(100, 1000)),
            'expense_am_fees_realized': maybe_none(rand_dec(500, 5000)),
            'expense_property_tax_realized': maybe_none(rand_dec(200, 800)),
            'expense_property_insurance_realized': maybe_none(rand_dec(100, 300)),
            
            # ------------------------------
            # Legal/DIL Costs
            # ------------------------------
            'legal_foreclosure_realized': maybe_none(rand_dec(2000, 10000)),
            'legal_bankruptcy_realized': maybe_none(rand_dec(1500, 6000)),
            'legal_dil_realized': maybe_none(rand_dec(1000, 4000)),
            'legal_cash_for_keys_realized': maybe_none(rand_dec(500, 5000)),
            'legal_eviction_realized': maybe_none(rand_dec(800, 3000)),
            
            # ------------------------------
            # REO Expenses
            # ------------------------------
            'reo_hoa_realized': maybe_none(rand_dec(50, 300)),
            'reo_utilities_realized': maybe_none(rand_dec(100, 400)),
            'reo_trashout_realized': maybe_none(rand_dec(500, 2000)),
            'reo_renovation_realized': maybe_none(rand_dec(5000, 50000)),
            'reo_property_preservation_realized': maybe_none(rand_dec(500, 3000)),
            
            # ------------------------------
            # CRE Expenses
            # ------------------------------
            'cre_marketing_realized': maybe_none(rand_dec(200, 1000)),
            'cre_ga_pool_realized': maybe_none(rand_dec(100, 500)),
            'cre_maintenance_realized': maybe_none(rand_dec(300, 2000)),
            
            # ------------------------------
            # Fund Expenses
            # ------------------------------
            'fund_taxes_realized': maybe_none(rand_dec(100, 1000)),
            'fund_legal_realized': maybe_none(rand_dec(200, 2000)),
            'fund_consulting_realized': maybe_none(rand_dec(300, 1500)),
            'fund_audit_realized': maybe_none(rand_dec(500, 3000)),
            
            # ------------------------------
            # Proceeds & Closing
            # ------------------------------
            'proceeds_realized': maybe_none(gross_proceeds),
            'broker_closing_realized': maybe_none(rand_dec(2000, 15000)),
            'other_closing_realized': maybe_none(rand_dec(500, 3000)),
            'net_liquidation_proceeds_realized': maybe_none(gross_proceeds * Decimal('0.92')),
        }
