<template>
  <div class="card">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Coupon</h4>
    </div>

    <div class="card-body pt-0">
      <!-- Error state -->
      <div v-if="errorWac" class="alert alert-danger d-flex align-items-center my-3" role="alert">
        <i class="mdi mdi-alert-circle-outline me-2"></i>
        <div>
          {{ errorWac }}
        </div>
      </div>

      <!-- Loading state -->
      <div v-else-if="loadingWac" class="d-flex align-items-center text-muted small py-3">
        <div class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></div>
        Loading WAC stratification…
      </div>

      <!-- Empty state (no selection or no bands) -->
      <div v-else-if="!hasRows" class="text-muted small py-3 d-flex align-items-center justify-content-center text-center">
        Select a seller and trade to see stratification.
      </div>

      <!-- Table of WAC bands: label, count, and sums -->
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
    </div>
  </div>
  
</template>

<script setup lang="ts">
// WAC stratification card driven by backend data.
// Docs reviewed:
// - Vue <script setup>: https://vuejs.org/api/sfc-script-setup.html
// - Pinia: https://pinia.vuejs.org/
// - Intl.NumberFormat: MDN

import { computed, onMounted, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useAcqSelectionsStore } from '@/stores/acqSelections'
import { useStratsStore, type StratBand } from '@/stores/strats'

// Selection state (seller and trade)
const sel = useAcqSelectionsStore()
const { selectedSellerId, selectedTradeId, hasBothSelections } = storeToRefs(sel)

// Stratification store
const strats = useStratsStore()
const { loadingWac, errorWac } = storeToRefs(strats)

// Safe numeric conversion for string decimals
function toNumber(val: unknown): number {
  if (val === null || val === undefined || val === '') return 0
  const n = typeof val === 'number' ? val : parseFloat(String(val).replace(/,/g, ''))
  return Number.isFinite(n) ? n : 0
}

// Reactive bands from cache
const bands = computed<StratBand[]>(() => {
  if (!hasBothSelections.value) return []
  return strats.getBandsWac(selectedSellerId.value as number, selectedTradeId.value as number)
})

// Fetch bands when needed
async function ensureBands() {
  if (!hasBothSelections.value) return
  await strats.fetchBandsWac(selectedSellerId.value as number, selectedTradeId.value as number)
}

onMounted(ensureBands)
watch([selectedSellerId, selectedTradeId], ensureBands)

// UI helpers
const hasRows = computed<boolean>(() => Array.isArray(bands.value) && bands.value.length > 0)

function formatInt(n: number): string {
  return new Intl.NumberFormat(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(n)
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
/* Match styling of other stratification tables */
.bands-table.table-striped {
  --bs-table-striped-bg: rgba(13, 110, 253, 0.06);
  --bs-table-striped-color: inherit;
}
</style>