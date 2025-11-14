# 🏗️ Reporting Backend Architecture

## ✅ Architecture Pattern (Your Standard)

```
┌─────────────────────────────────────────────────────────────────┐
│  FRONTEND (Vue + AG Grid)                                       │
│  • Sidebar filters (Trades, Statuses, Funds, Entities, Dates)  │
│  • User clicks "Apply"                                          │
│  • Axios HTTP call to backend                                   │
└──────────┬──────────────────────────────────────────────────────┘
           │
           ↓ HTTP GET with query params
           │
┌──────────▼──────────────────────────────────────────────────────┐
│  VIEW LAYER (Thin - No business logic)                          │
│  File: projectalphav1/reporting/views/view_rep_[name].py       │
│                                                                  │
│  • Parse request                                                │
│  • Call service layer                                           │
│  • Return Response                                              │
└──────────┬──────────────────────────────────────────────────────┘
           │
           ↓ Function call
           │
┌──────────▼──────────────────────────────────────────────────────┐
│  SERVICE LAYER (Business Logic)                                 │
│  File: projectalphav1/reporting/services/serv_rep_[name].py    │
│                                                                  │
│  • Parse filter params                                          │
│  • Build QuerySet with filters                                  │
│  • Aggregate data (sum, avg, count, group by)                  │
│  • Format results for frontend                                  │
└──────────┬──────────────────────────────────────────────────────┘
           │
           ↓ QuerySet operations
           │
┌──────────▼──────────────────────────────────────────────────────┐
│  MODEL LAYER (Data Access)                                      │
│  File: projectalphav1/acq_module/models/model_acq_seller.py    │
│                                                                  │
│  • SellerRawData (main reporting source)                       │
│  • Trade (ForeignKey relationship)                              │
│  • Seller (ForeignKey via Trade)                                │
│  • AssetHub (ForeignKey for master asset data)                  │
└──────────┬──────────────────────────────────────────────────────┘
           │
           ↓ SQL Query
           │
┌──────────▼──────────────────────────────────────────────────────┐
│  DATABASE (PostgreSQL/Neon)                                     │
│  • Returns filtered, aggregated data                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 File Structure (Your Naming Convention)

```
projectalphav1/reporting/
├── services/                          # ← NEW! Service layer
│   ├── __init__.py
│   ├── serv_rep_queryBuilder.py      # QuerySet construction with filters
│   ├── serv_rep_aggregations.py      # Aggregation logic (sum, avg, group by)
│   ├── serv_rep_byTrade.py           # By Trade specific logic
│   ├── serv_rep_byStatus.py          # By Status specific logic
│   ├── serv_rep_byFund.py            # By Fund specific logic (TODO)
│   └── serv_rep_byEntity.py          # By Entity specific logic (TODO)
│
├── views/                             # Thin views (HTTP handlers only)
│   ├── view_rep_summary.py           # Summary KPIs endpoint
│   ├── view_rep_trade.py             # By Trade endpoints
│   ├── view_rep_status.py            # By Status endpoints
│   └── view_rep_filters.py           # Filter options endpoints
│
├── serializers/                       # Thin wrappers (if needed)
│   └── serial_rep_[name].py          # Only if complex nested data
│
├── logic/                             # Legacy - migrate to services/
│   ├── logic_rep_filters.py          # ← Migrate to serv_rep_queryBuilder.py
│   └── logic_rep_metrics.py          # ← Migrate to serv_rep_aggregations.py
│
└── urls.py                            # URL routing
```

**FILE NAMING CONVENTION:**
- `serv_` = Services folder
- `_rep_` = Reporting module
- `byTrade` / `queryBuilder` / `aggregations` = Descriptive name

---

## 🔄 Data Flow Example

### Example: User filters by Trade and Status

```python
# 1. FRONTEND REQUEST
# User selects:
#    Trades: [1, 2, 3]
#    Statuses: ['DD', 'AWARDED']
# Clicks "Apply"
#
# Axios sends:
GET /api/reporting/by-trade/grid/?trade_ids=1,2,3&statuses=DD,AWARDED

# ────────────────────────────────────────────────────────────────

# 2. VIEW LAYER (view_rep_trade.py)
# WHAT: Thin view - just delegate to service
@api_view(['GET'])
def by_trade_grid(request):
    grid_data = get_by_trade_grid_data(request)  # Call service
    return Response(grid_data)

# ────────────────────────────────────────────────────────────────

# 3. SERVICE LAYER (serv_rep_byTrade.py)
# WHAT: Business logic - parse filters, build queryset, aggregate
def get_by_trade_grid_data(request):
    # Parse query params
    filters = parse_filter_params(request)
    # filters = {
    #     'trade_ids': [1, 2, 3],
    #     'statuses': ['DD', 'AWARDED']
    # }
    
    # Build filtered queryset
    queryset = build_reporting_queryset(**filters)
    
    # Group by trade and calculate metrics
    trade_metrics = group_by_trade(queryset)
    
    return trade_metrics

# ────────────────────────────────────────────────────────────────

# 4. QUERY BUILDER (serv_rep_queryBuilder.py)
# WHAT: Build optimized QuerySet
def build_reporting_queryset(trade_ids=None, statuses=None, ...):
    # Start with optimized base query
    queryset = SellerRawData.objects.select_related('trade', 'seller')
    
    # Apply trade filter
    if trade_ids:
        queryset = queryset.filter(trade_id__in=trade_ids)
    
    # Apply status filter
    if statuses:
        queryset = queryset.filter(trade__status__in=statuses)
    
    return queryset
    # Returns: QuerySet[SellerRawData] filtered to trades 1,2,3 with status DD or AWARDED

# ────────────────────────────────────────────────────────────────

# 5. AGGREGATIONS (serv_rep_aggregations.py)
# WHAT: Group and aggregate the data
def group_by_trade(queryset):
    trades = (
        queryset
        .values('trade_id', 'trade__trade_name', ...)
        .annotate(
            asset_count=Count('id'),
            total_upb=Sum('current_balance'),
            avg_ltv=Avg(...),
        )
    )
    
    return [
        {
            'id': t['trade_id'],
            'trade_name': t['trade__trade_name'],
            'asset_count': t['asset_count'],
            'total_upb': float(t['total_upb']),
            ...
        }
        for t in trades
    ]
    # Returns: List of dicts with aggregated trade data

# ────────────────────────────────────────────────────────────────

# 6. DATABASE QUERY (PostgreSQL)
# Django ORM generates SQL:
SELECT 
    trade_id,
    trade.trade_name,
    COUNT(id) as asset_count,
    SUM(current_balance) as total_upb,
    AVG(current_balance * 100.0 / seller_asis_value) as avg_ltv
FROM seller_raw_data
JOIN trade ON seller_raw_data.trade_id = trade.id
WHERE trade_id IN (1, 2, 3)
  AND trade.status IN ('DD', 'AWARDED')
GROUP BY trade_id, trade.trade_name

# ────────────────────────────────────────────────────────────────

# 7. RESPONSE BACK TO FRONTEND
[
    {
        'id': 1,
        'trade_name': 'NPL Portfolio 2024-Q1',
        'asset_count': 245,
        'total_upb': 12500000.00,
        'avg_ltv': 78.5,
        'status': 'DD',
        ...
    },
    {
        'id': 2,
        'trade_name': 'RPL Acquisition 2024-Q2',
        'asset_count': 156,
        'total_upb': 8900000.00,
        'avg_ltv': 65.2,
        'status': 'AWARDED',
        ...
    }
]

# ────────────────────────────────────────────────────────────────

# 8. FRONTEND (AG Grid)
# - Receives data
# - Displays in AG Grid
# - Users customize columns
# - Users export to CSV
```

---

## 📋 Service Layer Responsibilities

### **serv_rep_queryBuilder.py** (Core)
**WHAT**: Build and filter QuerySets  
**Functions**:
- `build_base_queryset()` - Optimized base query with joins
- `apply_trade_filter()` - Filter by trade IDs
- `apply_status_filter()` - Filter by statuses
- `apply_entity_filter()` - Filter by entity (now the single ownership filter)
- `apply_date_range_filter()` - Filter by date range
- `build_reporting_queryset()` - Apply ALL filters
- `parse_filter_params()` - Parse query params

### **serv_rep_aggregations.py** (Calculations)
**WHAT**: Aggregate and group data  
**Functions**:
- `calculate_summary_metrics()` - Top bar KPIs
- `group_by_trade()` - GROUP BY trade with metrics
- `group_by_status()` - GROUP BY status with metrics
- `group_by_entity()` - GROUP BY entity (TODO)

### **serv_rep_byTrade.py** (Report-Specific)
**WHAT**: By Trade report business logic  
**Functions**:
- `get_by_trade_chart_data()` - Chart data
- `get_by_trade_grid_data()` - Grid data
- `get_trade_drill_down_data()` - Drill-down details

### **serv_rep_byStatus.py** (Report-Specific)
**WHAT**: By Status report business logic  
**Functions**:
- `get_by_status_chart_data()` - Chart data
- `get_by_status_grid_data()` - Grid data

---

## 🎯 Why This Architecture?

### ✅ Separation of Concerns
- **Views** = HTTP handlers (request/response only)
- **Services** = Business logic (filtering, aggregation)
- **Serializers** = Data transformation (thin wrappers)
- **Models** = Data structure

### ✅ Testability
```python
# Easy to unit test services without HTTP mocking
from reporting.services.serv_rep_aggregations import group_by_trade

queryset = SellerRawData.objects.filter(trade_id=1)
result = group_by_trade(queryset)
assert len(result) == 1
assert result[0]['asset_count'] > 0
```

### ✅ Reusability
```python
# Same service functions used by multiple views
from reporting.services.serv_rep_byTrade import get_by_trade_grid_data

# Use in API endpoint
def by_trade_api(request):
    return Response(get_by_trade_grid_data(request))

# Use in export function
def export_trade_report(request):
    data = get_by_trade_grid_data(request)
    return generate_excel(data)

# Use in scheduled report
def nightly_trade_report():
    # Mock request with filters
    data = get_by_trade_grid_data(mock_request)
    send_email(data)
```

### ✅ Maintainability
- All filter logic in ONE place (`serv_rep_queryBuilder.py`)
- All aggregation logic in ONE place (`serv_rep_aggregations.py`)
- Easy to add new report types (copy pattern)
- Easy to modify calculations (change one service file)

---

## 🔧 How to Add a New Report View

### Example: Add "By Property Type" Report

**Step 1: Create Service File**
```python
# projectalphav1/reporting/services/serv_rep_byPropertyType.py

from .serv_rep_queryBuilder import build_reporting_queryset, parse_filter_params

def get_by_property_type_chart_data(request):
    filters = parse_filter_params(request)
    queryset = build_reporting_queryset(**filters)
    
    # Group by property type
    results = (
        queryset
        .values('property_type')
        .annotate(
            asset_count=Count('id'),
            total_upb=Sum('current_balance'),
        )
    )
    
    return [{'x': r['property_type'], 'y': r['total_upb']} for r in results]
```

**Step 2: Create View File**
```python
# projectalphav1/reporting/views/view_rep_propertyType.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from reporting.services.serv_rep_byPropertyType import get_by_property_type_chart_data

@api_view(['GET'])
def by_property_type_chart(request):
    chart_data = get_by_property_type_chart_data(request)
    return Response(chart_data)
```

**Step 3: Add URL Route**
```python
# projectalphav1/reporting/urls.py

from .views.view_rep_propertyType import by_property_type_chart

urlpatterns = [
    path('by-property-type/', by_property_type_chart, name='by-property-type-chart'),
]
```

**Step 4: Create Frontend View**
```vue
<!-- frontend_vue/src/views/dashboards/reporting/views/ByPropertyTypeReport.vue -->
<template>
  <ReportingAgGrid
    :column-defs="columnDefs"
    :row-data="gridData"
    @row-clicked="handleRowClick"
  />
</template>
```

**Done!** ✅

---

## 📊 Service Layer Functions Reference

### Query Builder Functions

| Function | Purpose | Returns |
|----------|---------|---------|
| `build_base_queryset()` | Create optimized base QuerySet with joins | `QuerySet[SellerRawData]` |
| `apply_trade_filter()` | Filter by trade IDs | Filtered QuerySet |
| `apply_status_filter()` | Filter by statuses | Filtered QuerySet |
| `apply_fund_filter()` | Filter by fund | Filtered QuerySet |
| `apply_entity_filter()` | Filter by entity | Filtered QuerySet |
| `apply_date_range_filter()` | Filter by date range | Filtered QuerySet |
| `build_reporting_queryset()` | Apply ALL filters | Filtered QuerySet |
| `parse_filter_params()` | Parse request query params | Dict of filters |

### Aggregation Functions

| Function | Purpose | Returns |
|----------|---------|---------|
| `calculate_summary_metrics()` | Top bar KPIs | Dict with totals/averages |
| `group_by_trade()` | GROUP BY trade | List of trade metrics |
| `group_by_status()` | GROUP BY status | List of status metrics |
| `group_by_fund()` | GROUP BY fund | List of fund metrics |
| `group_by_entity()` | GROUP BY entity | List of entity metrics |

---

## 🎯 Filter Parameters

### Query String Format

```
GET /api/reporting/by-trade/grid/?trade_ids=1,2,3&statuses=DD,AWARDED&start_date=2024-01-01
```

### Parsed Parameters

```python
{
    'trade_ids': [1, 2, 3],              # List[int]
    'statuses': ['DD', 'AWARDED'],       # List[str]
    'entity_ids': [2, 5],                # List[int]
    'start_date': '2024-01-01',          # str | None
    'end_date': '2024-12-31',            # str | None
    'q': 'search text',                  # str | None (quick search)
    'ordering': 'trade_name,-total_upb', # str | None (comma-separated)
}
```

---

## 🛣️ URL Routing

### Current Endpoints

```python
# projectalphav1/reporting/urls.py

urlpatterns = [
    # Summary KPIs (top bar)
    path('summary/', report_summary, name='report-summary'),
    
    # By Trade Report
    path('by-trade/', by_trade_chart, name='by-trade-chart'),
    path('by-trade/grid/', by_trade_grid, name='by-trade-grid'),
    
    # By Status Report
    path('by-status/', by_status_chart, name='by-status-chart'),
    path('by-status/grid/', by_status_grid, name='by-status-grid'),
    
    # Filter Options
    path('trades/', get_trade_options, name='trade-options'),
    path('statuses/', get_status_options, name='status-options'),
    path('entities/', get_entity_options, name='entity-options'),
]
```

### Expected Frontend Calls

```javascript
// Get summary KPIs
GET /api/reporting/summary/?trade_ids=1,2,3&statuses=DD,AWARDED

// Get chart data
GET /api/reporting/by-trade/?trade_ids=1,2,3&statuses=DD,AWARDED

// Get grid data
GET /api/reporting/by-trade/grid/?trade_ids=1,2,3&statuses=DD,AWARDED

// Get filter options
GET /api/reporting/trades/        // List of all trades
GET /api/reporting/statuses/      // List of all statuses
GET /api/reporting/partnerships/  // List of FundLegalEntity partnerships (fund wrappers, GP LLCs, SPVs)
```

---

## 💡 Best Practices (Your Standards)

### ✅ DO: Keep Views Thin
```python
# GOOD ✅
@api_view(['GET'])
def by_trade_chart(request):
    chart_data = get_by_trade_chart_data(request)  # Service layer
    return Response(chart_data)

# BAD ❌
@api_view(['GET'])
def by_trade_chart(request):
    # Don't put business logic in views!
    queryset = SellerRawData.objects.filter(...)
    trades = queryset.values('trade_id').annotate(...)
    result = [{'x': t['name'], 'y': t['upb']} for t in trades]
    return Response(result)
```

### ✅ DO: Keep Serializers Thin
```python
# GOOD ✅
class TradeReportSerializer(serializers.Serializer):
    # Just field definitions - no business logic
    trade_name = serializers.CharField()
    total_upb = serializers.DecimalField(max_digits=15, decimal_places=2)

# BAD ❌
class TradeReportSerializer(serializers.Serializer):
    # Don't calculate metrics in serializers!
    def get_total_upb(self, obj):
        return sum(asset.current_balance for asset in obj.assets.all())
```

### ✅ DO: Put Business Logic in Services
```python
# GOOD ✅ - in serv_rep_byTrade.py
def get_by_trade_grid_data(request):
    filters = parse_filter_params(request)
    queryset = build_reporting_queryset(**filters)
    return group_by_trade(queryset)
```

### ✅ DO: Use Django ORM Efficiently
```python
# GOOD ✅ - Single query with aggregation
queryset.values('trade_id').annotate(
    total_upb=Sum('current_balance'),
    asset_count=Count('id')
)

# BAD ❌ - N+1 queries
for trade in Trade.objects.all():
    total_upb = sum(a.current_balance for a in trade.assets.all())
```

---

## 🚀 Next Steps

### 1. Update URLs (if needed)
Check `projectalphav1/reporting/urls.py` and ensure endpoints are mapped:
```python
from .views.view_rep_trade import by_trade_chart, by_trade_grid
from .views.view_rep_summary import report_summary

urlpatterns = [
    path('summary/', report_summary),
    path('by-trade/', by_trade_chart),
    path('by-trade/grid/', by_trade_grid),
]
```

### 2. Test Endpoints
```bash
# Activate venv
& "C:\Users\garre\ProjectAlpha_v1\.venv\Scripts\Activate.ps1"

# Run Django server
python projectalphav1\manage.py runserver

# Test endpoints in browser or Postman:
# http://localhost:8000/api/reporting/by-trade/grid/
# http://localhost:8000/api/reporting/by-trade/grid/?trade_ids=1,2
```

### 3. Remove Placeholder Data from Frontend
Once backend is working, remove placeholder data from `reporting.ts`:
```typescript
// In src/stores/reporting.ts
// DELETE the placeholder data blocks marked with TODO
```

### 4. Create Additional Service Files
Copy the pattern for:
- `serv_rep_byFund.py` (once fund FK exists)
- `serv_rep_byEntity.py` (once entity FK exists)
- `serv_rep_geographic.py`
- `serv_rep_timeSeries.py`

---

## ✅ Summary

**You now have:**
✅ Proper service layer structure  
✅ Separation of concerns (View → Service → Model)  
✅ Thin views (HTTP handling only)  
✅ Thin serializers (field definitions only)  
✅ Business logic in services (filtering, aggregation)  
✅ Reusable query builders  
✅ Follows your naming convention (`serv_rep_[name].py`)  

**Next:**
1. Update `reporting/urls.py` to map endpoints
2. Test endpoints with Django runserver
3. Remove frontend placeholder data
4. Build remaining report service files

**Your architecture is solid!** 🎉

