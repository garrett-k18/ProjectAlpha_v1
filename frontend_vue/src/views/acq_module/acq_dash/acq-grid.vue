<template>
  <!-- Simplified Acquisitions Grid (refactor trial) -->
  <div class="card" ref="cardRef" :class="{ 'fullscreen-card': isFullscreen }">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Data Tape – {{ viewTitle }}</h4>
      <div class="d-flex align-items-center gap-2">
        <!-- Bulk action buttons - show when rows are selected -->
        <div v-if="selectedRowCount > 0" class="d-flex align-items-center gap-2 me-2">
          <span class="badge bg-primary">{{ selectedRowCount }} selected</span>
          <button 
            v-if="activeView !== 'drops'"
            class="btn btn-sm btn-warning text-nowrap" 
            @click="showBulkDropModal = true"
            title="Drop selected assets"
          >
            <i class="mdi mdi-arrow-down-circle me-1"></i>Bulk Drop
          </button>
          <button 
            v-if="activeView === 'drops'"
            class="btn btn-sm btn-success text-nowrap" 
            @click="showBulkRestoreModal = true"
            title="Restore selected assets"
          >
            <i class="mdi mdi-plus-circle me-1"></i>Bulk Restore
          </button>
          <button 
            class="btn btn-sm btn-outline-secondary" 
            @click="clearSelection"
            title="Clear selection"
          >
            <i class="mdi mdi-close"></i>
          </button>
        </div>
        
        <!-- View selector -->
        <label for="viewSelect" class="me-1 small mb-0">View</label>
        <select id="viewSelect" class="form-select form-select-sm" v-model="activeView" @change="applyView">
          <option value="snapshot">Snapshot</option>
          <option value="all">All</option>
          <option value="valuations">Valuations</option>
          <option value="drops">Drops</option>
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
        :rowSelection="{ mode: 'multiRow', checkboxes: true, headerCheckbox: true, selectAll: 'filtered', enableClickSelection: true }"
        :selectionColumnDef="{ pinned: 'left', lockPosition: 'left', suppressMovable: true }"
        :pagination="true"
        :paginationPageSize="50"
        :paginationPageSizeSelector="[25, 50, 100, 200, 500]"
        overlayNoRowsTemplate="No rows"
        @grid-ready="onGridReady"
        @selection-changed="updateSelectedRows"
      />
    </div>
  </div>

  <!-- Drop Confirmation Modal -->
  <BModal
    v-model="showDropModal"
    title="Drop Asset from List"
    centered
    hide-header-close
  >
    <p v-if="assetToDrop" class="mb-0 text-center">
      Are you sure you want to drop:<br>
      <strong>{{ assetToDrop.id }} - {{ getAssetAddress(assetToDrop) }}</strong>?
    </p>
    <template #footer>
      <div class="d-flex justify-content-end w-100 gap-2">
        <button class="btn btn-secondary" @click="showDropModal = false">Cancel</button>
        <button class="btn btn-warning" @click="confirmDrop">
          <i class="mdi mdi-arrow-down-circle me-1"></i>Drop Asset
        </button>
      </div>
    </template>
  </BModal>

  <!-- Add Back to Population Modal -->
  <BModal
    v-model="showRestoreModal"
    title="Add Back to Population"
    centered
    hide-header-close
  >
    <p v-if="assetToRestore" class="mb-0 text-center">
      Are you sure you want to add back:<br>
      <strong>{{ assetToRestore.id }} - {{ getAssetAddress(assetToRestore) }}</strong>?
    </p>
    <template #footer>
      <div class="d-flex justify-content-end w-100 gap-2">
        <button class="btn btn-secondary" @click="showRestoreModal = false">Cancel</button>
        <button class="btn btn-success" @click="confirmRestore">
          <i class="mdi mdi-plus-circle me-1"></i>Add to Population
        </button>
      </div>
    </template>
  </BModal>

  <!-- Bulk Drop Confirmation Modal -->
  <BModal
    v-model="showBulkDropModal"
    title="Drop Multiple Assets"
    centered
    hide-header-close
  >
    <div class="text-center">
      <p class="mb-2">Are you sure you want to drop <strong>{{ selectedRowCount }}</strong> assets?</p>
      <div v-if="selectedRows.length > 0 && selectedRows.length <= 10" class="text-start small bg-light p-2 rounded" style="max-height: 200px; overflow-y: auto;">
        <div v-for="row in selectedRows" :key="row.id" class="mb-1">
          • {{ row.id }} - {{ getAssetAddress(row) }}
        </div>
      </div>
      <p v-if="selectedRows.length > 10" class="text-muted small">
        (Showing summary - too many to list)
      </p>
    </div>
    <template #footer>
      <div class="d-flex justify-content-end w-100 gap-2">
        <button class="btn btn-secondary" @click="showBulkDropModal = false" :disabled="bulkProcessing">Cancel</button>
        <button class="btn btn-warning" @click="confirmBulkDrop" :disabled="bulkProcessing">
          <span v-if="bulkProcessing" class="spinner-border spinner-border-sm me-1"></span>
          <i v-else class="mdi mdi-arrow-down-circle me-1"></i>
          Drop {{ selectedRowCount }} Assets
        </button>
      </div>
    </template>
  </BModal>

  <!-- Bulk Restore Confirmation Modal -->
  <BModal
    v-model="showBulkRestoreModal"
    title="Restore Multiple Assets"
    centered
    hide-header-close
  >
    <div class="text-center">
      <p class="mb-2">Are you sure you want to restore <strong>{{ selectedRowCount }}</strong> assets?</p>
      <div v-if="selectedRows.length > 0 && selectedRows.length <= 10" class="text-start small bg-light p-2 rounded" style="max-height: 200px; overflow-y: auto;">
        <div v-for="row in selectedRows" :key="row.id" class="mb-1">
          • {{ row.id }} - {{ getAssetAddress(row) }}
        </div>
      </div>
      <p v-if="selectedRows.length > 10" class="text-muted small">
        (Showing summary - too many to list)
      </p>
    </div>
    <template #footer>
      <div class="d-flex justify-content-end w-100 gap-2">
        <button class="btn btn-secondary" @click="showBulkRestoreModal = false" :disabled="bulkProcessing">Cancel</button>
        <button class="btn btn-success" @click="confirmBulkRestore" :disabled="bulkProcessing">
          <span v-if="bulkProcessing" class="spinner-border spinner-border-sm me-1"></span>
          <i v-else class="mdi mdi-plus-circle me-1"></i>
          Restore {{ selectedRowCount }} Assets
        </button>
      </div>
    </template>
  </BModal>
</template>

<script setup lang="ts">
import { AgGridVue } from 'ag-grid-vue3'
import { themeQuartz } from 'ag-grid-community'
import type { ColDef, GridReadyEvent, GridApi } from 'ag-grid-community'
import { ref, computed, nextTick, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { BModal } from 'bootstrap-vue-next'
import http from '@/lib/http'
import ActionsCell from '@/views/acq_module/acq_dash/components/ActionsCell.vue'
import BadgeCell from '@/views/acq_module/acq_dash/components/BadgeCell.vue'
import { useAcqSelectionsStore } from '@/stores/acqSelections'
import { useAgGridRowsStore } from '@/stores/agGridRows'
import { propertyTypeEnumMap, occupancyEnumMap, assetStatusEnumMap } from '@/config/badgeTokens'

/* --------------------------------------------------------------------------
 * Pinned-left constant columns (order matters)
 * -------------------------------------------------------------------------- */
const constantColumns: ColDef[] = [
  {
    headerName: 'Actions',
    colId: 'actions',
    pinned: 'left',
    width: 170,
    minWidth: 160,
    lockPosition: true,
    suppressMovable: true,
    sortable: false,
    filter: false,
    suppressHeaderContextMenu: true,
    cellRenderer: ActionsCell as any,
    cellRendererParams: { onAction: onRowAction },
  },
  { headerName: 'Seller ID', field: 'sellertape_id', pinned: 'left' },
  // Address fields now pinned left for all views (sortable individually)
  { 
    headerName: 'Street Address', 
    field: 'street_address', 
    pinned: 'left',
    headerClass: ['ag-left-aligned-header', 'text-start'],
    cellClass: ['ag-left-aligned-cell', 'text-start'],
  },
  { 
    headerName: 'City', 
    field: 'city', 
    pinned: 'left',
    headerClass: ['ag-left-aligned-header', 'text-start'],
    cellClass: ['ag-left-aligned-cell', 'text-start'],
  },
  { 
    headerName: 'State', 
    field: 'state', 
    pinned: 'left',
  },
]
/* --------------------------------------------------------------------------
 * All dynamic columns defined once here – easy to rename & reuse
 * -------------------------------------------------------------------------- */
const cols: Record<string, ColDef> = {
  // Fields for "All" view only - appear right after State
  zip: { headerName: 'ZIP', field: 'zip' },
  as_of_date: { headerName: 'As Of Date', field: 'as_of_date', valueFormatter: dateFmt },
  // Category badges with subtle professional colors
  property_type: {
    headerName: 'Property Type',
    field: 'property_type',
    cellRenderer: BadgeCell as any,
    cellRendererParams: {
      mode: 'enum',
      enumMap: propertyTypeEnumMap,
    },
  },
  occupancy: {
    headerName: 'Occupancy',
    field: 'occupancy',
    cellRenderer: BadgeCell as any,
    cellRendererParams: {
      mode: 'enum',
      enumMap: occupancyEnumMap,
    },
  },
  // Asset status badges (professional subdued colors)
  asset_status: {
    headerName: 'Asset Status',
    field: 'asset_status',
    cellRenderer: BadgeCell as any,
    cellRendererParams: {
      mode: 'enum',
      enumMap: assetStatusEnumMap,
    },
  },
  seller_asis_value: { headerName: 'Seller AIV', field: 'seller_asis_value', valueFormatter: currency0 },
  seller_arv_value: { headerName: 'Seller ARV', field: 'seller_arv_value', valueFormatter: currency0 },
  // Origination value (from serializer)
  origination_value: { headerName: 'Origination AIV', field: 'origination_value', valueFormatter: currency0 },
  seller_value_date: { headerName: 'Seller Value Date', field: 'seller_value_date', valueFormatter: dateFmt },
  current_balance: { headerName: 'Current Balance', field: 'current_balance', valueFormatter: currency0 },
  interest_rate: { headerName: 'Interest Rate', field: 'interest_rate', valueFormatter: percentFmt },
  total_debt: { headerName: 'Total Debt', field: 'total_debt', valueFormatter: currency0 },
  months_dlq: { headerName: 'Months DLQ', field: 'months_dlq', width: 100 },
  next_due_date: { headerName: 'Next Due Date', field: 'next_due_date', width: 110, valueFormatter: dateFmt },
  // Flag badges with requested colors: Yes=red, No=yellow
  fc_flag: {
    headerName: 'FC Flag',
    field: 'fc_flag',
    cellRenderer: BadgeCell as any,
    cellRendererParams: { mode: 'boolean', booleanYesColor: 'bg-danger', booleanNoColor: 'bg-secondary' },
  },
  bk_flag: {
    headerName: 'BK Flag',
    field: 'bk_flag',
    cellRenderer: BadgeCell as any,
    cellRendererParams: { mode: 'boolean', booleanYesColor: 'bg-danger', booleanNoColor: 'bg-secondary' },
  },
  mod_flag: {
    headerName: 'MOD Flag',
    field: 'mod_flag',
    cellRenderer: BadgeCell as any,
    cellRendererParams: { mode: 'boolean', booleanYesColor: 'bg-danger', booleanNoColor: 'bg-secondary' },
  },
  // Local Agents columns
  agent_name: { headerName: 'Broker', field: 'agent_name' },
  bid_amount: { headerName: 'Bid Amount', field: 'bid_amount', valueFormatter: currency0 },
  // Valuations (unified from backend serializer)
  broker_asis_value: { headerName: 'Broker AIV', field: 'broker_asis_value', valueFormatter: currency0 },
  broker_arv_value: { headerName: 'Broker ARV', field: 'broker_arv_value', valueFormatter: currency0 },
  broker_value_date: { headerName: 'Broker Value Date', field: 'broker_value_date', valueFormatter: dateFmt },
  internal_initial_uw_asis_value: { headerName: 'Internal UW AIV', field: 'internal_initial_uw_asis_value', valueFormatter: currency0 },
  internal_initial_uw_arv_value: { headerName: 'Internal UW ARV', field: 'internal_initial_uw_arv_value', valueFormatter: currency0 },
  internal_initial_uw_value_date: { headerName: 'Internal UW Value Date', field: 'internal_initial_uw_value_date', valueFormatter: dateFmt },
  // Additional date and property fields
  
  product_type: { headerName: 'Product Type', field: 'product_type' ,width: 110},
  year_built: { headerName: 'Year Built', field: 'year_built',width: 90 },
  sq_ft: { headerName: 'Sq Ft', field: 'sq_ft',width: 90, valueFormatter: (p: any) => p.value ? new Intl.NumberFormat().format(p.value) : '' },
  lot_size: { headerName: 'Lot Size', field: 'lot_size', width: 90, valueFormatter: (p: any) => p.value ? new Intl.NumberFormat().format(p.value) : '' },
  beds: { headerName: 'Beds', field: 'beds', width: 90 },
  baths: { headerName: 'Baths', field: 'baths', width: 90 },
  // Financial fields
  original_balance: { headerName: 'Original Balance', field: 'original_balance', valueFormatter: currency0 },
  origination_date: { headerName: 'Origination Date', field: 'origination_date', valueFormatter: dateFmt },
  last_paid_date: { headerName: 'Last Paid Date', field: 'last_paid_date', valueFormatter: dateFmt },
  // Borrower fields
  borrower1_name: {
    headerName: 'Borrower 1',
    field: 'borrower1_full_name',
    headerClass: ['ag-left-aligned-header', 'text-start'],
    cellClass: ['ag-left-aligned-cell', 'text-start'],
  },
  borrower2_name: {
    headerName: 'Borrower 2',
    field: 'borrower2_full_name',
    headerClass: ['ag-left-aligned-header', 'text-start'],
    cellClass: ['ag-left-aligned-cell', 'text-start'],
  },
  // Additional valuation fields
  origination_arv: { headerName: 'Origination ARV', field: 'origination_arv', valueFormatter: currency0 },
  origination_value_date: { headerName: 'Origination Value Date', field: 'origination_value_date', valueFormatter: dateFmt },
  additional_asis_value: { headerName: 'Additional AIV', field: 'additional_asis_value', valueFormatter: currency0 },
  additional_arv_value: { headerName: 'Additional ARV', field: 'additional_arv_value', valueFormatter: currency0 },
  additional_value_date: { headerName: 'Additional Value Date', field: 'additional_value_date', valueFormatter: dateFmt },
  // Additional financial and schedule fields
  deferred_balance: { headerName: 'Deferred Balance', field: 'deferred_balance', valueFormatter: currency0 },
  first_pay_date: { headerName: 'First Pay Date', field: 'first_pay_date', valueFormatter: dateFmt },
  original_term: { headerName: 'Original Term', field: 'original_term' },
  original_rate: { headerName: 'Original Rate', field: 'original_rate', valueFormatter: percentFmt },
  original_maturity_date: { headerName: 'Original Maturity Date', field: 'original_maturity_date', valueFormatter: dateFmt },
  default_rate: { headerName: 'Default Rate', field: 'default_rate', valueFormatter: percentFmt },
  current_maturity_date: { headerName: 'Current Maturity Date', field: 'current_maturity_date', valueFormatter: dateFmt },
  current_term: { headerName: 'Current Term', field: 'current_term' },
  accrued_note_interest: { headerName: 'Accrued Note Interest', field: 'accrued_note_interest', valueFormatter: currency0 },
  accrued_default_interest: { headerName: 'Accrued Default Interest', field: 'accrued_default_interest', valueFormatter: currency0 },
  escrow_balance: { headerName: 'Escrow Balance', field: 'escrow_balance', valueFormatter: currency0 },
  escrow_advance: { headerName: 'Escrow Advance', field: 'escrow_advance', valueFormatter: currency0 },
  recoverable_corp_advance: { headerName: 'Recoverable Corp Advance', field: 'recoverable_corp_advance', valueFormatter: currency0 },
  late_fees: { headerName: 'Late Fees', field: 'late_fees', valueFormatter: currency0 },
  other_fees: { headerName: 'Other Fees', field: 'other_fees', valueFormatter: currency0 },
  suspense_balance: { headerName: 'Suspense Balance', field: 'suspense_balance', valueFormatter: currency0 },
  // Foreclosure fields
  fc_first_legal_date: { headerName: 'FC First Legal Date', field: 'fc_first_legal_date', valueFormatter: dateFmt },
  fc_referred_date: { headerName: 'FC Referred Date', field: 'fc_referred_date', valueFormatter: dateFmt },
  fc_judgement_date: { headerName: 'FC Judgement Date', field: 'fc_judgement_date', valueFormatter: dateFmt },
  fc_scheduled_sale_date: { headerName: 'FC Scheduled Sale Date', field: 'fc_scheduled_sale_date', valueFormatter: dateFmt },
  fc_sale_date: { headerName: 'FC Sale Date', field: 'fc_sale_date', valueFormatter: dateFmt },
  fc_starting: { headerName: 'FC Starting Bid', field: 'fc_starting', valueFormatter: currency0 },
  // Bankruptcy fields
  bk_chapter: { headerName: 'BK Chapter', field: 'bk_chapter' },
  // Modification fields
  mod_date: { headerName: 'MOD Date', field: 'mod_date', valueFormatter: dateFmt },
  mod_maturity_date: { headerName: 'MOD Maturity Date', field: 'mod_maturity_date', valueFormatter: dateFmt },
  mod_term: { headerName: 'MOD Term', field: 'mod_term' },
  mod_rate: { headerName: 'MOD Rate', field: 'mod_rate', valueFormatter: percentFmt },
  mod_initial_balance: { headerName: 'MOD Initial Balance', field: 'mod_initial_balance', valueFormatter: currency0 },
  // Acquisition status
  acq_status: { headerName: 'Acq Status', field: 'acq_status' },
}

/* --------------------------------------------------------------------------
 * View presets – simple arrays of keys from cols map
 * -------------------------------------------------------------------------- */
const OPTIONAL_REMOVABLE_FIELDS_ALL_VIEW = new Set<string>([
  'origination_arv',
  'additional_asis_value',
  'additional_arv_value',
  'additional_value_date',
  'deferred_balance',
  'first_pay_date',
  'original_term',
  'original_rate',
  'original_maturity_date',
  'default_rate',
  'current_maturity_date',
  'current_term',
  'accrued_note_interest',
  'accrued_default_interest',
  'escrow_balance',
  'escrow_advance',
  'recoverable_corp_advance',
  'late_fees',
  'other_fees',
  'suspense_balance',
  'fc_first_legal_date',
  'fc_referred_date',
  'fc_judgement_date',
  'fc_scheduled_sale_date',
  'fc_sale_date',
  'fc_starting',
  'bk_chapter',
  'mod_date',
  'mod_maturity_date',
  'mod_term',
  'mod_rate',
  'mod_initial_balance',
])

const ALWAYS_VISIBLE_FIELDS_ALL_VIEW = new Set<string>([
  'zip',
  'as_of_date',
  'property_type',
  'occupancy',
  'asset_status',
  'seller_asis_value',
  'seller_arv_value',
  'origination_value',
  'seller_value_date',
  'current_balance',
  'interest_rate',
  'total_debt',
  'months_dlq',
  'next_due_date',
  'fc_flag',
  'bk_flag',
  'mod_flag',
  'product_type',
  'year_built',
  'sq_ft',
  'lot_size',
  'beds',
  'baths',
  'original_balance',
  'origination_date',
  'last_paid_date',
  'borrower1_full_name',
  'borrower2_full_name',
])

const presets: Record<'snapshot' | 'all' | 'valuations' | 'drops', ColDef[]> = {
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
  drops: [
    // Drops view: assets removed from active bidding
    cols.property_type,
    cols.occupancy,
    cols.current_balance,
    cols.total_debt,
    cols.seller_asis_value,
    cols.months_dlq,
    cols.fc_flag,
    cols.bk_flag,
    // TODO: Add drop_reason, drop_date columns when backend model is updated
  ],
  all: [
    // WHAT: Curated "All" view – keep data tape essentials without flooding grid
    // WHY: Object.values(cols) produced >60 columns, breaking auto-sizing and UX
    // HOW: Blend categorical, financial, borrower, and foreclosure data in logical blocks
    cols.zip,
    cols.as_of_date,
    cols.property_type,
    cols.occupancy,
    cols.asset_status,
    cols.seller_asis_value,
    cols.seller_arv_value,
    cols.origination_value,
    cols.seller_value_date,
    cols.current_balance,
    cols.interest_rate,
    cols.total_debt,
    cols.months_dlq,
    cols.next_due_date,
    cols.fc_flag,
    cols.bk_flag,
    cols.mod_flag,
    cols.product_type,
    cols.year_built,
    cols.sq_ft,
    cols.lot_size,
    cols.beds,
    cols.baths,
    cols.original_balance,
    cols.origination_date,
    cols.last_paid_date,
    cols.borrower1_name,
    cols.borrower2_name,
    cols.origination_arv,
    cols.origination_value_date,
    cols.additional_asis_value,
    cols.additional_arv_value,
    cols.additional_value_date,
    cols.deferred_balance,
    cols.first_pay_date,
    cols.original_term,
    cols.original_rate,
    cols.original_maturity_date,
    cols.default_rate,
    cols.current_maturity_date,
    cols.current_term,
    cols.accrued_note_interest,
    cols.accrued_default_interest,
    cols.escrow_balance,
    cols.escrow_advance,
    cols.recoverable_corp_advance,
    cols.late_fees,
    cols.other_fees,
    cols.suspense_balance,
    cols.fc_first_legal_date,
    cols.fc_referred_date,
    cols.fc_judgement_date,
    cols.fc_scheduled_sale_date,
    cols.fc_sale_date,
    cols.fc_starting,
    cols.bk_chapter,
    cols.mod_date,
    cols.mod_maturity_date,
    cols.mod_term,
    cols.mod_rate,
    cols.mod_initial_balance,
  ],
}

/* -------------------------------------------------------------------------- */
const activeView = ref<'snapshot' | 'all' | 'valuations' | 'drops'>('snapshot')
const viewTitle = computed(() => {
  const titles: Record<typeof activeView.value, string> = {
    snapshot: 'Snapshot',
    all: 'All Assets',
    valuations: 'Valuations',
    drops: 'Drops'
  }
  return titles[activeView.value]
})
const columnDefs = ref<ColDef[]>(buildColumnsForView(activeView.value))

function columnHasMeaningfulData(field?: string): boolean {
  if (!field) return true
  const rows = rowData.value
  if (!Array.isArray(rows) || rows.length === 0) return true
  return rows.some((row: Record<string, any>) => {
    const value = row[field]
    if (value === null || value === undefined) return false
    if (typeof value === 'string') return value.trim() !== ''
    return true
  })
}

function pruneOptionalColumns(columns: ColDef[]): ColDef[] {
  if (activeView.value !== 'all') return columns
  return columns.filter((col: ColDef) => {
    const field = typeof col.field === 'string' ? col.field : undefined
    if (!field) return true
    if (ALWAYS_VISIBLE_FIELDS_ALL_VIEW.has(field)) return true
    if (!OPTIONAL_REMOVABLE_FIELDS_ALL_VIEW.has(field)) return true
    return columnHasMeaningfulData(field)
  })
}

function buildColumnsForView(view: 'snapshot' | 'all' | 'valuations' | 'drops'): ColDef[] {
  const baseColumns = [...constantColumns, ...presets[view]]
  return pruneOptionalColumns(baseColumns)
}

function refreshColumnDefs(): void {
  columnDefs.value = buildColumnsForView(activeView.value)
  nextTick(() => updateGridSize())
}

function applyView(): void {
  refreshColumnDefs()
}

/* --------------------------------------------------------------------------
 * Row data: sourced from Pinia stores (selections + cached rows)
 * Endpoint: GET /api/acq/raw-data/{sellerId}/{tradeId}/ (via http baseURL '/api')
 * -------------------------------------------------------------------------- */
const gridApi = ref<GridApi | null>(null)
// Rows store (provides rows + fetchRows action)
const gridRowsStore = useAgGridRowsStore()
const { rows: rawRows } = storeToRefs(gridRowsStore)
// Selections store (provides currently selected seller/trade)
const acqSelStore = useAcqSelectionsStore()
const { selectedSellerId, selectedTradeId } = storeToRefs(acqSelStore)

// Row data comes directly from store (backend now handles filtering by drop status)
const rowData = computed(() => rawRows.value)

function maybeFetchRows(): void {
  const sid = Number(selectedSellerId.value)
  const tid = Number(selectedTradeId.value)
  if (Number.isFinite(sid) && sid > 0 && Number.isFinite(tid) && tid > 0) {
    // Pass current view to fetch rows filtered by backend
    gridRowsStore.fetchRows(sid, tid, activeView.value)
  } else {
    // WHAT: when either selection is missing the grid should display empty state immediately
    // WHY: stale acquisition rows confuse users after trades are archived/boarded
    // WHERE: Pinia action resetRows (Docs: https://pinia.vuejs.org/core-concepts/state.html#resetting-the-state ) clears dataset reactively
    // HOW: call resetRows and keep cache intact so future selections remain performant
    gridRowsStore.resetRows()
  }
}

// React to selection changes and view changes to load rows
watch([selectedSellerId, selectedTradeId, activeView], () => {
  maybeFetchRows()
})

// React to data changes to trigger auto-sizing
watch(rowData, () => {
  refreshColumnDefs()
}, { flush: 'post' })

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
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(n)
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
  // We promote 'view' and 'drop' actions to the parent.
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
  
  if (action === 'drop') {
    // Drop action: show confirmation modal
    assetToDrop.value = row
    showDropModal.value = true
    return
  }
  
  if (action === 'restore') {
    // Restore action: show confirmation modal
    assetToRestore.value = row
    showRestoreModal.value = true
    return
  }
  
  console.log('[AcqGrid] action', action, row)
}

// Drop modal state
const showDropModal = ref(false)
const assetToDrop = ref<any>(null)

// Restore modal state
const showRestoreModal = ref(false)
const assetToRestore = ref<any>(null)

// Bulk selection state
const selectedRows = ref<any[]>([])
const selectedRowCount = computed(() => selectedRows.value.length)

// Bulk modal state
const showBulkDropModal = ref(false)
const showBulkRestoreModal = ref(false)
const bulkProcessing = ref(false)

/**
 * WHAT: Update selected rows from AG Grid selection
 * WHY: Track selection for bulk actions
 */
function updateSelectedRows(): void {
  if (!gridApi.value) return
  selectedRows.value = gridApi.value.getSelectedRows() || []
}

/**
 * WHAT: Clear all row selections
 * WHY: Allow user to deselect all rows
 */
function clearSelection(): void {
  if (!gridApi.value) return
  gridApi.value.deselectAll()
  selectedRows.value = []
}

// Helper to build address string from row data
function getAssetAddress(row: any): string {
  const street = String(row?.street_address ?? '').trim()
  const city = String(row?.city ?? '').trim()
  const state = String(row?.state ?? '').trim()
  return [street, [city, state].filter(Boolean).join(', ')].filter(Boolean).join(', ') || 'N/A'
}

// Confirm drop action
async function confirmDrop(): Promise<void> {
  if (!assetToDrop.value) return
  
  const assetId = assetToDrop.value?.id ?? assetToDrop.value?.asset_hub_id
  console.log('[AcqGrid] Dropping asset:', assetId, assetToDrop.value)
  
  try {
    // Call backend API to mark asset as dropped
    await http.post(`/acq/assets/${assetId}/drop/`, {
      reason: 'Dropped from grid by user'
    })
    
    // Close modal
    showDropModal.value = false
    assetToDrop.value = null
    
    // Clear cache to force fresh data
    gridRowsStore.clearCache()
    
    // Refresh current view first to remove the dropped asset
    await maybeFetchRows()
    
    // Then switch to Drops view to show user where it went
    activeView.value = 'drops'
    applyView()
    
  } catch (error: any) {
    console.error('[AcqGrid] Failed to drop asset:', error)
    alert(`Failed to drop asset: ${error?.response?.data?.error || error?.message || 'Unknown error'}`)
  }
}

// Confirm restore action (add back to population)
async function confirmRestore(): Promise<void> {
  if (!assetToRestore.value) return
  
  const assetId = assetToRestore.value?.id ?? assetToRestore.value?.asset_hub_id
  console.log('[AcqGrid] Adding asset back to population:', assetId, assetToRestore.value)
  
  try {
    // Call backend API to restore asset
    await http.post(`/acq/assets/${assetId}/restore/`)
    
    // Close modal
    showRestoreModal.value = false
    assetToRestore.value = null
    
    // Clear cache to force fresh data
    gridRowsStore.clearCache()
    
    // Refresh Drops view to remove the restored asset
    await maybeFetchRows()
    
  } catch (error: any) {
    console.error('[AcqGrid] Failed to add asset back to population:', error)
    alert(`Failed to add asset back: ${error?.response?.data?.error || error?.message || 'Unknown error'}`)
  }
}

// Confirm bulk drop action
async function confirmBulkDrop(): Promise<void> {
  if (selectedRows.value.length === 0) return
  
  bulkProcessing.value = true
  const rows = [...selectedRows.value]
  const assetIds = rows
    .map(row => row?.id ?? row?.asset_hub_id)
    .filter((id): id is number | string => id !== null && id !== undefined)

  console.log('[AcqGrid] Bulk dropping', assetIds.length, 'assets')
  
  try {
    await http.post('/acq/assets/bulk-drop/', {
      asset_ids: assetIds,
      reason: 'Bulk dropped from grid by user',
    })

    // Close modal and clear selection
    showBulkDropModal.value = false
    clearSelection()
    
    // Clear cache to force fresh data
    gridRowsStore.clearCache()
    
    // Refresh view
    await maybeFetchRows()
    
    // Switch to Drops view to show where they went
    activeView.value = 'drops'
    applyView()
    
  } finally {
    bulkProcessing.value = false
  }
}

// Confirm bulk restore action
async function confirmBulkRestore(): Promise<void> {
  if (selectedRows.value.length === 0) return
  
  bulkProcessing.value = true
  const rows = [...selectedRows.value]
  const assetIds = rows
    .map(row => row?.id ?? row?.asset_hub_id)
    .filter((id): id is number | string => id !== null && id !== undefined)

  console.log('[AcqGrid] Bulk restoring', assetIds.length, 'assets')
  
  try {
    await http.post('/acq/assets/bulk-restore/', {
      asset_ids: assetIds,
    })

    // Close modal and clear selection
    showBulkRestoreModal.value = false
    clearSelection()
    
    // Clear cache to force fresh data
    gridRowsStore.clearCache()
    
    // Refresh view
    await maybeFetchRows()
    
  } finally {
    bulkProcessing.value = false
  }
}

/* --------------------------------------------------------------------------
 * Layout helpers
 * -------------------------------------------------------------------------- */
const cardRef = ref<HTMLElement | null>(null)
const isFullscreen = ref<boolean>(false)
const gridRef = ref<any>(null)

const gridStyle = computed(() => (isFullscreen.value ? { width: '100%', height: '100%' } : { width: '100%', height: '420px' }))

function updateGridSize(): void {
  // WHAT: Auto-size columns that don't have manual width set
  // WHY: Columns with width property keep their size, others auto-size
  // HOW: autoSizeAllColumns will skip columns with explicit width
  //
  // TIMING ISSUES & KNOWN PROBLEMS:
  // - Auto-sizing sometimes fails when switching to "All" view for the first time
  // - Columns may not be fully rendered when autoSizeAllColumns() runs
  // - Data loading timing can affect auto-sizing accuracy
  // - AG Grid has limitations with many columns (>50) - auto-sizing may stop working after ~30-40 columns
  //
  // APPROACHES TRIED:
  // 1. Simple autoSizeAllColumns(false) - works for early columns but fails on later ones
  // 2. Individual column auto-sizing in a loop - helped ~3 more columns but still failed
  // 3. Increased delays (100ms, 200ms, 300ms) - helps but doesn't fully solve timing issues
  // 4. Data watcher to trigger auto-sizing after data loads - helps but still inconsistent
  // 5. Manual width settings on problematic columns - works but not ideal for dynamic content
  //
  // CURRENT STATE:
  // - Columns with explicit 'width' property keep their fixed size
  // - Other columns attempt auto-sizing but may fail on complex grids
  // - Users can manually resize any column by dragging borders
  // - Works better on subsequent view switches after initial render
  nextTick(() => {
    if (!gridApi.value) return
    // Small delay to ensure columns are fully rendered (especially when switching to "All" view)
    setTimeout(() => {
      if (!gridApi.value) return
      gridApi.value.autoSizeAllColumns(false)
    }, 300)
  })
}

function toggleFullscreen(): void {
  // WHAT: Toggle between normal card view and full-window maximized view
  // WHY: User wants window-based fullscreen, not native monitor fullscreen
  // HOW: Use CSS class to position card as fixed overlay covering viewport
  isFullscreen.value = !isFullscreen.value
  updateGridSize()
}

/* --------------------------------------------------------------------------
 * Default column behaviour
 * -------------------------------------------------------------------------- */
const defaultColDef: ColDef = {
  resizable: true,
  filter: true,
  // No minWidth - let AG Grid auto-size based on content (header vs data, whichever is longer)
  wrapHeaderText: true,  // Headers wrap to multiple lines if needed
  autoHeaderHeight: true,  // Header height adjusts automatically to fit wrapped text
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
/* Full-window overlay mode (not native fullscreen) */
.fullscreen-card {
  position: fixed;
  inset: 0;
  z-index: 1050;
  border-radius: 0 !important;
  margin: 0 !important;
  max-width: 100vw !important;
  max-height: 100vh !important;
  overflow: hidden;
}

.fullscreen-card .card-body {
  height: calc(100vh - 60px); /* Subtract header height */
  overflow: hidden;
}

 /* Center-align grid headers and cells by default */
 :deep(.acq-grid .ag-header-cell-label) {
   justify-content: center;
 }
 :deep(.acq-grid .ag-cell) {
   display: flex;
   align-items: center;
   justify-content: center;
   text-align: center;
 }

 /* Ensure selection column checkboxes (header + rows) are centered */
 :deep(.acq-grid .ag-header-select-all),
 :deep(.acq-grid .ag-selection-checkbox) {
   display: flex;
   align-items: center;
   justify-content: center;
   width: 100%;
   height: 100%;
 }

 :deep(.acq-grid .ag-header-select-all .ag-checkbox-input-wrapper),
 :deep(.acq-grid .ag-selection-checkbox .ag-checkbox-input-wrapper) {
   margin: 0 auto;
 }

 /* Multi-line header support - allow wrapping */
 :deep(.acq-grid .ag-header-cell-text) {
   white-space: normal !important;
   line-height: 1.2;
   word-break: break-word;
 }
</style>
