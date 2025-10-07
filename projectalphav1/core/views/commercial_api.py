"""
API Views for Commercial Real Estate Data.

What: REST API endpoints for UnitMix, LeaseComparableUnitMix, and LeaseComparableRentRoll
Why: Frontend Commercial Analysis tab needs to fetch this data by asset_hub_id
Where: projectalphav1/core/views/commercial_api.py
How: DRF ListAPIView filtered by asset_hub_id passed in URL

Endpoints:
- GET /core/unit-mix/<asset_hub_id>/ - Subject property unit mix
- GET /core/lease-comp-unit-mix/<asset_hub_id>/ - Lease comparable unit mix
- GET /core/lease-comp-rent-roll/<asset_hub_id>/ - Lease comparable rent roll

Docs reviewed:
- DRF Generic Views: https://www.django-rest-framework.org/api-guide/generic-views/
- DRF ListAPIView: https://www.django-rest-framework.org/api-guide/generic-views/#listapiview
"""
from rest_framework import generics
from core.models.commercial import UnitMix, RentRoll
from core.models.valuations import (
    LeaseComparableUnitMix,
    LeaseComparableRentRoll,
    ComparableProperty
)
from core.models.propertycfs import HistoricalPropertyCashFlow
from core.serializers.commercial_serializers import (
    UnitMixSerializer,
    LeaseComparableUnitMixSerializer,
    LeaseComparableRentRollSerializer,
    RentRollSerializer,
    HistoricalPropertyCashFlowSerializer
)


class UnitMixListView(generics.ListAPIView):
    """
    GET /core/unit-mix/<asset_hub_id>/
    
    What: Returns all unit mix records for a given asset
    Why: Frontend Commercial Analysis tab needs subject property unit mix data
    
    Returns: List of unit mix objects with unit_type, count, avg sqft, avg rent, rent/sqft
    """
    serializer_class = UnitMixSerializer
    
    def get_queryset(self):
        """
        Filter unit mix by asset_hub_id from URL parameter.
        
        What: Returns queryset filtered to the requested asset
        Why: Each asset has its own unit mix; need to isolate by asset_hub_id
        How: Extract asset_hub_id from self.kwargs (URL parameter)
        """
        asset_hub_id = self.kwargs.get('asset_hub_id')
        # NOTE: Model field is named 'asset_hub_id' (ForeignKey), so the integer column is 'asset_hub_id_id'
        return UnitMix.objects.filter(asset_hub_id_id=asset_hub_id).order_by('unit_type')


class LeaseComparableUnitMixListView(generics.ListAPIView):
    """
    GET /core/lease-comp-unit-mix/<asset_hub_id>/
    
    What: Returns all lease comp unit mix records for comps linked to a given asset
    Why: Frontend Commercial Analysis tab needs comparable property unit mix data
    How: Find all ComparableProperty records for asset_hub_id, then get related unit mix
    
    Returns: List of lease comp unit mix objects with property_label and unit mix details
    """
    serializer_class = LeaseComparableUnitMixSerializer
    
    def get_queryset(self):
        """
        Filter lease comp unit mix by asset_hub_id.
        
        What: Returns unit mix for all comps associated with the requested asset
        Why: Comps are linked to assets; need to find comps first, then their unit mix
        How: 
          1. Get asset_hub_id from URL
          2. Find ComparableProperty records where asset_hub = asset_hub_id
          3. Return LeaseComparableUnitMix filtered by those comparable properties
        """
        asset_hub_id = self.kwargs.get('asset_hub_id')
        
        # Find all comparable properties for this asset
        comp_ids = ComparableProperty.objects.filter(
            asset_hub_id=asset_hub_id
        ).values_list('id', flat=True)
        
        # Return unit mix records for those comps
        return LeaseComparableUnitMix.objects.filter(
            comparable_property_id__in=comp_ids
        ).select_related('comparable_property').order_by('comparable_property', 'unit_type')


class LeaseComparableRentRollListView(generics.ListAPIView):
    """
    GET /core/lease-comp-rent-roll/<asset_hub_id>/
    
    What: Returns all lease comp rent roll (unit-level) records for comps linked to asset
    Why: Frontend Commercial Analysis tab needs detailed unit-level lease data (rare)
    How: Find all ComparableProperty records for asset_hub_id, then get related rent roll units
    
    Returns: List of rent roll unit objects with property_label and lease details
    """
    serializer_class = LeaseComparableRentRollSerializer
    
    def get_queryset(self):
        """
        Filter lease comp rent roll by asset_hub_id.
        
        What: Returns rent roll units for all comps associated with the requested asset
        Why: Rent roll is linked to ComparableProperty; need to find comps first
        How:
          1. Get asset_hub_id from URL
          2. Find ComparableProperty records where asset_hub = asset_hub_id
          3. Return LeaseComparableRentRoll filtered by those comparable properties
        """
        asset_hub_id = self.kwargs.get('asset_hub_id')
        
        # Find all comparable properties for this asset
        comp_ids = ComparableProperty.objects.filter(
            asset_hub_id=asset_hub_id
        ).values_list('id', flat=True)
        
        # Return rent roll records for those comps
        return LeaseComparableRentRoll.objects.filter(
            comparable_property_id__in=comp_ids
        ).select_related('comparable_property').order_by('comparable_property', 'unit_number')


class RentRollListView(generics.ListAPIView):
    """
    GET /core/rent-roll/<asset_hub_id>/
    
    What: Returns subject property's rent roll units for the asset
    Why: Frontend needs per-unit rent roll for Commercial Analysis
    How: Filter RentRoll by asset_hub_id from the URL
    """
    serializer_class = RentRollSerializer

    def get_queryset(self):
        asset_hub_id = self.kwargs.get('asset_hub_id')
        # NOTE: Model field is named 'asset_hub_id' (ForeignKey), so the integer column is 'asset_hub_id_id'
        return RentRoll.objects.filter(asset_hub_id_id=asset_hub_id).order_by('unit_name', 'tenant_name')


class HistoricalPropertyCashFlowListView(generics.ListAPIView):
    """
    GET /core/historical-cashflow/<asset_hub_id>/
    
    What: Returns historical property cash flow records (annual operating data) for the asset
    Why: Frontend needs historical cash flow for Commercial Analysis tab
    How: Filter HistoricalPropertyCashFlow by asset_hub from the URL, order by year descending
    """
    serializer_class = HistoricalPropertyCashFlowSerializer

    def get_queryset(self):
        asset_hub_id = self.kwargs.get('asset_hub_id')
        return HistoricalPropertyCashFlow.objects.filter(asset_hub_id=asset_hub_id).order_by('-year')
