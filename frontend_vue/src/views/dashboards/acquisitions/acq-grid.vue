<template>
  <!-- Simplified Acquisitions Grid (refactor trial) -->
  <div class="card" ref="cardRef" :class="{ 'fullscreen-card': isFullscreen }">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Acquisitions – {{ viewTitle }}</h4>
      <div class="d-flex align-items-center gap-2">
        <!-- View selector -->
        <label for="viewSelect" class="me-1 small mb-0">View</label>
        <select id="viewSelect" class="form-select form-select-sm" v-model="activeView" @change="applyView">
          <option value="snapshot">Snapshot</option>
          <option value="all">All</option>
          <option value="valuations">Valuations</option>
        </select>
        <!-- Fullscreen toggle -->
        <button class="btn btn-sm btn-light" :title="isFullscreen ? 'Exit Full Page' : 'Full Page'" @click="toggleFullscreen">
          <i class="mdi" :class="isFullscreen ? 'mdi-fullscreen-exit' : 'mdi-fullscreen'" />
        </button>
      </div>
    </div>

    <div class="card-body pt-0">
      <ag-grid-vue
        ref="gridRef"
        class="acq-grid"
        :style="gridStyle"
        :theme="themeQuartz"
        :rowData="rowData"
        :columnDefs="columnDefs"
        :defaultColDef="defaultColDef"
        :rowSelection="{ mode: 'multiRow', checkboxes: false, headerCheckbox: false, enableClickSelection: true }"
        overlayNoRowsTemplate="No rows"
        @grid-ready="onGridReady"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { AgGridVue } from 'ag-grid-vue3'
import { themeQuartz } from 'ag-grid-community'
import type { ColDef, GridReadyEvent, GridApi } from 'ag-grid-community'
import { ref, computed, nextTick, watch } from 'vue'
import { storeToRefs } from 'pinia'
import ActionsCell from '@/views/dashboards/acquisitions/components/ActionsCell.vue'
import BadgeCell from '@/views/dashboards/acquisitions/components/BadgeCell.vue'
import { useAcqSelectionsStore } from '@/stores/acqSelections'
import { useAgGridRowsStore } from '@/stores/agGridRows'

/* --------------------------------------------------------------------------
 * Pinned-left constant columns (order matters)
 * -------------------------------------------------------------------------- */
const constantColumns: ColDef[] = [
  {
    headerName: 'Actions',
    colId: 'actions',
    pinned: 'left',
    width: 220,
    minWidth: 210,
    lockPosition: true,
    suppressMovable: true,
    sortable: false,
    filter: false,
    suppressHeaderContextMenu: true,
    cellRenderer: ActionsCell as any,
    cellRendererParams: { onAction: onRowAction },
  },
  { headerName: 'Seller ID', field: 'sellertape_id', pinned: 'left', minWidth: 90 },
  {
    headerName: 'Property Address',
    colId: 'address',
    pinned: 'left',
    minWidth: 260,
    wrapHeaderText: true,
    autoHeaderHeight: true,
    headerClass: ['ag-left-aligned-header', 'text-start'],
    cellClass: ['ag-left-aligned-cell', 'text-start'],
    valueGetter: (p: any) => {
      const s = (p.data?.street_address || '').toString().trim()
      const c = (p.data?.city || '').toString().trim()
      const st = (p.data?.state || '').toString().trim()
      return [s, c, st].filter(Boolean).join(', ')
    },
  },
]

/* --------------------------------------------------------------------------
 * All dynamic columns defined once here – easy to rename & reuse
 * -------------------------------------------------------------------------- */
const cols: Record<string, ColDef> = {
  // Category badges with subtle professional colors
  property_type: {
    headerName: 'Property Type',
    field: 'property_type',
    minWidth: 140,
    cellRenderer: BadgeCell as any,
    cellRendererParams: {
      mode: 'enum',
      enumMap: {
        'SFR': { label: 'SFR', color: 'bg-secondary', title: 'Single Family Residence' },
        'Manufactured': { label: 'Manufactured', color: 'bg-info', title: 'Manufactured Home' },
        'Condo': { label: 'Condo', color: 'bg-primary', title: 'Condominium' },
        '2-4 Family': { label: '2-4 Family', color: 'bg-warning text-dark', title: '2-4 Family Property' },
        'Land': { label: 'Land', color: 'bg-dark', title: 'Vacant Land' },
        'Multifamily 5+': { label: 'Multifamily 5+', color: 'bg-secondary', title: 'Multifamily 5+ Units' },
      },
    },
  },
  occupancy: {
    headerName: 'Occupancy',
    field: 'occupancy',
    minWidth: 130,
    cellRenderer: BadgeCell as any,
    cellRendererParams: {
      mode: 'enum',
      enumMap: {
        'Vacant': { label: 'Vacant', color: 'bg-danger', title: 'Property is Vacant' },
        'Occupied': { label: 'Occupied', color: 'bg-success', title: 'Property is Occupied' },
        'Unknown': { label: 'Unknown', color: 'bg-warning text-dark', title: 'Occupancy Status Unknown' },
      },
    },
  },
  // Asset status badges (professional subdued colors)
  asset_status: {
    headerName: 'Asset Status',
    field: 'asset_status',
    minWidth: 140,
    cellRenderer: BadgeCell as any,
    cellRendererParams: {
      mode: 'enum',
      enumMap: {
        'NPL': { label: 'NPL', color: 'bg-danger', title: 'Non-Performing Loan' },
        'REO': { label: 'REO', color: 'bg-secondary', title: 'Real Estate Owned' },
        'PERF': { label: 'PERF', color: 'bg-success', title: 'Performing' },
        'RPL': { label: 'RPL', color: 'bg-info', title: 'Re-Performing Loan' },
      },
    },
  },
  seller_asis_value: { headerName: 'Seller AIV', field: 'seller_asis_value', minWidth: 140, valueFormatter: currency0 },
  seller_arv_value: { headerName: 'Seller ARV', field: 'seller_arv_value', minWidth: 140, valueFormatter: currency0 },
  // Origination value (from serializer)
  origination_value: { headerName: 'Origination AIV', field: 'origination_value', minWidth: 140, valueFormatter: currency0 },
  seller_value_date: { headerName: 'Seller Value Date', field: 'seller_value_date', valueFormatter: dateFmt, minWidth: 140 },
  current_balance: { headerName: 'Current Balance', field: 'current_balance', valueFormatter: currency0, minWidth: 140 },
  interest_rate: { headerName: 'Interest Rate', field: 'interest_rate', valueFormatter: percentFmt, minWidth: 110 },
  total_debt: { headerName: 'Total Debt', field: 'total_debt', valueFormatter: currency0, minWidth: 140 },
  months_dlq: { headerName: 'Months DLQ', field: 'months_dlq', minWidth: 130 },
  next_due_date: { headerName: 'Next Due Date', field: 'next_due_date', valueFormatter: dateFmt, minWidth: 140 },
  // Flag badges with requested colors: Yes=red, No=yellow
  fc_flag: {
    headerName: 'FC Flag',
    field: 'fc_flag',
    minWidth: 100,
    cellRenderer: BadgeCell as any,
    cellRendererParams: { mode: 'boolean', booleanYesColor: 'bg-danger', booleanNoColor: 'bg-secondary' },
  },
  bk_flag: {
    headerName: 'BK Flag',
    field: 'bk_flag',
    minWidth: 100,
    cellRenderer: BadgeCell as any,
    cellRendererParams: { mode: 'boolean', booleanYesColor: 'bg-danger', booleanNoColor: 'bg-secondary' },
  },
  mod_flag: {
    headerName: 'MOD Flag',
    field: 'mod_flag',
    minWidth: 100,
    cellRenderer: BadgeCell as any,
    cellRendererParams: { mode: 'boolean', booleanYesColor: 'bg-danger', booleanNoColor: 'bg-secondary' },
  },
  // Local Agents columns
  agent_name: { headerName: 'Broker', field: 'agent_name', minWidth: 140 },
  bid_amount: { headerName: 'Bid Amount', field: 'bid_amount', valueFormatter: currency0, minWidth: 140 },
  // Valuations (unified from backend serializer)
  broker_asis_value: { headerName: 'Broker AIV', field: 'broker_asis_value', minWidth: 140, valueFormatter: currency0 },
  broker_arv_value: { headerName: 'Broker ARV', field: 'broker_arv_value', minWidth: 140, valueFormatter: currency0 },
  internal_initial_uw_asis_value: { headerName: 'Internal UW AIV', field: 'internal_initial_uw_asis_value', minWidth: 140, valueFormatter: currency0 },
  internal_initial_uw_arv_value: { headerName: 'Internal UW ARV', field: 'internal_initial_uw_arv_value', minWidth: 140, valueFormatter: currency0 },
}

/* --------------------------------------------------------------------------
 * View presets – simple arrays of keys from cols map
 * -------------------------------------------------------------------------- */
const presets: Record<'snapshot' | 'all' | 'valuations', ColDef[]> = {
  snapshot: [
    cols.asset_status,
    cols.property_type,
    cols.occupancy,
    cols.seller_asis_value,
    cols.seller_arv_value,
    cols.seller_value_date,
    cols.current_balance,
    cols.interest_rate,
    cols.total_debt,
    cols.months_dlq,
    cols.next_due_date,
    cols.fc_flag,
    cols.bk_flag,
    cols.mod_flag,
  ],
  valuations: [
    // Seller valuations
    cols.agent_name,
    cols.seller_asis_value,
    cols.seller_arv_value,
    // Broker valuations
    cols.broker_asis_value,
    cols.broker_arv_value,
    // Internal Initial UW valuations
    cols.internal_initial_uw_asis_value,
    cols.internal_initial_uw_arv_value,
    // Context columns for this view
    
  ],
  all: Object.values(cols),
}

/* -------------------------------------------------------------------------- */
const activeView = ref<'snapshot' | 'all' | 'valuations'>('snapshot')
const viewTitle = computed(() => {
  const titles: Record<typeof activeView.value, string> = {
    snapshot: 'Snapshot',
    all: 'All Properties',
    valuations: 'Valuations'
  }
  return titles[activeView.value]
})
const columnDefs = ref<ColDef[]>([...constantColumns, ...presets[activeView.value]])

function applyView(): void {
  columnDefs.value = [...constantColumns, ...presets[activeView.value]]
  nextTick(() => updateGridSize())
}

/* --------------------------------------------------------------------------
 * Row data: sourced from Pinia stores (selections + cached rows)
 * Endpoint: GET /api/acq/raw-data/{sellerId}/{tradeId}/ (via http baseURL '/api')
 * -------------------------------------------------------------------------- */
const gridApi = ref<GridApi | null>(null)
// Rows store (provides rows + fetchRows action)
const gridRowsStore = useAgGridRowsStore()
const { rows: rowData } = storeToRefs(gridRowsStore)
// Selections store (provides currently selected seller/trade)
const acqSelStore = useAcqSelectionsStore()
const { selectedSellerId, selectedTradeId } = storeToRefs(acqSelStore)

function maybeFetchRows(): void {
  const sid = Number(selectedSellerId.value)
  const tid = Number(selectedTradeId.value)
  if (Number.isFinite(sid) && sid > 0 && Number.isFinite(tid) && tid > 0) {
    gridRowsStore.fetchRows(sid, tid)
  } else {
    // When selections are incomplete, ensure grid shows empty state
    // (gridRowsStore.resetRows() would also be acceptable)
  }
}

// React to selection changes and load rows
watch([selectedSellerId, selectedTradeId], () => {
  maybeFetchRows()
})

function onGridReady(e: GridReadyEvent) {
  // Cache Grid API and size columns; data will load via watchers when IDs are present
  gridApi.value = e.api
  updateGridSize()
  maybeFetchRows()
}

/* --------------------------------------------------------------------------
 * Helpers – formatters & actions
 * -------------------------------------------------------------------------- */
function currency0(p: any): string {
  const v = p.value
  const n = typeof v === 'number' ? v : parseFloat(String(v))
  if (Number.isNaN(n)) return ''
  return new Intl.NumberFormat(undefined, { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(n)
}
function percentFmt(p: any): string { return p.value == null ? '' : `${(Number(p.value) * 100).toFixed(2)}%` }
function dateFmt(p: any): string {
  if (!p.value) return ''
  const d = new Date(String(p.value))
  if (isNaN(d.getTime())) return String(p.value)
  return new Intl.DateTimeFormat('en-US', { year: 'numeric', month: '2-digit', day: '2-digit' }).format(d)
}

function onRowAction(action: string, row: any): void {
  // NOTE: Actions originate from `ActionsCell.vue` via cellRendererParams.onAction
  // We promote only the 'view' action to the parent so it can open the Loan modal.
  // Other actions remain logged for now to avoid surprising side-effects.
  if (action === 'view') {
    // Build a friendly address string for modal header consistency
    const street = String(row?.street_address ?? '').trim()
    const city = String(row?.city ?? '').trim()
    const state = String(row?.state ?? '').trim()
    const addr = [street, [city, state].filter(Boolean).join(', ')].filter(Boolean).join(', ')

    // Ensure we pass a string id; prefer row.id, but fall back to hub-based keys
    const rawId = (row as any)?.id ?? (row as any)?.asset_hub_id ?? (row as any)?.asset_hub?.id ?? (row as any)?.asset_hub
    const id = rawId != null && rawId !== '' ? String(rawId) : ''
    console.log('[AcqGrid] open-loan: resolved id=', id, 'row.id=', (row as any)?.id, 'row.asset_hub=', (row as any)?.asset_hub, 'row=', row)

    // Emit to parent acquisitions page, which already has onOpenLoan(payload)
    emit('open-loan', { id, row, addr })
    return
  }
  console.log('[AcqGrid] action', action, row)
}

/* --------------------------------------------------------------------------
 * Layout helpers
 * -------------------------------------------------------------------------- */
const cardRef = ref<HTMLElement | null>(null)
const isFullscreen = ref<boolean>(false)
const gridRef = ref<any>(null)

const gridStyle = computed(() => (isFullscreen.value ? { width: '100%', height: '100%' } : { width: '100%', height: '420px' }))

function updateGridSize(): void {
  nextTick(() => gridApi.value?.autoSizeAllColumns?.())
}

async function toggleFullscreen(): Promise<void> {
  const el = cardRef.value as any
  if (!el) return
  if (isFullscreen.value || document.fullscreenElement) {
    await document.exitFullscreen?.()
    isFullscreen.value = false
  } else {
    await el.requestFullscreen?.()
    isFullscreen.value = true
  }
  updateGridSize()
}

/* --------------------------------------------------------------------------
 * Default column behaviour
 * -------------------------------------------------------------------------- */
const defaultColDef: ColDef = {
  resizable: true,
  filter: true,
  minWidth: 120,
  wrapHeaderText: true,
  autoHeaderHeight: true,
  headerClass: 'text-center',
  cellClass: 'text-center',
  menuTabs: ['filterMenuTab'],
}

/* --------------------------------------------------------------------------
 * Emits – bubble row actions up to parent container (index.vue)
 * -------------------------------------------------------------------------- */
const emit = defineEmits<{
  /**
   * open-loan
   * Emitted when the user clicks the "View" action for a row. The parent
   * `index.vue` listens to this event and opens the Loan-Level modal by
   * delegating to its existing `onOpenLoan(payload)` method.
   */
  (e: 'open-loan', payload: { id: string; row: any; addr?: string }): void
}>()
</script>

<style scoped>
.fullscreen-card {
  position: fixed;
  inset: 0;
  z-index: 1050;
  border-radius: 0 !important;
}
:deep(.acq-grid .ag-header-cell-label) {
  justify-content: center;
}
:deep(.acq-grid .ag-cell) {
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
}
</style>
