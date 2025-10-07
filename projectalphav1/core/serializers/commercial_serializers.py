"""
DRF Serializers for Commercial Real Estate Models.

What: Serializers for UnitMix, LeaseComparableUnitMix, and LeaseComparableRentRoll
Why: Expose commercial property data to frontend Commercial Analysis tab
Where: projectalphav1/core/serializers/commercial_serializers.py
How: Serialize all relevant fields with computed properties for UI consumption

Docs reviewed:
- DRF Serializers: https://www.django-rest-framework.org/api-guide/serializers/
- DRF ModelSerializer: https://www.django-rest-framework.org/api-guide/serializers/#modelserializer
"""
from rest_framework import serializers
from core.models.commercial import UnitMix, RentRoll
from core.models.valuations import LeaseComparableUnitMix, LeaseComparableRentRoll
from core.models.propertycfs import HistoricalPropertyCashFlow


class UnitMixSerializer(serializers.ModelSerializer):
    """
    Serializer for subject property unit mix data.
    
    What: Exposes all unit mix fields plus calculated metrics from model methods
    Why: Frontend displays backend calculations for consistency and auditability
    How: All calculations come from UnitMix model methods; no frontend math needed
    """
    # Expose all calculated fields from model methods
    total_sqft = serializers.SerializerMethodField()
    total_monthly_rent = serializers.SerializerMethodField()
    total_annual_rent = serializers.SerializerMethodField()
    
    class Meta:
        model = UnitMix
        fields = [
            'id',
            'unit_type',
            'unit_count',
            'unit_avg_sqft',
            'unit_avg_rent',
            'price_sqft',  # Auto-calculated on save: unit_avg_rent / unit_avg_sqft
            'total_sqft',  # Calculated: unit_count * unit_avg_sqft
            'total_monthly_rent',  # Calculated: unit_count * unit_avg_rent
            'total_annual_rent',  # Calculated: total_monthly_rent * 12
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'price_sqft', 'total_sqft', 'total_monthly_rent', 'total_annual_rent', 'created_at', 'updated_at']
    
    def get_total_sqft(self, obj):
        """
        What: Total square footage for this unit type
        Why: Shows total sqft footprint (count × avg_sqft)
        How: Calls obj.get_total_sqft()
        """
        try:
            return obj.get_total_sqft()
        except Exception:
            return 0
    
    def get_total_monthly_rent(self, obj):
        """
        What: Total monthly rent for this unit type
        Why: Shows revenue potential (count × avg_rent)
        How: Calls obj.get_total_monthly_rent()
        """
        try:
            return float(obj.get_total_monthly_rent())
        except Exception:
            return 0.0
    
    def get_total_annual_rent(self, obj):
        """
        What: Total annual rent for this unit type
        Why: Shows annualized revenue (total_monthly_rent × 12)
        How: Calls obj.get_total_annual_rent()
        """
        try:
            return float(obj.get_total_annual_rent())
        except Exception:
            return 0.0


class RentRollSerializer(serializers.ModelSerializer):
    """
    Serializer for subject property RentRoll rows.
    
    What: Exposes per-unit lease details and calculated metrics from model methods
    Why: Frontend Commercial Analysis tab needs subject rent roll data
    How: Include model-derived metrics like price per sqft and annual amounts
    """
    # Calculated metrics provided by model helpers
    price_per_sqft = serializers.SerializerMethodField()
    annual_rent = serializers.SerializerMethodField()
    cam_per_sqft = serializers.SerializerMethodField()
    annual_cam = serializers.SerializerMethodField()

    class Meta:
        model = RentRoll
        fields = [
            'id',
            'tenant_name',
            'unit_name',
            'sq_feet',
            'rent',
            'lease_start_date',
            'lease_end_date',
            'lease_term_months',
            'lease_type',
            'rent_increase_pct',
            'notes',
            # Calculated
            'price_per_sqft',
            'annual_rent',
            'cam_per_sqft',
            'annual_cam',
        ]
        read_only_fields = [
            'id', 'price_per_sqft', 'annual_rent', 'cam_per_sqft', 'annual_cam'
        ]

    def get_price_per_sqft(self, obj):
        try:
            return float(obj.get_price_per_sqft())
        except Exception:
            return 0.0

    def get_annual_rent(self, obj):
        try:
            return float(obj.get_annual_rent())
        except Exception:
            return 0.0

    def get_cam_per_sqft(self, obj):
        try:
            return float(obj.get_cam_per_sqft())
        except Exception:
            return 0.0

    def get_annual_cam(self, obj):
        try:
            return float(obj.get_annual_cam())
        except Exception:
            return 0.0
    
    def get_total_annual_rent(self, obj):
        """
        What: Total annual rent for this unit type
        Why: Shows annualized revenue (total_monthly_rent × 12)
        How: Calls obj.get_total_annual_rent()
        """
        try:
            return float(obj.get_total_annual_rent())
        except Exception:
            return 0.0


class LeaseComparableUnitMixSerializer(serializers.ModelSerializer):
    """
    Serializer for lease comparable unit mix data.
    
    What: Exposes all unit mix fields plus calculated metrics from model methods
    Why: Frontend displays backend calculations for consistency and auditability
    How: All calculations come from LeaseComparableUnitMix model methods
    """
    # Add property label for frontend display (from parent ComparableProperty)
    property_label = serializers.SerializerMethodField()
    # Expose all calculated fields from model methods
    total_sqft = serializers.SerializerMethodField()
    total_monthly_rent = serializers.SerializerMethodField()
    total_annual_rent = serializers.SerializerMethodField()
    
    class Meta:
        model = LeaseComparableUnitMix
        fields = [
            'id',
            'property_label',  # Computed from comparable_property
            'unit_type',
            'unit_count',
            'unit_avg_sqft',
            'unit_avg_rent',
            'price_sqft',  # Auto-calculated on save: unit_avg_rent / unit_avg_sqft
            'total_sqft',  # Calculated: unit_count * unit_avg_sqft
            'total_monthly_rent',  # Calculated: unit_count * unit_avg_rent
            'total_annual_rent',  # Calculated: total_monthly_rent * 12
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'price_sqft', 'total_sqft', 'total_monthly_rent', 'total_annual_rent', 'created_at', 'updated_at']
    
    def get_property_label(self, obj):
        """
        Return a readable label for the parent comparable property.
        
        What: Creates a display string like "Comp #1 - 123 Main St" or "Comp Property ID 5"
        Why: Frontend table needs to show which property each unit mix belongs to
        How: Use address if available, else fallback to ID
        """
        try:
            comp = obj.comparable_property
            # Prefer address if available
            if comp.address:
                return f"{comp.address}"
            # Fallback to ID
            return f"Comparable Property #{comp.id}"
        except Exception:
            return "Unknown Property"
    
    def get_total_sqft(self, obj):
        """
        What: Total square footage for this unit type
        Why: Shows total sqft footprint (count × avg_sqft)
        How: Calls obj.get_total_sqft()
        """
        try:
            return obj.get_total_sqft()
        except Exception:
            return 0
    
    def get_total_monthly_rent(self, obj):
        """
        What: Total monthly rent for this unit type
        Why: Shows revenue potential (count × avg_rent)
        How: Calls obj.get_total_monthly_rent()
        """
        try:
            return float(obj.get_total_monthly_rent())
        except Exception:
            return 0.0
    
    def get_total_annual_rent(self, obj):
        """
        What: Total annual rent for this unit type
        Why: Shows annualized revenue (total_monthly_rent × 12)
        How: Calls obj.get_total_annual_rent()
        """
        try:
            return float(obj.get_total_annual_rent())
        except Exception:
            return 0.0


class LeaseComparableRentRollSerializer(serializers.ModelSerializer):
    """
    Serializer for lease comparable rent roll (unit-level) data.
    
    What: Exposes individual unit lease details for comparable properties
    Why: Frontend needs this for Lease Comp Rent Roll table (rare but detailed)
    How: Include property_label from parent ComparableProperty for display
    """
    # Add property label for frontend display (from parent ComparableProperty)
    property_label = serializers.SerializerMethodField()
    
    class Meta:
        model = LeaseComparableRentRoll
        fields = [
            'id',
            'property_label',  # Computed from comparable_property
            'unit_number',
            'beds',
            'baths',
            'unit_sqft',
            'monthly_rent',
            'lease_start_date',
            'lease_end_date',
            'lease_term_months',
            'lease_type',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_property_label(self, obj):
        """
        Return a readable label for the parent comparable property.
        
        What: Creates a display string like "123 Main St" or "Property #5"
        Why: Frontend table needs to show which property each unit belongs to
        How: Use address if available, else fallback to ID
        """
        try:
            comp = obj.comparable_property
            # Prefer address if available
            if comp.address:
                return f"{comp.address}"
            # Fallback to ID
            return f"Comparable Property #{comp.id}"
        except Exception:
            return "Unknown Property"


class HistoricalPropertyCashFlowSerializer(serializers.ModelSerializer):
    """
    Serializer for Historical Property Cash Flow data.
    
    What: Exposes annual cash flow data with calculated metrics from model methods
    Why: Frontend needs historical operating performance for analysis
    How: Include model-derived metrics like vacancy_loss, effective rent, EGI, Total Opex, NOI, and OER
    """
    # Calculated metrics provided by model helpers
    vacancy_loss = serializers.SerializerMethodField()
    effective_gross_rent_revenue = serializers.SerializerMethodField()
    effective_gross_income = serializers.SerializerMethodField()
    total_operating_expenses = serializers.SerializerMethodField()
    net_operating_income = serializers.SerializerMethodField()
    operating_expense_ratio = serializers.SerializerMethodField()

    class Meta:
        model = HistoricalPropertyCashFlow
        fields = [
            'id',
            'year',
            # Income
            'gross_potential_rent_revenue',
            'cam_income',
            'other_income',
            'vacancy_pct',
            'vacancy_loss',  # Calculated from vacancy_pct * gross_potential_rent_revenue
            'effective_gross_rent_revenue',  # Calculated: gross_potential_rent_revenue - vacancy_loss
            # Operating Expenses
            'admin',
            'insurance',
            'utilities_water',
            'utilities_sewer',
            'utilities_electric',
            'utilities_gas',
            'trash',
            'utilities_other',
            'property_management',
            'repairs_maintenance',
            'marketing',
            'property_taxes',
            'hoa_fees',
            'security_property_preservation',
            'landscaping',
            'pool_maintenance',
            'other_expense',
            # Calculated fields
            'effective_gross_income',  # Calculated: effective_gross_rent_revenue + other_income + cam_income
            'total_operating_expenses',
            'net_operating_income',
            'operating_expense_ratio',
            # Meta
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'vacancy_loss', 'effective_gross_rent_revenue', 'effective_gross_income', 
            'total_operating_expenses', 'net_operating_income', 'operating_expense_ratio', 
            'created_at', 'updated_at'
        ]

    def get_vacancy_loss(self, obj):
        """
        What: Vacancy Loss (Gross Potential Rent * Vacancy %)
        Why: Shows dollar amount of lost revenue due to vacancy
        How: Calls obj.vacancy_loss()
        """
        try:
            return float(obj.vacancy_loss())
        except Exception:
            return 0.0

    def get_effective_gross_rent_revenue(self, obj):
        """
        What: Effective Gross Rent Revenue (GPR - Vacancy Loss)
        Why: Shows actual rent revenue after vacancy
        How: Calls obj.effective_gross_rent_revenue()
        """
        try:
            return float(obj.effective_gross_rent_revenue())
        except Exception:
            return 0.0

    def get_effective_gross_income(self, obj):
        """
        What: Effective Gross Income (Effective Rent + Other Income + CAM)
        Why: Shows total actual income after vacancy
        How: Calls obj.effective_gross_income()
        """
        try:
            return float(obj.effective_gross_income())
        except Exception:
            return 0.0

    def get_total_operating_expenses(self, obj):
        """
        What: Sum of all operating expenses
        Why: Shows total annual opex
        How: Calls obj.total_operating_expenses()
        """
        try:
            return float(obj.total_operating_expenses())
        except Exception:
            return 0.0

    def get_net_operating_income(self, obj):
        """
        What: Net Operating Income (EGI - Total Opex)
        Why: Key valuation metric (NOI / Cap Rate = Value)
        How: Calls obj.net_operating_income()
        """
        try:
            return float(obj.net_operating_income())
        except Exception:
            return 0.0

    def get_operating_expense_ratio(self, obj):
        """
        What: Operating Expense Ratio (Total Opex / EGI * 100)
        Why: Measures operating efficiency
        How: Calls obj.operating_expense_ratio()
        """
        try:
            return float(obj.operating_expense_ratio())
        except Exception:
            return 0.0
