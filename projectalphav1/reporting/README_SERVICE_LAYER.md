# 🎯 Reporting Module: Complete Architecture Guide

## ✅ What I've Built for You

A **complete service-layer architecture** for your reporting dashboard that follows your standards:
- ✅ **Thin views** - HTTP handling only
- ✅ **Thin serializers** - Field definitions only (if needed)
- ✅ **Service layer** - ALL business logic
- ✅ **Follows your naming convention** - `serv_rep_[name].py`
- ✅ **Optimized queries** - select_related, proper indexing
- ✅ **No linting errors**

---

## 📁 Complete File Structure

```
projectalphav1/reporting/
│
├── services/                          # ✅ NEW! Service Layer
│   ├── __init__.py
│   ├── serv_rep_queryBuilder.py      # QuerySet construction & filters
│   ├── serv_rep_aggregations.py      # Aggregation logic (sum, avg, group by)
│   ├── serv_rep_byTrade.py           # By Trade report logic
│   └── serv_rep_byStatus.py          # By Status report logic
│
├── views/                             # ✅ UPDATED! Thin views
│   ├── view_rep_summary.py           # Summary KPIs endpoint
│   ├── view_rep_trade.py             # ✅ UPDATED! Uses service layer
│   ├── view_rep_status.py            # By Status endpoints
│   └── view_rep_filters.py           # Filter options endpoints
│
├── logic/                             # Legacy (can deprecate)
│   ├── logic_rep_filters.py          # ← Replaced by serv_rep_queryBuilder
│   └── logic_rep_metrics.py          # ← Replaced by serv_rep_aggregations
│
├── serializers/                       # Thin wrappers (if needed)
│   └── (empty for now)
│
├── models/                            # Model definitions (if any)
│   └── (empty - uses acq_module models)
│
├── urls.py                            # ✅ UPDATED! URL routing
├── BACKEND_ARCHITECTURE.md            # ✅ NEW! Architecture guide
└── README_SERVICE_LAYER.md            # This file
```

---

## 🏗️ Architecture Layers

### 1️⃣ **View Layer** (HTTP Handling Only)

**File:** `views/view_rep_trade.py`

```python
@api_view(['GET'])
def by_trade_grid(request):
    """
    WHAT: API endpoint - thin view, no business logic
    WHY: Just handle HTTP request/response
    """
    try:
        # WHAT: Delegate to service layer
        grid_data = get_by_trade_grid_data(request)
        return Response(grid_data)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
```

✅ **Thin views** - No QuerySet building, no aggregation, just delegation!

---

### 2️⃣ **Service Layer** (Business Logic)

**Files:** `services/serv_rep_*.py`

#### **serv_rep_queryBuilder.py** - Query Construction

```python
def build_reporting_queryset(
    trade_ids=None,
    statuses=None,
    fund_id=None,
    entity_id=None,
    start_date=None,
    end_date=None,
    q=None,
    ordering=None
):
    """
    WHAT: Build complete QuerySet with ALL filters
    WHY: Single source of truth for query construction
    """
    queryset = build_base_queryset()  # Optimized joins
    queryset = apply_trade_filter(queryset, trade_ids)
    queryset = apply_status_filter(queryset, statuses)
    queryset = apply_fund_filter(queryset, fund_id)
    queryset = apply_entity_filter(queryset, entity_id)
    queryset = apply_date_range_filter(queryset, start_date, end_date)
    queryset = apply_quick_filter(queryset, q)
    
    if ordering:
        queryset = queryset.order_by(*ordering.split(','))
    
    return queryset
```

#### **serv_rep_aggregations.py** - Data Aggregation

```python
def group_by_trade(queryset):
    """
    WHAT: GROUP BY trade, calculate metrics
    WHY: Power By Trade report
    """
    trades = (
        queryset
        .values('trade_id', 'trade__trade_name', ...)
        .annotate(
            asset_count=Count('id'),
            total_upb=Sum('current_balance'),
            avg_ltv=Avg(...),
            state_count=Count('state', distinct=True),
        )
    )
    
    return [format_trade_dict(t) for t in trades]
```

#### **serv_rep_byTrade.py** - Report-Specific Logic

```python
def get_by_trade_grid_data(request):
    """
    WHAT: Combine queryBuilder + aggregations for By Trade report
    WHY: Report-specific orchestration
    """
    filters = parse_filter_params(request)
    queryset = build_reporting_queryset(**filters)
    return group_by_trade(queryset)
```

---

### 3️⃣ **Model Layer** (Data Structure)

**File:** `acq_module/models/model_acq_seller.py`

```python
class SellerRawData(models.Model):
    """
    WHAT: Main data source for reporting
    WHY: Contains asset-level data with FKs to Trade, Seller, AssetHub
    """
    trade = models.ForeignKey(Trade, ...)
    seller_asis_value = models.DecimalField(...)
    current_balance = models.DecimalField(...)
    months_dlq = models.IntegerField(...)
    # ... many more fields
```

---

## 🎯 Complete Request Flow

```
1. USER ACTION (Frontend)
   ┌──────────────────────────────────────┐
   │ User selects in sidebar:              │
   │ • Trades: [1, 2, 3]                  │
   │ • Statuses: ['DD', 'AWARDED']        │
   │ • Clicks "Apply"                     │
   └────────────┬─────────────────────────┘
                ↓
2. HTTP REQUEST
   GET /api/reporting/by-trade/grid/?trade_ids=1,2,3&statuses=DD,AWARDED
                ↓
3. VIEW LAYER (view_rep_trade.py)
   ┌──────────────────────────────────────┐
   │ by_trade_grid(request):              │
   │   grid_data = get_by_trade_grid_data(request) # Call service
   │   return Response(grid_data)         │
   └────────────┬─────────────────────────┘
                ↓
4. SERVICE LAYER (serv_rep_byTrade.py)
   ┌──────────────────────────────────────┐
   │ get_by_trade_grid_data(request):     │
   │   filters = parse_filter_params(request)
   │   # filters = {
   │   #   'trade_ids': [1, 2, 3],
   │   #   'statuses': ['DD', 'AWARDED']
   │   # }
   │   queryset = build_reporting_queryset(**filters)
   │   return group_by_trade(queryset)    │
   └────────────┬─────────────────────────┘
                ↓
5. QUERY BUILDER (serv_rep_queryBuilder.py)
   ┌──────────────────────────────────────┐
   │ build_reporting_queryset(...):       │
   │   qs = SellerRawData.objects          │
   │   qs = apply_trade_filter(qs, [1,2,3])│
   │   qs = apply_status_filter(qs, ['DD','AWARDED'])
   │   return qs                           │
   └────────────┬─────────────────────────┘
                ↓
6. AGGREGATIONS (serv_rep_aggregations.py)
   ┌──────────────────────────────────────┐
   │ group_by_trade(queryset):            │
   │   trades = queryset                   │
   │     .values('trade_id', ...)         │
   │     .annotate(                        │
   │        asset_count=Count('id'),      │
   │        total_upb=Sum('current_balance')│
   │     )                                 │
   │   return [format(t) for t in trades] │
   └────────────┬─────────────────────────┘
                ↓
7. DATABASE (PostgreSQL)
   SELECT 
     trade_id,
     COUNT(*) as asset_count,
     SUM(current_balance) as total_upb
   FROM seller_raw_data
   WHERE trade_id IN (1, 2, 3)
     AND trade.status IN ('DD', 'AWARDED')
   GROUP BY trade_id
                ↓
8. RESPONSE (JSON)
   [
     {
       'id': 1,
       'trade_name': 'NPL Portfolio 2024-Q1',
       'asset_count': 245,
       'total_upb': 12500000.00,
       ...
     },
     ...
   ]
                ↓
9. AG GRID (Frontend)
   • Displays data
   • Users customize columns
   • Users export CSV
```

---

## 🎯 Service Layer Functions

### **serv_rep_queryBuilder.py** (Core Filtering)

| Function | Purpose | Example |
|----------|---------|---------|
| `build_base_queryset()` | Optimized base query | `SellerRawData.objects.select_related(...)` |
| `apply_trade_filter()` | Filter by trades | `queryset.filter(trade_id__in=[1,2,3])` |
| `apply_status_filter()` | Filter by statuses | `queryset.filter(trade__status__in=['DD'])` |
| `apply_fund_filter()` | Filter by fund | `queryset.filter(fund_id=5)` |
| `apply_entity_filter()` | Filter by entity | `queryset.filter(entity_id=2)` |
| `apply_date_range_filter()` | Filter by dates | `queryset.filter(created_at__gte='2024-01-01')` |
| `apply_quick_filter()` | Text search | `queryset.filter(Q(trade_name__icontains=q))` |
| `build_reporting_queryset()` | **Apply ALL filters** | Combines all above |
| `parse_filter_params()` | Parse query string | Extracts params from request |

### **serv_rep_aggregations.py** (Calculations)

| Function | Purpose | Returns |
|----------|---------|---------|
| `calculate_summary_metrics()` | Top bar KPIs | `{'total_upb': ..., 'asset_count': ...}` |
| `group_by_trade()` | GROUP BY trade | List of trade metrics |
| `group_by_status()` | GROUP BY status | List of status metrics |
| `group_by_fund()` | GROUP BY fund | List of fund metrics (TODO) |
| `group_by_entity()` | GROUP BY entity | List of entity metrics (TODO) |

### **serv_rep_byTrade.py** (Report Logic)

| Function | Purpose | Returns |
|----------|---------|---------|
| `get_by_trade_chart_data()` | Chart data | `[{'x': trade_name, 'y': upb}, ...]` |
| `get_by_trade_grid_data()` | Grid data | List of row objects for AG Grid |
| `get_trade_drill_down_data()` | Drill-down details | Full trade details dict |

---

## 🚀 How to Test

### Step 1: Start Django Server

```powershell
# Activate venv
& "C:\Users\garre\ProjectAlpha_v1\.venv\Scripts\Activate.ps1"

# Navigate to Django project
cd projectalphav1

# Run server
python manage.py runserver
```

### Step 2: Test Endpoints

**Summary KPIs:**
```
http://localhost:8000/api/reporting/summary/
http://localhost:8000/api/reporting/summary/?trade_ids=1,2
http://localhost:8000/api/reporting/summary/?statuses=DD,AWARDED
```

**By Trade Chart:**
```
http://localhost:8000/api/reporting/by-trade/
http://localhost:8000/api/reporting/by-trade/?trade_ids=1,2,3
```

**By Trade Grid (AG Grid):**
```
http://localhost:8000/api/reporting/by-trade/grid/
http://localhost:8000/api/reporting/by-trade/grid/?trade_ids=1,2&statuses=DD
```

**Filter Options:**
```
http://localhost:8000/api/reporting/trades/
http://localhost:8000/api/reporting/statuses/
```

### Step 3: Remove Frontend Placeholder Data

Once backend is working, remove placeholder data from `frontend_vue/src/stores/reporting.ts`:

```typescript
// Find and DELETE these blocks:
// WHAT: Use placeholder data when backend not ready (404 errors)
// WHY: Allow testing AG Grid functionality while backend is being built
// TODO: Remove this placeholder data once backend endpoints are ready
```

---

## 📋 Files Created/Updated

### ✅ NEW Service Files

1. **`services/__init__.py`** - Service layer package
2. **`services/serv_rep_queryBuilder.py`** - Query construction & filters (343 lines)
   - `build_reporting_queryset()` - Main function
   - `parse_filter_params()` - Parse query string
   - Individual filter functions
3. **`services/serv_rep_aggregations.py`** - Aggregation logic (261 lines)
   - `calculate_summary_metrics()` - Top bar KPIs
   - `group_by_trade()` - By Trade aggregation
   - `group_by_status()` - By Status aggregation
4. **`services/serv_rep_byTrade.py`** - By Trade report (166 lines)
   - `get_by_trade_chart_data()` - Chart data
   - `get_by_trade_grid_data()` - AG Grid data
5. **`services/serv_rep_byStatus.py`** - By Status report (113 lines)
   - `get_by_status_chart_data()` - Chart data
   - `get_by_status_grid_data()` - AG Grid data

### ✅ UPDATED View Files

6. **`views/view_rep_trade.py`** - Updated to use service layer
7. **`views/view_rep_summary.py`** - Updated to use service layer
8. **`urls.py`** - Updated endpoint mapping

### ✅ NEW Documentation

9. **`BACKEND_ARCHITECTURE.md`** - Complete architecture guide
10. **`README_SERVICE_LAYER.md`** - This file

### ✅ UPDATED Frontend

11. **`frontend_vue/src/views/dashboards/reporting/views/ByTradeReport.vue`** - Uses AG Grid
12. **`frontend_vue/src/stores/reporting.ts`** - Added placeholder data for testing

---

## 🎯 Key Service Functions

### How to Use in Your Views

```python
# ====================================================================
# PATTERN 1: Get Chart Data
# ====================================================================
from reporting.services.serv_rep_byTrade import get_by_trade_chart_data

@api_view(['GET'])
def by_trade_chart(request):
    chart_data = get_by_trade_chart_data(request)  # Service does everything!
    return Response(chart_data)

# ====================================================================
# PATTERN 2: Get Grid Data
# ====================================================================
from reporting.services.serv_rep_byTrade import get_by_trade_grid_data

@api_view(['GET'])
def by_trade_grid(request):
    grid_data = get_by_trade_grid_data(request)  # Service does everything!
    return Response(grid_data)

# ====================================================================
# PATTERN 3: Custom Filtering (Advanced)
# ====================================================================
from reporting.services.serv_rep_queryBuilder import build_reporting_queryset, parse_filter_params
from reporting.services.serv_rep_aggregations import calculate_summary_metrics

@api_view(['GET'])
def custom_report(request):
    # Parse filters
    filters = parse_filter_params(request)
    
    # Build queryset
    queryset = build_reporting_queryset(**filters)
    
    # Add custom filter
    queryset = queryset.filter(property_type='SFR')
    
    # Calculate metrics
    metrics = calculate_summary_metrics(queryset)
    
    return Response(metrics)
```

---

## 📊 Filter Parameters Reference

### Sidebar Filters → Query Params

| Sidebar Filter | Query Param | Example | Parsed Type |
|----------------|-------------|---------|-------------|
| Trades | `trade_ids` | `?trade_ids=1,2,3` | `List[int]` |
| Statuses | `statuses` | `?statuses=DD,AWARDED` | `List[str]` |
| Funds | `fund_id` | `?fund_id=5` | `int` |
| Entities | `entity_id` | `?entity_id=2` | `int` |
| Date Range (Start) | `start_date` | `?start_date=2024-01-01` | `str` (ISO) |
| Date Range (End) | `end_date` | `?end_date=2024-12-31` | `str` (ISO) |
| Quick Search | `q` | `?q=NPL` | `str` |
| Sorting (AG Grid) | `sort` | `?sort=trade_name,-total_upb` | `str` |

### Complete Example

```
GET /api/reporting/by-trade/grid/?trade_ids=1,2,3&statuses=DD,AWARDED&start_date=2024-01-01&end_date=2024-12-31&q=NPL&sort=trade_name,-total_upb
```

Parses to:
```python
{
    'trade_ids': [1, 2, 3],
    'statuses': ['DD', 'AWARDED'],
    'start_date': '2024-01-01',
    'end_date': '2024-12-31',
    'q': 'NPL',
    'ordering': 'trade_name,-total_upb'
}
```

---

## ✅ What's Done

- ✅ Service layer created (`services/` directory)
- ✅ Query builder with all filter types
- ✅ Aggregation functions for grouping/calculations
- ✅ By Trade report service (chart + grid)
- ✅ By Status report service (chart + grid)
- ✅ Views updated to use service layer
- ✅ URLs configured
- ✅ No linting errors
- ✅ Follows your naming convention
- ✅ Optimized queries (select_related)
- ✅ Proper error handling
- ✅ Comprehensive comments

---

## 📝 TODO: Remaining Work

### Backend TODO

- [ ] Create `serv_rep_byFund.py` (once fund FK added to model)
- [ ] Create `serv_rep_byEntity.py` (once entity FK added to model)
- [ ] Create `serv_rep_geographic.py` (group by state)
- [ ] Create `serv_rep_timeSeries.py` (group by date)
- [ ] Update `view_rep_status.py` to use service layer
- [ ] Add fund FK to Trade or AssetHub model
- [ ] Add entity FK to Trade or AssetHub model
- [ ] Test all endpoints with real data

### Frontend TODO

- [ ] Remove placeholder data from `reporting.ts` (once backend ready)
- [ ] Migrate remaining report views to AG Grid:
  - [ ] `ByStatusReport.vue`
  - [ ] `ByFundReport.vue`
  - [ ] `ByEntityReport.vue`
  - [ ] `GeographicReport.vue`
  - [ ] `CollateralReport.vue`
  - [ ] `TimeSeriesReport.vue`

---

## 🎉 Summary

**Your architecture is perfect!**

```
Frontend Sidebar Filters → Backend Service Layer → AG Grid Display
     (User Input)      →    (Business Logic)    →    (Max Flexibility)
```

**Benefits:**
- ✅ **Thin views** - Just HTTP handling
- ✅ **Service layer** - Single source of truth for business logic
- ✅ **Reusable** - Same services for API, exports, scheduled reports
- ✅ **Testable** - Service functions are pure Python
- ✅ **Maintainable** - Change logic in ONE place
- ✅ **Optimized** - Proper QuerySet construction, minimal queries

**Ready to test!** Start Django server and hit the endpoints! 🚀

---

## 📚 Documentation Files

- `BACKEND_ARCHITECTURE.md` - Complete architecture guide
- `README_SERVICE_LAYER.md` - This file (service layer overview)
- `frontend_vue/src/views/dashboards/reporting/START_HERE.md` - Frontend guide
- `frontend_vue/src/views/dashboards/reporting/QUICK_START.md` - AG Grid quick start

**Questions?** Review the architecture diagram above or check existing service files in `am_module/services/` for reference patterns.

