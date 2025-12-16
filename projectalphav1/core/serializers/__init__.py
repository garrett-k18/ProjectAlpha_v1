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
from .serial_co_crm import (
    MasterCRMSerializer,
    InvestorSerializer,
    BrokerSerializer,
    TradingPartnerSerializer,
    LegalSerializer,
    MSAReferenceSerializer,
)
from .serial_co_assumptions import (
    StateReferenceSerializer,
    FCTimelinesSerializer,
    FCStatusSerializer,
    CommercialUnitsSerializer,
    ServicerSerializer,
)
from .serial_co_calendar import (
    CalendarEventReadSerializer,
    CustomCalendarEventSerializer,
    UnifiedCalendarEventSerializer,
    CALENDAR_DATE_FIELDS,
)

from .serial_core_notification import (
    NotificationSerializer,
    ActivityItemSerializer,
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
    'MSAReferenceSerializer',
    'StateReferenceSerializer',
    'FCTimelinesSerializer',
    'FCStatusSerializer',
    'CommercialUnitsSerializer',
    'ServicerSerializer',
    'CalendarEventReadSerializer',
    'CustomCalendarEventSerializer',
    'UnifiedCalendarEventSerializer',
    'CALENDAR_DATE_FIELDS',
    'NotificationSerializer',
    'ActivityItemSerializer',
]
