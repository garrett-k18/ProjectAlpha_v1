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

    <!-- Pool-Level KPI Widgets -->
    <b-row v-if="hasSelection" class="g-2 mb-3">
      <!-- Total Acquisition Cost -->
      <b-col xl="2" lg="4" md="6">
        <div class="card tilebox-one mb-0">
          <div class="card-body pt-3 pb-2 px-3">
            <i class="mdi mdi-cash-multiple float-end text-primary"></i>
            <h6 class="text-uppercase mt-0">Total Acquisition</h6>
            <h2 class="my-2 fs-4">{{ formatCurrency(poolMetrics.totalAcquisitionPrice) }}</h2>
            <p class="mb-0 text-muted">
              <span class="badge bg-info">{{ poolMetrics.modeledCount }} / {{ totalAssets }}</span>
              <span class="ms-2">Assets Modeled</span>
            </p>
          </div>
        </div>
      </b-col>

      <!-- Total Costs -->
      <b-col xl="2" lg="4" md="6">
        <div class="card tilebox-one mb-0">
          <div class="card-body pt-3 pb-2 px-3">
            <i class="mdi mdi-trending-down float-end text-danger"></i>
            <h6 class="text-uppercase mt-0">Total Costs</h6>
            <h2 class="my-2 fs-4">{{ formatCurrency(poolMetrics.totalCosts) }}</h2>
            <p class="mb-0 text-muted">
              <span class="text-muted small">Acq + Carry + Liq</span>
            </p>
          </div>
        </div>
      </b-col>

      <!-- Total Proceeds -->
      <b-col xl="2" lg="4" md="6">
        <div class="card tilebox-one mb-0">
          <div class="card-body pt-3 pb-2 px-3">
            <i class="mdi mdi-trending-up float-end text-success"></i>
            <h6 class="text-uppercase mt-0">Total Proceeds</h6>
            <h2 class="my-2 fs-4">{{ formatCurrency(poolMetrics.totalProceeds) }}</h2>
            <p class="mb-0 text-muted">
              <span class="text-muted small">Expected Recovery</span>
            </p>
          </div>
        </div>
      </b-col>

      <!-- Net P&L -->
      <b-col xl="2" lg="4" md="6">
        <div class="card tilebox-one mb-0">
          <div class="card-body pt-3 pb-2 px-3">
            <i class="mdi mdi-chart-line float-end" :class="poolMetrics.netPL >= 0 ? 'text-success' : 'text-danger'"></i>
            <h6 class="text-uppercase mt-0">Net P&L</h6>
            <h2 class="my-2 fs-4" :class="poolMetrics.netPL >= 0 ? 'text-success' : 'text-danger'">
              {{ formatCurrency(poolMetrics.netPL) }}
            </h2>
            <p class="mb-0 text-muted">
              <span class="text-muted small">Proceeds - Acq - Costs</span>
            </p>
          </div>
        </div>
      </b-col>

      <!-- Pool MOIC -->
      <b-col xl="2" lg="4" md="6">
        <div class="card tilebox-one mb-0">
          <div class="card-body pt-3 pb-2 px-3">
            <i class="mdi mdi-multiplication float-end" :class="poolMetrics.poolMOIC >= 1 ? 'text-success' : 'text-danger'"></i>
            <h6 class="text-uppercase mt-0">Pool MOIC</h6>
            <h2 class="my-2 fs-4" :class="poolMetrics.poolMOIC >= 1 ? 'text-success' : 'text-danger'">
              {{ poolMetrics.poolMOIC.toFixed(2) }}x
            </h2>
            <p class="mb-0 text-muted">
              <span class="text-muted small">Multiple on Invested</span>
            </p>
          </div>
        </div>
      </b-col>

      <!-- Bid % of UPB -->
      <b-col xl="2" lg="4" md="6">
        <div class="card tilebox-one mb-0">
          <div class="card-body pt-3 pb-2 px-3">
            <i class="mdi mdi-percent float-end text-info"></i>
            <h6 class="text-uppercase mt-0">Bid % of UPB</h6>
            <h2 class="my-2 fs-4">{{ poolMetrics.bidPctUPB.toFixed(1) }}%</h2>
            <p class="mb-0 text-muted">
              <span class="text-muted small">Acq / Current Balance</span>
            </p>
          </div>
        </div>
      </b-col>
    </b-row>

    <!-- Main Content Card -->
    <b-row v-if="hasSelection">
      <b-col>
        <div class="card">
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

                <!-- Refresh Button -->
                <button class="btn btn-sm btn-outline-secondary" @click="refreshData" :disabled="loading">
                  <i class="mdi mdi-refresh me-1" :class="{ 'mdi-spin': loading }"></i>
                  Refresh
                </button>
              </div>

              <!-- AG Grid Table -->
              <ag-grid-vue
                class="acq-grid"
                :style="{ width: '100%', height: '600px' }"
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
import http from '@/lib/http'

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

// Selection state
const hasSelection = computed(() => !!selectedSellerId.value && !!selectedTradeId.value)

// Modal state
const showLoanModal = ref(false)
const selectedAssetId = ref<string | null>(null)
const selectedRow = ref<any>(null)
const selectedAddr = ref<string | null>(null)

// AG Grid instance
const gridApi = ref<any>(null)

// Current trade name
const currentTradeName = computed(() => {
  const trade = tradeOptions.value.find(t => t.id === selectedTradeId.value)
  return trade?.trade_name || 'Unknown'
})

// Total assets from pool summary
const totalAssets = computed(() => poolSummary.value?.assets ?? 0)
const totalUPB = computed(() => poolSummary.value?.current_balance ?? 0)

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

// Pool-level metrics computed from rows
const poolMetrics = computed(() => {
  const data = rows.value
  if (!data.length) {
    return {
      totalAcquisitionPrice: 0,
      totalCosts: 0,
      totalProceeds: 0,
      netPL: 0,
      poolMOIC: 0,
      bidPctUPB: 0,
      modeledCount: 0,
    }
  }

  let totalAcq = 0
  let totalCosts = 0
  let totalProceeds = 0
  let modeledCount = 0

  for (const row of data) {
    const acqPrice = row.acquisition_price || 0
    const costs = row.total_costs || 0
    const proceeds = row.expected_proceeds || 0

    if (acqPrice > 0) {
      totalAcq += acqPrice
      totalCosts += costs
      totalProceeds += proceeds
      modeledCount++
    }
  }

  const netPL = totalProceeds - totalAcq - totalCosts
  const poolMOIC = totalAcq > 0 ? (totalProceeds - totalCosts) / totalAcq : 0
  const bidPctUPB = totalUPB.value > 0 ? (totalAcq / totalUPB.value) * 100 : 0

  return {
    totalAcquisitionPrice: totalAcq,
    totalCosts,
    totalProceeds,
    netPL,
    poolMOIC,
    bidPctUPB,
    modeledCount,
  }
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
    cellClass: 'text-center cursor-pointer',
  },
  {
    headerName: 'City',
    field: 'city',
    width: 120,
  },
  {
    headerName: 'State',
    field: 'state',
    width: 80,
  },
  {
    headerName: 'Model',
    field: 'primary_model',
    width: 100,
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
    width: 140,
    type: 'numericColumn',
    valueFormatter: (params: any) => formatCurrency(params.value),
    cellClass: 'text-center fw-semibold',
  },
  {
    headerName: 'Total Costs',
    field: 'total_costs',
    width: 120,
    type: 'numericColumn',
    valueFormatter: (params: any) => formatCurrency(params.value),
    cellClass: 'text-center text-danger',
  },
  {
    headerName: 'Expected Proceeds',
    field: 'expected_proceeds',
    width: 140,
    type: 'numericColumn',
    valueFormatter: (params: any) => formatCurrency(params.value),
    cellClass: 'text-center text-success',
  },
  {
    headerName: 'Net P&L',
    field: 'net_pl',
    width: 120,
    type: 'numericColumn',
    valueFormatter: (params: any) => formatCurrency(params.value),
    cellClass: (params: any) => `text-center fw-bold ${params.value >= 0 ? 'text-success' : 'text-danger'}`,
  },
  {
    headerName: 'MOIC',
    field: 'moic',
    width: 90,
    type: 'numericColumn',
    valueFormatter: (params: any) => params.value ? `${params.value.toFixed(2)}x` : '—',
    cellClass: (params: any) => `text-center ${params.value >= 1 ? 'text-success' : 'text-danger'}`,
  },
  {
    headerName: 'Duration',
    field: 'total_duration_months',
    width: 100,
    type: 'numericColumn',
    valueFormatter: (params: any) => params.value ? `${params.value} mo` : '—',
  },
  {
    headerName: 'Bid % UPB',
    field: 'bid_pct_upb',
    width: 100,
    type: 'numericColumn',
    valueFormatter: (params: any) => params.value ? `${params.value.toFixed(1)}%` : '—',
  },
  {
    headerName: 'Bid % TD',
    field: 'bid_pct_td',
    width: 110,
    type: 'numericColumn',
    valueFormatter: (params: any) => params.value ? `${params.value.toFixed(1)}%` : '—',
  },
  {
    headerName: 'Bid % Seller As-Is',
    field: 'bid_pct_sellerasis',
    width: 150,
    type: 'numericColumn',
    valueFormatter: (params: any) => params.value ? `${params.value.toFixed(1)}%` : '—',
  },
])

const defaultColDef = {
  sortable: true,
  filter: true,
  resizable: true,
  wrapHeaderText: true,
  autoHeaderHeight: true,
  headerClass: 'text-center',
  cellClass: 'text-center',
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
    
    console.log(`[ModelingCenter] Bulk endpoint returned ${rawAssets.value.length} assets`)

    // Map to scenario-specific values
    mapAssetsToScenario()
    
    console.log(`[ModelingCenter] Loaded ${rows.value.length} assets with modeling data`)
  } catch (e) {
    console.error('[ModelingCenter] fetchModelingData failed', e)
    rows.value = []
    rawAssets.value = []
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
</style>
