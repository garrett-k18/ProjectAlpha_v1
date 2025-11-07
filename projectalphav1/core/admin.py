from django.contrib import admin
from django.db.models import Exists, OuterRef
from django.utils.html import format_html
from django.urls import reverse
from urllib.parse import quote
from core.models import (
    DebtFacility,
    JVEquityPartner,  # DEPRECATED - no admin registration
    CoInvestor,
    InvestorContribution,
    InvestorDistribution,
    Fund,
    MasterCRM,
    AssetIdHub,
    Servicer,
    StateReference,
    FCStatus,
    FCTimelines,
    CommercialUnits,
    HOAAssumption,
    PropertyTypeAssumption,
    SquareFootageAssumption,
    UnitBasedAssumption,
    LlDataEnrichment,
    Valuation,
    ValuationGradeReference,
    Photo,
    Document,
    LLTransactionSummary,
    LLCashFlowSeries,
    UnitMix,
    RentRoll,
    ComparableProperty,
    SalesComparable,
    LeaseComparable,
    LeaseComparableUnitMix,
    LeaseComparableRentRoll,
    HistoricalPropertyCashFlow,
    CalendarEvent,
)

# Cross-app children that reference AssetIdHub
from acq_module.models.model_acq_seller import SellerRawData
# DEPRECATED: SellerBoardedData - use SellerRawData instead
# from am_module.models.boarded_data import SellerBoardedData, BlendedOutcomeModel
from am_module.models.boarded_data import BlendedOutcomeModel
from am_module.models.servicers import ServicerLoanData

# Use standard Django admin site

@admin.register(DebtFacility)
class DebtFacilityAdmin(admin.ModelAdmin):
    list_display = (
        "facility_name",  # renamed from partner_name to facility_name to match model field
        "firm_name",
        "commitment_size",
        "rate_index",
        "sofr_rate",
        "spread_bps",
        "start_date",
        "end_date",
        "created_at",
    )
    list_filter = ("rate_index", "start_date", "end_date")
    search_fields = ("facility_name", "firm_name")
    list_per_page = 5

@admin.register(CoInvestor)
class CoInvestorAdmin(admin.ModelAdmin):
    """Admin configuration for CoInvestor model.
    
    What: Parent investor record with commitment and ownership details.
    Why: Central management of investor relationships.
    How: Shows computed totals from child contribution/distribution records.
    """
    list_display = (
        "get_investor_name",
        "get_firm_name",
        "commitment_amount",
        "ownership_percentage",
        "get_total_contributed",
        "get_total_distributed",
        "get_net_position",
        "is_active",
    )
    list_filter = ("is_active", "created_at")
    search_fields = ("crm_contact__contact_name", "crm_contact__firm", "notes")
    list_per_page = 5
    autocomplete_fields = ['crm_contact']
    readonly_fields = ('created_at', 'updated_at')
    
    def get_investor_name(self, obj):
        """Display investor contact name from CRM"""
        return obj.crm_contact.contact_name if obj.crm_contact else '—'
    get_investor_name.short_description = 'Investor Name'
    
    def get_firm_name(self, obj):
        """Display investor firm name from CRM"""
        return obj.crm_contact.firm if obj.crm_contact else '—'
    get_firm_name.short_description = 'Firm'
    
    def get_total_contributed(self, obj):
        """Display total contributions from child records"""
        return f"${obj.total_contributed():,.2f}"
    get_total_contributed.short_description = 'Total Contributed'
    
    def get_total_distributed(self, obj):
        """Display total distributions from child records"""
        return f"${obj.total_distributed():,.2f}"
    get_total_distributed.short_description = 'Total Distributed'
    
    def get_net_position(self, obj):
        """Display net position (contributions - distributions)"""
        return f"${obj.net_position():,.2f}"
    get_net_position.short_description = 'Net Position'


@admin.register(InvestorContribution)
class InvestorContributionAdmin(admin.ModelAdmin):
    """Admin configuration for InvestorContribution model.
    
    What: Individual contribution transaction records.
    Why: Track all capital contributions with full audit trail.
    How: Links to parent CoInvestor with date, amount, and payment details.
    """
    list_display = (
        "get_investor_name",
        "contribution_date",
        "amount",
        "payment_method",
        "reference_number",
        "created_at",
    )
    list_filter = ("contribution_date", "payment_method")
    search_fields = (
        "co_investor__crm_contact__contact_name",
        "co_investor__crm_contact__firm",
        "reference_number",
        "notes"
    )
    list_per_page = 5
    autocomplete_fields = ['co_investor']
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'contribution_date'
    
    def get_investor_name(self, obj):
        """Display investor name from parent CoInvestor"""
        return str(obj.co_investor)
    get_investor_name.short_description = 'Investor'


@admin.register(InvestorDistribution)
class InvestorDistributionAdmin(admin.ModelAdmin):
    """Admin configuration for InvestorDistribution model.
    
    What: Individual distribution transaction records.
    Why: Track all distributions with type categorization for tax reporting.
    How: Links to parent CoInvestor with date, amount, type, and payment details.
    """
    list_display = (
        "get_investor_name",
        "distribution_date",
        "amount",
        "distribution_type",
        "payment_method",
        "reference_number",
        "created_at",
    )
    list_filter = ("distribution_date", "distribution_type", "payment_method")
    search_fields = (
        "co_investor__crm_contact__contact_name",
        "co_investor__crm_contact__firm",
        "reference_number",
        "notes"
    )
    list_per_page = 5
    autocomplete_fields = ['co_investor']
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'distribution_date'
    
    def get_investor_name(self, obj):
        """Display investor name from parent CoInvestor"""
        return str(obj.co_investor)
    get_investor_name.short_description = 'Investor'


@admin.register(Fund)
class FundAdmin(admin.ModelAdmin):
    """Admin configuration for Fund model.
    
    What: Investment fund/vehicle management.
    Why: Track fund lifecycle, capital structure, and performance.
    How: Displays key metrics with computed capital called percentage.
    """
    list_display = (
        "fund_name",
        "fund_type",
        "fund_status",
        "inception_date",
        "target_fund_size",
        "total_commitments",
        "total_funded",
        "get_capital_called_pct",
        "maturity_date",
    )
    list_filter = ("fund_status", "fund_type", "inception_date")
    search_fields = ("fund_name", "legal_entity_name", "investment_strategy", "notes")
    list_per_page = 5
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'inception_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('fund_name', 'fund_type', 'fund_status', 'legal_entity_name', 'tax_id')
        }),
        ('Capital Structure', {
            'fields': ('target_fund_size', 'total_commitments', 'total_funded')
        }),
        ('LP/GP Ownership Split', {
            'fields': ('lp_percentage', 'gp_percentage', 'lp_contribution_paydown', 'gp_contribution_paydown')
        }),
        ('Fund Lifecycle', {
            'fields': (
                'inception_date', 'first_close_date', 'final_close_date',
                'investment_period_end', 'fund_term_years', 'maturity_date'
            )
        }),
        ('Fee Structure', {
            'fields': (
                'management_fee_pct', 'acquisition_fee_pct', 'disposition_fee_pct',
                'am_fees', 'acq_fees'
            )
        }),
        ('Waterfall Structure', {
            'fields': ('preferred_return_pct', 'lp_promote', 'gp_promote_pct', 'gp_catchup_pct')
        }),
        ('Investment Strategy', {
            'fields': ('investment_strategy', 'target_geography')
        }),
        ('Additional Information', {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
    )
    
    def get_capital_called_pct(self, obj):
        """Display capital called as percentage"""
        return f"{obj.capital_called_pct():.1f}%"
    get_capital_called_pct.short_description = 'Capital Called %'

@admin.register(MasterCRM)
class MasterCRMAdmin(admin.ModelAdmin):
    """Admin configuration for unified Master CRM (Brokercrm) model."""
    list_display = (
        'contact_name', 'firm', 'email', 'states_list', 'city', 'tag',
        'alt_contact_name', 'nda_flag', 'nda_signed', 'created_at'
    )
    list_filter = (
        'states', 'tag', 'nda_flag'
    )
    search_fields = (
        'contact_name', 'email', 'firm', 'city',
        'alt_contact_name', 'alt_contact_email'
    )
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 5
    # No fieldsets: show all fields by default

    def states_list(self, obj):
        return ", ".join(sorted([s.state_code for s in obj.states.all()])) or '—'
    states_list.short_description = 'States'





@admin.register(Servicer)
class ServicerAdmin(admin.ModelAdmin):
    """Admin configuration for Servicer model."""
    list_display = (
        'servicer_name', 'contact_name', 'contact_email', 'contact_phone',
        'board_fee', 'current_fee', 'fc_fee', 'bk_fee', 'mod_fee', 'dil_fee',
    )
    search_fields = ('servicer_name', 'contact_name', 'contact_email')
    list_filter = ()
    list_per_page = 5




@admin.register(ValuationGradeReference)
class ValuationGradeReferenceAdmin(admin.ModelAdmin):
    """Admin for ValuationGradeReference model.
    
    WHAT: Manage valuation grade reference data (A+, A, B, C, D, F)
    WHY: Allow creating/editing grade definitions used in Valuation FK
    HOW: Simple list/edit interface for reference data
    """
    list_display = (
        'code', 'label', 'sort_order', 'description', 'created_at', 'updated_at'
    )
    list_filter = ('code',)
    search_fields = ('code', 'label', 'description')
    ordering = ('sort_order', 'code')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 10
    
    fieldsets = (
        ('Grade Information', {
            'fields': ('code', 'label', 'sort_order', 'description')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Valuation)
class ValuationAdmin(admin.ModelAdmin):
    """Admin for the unified Valuation model."""
    list_display = (
        'id', 'asset_hub', 'source', 'grade', 'asis_value', 'arv_value', 'value_date', 'created_at'
    )
    list_filter = (
        'source', 'grade', 'value_date'
    )
    search_fields = (
        'asset_hub__id', 'notes'
    )
    autocomplete_fields = ['grade', 'broker_contact']
    # No fieldsets: show all fields by default
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 5


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    """Admin for the Photo model."""
    list_display = (
        'id', 'asset_hub', 'valuation', 'source_tag', 'caption', 'created_at'
    )
    list_filter = (
        'source_tag',
    )
    search_fields = (
        'asset_hub__id', 'caption'
    )
    list_per_page = 5


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Admin for the Document model."""
    list_display = (
        'id', 'asset_hub', 'valuation', 'original_name', 'uploaded_at'
    )
    search_fields = (
        'asset_hub__id', 'original_name'
    )
    list_per_page = 5


@admin.register(StateReference)
class StateReferenceAdmin(admin.ModelAdmin):
    """Admin configuration for StateReference model."""
    list_display = (
        'state_code', 'state_name', 'judicialvsnonjudicial', 'fc_state_months'
    )
    search_fields = ('state_code', 'state_name')
    list_filter = ('judicialvsnonjudicial',)
    list_per_page = 5


@admin.register(FCStatus)
class FCStatusAdmin(admin.ModelAdmin):
    """Admin configuration for FCStatus model.
    
    What this does:
    - Manages foreclosure status records with categorical choices
    - Displays status, order, and associated metadata in list view
    - Allows filtering and searching by status category
    """
    list_display = (
        'id', 'status', 'order', 'notes', 'created_at', 'updated_at'
    )
    list_filter = ('status',)
    search_fields = ('notes',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('order', 'status')
    list_per_page = 5
    
    # No fieldsets: show all fields by default


@admin.register(FCTimelines)
class FCTimelinesAdmin(admin.ModelAdmin):
    """Admin configuration for FCTimelines model.
    
    What this does:
    - Manages state-specific foreclosure timeline data
    - Links states to foreclosure statuses with duration and cost metrics
    - Enforces unique state/status combinations
    """
    list_display = (
        'state', 'fc_status', 'duration_days', 'cost_avg', 'updated_at'
    )
    list_filter = ('state', 'fc_status__status')
    search_fields = ('state__state_code', 'state__state_name', 'notes')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ['state', 'fc_status']
    list_per_page = 5
    
    # No fieldsets: show all fields by default


@admin.register(CommercialUnits)
class CommercialUnitsAdmin(admin.ModelAdmin):
    """Admin configuration for CommercialUnits model.
    
    What this does:
    - Manages commercial unit scaling factors
    - Displays unit counts and their associated cost/duration multipliers
    - Used for adjusting assumptions based on property unit count
    """
    list_display = (
        'units', 'fc_cost_scale', 'rehab_cost_scale', 'rehab_duration_scale',
        'created_at', 'updated_at'
    )
    search_fields = ('units',)
    ordering = ('units',)
    readonly_fields = ('created_at', 'updated_at')
    
    # No fieldsets: show all fields by default
    list_per_page = 5


@admin.register(HOAAssumption)
class HOAAssumptionAdmin(admin.ModelAdmin):
    """Admin configuration for HOAAssumption model.
    
    What this does:
    - Manages HOA fee assumptions by property type
    - Displays property types and their associated monthly HOA fees
    - Used for estimating ongoing carrying costs in financial calculations
    """
    list_display = (
        'property_type', 'monthly_hoa_fee', 'notes', 'created_at', 'updated_at'
    )
    list_filter = ('property_type',)
    search_fields = ('property_type', 'notes')
    ordering = ('property_type',)
    readonly_fields = ('created_at', 'updated_at')
    
    # No fieldsets: show all fields by default
    list_per_page = 5


@admin.register(LlDataEnrichment)
class LlDataEnrichmentAdmin(admin.ModelAdmin):
    """Admin for loan-level enrichment records."""
    list_display = (
        'seller_raw_data', 'geocode_lat', 'geocode_lng', 'geocoded_at',
    )
    search_fields = (
        'seller_raw_data__seller__name',
        'seller_raw_data__trade__trade_name',
        'geocode_full_address', 'geocode_used_address', 'geocode_display_address',
    )
    list_filter = (
        'seller_raw_data__seller', 'seller_raw_data__trade',
    )
    list_per_page = 5


@admin.register(PropertyTypeAssumption)
class PropertyTypeAssumptionAdmin(admin.ModelAdmin):
    """Admin for property type-based utility and property management assumptions."""
    list_display = (
        'property_type', 'total_monthly_utilities', 'total_monthly_property_management', 
        'total_one_time_costs', 'is_active', 'updated_at'
    )
    list_filter = ('property_type', 'is_active')
    search_fields = ('property_type', 'notes')
    ordering = ('property_type',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('property_type', 'is_active', 'notes')
        }),
        ('Monthly Utility Costs', {
            'fields': (
                'utility_electric_monthly', 'utility_gas_monthly', 'utility_water_monthly',
                'utility_sewer_monthly', 'utility_trash_monthly', 'utility_other_monthly'
            )
        }),
        ('Monthly Property Management Costs', {
            'fields': (
                'property_management_monthly', 'repairs_maintenance_monthly', 'marketing_monthly',
                'security_cost_monthly', 'landscaping_monthly', 'pool_maintenance_monthly'
            )
        }),
        ('One-Time Costs', {
            'fields': ('trashout_cost', 'renovation_cost')
        }),
    )
    
    def total_monthly_utilities(self, obj):
        """Display total monthly utility costs."""
        return f"${obj.total_monthly_utilities():,.2f}"
    total_monthly_utilities.short_description = "Total Monthly Utilities"
    
    def total_monthly_property_management(self, obj):
        """Display total monthly property management costs."""
        return f"${obj.total_monthly_property_management():,.2f}"
    total_monthly_property_management.short_description = "Total Monthly Prop Mgmt"
    
    def total_one_time_costs(self, obj):
        """Display total one-time costs."""
        return f"${obj.total_one_time_costs():,.2f}"
    total_one_time_costs.short_description = "Total One-Time Costs"


@admin.register(SquareFootageAssumption)
class SquareFootageAssumptionAdmin(admin.ModelAdmin):
    """Admin for square footage-based utility and property management assumptions."""
    list_display = (
        'property_category', 'description', 'is_active', 'updated_at'
    )
    list_filter = ('property_category', 'is_active')
    search_fields = ('description', 'notes')
    ordering = ('property_category', 'description')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('property_category', 'description', 'is_active', 'notes')
        }),
        ('Per Square Foot Monthly Utility Costs', {
            'fields': (
                'utility_electric_per_sqft', 'utility_gas_per_sqft', 'utility_water_per_sqft',
                'utility_sewer_per_sqft', 'utility_trash_per_sqft', 'utility_other_per_sqft'
            )
        }),
        ('Per Square Foot Monthly Property Management Costs', {
            'fields': (
                'property_management_per_sqft', 'repairs_maintenance_per_sqft', 'marketing_per_sqft',
                'security_cost_per_sqft', 'landscaping_per_sqft', 'pool_maintenance_per_sqft'
            )
        }),
        ('Per Square Foot One-Time Costs', {
            'fields': ('trashout_per_sqft', 'renovation_per_sqft')
        }),
    )


@admin.register(UnitBasedAssumption)
class UnitBasedAssumptionAdmin(admin.ModelAdmin):
    """Admin for unit-based utility and property management assumptions."""
    list_display = (
        'unit_range', 'description', 'is_active', 'updated_at'
    )
    list_filter = ('is_active',)
    search_fields = ('description', 'notes')
    ordering = ('units_min',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('units_min', 'units_max', 'description', 'is_active', 'notes')
        }),
        ('Per Unit Monthly Utility Costs', {
            'fields': (
                'utility_electric_per_unit', 'utility_gas_per_unit', 'utility_water_per_unit',
                'utility_sewer_per_unit', 'utility_trash_per_unit', 'utility_other_per_unit'
            )
        }),
        ('Per Unit Monthly Property Management Costs', {
            'fields': (
                'property_management_per_unit', 'repairs_maintenance_per_unit', 'marketing_per_unit',
                'security_cost_per_unit', 'landscaping_per_unit', 'pool_maintenance_per_unit'
            )
        }),
        ('Per Unit One-Time Costs', {
            'fields': ('trashout_per_unit', 'renovation_per_unit')
        }),
    )
    
    def unit_range(self, obj):
        """Display unit count range."""
        max_display = f"{obj.units_max}" if obj.units_max else "∞"
        return f"{obj.units_min} - {max_display} units"
    unit_range.short_description = "Unit Count Range"


@admin.register(UnitMix)
class UnitMixAdmin(admin.ModelAdmin):
    """
    Admin configuration for UnitMix model.
    
    What: Manages unit mix records for commercial/multi-family properties.
    Why: Allow viewing and editing of unit type, count, sqft, and rent data.
    How: Display key metrics including calculated price_sqft field.
    """
    list_display = (
        'id', 'unit_type', 'unit_count', 'unit_avg_sqft', 'unit_avg_rent',
        'price_sqft', 'total_sqft_display', 'total_rent_display', 'created_at'
    )
    list_filter = ('unit_type',)
    search_fields = ('unit_type',)
    readonly_fields = ('price_sqft', 'created_at', 'updated_at')
    ordering = ('unit_type',)
    
    # No fieldsets: show all fields by default
    list_per_page = 5
    
    def total_sqft_display(self, obj):
        """Display total square footage for all units of this type."""
        return f"{obj.get_total_sqft():,} sqft"
    total_sqft_display.short_description = 'Total SqFt'
    
    def total_rent_display(self, obj):
        """Display total monthly rent for all units of this type."""
        return f"${obj.get_total_monthly_rent():,.2f}"
    total_rent_display.short_description = 'Total Monthly Rent'


@admin.register(RentRoll)
class RentRollAdmin(admin.ModelAdmin):
    """
    Admin configuration for RentRoll model.

    What: Manage per-tenant/unit rent roll records.
    Why: Allow full visibility and editing of rent roll details.
    How: Keep default form fields (no fieldsets/fields), expose helpful list columns.
    """
    list_display = (
        'id', 'asset_hub_id', 'tenant_name', 'unit_name', 'sq_feet',
        'rent', 'cam_month', 'lease_start_date', 'lease_end_date',
        'lease_term_months', 'lease_type', 'rent_increase_pct'
    )
    search_fields = ('tenant_name', 'unit_name')
    list_filter = ('lease_type',)
    ordering = ('asset_hub_id', 'tenant_name')
    # No fieldsets/fields/exclude: show all fields by default
    list_per_page = 5


@admin.register(ComparableProperty)
class ComparablePropertyAdmin(admin.ModelAdmin):
    """
    Admin configuration for ComparableProperty model.

    What: Parent model storing shared property characteristics for sales/lease comps.
    Why: Allow full visibility and editing of comparable property base data.
    How: Default form (all fields visible); list key property info (rating is on child models).
    """
    list_display = (
        'id', 'asset_hub', 'as_of_date', 'street_address', 'city', 'state',
        'property_type', 'beds', 'baths', 'units', 'livable_square_ft_building',
        'created_at'
    )
    search_fields = ('street_address', 'city', 'zip_code')
    list_filter = ('state', 'property_type', 'as_of_date')
    ordering = ('-as_of_date', 'street_address')
    readonly_fields = ('created_at', 'updated_at')
    # No fieldsets/fields/exclude: show all fields by default
    list_per_page = 5


@admin.register(SalesComparable)
class SalesComparableAdmin(admin.ModelAdmin):
    """
    Admin configuration for SalesComparable model.

    What: Sales-specific data extending ComparableProperty.
    Why: Allow editing of sale prices, dates, and listing info.
    How: Default form (all fields visible); list key sales metrics and comp rating.
    """
    list_display = (
        'id', 'comparable_property', 'last_sales_price', 'last_sales_date',
        'current_listed_price', 'current_listed_date', 'comp_rating', 'created_at'
    )
    search_fields = ('comparable_property__street_address', 'comparable_property__city')
    list_filter = ('last_sales_date', 'current_listed_date', 'comp_rating')
    ordering = ('-last_sales_date',)
    readonly_fields = ('created_at', 'updated_at')
    # No fieldsets/fields/exclude: show all fields by default
    list_per_page = 5


@admin.register(LeaseComparable)
class LeaseComparableAdmin(admin.ModelAdmin):
    """
    Admin configuration for LeaseComparable model.

    What: Lease-specific data extending ComparableProperty (property-level/SFR leases).
    Why: Allow editing of rent, lease terms, CAM, and property name.
    How: Default form (all fields visible); list key lease metrics and comp rating.
    """
    list_display = (
        'id', 'comparable_property', 'monthly_rent', 'lease_start_date',
        'lease_end_date', 'lease_term_months', 'lease_type', 'cam_monthly', 'comp_rating', 'created_at'
    )
    search_fields = ('comparable_property__street_address', 'comparable_property__city')
    list_filter = ('lease_type', 'lease_start_date', 'comp_rating')
    ordering = ('-lease_start_date',)
    readonly_fields = ('created_at', 'updated_at')
    # No fieldsets/fields/exclude: show all fields by default
    list_per_page = 5


@admin.register(LeaseComparableUnitMix)
class LeaseComparableUnitMixAdmin(admin.ModelAdmin):
    """
    Admin configuration for LeaseComparableUnitMix model.

    What: Aggregated unit mix data for lease comps (more common scenario).
    Why: Allow editing of unit type summaries (e.g., "20 1BR @ $1200/mo avg").
    How: Default form (all fields visible); list key metrics with auto-calculated price_sqft.
    """
    list_display = (
        'id', 'comparable_property', 'unit_type', 'unit_count', 'unit_avg_sqft',
        'unit_avg_rent', 'price_sqft', 'created_at'
    )
    search_fields = (
        'comparable_property__street_address',
        'comparable_property__city',
        'unit_type'
    )
    list_filter = ('unit_type',)
    ordering = ['comparable_property', 'unit_type']
    readonly_fields = ('price_sqft', 'created_at', 'updated_at')
    # No fieldsets/fields/exclude: show all fields by default
    list_per_page = 5


@admin.register(LeaseComparableRentRoll)
class LeaseComparableRentRollAdmin(admin.ModelAdmin):
    """
    Admin configuration for LeaseComparableRentRoll model.

    What: Unit-level rent roll data for lease comps (rare scenario).
    Why: Allow editing of per-unit rent, lease terms, and occupancy for multi-family comps.
    How: Default form (all fields visible); list key unit metrics.
    """
    list_display = (
        'id', 'comparable_property', 'unit_number', 'beds', 'baths', 'unit_sqft',
        'monthly_rent', 'lease_start_date', 'lease_end_date', 'is_occupied', 'created_at'
    )
    search_fields = (
        'comparable_property__street_address', 
        'comparable_property__city', 
        'unit_number',
        'tenant_name'
    )
    list_filter = ('is_occupied', 'lease_type', 'lease_start_date', 'beds')
    ordering = ['comparable_property', 'unit_number']
    readonly_fields = ('created_at', 'updated_at')
    # No fieldsets/fields/exclude: show all fields by default
    list_per_page = 5


@admin.register(HistoricalPropertyCashFlow)
class HistoricalPropertyCashFlowAdmin(admin.ModelAdmin):
    """
    Admin configuration for HistoricalPropertyCashFlow model.

    What: Historical property-level cash flows by year for owned/managed assets.
    Why: Allow editing of annual income and expense data for NOI analysis.
    How: Default form (all fields visible); list key metrics by asset and year.
    """
    list_display = (
        'id', 'asset_hub', 'year', 'gross_potential_rent_revenue', 'vacancy_loss',
        'property_management', 'property_taxes', 'created_at'
    )
    search_fields = ('asset_hub__id', 'year')
    list_filter = ('year',)
    ordering = ['asset_hub', '-year']
    readonly_fields = ('created_at', 'updated_at')
    # No fieldsets/fields/exclude: show all fields by default
    list_per_page = 5


@admin.register(LLTransactionSummary)
class LLTransactionSummaryAdmin(admin.ModelAdmin):
    """
    WHAT: Admin for LLTransactionSummary - realized P&L tracking
    WHY: Allow manual entry/editing of realized transaction data
    HOW: Organized fieldsets matching Performance Summary structure
    """
    list_display = (
        'asset_hub', 'last_updated', 'has_income', 'has_expenses', 'has_proceeds'
    )
    search_fields = ('asset_hub__id', 'asset_hub__servicer_id')
    readonly_fields = ('last_updated', 'created_at')
    list_per_page = 5
    
    # No fieldsets: show all fields by default
    
    def has_income(self, obj):
        """Check if any income fields have data"""
        return any([
            obj.income_principal_realized,
            obj.income_interest_realized,
            obj.income_rent_realized,
            obj.income_cam_realized,
            obj.income_mod_down_payment_realized,
        ])
    has_income.boolean = True
    has_income.short_description = 'Income?'
    
    def has_expenses(self, obj):
        """Check if any expense fields have data"""
        return any([
            obj.expense_servicing_realized,
            obj.expense_am_fees_realized,
            obj.legal_foreclosure_realized,
            obj.reo_hoa_realized,
        ])
    has_expenses.boolean = True
    has_expenses.short_description = 'Expenses?'
    
    def has_proceeds(self, obj):
        """Check if proceeds data exists"""
        return obj.proceeds_realized is not None
    has_proceeds.boolean = True
    has_proceeds.short_description = 'Proceeds?'


@admin.register(LLCashFlowSeries)
class LLCashFlowSeriesAdmin(admin.ModelAdmin):
    """
    WHAT: Admin for LLCashFlowSeries - period-by-period cash flow time series
    WHY: Allow viewing/editing of monthly cash flow data for analytics
    HOW: Organized by period with collapsible fieldsets for each category
    """
    list_display = (
        'asset_hub', 'period_number', 'period_date', 'net_cash_flow',
        'total_income', 'total_expenses', 'has_liquidation'
    )
    list_filter = ('period_number',)
    search_fields = ('asset_hub__id', 'asset_hub__servicer_id')
    readonly_fields = ('period_date', 'total_income', 'total_expenses', 'net_cash_flow', 'purchase_date')
    list_per_page = 5
    ordering = ('asset_hub', 'period_number')
    
    # No fieldsets: show all fields by default
    
    def has_liquidation(self, obj):
        """Check if this period has liquidation proceeds"""
        return obj.proceeds > 0 or obj.net_liquidation_proceeds > 0
    has_liquidation.boolean = True
    has_liquidation.short_description = 'Liquidation?'


# Module-level admin action so it reliably appears in the actions dropdown
@admin.action(description="Delete hub and all children")
def delete_hub_and_children(modeladmin, request, queryset):
    """For each selected hub, delete all child rows then the hub itself.

    Deletion order (to satisfy FK constraints):
    1) Photo, Document
    2) Valuation
    3) SellerRawData (acq)
    4) BlendedOutcomeModel, ServicerLoanData (AM)
    5) Hub
    """
    deleted_hubs = 0
    for hub in queryset:
        # Core attachments first (may reference valuation)
        Photo.objects.filter(asset_hub=hub).delete()
        Document.objects.filter(asset_hub=hub).delete()

        # Valuations (core)
        Valuation.objects.filter(asset_hub=hub).delete()

        # Acquisitions raw
        SellerRawData.objects.filter(asset_hub=hub).delete()

        # AM side
        BlendedOutcomeModel.objects.filter(asset_hub=hub).delete()
        ServicerLoanData.objects.filter(asset_hub=hub).delete()
        # SellerBoardedData.objects.filter(asset_hub=hub).delete()  # DEPRECATED - no longer used

        # Finally, delete the hub itself
        AssetIdHub.objects.filter(pk=hub.pk).delete()
        deleted_hubs += 1

    modeladmin.message_user(request, f"Deleted {deleted_hubs} hub(s) and all children.")
    
# Also register globally to ensure the action appears even if ModelAdmin.actions is overridden by theme/config
admin.site.add_action(delete_hub_and_children, name='delete_hub_and_children')


@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    """
    Admin configuration for CalendarEvent model.
    
    Displays user-created calendar events with filtering and search capabilities.
    """
    list_display = (
        'id',
        'title',
        'date',
        'time',
        'category',
        'seller',
        'trade',
        'asset_hub',
        'is_reminder',
        'created_by',
        'created_at',
    )
    
    list_filter = (
        'category',
        'is_reminder',
        'date',
        'created_at',
    )
    
    search_fields = (
        'title',
        'description',
        'seller__seller_name',
        'trade__trade_name',
    )
    
    readonly_fields = ('created_by', 'created_at', 'updated_at')
    
    date_hierarchy = 'date'
    
    list_per_page = 5
    
    fieldsets = (
        ('Event Details', {
            'fields': ('title', 'date', 'time', 'description', 'category', 'is_reminder')
        }),
        ('Relationships', {
            'fields': ('seller', 'trade', 'asset_hub'),
            'description': 'Optional links to business entities'
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """
        Automatically set created_by to the current user if not already set.
        """
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(AssetIdHub)
class AssetIdHubAdmin(admin.ModelAdmin):
    """Admin for the central Asset ID Hub."""
    list_display = (
        'id', 'servicer_id', 'is_commercial', 'servicer_refs',
        # PK columns showing actual IDs of related records
        'seller_raw_data_id', 'blended_outcome_model_id',  # seller_boarded_data_id removed (deprecated)
        'servicer_loan_data_id', 'valuation_id', 'photo_id', 'document_id',
        'created_at',
    )
    # Show more rows per page (default is 100). Also allow larger "Show all" limit.
    list_per_page = 5
    list_max_show_all = 2000
    search_fields = (
        'servicer_id',
    )
    list_filter = ('is_commercial',)
    actions_on_top = True
    actions_on_bottom = True
    actions = ['delete_selected', delete_hub_and_children]

    def get_queryset(self, request):
        """
        WHAT: Optimize queryset with select_related for related records
        WHY: Reduce database queries when displaying PKs of related records
        HOW: Use select_related for OneToOne/ForeignKey relationships
        """
        qs = super().get_queryset(request)
        return qs.select_related(
            'acq_raw',  # SellerRawData reverse relation
            # 'am_boarded',  # SellerBoardedData reverse relation - DEPRECATED
            'blended_outcome_model',  # BlendedOutcomeModel reverse relation
        )

    def servicer_refs(self, obj: AssetIdHub):  # type: ignore[name-defined]
        """Link to ServicerLoanData rows that share this hub's servicer_id.

        Allows quick navigation to all imported servicer rows tied to the same
        external servicer identifier.
        """
        sid = getattr(obj, 'servicer_id', None)
        if not sid:
            return '-'
        try:
            servicer_url = f"{reverse('admin:am_module_servicerloandata_changelist')}?servicer_id={quote(str(sid))}"
        except Exception:
            servicer_url = '#'

        count = ServicerLoanData.objects.filter(servicer_id=sid).count()
        return format_html('<a href="{}">Servicer Rows ({})</a>', servicer_url, count)
    servicer_refs.short_description = 'Servicer Data'

    # Override the built-in delete_selected to delete the hub bundle in the correct order
    @admin.action(description="Delete selected Asset ID Hub (bundle)")
    def delete_selected(self, request, queryset):
        return delete_hub_and_children(self, request, queryset)
    
    # WHAT: Display methods showing PKs of related records
    # WHY: Show actual IDs instead of checkmarks for reference table
    # HOW: Access reverse OneToOne relationships and return PK or dash
    
    def seller_raw_data_id(self, obj: AssetIdHub):
        """Display SellerRawData PK if exists"""
        return obj.acq_raw.pk if hasattr(obj, 'acq_raw') else '—'
    seller_raw_data_id.short_description = 'SellerRawData'

    # def seller_boarded_data_id(self, obj: AssetIdHub):
    #     """DEPRECATED - SellerBoardedData no longer used"""
    #     return obj.am_boarded.pk if hasattr(obj, 'am_boarded') else '—'
    # seller_boarded_data_id.short_description = 'SellerBoardedData'

    def blended_outcome_model_id(self, obj: AssetIdHub):
        """Display BlendedOutcomeModel PK if exists (PK = asset_hub_id)"""
        return obj.blended_outcome_model.pk if hasattr(obj, 'blended_outcome_model') else '—'
    blended_outcome_model_id.short_description = 'BlendedOutcomeModel'
    
    def servicer_loan_data_id(self, obj: AssetIdHub):
        """Display first ServicerLoanData PK if exists (may be multiple)"""
        servicer_data = ServicerLoanData.objects.filter(asset_hub=obj).first()
        return servicer_data.id if servicer_data else '—'
    servicer_loan_data_id.short_description = 'ServicerLoanData'
    
    def valuation_id(self, obj: AssetIdHub):
        """Display first Valuation PK if exists (may be multiple)"""
        valuation = Valuation.objects.filter(asset_hub=obj).first()
        return valuation.id if valuation else '—'
    valuation_id.short_description = 'Valuation'
    
    def photo_id(self, obj: AssetIdHub):
        """Display count of photos"""
        count = Photo.objects.filter(asset_hub=obj).count()
        return f'{count} photos' if count > 0 else '—'
    photo_id.short_description = 'Photos'
    
    def document_id(self, obj: AssetIdHub):
        """Display count of documents"""
        count = Document.objects.filter(asset_hub=obj).count()
        return f'{count} docs' if count > 0 else '—'
    document_id.short_description = 'Documents'
