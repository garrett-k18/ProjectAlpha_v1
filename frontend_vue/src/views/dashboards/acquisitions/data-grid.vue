<template>
  <!--
    Card container to match existing dashboard aesthetics.
    Contains the AG Grid Vue component styled with the Quartz theme.
  -->
  <div class="card">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Seller Data Tape</h4>
      
      <!-- Column visibility controls -->
      <div class="dropdown">
        <button class="btn btn-sm btn-light dropdown-toggle" type="button" id="columnVisibilityMenu" 
                data-bs-toggle="dropdown" aria-expanded="false">
          <i class="mdi mdi-eye-outline me-1"></i> Column Visibility
        </button>
        <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="columnVisibilityMenu">
          <!-- All columns toggle -->
          <li>
            <a class="dropdown-item" href="#" @click.prevent="toggleAllColumns(true)">
              <i class="mdi mdi-eye me-1"></i> Show All
            </a>
          </li>
          <li>
            <a class="dropdown-item" href="#" @click.prevent="toggleAllColumns(false)">
              <i class="mdi mdi-eye-off me-1"></i> Hide All
            </a>
          </li>
          <li><hr class="dropdown-divider"></li>
          <!-- Individual column toggles -->
          <li v-for="col in columnDefs" :key="col.field">
            <a 
              class="dropdown-item" 
              href="#" 
              @click.prevent="col.field && toggleColumnVisibility(col.field)"
            >
              <i :class="['mdi', col.hide ? 'mdi-eye-off' : 'mdi-eye', 'me-1']"></i>
              {{ col.headerName }}
            </a>
          </li>
        </ul>
      </div>
    </div>

    <div class="card-body pt-0">
      <!--
        The AG Grid Vue component. We set a fixed height for the example; adjust as needed.
        The CSS theme class 'ag-theme-quartz' applies the Quartz theme styling.
      -->
      <ag-grid-vue
        ref="gridRef"
        class="seller-grid"  
        style="width: 100%; height: 420px"
        :theme="themeQuartz"
        :rowData="rowData"
        :columnDefs="columnDefs"
        :defaultColDef="defaultColDef"
        :animateRows="true"
        @grid-ready="onGridReady"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
// Import the AG Grid Vue 3 component wrapper
import { AgGridVue } from 'ag-grid-vue3'

// AG Grid v34 Theming API (no CSS-file themes).
// Docs: https://www.ag-grid.com/vue-data-grid/theming-migration/
// Using themeQuartz object instead of CSS imports/classes.
import { themeQuartz } from 'ag-grid-community'

// Import types for better TypeScript support
import type { ColDef } from 'ag-grid-community'
import { ref, onMounted } from 'vue'

// ---------------------------------------------------------------------------
// Column Definitions: describe the columns shown in the grid.
// Each ColDef defines a column's header name, the field in the data, and behavior.
// ---------------------------------------------------------------------------
// Reactive column definitions that will be populated from the backend
// API that exposes Django model field names for SellerRawData.
const columnDefs = ref<ColDef[]>([])

// ---------------------------------------------------------------------------
// Default Column Definition: applied to all columns unless overridden above.
// Enables resizing and basic filtering globally.
// ---------------------------------------------------------------------------
const defaultColDef: ColDef = {
  resizable: true,
  filter: true,
  // Enable floating filters for all columns per AG Grid docs
  // https://www.ag-grid.com/vue-data-grid/filter-floating/
  floatingFilter: true,
}

// ---------------------------------------------------------------------------
// Row Data: example dataset to render in the grid. Replace with real data later.
// Each object represents a row; keys must match the 'field' values in columnDefs.
// ---------------------------------------------------------------------------
// Strongly type rowData as a Vue Ref to satisfy TS lints and enable reactivity
const rowData = ref<Record<string, unknown>[]>([])

// ---------------------------------------------------------------------------
// Utility: Convert a field name (e.g., seller_id, current_balance) to a
// user-friendly header (e.g., Seller Id, Current Balance).
// ---------------------------------------------------------------------------
function prettifyHeader(field: string): string {
  // Replace underscores with spaces and title-case words
  return field
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase())
}

// ---------------------------------------------------------------------------
// On mount, fetch field names from backend and build basic columnDefs.
// Endpoint is served by Django at /api/acq/raw-data/fields/.
// Only field names are used for now as requested; types and formatters can be
// added later.
// ---------------------------------------------------------------------------
// Custom Header Name Mappings
// This allows overriding the default header names generated from field names.
// ---------------------------------------------------------------------------
const headerNameMappings: { [key: string]: string } = {
  id: 'Internal ID', // Corrected 'Id' to 'id' to match the backend field name
  months_dlq: 'Months Delinquent',
  accrued_note_interest: 'Accrued Interest',
  fc_flag: 'FC Flag',
  fc_first_legal_date: 'FC First Legal Date',
  fc_referred_date: 'FC Referred Date',
  fc_judgement_date: 'FC Judgement Date',
  fc_scheduled_sale_date: 'FC Scheduled Sale Date',
  fc_sale_date: 'FC Sale Date',
  fc_starting: 'FC Starting',
  bk_flag: 'BK Flag',
  bk_chapter: 'BK Chapter',

  // Add more custom mappings here as needed
}

// Reference to the AG Grid instance for accessing columnApi
// Import the necessary types from AG Grid for proper typing
// Using type-only imports as required by TypeScript verbatimModuleSyntax
import type { GridApi, GridReadyEvent } from 'ag-grid-community'

// Using proper types for the grid API references
const gridRef = ref<any>(null)
const gridApi = ref<GridApi | null>(null)

/**
 * Event handler for when the grid is ready
 * This is called when the grid is initialized and ready to be interacted with
 * @param params - The grid ready event parameters
 */
const onGridReady = (params: GridReadyEvent) => {
  // Store reference to the grid API
  gridApi.value = params.api
  
  // Log initialization success
  console.log('AG Grid initialized successfully')
}

/**
 * Toggle visibility for a specific column
 * @param fieldName - The field name of the column to toggle
 */
function toggleColumnVisibility(fieldName: string): void {
  if (!gridApi.value) return
  
  // Get current visibility state from our local columnDefs
  const column = columnDefs.value.find(col => col.field === fieldName)
  if (!column) return
  
  const isCurrentlyVisible = !column.hide
  const newVisibility = !isCurrentlyVisible
  
  // Update column state using the Grid API's applyColumnState method
  // This is the recommended approach in AG Grid v34+
  gridApi.value.applyColumnState({
    state: [{ colId: fieldName, hide: newVisibility }],
    defaultState: { hide: false }
  })
  
  // Update our local columnDefs state to keep UI in sync
  columnDefs.value = columnDefs.value.map(col => {
    if (col.field === fieldName) {
      return { ...col, hide: newVisibility }
    }
    return col
  })
  
  // Log the action for debugging
  console.log(`Column '${fieldName}' is now ${newVisibility ? 'hidden' : 'visible'}`)
}

/**
 * Toggle visibility for all columns
 * @param visible - Whether to show or hide all columns
 */
function toggleAllColumns(visible: boolean): void {
  if (!gridApi.value) return
  
  // Get all column IDs - filter out undefined values to satisfy TypeScript
  const allColumnIds = columnDefs.value
    .map(col => col.field)
    .filter((field): field is string => field !== undefined)
  
  // Create state object for each column
  const columnStates = allColumnIds.map(colId => ({
    colId,
    hide: !visible
  }))
  
  // Apply column state using the Grid API
  gridApi.value.applyColumnState({
    state: columnStates,
    defaultState: { hide: !visible }
  })
  
  // Update our local columnDefs state to keep UI in sync
  columnDefs.value = columnDefs.value.map(col => ({
    ...col,
    hide: !visible
  }))
  
  // Log the action for debugging
  console.log(`All columns are now ${visible ? 'visible' : 'hidden'}`)
}

onMounted(async () => {
  try {
    const resp = await fetch('/api/acq/raw-data/fields/', {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
      credentials: 'same-origin',
    })
    if (!resp.ok) throw new Error(`Failed to fetch fields: ${resp.status}`)
    const json = (await resp.json()) as { fields: string[] }

    // Build minimal columnDefs from field names only
    columnDefs.value = json.fields.map((field: string) => ({
      // Use custom mapping if available, otherwise prettify the field name
      headerName: headerNameMappings[field] || prettifyHeader(field),
      field: field,
      sortable: true,
      filter: true,
    }))
    
    // Alternative approach: You can also hide columns after grid initialization
    // using the columnApi. This is useful for dynamic column hiding based on user preferences.
    // Example:
    // setTimeout(() => {
    //   if (gridRef.value?.api) {
    //     const columnApi = gridRef.value.columnApi
    //     columnsToHide.forEach(colId => {
    //       columnApi.setColumnVisible(colId, false)
    //     })
    //   }
    // }, 500) // Small delay to ensure grid is initialized
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error('Error loading SellerRawData fields for AG Grid:', err)
    // Fallback: populate a sensible default set of columns so the grid still renders
    // when the backend is unavailable or returns 500. These fields mirror a subset
    // of the Django `SellerRawData` model in `acq_module/models/seller.py`.
    // This is for development resilience only and can be removed once the API is stable.
    const fallbackFields = [
      // Identifiers
      'seller_id',
      'trade_id',
      'sellertape_id',
      // Status / dates
      'asset_status',
      'as_of_date',
      'next_due_date',
      // Location
      'city',
      'state',
      'zip',
      // Key finance
      'current_balance',
      'interest_rate',
    ]

    // Map fallback fields to AG Grid ColDefs with basic UX settings.
    columnDefs.value = fallbackFields.map((f): ColDef => ({
      field: f,                              // data key
      headerName: prettifyHeader(f),         // user-friendly header
      sortable: true,                        // allow sorting
      filter: true,                          // basic filtering
    }))

    // Optional: you can also set a minimal sample row to verify rendering.
    // Leaving rowData empty will render headers only, which is sufficient for layout.
    // rowData.value = []
  }
})
</script>

<!--
  No component-scoped styles are required as we rely on AG Grid's theme CSS and the
  dashboard's global styling. If needed, you can add local CSS here.
-->
<style scoped>
/*
  Center headers and cell text ONLY for this grid instance.
  We add a wrapper class (seller-grid) to the <ag-grid-vue> element and
  use :deep() to style AG Grid's internal DOM from this component only.
  Docs: https://www.ag-grid.com/javascript-data-grid/theming-headers/
*/

/* Center header captions (label text and icons container) */
:deep(.seller-grid .ag-header-cell .ag-header-cell-label) {
  justify-content: center; /* center flex contents (text + icons) */
  text-align: center;      /* ensure text nodes are centered */
}

/* Center all cell text values */
:deep(.seller-grid .ag-cell) {
  text-align: center;
}

/* Optional: center floating filter inputs as well (if desired) */
/* :deep(.seller-grid .ag-floating-filter-body) {
  justify-content: center;
} */
</style>
