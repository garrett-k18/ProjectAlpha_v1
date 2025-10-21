<template>
  <div class="card h-100 w-100">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Asset Summary</h4>
    </div>
    <div class="card-body pt-0">
      <div class="row g-3">
        <div class="col-md-6">
          <small class="text-muted d-block">Asset Status</small>
          <UiBadge
            v-if="showAssetStatusBadge"
            :tone="assetStatusTone"
            size="sm"
            :label="assetStatus"
          />
          <span v-else class="fw-semibold text-dark">{{ assetStatus }}</span>
        </div>
        <div class="col-md-6">
          <small class="text-muted d-block">Purchase Date</small>
          <span class="fw-semibold text-dark">{{ purchaseDate }}</span>
        </div>
        <div class="col-md-6">
          <small class="text-muted d-block">Purchase Cost</small>
          <span class="fw-semibold text-dark">{{ purchaseCost }}</span>
        </div>
        <div class="col-md-6">
          <small class="text-muted d-block">Current Balance</small>
          <span class="fw-semibold text-dark">{{ currentBalance }}</span>
        </div>
        <div class="col-md-6">
          <small class="text-muted d-block">Total Debt</small>
          <span class="fw-semibold text-dark">{{ totalDebt }}</span>
        </div>
        <div class="col-md-6">
          <small class="text-muted d-block">Latest UW Value</small>
          <span class="fw-semibold text-dark">{{ latestUwValue }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, withDefaults, defineProps } from 'vue'
import UiBadge from '@/components/ui/UiBadge.vue'
import { getAssetStatusBadgeTone } from '@/config/badgeTokens'

const dash = '—'

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
  if (numeric === null) return dash
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(numeric)
}

const formatDate = (value: unknown): string => {
  if (!value) return dash
  try {
    const date = new Date(String(value))
    return Number.isNaN(date.getTime()) ? dash : date.toLocaleDateString('en-US')
  } catch (error) {
    return dash
  }
}

const formatString = (value: unknown): string => {
  if (value === null || value === undefined || value === '') return dash
  return String(value)
}

const assetStatus = computed(() => formatString(props.row?.asset_status))
const assetStatusTone = computed(() => getAssetStatusBadgeTone(props.row?.asset_status))
const showAssetStatusBadge = computed(() => assetStatus.value !== dash)
const purchaseDate = computed(() => formatDate(props.row?.purchase_date))
const purchaseCost = computed(() => formatCurrency(props.row?.purchase_cost))
const currentBalance = computed(() => formatCurrency(props.row?.servicer_loan_data?.current_balance ?? props.row?.current_balance))
const totalDebt = computed(() => formatCurrency(props.row?.servicer_loan_data?.total_debt ?? props.row?.total_debt))
const latestUwValue = computed(() => formatCurrency(props.row?.latest_uw_value ?? props.row?.latest_underwriting_value))
</script>
