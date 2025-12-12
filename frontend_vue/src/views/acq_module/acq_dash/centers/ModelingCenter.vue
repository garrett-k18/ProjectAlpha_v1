<template>
  <Layout>
    <!-- Header -->
    <b-row>
      <b-col class="col-12">
        <div class="page-title-box">
          <div class="page-title-right">
            <router-link to="/acquisitions" class="btn btn-primary btn-sm">
              <i class="ri-arrow-left-line me-1"></i>Back to Dashboard
            </router-link>
          </div>
          <h4 class="page-title">
            <i class="mdi mdi-calculator-variant me-2"></i>
            Modeling Center
            <span v-if="hasSelection" class="trade-name-badge ms-3">
              {{ currentTradeName }}
            </span>
          </h4>
        </div>
      </b-col>
    </b-row>

    <!-- WHAT: Pool-Level Key Metrics - 3 focused metric cards -->
    <!-- WHY: Display high-level financial metrics in clean, prominent cards -->
    <!-- HOW: Three equal-width cards showing Bid % UPB, Total Proceeds, and Net P&L -->
    <!-- LAYOUT: metrics-row + h-100 on cards use flexbox so all three tiles share the same height and bottom whitespace -->
    <b-row v-if="hasSelection" class="g-2 mb-3 metrics-row">
      <!-- WHAT: Purchase Price & Bid Percentages Metric Card -->
      <!-- WHY: Display key acquisition metrics in a single consolidated card -->
      <!-- HOW: Show Total Purchase Price as primary metric, then three bid percentages below -->
      <b-col xl="4" lg="4" md="12">
        <!-- LAYOUT: h-100 lets this tile stretch to match the tallest sibling in metrics-row -->
        <div class="card tilebox-one mb-0 h-100">
          <div class="card-body pt-3 pb-2 px-3">
            <!-- WHAT: Header row for label + icon -->
            <!-- WHY: Keep title and icon on same line without overlapping the divider -->
            <div class="d-flex align-items-center justify-content-between mb-1">
              <!-- WHAT: Primary metric label - Total Purchase Price -->
              <!-- WHY: Most important metric - total acquisition cost -->
              <h6 class="text-uppercase mt-0 mb-0">Total Purchase Price</h6>
              <!-- WHAT: Icon indicator for purchase/acquisition metric -->
              <!-- WHY: Visual cue for metric type -->
              <i class="mdi mdi-cash-multiple text-primary"></i>
            </div>
            <!-- WHAT: Primary metric value displayed prominently -->
            <!-- WHY: Most important information - total acquisition price -->
            <h2 class="my-2 fs-3">{{ formatCurrency(poolMetrics.totalAcquisitionPrice) }}</h2>
            
            <!-- WHAT: Secondary metrics section showing bid percentages -->
            <!-- WHY: Display multiple related metrics in the same card -->
            <!-- HOW: Use divider and smaller text for secondary metrics; clearfix ensures border/content start below floated icon -->
            <div class="border-top pt-2 mt-2 clearfix">
              <!-- WHAT: Bid % of UPB metric -->
              <!-- WHY: Shows acquisition as percentage of current balance -->
              <div class="d-flex justify-content-between align-items-center mb-1">
                <span class="text-muted small">Bid % of UPB</span>
                <span class="fw-semibold">{{ poolMetrics.bidPctUPB.toFixed(1) }}%</span>
              </div>
              <!-- WHAT: Bid % of Total Debt metric -->
              <!-- WHY: Shows acquisition as percentage of total debt -->
              <div class="d-flex justify-content-between align-items-center mb-1">
                <span class="text-muted small">Bid % of Total Debt</span>
                <span class="fw-semibold">{{ poolMetrics.bidPctTotalDebt.toFixed(1) }}%</span>
              </div>
              <!-- WHAT: Bid % of Seller As-Is metric -->
              <!-- WHY: Shows acquisition as percentage of seller's as-is valuation -->
              <div class="d-flex justify-content-between align-items-center">
                <span class="text-muted small">Bid % of Seller As-Is</span>
                <span class="fw-semibold">{{ poolMetrics.bidPctSellerAsIs.toFixed(1) }}%</span>
              </div>
            </div>
          </div>
        </div>
      </b-col>

      <!-- Total Proceeds Metric Card -->
      <b-col xl="4" lg="4" md="12">
        <!-- LAYOUT: Same flex/height pattern keeps Pool Totals tile aligned with neighbors in this row -->
        <div class="card tilebox-one mb-0 h-100">
          <div class="card-body pt-3 pb-2 px-3">
            <!-- WHAT: Header row for Pool Totals label + icon -->
            <!-- WHY: Align text and icon cleanly above divider without collision -->
            <div class="d-flex align-items-center justify-content-between mb-1">
              <!-- WHAT: Metric label -->
              <!-- WHY: Clear identification of what the metric represents -->
              <h6 class="text-uppercase mt-0 mb-0">POOL TOTALS</h6>
              <!-- WHAT: Icon indicator for proceeds/revenue metric -->
              <!-- WHY: Visual cue for metric type -->
              <i class="mdi mdi-trending-up text-success"></i>
            </div>
            <!-- WHAT: Description text and related pool-level totals -->
            <!-- WHY: Help users understand the metric context and related balances; clearfix keeps divider below icon -->
            <div class="border-top pt-2 mt-2 clearfix">
              <div class="d-flex justify-content-between align-items-center mb-1">
                <span class="text-muted small">Total UPB</span>
                <span class="fw-semibold">{{ formatCurrency(totalUPB) }}</span>
              </div>
              <div class="d-flex justify-content-between align-items-center mb-1">
                <span class="text-muted small">Total Debt</span>
                <span class="fw-semibold">{{ formatCurrency(totalDebt) }}</span>
              </div>
              <div class="d-flex justify-content-between align-items-center mb-1">
                <span class="text-muted small">Seller As-Is</span>
                <span class="fw-semibold">{{ formatCurrency(sellerAsIsValue) }}</span>
              </div>
              <div class="d-flex justify-content-between align-items-center">
                <span class="text-muted small">Underwritten As-Is</span>
                <span class="fw-semibold">{{ formatCurrency(totalUnderwrittenAsIs) }}</span>
              </div>
            </div>
          </div>
        </div>
      </b-col>

      <!-- Net P&L Metric Card -->
      <b-col xl="4" lg="4" md="12">
        <!-- LAYOUT: Return Metrics tile reuses same h-100 flex pattern so all three headers line up cleanly -->
        <div class="card tilebox-one mb-0 h-100">
          <div class="card-body pt-3 pb-2 px-3">
            <!-- WHAT: Header row for Return Metrics label + icon -->
            <!-- WHY: Align label and icon on one row and keep divider below both -->
            <div class="d-flex align-items-center justify-content-between mb-1">
              <!-- WHAT: Metric label -->
              <!-- WHY: Clear identification of what the metric represents -->
              <h6 class="text-uppercase mt-0 mb-0">Return Metrics</h6>
              <!-- WHAT: Icon indicator for profit/loss metric with conditional color -->
              <!-- WHY: Visual cue for metric type, color indicates positive/negative -->
              <i
                class="mdi mdi-chart-line"
                :class="poolMetrics.netPL >= 0 ? 'text-success' : 'text-danger'"
              ></i>
            </div>
            <!-- WHAT: Primary metric value displayed prominently with conditional color -->
            <!-- WHY: Most important information - profit or loss amount, color indicates performance -->
            <h2 class="my-2 fs-3" :class="poolMetrics.netPL >= 0 ? 'text-success' : 'text-danger'">
              {{ poolIRR > 0 ? (poolIRR * 100).toFixed(1) + '%' : '-' }}
              /
              {{ poolMetrics.poolMOIC > 0 ? poolMetrics.poolMOIC.toFixed(2) + 'x' : '-' }}
            </h2>
            <!-- WHAT: Secondary metrics section for NPV and Net P&L -->
            <!-- WHY: Group related return metrics under the main IRR / MOIC header; clearfix keeps line below icon -->
            <div class="border-top pt-2 mt-2 clearfix">
              <div class="d-flex justify-content-between align-items-center mb-1">
                <span class="text-muted small">NPV</span>
                <span class="fw-semibold">{{ formatCurrency(poolNPV) }}</span>
              </div>
              <div class="d-flex justify-content-between align-items-center">
                <span class="text-muted small">Net P&L</span>
                <span class="fw-semibold" :class="poolMetrics.netPL >= 0 ? 'text-success' : 'text-danger'">
                  {{ formatCurrency(poolMetrics.netPL) }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </b-col>
    </b-row>

    <!-- WHAT: Pooled Cash Flow Table -->
    <!-- WHY: Show aggregated cash flows for all assets in the pool -->
    <!-- NOTE: Only show for REO Sale model type (FC Sale cash flows can be added later) -->
    <b-row v-if="hasSelection" class="mb-3">
      <b-col>
        <div class="card">
          <div class="card-body">
            <PooledCashFlowSeries
              :key="`pooled-cf-${selectedSellerId}-${selectedTradeId}-${reoScenario}`"
              :sellerId="selectedSellerId"
              :tradeId="selectedTradeId"
              modelType="reo_sale"
              :initialScenario="reoScenario"
            />
          </div>
        </div>
      </b-col>
    </b-row>

    <!-- Main Content Card -->
    <b-row v-if="hasSelection">
      <b-col>
        <!-- WHAT: Card Container - Wrapper for full window grid functionality -->
        <!-- WHY: Need a container element that can expand to fill viewport -->
        <!-- HOW: Use CSS class binding to toggle full window mode -->
        <div class="card" :class="{ 'full-window-grid': isFullScreen }">
          <div class="card-body">
            <!-- Loading state -->
            <div
              v-if="loading"
              class="d-flex align-items-center justify-content-center text-muted small py-5"
            >
              <div class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></div>
              <span>Loading modeling data...</span>
            </div>

            <template v-else>
              <!-- Filters Row -->
              <div class="d-flex align-items-center justify-content-between mb-3">
                <div class="d-flex align-items-center gap-3">
                  <!-- Model Type Filter -->
                  <div class="d-flex align-items-center gap-2">
                    <span class="fw-semibold text-muted small">Model Type:</span>
                    <div class="btn-group btn-group-sm" role="group">
                      <button
                        type="button"
                        class="btn"
                        :class="modelFilter === 'all' ? 'btn-primary' : 'btn-outline-primary'"
                        @click="modelFilter = 'all'"
                      >
                        All
                      </button>
                      <button
                        type="button"
                        class="btn"
                        :class="modelFilter === 'fc_sale' ? 'btn-primary' : 'btn-outline-primary'"
                        @click="modelFilter = 'fc_sale'"
                      >
                        FC Sale
                      </button>
                      <button
                        type="button"
                        class="btn"
                        :class="modelFilter === 'reo_sale' ? 'btn-primary' : 'btn-outline-primary'"
                        @click="modelFilter = 'reo_sale'"
                      >
                        REO Sale
                      </button>
                    </div>
                  </div>

                  <!-- Scenario Toggle (for REO) -->
                  <div v-if="modelFilter === 'reo_sale' || modelFilter === 'all'" class="d-flex align-items-center gap-2">
                    <span class="fw-semibold text-muted small">REO Scenario:</span>
                    <div class="btn-group btn-group-sm" role="group">
                      <button
                        type="button"
                        class="btn"
                        :class="reoScenario === 'as_is' ? 'btn-secondary' : 'btn-outline-secondary'"
                        @click="reoScenario = 'as_is'"
                      >
                        As-Is
                      </button>
                      <button
                        type="button"
                        class="btn"
                        :class="reoScenario === 'arv' ? 'btn-secondary' : 'btn-outline-secondary'"
                        @click="reoScenario = 'arv'"
                      >
                        ARV
                      </button>
                    </div>
                  </div>
                </div>

                <!-- Action Buttons -->
                <div class="d-flex gap-2">
                  <!-- WHAT: Full Window Button - Toggle grid to full window mode -->
                  <!-- WHY: Allow users to view more rows at once by expanding grid to fill viewport -->
                  <!-- HOW: Toggle CSS class to expand grid container to full window size -->
                  <button 
                    class="btn btn-sm btn-outline-primary" 
                    @click="toggleFullWindow"
                    :title="isFullScreen ? 'Exit Full Window' : 'Expand to Full Window'"
                    type="button"
                  >
                    <i class="mdi" :class="isFullScreen ? 'mdi-fullscreen-exit' : 'mdi-fullscreen'"></i>
                    {{ isFullScreen ? 'Exit Full Window' : 'Full Window' }}
                  </button>
                  <!-- WHAT: Refresh Button - Reload modeling data from API -->
                  <!-- WHY: Allow users to refresh data after backend updates -->
                  <!-- HOW: Call refreshData function which fetches latest data from API -->
                  <button class="btn btn-sm btn-outline-secondary" @click="refreshData" :disabled="loading">
                    <i class="mdi mdi-refresh me-1" :class="{ 'mdi-spin': loading }"></i>
                    Refresh
                  </button>
                </div>
              </div>

              <!-- WHAT: AG Grid Table - Main data grid component -->
              <!-- WHY: Display modeling data in an interactive, sortable, filterable table -->
              <!-- HOW: Use ag-grid-vue component with column definitions and row data -->
              <ag-grid-vue
                class="acq-grid"
                :style="{ width: '100%', height: gridHeight }"
                :theme="themeQuartz"
                :columnDefs="columnDefs"
                :rowData="filteredRows"
                :defaultColDef="defaultColDef"
                :animateRows="true"
                :pagination="true"
                :paginationPageSize="50"
                :rowSelection="'single'"
                @row-clicked="onRowClicked"
                @grid-ready="onGridReady"
              />
            </template>
          </div>
        </div>
      </b-col>
    </b-row>

    <!-- Empty State -->
    <b-row v-else>
      <b-col>
        <div class="card">
          <div class="card-body text-center py-5">
            <i class="mdi mdi-calculator-variant display-1 text-muted mb-3"></i>
            <h4>No Trade Selected</h4>
            <p class="text-muted">Please select a seller and trade from the Acquisitions Dashboard to view modeling data.</p>
            <router-link to="/acquisitions" class="btn btn-primary mt-2">
              <i class="ri-arrow-left-line me-1"></i>Go to Acquisitions Dashboard
            </router-link>
          </div>
        </div>
      </b-col>
    </b-row>

    <!-- Loan-Level Modal -->
    <BModal
      v-model="showLoanModal"
      size="xl"
      body-class="p-0 bg-body text-body"
      dialog-class="product-details-dialog"
      content-class="product-details-content bg-body text-body"
      hide-footer
    >
      <template #header>
        <div class="d-flex align-items-center w-100">
          <h5 class="modal-title mb-0">
            <div class="lh-sm"><span class="fw-bold">{{ modalIdText }}</span></div>
            <div class="text-muted lh-sm"><span class="fw-bold text-dark fs-4">{{ modalAddrText }}</span></div>
          </h5>
          <div class="ms-auto">
            <button type="button" class="btn-close" @click="showLoanModal = false" aria-label="Close" />
          </div>
        </div>
      </template>

      <LoanLevelIndex
        v-if="selectedAssetId"
        :key="`loan-${selectedAssetId}`"
        :assetId="selectedAssetId"
        :row="selectedRow"
        :address="selectedAddr"
        :standalone="false"
      />
    </BModal>
  </Layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useAcqSelectionsStore } from '@/stores/acqSelections'
import Layout from '@/components/layouts/layout.vue'
import { BModal } from 'bootstrap-vue-next'
import LoanLevelIndex from '@/views/acq_module/loanlvl/loanlvl_index.vue'
import { AgGridVue } from 'ag-grid-vue3'
import { themeQuartz } from 'ag-grid-community'
import type { ColDef } from 'ag-grid-community'
import http from '@/lib/http'
import PooledCashFlowSeries from '@/components/custom/PooledCashFlowSeries.vue'

// Stores
const acqStore = useAcqSelectionsStore()
const { selectedSellerId, selectedTradeId, tradeOptions } = storeToRefs(acqStore)

// State
const loading = ref(false)
const rows = ref<any[]>([])
const rawAssets = ref<any[]>([])  // Store raw data from API for scenario switching
const modelFilter = ref<'all' | 'fc_sale' | 'reo_sale'>('all')
const reoScenario = ref<'as_is' | 'arv'>('as_is')

// Pool summary for total assets and UPB
const poolSummary = ref<any>(null)

// Modeling summary from backend (pool-level metrics)
const modelingSummary = ref<any>(null)

// Underwritten As-Is total derived from modeling data (as-is proceeds)
const totalUnderwrittenAsIs = computed(() => {
  const summary = modelingSummary.value
  if (!summary) return 0
  const v = Number(summary.underwritten_asis_total ?? 0)
  return Number.isNaN(v) ? 0 : v
})

// Selection state
const hasSelection = computed(() => !!selectedSellerId.value && !!selectedTradeId.value)

// Modal state
const showLoanModal = ref(false)
const selectedAssetId = ref<string | null>(null)
const selectedRow = ref<any>(null)
const selectedAddr = ref<string | null>(null)

// AG Grid instance
const gridApi = ref<any>(null)

// WHAT: Full window state - Tracks whether grid is in full window mode
// WHY: Needed to update button icon and text based on current state
// HOW: Boolean ref that tracks full window status (CSS-based, not browser fullscreen API)
const isFullScreen = ref(false)

// WHAT: Grid height - Dynamic height for the grid component
// WHY: Default height is 720px (20% taller than original 600px), adjusts in full window mode
// HOW: Computed property that returns appropriate height based on full window state
const gridHeight = computed(() => {
  // WHAT: Default height increased by 20% (600px * 1.2 = 720px)
  // WHY: User requested 20% taller grid to see more rows at once
  const defaultHeight = '720px'
  // WHAT: Full window mode uses 100% height (flex layout handles sizing)
  // WHY: In full window mode, grid is in flex container and will expand automatically
  // HOW: Return 100% so flex layout can properly size the grid
  return isFullScreen.value ? '100%' : defaultHeight
})

// Current trade name
const currentTradeName = computed(() => {
  const trade = tradeOptions.value.find(t => t.id === selectedTradeId.value)
  return trade?.trade_name || 'Unknown'
})

// WHAT: Total assets from pool summary
// WHY: Used to show modeled count vs total assets
// HOW: Get from pool summary API response
const totalAssets = computed(() => poolSummary.value?.assets ?? 0)
// WHAT: Total UPB (Unpaid Principal Balance) from pool summary
// WHY: Used to calculate Bid % of UPB
// HOW: Get from pool summary API response
const totalUPB = computed(() => poolSummary.value?.current_balance ?? 0)
// WHAT: Total Debt from pool summary
// WHY: Used to calculate Bid % of Total Debt
// HOW: Get from pool summary API response
const totalDebt = computed(() => Number(poolSummary.value?.total_debt ?? 0))
// WHAT: Seller As-Is Value from pool summary
// WHY: Used to calculate Bid % of Seller As-Is
// HOW: Get from pool summary API response
const sellerAsIsValue = computed(() => Number(poolSummary.value?.seller_asis_value ?? 0))

// Modal header text
const modalIdText = computed(() => {
  const row = selectedRow.value
  if (!row) return '-'
  return row.seller_loan_id || row.id || (row.asset_hub_id ? `AH-${row.asset_hub_id}` : '-')
})
const modalAddrText = computed(() => selectedAddr.value || '-')

// Filtered rows based on model type
const filteredRows = computed(() => {
  if (modelFilter.value === 'all') return rows.value
  return rows.value.filter(r => r.primary_model === modelFilter.value)
})

// Pool-level metrics from backend modeling summary (scenario-aware)
const poolMetrics = computed(() => {
  const summary = modelingSummary.value
  const scenarioKey = reoScenario.value === 'arv' ? 'arv' : 'as_is'
  if (!summary || !summary[scenarioKey]) {
    return {
      totalAcquisitionPrice: 0,
      totalCosts: 0,
      totalProceeds: 0,
      netPL: 0,
      poolMOIC: 0,
      bidPctUPB: 0,
      bidPctTotalDebt: 0,
      bidPctSellerAsIs: 0,
      modeledCount: 0,
    }
  }

  const branch = summary[scenarioKey] || {}

  return {
    totalAcquisitionPrice: Number(summary.total_acquisition_price ?? 0),
    totalCosts: Number(branch.total_costs ?? 0),
    totalProceeds: Number(branch.total_proceeds ?? 0),
    netPL: Number(branch.net_pl ?? 0),
    poolMOIC: Number(branch.moic ?? 0),
    bidPctUPB: Number(summary.bid_pct_upb ?? 0),
    bidPctTotalDebt: Number(summary.bid_pct_total_debt ?? 0),
    bidPctSellerAsIs: Number(summary.bid_pct_seller_asis ?? 0),
    modeledCount: Number(summary.modeled_count ?? 0),
  }
})

// Pool-level annualized simple return from backend modeling summary
const poolIRR = computed(() => {
  const summary = modelingSummary.value
  const scenarioKey = reoScenario.value === 'arv' ? 'arv' : 'as_is'
  if (!summary || !summary[scenarioKey]) return 0
  const v = Number(summary[scenarioKey].annualized_roi ?? 0)
  return Number.isNaN(v) ? 0 : v
})

// Pool-level NPV from backend modeling summary (placeholder equals Net P&L)
const poolNPV = computed(() => {
  const summary = modelingSummary.value
  const scenarioKey = reoScenario.value === 'arv' ? 'arv' : 'as_is'
  if (!summary || !summary[scenarioKey]) return 0
  const v = Number(summary[scenarioKey].npv ?? 0)
  return Number.isNaN(v) ? 0 : v
})

// AG Grid column definitions
const columnDefs = computed(() => [
  {
    headerName: 'Loan ID',
    field: 'seller_loan_id',
    pinned: 'left' as const,
    width: 140,
    cellClass: 'fw-semibold text-primary text-center cursor-pointer',
  },
  {
    headerName: 'Address',
    field: 'street_address',
    width: 200,
    headerClass: ['ag-left-aligned-header', 'text-start'],
    cellClass: ['ag-left-aligned-cell', 'text-start', 'cursor-pointer'],
    cellStyle: { justifyContent: 'flex-start', textAlign: 'left' },
  },
  {
    headerName: 'City',
    field: 'city',
    width: 140,
    headerClass: ['ag-left-aligned-header', 'text-start'],
    cellClass: ['ag-left-aligned-cell', 'text-start'],
    cellStyle: { justifyContent: 'flex-start', textAlign: 'left' },
  },
  {
    headerName: 'State',
    field: 'state',
    width: 90,
  },
  {
    headerName: 'Strategy',
    field: 'primary_model',
    width: 120,
    cellRenderer: (params: any) => {
      const model = params.value
      if (model === 'fc_sale') return '<span class="badge bg-warning">FC Sale</span>'
      if (model === 'reo_sale') return '<span class="badge bg-info">REO Sale</span>'
      return '<span class="badge bg-secondary">—</span>'
    },
  },
  {
    headerName: 'Acquisition Price',
    field: 'acquisition_price',
    width: 130,
    valueFormatter: (params: any) => formatCurrency(params.value),
    cellClass: 'text-center fw-semibold',
  },
  {
    headerName: 'Total Costs',
    field: 'total_costs',
    width: 130,
    valueFormatter: (params: any) => formatCurrency(params.value),
    cellClass: 'text-center text-danger',
  },
  {
    headerName: 'Expected Proceeds',
    field: 'expected_proceeds',
    width: 120,
    valueFormatter: (params: any) => formatCurrency(params.value),
    cellClass: 'text-center text-success',
  },
  {
    headerName: 'Net P&L',
    field: 'net_pl',
    width: 120,
    valueFormatter: (params: any) => formatCurrency(params.value),
    cellClass: (params: any) => `text-center fw-bold ${params.value >= 0 ? 'text-success' : 'text-danger'}`,
  },
  {
    headerName: 'MOIC',
    field: 'moic',
    width: 90,
    valueFormatter: (params: any) => params.value ? `${params.value.toFixed(2)}x` : '—',
    cellClass: (params: any) => `text-center ${params.value >= 1 ? 'text-success' : 'text-danger'}`,
  },
  {
    headerName: 'Duration',
    field: 'total_duration_months',
    width: 110,
    valueFormatter: (params: any) => params.value ? `${params.value} mo` : '—',
  },
  {
    headerName: 'Bid % UPB',
    field: 'bid_pct_upb',
    width: 120,
    valueFormatter: (params: any) => params.value ? `${params.value.toFixed(1)}%` : '—',
  },
  {
    headerName: 'Bid % TD',
    field: 'bid_pct_td',
    width: 120,
    valueFormatter: (params: any) => params.value ? `${params.value.toFixed(1)}%` : '—',
  },
  {
    headerName: 'Bid % Seller AIV',
    field: 'bid_pct_sellerasis',
    width: 120,
    valueFormatter: (params: any) => params.value ? `${params.value.toFixed(1)}%` : '—',
  },
])

const defaultColDef: ColDef = {
  resizable: true,
  filter: true,
  wrapHeaderText: true,
  autoHeaderHeight: true,
  headerClass: 'text-center',
  cellClass: 'text-center',
  floatingFilter: false,
  menuTabs: ['filterMenuTab'],
}

// Format currency
function formatCurrency(value: number | null | undefined): string {
  if (value == null) return '—'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value)
}

// Grid ready handler
function onGridReady(params: any) {
  gridApi.value = params.api
}

// WHAT: Toggle Full Window - Enter or exit full window mode for the grid
// WHY: Allow users to maximize grid viewport to see more rows at once without using browser fullscreen
// HOW: Toggle CSS class to expand grid container to fill viewport using fixed positioning
function toggleFullWindow() {
  // WHAT: Toggle full window state
  // WHY: Switch between normal and full window view
  // HOW: Simply toggle the boolean state, CSS will handle the visual changes
  isFullScreen.value = !isFullScreen.value
}

// Row click handler - open loan modal
function onRowClicked(event: any) {
  const row = event.data
  if (!row) return
  
  selectedAssetId.value = row.id || row.asset_hub_id
  selectedRow.value = row
  selectedAddr.value = row.street_address || row.property_address || '-'
  showLoanModal.value = true
}

// Fetch pool summary
async function fetchPoolSummary() {
  if (!selectedSellerId.value || !selectedTradeId.value) {
    poolSummary.value = null
    return
  }
  try {
    const resp = await http.get(`/acq/summary/pool/${selectedSellerId.value}/${selectedTradeId.value}/`)
    poolSummary.value = resp.data
  } catch (e) {
    console.error('[ModelingCenter] fetchPoolSummary failed', e)
    poolSummary.value = null
  }
}

// Map raw assets to scenario-specific values (instant, no API call)
function mapAssetsToScenario() {
  const isAsIs = reoScenario.value === 'as_is'
  
  rows.value = rawAssets.value.map((asset: any) => ({
    ...asset,
    // Use scenario-specific values
    total_costs: isAsIs ? asset.total_costs_asis : asset.total_costs_arv,
    expected_proceeds: isAsIs ? asset.expected_proceeds_asis : asset.expected_proceeds_arv,
    net_pl: isAsIs ? asset.net_pl_asis : asset.net_pl_arv,
    moic: isAsIs ? asset.moic_asis : asset.moic_arv,
    total_duration_months: isAsIs ? asset.total_duration_months_asis : asset.total_duration_months_arv,
  }))
}

// Fetch modeling data for all assets using bulk endpoint
async function fetchModelingData() {
  if (!selectedSellerId.value || !selectedTradeId.value) {
    rows.value = []
    rawAssets.value = []
    return
  }

  loading.value = true
  try {
    // Use the new bulk modeling center endpoint - single request for all assets
    const resp = await http.get(`/acq/modeling-center/${selectedSellerId.value}/${selectedTradeId.value}/`)
    rawAssets.value = resp.data?.results || []
    modelingSummary.value = resp.data?.summary || null
    
    console.log(`[ModelingCenter] Bulk endpoint returned ${rawAssets.value.length} assets`)

    // Map to scenario-specific values
    mapAssetsToScenario()
    
    console.log(`[ModelingCenter] Loaded ${rows.value.length} assets with modeling data`)
  } catch (e) {
    console.error('[ModelingCenter] fetchModelingData failed', e)
    rows.value = []
    rawAssets.value = []
    modelingSummary.value = null
  } finally {
    loading.value = false
  }
}

// Refresh all data
async function refreshData() {
  await Promise.all([fetchPoolSummary(), fetchModelingData()])
}

// Watch for selection changes
watch([selectedSellerId, selectedTradeId], () => {
  if (hasSelection.value) {
    refreshData()
  }
})

// Watch for REO scenario changes - instant remapping, no API call
watch(reoScenario, () => {
  if (rawAssets.value.length > 0) {
    mapAssetsToScenario()
  }
})

// Initial load
// WHAT: Load pool summary + modeling data when component mounts
// WHY: When a trade is already selected, user should see data without clicking Refresh
// HOW: Call refreshData once on mount if hasSelection is true
onMounted(() => {
  if (hasSelection.value) {
    refreshData()
  }
})

</script>

<style scoped>
/* Trade name styling */
.trade-name-badge {
  display: inline-block;
  color: #3577f1;
  font-size: 1rem;
  font-weight: 600;
  letter-spacing: 0.3px;
  vertical-align: middle;
}

/* Cursor pointer for clickable cells */
:deep(.cursor-pointer) {
  cursor: pointer;
}

/* Match acquisitions grid AG Grid alignment (headers + cells) */
:deep(.acq-grid .ag-header-cell-label) {
  justify-content: center;
}

:deep(.acq-grid .ag-cell) {
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
}

/* Ensure checkbox column stays centered if added later */
:deep(.acq-grid .ag-header-select-all),
:deep(.acq-grid .ag-selection-checkbox) {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  padding: 0;
}

:deep(.acq-grid .ag-header-select-all .ag-checkbox-input-wrapper),
:deep(.acq-grid .ag-selection-checkbox .ag-checkbox-input-wrapper) {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  padding: 0;
}

/* Allow multi-line headers, same as main grid */
:deep(.acq-grid .ag-header-cell-text) {
  white-space: normal !important;
  line-height: 1.2;
  word-break: break-word;
}

/* Metrics row cards - ensure equal height and consistent whitespace */
.metrics-row > .col,
.metrics-row > [class*="col-"] {
  display: flex;
}

.metrics-row .card.tilebox-one {
  flex: 1 1 auto;
}

/* WHAT: Full Window Grid Card - Styles when card is in full window mode */
/* WHY: Make grid card fill entire viewport without using browser fullscreen API */
/* HOW: Use fixed positioning to overlay the card on top of the page */
.card.full-window-grid {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  width: 100vw;
  height: 100vh;
  z-index: 9999;
  margin: 0;
  border-radius: 0;
  background-color: var(--bs-body-bg, #fff);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* WHAT: Full Window Card Body - Ensure card body expands in full window mode */
/* WHY: Card body should take available space and allow scrolling */
/* HOW: Use flex layout with overflow handling */
.card.full-window-grid .card-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 1.5rem;
}

/* WHAT: Full Window Grid - Ensure grid expands to fill available space */
/* WHY: Grid should take all available vertical space in full window mode */
/* HOW: Use flex-grow to fill available space with minimum height constraint */
.card.full-window-grid .acq-grid {
  flex: 1;
  min-height: 0;
  width: 100%;
}
</style>
