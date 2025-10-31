"""
DEPRECATED: This file is no longer used.

All admin registrations have been moved to core/admin.py to use standard Django admin.
This file can be safely deleted.

Note: Linting errors are expected since imports are commented out.
"""

# DEPRECATED - DO NOT USE
# All admin registrations moved to core/admin.py

# from django.contrib import admin
# from core.models import (
#     DebtFacility,
#     CoInvestor,
#     InvestorContribution,
#     InvestorDistribution,
#     Fund,
# )


# # @admin.register(DebtFacility)
class DebtFacilityAdmin(admin.ModelAdmin):
    """Admin configuration for DebtFacility model."""
    list_display = (
        "facility_name",
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


# @admin.register(CoInvestor)
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


# @admin.register(InvestorContribution)
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


# @admin.register(InvestorDistribution)
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


# @admin.register(Fund)
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

