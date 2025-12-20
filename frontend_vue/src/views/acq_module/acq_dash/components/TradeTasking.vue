<template>
  <!-- Option 1: Status Card with Progress Bars -->
  <div class="card h-100 d-flex flex-column" data-testid="tasking-option1">
    <!-- Header -->
    <div class="d-flex card-header justify-content-between align-items-center py-2">
      <h4 class="header-title m-1">Due Diligence Tracker</h4>
    </div>

    <!-- Body -->
    <div class="card-body p-3 flex-grow-1 d-flex flex-column">
      <!-- Loading state -->
      <div v-if="isLoading" class="text-muted small py-3 d-flex align-items-center justify-content-center text-center">
        <i class="mdi mdi-loading mdi-spin me-1"></i> Loading...
      </div>

      <!-- Empty helper if no selection or no data -->
      <div v-else-if="!hasData" class="text-muted small py-3 d-flex align-items-center justify-content-center text-center">
        Select a seller and trade to see tasking metrics.
      </div>

      <!-- Values / BPOs -->
      <template v-else>
        <router-link to="/acquisitions/valuation-center" class="status-item-link mb-2">
          <div class="status-item">
            <div class="d-flex justify-content-between align-items-center">
              <div class="d-flex align-items-center">
                <i class="ri-line-chart-line me-2 text-primary fs-5"></i>
                <span class="fw-semibold">Valuation Center</span>
              </div>
              <span class="badge" :class="progressBadgeClass(valuesReconciled, totalAssets)">
               Reconciled Values {{ valuesReconciled }} / {{ totalAssets }}
              </span>
            </div>
            <div class="progress mt-1" style="height: 6px;">
              <div 
                class="progress-bar" 
                :class="progressBarClass(valuesReconciled, totalAssets)"
                role="progressbar" 
                :style="{width: progressPercent(valuesReconciled, totalAssets) + '%'}"
                :aria-valuenow="valuesReconciled" 
                :aria-valuemin="0" 
                :aria-valuemax="totalAssets"
              ></div>
            </div>
          </div>
        </router-link>

        <!-- Collateral Checks -->
        <router-link to="/acquisitions/collateral-center" class="status-item-link mb-2">
          <div class="status-item">
            <div class="d-flex justify-content-between align-items-center mb-0">
              <div class="d-flex align-items-center">
                <i class="ri-home-4-line me-2 text-success fs-5"></i>
                <span class="fw-semibold">Collateral Center</span>
              </div>
              <span class="badge" :class="progressBadgeClass(collateralCompleted, totalAssets)">
                Collateral Checks {{ collateralCompleted }} / {{ totalAssets }}
              </span>
            </div>
            <div class="progress mt-1" style="height: 6px;">
              <div 
                class="progress-bar" 
                :class="progressBarClass(collateralCompleted, totalAssets)"
                role="progressbar" 
                :style="{width: progressPercent(collateralCompleted, totalAssets) + '%'}"
                :aria-valuenow="collateralCompleted" 
                :aria-valuemin="0" 
                :aria-valuemax="totalAssets"
              ></div>
            </div>
          </div>
        </router-link>

        <!-- Title Checks -->
        <router-link to="/acquisitions/title-center" class="status-item-link mb-2">
          <div class="status-item">
            <div class="d-flex justify-content-between align-items-center mb-0">
              <div class="d-flex align-items-center">
                <i class="ri-file-shield-line me-2 text-info fs-5"></i>
                <span class="fw-semibold">Title Center</span>
              </div>
              <span class="badge" :class="progressBadgeClass(titleCompleted, totalAssets)">
                Title Checks {{ titleCompleted }} / {{ totalAssets }}
              </span>
            </div>
            <div class="progress mt-1" style="height: 6px;">
              <div 
                class="progress-bar" 
                :class="progressBarClass(titleCompleted, totalAssets)"
                role="progressbar" 
                :style="{width: progressPercent(titleCompleted, totalAssets) + '%'}"
                :aria-valuenow="titleCompleted" 
                :aria-valuemin="0" 
                :aria-valuemax="totalAssets"
              ></div>
            </div>
          </div>
        </router-link>

        <!-- Modeling Center -->
        <router-link to="/acquisitions/modeling-center" class="status-item-link">
          <div class="status-item">
            <div class="d-flex justify-content-between align-items-center mb-0">
              <div class="d-flex align-items-center">
                <i class="mdi mdi-calculator-variant me-2 text-warning fs-5"></i>
                <span class="fw-semibold">Modeling Center</span>
              </div>
              <span class="badge bg-secondary">
                Pool Modeling & Pricing
              </span>
            </div>
            <div class="progress mt-1" style="height: 6px;">
              <div 
                class="progress-bar bg-success" 
                role="progressbar" 
                style="width: 100%;"
                aria-valuenow="100" 
                aria-valuemin="0" 
                aria-valuemax="100"
              ></div>
            </div>
          </div>
        </router-link>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
// Component: TaskingGridOption1
// Purpose: Progress card layout with status icons and progress bars
// Data source: GET /acq/summary/pool/<seller_id>/<trade_id>/
// Docs reviewed: Vue 3 <script setup>, Pinia stores, Bootstrap 5 progress bars

import { ref, onMounted, watch, computed } from 'vue'
import { storeToRefs } from 'pinia'
import axios from '@/lib/http'
import { useAcqSelectionsStore } from '@/stores/acqSelections'
import { useAgGridRowsStore } from '@/stores/agGridRows'

// Reactive selection (seller/trade) from global store
const sel = useAcqSelectionsStore()
const { selectedSellerId, selectedTradeId } = storeToRefs(sel)
// Access currently loaded grid rows to compute tasking counts
const gridStore = useAgGridRowsStore()
const { rows: gridRows } = storeToRefs(gridStore)

// Local reactive state
const isLoading = ref(false)
const hasData = ref(false)
const metrics = ref({
  count: 0,
  sum_current_balance: 0,
  sum_total_debt: 0,
  sum_seller_asis_value: 0,
})

// WHAT: Pool summary from backend API (contains total asset count)
// WHY: Single source of truth for total assets
const poolSummary = ref<any>(null)

// WHAT: Valuation completion summary from backend API
// WHY: Get reconciled count from backend, not grid aggregation
const valuationSummary = ref<any>(null)

// WHAT: Collateral completion summary from backend API
// WHY: Get collateral counts from backend, not grid aggregation
const collateralSummary = ref<any>(null)

// WHAT: Title completion summary from backend API
// WHY: Get title counts from backend, not grid aggregation
const titleSummary = ref<any>(null)

// WHAT: Total assets from backend pool summary (excludes dropped assets automatically)
// WHY: Backend uses sellertrade_qs() which filters acq_status != DROP by default
// HOW: Use pool summary API, fallback to 0 if not loaded
const totalAssets = computed<number>(() => poolSummary.value?.assets ?? 0)

// WHAT: Reconciled valuations count from backend API
// WHY: Backend calculates this correctly from Valuation and SellerRawData models
const valuesReconciled = computed<number>(() => valuationSummary.value?.reconciled_count ?? 0)

// WHAT: Collateral completed count from backend API
// WHY: Backend calculates this from actual collateral check data
const collateralCompleted = computed<number>(() => collateralSummary.value?.reviewed ?? 0)

// WHAT: Title completed count from backend API
// WHY: Backend calculates this from actual title check data
const titleCompleted = computed<number>(() => titleSummary.value?.reviewed ?? 0)
// DD Approved: all required checks complete for all rows
const ddApproved = computed<boolean>(() => {
  const total = totalAssets.value
  if (!total) return false
  return valuesReconciled.value === total && collateralCompleted.value === total && titleCompleted.value === total
})

// WHAT: Fetch all summary data from backend APIs
// WHY: Single source of truth for all metrics - no frontend aggregation
async function fetchMetrics() {
  if (!selectedSellerId.value || !selectedTradeId.value) {
    hasData.value = false
    return
  }
  isLoading.value = true
  try {
    // WHAT: Fetch all summaries in parallel for efficiency
    // WHY: All metrics come from backend APIs
    const [poolResp, valuationResp, collateralResp, titleResp] = await Promise.all([
      axios.get(`/acq/summary/pool/${selectedSellerId.value}/${selectedTradeId.value}/`),
      axios.get(`/acq/summary/valuations/${selectedSellerId.value}/${selectedTradeId.value}/`),
      axios.get(`/acq/summary/collateral/${selectedSellerId.value}/${selectedTradeId.value}/`),
      axios.get(`/acq/summary/title/${selectedSellerId.value}/${selectedTradeId.value}/`),
    ])
    
    // WHAT: Store pool summary (contains total asset count)
    poolSummary.value = poolResp.data
    metrics.value = {
      count: Number(poolResp.data?.assets ?? 0),
      sum_current_balance: Number(poolResp.data?.current_balance ?? 0),
      sum_total_debt: Number(poolResp.data?.total_debt ?? 0),
      sum_seller_asis_value: Number(poolResp.data?.seller_asis_value ?? 0),
    }
    
    // WHAT: Store completion summaries
    valuationSummary.value = valuationResp.data
    collateralSummary.value = collateralResp.data
    titleSummary.value = titleResp.data
    
    hasData.value = true
  } catch (e) {
    console.error('[TradeTasking] Failed to load summaries', e)
    hasData.value = false
    // WHAT: Set defaults on error
    poolSummary.value = null
    valuationSummary.value = null
    collateralSummary.value = null
    titleSummary.value = null
  } finally {
    isLoading.value = false
  }
}

// Progress helpers
// Calculate percentage complete for progress bar
function progressPercent(completed: number, total: number): number {
  if (!total) return 0
  return Math.round((completed / total) * 100)
}

// Return Bootstrap progress bar color class based on completion percentage
// WHAT: Use Steel Blue instead of gold/warning for 50-99% completion
function progressBarClass(completed: number, total: number): string {
  const pct = progressPercent(completed, total)
  if (pct === 100) return 'bg-success'
  if (pct >= 50) return 'bg-progress-in-progress' // Custom class - Steel Blue instead of gold
  return 'bg-danger'
}

// Return Bootstrap badge color class based on completion percentage
// WHAT: Use Steel Blue instead of gold/warning for 50-99% completion
function progressBadgeClass(completed: number, total: number): string {
  const pct = progressPercent(completed, total)
  if (pct === 100) return 'bg-success'
  if (pct >= 50) return 'bg-progress-in-progress' // Custom class - Steel Blue instead of gold
  return 'bg-secondary'
}

// Formatters
function formatCurrency(n: number): string {
  return new Intl.NumberFormat('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(n || 0)
}

// Lifecycle + watchers
onMounted(() => {
  if (selectedSellerId.value && selectedTradeId.value) fetchMetrics()
})
watch([selectedSellerId, selectedTradeId], () => fetchMetrics())
</script>

<style scoped>
/* Status item link styling - Using ProjectAlpha Color Palette */
/* WHAT: Custom styling for Due Diligence Tracker status items */
/* WHY: Match action buttons styling with cream background and gold accents */
/* HOW: Apply cream background, gold border, and gold hover state */
.status-item-link {
  text-decoration: none;
  color: inherit;
  display: block;
  transition: all 0.2s ease;
  border-radius: 0.375rem;
  padding: 0.5rem 0.75rem;
  margin-left: -0.75rem;
  margin-right: -0.75rem;
  background-color: #F5F3EE !important; /* Cream - lighter than card for contrast */
  border: none !important; /* No border */
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2) !important; /* Subtle shadow for depth */
  margin-bottom: 0.5rem;
}

.status-item-link:hover {
  background-color: #D4AF37 !important; /* Accent Gold - prominent hover state */
  color: #ffffff !important; /* White text on gold */
  border: none !important; /* No border on hover */
  box-shadow: 0 4px 12px rgba(212, 175, 55, 0.4) !important; /* Enhanced gold shadow on hover */
  transform: translateX(4px);
}

.status-item-link:hover .status-item {
  box-shadow: none; /* Remove inner shadow on hover */
}

.status-item-link:hover .status-item .fw-semibold,
.status-item-link:hover .status-item span:not(.badge) {
  color: #ffffff !important; /* White text on gold hover */
}

.status-item-link:hover .status-item i {
  color: #ffffff !important; /* White icons on gold hover */
}

.status-item-link:hover .badge {
  background-color: rgba(255, 255, 255, 0.25) !important; /* Semi-transparent white badge on gold */
  color: #ffffff !important;
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
}

/* Status item styling */
.status-item {
  transition: all 0.2s ease;
}

/* Smooth progress bar transitions */
.progress-bar {
  transition: width 0.6s ease;
}

/* Custom progress bar color - Steel Blue instead of gold/warning */
/* WHAT: Replace gold/warning color with Steel Blue from palette for in-progress status */
/* WHY: User requested removal of gold from progress bars */
.bg-progress-in-progress {
  background-color: #4A6FA5 !important; /* Steel Blue - professional alternative to gold */
  color: #ffffff !important; /* White text for badges */
}
</style>
