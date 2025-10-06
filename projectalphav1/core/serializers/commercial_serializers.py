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
