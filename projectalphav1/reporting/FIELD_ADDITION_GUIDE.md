# 📋 Field Addition Guide - Step by Step

## 🎯 How to Add a New Field to Reporting

Follow these steps **in order** to add any field to your AG Grid reporting.

---

## 📝 **Example: Adding "Property Type" Field**

Let's say you want to add **Property Type** to the By Trade grid.

---

## **Step 1: Check if Field Needs Annotation** ⚙️

**File:** `services/serv_rep_queryBuilder.py`

### **Question:** Is the field on SellerRawData directly?

**✅ YES (field is on SellerRawData):**
- Fields like: `property_type`, `street_address`, `city`, `state`, `current_balance`
- **Skip to Step 2** - No annotation needed!

**❌ NO (field is on related model):**
- Fields like: `servicer_id` (on AssetIdHub), `servicer_current_balance` (on ServicerLoanData)
- **Add annotation:**

```python
# In build_base_queryset() function, in the .annotate() section:
queryset = queryset.annotate(
    # ... existing annotations ...
    
    # 🎯 YOUR NEW FIELD - Add here!
    property_type_annotated=F('property_type'),  # If already on SellerRawData
    # OR
    servicer_fc_status=F('asset_hub__servicer_data__fc_status'),  # From related model
)
```

**Patterns:**
- From SellerRawData: `F('field_name')`
- From AssetIdHub: `F('asset_hub__field_name')`
- From ServicerLoanData: `F('asset_hub__servicer_data__field_name')`
- From Trade: `F('trade__field_name')`
- From Seller: `F('trade__seller__field_name')`

---

## **Step 2: Add to Aggregation (if needed)** 📊

**File:** `services/serv_rep_aggregations.py`

### **Question:** Do you need to aggregate this field (sum, avg, count)?

**✅ YES (need to aggregate):**

```python
# In group_by_trade() function, in the .annotate() section:
trades = (
    queryset
    .values('trade_id', 'trade__trade_name', ...)
    .annotate(
        # ... existing aggregations ...
        
        # 🎯 YOUR AGGREGATION - Add here!
        # Count unique property types in this trade
        property_type_count=Count('property_type', distinct=True),
        
        # OR count assets of specific type
        sfr_count=Count('id', filter=Q(property_type='SFR')),
    )
)
```

**Common aggregations:**
- `Count('field')` - Count rows
- `Sum('field')` - Sum values
- `Avg('field')` - Average
- `Max('field')` - Maximum
- `Min('field')` - Minimum
- `Count('field', distinct=True)` - Count unique values
- `Count('id', filter=Q(condition))` - Conditional count

**❌ NO (just want to include field as-is):**

```python
# In group_by_trade() function, in the .values() section:
trades = (
    queryset
    .values(
        'trade_id',
        'trade__trade_name',
        # ... existing fields ...
        
        # 🎯 YOUR FIELD - Add here to include in GROUP BY!
        'property_type',  # Include in grouping
    )
    .annotate(...)
)
```

---

## **Step 3: Add to Results Dict** 📦

**File:** `services/serv_rep_aggregations.py`

**In the `group_by_trade()` function, in the results.append({...}) section:**

```python
results.append({
    # ... existing fields ...
    
    # 🎯 YOUR FIELD - Add here!
    # For aggregated field:
    'property_type_count': trade['property_type_count'] or 0,
    
    # OR for grouped field:
    'property_type': trade['property_type'] or '',
    
    # OR for nested field:
    'seller': trade['trade__seller__name'] or '',
})
```

---

## **Step 4: Define in Serializer** 📋

**File:** `serializers/serial_rep_byTrade.py`

**In the `TradeGridSerializer` class:**

```python
class TradeGridSerializer(serializers.Serializer):
    # ... existing fields ...
    
    # 🎯 YOUR FIELD - Add here!
    property_type = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Property type (SFR, Condo, etc.)"
    )
    
    # OR for count:
    property_type_count = serializers.IntegerField(
        required=False,
        help_text="Number of unique property types"
    )
```

**Field type reference:**
- `CharField()` - Text
- `IntegerField()` - Whole numbers
- `FloatField()` - Decimals
- `DecimalField(max_digits=15, decimal_places=2)` - Money (precise)
- `DateField()` - Date only
- `DateTimeField()` - Date + time
- `BooleanField()` - True/False

---

## **Step 5: Add to Frontend AG Grid** 🖥️

**File:** `frontend_vue/src/views/dashboards/reporting/views/ByTradeReport.vue`

**In the `columnDefs` array:**

```typescript
const columnDefs = ref<ColDef[]>([
  // ... existing columns ...
  
  // 🎯 YOUR COLUMN - Add here!
  {
    headerName: 'Property Type',
    field: 'property_type',  // Must match serializer field name!
    width: 140,
    // Optional: Add BadgeCell for enum fields
    cellRenderer: BadgeCell as any,
    cellRendererParams: {
      mode: 'enum',
      enumMap: propertyTypeEnumMap,
    },
  },
])
```

---

## ✅ **Complete Example: Adding "Average Interest Rate"**

### **Step 1: Annotation** (if from related model)

```python
# serv_rep_queryBuilder.py - build_base_queryset()
queryset = queryset.annotate(
    servicer_interest_rate=F('asset_hub__servicer_data__interest_rate'),
)
```

### **Step 2: Aggregation**

```python
# serv_rep_aggregations.py - group_by_trade()
trades = (
    queryset
    .values('trade_id', ...)
    .annotate(
        avg_interest_rate=Avg('servicer_interest_rate'),  # ← New!
    )
)
```

### **Step 3: Results Dict**

```python
# serv_rep_aggregations.py - group_by_trade() results
results.append({
    # ... existing ...
    'avg_interest_rate': float(trade['avg_interest_rate'] or 0),  # ← New!
})
```

### **Step 4: Serializer**

```python
# serial_rep_byTrade.py - TradeGridSerializer
class TradeGridSerializer(serializers.Serializer):
    # ... existing ...
    avg_interest_rate = serializers.FloatField(required=False)  # ← New!
```

### **Step 5: Frontend Column**

```typescript
// ByTradeReport.vue - columnDefs
{
  headerName: 'Avg Interest Rate',
  field: 'avg_interest_rate',  // ← Matches serializer!
  width: 150,
  valueFormatter: percentFormatter,
}
```

**Done! ✅** Users can now see and customize this column in AG Grid!

---

## 🎯 **Quick Reference: Where to Add What**

| What You Want | Where to Add It | File |
|---------------|-----------------|------|
| Field from related model | Annotation in `build_base_queryset()` | `serv_rep_queryBuilder.py` |
| Aggregation (sum, avg, count) | `.annotate()` in `group_by_trade()` | `serv_rep_aggregations.py` |
| Include in GROUP BY | `.values()` in `group_by_trade()` | `serv_rep_aggregations.py` |
| Include in response | `results.append({...})` | `serv_rep_aggregations.py` |
| Define field type | Class field in serializer | `serial_rep_byTrade.py` |
| Display in AG Grid | Column def | `ByTradeReport.vue` |

---

## 💡 **Common Field Additions**

### **Address Fields** (already on SellerRawData)

```python
# Step 2: Add to .values() (no aggregation needed)
.values('street_address', 'city', 'state', 'zip')

# Step 3: Include in results
'street_address': trade['street_address'] or '',
'city': trade['city'] or '',
'state': trade['state'] or '',

# Step 4: Serializer
street_address = serializers.CharField(required=False)
city = serializers.CharField(required=False)
state = serializers.CharField(required=False)
```

### **Servicer Fields** (from ServicerLoanData)

```python
# Step 1: Annotate in queryBuilder
servicer_investor_id=F('asset_hub__servicer_data__investor_id'),
servicer_fc_status=F('asset_hub__servicer_data__fc_status'),

# Step 2: Add to .values() to include in GROUP BY
.values('servicer_investor_id', 'servicer_fc_status')

# OR aggregate if needed
.annotate(fc_count=Count('id', filter=Q(servicer_fc_status__isnull=False)))

# Step 3: Include in results
'servicer_investor_id': trade['servicer_investor_id'] or '',
'fc_count': trade['fc_count'] or 0,

# Step 4: Serializer
servicer_investor_id = serializers.CharField(required=False)
fc_count = serializers.IntegerField(required=False)
```

### **Count Fields** (conditional counts)

```python
# Step 2: Add to .annotate()
.annotate(
    fc_count=Count('id', filter=Q(fc_flag=True)),
    bk_count=Count('id', filter=Q(bk_flag=True)),
    occupied_count=Count('id', filter=Q(occupancy='O')),
)

# Step 3: Include in results
'fc_count': trade['fc_count'] or 0,

# Step 4: Serializer
fc_count = serializers.IntegerField(required=False)
```

---

## 🎓 **Pro Tips**

### **Tip 1: Use Coalesce for Null Safety**

```python
# Good ✅
total_upb=Coalesce(Sum('current_balance'), 0.0, output_field=DecimalField())

# Bad ❌ (will error if no rows)
total_upb=Sum('current_balance')
```

### **Tip 2: Always Set required=False for Optional Fields**

```python
# Good ✅
avg_interest_rate = serializers.FloatField(required=False, allow_null=True)

# Bad ❌ (will error if field missing)
avg_interest_rate = serializers.FloatField()
```

### **Tip 3: Match Field Names Exactly**

```python
# Service returns:
{'property_type': 'SFR'}

# Serializer must match:
property_type = serializers.CharField()  # ✅ Matches!

# Frontend must match:
{ field: 'property_type' }  # ✅ Matches!
```

---

## ✅ **Checklist for Adding a Field**

- [ ] **Step 1:** Add annotation in `queryBuilder` (if from related model)
- [ ] **Step 2:** Add to aggregation in `aggregations` (if calculating)
- [ ] **Step 3:** Add to results dict in `aggregations`
- [ ] **Step 4:** Define in serializer
- [ ] **Step 5:** Add column to frontend AG Grid
- [ ] **Test:** Hit API endpoint to verify field appears
- [ ] **Test:** Check AG Grid displays field correctly

---

## 🎉 **Summary**

**The 5-Step Process:**
1. Annotate (if related model) → `queryBuilder`
2. Aggregate (if calculating) → `aggregations`
3. Include in results → `aggregations`
4. Define field → `serializer` ✅ (THE source of truth)
5. Add column → `frontend`

**Your serializer is the API contract!** Everything else is preparation to populate those fields. 🎯

