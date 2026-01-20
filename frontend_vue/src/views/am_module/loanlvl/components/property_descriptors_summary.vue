<template>
  <div class="card h-100 w-100">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Asset Summary</h4>
    </div>
    <div class="card-body pt-0">
      <div class="row g-3">
        <div class="col-md-6">
          <small class="text-muted d-block">Lifecycle Status</small>
          <UiBadge
            v-if="lifecycleStatus"
            :tone="lifecycleStatusTone"
            size="sm"
            :label="lifecycleStatus"
          />
          <span v-else class="fw-semibold text-dark">{{ blankDisplay }}</span>
        </div>
        <div class="col-md-6">
          <small class="text-muted d-block">Property Type</small>
          <UiBadge
            v-if="propertyType"
            :tone="propertyTypeTone"
            size="sm"
            :label="propertyType"
          />
          <span v-else class="fw-semibold text-dark">{{ blankDisplay }}</span>
        </div>
        <div class="col-md-6">
          <small class="text-muted d-block">Occupancy</small>
          <UiBadge
            v-if="occupancy"
            :tone="occupancyTone"
            size="sm"
            :label="occupancy"
          />
          <span v-else class="fw-semibold text-dark">{{ blankDisplay }}</span>
        </div>
        <div class="col-md-6">
          <small class="text-muted d-block">Product Type</small>
          <UiBadge
            v-if="productType"
            :tone="productTypeTone"
            size="sm"
            :label="productType"
          />
          <span v-else class="fw-semibold text-dark">{{ blankDisplay }}</span>
        </div>
        <div class="col-md-6">
          <small class="text-muted d-block">Asset Class</small>
          <UiBadge
            v-if="assetClass"
            :tone="assetClassTone"
            size="sm"
            :label="assetClass"
          />
          <span v-else class="fw-semibold text-dark">{{ blankDisplay }}</span>
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
          <small class="text-muted d-block">Latest As-is Property Value</small>
          <span class="fw-semibold text-dark">{{ latestAsIsValue }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import UiBadge from '@/components/ui/UiBadge.vue'
import { getPropertyTypeBadgeTone, getOccupancyBadgeTone, getProductTypeBadgeTone, getAssetStatusBadgeTone, getLifecycleBadgeTone } from '@/config/badgeTokens'

const blankDisplay = ''

const props = withDefaults(defineProps<{
  row?: Record<string, any> | null
  assetHubId?: string | number | null
}>(), {
  row: null,
  assetHubId: null,
})

const formatString = (value: unknown): string => {
  if (value === null || value === undefined || value === '') return blankDisplay
  return String(value)
}

const propertyType = computed(() => formatString(props.row?.property_type))
const occupancy = computed(() => formatString(props.row?.occupancy))
const productType = computed(() => formatString(props.row?.product_type))
const assetClass = computed(() => formatString(props.row?.asset_class ?? props.row?.asset_status))
const lifecycleStatus = computed(() => formatString(props.row?.lifecycle_status ?? props.row?.asset_status))

const propertyTypeTone = computed(() => getPropertyTypeBadgeTone(props.row?.property_type))
const occupancyTone = computed(() => getOccupancyBadgeTone(props.row?.occupancy))
const productTypeTone = computed(() => getProductTypeBadgeTone(props.row?.product_type))
const assetClassTone = computed(() => getAssetStatusBadgeTone(props.row?.asset_class ?? props.row?.asset_status))
const lifecycleStatusTone = computed(() => getLifecycleBadgeTone(props.row?.lifecycle_status ?? props.row?.asset_status))

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

const currentBalance = computed(() => formatCurrency(props.row?.servicer_loan_data?.current_balance ?? props.row?.current_balance))
const totalDebt = computed(() =>
  formatCurrency(
    props.row?.servicer_loan_data?.computed_total_debt
      ?? props.row?.servicer_loan_data?.total_debt
      ?? props.row?.total_debt,
  )
)
const latestAsIsValue = computed(() =>
  formatCurrency(props.row?.latest_internal_asis_value)
)
</script>
