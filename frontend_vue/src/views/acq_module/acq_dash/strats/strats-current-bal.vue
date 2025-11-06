<template>
  <div class="card">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Current Balance</h4>
    </div>

    <div class="card-body pt-0">
      <!-- Error state -->
      <div v-if="error" class="alert alert-danger d-flex align-items-center my-3" role="alert">
        <i class="mdi mdi-alert-circle-outline me-2"></i>
        <div>
          {{ error }}
        </div>
      </div>

      <!-- Loading state (reserve space) -->
      <div v-else-if="loading" class="d-flex align-items-center text-muted small py-3">
        <div class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></div>
        Loading stratification…
      </div>

      <!-- Empty-state helper when no seller/trade data is loaded or no bands (reserve space) -->
      <div v-else-if="!hasRows" class="text-muted small py-3 d-flex align-items-center justify-content-center text-center">
        Select a seller and trade to see stratification.
      </div>

      <!-- Borderless grid-table: rows are bands, columns are Count and Sum (no lines). Reserve space to match charts. -->
      <div v-else class="mt-2">
        <div class="table-responsive">
          <table class="table table-borderless table-striped align-middle mb-0 bands-table">
            <thead class="text-uppercase text-muted small">
              <tr>
                <th style="width: 40%">Band</th>
                <th class="text-center" style="width: 15%">Count</th>
                <th class="text-center" style="width: 15%">Current Balance</th>
                <th class="text-center" style="width: 15%">Total Debt</th>
                <th class="text-center" style="width: 15%">As-Is Value</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="band in bands" :key="band.key">
                <td class="py-2">{{ band.label }}</td>
                <td class="py-2 text-center fw-semibold">{{ formatInt(band.count) }}</td>
                <td class="py-2 text-center">{{ formatCurrencyNoDecimals(toNumber(band.sum_current_balance)) }}</td>
                <td class="py-2 text-center">{{ formatCurrencyNoDecimals(toNumber(band.sum_total_debt)) }}</td>
                <td class="py-2 text-center">{{ formatCurrencyNoDecimals(toNumber(band.sum_seller_asis_value)) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Removed footer count to reduce visual clutter and extra spacing -->
    </div>
  </div>
</template>

<script setup lang="ts">
// Documentation reviewed (per project standards):
// - Vue 3 <script setup>: https://vuejs.org/api/sfc-script-setup.html
// - Pinia stores: https://pinia.vuejs.org/core-concepts/
// - Intl.NumberFormat for number/currency formatting: MDN docs
// - Axios instance usage: https://axios-http.com/docs/instance

import { computed, onMounted, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useAcqSelectionsStore } from '@/stores/acqSelections'
import { useStratsStore, type StratBand } from '@/stores/strats'

// Selections (seller and trade)
const sel = useAcqSelectionsStore()
const { selectedSellerId, selectedTradeId, hasBothSelections } = storeToRefs(sel)

// Stratification store (server-provided)
const strats = useStratsStore()
const { loading, error } = storeToRefs(strats)

// Number parser usable for strings returned by backend
function toNumber(val: unknown): number {
  if (val === null || val === undefined || val === '') return 0
  const n = typeof val === 'number' ? val : parseFloat(String(val).replace(/,/g, ''))
  return Number.isFinite(n) ? n : 0
}

// Reactive bands fetched from backend cache
const bands = computed<StratBand[]>(() => {
  if (!hasBothSelections.value) return []
  return strats.getBands(selectedSellerId.value as number, selectedTradeId.value as number)
})

// Fetch on mount and whenever selection changes
async function ensureBands() {
  if (!hasBothSelections.value) return
  await strats.fetchBands(selectedSellerId.value as number, selectedTradeId.value as number)
}

onMounted(ensureBands)
watch([selectedSellerId, selectedTradeId], ensureBands)

// Whether we have any bands available
const hasRows = computed<boolean>(() => Array.isArray(bands.value) && bands.value.length > 0)

// Format helpers (display only; inputs use the global v-currency directive elsewhere)
function formatInt(n: number): string {
  return new Intl.NumberFormat('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(n)
}

function formatCurrencyNoDecimals(n: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'decimal',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(n)
}
</script>

<style scoped>
/* Removed fixed min-height to avoid extra whitespace at the bottom of cards. */
/* Use Bootstrap table-striped with a subtle light blue accent (uses BS5 CSS vars). */
.bands-table.table-striped {
  --bs-table-striped-bg: rgba(13, 110, 253, 0.06); /* light primary */
  --bs-table-striped-color: inherit; /* keep text color normal */
}
</style>