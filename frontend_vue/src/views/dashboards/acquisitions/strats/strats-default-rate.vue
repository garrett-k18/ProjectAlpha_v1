<template>
  <div class="card">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Default Rate</h4>
    </div>

    <div class="card-body pt-0">
      <div v-if="errorText" class="alert alert-danger d-flex align-items-center my-3" role="alert">
        <i class="mdi mdi-alert-circle-outline me-2"></i>
        <div>{{ errorText }}</div>
      </div>

      <div v-else-if="isLoading" class="d-flex align-items-center text-muted small py-3">
        <div class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></div>
        Loading default rate stratification…
      </div>

      <div v-else-if="!hasRows" class="text-muted small py-3 d-flex align-items-center justify-content-center text-center">
        Select a seller and trade to see stratification.
      </div>

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
import { useRateStratCard } from './useRateStratCard'
import type { useStratsStore } from '@/stores/strats'

type StratStore = ReturnType<typeof useStratsStore>

const { bands, isLoading, errorText, hasRows, formatInt, formatCurrencyNoDecimals, toNumber } = useRateStratCard({
  fetch: (store: StratStore, sellerId: number, tradeId: number) => store.fetchBandsDefaultRate(sellerId, tradeId),
  get: (store: StratStore, sellerId: number | null, tradeId: number | null) => store.getBandsDefaultRate(sellerId, tradeId),
  loadingKey: 'loadingDefaultRate',
  errorKey: 'errorDefaultRate',
})
</script>

<style scoped>
.bands-table.table-striped {
  --bs-table-striped-bg: rgba(220, 53, 69, 0.08);
  --bs-table-striped-color: inherit;
}
</style>
