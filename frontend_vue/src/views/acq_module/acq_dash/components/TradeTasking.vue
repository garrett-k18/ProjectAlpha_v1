<template>
  <!-- Option 1: Status Card with Progress Bars -->
  <div class="card h-100 d-flex flex-column" data-testid="tasking-option1">
    <!-- Header -->
    <div class="d-flex card-header justify-content-between align-items-center py-2">
      <h4 class="header-title m-1">Trade Tracker</h4>
    </div>

    <!-- Body -->
    <div class="card-body pt-0 flex-grow-1 d-flex flex-column">
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
        <router-link to="/acquisitions/valuation-center" class="status-item-link mb-3">
          <div class="status-item">
            <div class="d-flex justify-content-between align-items-center mb-1">
              <div class="d-flex align-items-center">
                <i class="ri-line-chart-line me-2 text-primary fs-4"></i>
                <span class="fw-semibold fs-5">Valuation Center</span>
              </div>
              <span class="badge" :class="progressBadgeClass(valuesReconciled, totalAssets)">
               Reconciled Values {{ valuesReconciled }} / {{ totalAssets }}
              </span>
            </div>
            <div class="progress" style="height: 8px;">
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
        <router-link to="/acquisitions/collateral-center" class="status-item-link mb-3">
          <div class="status-item">
            <div class="d-flex justify-content-between align-items-center mb-1">
              <div class="d-flex align-items-center">
                <i class="ri-home-4-line me-2 text-success fs-4"></i>
                <span class="fw-semibold fs-5">Collateral Center</span>
              </div>
              <span class="badge" :class="progressBadgeClass(collateralCompleted, totalAssets)">
                Collateral Checks {{ collateralCompleted }} / {{ totalAssets }}
              </span>
            </div>
            <div class="progress" style="height: 8px;">
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
            <div class="d-flex justify-content-between align-items-center mb-1">
              <div class="d-flex align-items-center">
                <i class="ri-file-shield-line me-2 text-info fs-4"></i>
                <span class="fw-semibold fs-5">Title Center</span>
              </div>
              <span class="badge" :class="progressBadgeClass(titleCompleted, totalAssets)">
                Title Checks {{ titleCompleted }} / {{ totalAssets }}
              </span>
            </div>
            <div class="progress" style="height: 8px;">
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

// Derived counts from current grid rows
const totalAssets = computed<number>(() => Array.isArray(gridRows.value) ? gridRows.value.length : 0)
// WHAT: computed total of reconciled valuations across grid rows to drive Valuation Center progress UI
// WHY: business requirement is to track only assets where all valuation sources have been reconciled
// HOW: count rows with seller, at least one external (broker or bpo), and internal underwriting values present
const valuesReconciled = computed<number>(() => {
  // COMMENT: guard against undefined rows array coming from Pinia store
  const rowsForCounting = gridRows.value || []
  // COMMENT: iterate rows and retain only assets with all required valuation touchpoints populated
  return rowsForCounting.filter((row: any) => {
    // COMMENT: ensure seller valuation exists (baseline prerequisite for reconciliation)
    const hasSellerValuation = row && row.seller_asis_value != null
    // COMMENT: reconciliation accepts either broker or BPO valuation sources in addition to seller
    const hasExternalValuation = row && (row.broker_asis_value != null || row.additional_asis_value != null)
    // COMMENT: internal underwriting valuation must be present to finalize reconciliation
    const hasInternalValuation = row && row.internal_initial_uw_asis_value != null
    // COMMENT: only count the asset when all three valuation pillars are available
    return Boolean(hasSellerValuation && hasExternalValuation && hasInternalValuation)
  }).length
})
// TODO: Replace with real flags when backend fields are available
const collateralCompleted = computed<number>(() => 0)
const titleCompleted = computed<number>(() => 0)
// DD Approved: all required checks complete for all rows
const ddApproved = computed<boolean>(() => {
  const total = totalAssets.value
  if (!total) return false
  return valuesReconciled.value === total && collateralCompleted.value === total && titleCompleted.value === total
})

// Fetch pool summary for current selection
async function fetchMetrics() {
  if (!selectedSellerId.value || !selectedTradeId.value) {
    hasData.value = false
    return
  }
  isLoading.value = true
  try {
    const { data } = await axios.get(`/acq/summary/pool/${selectedSellerId.value}/${selectedTradeId.value}/`)
    metrics.value = {
      count: Number(data?.count ?? 0),
      sum_current_balance: Number(data?.sum_current_balance ?? 0),
      sum_total_debt: Number(data?.sum_total_debt ?? 0),
      sum_seller_asis_value: Number(data?.sum_seller_asis_value ?? 0),
    }
    hasData.value = true
  } catch (e) {
    console.error('[TaskingGridOption1] Failed to load pool summary', e)
    hasData.value = false
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
function progressBarClass(completed: number, total: number): string {
  const pct = progressPercent(completed, total)
  if (pct === 100) return 'bg-success'
  if (pct >= 50) return 'bg-warning'
  return 'bg-danger'
}

// Return Bootstrap badge color class based on completion percentage
function progressBadgeClass(completed: number, total: number): string {
  const pct = progressPercent(completed, total)
  if (pct === 100) return 'bg-success'
  if (pct >= 50) return 'bg-warning'
  return 'bg-secondary'
}

// Formatters
function formatCurrency(n: number): string {
  return new Intl.NumberFormat(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(n || 0)
}

// Lifecycle + watchers
onMounted(() => {
  if (selectedSellerId.value && selectedTradeId.value) fetchMetrics()
})
watch([selectedSellerId, selectedTradeId], () => fetchMetrics())
</script>

<style scoped>
/* Status item link styling */
.status-item-link {
  text-decoration: none;
  color: inherit;
  display: block;
  transition: all 0.2s ease;
  border-radius: 0.375rem;
  padding: 0.75rem;
  margin-left: -0.75rem;
  margin-right: -0.75rem;
}

.status-item-link:hover {
  background-color: rgba(0, 0, 0, 0.02);
  transform: translateX(4px);
}

.status-item-link:hover .status-item {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Status item styling */
.status-item {
  transition: all 0.2s ease;
}

/* Smooth progress bar transitions */
.progress-bar {
  transition: width 0.6s ease;
}
</style>
