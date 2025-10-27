"""
Core serializers package.

What: DRF serializers for core models
Why: Centralize API serialization logic for core app
Where: projectalphav1/core/serializers/
How: Import serializers from submodules for easy access
"""
from .commercial_serializers import (
    UnitMixSerializer,
    LeaseComparableUnitMixSerializer,
    LeaseComparableRentRollSerializer
)
from .crm_serializers import (
    MasterCRMSerializer,
    InvestorSerializer,
    BrokerSerializer,
    TradingPartnerSerializer,
    LegalSerializer,
)
from .serial_co_calendar import (
    CalendarEventReadSerializer,
    CustomCalendarEventSerializer,
    UnifiedCalendarEventSerializer,
    CALENDAR_DATE_FIELDS,
)

__all__ = [
    'UnitMixSerializer',
    'LeaseComparableUnitMixSerializer',
    'LeaseComparableRentRollSerializer',
    'MasterCRMSerializer',
    'InvestorSerializer',
    'BrokerSerializer',
    'TradingPartnerSerializer',
    'LegalSerializer',
    'CalendarEventReadSerializer',
    'CustomCalendarEventSerializer',
    'UnifiedCalendarEventSerializer',
    'CALENDAR_DATE_FIELDS',
]
