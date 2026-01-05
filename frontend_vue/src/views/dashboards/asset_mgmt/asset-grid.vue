<template>
  <!--
    AssetGrid.vue
    Purpose: Reusable AG Grid card for the Asset Management module.
    Visuals: Matches acquisitions grid (card header, Quartz theme, spacing).
  -->
  <div class="card" ref="cardRef" :class="{ 'fullwindow-card': isFullWindow }">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Asset Inventory</h4>
      <div class="d-flex align-items-center gap-2">
        <!-- Fullscreen toggle to mirror acquisitions experience -->
        <button
          class="btn btn-sm btn-light"
          type="button"
          :title="isFullWindow ? 'Exit Full Window' : 'Full Window'"
          :aria-pressed="isFullWindow ? 'true' : 'false'"
          aria-label="Toggle full window view"
          @click="toggleFullWindow"
        >
          <i class="mdi" :class="isFullWindow ? 'mdi-fullscreen-exit' : 'mdi-fullscreen'"></i>
        </button>
      </div>
    </div>

    <div class="card-body pt-0">
      <!-- Controls row placed directly under header, aligned left -->
      <div class="d-flex justify-content-between flex-wrap gap-2 mb-2">
        <!-- Quick Filter on the left -->
        <div class="input-group input-group-sm" style="width: 260px; max-width: 100%;">
          <span class="input-group-text"><i class="mdi mdi-magnify"></i></span>
          <input
            v-model="quickFilter"
            type="text"
            class="form-control"
            placeholder="Quick filter..."
            aria-label="Quick filter"
          />
          <button
            v-if="quickFilter"
            class="btn btn-light"
            type="button"
            title="Clear"
            @click="quickFilter = ''"
          >
            <i class="mdi mdi-close"></i>
          </button>
        </div>

        <!-- View dropdown on the right -->
        <div class="d-flex align-items-center gap-2">
          <label for="viewSelect" class="small mb-0">View</label>
          <select id="viewSelect" class="form-select form-select-sm" v-model="activeView" @change="applyView">
            <option value="snapshot">Snapshot</option>
            <option value="performance">Performance</option>
            <option value="servicing">Servicing</option>
            <option value="all">All</option>
          </select>
        </div>
      </div>
      <!-- AG Grid with Quartz theme and consistent height -->
      <ag-grid-vue
        ref="gridRef"
        class="asset-grid"
        :style="gridStyle"
        :theme="themeQuartz"
        :rowData="rowData"
        :columnDefs="columnDefs"
        :defaultColDef="defaultColDef"
        :quickFilterText="quickFilter"
        :rowSelection="{ mode: 'multiRow', checkboxes: false, headerCheckbox: false, enableClickSelection: true }"
        :animateRows="true"
        :loading="loading"
        overlayNoRowsTemplate="No assets found"
        overlayLoadingTemplate="Loading assets…"
        @grid-ready="onGridReady"
        @sort-changed="onSortChanged"
        @cell-value-changed="onAssetMasterStatusChanged"
      />

      <!-- Bottom-right pagination controls -->
      <div class="d-flex justify-content-end align-items-center gap-2 mt-2">
        <label for="pageSizeSelect" class="small mb-0">Rows</label>
        <select id="pageSizeSelect" class="form-select form-select-sm" v-model.number="pageSizeSelection" @change="onPageSizeChange" autocomplete="off" style="width: auto;">
          <option :value="50">50</option>
          <option :value="100">100</option>
          <option :value="200">200</option>
          <option :value="500">500</option>
          <option value="ALL">All</option>
        </select>

        <div class="d-flex align-items-center gap-1" v-if="!viewAll">
          <button class="btn btn-sm btn-light" :disabled="page <= 1 || loading" @click="prevPage" title="Prev">‹</button>
          <span class="small">Page {{ page }} / {{ totalPages || 1 }}</span>
          <button class="btn btn-sm btn-light" :disabled="page >= (totalPages || 1) || loading" @click="nextPage" title="Next">›</button>
        </div>

        <div class="small" v-if="totalCount !== null">Total: <strong>{{ totalCount }}</strong></div>
      </div>

      <!-- Loan-Level Modal (mirrors acquisitions dashboard) -->
      <!-- Docs: https://bootstrap-vue-next.github.io/bootstrap-vue-next/docs/components/modal -->
      <BModal
        v-model="showAssetModal"
        size="xl"
        body-class="p-0 bg-body text-body"
        dialog-class="product-details-dialog"
        content-class="product-details-content bg-body text-body"
        hide-footer
        @shown="onModalShown"
        @hidden="onModalHidden"
      >
        <!-- Custom header with action button (far right) -->
        <template #header>
          <div class="d-flex align-items-center w-100">
            <h5 class="modal-title mb-0">
              <div class="lh-sm">
                <span class="fw-bold text-dark">{{ modalIdText }}</span>
                <span v-if="modalTradeText" class="fw-bold text-dark ms-1">/ {{ modalTradeText }}</span>
              </div>
              <div class="text-muted lh-sm"><span class="fw-bold text-dark">{{ modalAddrText }}</span></div>
            </h5>
            <div class="ms-auto">
              <button
                type="button"
                class="btn btn-sm btn-primary"
                @click="openFullPage"
                title="Open full page (Ctrl + Enter)"
                aria-label="Open full page"
              >
                ⤢ Full Page
              </button>
            </div>
          </div>
        </template>
        <!-- Centralized loan-level wrapper rendered inside the modal -->
        <LoanLevelIndex
          :assetHubId="selectedId"
          :row="selectedRow"
          :address="selectedAddr"
          :standalone="false"
        />
      </BModal>
    </div>
  </div>
</template>

<script setup lang="ts">
// AG Grid Vue 3 wrapper and Quartz theme (matches acquisitions)
import { AgGridVue } from 'ag-grid-vue3'
import { themeQuartz } from 'ag-grid-community'
import type { GridApi, GridReadyEvent, ColDef, ValueFormatterParams } from 'ag-grid-community'
import { ref, computed, nextTick, watch, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { BModal } from 'bootstrap-vue-next'
import LoanLevelIndex from '@/views/am_module/loanlvl_index.vue'
import ActionsCell from '@/views/acq_module/acq_dash/components/ActionsCell.vue'
import BadgeCell from '@/views/acq_module/acq_dash/components/BadgeCell.vue'
import http from '@/lib/http'
// assetStatusEnumMap: Badge styling for asset_status field (displayed as "Asset Class" in grid)
// activeTracksEnumMap: Badge styling for active_tracks field (DIL, Modification, REO, FC, Short Sale)
// activeTasksColorMap: Color mapping for active_tasks field based on outcome type prefix
import { propertyTypeEnumMap, occupancyEnumMap, assetStatusEnumMap, activeTracksEnumMap, activeTasksColorMap } from '@/config/badgeTokens'

// Props for optional filtering (overrides URL query params)
const props = defineProps<{
  filterTradeName?: string
  filterSellerName?: string
  filterActiveOnly?: boolean  // If true, only show assets with ACTIVE master status
}>()

// Constant columns (always shown, pinned left first)
const constantColumns: ColDef[] = [
  {
    headerName: 'Actions',
    colId: 'actions',
    pinned: 'left',
    width: 220,
    minWidth: 210,  // Keep fixed width for Actions column (has buttons)
    lockPosition: true,
    suppressMovable: true,
    sortable: false,
    filter: false,
    suppressHeaderContextMenu: true,
    cellRenderer: ActionsCell as any,
    cellRendererParams: { onAction: onRowAction },
  },
  {
    headerName: 'Servicer ID',
    field: 'servicer_id',
    colId: 'servicer_id',
    pinned: 'left',
    // WHAT: Surface the external servicer identifier that asset managers reference daily
    // WHY: Product guidance indicates hub PKs are rarely used operationally; servicer IDs are the primary lookup key
    // HOW: Favor serializer field `servicer_id`, fall back to hub relationship if serializer omitted, and leave blank when no servicer id available
    valueGetter: (p: any) => {
      const row = p.data ?? {}
      const explicitServicerId = row.servicer_id ?? row.servicerId
      if (explicitServicerId != null && explicitServicerId !== '') return explicitServicerId
      const hubServicerId = row.asset_hub?.servicer_id ?? row.asset_hub?.servicerId
      if (hubServicerId != null && hubServicerId !== '') return hubServicerId
      return ''
    },
  },
  {
    headerName: 'Property Address',
    colId: 'address',
    wrapHeaderText: true,
    autoHeaderHeight: true,
    headerClass: ['ag-left-aligned-header', 'text-start'],
    cellClass: ['ag-left-aligned-cell', 'text-start'],
    cellStyle: { justifyContent: 'flex-start', textAlign: 'left' },
    pinned: 'left',
    valueGetter: (p: any) => {
      const s = (p.data?.street_address || '').toString().trim()
      const c = (p.data?.city || '').toString().trim()
      const st = (p.data?.state || '').toString().trim()
      return [s, c, st].filter(Boolean).join(', ')
    },
  },
]

// Additional columns (vary by view) as a named map to avoid fragile index references
// Each key is a stable identifier used by presets below.
// No minWidth set - let AG Grid auto-size based on content (header vs data, whichever is longer)
const cols: Record<string, ColDef> = {
  // ZIP intentionally omitted per latest serializer change
  propertyType: {
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
  trade: { headerName: 'Trade', field: 'trade_name', cellClass: 'text-start' },
  // FIELD: asset_status → Renamed display as "Asset Class" and moved to right of Trade (unpinned)
  assetClass: {
    headerName: 'Asset Class',
    field: 'asset_status',  // Backend field: asset_status (SellerRawData)
    cellRenderer: BadgeCell as any,
    cellRendererParams: {
      mode: 'enum',
      enumMap: assetStatusEnumMap,  // Uses assetStatusEnumMap for badge styling
    },
  },
  // FIELD: asset_master_status → Master lifecycle status from AssetIdHub (ACTIVE/LIQUIDATED)
  assetMasterStatus: {
    headerName: 'Asset Master Status',
    field: 'asset_master_status',  // Backend field: asset_hub.asset_status
    editable: true,  // WHAT: Enable inline editing with dropdown
    cellEditor: 'agSelectCellEditor',  // WHAT: AG Grid built-in dropdown editor (Docs: https://www.ag-grid.com/javascript-data-grid/cell-editors/#select-cell-editor)
    cellEditorParams: {
      values: ['ACTIVE', 'LIQUIDATED'],  // WHAT: AssetIdHub.AssetStatus choices from backend model
    },
  },
  // FIELD: active_tracks → Comma-separated list of active outcome workflows (DIL, Modification, REO, FC, Short Sale)
  activeTracks: {
    headerName: 'Active Tracks',
    field: 'active_tracks',  // Backend field: computed from outcome model existence checks (DIL, Modification, REO, FC, Short Sale)
    // WHAT: Fixed width at 160px - badges will wrap to multiple rows within this space
    // WHY: Multi-badge cells look better with wrapping instead of expanding horizontally to fit all badges on one line
    // HOW: This column is explicitly excluded from autoSizeColumns() in updateGridSize() function to preserve this width
    width: 160,
    suppressSizeToFit: false,  // Not needed since we exclude from autoSizeColumns explicitly
    wrapText: true,  // WHAT: Enable wrapping so badges can flow to multiple rows
    autoHeight: true,  // WHAT: Auto-adjust row height to accommodate wrapped badges (critical for multi-row badge display)
    cellRenderer: BadgeCell as any,  // WHAT: Render multiple small badges for each track
    cellRendererParams: {
      mode: 'multi',  // WHAT: Multi-badge mode splits comma-separated values ("DIL, Modification") into individual badges
      enumMap: activeTracksEnumMap,  // WHAT: Maps each track type (DIL, Modification, REO, FC, Short Sale) to badge colors
      size: 'sm',  // WHAT: Small preset from badgeTokens.ts for compact square badges (0.7rem font, tight padding)
    },
  },
  // FIELD: active_tasks → Current active tasks with outcome prefix (e.g., "DIL: Owner/Heirs contacted")
  activeTasks: {
    headerName: 'Active Tasks',
    field: 'active_tasks',  // Backend field: computed from latest task per outcome type
    // WHAT: Fixed width - task badges will wrap within this space
    // WHY: Task descriptions can be long; wrapping provides better readability than horizontal expansion
    // HOW: This column is explicitly excluded from autoSizeColumns() in updateGridSize() function
    width: 200,
    wrapText: true,  // WHAT: Enable wrapping for long task descriptions
    autoHeight: true,  // WHAT: Auto-adjust row height to fit wrapped badges
    cellRenderer: BadgeCell as any,  // WHAT: Render multiple small badges for each task
    cellRendererParams: {
      mode: 'multi-prefix',  // WHAT: Multi-prefix mode handles "DIL: Owner contacted" format - colors by prefix
      colorMap: activeTasksColorMap,  // WHAT: Maps outcome prefixes (DIL, Modification, etc.) to badge colors
      size: 'sm',  // WHAT: Small preset from badgeTokens.ts for compact square badges
    },
  },
  lifecycleStatus: { headerName: 'Lifecycle Status', field: 'lifecycle_status' },
  arvSeller: { headerName: 'ARV (Seller)', field: 'seller_arv_value', valueFormatter: currencyFormatter },
  asIsSeller: { headerName: 'As-Is (Seller)', field: 'seller_asis_value', valueFormatter: currencyFormatter },
  acqCost: { headerName: 'Acq Cost', field: 'acq_cost', valueFormatter: currencyFormatter },
  totalExpenses: { headerName: 'Total Expenses', field: 'total_expenses', valueFormatter: currencyFormatter },
  totalHold: { headerName: 'Total Hold (days)', field: 'total_hold' },
  exitDate: { headerName: 'Exit Date', field: 'exit_date', valueFormatter: dateFormatter },
  expectedGrossProceeds: { headerName: 'Gross Proceeds', field: 'expected_gross_proceeds', valueFormatter: currencyFormatter },
  expectedNetProceeds: { headerName: 'Net Proceeds', field: 'expected_net_proceeds', valueFormatter: currencyFormatter },
  expectedPL: { headerName: 'Expected P/L', field: 'expected_pl', valueFormatter: currencyFormatter },
  expectedCF: { headerName: 'Expected CF', field: 'expected_cf', valueFormatter: currencyFormatter },
  expectedIRR: { headerName: 'IRR %', field: 'expected_irr', valueFormatter: percentFormatter },
  expectedMOIC: { headerName: 'MOIC', field: 'expected_moic', valueFormatter: moicFormatter },
  expectedNPV: { headerName: 'NPV', field: 'expected_npv', valueFormatter: currencyFormatter },
 
  // ---- Servicing (nested under servicer_loan_data) ----
  sAsOfDate: { headerName: 'As Of', valueGetter: (p:any) => p.data?.servicer_loan_data?.as_of_date, valueFormatter: dateFormatter },
  sCurrentBalance: { headerName: 'Current Balance', valueGetter: (p:any) => p.data?.servicer_loan_data?.current_balance, valueFormatter: currencyFormatter },
  sInterestRate: { headerName: 'Interest Rate', valueGetter: (p:any) => p.data?.servicer_loan_data?.interest_rate, valueFormatter: (p:any) => (p.value == null ? '' : `${(Number(p.value) * 100).toFixed(2)}%`) },
  sNextDueDate: { headerName: 'Next Due Date', valueGetter: (p:any) => p.data?.servicer_loan_data?.next_due_date, valueFormatter: dateFormatter },
  sTotalDebt: { headerName: 'Total Debt', valueGetter: (p:any) => p.data?.servicer_loan_data?.total_debt, valueFormatter: currencyFormatter },
  sInvestorId: { headerName: 'Investor ID', valueGetter: (p:any) => p.data?.servicer_loan_data?.investor_id },
  sServicerId: { headerName: 'Servicer ID', valueGetter: (p:any) => p.data?.servicer_loan_data?.servicer_id },
  sFCStatus: { headerName: 'FC Status', valueGetter: (p:any) => p.data?.servicer_loan_data?.fc_status },
  sBKStatus: { headerName: 'BK Status', valueGetter: (p:any) => p.data?.servicer_loan_data?.bk_current_status },
  sLossMitStatus: { headerName: 'Loss Mit Status', valueGetter: (p:any) => p.data?.servicer_loan_data?.loss_mitigation_status },
  sCurrentPI: { headerName: 'Current P&I', valueGetter: (p:any) => p.data?.servicer_loan_data?.current_pi, valueFormatter: currencyFormatter },
  sCurrentTI: { headerName: 'Current T&I', valueGetter: (p:any) => p.data?.servicer_loan_data?.current_ti, valueFormatter: currencyFormatter },
  sPITI: { headerName: 'PITI', valueGetter: (p:any) => p.data?.servicer_loan_data?.piti, valueFormatter: currencyFormatter },
  // Additional BK/FC/Loss Mit detail
  sBKFiledDate: { headerName: 'BK Filed', valueGetter: (p:any) => p.data?.servicer_loan_data?.bk_filed_date, valueFormatter: dateFormatter },
  sBKDischargeDate: { headerName: 'BK Discharge', valueGetter: (p:any) => p.data?.servicer_loan_data?.bk_discharge_date, valueFormatter: dateFormatter },
  sBKDismissedDate: { headerName: 'BK Dismissed', valueGetter: (p:any) => p.data?.servicer_loan_data?.bk_dismissed_date, valueFormatter: dateFormatter },
  sFCScheduledSaleDate: { headerName: 'FC Scheduled Sale', valueGetter: (p:any) => p.data?.servicer_loan_data?.scheduled_fc_sale_date, valueFormatter: dateFormatter },
  sFCActualSaleDate: { headerName: 'FC Actual Sale', valueGetter: (p:any) => p.data?.servicer_loan_data?.actual_fc_sale_date, valueFormatter: dateFormatter },
  sFCBAStatusDate: { headerName: 'FC BA Status Date', valueGetter: (p:any) => p.data?.servicer_loan_data?.foreclosure_business_area_status_date, valueFormatter: dateFormatter },
  sFCBAStatus: { headerName: 'FC BA Status', valueGetter: (p:any) => p.data?.servicer_loan_data?.foreclosure_business_area_status },
  sLossMitStartDate: { headerName: 'Loss Mit Start', valueGetter: (p:any) => p.data?.servicer_loan_data?.loss_mitigation_start_date, valueFormatter: dateFormatter },
  sLoanModDate: { headerName: 'Loan Mod Date', valueGetter: (p:any) => p.data?.servicer_loan_data?.loan_modification_date, valueFormatter: dateFormatter },
  sRepayPlanStatus: { headerName: 'Repay Plan Status', valueGetter: (p:any) => p.data?.servicer_loan_data?.repayment_plan_status },
  internal_initial_uw_asis_value: { headerName: 'Underwritten AIV', field: 'internal_initial_uw_asis_value', valueFormatter: currencyFormatter },
  internal_initial_uw_arv_value: { headerName: 'Underwritten ARV', field: 'internal_initial_uw_arv_value', valueFormatter: currencyFormatter },
}

// Presets now reference the named columns for clarity and stability
const presets: Record<string, ColDef[]> = {
  snapshot: [
    cols.trade,
    cols.assetClass,  // FIELD: asset_status (renamed to "Asset Class" display, positioned after Trade)
    cols.assetMasterStatus,  // FIELD: asset_master_status (editable dropdown from AssetIdHub)
    cols.activeTracks,  // FIELD: active_tracks (comma-separated outcome types: DIL, Modification, REO, FC, Short Sale)
    cols.activeTasks,  // FIELD: active_tasks (current tasks with outcome prefix: "DIL: Owner/Heirs contacted")
    cols.propertyType,
    cols.internal_initial_uw_asis_value,
    cols.internal_initial_uw_arv_value,
    cols.sCurrentBalance,
    cols.sInterestRate,
    cols.sNextDueDate,
    cols.sTotalDebt,
  ],
  performance: [
    cols.arvSeller,
    cols.asIsSeller,
    cols.acqCost,
    cols.totalExpenses,
    cols.expectedPL,
    cols.expectedCF,
    cols.expectedIRR,
    cols.expectedMOIC,
    cols.expectedNPV,
  ],
  servicing: [
    cols.sAsOfDate,
    cols.sInvestorId,
    cols.sServicerId,
    cols.sCurrentBalance,
    cols.sInterestRate,
    cols.sCurrentPI,
    cols.sCurrentTI,
    cols.sPITI,
    cols.sTotalDebt,
    cols.sNextDueDate,
    cols.sFCStatus,
    cols.sBKStatus,
    cols.sLossMitStatus,
    cols.sBKFiledDate,
    cols.sBKDischargeDate,
    cols.sBKDismissedDate,
    cols.sFCScheduledSaleDate,
    cols.sFCActualSaleDate,
    cols.sFCBAStatusDate,
    cols.sFCBAStatus,
    cols.sLossMitStartDate,
    cols.sLoanModDate,
    cols.sRepayPlanStatus,
  ],
  all: Object.values(cols),
}

const activeView = ref<'snapshot' | 'performance' | 'servicing' | 'all'>('snapshot')
const columnDefs = ref<ColDef[]>([...constantColumns, ...presets[activeView.value]])

function applyView() {
  columnDefs.value = [...constantColumns, ...presets[activeView.value]]

  // Re-apply sort because visible columns changed
  nextTick(() => {
    onSortChanged()
    updateGridSize()  // WHAT: Autosize columns after view switch so address and other columns fit content
  })
}

// ---------------------------------------------------------------------------
// Modal + Actions from ActionsCell (view/edit/notes/delete)
// ---------------------------------------------------------------------------
// Modal visibility and selected payload
const showAssetModal = ref<boolean>(false)
const selectedId = ref<string | number | null>(null)
const selectedRow = ref<any>(null)
const selectedAddr = ref<string | null>(null)

// Build friendly header text for modal
const modalIdText = computed<string>(() => {
  // Prefer the external servicer identifier surfaced from AssetIdHub so asset managers can reconcile against servicer systems quickly
  const servicerId = selectedRow.value?.servicer_id ?? selectedRow.value?.asset_hub?.servicer_id
  if (servicerId != null && servicerId !== '') return String(servicerId)
  // Fallback to the canonical hub id so we always present a stable identifier even when servicer id is blank
  const hubId = selectedRow.value?.asset_hub_id ?? selectedRow.value?.asset_hub?.id
  if (hubId != null && hubId !== '') return String(hubId)
  // Final fallback: show the selected row id (equals hub pk) or generic label
  return selectedId.value != null ? String(selectedId.value) : 'Asset'
})
const modalTradeText = computed<string>(() => {
  // Normalize trade name across potential naming conventions and trim whitespace for display
  const rawTrade = selectedRow.value?.trade_name ?? selectedRow.value?.tradeName ?? ''
  return rawTrade ? String(rawTrade).trim() : ''
})
const modalAddrText = computed<string>(() => {
  const r: any = selectedRow.value || {}
  const street = String(r.street_address ?? '').trim()
  const city = String(r.city ?? '').trim()
  const state = String(r.state ?? '').trim()
  const locality = [city, state].filter(Boolean).join(', ')
  const built = [street, locality].filter(Boolean).join(', ')
  if (built) return built
  const rawAddr = selectedAddr.value ? String(selectedAddr.value) : ''
  // Strip trailing ZIP if present
  return rawAddr.replace(/,?\s*\d{5}(?:-\d{4})?$/, '')
})

// WHAT: Helper to extract the canonical asset hub identifier for API navigation
// WHY: Modal components and backend routes expect the hub primary key, not the external servicer identifier
// HOW: Prefer serializer field `asset_hub_id`, then nested hub pk/id, and finally legacy `id` fallbacks
function getAssetHubIdFromRow(row: any): string | number | null {
  const candidates = [
    row?.asset_hub_id,
    row?.asset_hub?.id,
    row?.asset_hub?.pk,
    row?.id,
  ]
  for (const c of candidates) {
    if (c !== undefined && c !== null && c !== '') return c as any
  }
  return null
}

// Build a one-line address string (for header and route query)
function buildAddress(row: any): string {
  const zip = row?.zip ?? row?.zip_code
  const parts = [row?.street_address, row?.city, row?.state, zip]
    .map((p: any) => (p != null ? String(p).trim() : ''))
    .filter((p: string) => !!p)
  return parts.join(', ')
}

function onRowAction(action: string, row: any): void {
  // Normalize action; only 'view' opens modal currently
  if (action === 'view') {
    selectedId.value = getAssetHubIdFromRow(row)
    selectedRow.value = row
    selectedAddr.value = buildAddress(row)
    showAssetModal.value = true
  } else {
    // Placeholders for future actions
    console.log(`[AssetGrid] action="${action}"`, row)
  }
}

// WHAT: Handle inline editing of Asset Master Status dropdown in the grid
// WHY: Users need to update AssetIdHub.asset_status (ACTIVE/LIQUIDATED) directly from the grid
// HOW: Extract asset ID and new value, PATCH to backend, refresh row data on success
async function onAssetMasterStatusChanged(params: any): Promise<void> {
  const row = params.data
  const newValue = params.newValue
  const oldValue = params.oldValue
  
  // WHAT: Skip update if value hasn't actually changed
  if (newValue === oldValue) return
  
  const assetId = getAssetHubIdFromRow(row)
  if (!assetId) {
    console.error('[AssetGrid] Cannot update asset_master_status: missing asset ID')
    return
  }
  
  try {
    // WHAT: Send PATCH request to update asset_master_status on the backend
    // Docs: https://axios-http.com/docs/api_intro
    const { data } = await http.patch(`/am/assets/${assetId}/`, {
      asset_master_status: newValue,
    })
    
    // WHAT: Update the row in the grid with the fresh data from backend
    // WHY: Ensures any computed fields are refreshed and grid stays in sync
    const api = gridApi.value
    if (api) {
      const rowNode = api.getRowNode(String(assetId))
      if (rowNode) {
        rowNode.setData(data)
      }
    }
    
    console.debug(`[AssetGrid] Updated asset_master_status: ${assetId} → ${newValue}`)
  } catch (err) {
    console.error('[AssetGrid] Failed to update asset_master_status:', err)
    // WHAT: Revert cell value on error so grid shows accurate state
    const api = gridApi.value
    if (api) {
      const rowNode = api.getRowNode(String(assetId))
      if (rowNode) {
        rowNode.setDataValue('asset_master_status', oldValue)
      }
    }
  }
}

// Modal lifecycle + shortcut
function onModalShown(): void {
  document.addEventListener('keydown', onKeydown as any)
}
function onModalHidden(): void {
  document.removeEventListener('keydown', onKeydown as any)
  selectedId.value = null
  selectedRow.value = null
  selectedAddr.value = null
}
function onKeydown(e: KeyboardEvent): void {
  if (e.ctrlKey && (e.key === 'Enter' || e.code === 'Enter')) {
    e.preventDefault()
    openFullPage()
  }
}

function openFullPage(): void {
  if (!selectedId.value) return
  const query: any = { id: selectedId.value }
  if (selectedAddr.value) query.addr = selectedAddr.value
  query.module = 'am'
  // Hide modal and navigate to the loan-level details page
  showAssetModal.value = false
  router.push({ path: '/loanlvl/products-details', query })
}

// Router instance for navigation
const router = useRouter()
const route = router.currentRoute

// Default column behavior
const defaultColDef: ColDef = {
  resizable: true,
  filter: true,
  // No minWidth - let AG Grid auto-size based on content (header vs data, whichever is longer)
  wrapHeaderText: true,  // Headers wrap to multiple lines if needed
  autoHeaderHeight: true,  // Header height adjusts automatically to fit wrapped text
  // Center-align headers and cell content for consistent presentation
  headerClass: 'text-center',
  cellClass: 'text-center',
  floatingFilter: false,
  menuTabs: ['filterMenuTab'],
}

// Live data from API
const rowData = ref<any[]>([])
const loading = ref<boolean>(false)
const page = ref<number>(1)
const pageSize = ref<number>(50)
const pageSizeSelection = ref<number | 'ALL'>(50)
const viewAll = ref<boolean>(false)
const totalCount = ref<number | null>(null)
const totalPages = ref<number | null>(null)
const sortExpr = ref<string>('')

// Quick filter state bound to the grid's quickFilterText option
const quickFilter = ref<string>('')

// Number formatting helpers (consistent with acquisitions)
function currencyFormatter(params: ValueFormatterParams): string {
  const v = params.value
  const num = typeof v === 'number' ? v : parseFloat(String(v))
  if (Number.isNaN(num)) return v == null ? '' : String(v)
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(num)
}

function dateFormatter(params: ValueFormatterParams): string {
  const v = params.value
  if (!v) return ''
  const d = new Date(String(v))
  if (isNaN(d.getTime())) return String(v)
  return new Intl.DateTimeFormat('en-US', { year: 'numeric', month: '2-digit', day: '2-digit' }).format(d)
}

function percentFormatter(params: ValueFormatterParams): string {
  const v = params.value
  if (v == null || v === '') return ''
  const num = typeof v === 'number' ? v : parseFloat(String(v))
  if (Number.isNaN(num)) return String(v)
  return `${num.toFixed(2)}%`
}

function moicFormatter(params: ValueFormatterParams): string {
  const v = params.value
  if (v == null || v === '') return ''
  const num = typeof v === 'number' ? v : parseFloat(String(v))
  if (Number.isNaN(num)) return String(v)
  return num.toFixed(2)
}

// Grid instance refs
const gridRef = ref<any>(null)
const gridApi = ref<GridApi | null>(null)

// Full window state for the card wrapper + scroll locking metadata
const cardRef = ref<HTMLElement | null>(null)
const isFullWindow = ref<boolean>(false) // WHAT: Reactive flag that drives CSS-based full-window layout
const bodyOverflowStack = ref<number>(0) // WHAT: Counter to manage document body overflow stacking when multiple components toggle

// Grid area size
const gridStyle = computed(() => (
  isFullWindow.value
    ? { width: '100%', height: '100%' } // WHAT: Stretch grid to fill available space when in full window mode
    : { width: '100%', height: '420px' } // WHAT: Default fixed height inside dashboard layout
))

function updateGridSize(): void {
  // WHAT: Delay autosizing to ensure AG Grid has fully rendered row data, then autosize columns selectively
  // WHY: Some columns need fixed widths with wrapping (Active Tracks), while others should expand to fit content
  // HOW: Use setTimeout + nextTick, filter out fixed-width columns, then call autoSizeColumns on remaining columns
  nextTick(() => {
    setTimeout(() => {
      try {
        const api = gridApi.value as any
        if (!api) return
        
        // WHAT: Exclude specific columns from autosizing to preserve their fixed widths
        // WHY: Active Tracks column displays multi-badge cells that should wrap within a fixed width (160px)
        //      Active Tasks column displays text that should wrap within a fixed width (200px)
        //      - autoSizeAllColumns() would expand these columns to fit content on one line, defeating the wrap behavior
        //      - We want content to wrap to multiple rows within the fixed width instead of expanding horizontally
        // HOW: Filter column list by colId, excluding these columns before calling autoSizeColumns
        // FUTURE: Add other column IDs to this array if they need fixed widths
        const fixedWidthColumns = ['active_tracks', 'active_tasks']
        
        const allColumns = api.getColumns?.() || []
        const columnsToAutosize = allColumns
          .filter((col: any) => !fixedWidthColumns.includes(col.getColId()))
          .map((col: any) => col.getColId())
        
        // WHAT: Call autoSizeColumns with filtered list instead of autoSizeAllColumns
        // WHY: autoSizeColumns(columnIds) respects our exclusion list; autoSizeAllColumns does not
        // RESULT: Most columns expand to fit content, Active Tracks stays at 120px and wraps badges
        if (columnsToAutosize.length > 0) {
          api.autoSizeColumns?.(columnsToAutosize) || api.columnApi?.autoSizeColumns?.(columnsToAutosize)
        }
      } catch {}
    }, 50)
  })
}

function onGridReady(e: GridReadyEvent) {
  gridApi.value = e.api
  
  // WHAT: Sync pageSize with pageSizeSelection on initial load
  // WHY: Browser autofill may have changed the select value without triggering @change
  // HOW: Read current selection and update pageSize before fetching
  if (pageSizeSelection.value !== 'ALL' && typeof pageSizeSelection.value === 'number') {
    pageSize.value = pageSizeSelection.value
  }
  
  // WHAT: Don't call updateGridSize here - let it happen after data loads in fetchRows
  // WHY: Autosizing before data loads causes columns to size based only on headers, not content
  fetchRows()
}

function toggleFullWindow(): void {
  const next = !isFullWindow.value // WHAT: Determine the next full-window state
  isFullWindow.value = next // WHAT: Flip reactive flag so template updates
  manageDocumentOverflow(next) // WHAT: Synchronize body scroll locking so background content does not scroll
  nextTick(() => updateGridSize()) // WHAT: Recalculate grid layout once DOM applies new classes
}

function manageDocumentOverflow(lock: boolean): void {
  const body = document.body // WHAT: Direct reference to the document body element we need to mutate
  if (!body) return // WHAT: Guard for SSR/testing environments
  if (lock) {
    bodyOverflowStack.value += 1 // WHAT: Increment stack counter so nested locks keep state consistent
    if (bodyOverflowStack.value === 1) {
      body.dataset.assetGridOverflow = body.style.overflow || '' // WHAT: Preserve prior overflow so we can restore precisely
      body.style.overflow = 'hidden' // WHAT: Prevent background scrolling while full window is active
    }
  } else {
    bodyOverflowStack.value = Math.max(0, bodyOverflowStack.value - 1) // WHAT: Decrease counter without falling below zero
    if (bodyOverflowStack.value === 0) {
      const prev = body.dataset.assetGridOverflow ?? '' // WHAT: Retrieve original overflow value from data attribute
      body.style.overflow = prev // WHAT: Restore previous overflow state
      delete body.dataset.assetGridOverflow // WHAT: Clean attribute to avoid leaks
    }
  }
}

onBeforeUnmount(() => {
  if (isFullWindow.value) {
    manageDocumentOverflow(false) // WHAT: Ensure body overflow resets if component unmounts while in full window mode
  }
})

// Fetch rows from backend with q and sort
async function fetchRows(): Promise<void> {
  loading.value = true
  try {
    const params: Record<string, any> = {
      page: page.value,
      page_size: pageSize.value,
    }
    if (quickFilter.value) params.q = quickFilter.value
    if (sortExpr.value) params.sort = sortExpr.value
    
    // Apply filters: props take precedence over URL query params
    const tradeName = props.filterTradeName || route.value.query.trade_name
    const sellerName = props.filterSellerName || route.value.query.seller_name
    if (tradeName) params.trade_name = tradeName
    if (sellerName) params.seller_name = sellerName
    if (props.filterActiveOnly) params.lifecycle_status = 'ACTIVE'
    
    const { data } = await http.get('/am/assets/', { params })
    // DRF pagination: { count, next, previous, results }
    totalCount.value = typeof data?.count === 'number' ? data.count : null
    rowData.value = Array.isArray(data?.results) ? data.results : []
    if (totalCount.value != null && pageSize.value > 0) {
      totalPages.value = Math.max(1, Math.ceil(totalCount.value / pageSize.value))
    } else {
      totalPages.value = null
    }
    console.debug('[AssetGrid] loaded rows:', rowData.value.length)
  } catch (e) {
    console.debug('[AssetGrid] fetch failed', e)
    rowData.value = []
    totalCount.value = null
    totalPages.value = null
  } finally {
    loading.value = false
    nextTick(() => updateGridSize())
  }
}

// Fetch all pages (uses server max_page_size=500)
async function fetchAllRows(): Promise<void> {
  loading.value = true
  try {
    const baseParams: Record<string, any> = { page: 1, page_size: 500 }
    if (quickFilter.value) baseParams.q = quickFilter.value
    if (sortExpr.value) baseParams.sort = sortExpr.value
    
    // Apply filters: props take precedence over URL query params
    const tradeName = props.filterTradeName || route.value.query.trade_name
    const sellerName = props.filterSellerName || route.value.query.seller_name
    if (tradeName) baseParams.trade_name = tradeName
    if (sellerName) baseParams.seller_name = sellerName
    if (props.filterActiveOnly) baseParams.lifecycle_status = 'ACTIVE'

    const all: any[] = []
    let currentPage = 1
    let count: number | null = null
    while (true) {
      const params = { ...baseParams, page: currentPage }
      const { data } = await http.get('/am/assets/', { params })
      const results = Array.isArray(data?.results) ? data.results : []
      if (count === null && typeof data?.count === 'number') count = data.count
      all.push(...results)
      if (!data?.next || results.length === 0) break
      currentPage += 1
      // Safety cap to avoid runaway loops
      if (currentPage > 100) break
    }
    rowData.value = all
    totalCount.value = count ?? all.length
    totalPages.value = 1
    console.debug('[AssetGrid] loaded ALL rows:', rowData.value.length)
  } catch (e) {
    console.debug('[AssetGrid] fetchAll failed', e)
    rowData.value = []
    totalCount.value = null
    totalPages.value = null
  } finally {
    loading.value = false
    nextTick(() => updateGridSize())
  }
}

function onPageSizeChange(): void {
  // WHAT: Handle page size selection change
  // WHY: Sync internal pageSize with dropdown and fetch new data
  // HOW: Check for 'ALL' special case, otherwise convert to number
  if (pageSizeSelection.value === 'ALL') {
    viewAll.value = true
    // keep pageSize for future use but fetch all now
    fetchAllRows()
  } else {
    viewAll.value = false
    // Ensure we have a valid number (v-model.number should handle this, but be safe)
    const newSize = typeof pageSizeSelection.value === 'number' 
      ? pageSizeSelection.value 
      : Number(pageSizeSelection.value)
    if (newSize > 0 && Number.isFinite(newSize)) {
      pageSize.value = newSize
    }
    page.value = 1
    fetchRows()
  }
}

function prevPage(): void {
  if (loading.value || viewAll.value) return // WHAT: Do nothing while loading or when all rows already loaded
  if (page.value > 1) {
    page.value -= 1
    fetchRows()
  }
}

function nextPage(): void {
  if (loading.value || viewAll.value) return // WHAT: Block next-page when data still loading or view-all active
  const tp = totalPages.value || 1
  if (page.value < tp) {
    page.value += 1
    fetchRows()
  }
}

// Debounce quick filter API calls
let qTimer: any = null
watch(quickFilter, () => {
  if (qTimer) clearTimeout(qTimer)
  qTimer = setTimeout(() => fetchRows(), 300)
})

// Capture sort changes and build sort expression (supports multi-col)
function onSortChanged(): void {
  const api: any = gridApi.value
  if (!api) return
  const sortModels = api.getColumnState?.().filter((c: any) => c.sort)
  if (!sortModels || sortModels.length === 0) {
    sortExpr.value = ''
    fetchRows()
    return
  }
  // Exclude derived 'address' from server-side sorting; let grid sort client-side for it
  const serverSorts = sortModels
    .filter((c: any) => c.colId !== 'address')
    .map((c: any) => (c.sort === 'desc' ? `-${c.colId}` : c.colId))
  sortExpr.value = serverSorts.join(',')
  if (serverSorts.length > 0) {
    fetchRows()
  }
}

// WHAT: Keep AG Grid overlay messaging synchronized with dataset size (loading handled by :loading prop in v32+)
// WHY: Display appropriate "No assets found" message when dataset is empty
// HOW: Show no-rows overlay for empty datasets, hide overlay when rows exist
// NOTE: Loading state now handled by :loading prop (AG Grid v32+ deprecates api.showLoadingOverlay)
function syncGridOverlay(): void {
  const api = gridApi.value
  if (!api) return
  if (rowData.value.length === 0 && !loading.value) {
    api.showNoRowsOverlay()
    return
  }
  api.hideOverlay()
}

// WHAT: Re-evaluate overlay once new row data arrives because empty arrays should display the no-rows overlay while populated arrays should hide overlays entirely
watch(rowData, () => {
  syncGridOverlay()
})
</script>

<style scoped>
.fullwindow-card {
  position: fixed;
  inset: 0;
  z-index: 1050; /* WHAT: Elevate above dashboard chrome so overlay feels native */
  border-radius: 0 !important;
  display: flex;
  flex-direction: column;
}

.fullwindow-card > .card-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0; /* WHAT: Allow nested grid to stretch without forcing overflow */
}

.fullwindow-card :deep(.asset-grid) {
  flex: 1;
  height: 100% !important; /* WHAT: Ensure AG Grid surface consumes available vertical space */
}

/* Center AG Grid header text and cell contents (Quartz theme uses flex wrappers) */
:deep(.asset-grid .ag-header-cell-label) {
  justify-content: center;
}

:deep(.asset-grid .ag-cell) {
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
}
</style>
