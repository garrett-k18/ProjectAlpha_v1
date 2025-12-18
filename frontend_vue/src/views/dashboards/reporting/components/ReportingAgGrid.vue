<template>
  <!--
    Reusable AG Grid Component for Reporting Dashboard
    
    WHAT: Enterprise-grade data grid with column management, filtering, sorting, export
    WHY: Maximum user flexibility - users control which columns to show, how to arrange them
    WHERE: Used across all reporting views (By Trade, By Status, By Fund, etc.)
    
    KEY FEATURES:
    - Column show/hide panel (right-click or toolbar button)
    - Drag & drop column reordering
    - Column resizing with auto-size option
    - Pinned columns (left/right)
    - Built-in CSV/Excel export
    - Advanced filtering per column
    - Row click for drill-down
    - Custom cell renderers (currency, badges, percentages)
    - Pagination with configurable page sizes
    - Loading overlay
    - Empty state
  -->
  <div :class="containerClasses">
    <!-- Grid Toolbar -->
    <div class="grid-toolbar mb-2 d-flex justify-content-between align-items-center">
      <div class="d-flex gap-2 align-items-center">
        <!-- Quick Filter Search -->
        <div class="input-group input-group-sm" style="max-width: 300px;">
          <span class="input-group-text">
            <i class="mdi mdi-magnify"></i>
          </span>
          <input
            type="text"
            class="form-control"
            placeholder="Quick search..."
            v-model="quickFilterText"
            @input="onQuickFilterChanged"
          />
        </div>

        <!-- Column Management Button -->
        <button
          class="btn btn-sm btn-outline-secondary"
          @click="showColumnPanel = !showColumnPanel"
          title="Show/Hide Columns"
        >
          <i class="mdi mdi-view-column"></i>
        </button>

        <!-- Auto-size All Columns -->
        <button
          class="btn btn-sm btn-outline-secondary"
          @click="autoSizeAll"
          title="Auto-size all columns"
        >
          <i class="mdi mdi-arrow-expand-horizontal"></i>
        </button>

        <!-- Full Window Toggle -->
        <button
          class="btn btn-sm btn-outline-secondary"
          @click="toggleFullWindow"
          :title="isFullWindow ? 'Exit full window mode' : 'Expand grid to full window'"
        >
          <i class="mdi" :class="isFullWindow ? 'mdi-arrow-collapse' : 'mdi-arrow-expand'"></i>
        </button>

        <!-- Reset Grid -->
        <button
          class="btn btn-sm btn-outline-secondary"
          @click="resetGrid"
          title="Reset grid to defaults"
        >
          <i class="mdi mdi-restore"></i>
        </button>
      </div>

      <div class="d-flex gap-2">
        <!-- Export Dropdown -->
        <div class="dropdown">
          <button
            class="btn btn-sm btn-success dropdown-toggle"
            type="button"
            @click="showExportDropdown = !showExportDropdown"
          >
            <i class="mdi mdi-download me-1"></i>
            Export
          </button>
          <ul
            class="dropdown-menu dropdown-menu-end"
            :class="{ show: showExportDropdown }"
          >
            <li>
              <a class="dropdown-item" href="#" @click.prevent="handleExportCsv">
                <i class="mdi mdi-file-delimited me-2"></i>
                Export as CSV
              </a>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Column Management Panel (Collapsible) -->
    <div v-if="showColumnPanel" class="column-panel card mb-2">
      <div class="card-body py-2">
        <div class="d-flex justify-content-between align-items-center mb-2">
          <h6 class="mb-0">
            <i class="mdi mdi-view-column me-1"></i>
            Manage Columns
          </h6>
          <button
            class="btn btn-sm btn-link p-0"
            @click="showColumnPanel = false"
          >
            <i class="mdi mdi-close"></i>
          </button>
        </div>
        <div class="row g-2">
          <div
            v-for="col in allColumns"
            :key="col.field"
            class="col-lg-3 col-md-4 col-sm-6"
          >
            <div class="form-check">
              <input
                class="form-check-input"
                type="checkbox"
                :id="`col-${col.field}`"
                :checked="col.visible"
                @change="toggleColumn(col.field)"
              />
              <label class="form-check-label small" :for="`col-${col.field}`">
                {{ col.headerName }}
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- AG Grid with Quartz theme (matches existing grids) -->
    <div class="ag-grid-wrapper">
      <ag-grid-vue
        ref="gridRef"
        class="reporting-grid"
        :style="{ width: '100%', height: computedGridHeight }"
        :theme="themeQuartz"
        :columnDefs="columnDefs"
        :rowData="rowData"
        :defaultColDef="defaultColDef"
        :rowClassRules="rowClassRules"
        :getRowStyle="getRowStyle"
        :pagination="pagination"
        :paginationPageSize="pageSize"
        :paginationPageSizeSelector="pageSizeOptions"
        :rowSelection="{ mode: rowSelection === 'multiple' ? 'multiRow' : 'singleRow', checkboxes: false, headerCheckbox: false, enableClickSelection: true }"
        :suppressRowClickSelection="false"
        :animateRows="true"
        :enableCellTextSelection="true"
        :loading="loading"
        :pinnedTopRowData="pinnedTopRowData"
        overlayNoRowsTemplate="No data available"
        overlayLoadingTemplate="Loading..."
        @grid-ready="onGridReady"
        @row-clicked="onRowClicked"
        @selection-changed="onSelectionChanged"
        @filter-changed="onFilterOrSortChanged"
        @sort-changed="onFilterOrSortChanged"
      />
    </div>

    <!-- Grid Status Bar -->
    <div class="grid-status-bar mt-2 text-muted small">
      <i class="mdi mdi-information-outline me-1"></i>
      {{ statusBarText }}
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * WHAT: Reusable AG Grid component for reporting dashboard
 * WHY: Provides enterprise-grade data grid with max flexibility
 * HOW: Wraps AG Grid Community Edition with custom toolbar and column management
 * 
 * FEATURES:
 * - Dynamic column visibility control
 * - Column reordering via drag & drop
 * - Column resizing with auto-size
 * - Quick filter search across all columns
 * - CSV/Excel export
 * - Custom cell renderers for currency, badges, percentages
 * - Pagination with page size selector
 * - Loading & empty states
 * - Row selection and drill-down
 */
import { ref, computed, watch, nextTick } from 'vue'
import { AgGridVue } from 'ag-grid-vue3'
import { themeQuartz } from 'ag-grid-community'
import type { 
  GridApi, 
  ColDef, 
  ColGroupDef,
  GridReadyEvent,
  RowClickedEvent,
  SelectionChangedEvent 
} from 'ag-grid-community'

// WHAT: Component props interface
// WHY: Define all inputs needed from parent components
interface Props {
  columnDefs: Array<ColDef | ColGroupDef> // WHAT: AG Grid column definitions (supports groups)
  rowData: any[]                 // WHAT: Array of row data objects
  loading?: boolean              // WHAT: Show loading spinner
  gridHeight?: string            // WHAT: CSS height for grid (default: 600px)
  pagination?: boolean           // WHAT: Enable pagination (default: true)
  pageSize?: number              // WHAT: Rows per page (default: 25)
  rowSelection?: 'single' | 'multiple' // WHAT: Row selection mode
  enableExport?: boolean         // WHAT: Show export buttons (default: true)
}

// WHAT: Define props with defaults
// WHY: Allow parent to customize grid behavior
const props = withDefaults(defineProps<Props>(), {
  loading: false,
  gridHeight: '600px',
  pagination: true,
  pageSize: 25,
  rowSelection: 'single',
  enableExport: true,
})

// WHAT: Component emits interface
// WHY: Define events parent can listen to
const emit = defineEmits<{
  (e: 'rowClicked', row: any): void          // WHAT: User clicked a row (for drill-down)
  (e: 'selectionChanged', rows: any[]): void // WHAT: Selected rows changed
  (e: 'gridReady', api: GridApi): void       // WHAT: Grid is ready, return API
}>()

// WHAT: Grid API reference
// WHY: Store AG Grid API instance for programmatic control
const gridApi = ref<GridApi | null>(null)

// WHAT: UI state
// WHY: Control toolbar buttons, panels, and dropdowns
const showColumnPanel = ref<boolean>(false)
const isFullWindow = ref<boolean>(false)
const quickFilterText = ref<string>('')
const showExportDropdown = ref<boolean>(false)

// WHAT: Page size selector options
// WHY: Let users choose how many rows per page
const pageSizeOptions = ref<number[]>([10, 25, 50, 100, 200])

// WHAT: Default column definition (matches existing grid patterns)
// WHY: Apply common settings to all columns
const defaultColDef = ref<ColDef>({
  sortable: true,                // WHAT: Enable sorting on all columns
  filter: true,                  // WHAT: Enable column filters
  resizable: true,               // WHAT: Allow column resizing
  wrapHeaderText: true,          // WHAT: Headers wrap to multiple lines if needed
  autoHeaderHeight: true,        // WHAT: Header height adjusts automatically
  headerClass: 'text-center',    // WHAT: Center-align headers
  cellClass: 'text-center',      // WHAT: Center-align cell content
  floatingFilter: false,         // WHAT: Don't show filter row by default
  menuTabs: ['filterMenuTab'],   // WHAT: Show only filter tab in column menu
})

// WHAT: Track all columns with visibility state
// WHY: Power the column management panel
const allColumns = ref<Array<{ field: string; headerName: string; visible: boolean }>>([])

// WHAT: Row class rules
// WHY: Use AG Grid + Bootstrap classes to style special rows (e.g., pinned aggregate row)
const rowClassRules: { [cssClass: string]: (params: any) => boolean } = {
  // Highlight pinned top row using Bootstrap utilities
  'table-active fw-bold': (params: any) => params.node?.rowPinned === 'top',
}

// WHAT: Inline row styling for pinned aggregate row
// WHY: AG Grid v34 with themeQuartz needs inline styles for reliable styling
function getRowStyle(params: any): any {
  if (params.node?.rowPinned === 'top') {
    return {
      backgroundColor: '#f8f9fa',
      fontWeight: 'bold',
      borderTop: '3px solid #6c757d',
      borderBottom: '3px solid #6c757d',
    }
  }
  return undefined
}

// WHAT: Computed row count
// WHY: Display in toolbar badge
const rowCount = computed(() => props.rowData?.length || 0)

// WHAT: Status bar text
// WHY: Show helpful grid info at bottom
const statusBarText = computed(() => {
  if (props.loading) return 'Loading data...'
  if (rowCount.value === 0) return 'No data available'
  return `Drag column headers to reorder • Right-click for options • Double-click header edge to auto-size`
})

// WHAT: Pinned top row data for aggregates
// WHY: Show totals based on currently filtered rows, not affected by filters
const pinnedTopRowData = ref<any[]>([])

// WHAT: Loading overlay component
// WHY: Custom loading spinner
const loadingOverlayComponent = ref<any>(null)

// WHAT: No rows overlay component
// WHY: Custom empty state
const noRowsOverlayComponent = ref<any>(null)

/**
 * WHAT: Grid ready event handler
 * WHY: Store API reference and initialize column state
 * WHEN: Called once when AG Grid finishes initializing
 */
function onGridReady(params: GridReadyEvent): void {
  gridApi.value = params.api

  // WHAT: Initialize column visibility tracking
  // WHY: Populate the column management panel
  syncColumnState()

  // WHAT: Auto-size all columns on initial load
  // WHY: Fit content properly
  nextTick(() => {
    setTimeout(() => {
      autoSizeAll()
    }, 100)
  })

  // WHAT: Emit grid ready event
  // WHY: Let parent component access AG Grid API
  emit('gridReady', params.api)
}

/**
 * WHAT: Sync column visibility state
 * WHY: Keep allColumns ref in sync with AG Grid's column state
 */
function isGroupDef(def: ColDef | ColGroupDef): def is ColGroupDef {
  return (def as ColGroupDef).children !== undefined
}

function getLeafColumns(defs: Array<ColDef | ColGroupDef>): ColDef[] {
  const leaves: ColDef[] = []
  for (const d of defs) {
    if (isGroupDef(d) && Array.isArray(d.children)) {
      leaves.push(...getLeafColumns(d.children as Array<ColDef | ColGroupDef>))
    } else {
      leaves.push(d as ColDef)
    }
  }
  return leaves
}

function syncColumnState(): void {
  if (!gridApi.value) return

  const leaves = getLeafColumns(props.columnDefs)
  allColumns.value = leaves
    .filter(col => !!col.field)
    .map(col => ({
      field: col.field as string,
      headerName: (col.headerName as string) || (col.field as string),
      visible: col.hide !== true,
    }))
}

// WHAT: Recalculate pinned top aggregate row from currently filtered rows
// WHY: Show totals that always reflect current grid filters (option A)
// HOW: Use aggFunc from column definitions to determine aggregation type
function updatePinnedTopRowFromGrid(): void {
  // Use rowData prop directly since sidebar filters modify it before passing to grid
  // This ensures aggregates reflect the externally filtered data
  const rows = props.rowData || []

  if (rows.length === 0) {
    pinnedTopRowData.value = []
    return
  }

  // Build a map of field -> aggFunc from column definitions
  const leaves = getLeafColumns(props.columnDefs)
  const aggFuncMap: Record<string, { type: string; weightField?: string; numeratorField?: string; denominatorField?: string }> = {}
  for (const col of leaves) {
    if (col.field) {
      const colAny = col as any
      if (colAny.aggFunc) {
        aggFuncMap[col.field] = typeof colAny.aggFunc === 'string' 
          ? { type: colAny.aggFunc } 
          : colAny.aggFunc
      }
    }
  }

  const totalRow: Record<string, any> = {}

  // Calculate aggregates based on aggFunc
  for (const col of leaves) {
    const field = col.field
    if (!field) continue

    const aggConfig = aggFuncMap[field]
    
    if (!aggConfig) {
      // Default: sum for numbers, skip for non-numbers
      const firstVal = rows.find(r => r[field] != null)?.[field]
      if (typeof firstVal === 'number') {
        totalRow[field] = rows.reduce((sum, r) => sum + (Number(r[field]) || 0), 0)
      }
      continue
    }

    switch (aggConfig.type) {
      case 'sum':
        totalRow[field] = rows.reduce((sum, r) => sum + (Number(r[field]) || 0), 0)
        break
      
      case 'count':
        totalRow[field] = rows.filter(r => r[field] != null && r[field] !== '').length
        break
      
      case 'avg':
        const validVals = rows.filter(r => r[field] != null && !isNaN(Number(r[field])))
        totalRow[field] = validVals.length > 0
          ? validVals.reduce((sum, r) => sum + Number(r[field]), 0) / validVals.length
          : 0
        break
      
      case 'weightedAvg':
        // Weighted average using weightField (e.g., purchase_price)
        const wf = aggConfig.weightField || 'purchase_price'
        let totalWeight = 0
        let weightedSum = 0
        for (const r of rows) {
          const val = Number(r[field])
          const weight = Number(r[wf]) || 0
          if (!isNaN(val) && weight > 0) {
            weightedSum += val * weight
            totalWeight += weight
          }
        }
        totalRow[field] = totalWeight > 0 ? Math.round(weightedSum / totalWeight) : 0
        break
      case 'ratioOfSums': {
        // Ratio of sums for percentage fields, e.g. (Σ bid) / (Σ balance) * 100
        const nf = aggConfig.numeratorField
        const df = aggConfig.denominatorField
        if (!nf || !df) {
          totalRow[field] = ''
          break
        }
        let numSum = 0
        let denomSum = 0
        for (const r of rows) {
          const num = Number(r[nf])
          const den = Number(r[df])
          if (!isNaN(num)) numSum += num
          if (!isNaN(den)) denomSum += den
        }
        totalRow[field] = denomSum > 0 ? (numSum / denomSum) * 100 : 0
        break
      }
      
      case 'skip':
        // Don't aggregate this field
        totalRow[field] = ''
        break
      
      default:
        // Unknown aggFunc, default to sum for numbers
        const fv = rows.find(r => r[field] != null)?.[field]
        if (typeof fv === 'number') {
          totalRow[field] = rows.reduce((sum, r) => sum + (Number(r[field]) || 0), 0)
        }
    }
  }

  // WHAT: Label first visible column so the row is clearly a total row
  const firstColField = allColumns.value[0]?.field
  if (firstColField) {
    totalRow[firstColField] = 'Aggregate'
  }

  pinnedTopRowData.value = [totalRow]
}

function onFilterOrSortChanged(): void {
  updatePinnedTopRowFromGrid()
}

/**
 * WHAT: Toggle column visibility
 * WHY: Show/hide columns from management panel
 */
function toggleColumn(field: string): void {
  if (!gridApi.value) return

  const col = allColumns.value.find(c => c.field === field)
  if (!col) return

  col.visible = !col.visible
  gridApi.value.setColumnsVisible([field], col.visible)
}

/**
 * WHAT: Quick filter text changed
 * WHY: Apply search across all columns
 */
const containerClasses = computed(() => ({
  'reporting-ag-grid-container': true,
  'full-window': isFullWindow.value,
}))

const computedGridHeight = computed(() => {
  if (isFullWindow.value) {
    return 'calc(100vh - 180px)'
  }
  return props.gridHeight
})

const fullWindowLabel = computed(() => (isFullWindow.value ? 'Contract' : 'Expand'))

function onQuickFilterChanged(): void {
  if (!gridApi.value) return
  gridApi.value.setGridOption('quickFilterText', quickFilterText.value)
}

/**
 * WHAT: Auto-size all columns
 * WHY: Fit columns to content width
 */
function autoSizeAll(): void {
  if (!gridApi.value) return
  
  gridApi.value.autoSizeAllColumns(false)
}

/**
 * WHAT: Reset grid to default state
 * WHY: Clear filters, sorting, column order
 */
function resetGrid(): void {
  if (!gridApi.value) return

  // WHAT: Clear all filters
  gridApi.value.setFilterModel(null)

  // WHAT: Clear quick filter
  quickFilterText.value = ''
  gridApi.value.setGridOption('quickFilterText', '')

  // WHAT: Reset column state
  gridApi.value.resetColumnState()

  // WHAT: Auto-size columns
  nextTick(() => {
    setTimeout(() => autoSizeAll(), 100)
  })
}

/**
 * WHAT: Export to CSV
 * WHY: Download grid data as CSV file
 */
function exportToCsv(): void {
  console.log('[ReportingAgGrid] Export CSV clicked, hasApi:', !!gridApi.value)
  if (!gridApi.value) return

  gridApi.value.exportDataAsCsv({
    fileName: `report-${new Date().toISOString().split('T')[0]}.csv`,
    columnKeys: allColumns.value.filter(c => c.visible).map(c => c.field),
    skipPinnedTop: true,
  })
}

function handleExportCsv(): void {
  showExportDropdown.value = false
  exportToCsv()
}

/**
 * WHAT: Export to Excel
 * WHY: Download grid data as Excel file (requires ag-grid-enterprise)
 */
function exportToExcel(): void {
  if (!gridApi.value) return

  // WHAT: Check if Excel export is available (enterprise feature)
  // WHY: Fall back to CSV for community edition
  if (typeof (gridApi.value as any).exportDataAsExcel === 'function') {
    (gridApi.value as any).exportDataAsExcel({
      fileName: `report-${new Date().toISOString().split('T')[0]}.xlsx`,
      columnKeys: allColumns.value.filter(c => c.visible).map(c => c.field),
    })
  } else {
    // WHAT: Fallback to CSV export
    console.warn('[AG Grid] Excel export requires ag-grid-enterprise. Falling back to CSV.')
    exportToCsv()
  }
}

/**
 * WHAT: Row clicked event handler
 * WHY: Emit to parent for drill-down functionality
 */
function onRowClicked(event: RowClickedEvent): void {
  emit('rowClicked', event.data)
}

/**
 * WHAT: Selection changed event handler
 * WHY: Emit selected rows to parent
 */
function onSelectionChanged(event: SelectionChangedEvent): void {
  if (!gridApi.value) return
  const selectedRows = gridApi.value.getSelectedRows()
  emit('selectionChanged', selectedRows)
}

/**
 * WHAT: Watch for column def changes
 * WHY: Update column state when parent changes columns
 */
watch(() => props.columnDefs, () => {
  syncColumnState()
}, { deep: true })

function toggleFullWindow(): void {
  isFullWindow.value = !isFullWindow.value
  nextTick(() => {
    if (gridApi.value) {
      gridApi.value.resetRowHeights()
      // Don't auto-fit columns - let them keep their natural widths with horizontal scroll
    }
  })
}

/**
 * WHAT: Watch for loading state changes
 * WHY: Show/hide loading overlay
 */
watch(() => props.loading, (newVal) => {
  if (gridApi.value) {
    gridApi.value.setGridOption('loading', newVal)
  }
})

/**
 * WHAT: Watch for data changes
 * WHY: Show no rows overlay if empty
 */
watch(() => props.rowData, (newData) => {
  if (!gridApi.value) return

  const isLoading = !!gridApi.value.getGridOption('loading')

  if (!newData || newData.length === 0) {
    if (!props.loading && !isLoading) {
      gridApi.value.showNoRowsOverlay()
    }
  } else {
    if (!props.loading && !isLoading) {
      gridApi.value.hideOverlay()
    }
  }

  updatePinnedTopRowFromGrid()
}, { immediate: true })

// WHAT: Expose methods to parent via template ref
// WHY: Allow parent to call grid methods directly
defineExpose({
  gridApi,
  exportToCsv,
  exportToExcel,
  autoSizeAll,
  resetGrid,
})
</script>

<style scoped>
/**
 * WHAT: AG Grid container styles
 * WHY: Proper layout and spacing for grid and toolbar
 */
.reporting-ag-grid-container {
  width: 100%;
}

.reporting-ag-grid-container.full-window {
  position: fixed;
  top: 70px;
  left: 20px;
  right: 20px;
  bottom: 20px;
  z-index: 1050;
  background: #FDFBF7;
  padding: 1rem;
  border-radius: 0.5rem;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
  overflow: hidden;
}

.grid-toolbar {
  padding: 0.5rem;
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 0.25rem;
}

.grid-toolbar .btn-sm {
  font-size: 0.75rem;
  padding: 0.25rem 0.6rem;
  line-height: 1.2;
}

.column-panel {
  max-height: 200px;
  overflow-y: auto;
}

.ag-grid-wrapper {
  width: 100%;
  border: 1px solid #dee2e6;
  border-radius: 0.25rem;
  overflow: hidden;
}

/* WHAT: Visual outline for pinned aggregate row (thick border + subtle background) */
:deep(.ag-row-pinned-top) {
  box-shadow: 0 0 0 3px #495057 inset !important;
  background-color: #e9ecef !important;
}

:deep(.ag-pinned-left-cols-container .ag-row-pinned-top),
:deep(.ag-center-cols-container .ag-row-pinned-top) {
  box-shadow: 0 0 0 3px #495057 inset !important;
  background-color: #e9ecef !important;
}

.grid-status-bar {
  display: flex;
  align-items: center;
  padding: 0.5rem;
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-top: none;
  border-radius: 0 0 0.25rem 0.25rem;
}

/* WHAT: Center-align grid headers and cells (matches existing grids) */
:deep(.reporting-grid .ag-header-cell-label) {
  justify-content: center;
}

:deep(.reporting-grid .ag-cell) {
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
}

/* WHAT: Multi-line header support */
:deep(.reporting-grid .ag-header-cell-text) {
  white-space: normal !important;
  line-height: 1.2;
  word-break: break-word;
}

/* WHAT: Badge styles for grid status */
.badge.bg-primary-lighten {
  background-color: rgba(54, 162, 235, 0.1);
  color: #36a2eb;
  font-weight: 500;
}
</style>

