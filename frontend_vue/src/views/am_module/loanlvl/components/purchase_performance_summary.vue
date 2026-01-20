<template>
  <div class="card h-100 w-100">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Purchase & Performance</h4>
    </div>
    <div class="card-body pt-0">
      <div class="row g-3">
        <div class="col-md-6">
          <small class="text-muted d-block">Purchase Date</small>
          <span class="fw-semibold text-dark">{{ purchaseDate }}</span>
        </div>
        <div class="col-md-6">
          <small class="text-muted d-block">Purchase Cost</small>
          <span class="fw-semibold text-dark">{{ purchaseCost }}</span>
        </div>
        <div class="col-md-6">
          <small class="text-muted d-block">Initial UW <span class="fst-italic">As-is - ARV</span></small>
          <span class="fw-semibold text-dark">{{ initialUwRange }}</span>
        </div>
        <div class="col-md-6">
          <small class="text-muted d-block">Months DLQ</small>
          <span class="fw-semibold text-dark">{{ monthsDlq }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const blankDisplay = ''

const props = withDefaults(defineProps<{
  row?: Record<string, any> | null
  assetHubId?: string | number | null
}>(), {
  row: null,
  assetHubId: null,
})

const maybeNumber = (value: unknown): number | null => {
  if (value === null || value === undefined) return null
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : null
}

const formatCurrency = (value: unknown): string => {
  const numeric = maybeNumber(value)
  if (numeric === null) return blankDisplay
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(numeric)
}

const formatDate = (value: unknown): string => {
  if (!value) return blankDisplay
  try {
    const date = new Date(String(value))
    return Number.isNaN(date.getTime()) ? blankDisplay : date.toLocaleDateString('en-US')
  } catch (error) {
    return blankDisplay
  }
}

const formatString = (value: unknown): string => {
  if (value === null || value === undefined || value === '') return blankDisplay
  return String(value)
}

const purchaseDate = computed(() => formatDate(props.row?.purchase_date))
const purchaseCost = computed(() => formatCurrency(props.row?.purchase_cost))
const initialUwRange = computed(() => {
  const asIs = formatCurrency(props.row?.internal_initial_uw_asis_value)
  const arv = formatCurrency(props.row?.internal_initial_uw_arv_value)

  if (!asIs && !arv) return blankDisplay
  if (asIs && arv) return `${asIs} - ${arv}`
  return asIs || arv
})
const monthsDlq = computed(() => formatString(props.row?.months_dlq))
</script>
