"""
Reporting Module Services

WHAT: Service layer for reporting dashboard business logic
WHY: Separate data access and computation from serialization (thin serializers principle)
WHERE: Imported by views and serializers for data preparation

SERVICE FILES:
- serv_rep_queryBuilder.py - QuerySet construction with filters
- serv_rep_aggregations.py - Aggregation and grouping logic
- serv_rep_byTrade.py - By Trade report specific logic
- serv_rep_byStatus.py - By Status report specific logic
- serv_rep_byFund.py - By Fund report specific logic
- serv_rep_byEntity.py - By Entity report specific logic

ARCHITECTURE:
View → Service → QuerySet → Model
     ↓
  Serializer (thin wrapper)
"""

