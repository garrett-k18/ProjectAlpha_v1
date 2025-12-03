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
            <i class="ri-line-chart-line me-2"></i>
            Valuation Center
            <span v-if="hasSelection" class="trade-name-badge ms-3">
              {{ currentTradeName }}
            </span>
          </h4>
        </div>
      </b-col>
    </b-row>

    <!-- Summary Cards -->
    <b-row v-if="hasSelection" class="g-2 mb-2">
      <b-col xl lg="4" md="6">
        <div class="card tilebox-one mb-0">
          <div class="card-body pt-3 pb-2 px-3">
            <i class="uil uil-building float-end"></i>
            <h6 class="text-uppercase mt-0">Seller Values</h6>
            <h2 class="my-2 fs-3">{{ valuationMetrics.seller_count }} / {{ totalAssets }}</h2>
            <p class="mb-0 text-muted">
              <span class="badge" :class="progressBadgeClass(valuationMetrics.seller_count, totalAssets)">
                {{ valuationMetrics.seller_pct }}%
              </span>
              <span class="ms-2">Complete</span>
            </p>
          </div>
        </div>
      </b-col>

      <b-col xl lg="4" md="6">
        <div class="card tilebox-one mb-0">
          <div class="card-body pt-3 pb-2 px-3">
            <i class="uil uil-file-alt float-end"></i>
            <h6 class="text-uppercase mt-0">BPO Values</h6>
            <h2 class="my-2 fs-3">{{ valuationMetrics.bpo_count }} / {{ totalAssets }}</h2>
            <p class="mb-0 text-muted">
              <span class="badge" :class="progressBadgeClass(valuationMetrics.bpo_count, totalAssets)">
                {{ valuationMetrics.bpo_pct }}%
              </span>
              <span class="ms-2">Complete</span>
            </p>
          </div>
        </div>
      </b-col>

      <b-col xl lg="4" md="6">
        <div class="card tilebox-one mb-0">
          <div class="card-body pt-3 pb-2 px-3">
            <i class="uil uil-user-check float-end"></i>
            <h6 class="text-uppercase mt-0">Broker Values</h6>
            <h2 class="my-2 fs-3">{{ valuationMetrics.broker_count }} / {{ totalAssets }}</h2>
            <p class="mb-0 text-muted">
              <span class="badge" :class="progressBadgeClass(valuationMetrics.broker_count, totalAssets)">
                {{ valuationMetrics.broker_pct }}%
              </span>
              <span class="ms-2">Complete</span>
            </p>
          </div>
        </div>
      </b-col>

      <b-col xl lg="4" md="6">
        <div class="card tilebox-one mb-0">
          <div class="card-body pt-3 pb-2 px-3">
            <i class="uil uil-shield-check float-end"></i>
            <h6 class="text-uppercase mt-0">Reconciled</h6>
            <h2 class="my-2 fs-3">{{ valuationMetrics.reconciled_count }} / {{ totalAssets }}</h2>
            <p class="mb-0 text-muted">
              <span class="badge" :class="progressBadgeClass(valuationMetrics.reconciled_count, totalAssets)">
                {{ valuationMetrics.reconciled_pct }}%
              </span>
              <span class="ms-2">Complete</span>
            </p>
          </div>
        </div>
      </b-col>

      <b-col xl lg="4" md="6">
        <div class="card tilebox-one mb-0">
          <div class="card-body pt-3 pb-2 px-3">
            <i class="uil uil-star float-end text-success"></i>
            <h6 class="text-uppercase mt-0">Graded Assets</h6>
            <h2 class="my-2 fs-3">{{ valuationMetrics.graded_count }} / {{ totalAssets }}</h2>
            <p class="mb-0 text-muted">
              <span class="badge" :class="progressBadgeClass(valuationMetrics.graded_count, totalAssets)">
                {{ valuationMetrics.graded_pct }}%
              </span>
              <span class="ms-2">Complete</span>
            </p>
          </div>
        </div>
      </b-col>
    </b-row>

    <!-- Tabs -->
    <!-- WHAT: Tab navigation managed by Vue state instead of Bootstrap JS -->
    <!-- WHY: Ensures proper tab switching without Bootstrap initialization issues -->
    <b-row v-if="hasSelection">
      <b-col>
        <div class="card">
          <div class="card-body">
            <!-- Loading state while valuation rows are being fetched -->
            <div
              v-if="showValuationLoading"
              class="d-flex align-items-center justify-content-center text-muted small py-3"
            >
              <div class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></div>
              <span>Loading valuation rows</span>
            </div>

            <template v-else>
            <ul class="nav nav-tabs nav-bordered mb-3">
              <li class="nav-item">
                <a 
                  href="#" 
                  @click.prevent="activeTab = 'overview'" 
                  class="nav-link" 
                  :class="{ active: activeTab === 'overview' }"
                >
                  <i class="ri-dashboard-line me-1"></i>Overview
                </a>
              </li>
              <li class="nav-item">
                <a 
                  href="#" 
                  @click.prevent="activeTab = 'reconciliation'" 
                  class="nav-link" 
                  :class="{ active: activeTab === 'reconciliation' }"
                >
                  <i class="ri-scales-line me-1"></i>Reconciliation
                </a>
              </li>
              <li class="nav-item">
                <a 
                  href="#" 
                  @click.prevent="activeTab = 'brokers'" 
                  class="nav-link" 
                  :class="{ active: activeTab === 'brokers' }"
                >
                  <i class="ri-user-line me-1"></i>Brokers
                </a>
              </li>
              <li class="nav-item">
                <a 
                  href="#" 
                  @click.prevent="activeTab = 'bpo-tracker'" 
                  class="nav-link" 
                  :class="{ active: activeTab === 'bpo-tracker' }"
                >
                  <i class="ri-file-list-line me-1"></i>BPO Tracker
                </a>
              </li>
            </ul>

            <!-- WHAT: Tab content panels controlled by Vue v-if for proper conditional rendering -->
            <!-- WHY: Ensures only the active tab content is rendered in the DOM -->
            <div class="tab-content">
              <OverviewTab 
                v-if="activeTab === 'overview'"
                :rows="rows"
                :selectedSellerId="selectedSellerId"
                :selectedTradeId="selectedTradeId"
                @openLoanModal="openLoanModal"
                @saveGrade="saveGrade"
                @saveInternalUW="saveInternalUW"
              />

              <ReconciliationTab 
                v-if="activeTab === 'reconciliation'"
                :rows="rows"
                @openLoanModal="openLoanModal"
                @saveInternalUW="saveInternalUW"
                @saveGrade="saveGrade"
                @saveRehabEst="saveRehabEst"
                @saveRecommendRehab="saveRecommendRehab"
              />

              <BrokersTab 
                v-if="activeTab === 'brokers'"
                :rows="rows"
                @openLoanModal="openLoanModal"
              />

              <BpoTab v-if="activeTab === 'bpo-tracker'" />
            </div>
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
            <i class="ri-line-chart-line display-1 text-muted mb-3"></i>
            <h4>No Trade Selected</h4>
            <p class="text-muted">Please select a seller and trade from the Acquisitions Dashboard to view valuation data.</p>
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
        v-if="selectedId"
        :key="`loan-${selectedId}`"
        :assetId="selectedId"
        :row="selectedRow"
        :address="selectedAddr"
        :standalone="false"
      />
    </BModal>
  </Layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useAcqSelectionsStore } from '@/stores/acqSelections'
import { useValuationCenterStore } from '@/stores/valuationCenter'
import Layout from '@/components/layouts/layout.vue'
import { BModal } from 'bootstrap-vue-next'
import LoanLevelIndex from '@/views/acq_module/loanlvl/loanlvl_index.vue'
import http from '@/lib/http'  // Still needed for fetchPoolSummary and fetchValuationMetrics
import OverviewTab from './ValuationComponenets/OverviewTab.vue'
import BrokersTab from './ValuationComponenets/BrokersTab.vue'
import BpoTab from './ValuationComponenets/BpoTab.vue'
import ReconciliationTab from './ValuationComponenets/ReconciliationTab.vue'

// Stores
const acqStore = useAcqSelectionsStore()
const { selectedSellerId, selectedTradeId, sellerOptions, tradeOptions } = storeToRefs(acqStore)
const valuationStore = useValuationCenterStore()
const { rows, loading: valuationLoading } = storeToRefs(valuationStore)

// Track initial load so we don't flash an empty table before rows arrive
const initialized = ref(false)
const showValuationLoading = computed<boolean>(() => !initialized.value || valuationLoading.value)

// Selection state
const hasSelection = computed(() => !!selectedSellerId.value && !!selectedTradeId.value)

// Modal state
const showLoanModal = ref<boolean>(false)
const selectedId = ref<string | null>(null)
const selectedRow = ref<any>(null)
const selectedAddr = ref<string | null>(null)

// Tab state
// WHAT: Track active tab using Vue state instead of Bootstrap JS
// WHY: Ensures proper tab switching in Vue 3 without Bootstrap initialization issues
const activeTab = ref<string>('overview')

// Modal header text
const modalIdText = computed<string>(() => {
  const row = selectedRow.value
  if (!row) return '-'
  return (
    row.seller_loan_id ||
    row.id ||
    row.asset_id ||
    (row.asset_hub_id ? `AH-${row.asset_hub_id}` : '-') ||
    '-'
  )
})
const modalAddrText = computed<string>(() => selectedAddr.value || '-')

// Pool summary
const poolSummary = ref<any>(null)
const poolLoading = ref(false)
const totalAssets = computed(() => poolSummary.value?.assets ?? 0)

const currentTradeName = computed(() => {
  const trade = tradeOptions.value.find(t => t.id === selectedTradeId.value)
  return trade?.trade_name || 'Unknown'
})

// Valuation metrics
const valuationMetrics = ref({
  seller_count: 0,
  seller_pct: 0,
  bpo_count: 0,
  bpo_pct: 0,
  broker_count: 0,
  broker_pct: 0,
  internal_count: 0,
  internal_pct: 0,
  reconciled_count: 0,
  reconciled_pct: 0,
  graded_count: 0,
  graded_pct: 0,
})

function progressBadgeClass(completed: number, total: number): string {
  if (!total) return 'bg-secondary'
  const pct = (completed / total) * 100
  if (pct === 100) return 'bg-success'
  if (pct >= 50) return 'bg-warning'
  return 'bg-secondary'
}

function openLoanModal(asset: any) {
  selectedId.value = asset.seller_loan_id || asset.id || String(asset.asset_hub_id)
  selectedRow.value = asset
  selectedAddr.value = asset.street_address || asset.property_address || asset.address || '-'
  showLoanModal.value = true
}

async function saveGrade(asset: any, gradeCode: string) {
  const assetId = asset.id
  if (!assetId) {
    console.error('[ValuationCenter] saveGrade: No asset id found!')
    return
  }
  
  const success = await valuationStore.saveGrade(assetId, gradeCode || null)
  if (success) {
    await fetchValuationMetrics()
  }
}

async function saveInternalUW(asset: any, field: 'asis' | 'arv', eventOrValue: Event | any) {
  let num: number | null = null
  
  // WHAT: Handle both Event (from blur/enter) and direct value (from emit)
  if (eventOrValue instanceof Event) {
    const input = eventOrValue.target as HTMLInputElement
    const valueStr = input.value.replace(/[$,]/g, '')
    if (!valueStr.trim()) return
    num = parseFloat(valueStr)
    if (isNaN(num)) return
  } else {
    num = eventOrValue
  }
  
  // WHAT: Ignore empty/invalid values
  if (num == null) return
  
  const assetId = asset.id
  if (!assetId) {
    console.error('[ValuationCenter] saveInternalUW: No asset id found!')
    return
  }
  
  const success = await valuationStore.saveInternalUWValue(assetId, field, num)
  if (success) {
    await fetchValuationMetrics()
  }
}

// WHAT: Save rehab estimate to broker valuation
// WHY: Allow users to update rehab estimates in reconciliation tab
async function saveRehabEst(asset: any, value: number) {
  const assetId = asset.id
  if (!assetId) return
  
  const success = await valuationStore.saveBrokerRehab(assetId, value)
  if (success) {
    await fetchValuationMetrics()
  }
}

// WHAT: Save recommend rehab flag to broker valuation
// WHY: Allow users to update rehab recommendation in reconciliation tab
async function saveRecommendRehab(asset: any, value: boolean) {
  const assetId = asset.id
  if (!assetId) return
  
  const success = await valuationStore.saveBrokerRecommendRehab(assetId, value)
  if (success) {
    await fetchValuationMetrics()
  }
}

async function fetchPoolSummary() {
  if (!selectedSellerId.value || !selectedTradeId.value) { poolSummary.value = null; return }
  poolLoading.value = true
  try {
    const resp = await http.get(`/acq/summary/pool/${selectedSellerId.value}/${selectedTradeId.value}/`)
    poolSummary.value = resp.data
  } catch (e) {
    console.error('fetchPoolSummary failed', e)
    poolSummary.value = null
  } finally {
    poolLoading.value = false
  }
}

async function fetchValuationMetrics() {
  if (!selectedSellerId.value || !selectedTradeId.value) return
  try {
    const resp = await http.get(`/acq/summary/valuations/${selectedSellerId.value}/${selectedTradeId.value}/`)
    const d = resp.data
    const total = totalAssets.value || 1
    valuationMetrics.value = {
      seller_count: d.seller_count || 0,
      seller_pct: Math.round(((d.seller_count || 0) / total) * 100),
      bpo_count: d.bpo_count || 0,
      bpo_pct: Math.round(((d.bpo_count || 0) / total) * 100),
      broker_count: d.broker_count || 0,
      broker_pct: Math.round(((d.broker_count || 0) / total) * 100),
      internal_count: d.internal_uw_count || 0,
      internal_pct: Math.round(((d.internal_uw_count || 0) / total) * 100),
      reconciled_count: d.reconciled_count || 0,
      reconciled_pct: Math.round(((d.reconciled_count || 0) / total) * 100),
      graded_count: d.graded_count || 0,
      graded_pct: Math.round(((d.graded_count || 0) / total) * 100),
    }
  } catch (e) {
    console.error('fetchValuationMetrics failed', e)
    valuationMetrics.value = { seller_count: 0, seller_pct: 0, bpo_count: 0, bpo_pct: 0, broker_count: 0, broker_pct: 0, internal_count: 0, internal_pct: 0, reconciled_count: 0, reconciled_pct: 0, graded_count: 0, graded_pct: 0 }
  }
}

onMounted(async () => {
  console.log('[ValuationCenter] onMounted - sellerId:', selectedSellerId.value, 'tradeId:', selectedTradeId.value)
  await fetchPoolSummary()
  await fetchValuationMetrics()
  
  // Fetch valuation center data
  if (hasSelection.value && selectedSellerId.value && selectedTradeId.value) {
    await valuationStore.refresh(selectedSellerId.value, selectedTradeId.value)
    console.log('[ValuationCenter] Loaded', rows.value?.length, 'rows')
  }
  initialized.value = true
})
</script>

<style scoped>
/* WHAT: Trade name styling */
/* WHY: Make trade name prominent and visually distinct in header */
.trade-name-badge {
  display: inline-block;
  color: #3577f1;
  font-size: 1rem;
  font-weight: 600;
  letter-spacing: 0.3px;
  vertical-align: middle;
}
</style>
