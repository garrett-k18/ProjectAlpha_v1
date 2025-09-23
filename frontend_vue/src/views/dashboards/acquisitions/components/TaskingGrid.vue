<template>
  <!-- Tasking card using Hyper UI/Bootstrap card styles -->
  <div class="card h-100" data-testid="tasking-grid-card">
    <!-- Header -->
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title mb-0">Tasking</h4>
      <!-- Optional actions area kept for future controls -->
      <div class="d-flex align-items-center gap-2"><!-- placeholder --></div>
    </div>

    <!-- Body: simple grid with headers + a single metrics row -->
    <div class="card-body pt-0 pb-2">
      <!-- Loading state -->
      <div v-if="isLoading" class="text-muted small py-3 d-flex align-items-center justify-content-center text-center">
        <i class="mdi mdi-loading mdi-spin me-1"></i> Loading...
      </div>

      <!-- Empty helper if no selection or no data -->
      <div v-else-if="!hasData" class="text-muted small py-3 d-flex align-items-center justify-content-center text-center">
        Select a seller and trade to see tasking metrics.
      </div>

      <!-- Metrics grid (column-oriented: header row + single values row) -->
      <div v-else class="table-responsive">
        <table class="table table-bordered table-sm align-middle mb-0 tasking-table rounded-2">
          <thead class="text-uppercase text-muted small">
            <tr>
              <th class="text-center" style="width: 20%">DD Approved?</th>
              <th class="text-center" style="width: 20%">Values / BPOs</th>
              <th class="text-center" style="width: 20%">Collateral Checks</th>
              <th class="text-center" style="width: 20%">Title Checks</th>
              <th class="text-center" style="width: 20%">As-Is Value</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td class="text-center">
                <i v-if="ddApproved" class="ri-check-line text-success" aria-label="Approved"></i>
                <i v-else class="ri-close-line text-danger" aria-label="Not approved"></i>
              </td>
              <td class="text-center">{{ valuesCompleted }} / {{ totalAssets }}</td>
              <td class="text-center">{{ collateralCompleted }} / {{ totalAssets }}</td>
              <td class="text-center">{{ titleCompleted }} / {{ totalAssets }}</td>
              <td class="text-center">{{ formatCurrency(metrics.sum_seller_asis_value) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Component: TaskingGrid
// Purpose: Show a simple one-row summary grid (pool-level metrics) beneath the selectors card.
// Data source: GET /acq/summary/pool/<seller_id>/<trade_id>/
// Docs reviewed: Vue 3 <script setup>, Pinia stores, Axios instance.

import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
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
  // Count of loans in the selected pool
  count: 0,
  // Sums returned by backend (numbers)
  sum_current_balance: 0,
  sum_total_debt: 0,
  sum_seller_asis_value: 0,
})

// Derived counts from current grid rows (column grid expects X / total)
const totalAssets = computed<number>(() => Array.isArray(gridRows.value) ? gridRows.value.length : 0)
// Heuristic: consider Values/BPOs complete when seller_asis_value is present
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
    // Expected shape from backend: { count: int, sum_current_balance: number, sum_total_debt: number, sum_seller_asis_value: number }
    metrics.value = {
      count: Number(data?.count ?? 0),
      sum_current_balance: Number(data?.sum_current_balance ?? 0),
      sum_total_debt: Number(data?.sum_total_debt ?? 0),
      sum_seller_asis_value: Number(data?.sum_seller_asis_value ?? 0),
    }
    hasData.value = true
  } catch (e) {
    console.error('[TaskingGrid] Failed to load pool summary', e)
    hasData.value = false
  } finally {
    isLoading.value = false
  }
}

// Formatters (match other cards: commas, no $ symbol)
function formatInt(n: number): string {
  return new Intl.NumberFormat(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(n || 0)
}
function formatCurrency(n: number): string {
  return new Intl.NumberFormat(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(n || 0)
}

// Lifecycle + watchers
onMounted(() => {
  // Debug: track mount count to diagnose duplicate renders
  try { console.count('[TaskingGrid] mounted') } catch {}
  if (selectedSellerId.value && selectedTradeId.value) fetchMetrics()
})
watch([selectedSellerId, selectedTradeId], () => fetchMetrics())

onUnmounted(() => {
  try { console.count('[TaskingGrid] unmounted') } catch {}
})
</script>

<style scoped>
/* Subtle inner/outer borders */
.tasking-table {
  border-color: var(--bs-border-color-translucent);
}
.tasking-table th,
.tasking-table td {
  border-color: var(--bs-border-color-translucent);
}
.tasking-table thead th {
  background-color: var(--bs-body-bg);
}
</style>
