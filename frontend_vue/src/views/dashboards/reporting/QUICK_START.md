# 🚀 Quick Start: AG Grid for Reporting Dashboard

## You Already Have Everything! ✅

You're already using AG Grid with `themeQuartz` in:
- Acquisitions dashboard (`acq-grid.vue`)
- Asset Management (`asset-grid.vue`)

Now let's add the same power to your **Reporting Dashboard** with the filters driving the data!

---

## 📝 How to Use (3 Simple Steps)

### Step 1: Define Your Columns

Create column definitions using your **existing** patterns. Example for `ByTradeReport.vue`:

```typescript
import type { ColDef, ValueFormatterParams } from 'ag-grid-community'
import BadgeCell from '@/views/acq_module/acq_dash/components/BadgeCell.vue'

// WHAT: Value formatters (matches your existing grids)
function currencyFormatter(params: ValueFormatterParams): string {
  const v = params.value
  const num = typeof v === 'number' ? v : parseFloat(String(v))
  if (Number.isNaN(num)) return v == null ? '' : String(v)
  return new Intl.NumberFormat('en-US', { 
    style: 'currency', 
    currency: 'USD', 
    maximumFractionDigits: 0 
  }).format(num)
}

function percentFormatter(params: ValueFormatterParams): string {
  return params.value == null ? '' : `${Number(params.value).toFixed(1)}%`
}

// WHAT: Column definitions
const columnDefs = ref<ColDef[]>([
  {
    headerName: 'Trade Name',
    field: 'trade_name',
    pinned: 'left',
    width: 250,
    headerClass: 'ag-left-aligned-header text-start',
    cellClass: 'ag-left-aligned-cell text-start fw-semibold',
  },
  {
    headerName: 'Asset Count',
    field: 'asset_count',
    width: 130,
    valueFormatter: (p) => p.value ? new Intl.NumberFormat().format(p.value) : '',
  },
  {
    headerName: 'Total UPB',
    field: 'total_upb',
    width: 150,
    valueFormatter: currencyFormatter,
  },
  {
    headerName: 'Avg LTV',
    field: 'avg_ltv',
    width: 120,
    valueFormatter: percentFormatter,
    cellClass: (params) => {
      // WHAT: Color-code LTV by risk
      const ltv = params.value
      if (ltv > 100) return 'text-danger fw-bold'
      if (ltv >= 90) return 'text-warning fw-semibold'
      return 'text-success'
    },
  },
  {
    headerName: 'Status',
    field: 'status',
    width: 140,
    cellRenderer: BadgeCell as any,  // Use your existing BadgeCell!
    cellRendererParams: {
      mode: 'enum',
      enumMap: {
        'DD': { label: 'DD', color: 'bg-info' },
        'AWARDED': { label: 'Awarded', color: 'bg-success' },
        'PASS': { label: 'Pass', color: 'bg-secondary' },
        'BOARD': { label: 'Board', color: 'bg-primary' },
      },
    },
  },
])
```

### Step 2: Add AG Grid to Template

Replace your Bootstrap table with:

```vue
<template>
  <div class="card">
    <div class="card-header">
      <h4 class="header-title">
        <i class="mdi mdi-table me-2"></i>
        Trade Details
      </h4>
    </div>
    <div class="card-body">
      <ReportingAgGrid
        :column-defs="columnDefs"
        :row-data="gridData"
        :loading="loadingGrid"
        grid-height="600px"
        @row-clicked="handleRowClick"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import ReportingAgGrid from '../components/ReportingAgGrid.vue'
// ... your column defs from Step 1
</script>
```

### Step 3: Handle Row Clicks

```typescript
function handleRowClick(row: any): void {
  emit('drill-down', { type: 'trade', data: row })
}
```

**That's it!** Your filters drive the API, AG Grid displays the data with full column control.

---

## 🎯 Using Your Existing BadgeCell Component

You already have `BadgeCell` component! Use it in column definitions:

```typescript
import BadgeCell from '@/views/acq_module/acq_dash/components/BadgeCell.vue'

const columnDefs = ref<ColDef[]>([
  {
    headerName: 'Status',
    field: 'status',
    cellRenderer: BadgeCell as any,
    cellRendererParams: {
      mode: 'enum',
      enumMap: {
        'DD': { label: 'DD', color: 'bg-info' },
        'AWARDED': { label: 'Awarded', color: 'bg-success' },
        'PASS': { label: 'Pass', color: 'bg-secondary' },
      },
    },
  },
  {
    headerName: 'Property Type',
    field: 'property_type',
    cellRenderer: BadgeCell as any,
    cellRendererParams: {
      mode: 'enum',
      enumMap: propertyTypeEnumMap, // From @/config/badgeTokens
    },
  },
])
```

---

## 🎨 Column Alignment (Matches Your Grids)

### Left-aligned (for text/names):
```typescript
{
  headerName: 'Trade Name',
  field: 'trade_name',
  headerClass: 'ag-left-aligned-header text-start',
  cellClass: 'ag-left-aligned-cell text-start',
}
```

### Center-aligned (default for numbers/badges):
```typescript
{
  headerName: 'Asset Count',
  field: 'asset_count',
  // No special class needed - center is default
}
```

---

## 📊 Complete Example: Migrate ByTradeReport

Here's how to convert `ByTradeReport.vue` to use AG Grid:

### OLD (Bootstrap Table)
```vue
<div class="table-responsive">
  <table class="table table-hover">
    <thead>
      <tr>
        <th>Trade Name</th>
        <th>Asset Count</th>
        <th>Total UPB</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="row in gridData" :key="row.id">
        <td>{{ row.trade_name }}</td>
        <td>{{ row.asset_count }}</td>
        <td>{{ formatCurrency(row.total_upb) }}</td>
      </tr>
    </tbody>
  </table>
</div>
```

### NEW (AG Grid)
```vue
<ReportingAgGrid
  :column-defs="columnDefs"
  :row-data="gridData"
  :loading="loadingGrid"
  @row-clicked="handleRowClick"
/>

<script setup lang="ts">
import type { ColDef } from 'ag-grid-community'
import ReportingAgGrid from '../components/ReportingAgGrid.vue'

const columnDefs = ref<ColDef[]>([
  {
    headerName: 'Trade Name',
    field: 'trade_name',
    pinned: 'left',
    width: 250,
    headerClass: 'ag-left-aligned-header text-start',
    cellClass: 'ag-left-aligned-cell text-start',
  },
  {
    headerName: 'Asset Count',
    field: 'asset_count',
    width: 130,
    valueFormatter: (p) => p.value ? new Intl.NumberFormat().format(p.value) : '',
  },
  {
    headerName: 'Total UPB',
    field: 'total_upb',
    width: 150,
    valueFormatter: (p) => {
      const num = Number(p.value)
      if (isNaN(num)) return ''
      return new Intl.NumberFormat('en-US', { 
        style: 'currency', 
        currency: 'USD', 
        maximumFractionDigits: 0 
      }).format(num)
    },
  },
])
</script>
```

---

## ✅ What Users Get

Your **sidebar filters** still drive what data loads from the API. AG Grid adds:

- ✅ **Column show/hide** - Click "Columns" button
- ✅ **Column reordering** - Drag headers
- ✅ **Column resizing** - Drag column edges
- ✅ **Quick search** - Search across all columns
- ✅ **Per-column filters** - Filter icon in each header
- ✅ **Multi-sort** - Click headers, Shift+click for multi-sort
- ✅ **CSV export** - Built-in
- ✅ **Pagination** - Choose 10/25/50/100/200 rows per page

---

## 🔧 Files You Have

1. **ReportingAgGrid.vue** - Reusable wrapper component
   - Uses `themeQuartz` ✅ (matches your existing grids)
   - Column management toolbar
   - Export buttons
   - Quick search

2. **ByTradeReportAG.vue** - Example implementation
   - Shows how to define columns
   - Chart + AG Grid layout
   - Row click drill-down

3. **gridCellRenderers.ts** - Optional custom renderers
   - You can ignore this! Use your existing `BadgeCell` and value formatters instead

---

## 💡 Pro Tips

### 1. Reuse Your Existing Components
```typescript
// Use BadgeCell for enum fields
import BadgeCell from '@/views/acq_module/acq_dash/components/BadgeCell.vue'
import { propertyTypeEnumMap, assetStatusEnumMap } from '@/config/badgeTokens'

{
  headerName: 'Property Type',
  field: 'property_type',
  cellRenderer: BadgeCell as any,
  cellRendererParams: {
    mode: 'enum',
    enumMap: propertyTypeEnumMap,
  },
}
```

### 2. Match Your Existing Formatters
```typescript
// Currency (your pattern)
function currency0(p: any): string {
  const v = p.value
  const n = typeof v === 'number' ? v : parseFloat(String(v))
  if (Number.isNaN(n)) return ''
  return new Intl.NumberFormat('en-US', { 
    style: 'currency', 
    currency: 'USD', 
    maximumFractionDigits: 0 
  }).format(n)
}

// Percentage (your pattern)
function percentFmt(p: any): string {
  return p.value == null ? '' : `${(Number(p.value) * 100).toFixed(2)}%`
}

// Date (your pattern)
function dateFmt(p: any): string {
  if (!p.value) return ''
  const d = new Date(String(p.value))
  if (isNaN(d.getTime())) return String(p.value)
  return new Intl.DateTimeFormat('en-US', { 
    year: 'numeric', 
    month: '2-digit', 
    day: '2-digit' 
  }).format(d)
}
```

### 3. Pin Important Columns
```typescript
{
  headerName: 'Trade Name',
  field: 'trade_name',
  pinned: 'left',  // Stays visible when scrolling horizontally
}
```

---

## 🎯 Your Architecture (Perfect!)

```
┌─────────────────────────────────┐
│  Sidebar Filters (API-level)   │
│  • Trades: [1, 2, 3]           │
│  • Statuses: [DD, AWARDED]     │
│  • Funds, Entities, Dates      │
└──────────┬──────────────────────┘
           ↓ [Apply Button]
┌──────────▼──────────────────────┐
│  Backend API                    │
│  GET /api/reporting/by-trade/  │
│  ?trade_ids=1,2,3...           │
└──────────┬──────────────────────┘
           ↓ [Returns Filtered Data]
┌──────────▼──────────────────────┐
│  AG Grid (Client-side)          │
│  ✅ Users customize columns     │
│  ✅ Users filter/sort           │
│  ✅ Users export CSV/Excel      │
└─────────────────────────────────┘
```

**Your thinking is spot-on:** Sidebar filters query the backend, AG Grid gives users max flexibility on the results!

---

## 🎉 Ready to Use!

**Files Created:**
- `components/ReportingAgGrid.vue` - Reusable component (uses `themeQuartz` ✅)
- `views/ByTradeReportAG.vue` - Example implementation
- `utils/gridCellRenderers.ts` - Optional (you can use your existing formatters instead)

**Next Steps:**
1. Import `ReportingAgGrid` into a report view
2. Define columns using your existing formatter patterns
3. Use your `BadgeCell` for status/enum fields
4. Test with your sidebar filters

**No new packages needed** - AG Grid is already installed! 🎉

