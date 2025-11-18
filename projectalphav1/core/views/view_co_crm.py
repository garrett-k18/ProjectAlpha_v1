"""
core.views.crm_api

Purpose
-------
API endpoints for MasterCRM model to support CRM views (Brokers, Trading Partners, Investors, etc.)

Docs Reviewed
-------------
- DRF ViewSets: https://www.django-rest-framework.org/api-guide/viewsets/
- Filtering: https://www.django-rest-framework.org/api-guide/filtering/
- Pagination: https://www.django-rest-framework.org/api-guide/pagination/
"""

from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Q

from core.models.model_co_crm import MasterCRM
from core.serializers.serial_co_crm import (
    MasterCRMSerializer,
    InvestorSerializer,
    BrokerSerializer,
    TradingPartnerSerializer,
    LegalSerializer,
    ServicerSerializer,
)


class MasterCRMViewSet(viewsets.ModelViewSet):
    """
    Base ViewSet for MasterCRM model with filtering and search.
    
    What: Provides CRUD operations for MasterCRM entries
    Why: Centralized API for all CRM data with tag-based filtering
    Where: Base class for specific CRM type viewsets (Investors, Brokers, etc.)
    How: Filters by tag, supports search across firm/name/email, paginated results
    """
    
    queryset = (
        MasterCRM.objects.all()
        .select_related('firm_ref')
        .prefetch_related(
            'states',
            'firm_ref__states',
            'msa_assignments__msa',
        )
        .order_by('-created_at')
    )
    serializer_class = MasterCRMSerializer
    permission_classes = [AllowAny]  # Match project pattern - authentication bypassed in dev
    pagination_class = None  # Disable pagination to show all brokers (100+)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        'firm_ref__name',
        'contact_name',
        'email',
        'phone',
        'city',
        'states__state_code',
        'states__state_name',
        'msa_assignments__msa__msa_name',
        'msa_assignments__msa__msa_code',
    ]
    ordering_fields = ['firm_ref__name', 'contact_name', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Filter queryset based on tag parameter.
        
        What: Returns filtered MasterCRM records
        Why: Allows filtering by contact type (broker, investor, etc.)
        How: Checks 'tag' query param and filters queryset accordingly
        """
        queryset = super().get_queryset()
        
        # Safely get query params (handle both DRF and Django request objects)
        query_params = getattr(self.request, 'query_params', None) or getattr(self.request, 'GET', {})
        
        # Filter by tag if provided in query params
        tag = query_params.get('tag', None) if query_params else None
        if tag:
            queryset = queryset.filter(tag=tag)
        
        # Support search query parameter 'q' for frontend compatibility
        q = query_params.get('q', None) if query_params else None
        if q:
            queryset = queryset.filter(
                Q(firm_ref__name__icontains=q)
                | Q(contact_name__icontains=q)
                | Q(email__icontains=q)
                | Q(phone__icontains=q)
                | Q(city__icontains=q)
                | Q(states__state_code__icontains=q)
                | Q(states__state_name__icontains=q)
            ).distinct()

        # Optional filter by single state code (M2M only)
        state_code = query_params.get('state', None) if query_params else None
        if state_code:
            queryset = queryset.filter(
                Q(states__state_code__iexact=state_code)
            ).distinct()

        # Optional filter by multiple state codes: states=CA,AZ,TX
        multi_states = query_params.get('states', None) if query_params else None
        if multi_states:
            codes = [s.strip().upper() for s in multi_states.split(',') if s.strip()]
            if codes:
                queryset = queryset.filter(states__state_code__in=codes).distinct()

        # Optional filter by MSA name or code: msa=Los Angeles
        msa_filter = query_params.get('msa', None) if query_params else None
        if msa_filter:
            queryset = queryset.filter(
                Q(msa_assignments__msa__msa_name__icontains=msa_filter)
                | Q(msa_assignments__msa__msa_code__icontains=msa_filter)
            ).distinct()
        
        return queryset


class InvestorViewSet(MasterCRMViewSet):
    """
    ViewSet for Investor CRM entries (tag='investor').
    
    What: API endpoint specifically for investor contacts
    Why: Provides dedicated /api/core/crm/investors/ endpoint
    Where: Mounted at /api/core/crm/investors/ in urls.py
    How: Filters MasterCRM to only show investor-tagged entries
    """
    
    serializer_class = InvestorSerializer
    
    def get_queryset(self):
        """
        Return only MasterCRM entries with tag='investor'.
        
        What: Filters to investor-only records
        Why: This endpoint should only show/manage investors
        How: Adds tag filter to base queryset
        """
        queryset = super().get_queryset()
        return queryset.filter(tag=MasterCRM.ContactTag.INVESTOR)


class BrokerViewSet(MasterCRMViewSet):
    """
    ViewSet for Broker CRM entries (tag='broker').
    
    What: API endpoint specifically for broker contacts
    Why: Provides dedicated /api/core/crm/brokers/ endpoint
    Where: Mounted at /api/core/crm/brokers/ in urls.py
    How: Filters MasterCRM to only show broker-tagged entries
    """
    
    serializer_class = BrokerSerializer
    
    def get_queryset(self):
        """
        Return only MasterCRM entries with tag='broker'.
        
        What: Filters to broker-only records
        Why: This endpoint should only show/manage brokers
        How: Adds tag filter to base queryset
        """
        queryset = super().get_queryset()
        return queryset.filter(tag=MasterCRM.ContactTag.BROKER)


class TradingPartnerViewSet(MasterCRMViewSet):
    """
    ViewSet for Trading Partner CRM entries (tag='trading_partner').
    
    What: API endpoint specifically for trading partner contacts
    Why: Provides dedicated /api/core/crm/trading-partners/ endpoint
    Where: Mounted at /api/core/crm/trading-partners/ in urls.py
    How: Filters MasterCRM to only show trading_partner-tagged entries
    """
    
    serializer_class = TradingPartnerSerializer
    
    def get_queryset(self):
        """
        Return only MasterCRM entries with tag='trading_partner'.
        
        What: Filters to trading partner-only records
        Why: This endpoint should only show/manage trading partners
        How: Adds tag filter to base queryset
        """
        queryset = super().get_queryset()
        return queryset.filter(tag=MasterCRM.ContactTag.TRADING_PARTNER)


class LegalViewSet(MasterCRMViewSet):
    """
    ViewSet for Legal CRM entries (tag='legal').
    
    What: API endpoint specifically for legal contacts
    Why: Provides dedicated /api/core/crm/legal/ endpoint
    Where: Mounted at /api/core/crm/legal/ in urls.py
    How: Filters MasterCRM to only show legal-tagged entries
    """
    
    serializer_class = LegalSerializer
    
    def get_queryset(self):
        """
        Return only MasterCRM entries with tag='legal'.
        
        What: Filters to legal-only records
        Why: This endpoint should only show/manage legal contacts
        How: Adds tag filter to base queryset
        """
        queryset = super().get_queryset()
        return queryset.filter(tag=MasterCRM.ContactTag.LEGAL)


class ServicerViewSet(MasterCRMViewSet):
    """
    ViewSet for Servicer CRM entries (tag='servicer').
    
    What: API endpoint specifically for servicer contacts
    Why: Provides dedicated /api/core/crm/servicers/ endpoint
    Where: Mounted at /api/core/crm/servicers/ in urls.py
    How: Filters MasterCRM to only show servicer-tagged entries
    """
    
    serializer_class = ServicerSerializer
    
    def get_queryset(self):
        """
        Return only MasterCRM entries with tag='servicer'.
        
        What: Filters to servicer-only records
        Why: This endpoint should only show/manage servicer contacts
        How: Adds tag filter to base queryset
        """
        queryset = super().get_queryset()
        return queryset.filter(tag=MasterCRM.ContactTag.SERVICER)
