"""
Management command to clear test data from the database.

This command respects the preservation list from TEST_DATA_CONFIG.md:
- KEEPS: Reference data (states, counties, MSAs, crosswalks)
- KEEPS: Task models (REOtask, FCTask, DILTask, etc.)
- KEEPS: Assumption models (HOA, PropertyType, SquareFootage, UnitBased)
- KEEPS: ValuationGradeReference, FCStatus
- DELETES: All transactional data (assets, trades, outcomes, etc.)

Usage:
    python manage.py clear_test_data --no-input
    python manage.py clear_test_data --verbose
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, connection
from django.contrib.contenttypes.models import ContentType

# Import all models
from core.models import (
    AssetIdHub, AssetDetails,
    DebtFacility, CoInvestor, InvestorContribution, InvestorDistribution,
    Entity, FundLegalEntity, FundMembership, EntityMembership,
    FirmCRM, MasterCRM, BrokerMSAAssignment,
    Servicer,
    LlDataEnrichment,
    Valuation,
    LLTransactionSummary, LLCashFlowSeries,
    ComparableProperty, SalesComparable, LeaseComparable,
    LeaseComparableUnitMix, LeaseComparableRentRoll,
    GeneralLedgerEntries, ChartOfAccounts,
)

from acq_module.models import (
    Seller, Trade, SellerRawData,
    LoanLevelAssumption, TradeLevelAssumption, NoteSaleAssumption,
)

from am_module.models import (
    AMMetrics, AMNote, AssetCRMContact,
    REOData, FCSale, DIL, ShortSale, Modification, NoteSale,
    REOScope, Offers, AuditLog,
)


class Command(BaseCommand):
    help = 'Clear test data from database (preserves reference data and task models per config)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-input',
            action='store_true',
            help='Skip confirmation prompt',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed deletion progress',
        )

    def handle(self, *args, **options):
        verbose = options['verbose']
        no_input = options['no_input']  # Django converts hyphens to underscores

        # Confirmation prompt
        if not no_input:
            self.stdout.write(
                self.style.WARNING(
                    '\n>> WARNING: This will delete ALL transactional data from the database.\n'
                    'The following data will be PRESERVED:\n'
                    '  - Reference data (states, counties, MSAs, ZIP crosswalks)\n'
                    '  - Task models (REOtask, FCTask, DILTask, etc.)\n'
                    '  - Assumption models (HOA, PropertyType, SquareFootage, etc.)\n'
                    '  - ValuationGradeReference, FCStatus, FCTimelines\n'
                    '\nThe following data will be DELETED:\n'
                    '  - All assets (AssetIdHub, SellerRawData, AssetDetails)\n'
                    '  - All trades and sellers\n'
                    '  - All outcomes (REO, FC, DIL, ShortSale, Modification, NoteSale)\n'
                    '  - All valuations and comparables\n'
                    '  - All financial data (GL entries, transaction summaries)\n'
                    '  - All CRM data (firms, contacts)\n'
                    '  - All capital structure data (entities, funds)\n'
                )
            )
            confirm = input('\nType "yes" to continue, or "no" to cancel: ')
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.ERROR('[CANCELLED] Operation cancelled.'))
                return

        self.stdout.write(self.style.SUCCESS('\n>> Starting data deletion...\n'))

        try:
            with transaction.atomic():
                # Track counts
                total_deleted = 0

                # LEVEL 6: Deepest dependencies (delete first)
                self.stdout.write('>> Deleting deepest dependencies...')
                
                # Audit logs
                count = AuditLog.objects.count()
                if count > 0:
                    AuditLog.objects.all().delete()
                    total_deleted += count
                    if verbose:
                        self.stdout.write(f'  [OK] Deleted {count} AuditLog records')

                # AM Notes
                count = AMNote.objects.count()
                if count > 0:
                    AMNote.objects.all().delete()
                    total_deleted += count
                    if verbose:
                        self.stdout.write(f'  [OK] Deleted {count} AMNote records')

                # Asset CRM Contacts
                count = AssetCRMContact.objects.count()
                if count > 0:
                    AssetCRMContact.objects.all().delete()
                    total_deleted += count
                    if verbose:
                        self.stdout.write(f'  [OK] Deleted {count} AssetCRMContact records')

                # REO Scopes
                count = REOScope.objects.count()
                if count > 0:
                    REOScope.objects.all().delete()
                    total_deleted += count
                    if verbose:
                        self.stdout.write(f'  [OK] Deleted {count} REOScope records')

                # Offers
                count = Offers.objects.count()
                if count > 0:
                    Offers.objects.all().delete()
                    total_deleted += count
                    if verbose:
                        self.stdout.write(f'  [OK] Deleted {count} Offers records')

                # NOTE: Task models (REOtask, FCTask, etc.) are PRESERVED per config

                # Cash flow series
                count = LLCashFlowSeries.objects.count()
                if count > 0:
                    LLCashFlowSeries.objects.all().delete()
                    total_deleted += count
                    if verbose:
                        self.stdout.write(f'  [OK] Deleted {count} LLCashFlowSeries records')

                # GL Entries (clear M2M first)
                count = GeneralLedgerEntries.objects.count()
                if count > 0:
                    for entry in GeneralLedgerEntries.objects.all():
                        entry.tags.clear()
                    GeneralLedgerEntries.objects.all().delete()
                    total_deleted += count
                    if verbose:
                        self.stdout.write(f'  [OK] Deleted {count} GeneralLedgerEntries records')

                # Investor transactions
                count = InvestorContribution.objects.count()
                if count > 0:
                    InvestorContribution.objects.all().delete()
                    total_deleted += count
                    if verbose:
                        self.stdout.write(f'  [OK] Deleted {count} InvestorContribution records')

                count = InvestorDistribution.objects.count()
                if count > 0:
                    InvestorDistribution.objects.all().delete()
                    total_deleted += count
                    if verbose:
                        self.stdout.write(f'  [OK] Deleted {count} InvestorDistribution records')

                # Broker MSA assignments
                count = BrokerMSAAssignment.objects.count()
                if count > 0:
                    BrokerMSAAssignment.objects.all().delete()
                    total_deleted += count
                    if verbose:
                        self.stdout.write(f'  [OK] Deleted {count} BrokerMSAAssignment records')

                # Entity memberships
                count = EntityMembership.objects.count()
                if count > 0:
                    EntityMembership.objects.all().delete()
                    total_deleted += count
                    if verbose:
                        self.stdout.write(f'  [OK] Deleted {count} EntityMembership records')

                count = FundMembership.objects.count()
                if count > 0:
                    FundMembership.objects.all().delete()
                    total_deleted += count
                    if verbose:
                        self.stdout.write(f'  [OK] Deleted {count} FundMembership records')

                # Comparable property details
                count = LeaseComparableRentRoll.objects.count()
                if count > 0:
                    LeaseComparableRentRoll.objects.all().delete()
                    total_deleted += count
                    if verbose:
                        self.stdout.write(f'  [OK] Deleted {count} LeaseComparableRentRoll records')

                count = LeaseComparableUnitMix.objects.count()
                if count > 0:
                    LeaseComparableUnitMix.objects.all().delete()
                    total_deleted += count
                    if verbose:
                        self.stdout.write(f'  [OK] Deleted {count} LeaseComparableUnitMix records')

                count = SalesComparable.objects.count()
                if count > 0:
                    SalesComparable.objects.all().delete()
                    total_deleted += count
                    if verbose:
                        self.stdout.write(f'  [OK] Deleted {count} SalesComparable records')

                count = LeaseComparable.objects.count()
                if count > 0:
                    LeaseComparable.objects.all().delete()
                    total_deleted += count
                    if verbose:
                        self.stdout.write(f'  [OK] Deleted {count} LeaseComparable records')

                # LEVEL 5: Outcome models
                self.stdout.write('>> Deleting outcome models...')
                
                count = REOData.objects.count()
                if count > 0:
                    REOData.objects.all().delete()
                    total_deleted += count
                    if verbose:
                        self.stdout.write(f'  [OK] Deleted {count} REOData records')

                count = FCSale.objects.count()
                if count > 0:
                    FCSale.objects.all().delete()
                    total_deleted += count
                    if verbose:
                        self.stdout.write(f'  [OK] Deleted {count} FCSale records')

                count = DIL.objects.count()
                if count > 0:
                    DIL.objects.all().delete()
                    total_deleted += count
                    if verbose:
                        self.stdout.write(f'  [OK] Deleted {count} DIL records')

                count = ShortSale.objects.count()
                if count > 0:
                    ShortSale.objects.all().delete()
                    total_deleted += count
                    if verbose:
                        self.stdout.write(f'  [OK] Deleted {count} ShortSale records')

                count = Modification.objects.count()
                if count > 0:
                    Modification.objects.all().delete()
                    total_deleted += count
                    if verbose:
                        self.stdout.write(f'  [OK] Deleted {count} Modification records')

                count = NoteSale.objects.count()
                if count > 0:
                    NoteSale.objects.all().delete()
                    total_deleted += count
                    if verbose:
                        self.stdout.write(f'  [OK] Deleted {count} NoteSale records')

                # LEVEL 4: Asset-linked data
                self.stdout.write('>> Deleting asset-linked data...')
                
                count = LLTransactionSummary.objects.count()
                if count > 0:
                    LLTransactionSummary.objects.all().delete()
                    total_deleted += count
                    if verbose:
                        self.stdout.write(f'  [OK] Deleted {count} LLTransactionSummary records')

                count = LlDataEnrichment.objects.count()
                if count > 0:
                    LlDataEnrichment.objects.all().delete()
                    total_deleted += count
                    if verbose:
                        self.stdout.write(f'  [OK] Deleted {count} LlDataEnrichment records')

                count = Valuation.objects.count()
                if count > 0:
                    Valuation.objects.all().delete()
                    total_deleted += count
                    if verbose:
                        self.stdout.write(f'  [OK] Deleted {count} Valuation records')

                count = ComparableProperty.objects.count()
                if count > 0:
                    ComparableProperty.objects.all().delete()
                    total_deleted += count
                    if verbose:
                        self.stdout.write(f'  [OK] Deleted {count} ComparableProperty records')

                count = AMMetrics.objects.count()
                if count > 0:
                    AMMetrics.objects.all().delete()
                    total_deleted += count
                    if verbose:
                        self.stdout.write(f'  [OK] Deleted {count} AMMetrics records')

                count = LoanLevelAssumption.objects.count()
                if count > 0:
                    LoanLevelAssumption.objects.all().delete()
                    total_deleted += count
                    if verbose:
                        self.stdout.write(f'  [OK] Deleted {count} LoanLevelAssumption records')

                # LEVEL 3: Asset core data
                self.stdout.write('>> Deleting asset core data...')
                
                count = AssetDetails.objects.count()
                if count > 0:
                    AssetDetails.objects.all().delete()
                    total_deleted += count
                    if verbose:
                        self.stdout.write(f'  [OK] Deleted {count} AssetDetails records')

                count = SellerRawData.objects.count()
                if count > 0:
                    SellerRawData.objects.all().delete()
                    total_deleted += count
                    if verbose:
                        self.stdout.write(f'  [OK] Deleted {count} SellerRawData records')

                # LEVEL 2: Trade and fund structures
                self.stdout.write('>> Deleting trade and fund structures...')
                
                count = TradeLevelAssumption.objects.count()
                if count > 0:
                    TradeLevelAssumption.objects.all().delete()
                    total_deleted += count
                    if verbose:
                        self.stdout.write(f'  [OK] Deleted {count} TradeLevelAssumption records')

                count = Trade.objects.count()
                if count > 0:
                    Trade.objects.all().delete()
                    total_deleted += count
                    if verbose:
                        self.stdout.write(f'  [OK] Deleted {count} Trade records')

                count = FundLegalEntity.objects.count()
                if count > 0:
                    FundLegalEntity.objects.all().delete()
                    total_deleted += count
                    if verbose:
                        self.stdout.write(f'  [OK] Deleted {count} FundLegalEntity records')

                count = CoInvestor.objects.count()
                if count > 0:
                    CoInvestor.objects.all().delete()
                    total_deleted += count
                    if verbose:
                        self.stdout.write(f'  [OK] Deleted {count} CoInvestor records')

                # LEVEL 1: Top-level entities
                self.stdout.write('>> Deleting top-level entities...')
                
                # AssetIdHub (central hub - delete after all spokes)
                count = AssetIdHub.objects.count()
                if count > 0:
                    AssetIdHub.objects.all().delete()
                    total_deleted += count
                    if verbose:
                        self.stdout.write(f'  [OK] Deleted {count} AssetIdHub records')

                count = Seller.objects.count()
                if count > 0:
                    Seller.objects.all().delete()
                    total_deleted += count
                    if verbose:
                        self.stdout.write(f'  [OK] Deleted {count} Seller records')

                count = Entity.objects.count()
                if count > 0:
                    Entity.objects.all().delete()
                    total_deleted += count
                    if verbose:
                        self.stdout.write(f'  [OK] Deleted {count} Entity records')

                # Clear M2M relationships for CRM before deleting
                for crm in MasterCRM.objects.all():
                    crm.states.clear()
                    crm.msas.clear()
                
                count = MasterCRM.objects.count()
                if count > 0:
                    MasterCRM.objects.all().delete()
                    total_deleted += count
                    if verbose:
                        self.stdout.write(f'  [OK] Deleted {count} MasterCRM records')

                for firm in FirmCRM.objects.all():
                    firm.states.clear()
                
                count = FirmCRM.objects.count()
                if count > 0:
                    FirmCRM.objects.all().delete()
                    total_deleted += count
                    if verbose:
                        self.stdout.write(f'  [OK] Deleted {count} FirmCRM records')

                # Delete servicers (config doesn't specify to keep)
                count = Servicer.objects.count()
                if count > 0:
                    Servicer.objects.all().delete()
                    total_deleted += count
                    if verbose:
                        self.stdout.write(f'  [OK] Deleted {count} Servicer records')

                # Delete debt facilities
                count = DebtFacility.objects.count()
                if count > 0:
                    DebtFacility.objects.all().delete()
                    total_deleted += count
                    if verbose:
                        self.stdout.write(f'  [OK] Deleted {count} DebtFacility records')

                # Delete note sale assumptions
                count = NoteSaleAssumption.objects.count()
                if count > 0:
                    NoteSaleAssumption.objects.all().delete()
                    total_deleted += count
                    if verbose:
                        self.stdout.write(f'  [OK] Deleted {count} NoteSaleAssumption records')

                # Reset sequences for PostgreSQL
                if connection.vendor == 'postgresql':
                    self.stdout.write('>> Resetting database sequences...')
                    with connection.cursor() as cursor:
                        # Reset sequences for models with auto-increment IDs
                        sequences = [
                            ('core_assetidhub', 'id'),
                            ('acq_seller', 'id'),
                            ('acq_trade', 'id'),
                            ('core_firmcrm', 'id'),
                            ('core_mastercrm', 'id'),
                            ('entity', 'id'),
                            ('fund_legal_entity', 'id'),
                            # Add more as needed
                        ]
                        for table, column in sequences:
                            try:
                                cursor.execute(
                                    f"SELECT setval(pg_get_serial_sequence('{table}', '{column}'), 1, false);"
                                )
                            except Exception as e:
                                if verbose:
                                    self.stdout.write(f'  [WARN] Could not reset sequence for {table}.{column}: {e}')

                self.stdout.write(
                    self.style.SUCCESS(
                        f'\n[OK] Successfully deleted {total_deleted} records.\n'
                        f'[OK] Reference data, task models, and assumptions have been preserved.\n'
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'\n[ERROR] Error during deletion: {str(e)}\n')
            )
            raise CommandError(f'Data deletion failed: {str(e)}')
