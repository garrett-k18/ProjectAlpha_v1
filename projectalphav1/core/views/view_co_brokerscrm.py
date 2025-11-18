"""
Broker-specific CRM API views.

What: Simple, focused API for broker CRM operations
Why: Clean separation from complex unified CRM views
Where: Provides /api/core/brokers/ endpoints
How: Large page size pagination, simple filtering, broker-only data
"""

from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q

from core.models.model_co_crm import MasterCRM
from core.serializers.serial_co_brokerscrm import BrokerCRMSerializer


class BrokerPagination(PageNumberPagination):
    """Large page size pagination for brokers to avoid timeouts."""
    page_size = 100  # Load 100 brokers per page
    page_size_query_param = 'page_size'
    max_page_size = 500


class BrokerCRMViewSet(viewsets.ModelViewSet):
    """
    Simple ViewSet for broker CRM operations.
    
    What: CRUD operations for brokers only
    Why: Focused, clean API without complex filtering
    How: Large page size pagination, simple search, broker tag filter
    """
    
    serializer_class = BrokerCRMSerializer
    permission_classes = [AllowAny]  # Dev mode - no auth
    pagination_class = BrokerPagination  # Large page size to prevent timeouts
    filter_backends = [filters.SearchFilter]
    search_fields = ['contact_name', 'firm', 'email', 'phone']
    
    def get_queryset(self):
        """Get all brokers with heavily optimized queries for performance."""
        queryset = (
            MasterCRM.objects
            .filter(tag=MasterCRM.ContactTag.BROKER)  # Only brokers
            .select_related('firm_ref')  # Join firm table in single query
            .prefetch_related(
                'states',  # Prefetch states M2M
                'msa_assignments__msa__state',  # Prefetch MSA assignments with state info
            )
            .only(  # Only fetch needed fields to reduce data transfer
                'id', 'contact_name', 'email', 'phone', 'city', 'created_at', 'updated_at',
                'firm_ref__name', 'firm_ref__id'  # Only needed firm fields
            )
            .order_by('contact_name')
        )
        
        # Simple search support
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(contact_name__icontains=search) |
                Q(firm_ref__name__icontains=search) |  # Use firm_ref instead of firm property
                Q(email__icontains=search) |
                Q(phone__icontains=search)
            )
        
        # Filter by state
        state = self.request.query_params.get('state', None)
        if state:
            queryset = queryset.filter(states__state_code__iexact=state)
        
        return queryset.distinct()
