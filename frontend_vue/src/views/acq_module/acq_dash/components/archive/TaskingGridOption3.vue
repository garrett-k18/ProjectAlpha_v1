<template>
  <!-- Option 3: Mini Widget Grid (Tilebox Pattern) -->
  <div class="card h-100" data-testid="tasking-option3">
    <!-- Header -->
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title mb-0">Tasking - Option 3: Widget Grid</h4>
    </div>

    <!-- Body -->
    <div class="card-body pt-2 pb-2">
      <!-- Loading state -->
      <div v-if="isLoading" class="text-muted small py-3 d-flex align-items-center justify-content-center text-center">
        <i class="mdi mdi-loading mdi-spin me-1"></i> Loading...
      </div>

      <!-- Empty helper if no selection or no data -->
      <div v-else-if="!hasData" class="text-muted small py-3 d-flex align-items-center justify-content-center text-center">
        Select a seller and trade to see tasking metrics.
      </div>

      <!-- Mini widget grid (5 tileboxes in a row) -->
      <div v-else class="row g-2">
        <!-- DD Approved Tile -->
        <div class="col">
          <div class="mini-tilebox text-center p-2" :class="ddApproved ? 'border-success' : 'border-danger'">
            <i 
              :class="ddApproved ? 'ri-checkbox-circle-fill text-success' : 'ri-close-circle-fill text-danger'" 
              class="fs-1 mb-1"
              aria-label="DD Status"
            ></i>
            <div class="small text-uppercase text-muted mb-1">DD Approved</div>
            <div class="fw-bold">{{ ddApproved ? 'Yes' : 'No' }}</div>
          </div>
        </div>

        <!-- Values / BPOs Tile -->
        <div class="col">
          <div class="mini-tilebox text-center p-2" :class="tileBorderClass(valuesCompleted, totalAssets)">
            <i class="uil uil-file-check-alt fs-1 mb-1 text-primary" aria-hidden="true"></i>
            <div class="small text-uppercase text-muted mb-1">BPO / Values</div>
            <div class="fw-bold">{{ valuesCompleted }} / {{ totalAssets }}</div>
            <div class="small text-muted">{{ progressPercent(valuesCompleted, totalAssets) }}%</div>
          </div>
        </div>

        <!-- Collateral Checks Tile -->
        <div class="col">
          <div class="mini-tilebox text-center p-2" :class="tileBorderClass(collateralCompleted, totalAssets)">
            <i class="uil uil-home-alt fs-1 mb-1 text-warning" aria-hidden="true"></i>
            <div class="small text-uppercase text-muted mb-1">Collateral</div>
            <div class="fw-bold">{{ collateralCompleted }} / {{ totalAssets }}</div>
            <div class="small text-muted">{{ progressPercent(collateralCompleted, totalAssets) }}%</div>
          </div>
        </div>

        <!-- Title Checks Tile -->
        <div class="col">
          <div class="mini-tilebox text-center p-2" :class="tileBorderClass(titleCompleted, totalAssets)">
            <i class="uil uil-file-shield-alt fs-1 mb-1 text-info" aria-hidden="true"></i>
            <div class="small text-uppercase text-muted mb-1">Title</div>
            <div class="fw-bold">{{ titleCompleted }} / {{ totalAssets }}</div>
            <div class="small text-muted">{{ progressPercent(titleCompleted, totalAssets) }}%</div>
          </div>
        </div>

        <!-- As-Is Value Tile -->
        <div class="col">
          <div class="mini-tilebox text-center p-2 border-primary">
            <i class="uil uil-dollar-sign fs-1 mb-1 text-success" aria-hidden="true"></i>
            <div class="small text-uppercase text-muted mb-1">As-Is Value</div>
            <div class="fw-bold" style="font-size: 0.9rem;">{{ formatCurrencyCompact(metrics.sum_seller_asis_value) }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Component: TaskingGridOption3
// Purpose: Mini widget grid layout (tilebox pattern like top widgets)
// Data source: GET /acq/summary/pool/<seller_id>/<trade_id>/
// Docs reviewed: Vue 3 <script setup>, Pinia stores, Bootstrap 5 grid

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
    console.error('[TaskingGridOption3] Failed to load pool summary', e)
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

// Return border color class for mini tiles based on completion percentage
function tileBorderClass(completed: number, total: number): string {
  const pct = progressPercent(completed, total)
  if (pct === 100) return 'border-success'
  if (pct >= 50) return 'border-warning'
  return 'border-secondary'
}

// Formatters
// Standard currency formatter (no decimals)
function formatCurrency(n: number): string {
  return new Intl.NumberFormat('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(n || 0)
}

// Compact currency formatter for tile (e.g., $1.2M)
function formatCurrencyCompact(n: number): string {
  const num = n || 0
  if (num >= 1000000) {
    return '$' + (num / 1000000).toFixed(1) + 'M'
  } else if (num >= 1000) {
    return '$' + (num / 1000).toFixed(0) + 'K'
  }
  return '$' + num.toFixed(0)
}

// Lifecycle + watchers
onMounted(() => {
  if (selectedSellerId.value && selectedTradeId.value) fetchMetrics()
})
watch([selectedSellerId, selectedTradeId], () => fetchMetrics())
</script>

<style scoped>
/* Mini tilebox styling (compact version of main widget tiles) */
.mini-tilebox {
  background-color: var(--bs-body-bg);
  border: 2px solid var(--bs-border-color-translucent);
  border-radius: 0.375rem;
  transition: all 0.2s ease;
  min-height: 120px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.mini-tilebox:hover {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  transform: translateY(-2px);
}

/* Border color overrides for status indication */
.mini-tilebox.border-success {
  border-color: var(--bs-success) !important;
}

.mini-tilebox.border-warning {
  border-color: var(--bs-warning) !important;
}

.mini-tilebox.border-danger {
  border-color: var(--bs-danger) !important;
}

.mini-tilebox.border-primary {
  border-color: var(--bs-primary) !important;
}

.mini-tilebox.border-secondary {
  border-color: var(--bs-secondary) !important;
}

/* Responsive: stack on smaller screens */
@media (max-width: 768px) {
  .mini-tilebox {
    min-height: 100px;
  }
}
</style>
