<template>
  <!--
    Card container to match existing dashboard aesthetics.
    Contains the AG Grid Vue component styled with the Quartz theme.
  -->
  <div class="card">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">{{ viewTitle }}</h4>

      <!-- Right-side controls: View selector + Column visibility -->
      <div class="d-flex align-items-center gap-2">
        <!-- View selector to switch between column presets -->
        <div class="d-flex align-items-center">
          <label for="viewSelect" class="me-2 small mb-0">View</label>
          <select
            id="viewSelect"
            class="form-select form-select-sm"
            v-model="activeView"
          >
            <option value="sellerDataTape">Seller Data Tape</option>
            <option value="localAgents">Local Agents</option>
          </select>
        </div>

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

        <!-- Row-level invite checkbox column added; header button removed -->
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
        overlayNoRowsTemplate="Choose Seller and Trade"
        :columnDefs="columnDefs"
        :defaultColDef="defaultColDef"
        rowSelection="multiple"
        :animateRows="true"
        @grid-ready="onGridReady"
        @selection-changed="onSelectionChanged"
      />
      
      <!-- Details modal removed: this component is grid-only by design -->
      <!-- Simple portal results list to surface created URLs -->
      <div v-if="portalResults.length > 0" class="alert alert-info mt-2" role="alert">
        <div class="fw-semibold mb-1">Broker Portal Links</div>
        <ul class="mb-0">
          <li v-for="r in portalResults" :key="r.token">
            Broker {{ r.broker_id }} — {{ r.count }} invite(s):
            <a :href="r.url" target="_blank" rel="noopener">{{ r.url }}</a>
          </li>
        </ul>
        <div class="small text-muted mt-1">Share the portal link with the broker to access all active invites.</div>
      </div>
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
import { useAcqSelectionsStore } from '@/stores/acqSelections'
import { useAgGridRowsStore } from '@/stores/agGridRows'
import { storeToRefs } from 'pinia'
// Centralized Axios instance for API calls
import http from '@/lib/http'
// Actions cell renderer for the first column
import ActionsCell from './components/ActionsCell.vue'
// ID link cell renderer for the internal ID link (no modal logic here)
import IdLinkCell from './components/IdLinkCell.vue'
// Per-row invite checkbox cell renderer
import AssignInviteCell from './components/AssignInviteCell.vue'
// Grid-only: remove modal, tabs, and product image imports

// Grid-only: removed modal sizing and resize listeners

// Grid-only: removed demo images used by modal snapshot tab

// ---------------------------------------------------------------------------
// Props: allow parent to control how the ID link opens (modal vs page)
// - openMode: 'modal' | 'page' (default behavior can be controlled by parent)
// - openLoan: callback invoked when openMode==='modal' to open a parent modal
// This keeps the grid component UI-agnostic while enabling modal-first flows.
// ---------------------------------------------------------------------------
const props = defineProps<{
  openMode?: 'modal' | 'page'
  openLoan?: (payload: { id: string; row: any; addr?: string }) => void
}>()

// ---------------------------------------------------------------------------
// Column Definitions: describe the columns shown in the grid.
// Each ColDef defines a column's header name, the field in the data, and behavior.
// ---------------------------------------------------------------------------
// Reactive column definitions currently applied to the grid
const columnDefs = ref<ColDef[]>([])

// Preserve the default (Seller Data Tape) columns after generation so we can
// switch between views without losing the original definitions.
const sellerDataTapeColumns = ref<ColDef[] | null>(null)

// View selector state: 'sellerDataTape' (default) | 'localAgents'
const activeView = ref<'sellerDataTape' | 'localAgents'>('sellerDataTape')

// Friendly title reflecting the active view
const viewTitle = computed(() => (activeView.value === 'sellerDataTape' ? 'Seller Data Tape' : 'Local Agents'))

// ---------------------------------------------------------------------------
// Default Column Definition: applied to all columns unless overridden above.
// Enables resizing and basic filtering globally.
// ---------------------------------------------------------------------------
const defaultColDef: ColDef = {
  resizable: true,
  filter: true,
  // Allow long header captions to wrap onto multiple lines and
  // automatically grow the header row height to fit.
  // Docs: https://www.ag-grid.com/javascript-data-grid/column-headers/#text-wrapping
  wrapHeaderText: true,
  autoHeaderHeight: true,
  // Enable floating filters for all columns per AG Grid docs
  // https://www.ag-grid.com/vue-data-grid/filter-floating/
  floatingFilter: true,
}

// ---------------------------------------------------------------------------
// Row Data: provided by centralized Pinia store (agGridRows)
// - Keeps data cached by sellerId:tradeId and shared across components
// - We map store refs to local names for minimal template changes
// ---------------------------------------------------------------------------
const gridRowsStore = useAgGridRowsStore()
const { rows: rowData, loadingRows: gridLoading } = storeToRefs(gridRowsStore)

// Selected agent per row (by row id or sellertape_id).
// Persisted in localStorage, namespaced by sellerId and tradeId.
// Keys are normalized to strings to avoid number/string key mismatches after JSON parse.
const selectedAgents = ref<Record<string, string>>({})
// Invited map: tracks whether an invite was created for a given row key.
// Persisted in localStorage per seller/trade so checkboxes remain checked after refresh.
const invitedMap = ref<Record<string, boolean>>({})

// Broker options keyed by state, supplied by backend endpoint
// Store objects so we can retain IDs while showing labels in the select editor
type BrokerOption = { id: number; label: string }
const brokerOptionsByState = ref<Record<string, BrokerOption[]>>({})
// Global label->id lookup to translate cell selections back to broker_id
const labelToIdMap = ref<Record<string, number>>({})

// Track current selection count for enabling the Assign button
const selectedCount = ref<number>(0)
// Latest portal results to display to the user after assignment
const portalResults = ref<Array<{ broker_id: number; url: string; token: string; count: number }>>([])

// ---------------------------------------------------------------------------
// Persistence for Agent selections (per sellerId + tradeId)
// ---------------------------------------------------------------------------
const STORAGE_KEY_PREFIX = 'acq_local_agents_selected_agents'
const INVITED_STORAGE_KEY_PREFIX = 'acq_local_agents_invited'

function storageKey(): string {
  // Use 'null' placeholders to ensure stable keys when IDs are missing
  const sid = selectedSellerId.value ?? 'null'
  const tid = selectedTradeId.value ?? 'null'
  return `${STORAGE_KEY_PREFIX}:${sid}:${tid}`
}

function saveSelectedAgentsToStorage(): void {
  try {
    // Persist the current map for the active seller/trade
    localStorage.setItem(storageKey(), JSON.stringify(selectedAgents.value))
  } catch (e) {
    console.debug('[LocalAgents] Failed to persist selected agents', e)
  }
}

function loadSelectedAgentsFromStorage(): void {
  try {
    const raw = localStorage.getItem(storageKey())
    selectedAgents.value = raw ? (JSON.parse(raw) as Record<string, string>) : {}
  } catch (e) {
    console.debug('[LocalAgents] Failed to load persisted selected agents', e)
    selectedAgents.value = {}
  }
}

// ---------------------------------------------------------------------------
// Persistence for Invite checkbox state (per sellerId + tradeId)
// ---------------------------------------------------------------------------
function invitedStorageKey(): string {
  const sid = selectedSellerId.value ?? 'null'
  const tid = selectedTradeId.value ?? 'null'
  return `${INVITED_STORAGE_KEY_PREFIX}:${sid}:${tid}`
}

function saveInvitedToStorage(): void {
  try {
    localStorage.setItem(invitedStorageKey(), JSON.stringify(invitedMap.value))
  } catch (e) {
    console.debug('[LocalAgents] Failed to persist invited map', e)
  }
}

function loadInvitedFromStorage(): void {
  try {
    const raw = localStorage.getItem(invitedStorageKey())
    invitedMap.value = raw ? (JSON.parse(raw) as Record<string, boolean>) : {}
  } catch (e) {
    console.debug('[LocalAgents] Failed to load invited map', e)
    invitedMap.value = {}
  }
}

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

// Use centralized Pinia store for selections to share state across components
const acqStore = useAcqSelectionsStore()
const { selectedSellerId, selectedTradeId } = storeToRefs(acqStore)

const sellersLoading = ref<boolean>(false)
const tradesLoading = ref<boolean>(false)
// gridLoading now comes from the store

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

// Fields that should behave as the primary clickable ID column to open loan-level details
// Recognize a small, explicit allow-list to avoid making unrelated *_id fields clickable
const clickableIdFields = new Set<string>(['id', 'sellertape_id', 'loan_id'])
function isClickableIdField(field: string): boolean {
  return clickableIdFields.has(field)
}

// Helper to pick a stable row key (prefer 'id', else 'sellertape_id')
function getRowKey(row: any): string | number | undefined {
  if (!row) return undefined
  if (row.id !== undefined && row.id !== null) return row.id as any
  if (row.sellertape_id !== undefined && row.sellertape_id !== null) return row.sellertape_id as any
  return undefined
}

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

// Grid-only: removed modal state and handlers

/**
 * productModalTitle
 * Computes a friendly modal title, including the current record's ID when
 * available. Keeps UX consistent with Hyper UI headings.
 */
// ---------------------------------------------------------------------------
// Title helpers for the Product Details Modal
// - Build a one-line address from common field names present on the row
// - Compose the title as: "<ID> — <Full Address>"
//   (falls back gracefully if some parts are missing)
// ---------------------------------------------------------------------------

// Grid-only: removed address helpers used for modal title

/**
 * productModalTitle
 * Title format: "<ID> — <Full Address>"
 * - If only ID exists, return ID
 * - If only address exists, return address
 * - If neither exists, return empty string (no static prefix)
 * Docs: BootstrapVue3 modal `title` prop and header slot accept any string
 * https://github.com/cdmoro/bootstrap-vue-3#modal
 */
// Grid-only: removed modal title

/**
 * activeProductId
 * Strongly-typed computed accessor for the current row's ID to satisfy
 * TypeScript in template bindings. Ensures we only pass string | number | null.
 * - Returns null when there is no active row or id is not a string/number.
 */
// Grid-only: removed activeProductId used by modal tabs

// Grid-only: removed router navigation logic

// Grid-only: removed modal keyboard shortcuts and watchers

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
 * Update selectedCount when grid selection changes.
 */
function onSelectionChanged(): void {
  if (!gridApi.value) {
    selectedCount.value = 0
    return
  }
  selectedCount.value = gridApi.value.getSelectedRows()?.length || 0
}

// ---------------------------------------------------------------------------
// Local Agents view: curated column set including an "Agent" select editor
// Options are populated by state via backend batch endpoint.
// ---------------------------------------------------------------------------

function formatBrokerLabel(b: { broker_name?: string | null; broker_firm?: string | null; broker_city?: string | null; broker_email?: string | null }): string {
  const name = (b.broker_name || '').trim()
  const firm = (b.broker_firm || '').trim()
  const city = (b.broker_city || '').trim()
  const email = (b.broker_email || '').trim()
  // Label format: "Broker name - broker firm - Broker city" with email fallback
  const parts: string[] = []
  if (name) parts.push(name)
  if (firm) parts.push(firm)
  if (city) parts.push(city)
  const label = parts.join(' - ')
  return label || email
}

function buildAgentColumn(): ColDef {
  return {
    headerName: 'Agent Assignment',
    field: '__agent__',
    editable: true,
    cellEditor: 'agSelectCellEditor' as any,
    cellEditorParams: (params: any) => {
      const st = String(params.data?.state || '').trim().toUpperCase()
      const opts = brokerOptionsByState.value[st] || []
      // agSelectCellEditor accepts a string[]; provide labels for UX
      return { values: opts.map(o => o.label) }
    },
    // Allow single-click to start editing to reinforce that it's a dropdown
    singleClickEdit: true,
    // Display a subtle placeholder when no agent is selected so users know
    // they can interact with this cell. This does NOT change the underlying
    // value; it only affects rendering.
    valueFormatter: (params: any) => {
      const v = (params.value ?? '').toString().trim()
      return v || 'Choose agent…'
    },
    // Add a muted style when the cell has no value to make the placeholder
    // look distinct from a real selection.
    cellClassRules: {
      'agent-placeholder': (p: any) => !p.value || String(p.value).trim() === ''
    },
    // Helpful tooltip: when empty, prompt the user; otherwise show the value
    tooltipValueGetter: (p: any) => {
      const v = (p.value ?? '').toString().trim()
      return v || 'Click to choose an agent'
    },
    // Pointer cursor hints interactivity even before editing
    cellStyle: () => ({ cursor: 'pointer' }),
    // No custom cell class; rely on AG Grid's default caret only while editing
    valueGetter: (params: any) => {
      const key = getRowKey(params.data)
      if (key === undefined) return ''
      const k = String(key)
      return selectedAgents.value[k] || ''
    },
    valueSetter: (params: any) => {
      const key = getRowKey(params.data)
      if (key === undefined) return false
      const k = String(key)
      selectedAgents.value[k] = params.newValue
      // Persist immediately so a hard refresh restores the choice
      saveSelectedAgentsToStorage()
      return true
    },
    width: 240,
    minWidth: 200,
  }
}

// Determine if a row can be assigned (requires an agent selection and valid row id)
function canAssignRow(row: any): boolean {
  const key = getRowKey(row)
  if (key === undefined) return false
  const label = selectedAgents.value[String(key)] || ''
  const brokerId = labelToIdMap.value[label]
  const srdId = Number(row?.id)
  return !!brokerId && Number.isFinite(srdId)
}

// Assign a single row by creating an invite via the batch endpoint
async function assignSingleRow(row: any): Promise<boolean> {
  const key = getRowKey(row)
  if (key === undefined) return false
  const label = selectedAgents.value[String(key)] || ''
  const brokerId = labelToIdMap.value[label]
  const srdId = Number(row?.id)
  if (!brokerId || !Number.isFinite(srdId)) return false
  try {
    const { data } = await http.post<any>('acq/broker-portal/assign/', {
      broker_id: brokerId,
      seller_raw_data_ids: [srdId],
    })
    const portal = data?.portal || {}
    if (portal?.url && portal?.token) {
      const idx = portalResults.value.findIndex(r => r.token === portal.token && r.broker_id === brokerId)
      const item = { broker_id: brokerId, url: portal.url, token: portal.token, count: 1 }
      if (idx >= 0) portalResults.value[idx] = item
      else portalResults.value.push(item)
      // Mark row as invited and persist so the checkbox stays checked
      const k = String(key)
      invitedMap.value[k] = true
      saveInvitedToStorage()
    }
    return true
  } catch (e) {
    console.error('Assign single row failed', e)
    alert('Failed to create invite for this row.')
    return false
  }
}

function buildLocalAgentsColumns(): ColDef[] {
  // Actions column (reuse existing renderer)
  const actionsCol: ColDef = {
    headerName: 'Actions',
    colId: 'actions',
    pinned: 'left',
    sortable: false,
    filter: false,
    suppressHeaderMenuButton: true,
    suppressHeaderContextMenu: true,
    width: 220,
    minWidth: 160,
    cellRenderer: ActionsCell as any,
    cellRendererParams: { onAction: onRowAction },
  }

  // Prefer 'id'; fallback to 'sellertape_id' clickable id
  const idField = 'id'
  const idCol: ColDef = {
    headerName: headerNameMappings[idField] || prettifyHeader(idField),
    field: idField,
    sortable: true,
    filter: true,
    cellRenderer: IdLinkCell as any,
    cellRendererParams: {
      openMode: props.openMode,
      onOpen: props.openLoan,
    },
    width: 120,
    maxWidth: 140,
  }

  // Per-row Invite column to create a token for a single row
  const inviteCol: ColDef = {
    headerName: 'Invite',
    colId: 'invite',
    sortable: false,
    filter: false,
    width: 100,
    maxWidth: 120,
    cellRenderer: AssignInviteCell as any,
    cellRendererParams: {
      onAssign: assignSingleRow,
      canAssign: canAssignRow,
      isInvited: (row: any) => {
        const key = getRowKey(row)
        if (key === undefined) return false
        return !!invitedMap.value[String(key)]
      },
    },
  }

  const cols: ColDef[] = [
    actionsCol,
    idCol,
    { headerName: 'Address', field: 'street_address', sortable: true, filter: true },
    { headerName: 'City', field: 'city', sortable: true, filter: true },
    { headerName: 'State', field: 'state', sortable: true, filter: true, width: 110, maxWidth: 120 },
    { headerName: 'Current Balance', field: 'current_balance', sortable: true, filter: true, valueFormatter: numberNoDecimalFormatter, width: 160 },
    { headerName: 'Total Debt', field: 'total_debt', sortable: true, filter: true, valueFormatter: numberNoDecimalFormatter, width: 140 },
    { headerName: 'Seller As Is', field: 'seller_asis_value', sortable: true, filter: true, valueFormatter: numberNoDecimalFormatter, width: 140 },
    { headerName: 'Seller ARV', field: 'seller_arv_value', sortable: true, filter: true, valueFormatter: numberNoDecimalFormatter, width: 140 },
    buildAgentColumn(),
    inviteCol,
  ]

  return cols
}

function applyViewColumns(view: 'sellerDataTape' | 'localAgents') {
  if (view === 'sellerDataTape') {
    // Restore original generated columns
    if (sellerDataTapeColumns.value) {
      columnDefs.value = sellerDataTapeColumns.value
    }
  } else {
    // Switch to curated Local Agents set
    columnDefs.value = buildLocalAgentsColumns()
  }
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

/**
 * Handle actions from the ActionsCell buttons. Replace the
 * console logs with modal open logic as needed.
 */
function onRowAction(action: string, row: any): void {
  // TODO: Integrate your modal system here
  // eslint-disable-next-line no-console
  console.log(`[Grid] action=\\"${action}\\"`, row)
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
    const generated = json.fields.map((field: string) => {
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
      // Render the primary ID as a clickable link using a dedicated cell renderer
      if (isClickableIdField(field)) {
        base.cellRenderer = IdLinkCell as any
        // Pass behavior controls to the cell renderer
        base.cellRendererParams = {
          openMode: props.openMode,
          onOpen: props.openLoan,
        }
        // Debug which field is wired as the ID link
        console.debug('[Grid] Configured ID link cell renderer for field', field)
        // Keep ID narrow by default
        base.width = 120
        base.maxWidth = 140
      }
      // Encourage header wrapping on specific columns by setting a smaller width
      if (field === 'current_balance') {
        base.width = 140
        base.maxWidth = 160
      }
      return base
    })

    // Prepend an Actions column with a Vue cell renderer
    const actionsCol: ColDef = {
      headerName: 'Actions',
      colId: 'actions',
      pinned: 'left',
      sortable: false,
      filter: false,
      // AG Grid v34+: disable the header menu button and header context menu
      suppressHeaderMenuButton: true,
      suppressHeaderContextMenu: true,
      width: 220,
      minWidth: 160,
      cellRenderer: ActionsCell as any,
      cellRendererParams: { onAction: onRowAction },
    }

    columnDefs.value = [actionsCol, ...generated]
    // Preserve as the default view's columns
    sellerDataTapeColumns.value = columnDefs.value
    
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
    // Per request: no fallbacks — if dynamic column load fails, exit early.
    return
  }

  // Always try to load sellers for the first dropdown after column setup
  await fetchSellers()

  // Apply initial view columns after defaults are prepared
  applyViewColumns(activeView.value)

  // Load any persisted Agent selections for the current seller/trade
  loadSelectedAgentsFromStorage()
  // Load invited state for the current seller/trade
  loadInvitedFromStorage()
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

// fetchGridData is now provided by the agGridRows store (fetchRows)

// ---------------------------------------------------------------------------
// Watchers: react to selection changes
// - When seller changes: reset trade selection and fetch trades for that seller
// - When either selection changes: if both selected, load grid data
// ---------------------------------------------------------------------------
watch(selectedSellerId, async (newSellerId) => {
  // Clear previous dependent state
  selectedTradeId.value = null
  trades.value = []
  // Clear grid rows via store when seller changes
  gridRowsStore.resetRows()
  // Also clear markers when seller changes
  acqStore.resetMarkers()

  // If a seller is chosen, load trades for that seller
  if (newSellerId) {
    await fetchTrades(newSellerId)
  }
})

watch([selectedSellerId, selectedTradeId], async ([sellerId, tradeId]) => {
  // Only fetch when both selections are truthy
  if (sellerId && tradeId) {
    // Load grid rows via centralized store (with caching)
    await gridRowsStore.fetchRows(sellerId, tradeId)
    // Fetch geocoded markers for US map when both IDs are set
    await acqStore.fetchMarkers()
  } else {
    // If either selection is missing, clear the grid to enforce data siloing
    gridRowsStore.resetRows()
    // Also reset markers when selection incomplete
    acqStore.resetMarkers()
  }
})

// When row data changes, gather distinct states and fetch broker options batch
watch(rowData, async (rows) => {
  if (!Array.isArray(rows) || rows.length === 0) {
    brokerOptionsByState.value = {}
    return
  }
  // Only fetch broker options when Local Agents view is relevant or prefetch anyway
  const states = Array.from(new Set((rows as any[])
    .map(r => (r && r.state ? String(r.state).trim().toUpperCase() : ''))
    .filter(Boolean)
  ))
  if (states.length === 0) return
  await fetchBrokerOptionsByStates(states)
})

// Reload persisted Agent selections when seller or trade changes
watch([selectedSellerId, selectedTradeId], () => {
  loadSelectedAgentsFromStorage()
  loadInvitedFromStorage()
})

// Switch columns when the active view changes
watch(activeView, async (v) => {
  applyViewColumns(v)
  // If switching to Local Agents and we already have rows, ensure broker options are loaded
  if (v === 'localAgents' && Array.isArray(rowData.value) && rowData.value.length > 0) {
    const states = Array.from(new Set((rowData.value as any[])
      .map(r => (r && r.state ? String(r.state).trim().toUpperCase() : ''))
      .filter(Boolean)
    ))
    if (states.length > 0) {
      await fetchBrokerOptionsByStates(states)
    }
  }
})

// Fetch broker options by state via backend batch endpoint
async function fetchBrokerOptionsByStates(states: string[]): Promise<void> {
  try {
    const qp = encodeURIComponent(states.join(','))
    // Use Axios instance (baseURL='/api') -> GET /api/acq/broker-invites/by-state-batch/
    const { data: json } = await http.get<any>(`acq/broker-invites/by-state-batch/`, {
      params: { states: states.join(',') },
    })
    const results = (json && json.results) || {}
    const mapped: Record<string, BrokerOption[]> = {}
    const labelIndex: Record<string, number> = {}
    for (const [state, arr] of Object.entries(results)) {
      const upper = state.toUpperCase()
      const list: BrokerOption[] = []
      if (Array.isArray(arr)) {
        for (const b of arr as any[]) {
          const label = formatBrokerLabel(b)
          if (!label || !label.trim()) continue
          const id = Number(b?.id)
          if (!Number.isFinite(id)) continue
          list.push({ id, label })
          // Maintain a fast label->id lookup (labels are effectively unique per our dedupe rules)
          if (labelIndex[label] === undefined) labelIndex[label] = id
        }
      }
      mapped[upper] = list
    }
    brokerOptionsByState.value = mapped
    labelToIdMap.value = labelIndex
  } catch (e) {
    console.error('Failed to load brokers by state', e)
    brokerOptionsByState.value = {}
    labelToIdMap.value = {}
  }
}

// ---------------------------------------------------------------------------
// Assign Selected: group selected SRD rows by chosen agent and POST invites
// Endpoint (DRF): POST /api/acq/broker-portal/assign/
// Body: { broker_id: number, seller_raw_data_ids: number[], expires_in_hours?, portal_expires_in_hours? }
// Docs reviewed:
// - DRF Views/Serializers: https://www.django-rest-framework.org/api-guide/serializers/
// - AG Grid Selection API: https://www.ag-grid.com/vue-data-grid/row-selection/
// ---------------------------------------------------------------------------
async function assignSelected(): Promise<void> {
  if (!gridApi.value) return
  const rows = gridApi.value.getSelectedRows() || []
  if (rows.length === 0) {
    alert('Please select at least one row.')
    return
  }

  // Build groups keyed by broker label (as stored in selectedAgents)
  const groups = new Map<number, number[]>() // broker_id -> srd ids
  const missing: Array<string | number> = []

  for (const r of rows as any[]) {
    const key = getRowKey(r)
    if (key === undefined) continue
    const label = selectedAgents.value[String(key)] || ''
    if (!label) {
      missing.push(key as any)
      continue
    }
    const brokerId = labelToIdMap.value[label]
    if (!brokerId) {
      console.warn('No broker_id found for label', label)
      missing.push(key as any)
      continue
    }
    const srdId = Number(r?.id)
    if (!Number.isFinite(srdId)) continue
    const list = groups.get(brokerId) || []
    list.push(srdId)
    groups.set(brokerId, list)
  }

  if (groups.size === 0) {
    alert('No rows had an assigned agent. Use the Agent Assignment column to choose an agent per row.')
    return
  }

  const results: Array<{ broker_id: number; url: string; token: string; count: number }> = []
  for (const [broker_id, seller_raw_data_ids] of groups.entries()) {
    try {
      const { data } = await http.post<any>('acq/broker-portal/assign/', {
        broker_id,
        seller_raw_data_ids,
      })
      const portal = data?.portal || {}
      if (portal?.url && portal?.token) {
        results.push({ broker_id, url: portal.url, token: portal.token, count: seller_raw_data_ids.length })
      }
    } catch (e: any) {
      console.error('Assign API failed for broker', broker_id, e)
      alert(`Failed to assign ${seller_raw_data_ids.length} rows to broker ${broker_id}.`)
    }
  }

  portalResults.value = results
  if (results.length > 0) {
    // Basic acknowledgement; results are shown below the grid
    console.log('Broker portal URLs created:', results)
  }
}
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

/* Subtle placeholder appearance for empty Agent cells */
:deep(.seller-grid .agent-placeholder) {
  color: #6c757d;       /* muted gray similar to Bootstrap text-muted */
  font-style: italic;   /* differentiate from real selections */
}

/* Agent cell text in blue when a value is selected (non-placeholder) */
:deep(.seller-grid .ag-cell[col-id="__agent__"]:not(.agent-placeholder)) {
  color: #2563eb; /* tailwind blue-600 */
}

/* Subtle blue border around Agent cells (no background) */
:deep(.seller-grid .ag-cell[col-id="__agent__"]) {
  box-shadow: inset 0 0 0 1px rgba(37, 99, 235, 0.35); /* blue-600 @ 35% */
  border-radius: 6px; /* gentle rounding */
}

/* Slightly stronger border on hover/focus for clarity */
:deep(.seller-grid .ag-cell[col-id="__agent__"]:hover),
:deep(.seller-grid .ag-cell[col-id="__agent__"].ag-cell-focus) {
  box-shadow: inset 0 0 0 1.5px rgba(37, 99, 235, 0.6);
}
/* Custom persistent chevron removed per request; default AG Grid icon shows only while editing */
</style>

<style>
/* Global styles intentionally left empty; no modal styles in grid component */
</style>
