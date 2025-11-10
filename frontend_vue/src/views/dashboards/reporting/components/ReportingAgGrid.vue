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
  <div class="reporting-ag-grid-container">
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
          <i class="mdi mdi-view-column me-1"></i>
          Columns
        </button>

        <!-- Auto-size All Columns -->
        <button
          class="btn btn-sm btn-outline-secondary"
          @click="autoSizeAll"
          title="Auto-size all columns"
        >
          <i class="mdi mdi-arrow-expand-horizontal"></i>
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
        <!-- Row Count Badge -->
        <span class="badge bg-primary-lighten text-primary align-self-center">
          {{ rowCount }} {{ rowCount === 1 ? 'row' : 'rows' }}
        </span>

        <!-- Export Dropdown -->
        <div class="dropdown">
          <button
            class="btn btn-sm btn-success dropdown-toggle"
            type="button"
            data-bs-toggle="dropdown"
            aria-expanded="false"
          >
            <i class="mdi mdi-download me-1"></i>
            Export
          </button>
          <ul class="dropdown-menu dropdown-menu-end">
            <li>
              <a class="dropdown-item" href="#" @click.prevent="exportToCsv">
                <i class="mdi mdi-file-delimited me-2"></i>
                Export as CSV
              </a>
            </li>
            <li>
              <a class="dropdown-item" href="#" @click.prevent="exportToExcel">
                <i class="mdi mdi-file-excel me-2"></i>
                Export as Excel
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
        :style="{ width: '100%', height: gridHeight }"
        :theme="themeQuartz"
        :columnDefs="columnDefs"
        :rowData="rowData"
        :defaultColDef="defaultColDef"
        :pagination="pagination"
        :paginationPageSize="pageSize"
        :paginationPageSizeSelector="pageSizeOptions"
        :rowSelection="{ mode: rowSelection === 'multiple' ? 'multiRow' : 'singleRow', checkboxes: false, headerCheckbox: false, enableClickSelection: true }"
        :suppressRowClickSelection="false"
        :animateRows="true"
        :enableCellTextSelection="true"
        :loading="loading"
        overlayNoRowsTemplate="No data available"
        overlayLoadingTemplate="Loading..."
        @grid-ready="onGridReady"
        @row-clicked="onRowClicked"
        @selection-changed="onSelectionChanged"
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
  GridReadyEvent,
  RowClickedEvent,
  SelectionChangedEvent 
} from 'ag-grid-community'

// WHAT: Component props interface
// WHY: Define all inputs needed from parent components
interface Props {
  columnDefs: ColDef[]           // WHAT: AG Grid column definitions
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
// WHY: Control toolbar buttons and panels
const showColumnPanel = ref<boolean>(false)
const quickFilterText = ref<string>('')

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
function syncColumnState(): void {
  if (!gridApi.value) return

  allColumns.value = props.columnDefs.map(col => ({
    field: col.field as string,
    headerName: col.headerName || col.field as string,
    visible: col.hide !== true,
  }))
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
  if (!gridApi.value) return

  gridApi.value.exportDataAsCsv({
    fileName: `report-${new Date().toISOString().split('T')[0]}.csv`,
    columnKeys: allColumns.value.filter(c => c.visible).map(c => c.field),
  })
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

/**
 * WHAT: Watch for loading state changes
 * WHY: Show/hide loading overlay
 */
watch(() => props.loading, (newVal) => {
  if (gridApi.value) {
    if (newVal) {
      gridApi.value.showLoadingOverlay()
    } else {
      gridApi.value.hideOverlay()
    }
  }
})

/**
 * WHAT: Watch for data changes
 * WHY: Show no rows overlay if empty
 */
watch(() => props.rowData, (newData) => {
  if (gridApi.value) {
    if (!newData || newData.length === 0) {
      gridApi.value.showNoRowsOverlay()
    } else {
      gridApi.value.hideOverlay()
    }
  }
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

.grid-toolbar {
  padding: 0.5rem;
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 0.25rem;
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

