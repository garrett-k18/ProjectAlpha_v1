# ⚡ Quick Field Addition Reference

## 🎯 **TL;DR - Where to Add Fields**

```
Want to add a field to AG Grid? Follow this order:

1. serv_rep_queryBuilder.py   → Annotate (if from related model)
2. serv_rep_aggregations.py   → Aggregate (if calculating sum/avg/count)
3. serv_rep_aggregations.py   → Include in results dict
4. serial_rep_byTrade.py      → Define field ✅ (SOURCE OF TRUTH)
5. ByTradeReport.vue          → Add column to AG Grid
```

---

## 📍 **Exact Locations (Copy & Paste)**

### **1. Annotate Field** (if from related model)

**File:** `services/serv_rep_queryBuilder.py`  
**Line:** ~75 (in `build_base_queryset()` function)  
**Section:** Look for comment `# 🎯 ADD YOUR OWN FIELDS HERE`

```python
queryset = queryset.annotate(
    # Existing annotations...
    
    # 🎯 ADD HERE:
    your_field_name=F('asset_hub__servicer_data__field_name'),
)
```

---

### **2. Aggregate Field** (if calculating)

**File:** `services/serv_rep_aggregations.py`  
**Line:** ~200 (in `group_by_trade()` function)  
**Section:** Look for comment `# 🎯 ADD YOUR OWN AGGREGATIONS HERE`

```python
.annotate(
    # Existing aggregations...
    
    # 🎯 ADD HERE:
    your_metric=Sum('your_field_name'),
    your_count=Count('id', filter=Q(condition)),
)
```

---

### **3. Include in Results**

**File:** `services/serv_rep_aggregations.py`  
**Line:** ~275 (in `group_by_trade()` results section)  
**Section:** Look for comment `# 🎯 ADD MORE FIELDS HERE`

```python
results.append({
    # Existing fields...
    
    # 🎯 ADD HERE:
    'your_field': trade['your_field'] or '',
    'your_metric': float(trade['your_metric'] or 0),
})
```

---

### **4. Define Field** (API contract)

**File:** `serializers/serial_rep_byTrade.py`  
**Line:** ~140 (in `TradeGridSerializer` class)  
**Section:** Look for comment `# 🎯 ADD YOUR OWN FIELDS HERE`

```python
class TradeGridSerializer(serializers.Serializer):
    # Existing fields...
    
    # 🎯 ADD HERE:
    your_field = serializers.CharField(required=False)
    your_metric = serializers.FloatField(required=False)
```

---

### **5. Frontend Column**

**File:** `frontend_vue/src/views/dashboards/reporting/views/ByTradeReport.vue`  
**Line:** ~230 (in `columnDefs` array)  
**Section:** End of columnDefs array

```typescript
const columnDefs = ref<ColDef[]>([
  // Existing columns...
  
  // 🎯 ADD HERE:
  {
    headerName: 'Your Field',
    field: 'your_field',  // Must match serializer!
    width: 140,
  },
])
```

---

## 🔍 **Field Type Quick Reference**

### **From SellerRawData** (already there)
Just reference directly - no annotation needed!
- `property_type`, `occupancy`, `street_address`, `city`, `state`, `zip`
- `current_balance`, `total_debt`, `months_dlq`
- `fc_flag`, `bk_flag`, `mod_flag`

### **From AssetIdHub**
```python
F('asset_hub__servicer_id')
F('asset_hub__asset_status')
```

### **From ServicerLoanData**
```python
F('asset_hub__servicer_data__current_balance')
F('asset_hub__servicer_data__interest_rate')
F('asset_hub__servicer_data__total_debt')
F('asset_hub__servicer_data__fc_status')
F('asset_hub__servicer_data__investor_id')
```

### **From Trade**
```python
F('trade__trade_name')
F('trade__status')
F('trade__created_at')
```

### **From Seller**
```python
F('trade__seller__name')
F('trade__seller__email')
```

---

## 🎨 **Serializer Field Types**

```python
# Text fields
field_name = serializers.CharField()
field_name = serializers.CharField(required=False, allow_blank=True)

# Numbers
count_field = serializers.IntegerField()
avg_field = serializers.FloatField()
money_field = serializers.DecimalField(max_digits=15, decimal_places=2)

# Dates
date_field = serializers.DateField()
datetime_field = serializers.DateTimeField()

# Boolean
flag_field = serializers.BooleanField()

# Always add for optional fields:
field_name = serializers.CharField(required=False, allow_null=True)
```

---

## ✅ **Checklist**

When adding a field, ask yourself:

- [ ] Is it on SellerRawData? → **No annotation needed**, skip to Step 2
- [ ] Is it on related model? → **Annotate in queryBuilder Step 1**
- [ ] Do I need to sum/avg/count it? → **Add to .annotate() in Step 2**
- [ ] Do I just want to show it? → **Add to .values() in Step 2**
- [ ] Did I add to results dict? → **Step 3**
- [ ] Did I define in serializer? → **Step 4** ✅ (Source of truth!)
- [ ] Did I add column to frontend? → **Step 5**

---

## 🎉 **You're Ready!**

Open the files and look for the `🎯` emoji - that's where you add your fields!

**Three key files to edit:**
1. `services/serv_rep_queryBuilder.py` - Lines ~135-156 (annotations)
2. `services/serv_rep_aggregations.py` - Lines ~200-220 (aggregations) + Lines ~275-290 (results)
3. `serializers/serial_rep_byTrade.py` - Lines ~140+ (field definitions) ✅

**The serializer is your source of truth!** 🎯

