<template>
  <!-- Option 2: Borderless Striped Table (like Strat Cards) -->
  <div class="card h-100" data-testid="tasking-option2">
    <!-- Header -->
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title mb-0">Tasking - Option 2: Striped Table</h4>
    </div>

    <!-- Body -->
    <div class="card-body pt-0">
      <!-- Loading state -->
      <div v-if="isLoading" class="text-muted small py-3 d-flex align-items-center justify-content-center text-center">
        <i class="mdi mdi-loading mdi-spin me-1"></i> Loading...
      </div>

      <!-- Empty helper if no selection or no data -->
      <div v-else-if="!hasData" class="text-muted small py-3 d-flex align-items-center justify-content-center text-center">
        Select a seller and trade to see tasking metrics.
      </div>

      <!-- Borderless striped table (vertical layout: metric rows) -->
      <div v-else class="mt-2">
        <div class="table-responsive">
          <table class="table table-borderless table-striped align-middle mb-0 tasking-table">
            <thead class="text-uppercase text-muted small">
              <tr>
                <th style="width: 50%">Metric</th>
                <th class="text-center" style="width: 25%">Status</th>
                <th class="text-end" style="width: 25%">Value</th>
              </tr>
            </thead>
            <tbody>
              <!-- DD Approved Row -->
              <tr>
                <td class="py-2">
                  <div class="fw-semibold">DD Approved</div>
                  <div class="text-muted small">All checks complete</div>
                </td>
                <td class="py-2 text-center">
                  <i v-if="ddApproved" class="ri-check-line text-success fs-4" aria-label="Approved"></i>
                  <i v-else class="ri-close-line text-danger fs-4" aria-label="Not approved"></i>
                </td>
                <td class="py-2 text-end">
                  <span :class="ddApproved ? 'badge bg-success' : 'badge bg-danger'">
                    {{ ddApproved ? 'Complete' : 'Pending' }}
                  </span>
                </td>
              </tr>

              <!-- Values / BPOs Row -->
              <tr>
                <td class="py-2">
                  <div class="fw-semibold">Values / BPOs</div>
                  <div class="text-muted small">Property valuations</div>
                </td>
                <td class="py-2 text-center">
                  <span class="badge" :class="progressBadgeClass(valuesCompleted, totalAssets)">
                    {{ valuesCompleted }} / {{ totalAssets }}
                  </span>
                </td>
                <td class="py-2 text-end">
                  <span class="text-muted">{{ progressPercent(valuesCompleted, totalAssets) }}%</span>
                </td>
              </tr>

              <!-- Collateral Checks Row -->
              <tr>
                <td class="py-2">
                  <div class="fw-semibold">Collateral Checks</div>
                  <div class="text-muted small">Physical inspections</div>
                </td>
                <td class="py-2 text-center">
                  <span class="badge" :class="progressBadgeClass(collateralCompleted, totalAssets)">
                    {{ collateralCompleted }} / {{ totalAssets }}
                  </span>
                </td>
                <td class="py-2 text-end">
                  <span class="text-muted">{{ progressPercent(collateralCompleted, totalAssets) }}%</span>
                </td>
              </tr>

              <!-- Title Checks Row -->
              <tr>
                <td class="py-2">
                  <div class="fw-semibold">Title Checks</div>
                  <div class="text-muted small">Legal title verification</div>
                </td>
                <td class="py-2 text-center">
                  <span class="badge" :class="progressBadgeClass(titleCompleted, totalAssets)">
                    {{ titleCompleted }} / {{ totalAssets }}
                  </span>
                </td>
                <td class="py-2 text-end">
                  <span class="text-muted">{{ progressPercent(titleCompleted, totalAssets) }}%</span>
                </td>
              </tr>

              <!-- As-Is Value Row -->
              <tr>
                <td class="py-2">
                  <div class="fw-semibold">Total As-Is Value</div>
                  <div class="text-muted small">Aggregate property value</div>
                </td>
                <td class="py-2 text-center">
                  <i class="uil uil-dollar-sign text-primary fs-4"></i>
                </td>
                <td class="py-2 text-end">
                  <span class="fw-bold">{{ formatCurrency(metrics.sum_seller_asis_value) }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Component: TaskingGridOption2
// Purpose: Borderless striped table layout (similar to stratification cards)
// Data source: GET /acq/summary/pool/<seller_id>/<trade_id>/
// Docs reviewed: Vue 3 <script setup>, Pinia stores, Bootstrap 5 tables

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
const valuesCompleted = computed<number>(() => (gridRows.value || []).filter((r: any) => r && r.seller_asis_value != null).length)
// TODO: Replace with real flags when backend fields are available
const collateralCompleted = computed<number>(() => 0)
const titleCompleted = computed<number>(() => 0)
// DD Approved: all required checks complete for all rows
const ddApproved = computed<boolean>(() => {
  const total = totalAssets.value
  if (!total) return false
  return valuesCompleted.value === total && collateralCompleted.value === total && titleCompleted.value === total
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
    console.error('[TaskingGridOption2] Failed to load pool summary', e)
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
/* Use Bootstrap table-striped with a subtle light blue accent (matches strat cards). */
.tasking-table.table-striped {
  --bs-table-striped-bg: rgba(13, 110, 253, 0.06); /* light primary */
  --bs-table-striped-color: inherit; /* keep text color normal */
}

/* Hover effect for better interactivity */
.tasking-table tbody tr {
  transition: background-color 0.15s ease;
}
</style>
