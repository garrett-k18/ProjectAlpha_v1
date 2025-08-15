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
        Filter controls row:
        - Seller dropdown (populated from /api/acq/sellers/)
        - Trade dropdown (depends on seller, populated from /api/acq/trades/{sellerId}/)
        Data is only loaded into the grid when BOTH seller and trade are selected.
      -->
      <div class="row g-2 align-items-end mb-3">
        <!-- Seller selector: choose a seller first -->
        <div class="col-12 col-md-4">
          <label class="form-label" for="sellerSelect">Seller</label>
          <select
            id="sellerSelect"
            class="form-select"
            v-model="selectedSellerId"
            :disabled="sellersLoading"
          >
            <option :value="null">Select a seller</option>
            <option v-for="s in sellers" :key="s.id" :value="s.id">{{ s.name }}</option>
          </select>
        </div>

        <!-- Trade selector: populated after a seller is chosen -->
        <div class="col-12 col-md-4">
          <label class="form-label" for="tradeSelect">Trade</label>
          <select
            id="tradeSelect"
            class="form-select"
            v-model="selectedTradeId"
            :disabled="!selectedSellerId || tradesLoading"
          >
            <option :value="null">Select a trade</option>
            <option v-for="t in trades" :key="t.id" :value="t.id">{{ t.trade_name }}</option>
          </select>
        </div>

        <!-- Status / helper text area -->
        <div class="col-12 col-md-4">
          <div class="form-text">
            <!-- Provide simple status guidance for users -->
            <span v-if="sellersLoading">Loading sellers…</span>
            <span v-else-if="selectedSellerId && tradesLoading">Loading trades…</span>
            <span v-else-if="selectedSellerId && !selectedTradeId">Select a trade to view data.</span>
            <span v-else-if="!selectedSellerId">Select a seller to begin.</span>
          </div>
        </div>
      </div>

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
import type { ColDef, ValueFormatterParams } from 'ag-grid-community'
import { ref, onMounted, watch, computed } from 'vue'

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
// Dropdown data sources and selection state
// - sellers: options for the seller dropdown
// - trades: options for the trade dropdown (depends on selected seller)
// - selectedSellerId / selectedTradeId: the chosen IDs
// - loading flags: indicate network activity
// ---------------------------------------------------------------------------
interface SellerOption { id: number; name: string }
interface TradeOption { id: number; trade_name: string }

const sellers = ref<SellerOption[]>([])
const trades = ref<TradeOption[]>([])

const selectedSellerId = ref<number | null>(null)
const selectedTradeId = ref<number | null>(null)

const sellersLoading = ref<boolean>(false)
const tradesLoading = ref<boolean>(false)
const gridLoading = ref<boolean>(false)

// Whether we have both IDs selected (i.e., grid is allowed to load data)
const hasBothSelections = computed(() => !!selectedSellerId.value && !!selectedTradeId.value)

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

// ---------------------------------------------------------------------------
// Display formatters and field typing helpers
// - Keep backend values raw; UI handles presentation per AG Grid docs
//   https://www.ag-grid.com/vue-data-grid/value-formatters/
// - Dates: MM/DD/YYYY (US style)
// - Percents: 2 decimals, auto-multiply if value appears fractional
// - Currency-like: commas, no decimals (uses Intl.NumberFormat)
// ---------------------------------------------------------------------------

// Fields that should show thousand separators with no decimals (currency-like)
const commaNoDecimalFields = new Set<string>([
  'current_balance',
  'original_balance',
  'deferred_balance',
  'accrued_note_interest',
  'accrued_default_interest',
  'escrow_balance',
  'mod_initial_balance',
  'total_debt',
])

// Fields that should display as dates in MM/DD/YYYY
const dateFields = new Set<string>([
  'as_of_date',
  'next_due_date',
  'origination_date',
  'maturity_date',
  'first_payment_date',
  'last_payment_date',
])

// Fields that should display as percents with two decimals
const percentFields = new Set<string>([
  'interest_rate',
  'discount_rate',
  'cap_rate',
])

/**
 * formatNumberNoDecimals
 * Renders a value with thousand separators and no decimal places.
 * Leaves non-numeric inputs untouched (except null/undefined -> empty string).
 */
function formatNumberNoDecimals(value: unknown): string {
  const num = typeof value === 'number' ? value : parseFloat(String(value))
  if (Number.isNaN(num)) {
    return value === null || value === undefined ? '' : String(value)
  }
  return new Intl.NumberFormat(undefined, {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(num)
}

// AG Grid valueFormatter wrapper to use in ColDefs
function numberNoDecimalFormatter(params: ValueFormatterParams): string {
  return formatNumberNoDecimals(params.value)
}

/**
 * formatDateMMDDYYYY
 * Safely formats a value into MM/DD/YYYY using Intl.DateTimeFormat.
 * Accepts Date, timestamp, or parseable string.
 */
function formatDateMMDDYYYY(value: unknown): string {
  if (value === null || value === undefined || value === '') return ''
  const d = value instanceof Date ? value : new Date(String(value))
  if (isNaN(d.getTime())) return String(value)
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(d)
}

// AG Grid valueFormatter for dates
function dateMMDDYYYYFormatter(params: ValueFormatterParams): string {
  return formatDateMMDDYYYY(params.value)
}

/**
 * formatPercentTwoDecimals
 * Formats a numeric value as a percentage with two decimals.
 * If |value| <= 1, assumes fractional and multiplies by 100.
 */
function formatPercentTwoDecimals(value: unknown): string {
  const num = typeof value === 'number' ? value : parseFloat(String(value))
  if (Number.isNaN(num)) return value === null || value === undefined ? '' : String(value)
  const normalized = Math.abs(num) <= 1 ? num * 100 : num
  return `${normalized.toFixed(2)}%`
}

// AG Grid valueFormatter for percents
function percentTwoDecimalFormatter(params: ValueFormatterParams): string {
  return formatPercentTwoDecimals(params.value)
}

// Simple name-based heuristics for resilience if backend field names evolve
function isLikelyDateField(field: string): boolean {
  const lc = field.toLowerCase()
  return lc.endsWith('_date') || lc.includes('date')
}

function isLikelyPercentField(field: string): boolean {
  const lc = field.toLowerCase()
  return lc.includes('rate') || lc.endsWith('_pct') || lc.endsWith('_percent')
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
    // Fetch column field names for grid definition
    const resp = await fetch('/api/acq/raw-data/fields/', {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
      credentials: 'same-origin',
    })
    if (!resp.ok) throw new Error(`Failed to fetch fields: ${resp.status}`)
    const json = (await resp.json()) as { fields: string[] }

    // Build minimal columnDefs from field names only
    columnDefs.value = json.fields.map((field: string) => {
      // Base definition shared by all fields
      const base: ColDef = {
        headerName: headerNameMappings[field] || prettifyHeader(field),
        field: field,
        sortable: true,
        filter: true,
      }
      // Attach display formatters (do not change underlying values used by sorting/filtering)
      // Priority: explicit sets > heuristics; first match wins
      if (!base.valueFormatter && commaNoDecimalFields.has(field)) {
        base.valueFormatter = numberNoDecimalFormatter
      }
      if (!base.valueFormatter && (dateFields.has(field) || isLikelyDateField(field))) {
        base.valueFormatter = dateMMDDYYYYFormatter
      }
      if (!base.valueFormatter && (percentFields.has(field) || isLikelyPercentField(field))) {
        base.valueFormatter = percentTwoDecimalFormatter
      }
      return base
    })
    
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

    // Map fallback fields to AG Grid ColDefs with basic UX settings + formatters
    columnDefs.value = fallbackFields.map((f): ColDef => {
      const col: ColDef = {
        field: f,                              // data key
        headerName: prettifyHeader(f),         // user-friendly header
        sortable: true,                        // allow sorting
        filter: true,                          // basic filtering
      }
      if (!col.valueFormatter && commaNoDecimalFields.has(f)) {
        col.valueFormatter = numberNoDecimalFormatter
      }
      if (!col.valueFormatter && (dateFields.has(f) || isLikelyDateField(f))) {
        col.valueFormatter = dateMMDDYYYYFormatter
      }
      if (!col.valueFormatter && (percentFields.has(f) || isLikelyPercentField(f))) {
        col.valueFormatter = percentTwoDecimalFormatter
      }
      return col
    })

    // Optional: you can also set a minimal sample row to verify rendering.
    // Leaving rowData empty will render headers only, which is sufficient for layout.
    // rowData.value = []
  }

  // Always try to load sellers for the first dropdown after column setup
  await fetchSellers()
})

// ---------------------------------------------------------------------------
// Networking helpers: fetch sellers, trades (by seller), and grid row data
// All functions include defensive checks and extensive comments for clarity.
// ---------------------------------------------------------------------------
async function fetchSellers(): Promise<void> {
  // Guard: prevent duplicate concurrent requests
  if (sellersLoading.value) return
  sellersLoading.value = true
  try {
    const resp = await fetch('/api/acq/sellers/', {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
      credentials: 'same-origin',
    })
    if (!resp.ok) throw new Error(`Failed to fetch sellers: ${resp.status}`)
    const data = (await resp.json()) as SellerOption[]
    sellers.value = data
  } catch (e) {
    console.error('Failed to load sellers', e)
    sellers.value = []
  } finally {
    sellersLoading.value = false
  }
}

async function fetchTrades(sellerId: number): Promise<void> {
  // Guard: require a valid sellerId
  if (!sellerId) {
    trades.value = []
    return
  }
  tradesLoading.value = true
  try {
    const resp = await fetch(`/api/acq/trades/${sellerId}/`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
      credentials: 'same-origin',
    })
    if (!resp.ok) throw new Error(`Failed to fetch trades: ${resp.status}`)
    const data = (await resp.json()) as TradeOption[]
    trades.value = data
  } catch (e) {
    console.error('Failed to load trades', e)
    trades.value = []
  } finally {
    tradesLoading.value = false
  }
}

async function fetchGridData(sellerId: number, tradeId: number): Promise<void> {
  // Guard: require both IDs; if not present, clear the grid
  if (!sellerId || !tradeId) {
    rowData.value = []
    return
  }
  gridLoading.value = true
  try {
    const resp = await fetch(`/api/acq/raw-data/${sellerId}/${tradeId}/`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
      credentials: 'same-origin',
    })
    if (!resp.ok) throw new Error(`Failed to fetch grid data: ${resp.status}`)
    const data = (await resp.json()) as Record<string, unknown>[]
    rowData.value = data
  } catch (e) {
    console.error('Failed to load grid data', e)
    rowData.value = []
  } finally {
    gridLoading.value = false
  }
}

// ---------------------------------------------------------------------------
// Watchers: react to selection changes
// - When seller changes: reset trade selection and fetch trades for that seller
// - When either selection changes: if both selected, load grid data
// ---------------------------------------------------------------------------
watch(selectedSellerId, async (newSellerId) => {
  // Clear previous dependent state
  selectedTradeId.value = null
  trades.value = []
  rowData.value = []

  // If a seller is chosen, load trades for that seller
  if (newSellerId) {
    await fetchTrades(newSellerId)
  }
})

watch([selectedSellerId, selectedTradeId], async ([sellerId, tradeId]) => {
  // Only fetch when both selections are truthy
  if (sellerId && tradeId) {
    await fetchGridData(sellerId, tradeId)
  } else {
    // If either selection is missing, clear the grid to enforce data siloing
    rowData.value = []
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
