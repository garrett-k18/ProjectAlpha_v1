"""
Reporting Module Serializers

WHAT: Field definitions for reporting dashboard API responses
WHY: Single source of truth for API contracts (thin serializers principle)
WHERE: Imported by views for response formatting

SERIALIZERS:
- serial_rep_summary.py - Summary KPI fields
- serial_rep_byTrade.py - By Trade report fields
- serial_rep_byStatus.py - By Status report fields (TODO)
- serial_rep_byFund.py - By Fund report fields (TODO)
- serial_rep_byEntity.py - By Entity report fields (TODO)

RULE: All field definitions live in serializers. Views/APIs import from serializers.
      Never define fields inline in views or services.
"""

from .serial_rep_summary import SummaryKPISerializer
from .serial_rep_byTrade import (
    TradeChartSerializer,
    TradeGridSerializer,
    TradeReportSerializer,
)
from .serial_rep_filterOptions import (
    TradeOptionSerializer,
    StatusOptionSerializer,
    FundOptionSerializer,
    FundLegalEntityOptionSerializer,
)

__all__ = [
    'SummaryKPISerializer',
    'TradeChartSerializer',
    'TradeGridSerializer',
    'TradeReportSerializer',
    'TradeOptionSerializer',
    'StatusOptionSerializer',
    'FundOptionSerializer',
    'FundLegalEntityOptionSerializer',
]

