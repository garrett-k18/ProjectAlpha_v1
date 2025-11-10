# 📋 Report View Template (Copy & Paste)

Use this template for migrating any report view to AG Grid.

---

## Template Code

```vue
<template>
  <!--
    [VIEW NAME] Report - AG Grid Implementation
    
    WHAT: [Brief description]
    WHY: Users can customize columns, filter, sort, and export
    WHERE: Reporting Dashboard > [View Name]
  -->
  <div>
    <!-- Chart Card (Optional - keep your existing chart) -->
    <div class="card" v-if="chartData && chartData.length > 0">
      <div class="card-header">
        <h4 class="header-title">
          <i class="mdi mdi-chart-bar me-2"></i>
          [Chart Title]
        </h4>
      </div>
      <div class="card-body">
        <!-- Your existing chart code here -->
        <canvas ref="chartCanvas"></canvas>
      </div>
    </div>

    <!-- AG Grid Card -->
    <div class="card" :class="{ 'mt-3': chartData && chartData.length > 0 }">
      <div class="card-header">
        <h4 class="header-title mb-0">
          <i class="mdi mdi-table me-2"></i>
          [Grid Title]
        </h4>
        <p class="text-muted small mb-0 mt-1">
          Customize columns, filter data, and export to CSV
        </p>
      </div>

      <div class="card-body">
        <ReportingAgGrid
          ref="agGridRef"
          :column-defs="columnDefs"
          :row-data="gridData"
          :loading="loadingGrid"
          grid-height="600px"
          :pagination="true"
          :page-size="50"
          row-selection="single"
          @row-clicked="handleRowClick"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * WHAT: [View Name] Report with AG Grid
 * WHY: [Purpose]
 * HOW: Uses ReportingAgGrid component with custom column definitions
 */
import { ref } from 'vue'
import type { ColDef, ValueFormatterParams } from 'ag-grid-community'
import ReportingAgGrid from '../components/ReportingAgGrid.vue'
// Optional: Import BadgeCell if you need badges
import BadgeCell from '@/views/acq_module/acq_dash/components/BadgeCell.vue'

// WHAT: Component props
// WHY: Receive data from parent reporting dashboard
const props = defineProps<{
  chartData: any[]
  gridData: any[]
  loadingChart: boolean
  loadingGrid: boolean
}>()

// WHAT: Component emits
// WHY: Notify parent when user drills down
const emit = defineEmits<{
  (e: 'drill-down', payload: { type: string; data: any }): void
}>()

// WHAT: Value formatters (matches existing grids)
// WHY: Consistent formatting across all reporting
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
  const v = params.value
  if (v == null || v === '') return ''
  return `${Number(v).toFixed(1)}%`
}

function numberFormatter(params: ValueFormatterParams): string {
  const v = params.value
  if (v == null || v === '') return ''
  return new Intl.NumberFormat('en-US').format(Number(v))
}

function dateFormatter(params: ValueFormatterParams): string {
  const v = params.value
  if (!v) return ''
  const d = new Date(String(v))
  if (isNaN(d.getTime())) return String(v)
  return new Intl.DateTimeFormat('en-US', { 
    year: 'numeric', 
    month: '2-digit', 
    day: '2-digit' 
  }).format(d)
}

// WHAT: AG Grid reference
const agGridRef = ref<InstanceType<typeof ReportingAgGrid> | null>(null)

/**
 * WHAT: AG Grid column definitions
 * WHY: Define all columns for this report view
 */
const columnDefs = ref<ColDef[]>([
  // ===== EXAMPLE COLUMNS - Replace with your fields =====
  
  // Text column (left-aligned)
  {
    headerName: 'Name',
    field: 'name',
    pinned: 'left',
    width: 250,
    headerClass: 'ag-left-aligned-header text-start',
    cellClass: 'ag-left-aligned-cell text-start fw-semibold',
  },
  
  // Number column
  {
    headerName: 'Count',
    field: 'count',
    width: 120,
    valueFormatter: numberFormatter,
  },
  
  // Currency column
  {
    headerName: 'Total UPB',
    field: 'total_upb',
    width: 150,
    valueFormatter: currencyFormatter,
  },
  
  // Percentage column with color coding
  {
    headerName: 'LTV',
    field: 'ltv',
    width: 120,
    valueFormatter: percentFormatter,
    cellClass: (params) => {
      const ltv = params.value
      if (ltv > 100) return 'text-danger fw-bold'
      if (ltv >= 90) return 'text-warning fw-semibold'
      return 'text-success'
    },
  },
  
  // Badge column (using BadgeCell)
  {
    headerName: 'Status',
    field: 'status',
    width: 140,
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
  
  // Date column
  {
    headerName: 'Bid Date',
    field: 'bid_date',
    width: 130,
    valueFormatter: dateFormatter,
  },
  
  // Hidden column (users can show via column panel)
  {
    headerName: 'Notes',
    field: 'notes',
    width: 200,
    hide: true,
    headerClass: 'ag-left-aligned-header text-start',
    cellClass: 'ag-left-aligned-cell text-start',
  },
])

/**
 * WHAT: Handle grid row click
 * WHY: Drill down when user clicks table row
 */
function handleRowClick(row: any): void {
  console.log('[ReportView] Row clicked:', row)
  emit('drill-down', { type: 'trade', data: row })  // Change 'trade' to your view type
}
</script>

<style scoped>
/**
 * WHAT: Custom styles for this report view
 * WHY: Override default styles if needed
 */
</style>
```

---

## 🎯 Column Types Cheat Sheet

### Text/Name (left-aligned)
```typescript
{
  headerName: 'Trade Name',
  field: 'trade_name',
  headerClass: 'ag-left-aligned-header text-start',
  cellClass: 'ag-left-aligned-cell text-start',
}
```

### Number (center-aligned)
```typescript
{
  headerName: 'Count',
  field: 'count',
  valueFormatter: (p) => p.value ? new Intl.NumberFormat().format(p.value) : '',
}
```

### Currency
```typescript
{
  headerName: 'Amount',
  field: 'amount',
  valueFormatter: currencyFormatter,
}
```

### Percentage
```typescript
{
  headerName: 'Rate',
  field: 'rate',
  valueFormatter: percentFormatter,
}
```

### Date
```typescript
{
  headerName: 'Date',
  field: 'date',
  valueFormatter: dateFormatter,
}
```

### Badge (using your BadgeCell)
```typescript
{
  headerName: 'Status',
  field: 'status',
  cellRenderer: BadgeCell as any,
  cellRendererParams: {
    mode: 'enum',
    enumMap: {
      'DD': { label: 'DD', color: 'bg-info' },
      'AWARDED': { label: 'Awarded', color: 'bg-success' },
    },
  },
}
```

### Color-coded Number
```typescript
{
  headerName: 'LTV',
  field: 'ltv',
  valueFormatter: percentFormatter,
  cellClass: (params) => {
    if (params.value > 100) return 'text-danger fw-bold'
    if (params.value >= 90) return 'text-warning'
    return 'text-success'
  },
}
```

### Pinned Column
```typescript
{
  headerName: 'ID',
  field: 'id',
  pinned: 'left',  // Or 'right'
}
```

### Hidden by Default
```typescript
{
  headerName: 'Notes',
  field: 'notes',
  hide: true,  // Users can show via column panel
}
```

---

## 📝 Migration Checklist

For each report view (`ByTradeReport`, `ByStatusReport`, `ByFundReport`, etc.):

- [ ] Copy template above
- [ ] Replace `[VIEW NAME]`, `[Chart Title]`, `[Grid Title]` placeholders
- [ ] Define column defs for your specific fields
- [ ] Keep your existing chart code (or remove if not needed)
- [ ] Replace Bootstrap table with `<ReportingAgGrid>`
- [ ] Test column show/hide
- [ ] Test sorting and filtering
- [ ] Test row click drill-down
- [ ] Test CSV export

---

## 🎉 That's It!

You now have a **standardized template** to apply AG Grid across all your reporting views. Same styling, same patterns, maximum user flexibility!

**Questions?** Review your existing grids in:
- `acq-grid.vue` - Your acquisitions pattern
- `asset-grid.vue` - Your asset management pattern
- This template - Reporting pattern

**Happy coding!** 🚀

