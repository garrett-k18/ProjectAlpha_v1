<template>
  <b-row class="g-2 mb-2">
    <b-col xl="3" lg="6">
      <div class="card tilebox-one mb-0">
        <div class="card-body pt-3 pb-2 px-3">
          <i class="uil uil-dollar-sign float-end text-primary" aria-hidden="true"></i>
          <h6 class="text-uppercase mt-0">Total UPB</h6>
          <h2 class="my-2">
            <span v-if="loading">...</span>
            <span v-else class="fs-3 fs-lg-1">{{ formatCurrency(totalUpb) }}</span>
          </h2>
        </div>
      </div>
    </b-col>

    <b-col xl="3" lg="6">
      <div class="card tilebox-one mb-0">
        <div class="card-body pt-3 pb-2 px-3">
          <i class="uil uil-apps float-end text-success" aria-hidden="true"></i>
          <h6 class="text-uppercase mt-0">Asset Count</h6>
          <h2 class="my-2">
            <span v-if="loading">...</span>
            <span v-else class="fs-3 fs-lg-1">{{ formatNumber(assetCount) }}</span>
          </h2>
        </div>
      </div>
    </b-col>

    <b-col xl="3" lg="6">
      <div class="card tilebox-one mb-0">
        <div class="card-body pt-3 pb-2 px-3">
          <i class="uil uil-chart-line float-end text-warning" aria-hidden="true"></i>
          <h6 class="text-uppercase mt-0">Avg LTV</h6>
          <h2 class="my-2 d-flex align-items-baseline">
            <span v-if="loading">...</span>
            <span v-else :class="['fs-3 fs-lg-1', ltvColorClass]">{{ formatPercent(avgLtv) }}</span>
          </h2>
        </div>
      </div>
    </b-col>

    <b-col xl="3" lg="6">
      <div class="card tilebox-one mb-0">
        <div class="card-body pt-3 pb-2 px-3">
          <i class="uil uil-exclamation-triangle float-end text-danger" aria-hidden="true"></i>
          <h6 class="text-uppercase mt-0">Delinquency Rate</h6>
          <h2 class="my-2">
            <span v-if="loading">...</span>
            <span v-else class="fs-3 fs-lg-1">{{ formatPercent(delinquencyRate) }}</span>
          </h2>
        </div>
      </div>
    </b-col>
  </b-row>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ReportSummary } from '@/stores/reporting'

const props = defineProps<{
  summary: ReportSummary | null
  loading: boolean
}>()

const totalUpb = computed<number>(() => {
  if (!props.summary) return 0
  return typeof props.summary.total_upb === 'string'
    ? parseFloat(props.summary.total_upb)
    : props.summary.total_upb
})

const assetCount = computed<number>(() => {
  return props.summary?.asset_count || 0
})

const avgLtv = computed<number>(() => {
  return props.summary?.avg_ltv || 0
})

const delinquencyRate = computed<number>(() => {
  return props.summary?.delinquency_rate || 0
})

const ltvColorClass = computed<string>(() => {
  const ltv = avgLtv.value
  if (ltv > 100) return 'text-danger'
  if (ltv >= 90) return 'text-warning'
  return 'text-success'
})

function formatCurrency(value: number): string {
  const abs = Math.abs(value || 0)
  const sign = value < 0 ? '-' : ''
  
  if (abs >= 1_000_000_000) {
    return `${sign}$${(abs / 1_000_000_000).toFixed(1)}B`
  }
  if (abs >= 1_000_000) {
    return `${sign}$${(abs / 1_000_000).toFixed(1)}MM`
  }
  if (abs >= 1_000) {
    return `${sign}$${(abs / 1_000).toFixed(1)}k`
  }
  return `${sign}$${abs.toFixed(0)}`
}

function formatNumber(value: number): string {
  return new Intl.NumberFormat().format(value || 0)
}

function formatPercent(value: number): string {
  return `${(value || 0).toFixed(1)}%`
}
</script>

<style scoped>
.tilebox-one .card-body h6.text-uppercase.mt-0 {
  margin-bottom: 0.25rem;
}

.tilebox-one .card-body h2.my-2 {
  display: flex;
  align-items: baseline;
  min-height: 2.25rem;
  margin-top: 0.5rem;
  margin-bottom: 0.25rem;
  white-space: nowrap;
}
</style>
