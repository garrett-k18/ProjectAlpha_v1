# AG Grid Implementation Guide for Reporting Dashboard

## 📋 Overview

This guide covers the AG Grid implementation for the reporting dashboard, providing users with maximum flexibility to customize columns, filter data, sort, and export reports.

---

## 🚀 Installation

### Step 1: Install AG Grid packages

```bash
cd frontend_vue
npm install ag-grid-community ag-grid-vue3
```

**For Excel export support (optional):**
```bash
npm install ag-grid-enterprise
```

> **Note:** AG Grid Community Edition (free) includes CSV export. Enterprise Edition ($) adds Excel export, advanced filtering, row grouping, and more. Start with Community Edition.

### Step 2: Import AG Grid CSS

Add to `frontend_vue/src/main.ts` (or your main entry file):

```typescript
// AG Grid Community styles
import 'ag-grid-community/styles/ag-grid.css'
import 'ag-grid-community/styles/ag-theme-alpine.css'

// Optional: Other themes
// import 'ag-grid-community/styles/ag-theme-balham.css'
// import 'ag-grid-community/styles/ag-theme-material.css'
```

---

## 📁 File Structure

```
frontend_vue/src/views/dashboards/reporting/
├── components/
│   ├── ReportingAgGrid.vue          # ✅ NEW: Reusable AG Grid wrapper
│   ├── ReportingSidebar.vue         # Existing filter sidebar
│   ├── ReportHeader.vue             # Existing header
│   └── DrillDownModal.vue           # Existing drill-down modal
├── utils/
│   └── gridCellRenderers.ts         # ✅ NEW: Custom cell renderers
├── views/
│   ├── ByTradeReport.vue            # Original Bootstrap table version
│   ├── ByTradeReportAG.vue          # ✅ NEW: AG Grid version (example)
│   ├── ByStatusReport.vue           # To be migrated
│   ├── ByFundReport.vue             # To be migrated
│   ├── ByEntityReport.vue           # To be migrated
│   └── ... (other views)
└── AG_GRID_SETUP.md                 # This file
```

---

## 🎯 How It Works

### Architecture Flow

```
User Selects Filters (Sidebar)
    ↓
Backend API Query (with filter params)
    ↓
Raw Data → AG Grid Component
    ↓
User Customizes Columns (Show/Hide, Reorder, Resize)
    ↓
User Applies Client-side Filters (AG Grid column filters)
    ↓
User Exports to CSV/Excel
```

**Key Point:** Sidebar filters = **API-level** (reduce data from backend). AG Grid filters = **Client-side** (refine already-loaded data).

---

## 🔧 Using ReportingAgGrid Component

### Basic Usage

```vue
<template>
  <ReportingAgGrid
    :column-defs="columnDefs"
    :row-data="gridData"
    :loading="loadingGrid"
    @row-clicked="handleRowClick"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { ColDef } from 'ag-grid-community'
import ReportingAgGrid from '../components/ReportingAgGrid.vue'
import { currencyRenderer, statusBadgeRenderer } from '../utils/gridCellRenderers'

// Define columns
const columnDefs = ref<ColDef[]>([
  {
    headerName: 'Trade Name',
    field: 'trade_name',
    pinned: 'left',
    width: 250,
  },
  {
    headerName: 'Total UPB',
    field: 'total_upb',
    cellRenderer: currencyRenderer,
  },
  {
    headerName: 'Status',
    field: 'status',
    cellRenderer: statusBadgeRenderer,
  },
])

// Your data
const gridData = ref([
  { trade_name: 'Trade 1', total_upb: 1500000, status: 'DD' },
  { trade_name: 'Trade 2', total_upb: 2300000, status: 'AWARDED' },
])

// Handle row clicks
function handleRowClick(row: any) {
  console.log('Row clicked:', row)
}
</script>
```

---

## 🎨 Custom Cell Renderers

Located in `utils/gridCellRenderers.ts`:

| Renderer | Use Case | Example |
|----------|----------|---------|
| `currencyRenderer` | Dollar amounts | `$1.5MM`, `$250k` |
| `percentRenderer` | Percentages | `85.5%` |
| `ltvRenderer` | LTV ratios with color | <span style="color:green">75%</span>, <span style="color:red">105%</span> |
| `statusBadgeRenderer` | Status badges | <span style="background:#0acf97;color:white;padding:2px 8px;border-radius:3px;">AWARDED</span> |
| `numberRenderer` | Numbers with commas | `1,234,567` |
| `dateRenderer` | Date formatting | `01/15/2024` |
| `booleanRenderer` | Yes/No checkmarks | ✓ / ✗ |
| `propertyTypeRenderer` | Property type icons | 🏠 Single Family |
| `delinquencyRenderer` | Delinquency days | <span style="color:red">90 days</span> |

### Example: Using Custom Renderers

```typescript
const columnDefs = ref<ColDef[]>([
  {
    headerName: 'Total UPB',
    field: 'total_upb',
    cellRenderer: currencyRenderer, // $1.5MM format
  },
  {
    headerName: 'LTV',
    field: 'avg_ltv',
    cellRenderer: ltvRenderer, // Color-coded by risk
  },
  {
    headerName: 'Status',
    field: 'status',
    cellRenderer: statusBadgeRenderer, // Colored badges
  },
])
```

---

## 📊 Column Definition Options

Common column properties:

```typescript
{
  headerName: 'Column Title',         // Display name
  field: 'data_field',                // Data property name
  width: 150,                         // Fixed width (optional)
  minWidth: 100,                      // Minimum width
  maxWidth: 300,                      // Maximum width
  flex: 1,                            // Flexible width (fills space)
  sortable: true,                     // Enable sorting
  filter: 'agTextColumnFilter',      // Enable filtering
  resizable: true,                    // Allow resizing
  pinned: 'left',                     // Pin to left/right
  hide: true,                         // Hidden by default
  cellRenderer: customRenderer,       // Custom cell renderer
  valueFormatter: (params) => ...,    // Format value
  comparator: (a, b) => a - b,        // Custom sorting
  checkboxSelection: true,            // Add checkbox
  cellClass: 'custom-class',          // CSS class
  type: 'numericColumn',              // Right-align numbers
}
```

### Filter Types

- `'agTextColumnFilter'` - Text search
- `'agNumberColumnFilter'` - Number range
- `'agDateColumnFilter'` - Date range
- `'agSetColumnFilter'` - Multi-select dropdown

---

## 🎛️ ReportingAgGrid Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `columnDefs` | `ColDef[]` | **required** | Column definitions |
| `rowData` | `any[]` | **required** | Array of data objects |
| `loading` | `boolean` | `false` | Show loading overlay |
| `gridHeight` | `string` | `'600px'` | CSS height value |
| `gridTheme` | `string` | `'ag-theme-alpine'` | AG Grid theme class |
| `pagination` | `boolean` | `true` | Enable pagination |
| `pageSize` | `number` | `25` | Rows per page |
| `rowSelection` | `'single' | 'multiple'` | `'single'` | Row selection mode |
| `enableExport` | `boolean` | `true` | Show export buttons |

---

## 🔧 ReportingAgGrid Events

| Event | Payload | Description |
|-------|---------|-------------|
| `@row-clicked` | `row: any` | User clicked a row (for drill-down) |
| `@selection-changed` | `rows: any[]` | Selected rows changed |
| `@grid-ready` | `api: GridApi` | Grid initialized, returns API |

---

## 📝 Migrating Existing Reports

### Before (Bootstrap Table)

```vue
<div class="table-responsive">
  <table class="table table-hover">
    <thead>
      <tr>
        <th>Trade Name</th>
        <th>UPB</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="row in gridData" :key="row.id">
        <td>{{ row.trade_name }}</td>
        <td>{{ formatCurrency(row.total_upb) }}</td>
      </tr>
    </tbody>
  </table>
</div>
```

### After (AG Grid)

```vue
<ReportingAgGrid
  :column-defs="columnDefs"
  :row-data="gridData"
  :loading="loadingGrid"
  @row-clicked="handleRowClick"
/>

<script setup lang="ts">
const columnDefs = ref<ColDef[]>([
  {
    headerName: 'Trade Name',
    field: 'trade_name',
  },
  {
    headerName: 'Total UPB',
    field: 'total_upb',
    cellRenderer: currencyRenderer,
  },
])
</script>
```

**Benefits:**
- ✅ Column show/hide
- ✅ Column reordering
- ✅ Column resizing
- ✅ Built-in filtering
- ✅ Built-in sorting
- ✅ CSV/Excel export
- ✅ Pagination
- ✅ Quick search

---

## 🎯 Step-by-Step Migration Example

### 1. Import Required Modules

```typescript
import { ref } from 'vue'
import type { ColDef } from 'ag-grid-community'
import ReportingAgGrid from '../components/ReportingAgGrid.vue'
import { currencyRenderer, statusBadgeRenderer, numberRenderer } from '../utils/gridCellRenderers'
```

### 2. Define Column Definitions

```typescript
const columnDefs = ref<ColDef[]>([
  {
    headerName: 'Trade Name',
    field: 'trade_name',
    pinned: 'left',
    width: 250,
    sortable: true,
    filter: 'agTextColumnFilter',
    checkboxSelection: true,
  },
  {
    headerName: 'Asset Count',
    field: 'asset_count',
    width: 130,
    type: 'numericColumn',
    cellRenderer: numberRenderer,
  },
  {
    headerName: 'Total UPB',
    field: 'total_upb',
    width: 150,
    type: 'numericColumn',
    cellRenderer: currencyRenderer,
  },
  {
    headerName: 'Status',
    field: 'status',
    width: 140,
    cellRenderer: statusBadgeRenderer,
    filter: 'agSetColumnFilter',
  },
])
```

### 3. Replace Table with AG Grid

```vue
<template>
  <!-- Remove old table -->
  <!-- <div class="table-responsive">...</div> -->

  <!-- Add AG Grid -->
  <ReportingAgGrid
    :column-defs="columnDefs"
    :row-data="gridData"
    :loading="loadingGrid"
    grid-height="600px"
    :pagination="true"
    :page-size="25"
    @row-clicked="handleRowClick"
  />
</template>
```

### 4. Handle Row Clicks (Drill-down)

```typescript
function handleRowClick(row: any): void {
  emit('drill-down', { type: 'trade', data: row })
}
```

---

## 🎨 Styling & Theming

### Using Different Themes

```vue
<ReportingAgGrid
  grid-theme="ag-theme-balham"
  ...
/>
```

Available themes:
- `ag-theme-alpine` (default) - Clean, modern
- `ag-theme-balham` - Traditional
- `ag-theme-material` - Material Design

### Custom Theme Overrides

In your component's `<style>` section:

```vue
<style scoped>
:deep(.ag-theme-alpine) {
  --ag-header-background-color: #f1f3fa;
  --ag-header-foreground-color: #6c757d;
  --ag-row-hover-color: rgba(54, 162, 235, 0.05);
  --ag-font-family: 'Inter', sans-serif;
}
</style>
```

---

## 📦 Export Functionality

### CSV Export (Community Edition)

Built-in - no additional setup required. Users click "Export > Export as CSV" in the toolbar.

### Excel Export (Enterprise Edition Only)

1. Install enterprise package:
   ```bash
   npm install ag-grid-enterprise
   ```

2. Set license key in `main.ts`:
   ```typescript
   import { LicenseManager } from 'ag-grid-enterprise'
   LicenseManager.setLicenseKey('YOUR_LICENSE_KEY')
   ```

3. Excel export will automatically be available

---

## 🔍 Advanced Features

### 1. Column Pinning

```typescript
{
  headerName: 'Trade Name',
  field: 'trade_name',
  pinned: 'left', // Pin to left side
}
```

### 2. Row Grouping (Enterprise)

```typescript
{
  headerName: 'Status',
  field: 'status',
  enableRowGroup: true, // Allow grouping by status
}
```

### 3. Aggregation (Enterprise)

```typescript
{
  headerName: 'Total UPB',
  field: 'total_upb',
  aggFunc: 'sum', // Sum values when grouped
}
```

### 4. Master/Detail (Enterprise)

Show expandable row details:

```typescript
const gridOptions = {
  masterDetail: true,
  detailCellRendererParams: {
    detailGridOptions: {
      columnDefs: [...], // Columns for detail view
    },
    getDetailRowData: (params) => {
      params.successCallback(params.data.details)
    },
  },
}
```

---

## 🐛 Troubleshooting

### Issue: Grid not displaying

**Solution:** Ensure AG Grid CSS is imported in `main.ts`:
```typescript
import 'ag-grid-community/styles/ag-grid.css'
import 'ag-grid-community/styles/ag-theme-alpine.css'
```

### Issue: Columns not showing

**Solution:** Check `field` property matches your data keys exactly (case-sensitive).

### Issue: Export not working

**Solution:** CSV export is free. Excel requires `ag-grid-enterprise` package.

### Issue: Cell renderers not working

**Solution:** Ensure renderer function returns string or DOM element:
```typescript
cellRenderer: (params) => `<span>${params.value}</span>`
```

---

## 📚 Additional Resources

- [AG Grid Vue 3 Docs](https://www.ag-grid.com/vue-data-grid/)
- [Column Definitions](https://www.ag-grid.com/vue-data-grid/column-definitions/)
- [Cell Rendering](https://www.ag-grid.com/vue-data-grid/cell-rendering/)
- [Filtering](https://www.ag-grid.com/vue-data-grid/filtering/)
- [Sorting](https://www.ag-grid.com/vue-data-grid/row-sorting/)
- [Export](https://www.ag-grid.com/vue-data-grid/csv-export/)

---

## ✅ Migration Checklist

- [ ] Install `ag-grid-community` and `ag-grid-vue3`
- [ ] Import AG Grid CSS in `main.ts`
- [ ] Create column definitions for your view
- [ ] Replace Bootstrap table with `<ReportingAgGrid>` component
- [ ] Add custom cell renderers from `gridCellRenderers.ts`
- [ ] Test column show/hide functionality
- [ ] Test column reordering (drag & drop)
- [ ] Test filtering and sorting
- [ ] Test CSV export
- [ ] Test row click drill-down
- [ ] Test with sidebar filters applied
- [ ] Update linting errors (if any)

---

## 💡 Best Practices

1. **Column Widths:** Use `width` for fixed columns, `flex` for responsive
2. **Performance:** Limit visible columns to 10-15 for best UX
3. **Pinning:** Pin 1-2 key columns (e.g., Name, ID) to left
4. **Filters:** Use appropriate filter type (`agTextColumnFilter`, `agNumberColumnFilter`, etc.)
5. **Cell Renderers:** Reuse renderers from `gridCellRenderers.ts` instead of inline functions
6. **Export:** Always enable export functionality for power users
7. **Pagination:** Use pagination for datasets > 100 rows
8. **Loading States:** Always pass `:loading` prop for better UX

---

## 🎉 Next Steps

1. **Migrate remaining views:** Apply AG Grid to `ByStatusReport`, `ByFundReport`, `ByEntityReport`, etc.
2. **Add more cell renderers:** Create domain-specific renderers as needed
3. **Test with real backend data:** Ensure column fields match API response keys
4. **Collect user feedback:** See which columns users want to see by default
5. **Consider Enterprise Edition:** If users need Excel export, row grouping, or advanced filtering

---

**Questions?** Review this guide or check AG Grid documentation.

**Happy coding!** 🚀

