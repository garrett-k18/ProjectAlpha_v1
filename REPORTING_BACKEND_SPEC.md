# Reporting Dashboard - Backend API Specification

## Overview
This document outlines the backend API structure needed to support the reporting dashboard frontend. The frontend is **100% complete** and ready for integration.

---

## Required Metrics & Calculations

### Portfolio-Level Metrics
- **Monthly Cash Flow** - For IRR and NPV calculations
- **MOIC** (Multiple on Invested Capital) - Total proceeds / Total invested
- **Gross Cost Basis** - Sum of all acquisition costs
- **Total Purchase Price** - Sum of all purchase prices
- **Total Proceeds** - Sum of all disposition proceeds
- **Net Proceeds** - Total proceeds - Total costs
- **P&L** (Profit & Loss) - Net proceeds - Gross cost basis
- **IRR** (Internal Rate of Return) - Time-weighted return on investment
- **NPV** (Net Present Value) - Present value of future cash flows
- **Duration** - Average holding period across portfolio

### Asset Management Metrics (NEW)
- **Foreclosure Count** - Active foreclosure tasks by status
- **REO Count** - Active REO properties by task type (Eviction, Trashout, Renovation, Marketing)
- **Modification Count** - Active loan modifications by status
- **Short Sale Count** - Active short sales by status
- **BPO Count** - Broker Price Opinions completed/pending
- **Title Count** - Title issues by status
- **Active Tracks** - Count of active asset management tracks
- **Completed Tasks** - Count of completed AM tasks by type

---

## Django Project Structure

```
projectalphav1/
├── reporting/                          # NEW Django app (separate from acq_module)
│   ├── __init__.py
│   ├── models/
│   │   └── model_rep_config.py        # Report config models (optional)
│   ├── serializers/
│   │   ├── serial_rep_filters.py      # Filter option serializers
│   │   └── serial_rep_data.py         # Report data serializers
│   ├── views/
│   │   ├── view_rep_filters.py        # Filter dropdown endpoints
│   │   ├── view_rep_summary.py        # Summary KPI endpoint
│   │   ├── view_rep_trade.py          # By Trade report
│   │   ├── view_rep_status.py         # By Status report
│   │   ├── view_rep_fund.py           # By Fund report
│   │   ├── view_rep_entity.py         # By Entity report
│   │   └── view_rep_am.py             # Asset Management report (NEW)
│   ├── logic/
│   │   ├── logic_rep_metrics.py       # Portfolio metric calculations
│   │   ├── logic_rep_filters.py       # Filter query helpers
│   │   └── logic_rep_am.py            # Asset management rollups (NEW)
│   └── urls.py                         # URL routing
```

**File Naming Convention:**
- Logic files: `logic_rep_<purpose>.py`
- View files: `view_rep_<purpose>.py`
- Serializer files: `serial_rep_<purpose>.py`
- Model files: `model_rep_<purpose>.py`

---

## API Endpoints

### 1. Filter Options (Dropdowns)

#### GET `/api/reporting/trades/`
**Purpose:** Populate trades multi-select dropdown

**Response:**
```json
[
  {
    "id": 1,
    "trade_name": "Trade ABC",
    "seller_name": "Seller XYZ"
  },
  {
    "id": 2,
    "trade_name": "Trade DEF",
    "seller_name": "Seller QRS"
  }
]
```

**Django Implementation:**
```python
# views/view_rep_filters.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from acq_module.models import Trade

@api_view(['GET'])
def get_trade_options(request):
    """
    **WHAT**: Return all trades for filter dropdown
    **WHY**: Populate multi-select trade filter
    **WHERE**: Called on dashboard mount
    """
    trades = Trade.objects.select_related('seller').values(
        'id', 
        'trade_name',
        seller_name=F('seller__seller_name')
    )
    return Response(list(trades))
```

---

#### GET `/api/reporting/statuses/`
**Purpose:** Populate statuses multi-select dropdown

**Response:**
```json
[
  { "value": "DD", "label": "Due Diligence", "count": 15 },
  { "value": "AWARDED", "label": "Awarded", "count": 8 },
  { "value": "PASS", "label": "Passed", "count": 3 },
  { "value": "BOARD", "label": "Boarded", "count": 12 }
]
```

**Django Implementation:**
```python
@api_view(['GET'])
def get_status_options(request):
    """
    **WHAT**: Return all statuses with counts
    **WHY**: Populate multi-select status filter
    """
    from acq_module.models import TradeStatus
    
    statuses = TradeStatus.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    status_map = {
        'DD': 'Due Diligence',
        'AWARDED': 'Awarded',
        'PASS': 'Passed',
        'BOARD': 'Boarded'
    }
    
    result = [
        {
            'value': s['status'],
            'label': status_map.get(s['status'], s['status']),
            'count': s['count']
        }
        for s in statuses
    ]
    
    return Response(result)
```

---

#### GET `/api/reporting/funds/`
**Purpose:** Populate funds multi-select dropdown

**Response:**
```json
[
  { "id": 1, "name": "Fund I", "code": "FUND-I" },
  { "id": 2, "name": "Fund II", "code": "FUND-II" }
]
```

**Note:** If you don't have a Fund model yet, create one or return placeholder data.

---

#### GET `/api/reporting/entities/`
**Purpose:** Populate entities multi-select dropdown

**Response:**
```json
[
  { "id": 1, "name": "Alpha Capital LLC", "entity_type": "LLC" },
  { "id": 2, "name": "Beta Properties LP", "entity_type": "LP" }
]
```

**Note:** If you don't have an Entity model yet, create one or return placeholder data.

---

### 2. Summary KPIs

#### GET `/api/reporting/summary/?{filters}`
**Purpose:** Return top-level KPI metrics for header bar

**Query Parameters:**
- `trade_ids` (optional): Comma-separated trade IDs (e.g., `1,2,3`)
- `statuses` (optional): Comma-separated statuses (e.g., `DD,AWARDED`)
- `fund_id` (optional): Single fund ID
- `entity_id` (optional): Single entity ID
- `start_date` (optional): ISO date (e.g., `2024-01-01`)
- `end_date` (optional): ISO date (e.g., `2024-12-31`)

**Response:**
```json
{
  "total_upb": 125000000.50,
  "asset_count": 245,
  "avg_ltv": 72.5,
  "delinquency_rate": 3.2
}
```

**Django Implementation:**
```python
# views/view_rep_summary.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum, Avg, Count, Q
from acq_module.models import SellerRawData

@api_view(['GET'])
def get_report_summary(request):
    """
    **WHAT**: Calculate summary KPIs based on filters
    **WHY**: Display top bar metrics
    **WHERE**: Called when filters change
    """
    # Parse filters from query params
    trade_ids = request.GET.get('trade_ids', '').split(',') if request.GET.get('trade_ids') else []
    statuses = request.GET.get('statuses', '').split(',') if request.GET.get('statuses') else []
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Build base queryset
    qs = SellerRawData.objects.all()
    
    # Apply filters
    if trade_ids:
        qs = qs.filter(trade_id__in=trade_ids)
    if statuses:
        qs = qs.filter(trade__status__in=statuses)
    if start_date:
        qs = qs.filter(trade__bid_date__gte=start_date)
    if end_date:
        qs = qs.filter(trade__bid_date__lte=end_date)
    
    # Calculate aggregates
    summary = qs.aggregate(
        total_upb=Sum('current_balance'),
        asset_count=Count('id'),
        avg_ltv=Avg('ltv')
    )
    
    # Calculate delinquency rate (example logic)
    total_count = summary['asset_count'] or 1
    delinquent_count = qs.filter(
        Q(days_delinquent__gt=30) | Q(status__icontains='delinquent')
    ).count()
    delinquency_rate = (delinquent_count / total_count) * 100
    
    return Response({
        'total_upb': summary['total_upb'] or 0,
        'asset_count': summary['asset_count'] or 0,
        'avg_ltv': summary['avg_ltv'] or 0,
        'delinquency_rate': delinquency_rate
    })
```

---

### 3. By Trade Report

#### GET `/api/reporting/by-trade/?{filters}`
**Purpose:** Return chart data for By Trade report

**Response:**
```json
[
  {
    "x": "Trade ABC",
    "y": 45000000,
    "meta": {
      "count": 120,
      "ltv": 68.5,
      "status": "DD"
    }
  },
  {
    "x": "Trade DEF",
    "y": 32000000,
    "meta": {
      "count": 85,
      "ltv": 75.2,
      "status": "AWARDED"
    }
  }
]
```

**Django Implementation:**
```python
# views/view_rep_trade.py
@api_view(['GET'])
def get_by_trade_chart(request):
    """
    **WHAT**: Aggregate data by trade for chart visualization
    **WHY**: Power By Trade report view
    """
    # Apply same filter logic as summary
    qs = apply_filters(request, SellerRawData.objects.all())
    
    # Group by trade
    trades = qs.values('trade__trade_name', 'trade__status').annotate(
        total_upb=Sum('current_balance'),
        count=Count('id'),
        avg_ltv=Avg('ltv')
    ).order_by('-total_upb')
    
    result = [
        {
            'x': t['trade__trade_name'],
            'y': float(t['total_upb'] or 0),
            'meta': {
                'count': t['count'],
                'ltv': float(t['avg_ltv'] or 0),
                'status': t['trade__status']
            }
        }
        for t in trades
    ]
    
    return Response(result)
```

---

#### GET `/api/reporting/by-trade/grid/?{filters}`
**Purpose:** Return detailed table data for By Trade report

**Response:**
```json
[
  {
    "id": 1,
    "trade_name": "Trade ABC",
    "seller_name": "Seller XYZ",
    "asset_count": 120,
    "total_upb": 45000000,
    "avg_upb": 375000,
    "avg_ltv": 68.5,
    "status": "DD",
    "bid_date": "2024-03-15"
  }
]
```

---

### 4. By Status Report

#### GET `/api/reporting/by-status/?{filters}`
**Purpose:** Return chart data for By Status report

**Response:**
```json
[
  {
    "x": "DD",
    "y": 55000000,
    "meta": {
      "count": 145,
      "percentage": 35.2
    }
  },
  {
    "x": "AWARDED",
    "y": 42000000,
    "meta": {
      "count": 98,
      "percentage": 26.9
    }
  }
]
```

---

#### GET `/api/reporting/by-status/grid/?{filters}`
**Purpose:** Return detailed table data for By Status report

**Response:**
```json
[
  {
    "status": "DD",
    "count": 145,
    "total_upb": 55000000,
    "avg_upb": 379310,
    "percentage": 35.2,
    "avg_ltv": 71.2,
    "total_debt": 62000000,
    "delinquency_rate": 2.8
  }
]
```

---

### 5. By Fund Report

#### GET `/api/reporting/by-fund/?{filters}`
**Purpose:** Return chart data for By Fund report

**Response:**
```json
[
  {
    "x": "Fund I",
    "y": 78000000,
    "meta": {
      "count": 185,
      "ltv": 69.5
    }
  }
]
```

---

### 6. By Entity Report

#### GET `/api/reporting/by-entity/?{filters}`
**Purpose:** Return chart data for By Entity report

**Response:**
```json
[
  {
    "x": "Alpha Capital LLC",
    "y": 92000000,
    "meta": {
      "count": 210,
      "ltv": 68.2,
      "entity_type": "LLC"
    }
  }
]
```

---

### 7. Asset Management Report (NEW)

#### GET `/api/reporting/by-am/?{filters}`
**Purpose:** Return asset management task rollup data

**Response:**
```json
{
  "summary": {
    "total_active_tracks": 245,
    "total_active_tasks": 387,
    "total_completed_tasks": 1523
  },
  "by_track_type": [
    {
      "track_type": "foreclosure",
      "count": 68,
      "by_status": [
        { "status": "title_review", "count": 12 },
        { "status": "filing", "count": 25 },
        { "status": "sale_scheduled", "count": 18 },
        { "status": "completed", "count": 13 }
      ]
    },
    {
      "track_type": "reo",
      "count": 92,
      "by_task_type": [
        { "task_type": "eviction", "count": 15 },
        { "task_type": "trashout", "count": 28 },
        { "task_type": "renovation", "count": 35 },
        { "task_type": "marketing", "count": 14 }
      ]
    },
    {
      "track_type": "modification",
      "count": 45,
      "by_status": [
        { "status": "submitted", "count": 18 },
        { "status": "in_review", "count": 15 },
        { "status": "approved", "count": 8 },
        { "status": "denied", "count": 4 }
      ]
    },
    {
      "track_type": "short_sale",
      "count": 28,
      "by_status": [
        { "status": "listing", "count": 10 },
        { "status": "offer_received", "count": 8 },
        { "status": "bank_approval", "count": 7 },
        { "status": "closed", "count": 3 }
      ]
    },
    {
      "track_type": "bpo",
      "count": 12,
      "by_status": [
        { "status": "ordered", "count": 5 },
        { "status": "completed", "count": 7 }
      ]
    }
  ],
  "chart_data": [
    { "x": "Foreclosure", "y": 68 },
    { "x": "REO", "y": 92 },
    { "x": "Modification", "y": 45 },
    { "x": "Short Sale", "y": 28 },
    { "x": "BPO", "y": 12 }
  ]
}
```

**Django Implementation:**
```python
# reporting/views/view_rep_am.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count
from am_module.models import (
    ForeClosureTrack, ForeClosureTask,
    REOtrack, REOtask,
    ModificationTrack, ModificationTask,
    ShortSaleTrack, ShortSaleTask,
    BPOtrack
)
from reporting.logic.logic_rep_am import (
    rollup_foreclosure_data,
    rollup_reo_data,
    rollup_modification_data,
    rollup_shortsale_data,
    rollup_bpo_data
)

@api_view(['GET'])
def get_am_report(request):
    """
    **WHAT**: Aggregate asset management task data across all track types
    **WHY**: Provide executive-level view of AM operations
    **WHERE**: Called by Asset Management report view
    """
    # Apply filters (if any)
    # For AM report, filters might be date range, fund, entity
    
    # Rollup each track type
    fc_data = rollup_foreclosure_data(request)
    reo_data = rollup_reo_data(request)
    mod_data = rollup_modification_data(request)
    ss_data = rollup_shortsale_data(request)
    bpo_data = rollup_bpo_data(request)
    
    # Calculate summary
    summary = {
        'total_active_tracks': (
            fc_data['count'] + 
            reo_data['count'] + 
            mod_data['count'] + 
            ss_data['count'] + 
            bpo_data['count']
        ),
        'total_active_tasks': sum([
            sum(s['count'] for s in fc_data.get('by_status', [])),
            sum(t['count'] for t in reo_data.get('by_task_type', [])),
            sum(s['count'] for s in mod_data.get('by_status', [])),
            sum(s['count'] for s in ss_data.get('by_status', []))
        ]),
        'total_completed_tasks': 0  # TODO: Add completed task count
    }
    
    # Format for chart
    chart_data = [
        {'x': 'Foreclosure', 'y': fc_data['count']},
        {'x': 'REO', 'y': reo_data['count']},
        {'x': 'Modification', 'y': mod_data['count']},
        {'x': 'Short Sale', 'y': ss_data['count']},
        {'x': 'BPO', 'y': bpo_data['count']}
    ]
    
    return Response({
        'summary': summary,
        'by_track_type': [fc_data, reo_data, mod_data, ss_data, bpo_data],
        'chart_data': chart_data
    })
```

**Logic Module:**
```python
# reporting/logic/logic_rep_am.py
from django.db.models import Count, Q
from am_module.models import ForeClosureTrack, REOtrack, REOtask

def rollup_foreclosure_data(request):
    """
    **WHAT**: Count foreclosure tracks by status
    **WHY**: Show foreclosure pipeline breakdown
    """
    # Get active foreclosure tracks
    tracks = ForeClosureTrack.objects.filter(
        is_active=True
    ).values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    return {
        'track_type': 'foreclosure',
        'count': ForeClosureTrack.objects.filter(is_active=True).count(),
        'by_status': [
            {'status': t['status'], 'count': t['count']}
            for t in tracks
        ]
    }


def rollup_reo_data(request):
    """
    **WHAT**: Count REO tracks and tasks by task type
    **WHY**: Show REO task breakdown (Eviction, Trashout, Renovation, Marketing)
    """
    # Get active REO tracks
    track_count = REOtrack.objects.filter(is_active=True).count()
    
    # Get REO tasks by type
    tasks = REOtask.objects.filter(
        reo_track__is_active=True
    ).values('task_type').annotate(
        count=Count('id')
    ).order_by('task_type')
    
    return {
        'track_type': 'reo',
        'count': track_count,
        'by_task_type': [
            {'task_type': t['task_type'], 'count': t['count']}
            for t in tasks
        ]
    }


def rollup_modification_data(request):
    """
    **WHAT**: Count modification tracks by status
    **WHY**: Show loan modification pipeline
    """
    from am_module.models import ModificationTrack
    
    tracks = ModificationTrack.objects.filter(
        is_active=True
    ).values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    return {
        'track_type': 'modification',
        'count': ModificationTrack.objects.filter(is_active=True).count(),
        'by_status': [
            {'status': t['status'], 'count': t['count']}
            for t in tracks
        ]
    }


def rollup_shortsale_data(request):
    """
    **WHAT**: Count short sale tracks by status
    **WHY**: Show short sale pipeline
    """
    from am_module.models import ShortSaleTrack
    
    tracks = ShortSaleTrack.objects.filter(
        is_active=True
    ).values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    return {
        'track_type': 'short_sale',
        'count': ShortSaleTrack.objects.filter(is_active=True).count(),
        'by_status': [
            {'status': t['status'], 'count': t['count']}
            for t in tracks
        ]
    }


def rollup_bpo_data(request):
    """
    **WHAT**: Count BPO tracks by status
    **WHY**: Show BPO completion status
    """
    from am_module.models import BPOtrack
    
    tracks = BPOtrack.objects.filter(
        is_active=True
    ).values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    return {
        'track_type': 'bpo',
        'count': BPOtrack.objects.filter(is_active=True).count(),
        'by_status': [
            {'status': t['status'], 'count': t['count']}
            for t in tracks
        ]
    }
```

---

## Reusable Query Helper

Create a helper function to apply filters consistently:

```python
# reporting/logic/logic_rep_filters.py
from django.db.models import Q

def apply_filters(request, queryset):
    """
    **WHAT**: Apply common filters to any queryset
    **WHY**: DRY principle - reuse filter logic across all endpoints
    **HOW**: Parse query params and build Q objects
    """
    # Parse filters
    trade_ids = request.GET.get('trade_ids', '').split(',') if request.GET.get('trade_ids') else []
    statuses = request.GET.get('statuses', '').split(',') if request.GET.get('statuses') else []
    fund_id = request.GET.get('fund_id')
    entity_id = request.GET.get('entity_id')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Apply filters
    if trade_ids and trade_ids[0]:  # Check for non-empty string
        queryset = queryset.filter(trade_id__in=trade_ids)
    if statuses and statuses[0]:
        queryset = queryset.filter(trade__status__in=statuses)
    if fund_id:
        queryset = queryset.filter(fund_id=fund_id)
    if entity_id:
        queryset = queryset.filter(entity_id=entity_id)
    if start_date:
        queryset = queryset.filter(trade__bid_date__gte=start_date)
    if end_date:
        queryset = queryset.filter(trade__bid_date__lte=end_date)
    
    return queryset
```

---

## URL Routing

```python
# reporting/urls.py
from django.urls import path
from .views import (
    view_rep_filters,
    view_rep_summary,
    view_rep_trade,
    view_rep_status,
    view_rep_am
)

urlpatterns = [
    # Filter options
    path('trades/', view_rep_filters.get_trade_options, name='reporting-trades'),
    path('statuses/', view_rep_filters.get_status_options, name='reporting-statuses'),
    path('funds/', view_rep_filters.get_fund_options, name='reporting-funds'),
    path('entities/', view_rep_filters.get_entity_options, name='reporting-entities'),
    
    # Summary
    path('summary/', view_rep_summary.get_report_summary, name='reporting-summary'),
    
    # By Trade
    path('by-trade/', view_rep_trade.get_by_trade_chart, name='reporting-by-trade-chart'),
    path('by-trade/grid/', view_rep_trade.get_by_trade_grid, name='reporting-by-trade-grid'),
    
    # By Status
    path('by-status/', view_rep_status.get_by_status_chart, name='reporting-by-status-chart'),
    path('by-status/grid/', view_rep_status.get_by_status_grid, name='reporting-by-status-grid'),
    
    # Asset Management (NEW)
    path('by-am/', view_rep_am.get_am_report, name='reporting-by-am'),
    
    # By Fund (TODO)
    # path('by-fund/', ...),
    
    # By Entity (TODO)
    # path('by-entity/', ...),
]
```

**Main URLs:**
```python
# projectalphav1/urls.py
urlpatterns = [
    # ... existing patterns
    path('api/reporting/', include('reporting.urls')),
]
```

---

## Implementation Checklist

### Phase 1: Core Setup (15 min)
- [ ] Create `reporting` Django app: `python manage.py startapp reporting`
- [ ] Add `'reporting'` to `INSTALLED_APPS` in settings.py
- [ ] Create file structure following naming convention:
  - `reporting/logic/logic_rep_metrics.py`
  - `reporting/logic/logic_rep_filters.py`
  - `reporting/logic/logic_rep_am.py`
  - `reporting/views/view_rep_filters.py`
  - `reporting/views/view_rep_summary.py`
  - `reporting/views/view_rep_trade.py`
  - `reporting/views/view_rep_status.py`
  - `reporting/views/view_rep_am.py`
- [ ] Wire up URL routing in `projectalphav1/urls.py`

### Phase 2: Filter Endpoints (30 min)
- [ ] Implement `get_trade_options()` in `view_rep_filters.py`
- [ ] Implement `get_status_options()` in `view_rep_filters.py`
- [ ] Implement `get_fund_options()` placeholder in `view_rep_filters.py`
- [ ] Implement `get_entity_options()` placeholder in `view_rep_filters.py`
- [ ] Test all filter endpoints with Postman/curl

### Phase 3: Summary KPIs & Metrics (45 min)
- [ ] Create `logic_rep_metrics.py` with portfolio metric calculations:
  - [ ] `calculate_summary_metrics()` - Basic KPIs (UPB, count, LTV, delinquency)
  - [ ] `calculate_moic()` - Multiple on Invested Capital
  - [ ] `calculate_irr()` - Internal Rate of Return
  - [ ] `calculate_npv()` - Net Present Value
  - [ ] `calculate_pl()` - Profit & Loss
- [ ] Create `logic_rep_filters.py` with `apply_filters()` helper
- [ ] Implement `get_report_summary()` in `view_rep_summary.py`
- [ ] Test with various filter combinations

### Phase 4: By Trade Report (30 min)
- [ ] Implement `get_by_trade_chart()` in `view_rep_trade.py`
- [ ] Implement `get_by_trade_grid()` in `view_rep_trade.py`
- [ ] Test chart and grid endpoints

### Phase 5: By Status Report (30 min)
- [ ] Implement `get_by_status_chart()` in `view_rep_status.py`
- [ ] Implement `get_by_status_grid()` in `view_rep_status.py`
- [ ] Test chart and grid endpoints

### Phase 6: Asset Management Report (45 min) **NEW**
- [ ] Create `logic_rep_am.py` with rollup functions:
  - [ ] `rollup_foreclosure_data()` - FC tracks by status
  - [ ] `rollup_reo_data()` - REO tasks by type (Eviction, Trashout, Renovation, Marketing)
  - [ ] `rollup_modification_data()` - Mod tracks by status
  - [ ] `rollup_shortsale_data()` - SS tracks by status
  - [ ] `rollup_bpo_data()` - BPO tracks by status
- [ ] Implement `get_am_report()` in `view_rep_am.py`
- [ ] Test AM endpoint with real data

### Phase 7: By Fund & Entity (Optional - 1 hour)
- [ ] Create Fund and Entity models (if needed)
- [ ] Implement By Fund endpoints
- [ ] Implement By Entity endpoints

---

## Testing Commands

```bash
# Test filter options
curl http://localhost:8000/api/reporting/trades/
curl http://localhost:8000/api/reporting/statuses/
curl http://localhost:8000/api/reporting/funds/
curl http://localhost:8000/api/reporting/entities/

# Test summary with filters
curl "http://localhost:8000/api/reporting/summary/?trade_ids=1,2&statuses=DD,AWARDED"

# Test By Trade report
curl "http://localhost:8000/api/reporting/by-trade/?trade_ids=1"
curl "http://localhost:8000/api/reporting/by-trade/grid/?trade_ids=1"

# Test By Status report
curl "http://localhost:8000/api/reporting/by-status/"
curl "http://localhost:8000/api/reporting/by-status/grid/"

# Test Asset Management report (NEW)
curl "http://localhost:8000/api/reporting/by-am/"
curl "http://localhost:8000/api/reporting/by-am/?start_date=2024-01-01&end_date=2024-12-31"
```

---

## Frontend Integration

Once backend is ready, update the Pinia store:

```typescript
// frontend_vue/src/stores/reporting.ts

// Change this:
const response = await http.get<TradeOption[]>('/api/acq/trades/')

// To this:
const response = await http.get<TradeOption[]>('/api/reporting/trades/')
```

Update all placeholder endpoints in:
- `fetchTradeOptions()` → `/api/reporting/trades/`
- `fetchStatusOptions()` → `/api/reporting/statuses/`
- `fetchFundOptions()` → `/api/reporting/funds/`
- `fetchEntityOptions()` → `/api/reporting/entities/`
- `fetchReportSummary()` → `/api/reporting/summary/`
- `fetchChartData()` → `/api/reporting/{currentView}/`
- `fetchGridData()` → `/api/reporting/{currentView}/grid/`

---

## Performance Considerations

1. **Indexing:** Add database indexes on frequently filtered fields:
   ```python
   class Meta:
       indexes = [
           models.Index(fields=['trade_id']),
           models.Index(fields=['status']),
           models.Index(fields=['fund_id']),
           models.Index(fields=['entity_id']),
       ]
   ```

2. **Caching:** Use Django cache for filter options (they rarely change):
   ```python
   from django.core.cache import cache
   
   def get_trade_options(request):
       trades = cache.get('reporting_trade_options')
       if not trades:
           trades = list(Trade.objects.values('id', 'trade_name'))
           cache.set('reporting_trade_options', trades, 3600)  # 1 hour
       return Response(trades)
   ```

3. **Pagination:** For large datasets, add pagination to grid endpoints:
   ```python
   from rest_framework.pagination import PageNumberPagination
   ```

---

## Next Steps

1. **Start with Phase 1-2** (Setup + Filters) - Get dropdowns working first
2. **Implement Phase 3** (Summary KPIs) - Add basic metrics
3. **Test frontend integration** with real data
4. **Implement Phase 4-5** (By Trade, By Status) - Core reports
5. **Implement Phase 6** (Asset Management) - AM rollups
6. **Add Phase 7** (Fund/Entity) if needed
7. **Optimize queries** based on performance testing

---

## Summary

### ✅ What's Complete
- **Frontend:** 100% complete with simplified sidebar and multi-select filters
- **Sidebar:** Clean, organized UI with dropdown multi-selects for all filters
- **Views:** 8 report views ready (Overview, By Trade, By Status, By Fund, By Entity, Geographic, Collateral, Time Series)
- **Asset Management View:** Ready to display AM task rollups

### 🔨 What Needs Building
- **Backend API:** ~3 hours total implementation time
  - Phase 1-2: 45 min (Setup + Filters)
  - Phase 3: 45 min (Summary KPIs + Metrics)
  - Phase 4-5: 60 min (By Trade + By Status)
  - Phase 6: 45 min (Asset Management rollups)
  - Phase 7: 60 min (Optional Fund/Entity)

### 📋 File Naming Convention
- **Logic:** `logic_rep_<purpose>.py`
- **Views:** `view_rep_<purpose>.py`
- **Serializers:** `serial_rep_<purpose>.py`
- **Models:** `model_rep_<purpose>.py`

### 🎯 Key Metrics to Calculate
- Portfolio: MOIC, IRR, NPV, P&L, Duration, Cash Flow
- Asset Management: FC/REO/Mod/SS/BPO counts by status/type

### 📊 Asset Management Breakdown
- **Foreclosure:** Count by status (title_review, filing, sale_scheduled, completed)
- **REO:** Count by task type (Eviction, Trashout, Renovation, Marketing)
- **Modification:** Count by status (submitted, in_review, approved, denied)
- **Short Sale:** Count by status (listing, offer_received, bank_approval, closed)
- **BPO:** Count by status (ordered, completed)

---

**Revised Total Time:** 2-3 hours (leveraging existing models)

**Frontend Status:** ✅ 100% Complete and ready for integration

**Backend Status:** 📝 Spec complete, ready to implement
