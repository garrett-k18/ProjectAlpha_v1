"""
WHAT: Management command to generate dummy LLCashFlowSeries data for time-series cash flow analysis
WHY: Test period-by-period cash flow functionality and populate cash flow tables
HOW: Creates 30 periods of cash flow data for assets 140-148 with realistic monthly values
WHERE: Run via `python manage.py generate_cashflow_series_dummy_data`
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import AssetIdHub, LLCashFlowSeries
from decimal import Decimal
import random
from datetime import date


class Command(BaseCommand):
    help = 'Generate dummy LLCashFlowSeries data for assets 140-148 (30 periods each)'

    def add_arguments(self, parser):
        # WHAT: Optional argument to purge existing data before generating
        parser.add_argument(
            '--purge',
            action='store_true',
            help='Delete all existing LLCashFlowSeries records before generating new ones',
        )
        parser.add_argument(
            '--periods',
            type=int,
            default=30,
            help='Number of periods to create per asset (default: 30)',
        )

    def handle(self, *args, **options):
        purge = options['purge']
        num_periods = options['periods']

        # WHAT: Purge existing data if requested
        if purge:
            existing_count = LLCashFlowSeries.objects.count()
            LLCashFlowSeries.objects.all().delete()
            self.stdout.write(f"Purging {existing_count} existing LLCashFlowSeries records...")
            self.stdout.write(self.style.SUCCESS(f"✓ Deleted {existing_count} records\n"))

        # WHAT: Get asset hubs 140-148
        # WHY: Limited set for meaningful testing without overwhelming data
        target_hub_ids = list(range(140, 149))  # IDs 140 through 148
        available_hubs = AssetIdHub.objects.filter(id__in=target_hub_ids).select_related('blended_outcome_model').order_by('id')

        if not available_hubs.exists():
            self.stdout.write(self.style.WARNING("No AssetIdHub records found for IDs 140-148"))
            return

        actual_count = available_hubs.count()
        self.stdout.write(f"Generating LLCashFlowSeries data for asset_hub IDs 140-148 ({actual_count} assets)")
        self.stdout.write(f"Creating {num_periods} periods per asset (Period 0 = acquisition, 1-{num_periods-1} = monthly)\n")

        total_created = 0
        total_updated = 0
        total_skipped = 0

        # WHAT: Generate cash flow series for each hub
        for hub in available_hubs:
            self.stdout.write(f"\nProcessing Asset Hub {hub.id}...")
            
            # WHAT: Check if hub has blended outcome model with purchase date
            if not hasattr(hub, 'blended_outcome_model') or not hub.blended_outcome_model.purchase_date:
                self.stdout.write(self.style.WARNING(f"  ⚠ Skipping hub {hub.id} - no purchase_date in BlendedOutcomeModel"))
                total_skipped += num_periods
                continue
            
            created = 0
            updated = 0
            
            # WHAT: Generate base values for this asset (used across all periods)
            base_values = self._generate_base_asset_values()
            
            # WHAT: Create periods 0 through num_periods-1
            for period_num in range(num_periods):
                try:
                    with transaction.atomic():
                        # WHAT: Generate period-specific data
                        period_data = self._generate_period_data(period_num, base_values)
                        
                        # WHAT: Create or update cash flow series record
                        # Note: period_date is auto-calculated in model's save() method
                        cash_flow, was_created = LLCashFlowSeries.objects.update_or_create(
                            asset_hub=hub,
                            period_number=period_num,
                            defaults=period_data
                        )
                        
                        if was_created:
                            created += 1
                        else:
                            updated += 1
                            
                except Exception as e:
                    total_skipped += 1
                    self.stdout.write(
                        self.style.ERROR(f"  ✗ Error creating period {period_num} for hub {hub.id}: {str(e)}")
                    )
            
            total_created += created
            total_updated += updated
            self.stdout.write(f"  ✓ Hub {hub.id}: Created {created}, Updated {updated} periods")

        # WHAT: Summary output
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("Summary:")
        self.stdout.write(f"  Assets processed: {actual_count}")
        self.stdout.write(f"  Periods per asset: {num_periods}")
        self.stdout.write(f"  Total records created: {total_created}")
        self.stdout.write(f"  Total records updated: {total_updated}")
        self.stdout.write(f"  Total skipped: {total_skipped}")
        self.stdout.write(f"  Total processed: {total_created + total_updated + total_skipped}")
        self.stdout.write(self.style.SUCCESS("\n✓ Cash flow series generation complete!"))

    def _generate_base_asset_values(self):
        """
        WHAT: Generate base values for an asset that remain consistent across periods
        WHY: Realistic cash flows have consistent monthly patterns
        HOW: Random values within realistic ranges
        
        Returns:
            dict: Base values for this asset
        """
        # WHAT: Helper to generate random decimal in range
        def rand_dec(min_val, max_val, decimals=2):
            return Decimal(str(round(random.uniform(min_val, max_val), decimals)))
        
        return {
            'purchase_price': rand_dec(50000, 500000),
            'monthly_interest': rand_dec(800, 3000),
            'monthly_principal': rand_dec(200, 1500),
            'monthly_rent': rand_dec(0, 2000),
            'monthly_servicing': rand_dec(100, 500),
            'monthly_am_fees': rand_dec(200, 1000),
            'property_tax_annual': rand_dec(1000, 5000),
            'insurance_annual': rand_dec(500, 2000),
        }

    def _generate_period_data(self, period_num, base_values):
        """
        WHAT: Generate cash flow data for a specific period
        WHY: Each period has different cash flows based on period number
        HOW: Period 0 = acquisition costs, Period 1+ = monthly operations, some periods have one-time events
        
        Args:
            period_num (int): Period number (0 = acquisition, 1+ = monthly)
            base_values (dict): Base values for this asset
            
        Returns:
            dict: Field values for LLCashFlowSeries
        """
        # WHAT: Helper to generate random decimal in range
        def rand_dec(min_val, max_val, decimals=2):
            return Decimal(str(round(random.uniform(min_val, max_val), decimals)))
        
        # WHAT: Helper to add random variance to base value (+/- 20%)
        def vary(base_value, variance=0.2):
            factor = 1 + random.uniform(-variance, variance)
            return base_value * Decimal(str(factor))
        
        data = {
            'period_date': date.today(),  # Will be overwritten by save() method
        }
        
        # WHAT: Period 0 = Acquisition (negative cash flows)
        if period_num == 0:
            data.update({
                'purchase_price': base_values['purchase_price'],
                'acq_due_diligence_expenses': rand_dec(500, 2000),
                'acq_legal_expenses': rand_dec(1000, 3000),
                'acq_title_expenses': rand_dec(500, 1500),
                'acq_other_expenses': rand_dec(300, 1000),
                # No income in period 0
            })
        
        # WHAT: Period 1-6 = Early months (lower income, some one-time costs)
        elif 1 <= period_num <= 6:
            data.update({
                # Income fields
                'income_interest': vary(base_values['monthly_interest'], 0.1),
                'income_principal': vary(base_values['monthly_principal'], 0.1),
                'income_rent': vary(base_values['monthly_rent'], 0.3) if random.random() > 0.3 else Decimal('0'),
                'income_cam': rand_dec(0, 200) if random.random() > 0.7 else Decimal('0'),
                'income_mod_down_payment': rand_dec(1000, 5000) if period_num == 3 and random.random() > 0.8 else Decimal('0'),
                
                # Operating expenses
                'servicing_expenses': vary(base_values['monthly_servicing'], 0.1),
                'am_fees_expenses': vary(base_values['monthly_am_fees'], 0.1),
                'property_tax_expenses': base_values['property_tax_annual'] / 12 if period_num % 3 == 0 else Decimal('0'),
                'property_insurance_expenses': base_values['insurance_annual'] / 12 if period_num == 1 else Decimal('0'),
                
                # Legal/DIL costs (higher in early periods)
                'legal_foreclosure_expenses': rand_dec(2000, 8000) if random.random() > 0.7 else Decimal('0'),
                'legal_bankruptcy_expenses': rand_dec(1500, 5000) if random.random() > 0.85 else Decimal('0'),
                'legal_dil_expenses': rand_dec(1000, 3000) if random.random() > 0.9 else Decimal('0'),
                'legal_cash_for_keys_expenses': rand_dec(500, 3000) if random.random() > 0.85 else Decimal('0'),
                'legal_eviction_expenses': rand_dec(800, 2500) if random.random() > 0.8 else Decimal('0'),
                
                # REO expenses
                'reo_hoa_expenses': rand_dec(50, 300) if random.random() > 0.5 else Decimal('0'),
                'reo_utilities_expenses': rand_dec(100, 400) if random.random() > 0.4 else Decimal('0'),
                'reo_trashout_expenses': rand_dec(500, 2000) if random.random() > 0.7 else Decimal('0'),
                'reo_renovation_expenses': rand_dec(5000, 30000) if period_num <= 3 and random.random() > 0.6 else Decimal('0'),
                'reo_property_preservation_expenses': rand_dec(200, 1000) if random.random() > 0.6 else Decimal('0'),
                
                # CRE expenses
                'cre_marketing_expenses': rand_dec(200, 800) if random.random() > 0.7 else Decimal('0'),
                'cre_ga_pool_expenses': rand_dec(100, 400) if random.random() > 0.6 else Decimal('0'),
                'cre_maintenance_expenses': rand_dec(300, 1500) if random.random() > 0.7 else Decimal('0'),
                
                # Fund expenses (allocated monthly)
                'fund_taxes_expenses': rand_dec(50, 200) if random.random() > 0.8 else Decimal('0'),
                'fund_legal_expenses': rand_dec(100, 500) if random.random() > 0.9 else Decimal('0'),
                'fund_consulting_expenses': rand_dec(150, 600) if random.random() > 0.85 else Decimal('0'),
                'fund_audit_expenses': rand_dec(200, 800) if period_num == 6 and random.random() > 0.7 else Decimal('0'),
            })
        
        # WHAT: Period 7-24 = Normal operations
        elif 7 <= period_num <= 24:
            data.update({
                # Income fields (more consistent)
                'income_interest': vary(base_values['monthly_interest'], 0.15),
                'income_principal': vary(base_values['monthly_principal'], 0.15),
                'income_rent': vary(base_values['monthly_rent'], 0.2),
                'income_cam': rand_dec(50, 300) if random.random() > 0.5 else Decimal('0'),
                'income_mod_down_payment': Decimal('0'),  # Rare in normal operations
                
                # Operating expenses (consistent monthly)
                'servicing_expenses': vary(base_values['monthly_servicing'], 0.1),
                'am_fees_expenses': vary(base_values['monthly_am_fees'], 0.1),
                'property_tax_expenses': base_values['property_tax_annual'] / 4 if period_num % 3 == 0 else Decimal('0'),
                'property_insurance_expenses': base_values['insurance_annual'] if period_num == 12 else Decimal('0'),
                
                # Legal/DIL costs (lower in normal operations)
                'legal_foreclosure_expenses': rand_dec(1000, 4000) if random.random() > 0.85 else Decimal('0'),
                'legal_bankruptcy_expenses': rand_dec(1000, 3000) if random.random() > 0.9 else Decimal('0'),
                'legal_dil_expenses': rand_dec(500, 2000) if random.random() > 0.95 else Decimal('0'),
                'legal_cash_for_keys_expenses': rand_dec(300, 2000) if random.random() > 0.9 else Decimal('0'),
                'legal_eviction_expenses': rand_dec(500, 1500) if random.random() > 0.85 else Decimal('0'),
                
                # REO expenses (ongoing maintenance)
                'reo_hoa_expenses': rand_dec(50, 300) if random.random() > 0.3 else Decimal('0'),
                'reo_utilities_expenses': rand_dec(100, 400) if random.random() > 0.3 else Decimal('0'),
                'reo_trashout_expenses': rand_dec(300, 1000) if random.random() > 0.9 else Decimal('0'),
                'reo_renovation_expenses': rand_dec(2000, 15000) if random.random() > 0.85 else Decimal('0'),
                'reo_property_preservation_expenses': rand_dec(200, 1000) if random.random() > 0.6 else Decimal('0'),
                
                # CRE expenses (regular operations)
                'cre_marketing_expenses': rand_dec(100, 500) if random.random() > 0.6 else Decimal('0'),
                'cre_ga_pool_expenses': rand_dec(100, 400) if random.random() > 0.5 else Decimal('0'),
                'cre_maintenance_expenses': rand_dec(500, 3000) if random.random() > 0.7 else Decimal('0'),
                
                # Fund expenses (allocated monthly)
                'fund_taxes_expenses': rand_dec(50, 200) if random.random() > 0.7 else Decimal('0'),
                'fund_legal_expenses': rand_dec(100, 500) if random.random() > 0.85 else Decimal('0'),
                'fund_consulting_expenses': rand_dec(150, 600) if random.random() > 0.8 else Decimal('0'),
                'fund_audit_expenses': rand_dec(300, 1000) if period_num == 12 and random.random() > 0.6 else Decimal('0'),
            })
        
        # WHAT: Period 25+ = Liquidation phase
        else:
            # WHAT: Liquidation in period 28
            if period_num == 28:
                gross_proceeds = base_values['purchase_price'] * Decimal(str(random.uniform(0.9, 1.3)))
                data.update({
                    'proceeds': gross_proceeds,
                    'broker_closing_expenses': rand_dec(2000, 10000),
                    'other_closing_expenses': rand_dec(500, 2000),
                    'net_liquidation_proceeds': gross_proceeds * Decimal('0.93'),
                    # Minimal operations during liquidation
                    'servicing_expenses': vary(base_values['monthly_servicing'], 0.2),
                    'am_fees_expenses': vary(base_values['monthly_am_fees'], 0.2),
                })
            else:
                # WHAT: Reduced operations in liquidation phase
                data.update({
                    'income_interest': vary(base_values['monthly_interest'], 0.3) if random.random() > 0.5 else Decimal('0'),
                    'income_principal': vary(base_values['monthly_principal'], 0.3) if random.random() > 0.5 else Decimal('0'),
                    'servicing_expenses': vary(base_values['monthly_servicing'], 0.2),
                    'am_fees_expenses': vary(base_values['monthly_am_fees'], 0.2),
                    'reo_utilities_expenses': rand_dec(50, 200) if random.random() > 0.5 else Decimal('0'),
                    'reo_property_preservation_expenses': rand_dec(100, 500) if random.random() > 0.6 else Decimal('0'),
                })
        
        return data
