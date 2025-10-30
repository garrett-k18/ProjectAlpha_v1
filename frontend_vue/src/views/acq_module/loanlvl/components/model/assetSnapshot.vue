<template>
  <!--
    assetSnapshot.vue
    What: Reusable asset snapshot card showing key financial and status fields.
    Why: Provide quick overview of asset fundamentals across different views.
    Where: frontend_vue/src/views/acq_module/loanlvl/components/model/assetSnapshot.vue
    How: Props-driven component that accepts row data and formats key fields consistently.
  -->
  <div class="asset-snapshot">
    <div class="card mb-3">
      <div class="card-body">
        <h5 class="card-title mb-3">Asset Snapshot</h5>
        <!-- Intro banner: classification badges (top-left) -->
        <div class="mb-3">
          <div class="d-flex flex-wrap align-items-center gap-2">
            <!-- Asset Status (moved to front) -->
            <UiBadge :tone="assetStatusTone" size="md" :label="row?.asset_status ?? '—'" ariaLabel="Asset Status" />
            <!-- Property Type -->
            <UiBadge :tone="propertyTypeTone" size="md" :label="row?.property_type ?? '—'" ariaLabel="Property Type" />
            <!-- Product Type -->
            <UiBadge :tone="productTypeTone" size="md" :label="row?.product_type ?? '—'" ariaLabel="Product Type" />
            <!-- Occupancy -->
            <UiBadge :tone="occupancyTone" size="md" :label="occupancyLabel" ariaLabel="Occupancy" />
          </div>
        </div>
        
        <!-- Financial Metrics -->
        <div class="row g-2 mb-3">
          <div class="col-md-6">
            <div class="d-flex align-items-baseline gap-2">
              <span class="text-muted">Current Balance:</span>
              <span class="fw-bold">{{ formatCurrency(row?.current_balance) }}</span>
            </div>
          </div>
          <div class="col-md-6">
            <div class="d-flex align-items-baseline gap-2">
              <span class="text-muted">Interest Rate:</span>
              <span class="fw-bold">{{ formatPercent(row?.interest_rate) }}</span>
            </div>
          </div>
        </div>

        <div class="row g-2 mb-3">
          <div class="col-md-6">
            <div class="d-flex align-items-baseline gap-2">
              <span class="text-muted">Total Debt:</span>
              <span class="fw-bold">{{ formatCurrency(row?.total_debt) }}</span>
            </div>
          </div>
          <div class="col-md-6">
            <div class="d-flex align-items-baseline gap-2">
              <span class="text-muted">Months Delinquent:</span>
              <span class="fw-bold" :class="monthsDelinquentClass">{{ formatMonthsDelinquent(row?.months_dlq) }}</span>
            </div>
          </div>
        </div>

        <div class="row g-2 mb-3">
          <div class="col-md-6">
            <div class="d-flex align-items-baseline gap-2">
              <span class="text-muted">FC Flag:</span>
              <span class="fw-bold" :class="fcFlagClass">{{ formatFcFlag(row?.fc_flag) }}</span>
            </div>
          </div>
          <div class="col-md-6">
            <!-- Reserved for future field -->
          </div>
        </div>

        <!-- Valuation Range -->
        <div class="mb-2">
          <div class="d-flex align-items-baseline gap-2">
            <span class="text-muted">Seller Valuation Range:</span>
            <span class="fw-bold">{{ formatValuationRange(row?.seller_asis_value, row?.seller_arv_value) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Props-driven asset snapshot component showing key financial metrics.
 * Accepts a row object (typically SellerRawData) and formats key fields.
 */

import { computed } from 'vue'
// Reusable badge UI + centralized tone tokens
import UiBadge from '../../../../../components/ui/UiBadge.vue'
import type { BadgeToneKey } from '../../../../../config/badgeTokens'
import { getPropertyTypeBadgeTone, getOccupancyBadgeTone, getAssetStatusBadgeTone, getProductTypeBadgeTone } from '../../../../../config/badgeTokens'

// Props - row object containing asset data
const props = defineProps<{
  row?: Record<string, any> | null
}>()

/**
 * Format currency values with proper fallback for null/undefined
 */
function formatCurrency(value: any): string {
  if (value == null || value === '' || isNaN(Number(value))) {
    return '—'
  }
  try {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(Number(value))
  } catch {
    return '—'
  }
}

/**
 * Format percentage values (interest rates)
 */
function formatPercent(value: any): string {
  if (value == null || value === '' || isNaN(Number(value))) {
    return '—'
  }
  try {
    // Assuming backend stores as decimal (0.0450 = 4.50%)
    const percent = Number(value) * 100
    return `${percent.toFixed(2)}%`
  } catch {
    return '—'
  }
}

/**
 * Format FC flag as Yes/No with appropriate styling
 */
function formatFcFlag(value: any): string {
  if (value == null || value === '') return '—'
  // Handle boolean or string values
  if (value === true || value === 'true' || value === 'Yes' || value === 'Y') {
    return 'Yes'
  }
  if (value === false || value === 'false' || value === 'No' || value === 'N') {
    return 'No'
  }
  return String(value)
}

/**
 * Format months delinquent with proper handling
 */
function formatMonthsDelinquent(value: any): string {
  if (value == null || value === '' || isNaN(Number(value))) {
    return '—'
  }
  const months = Number(value)
  if (months === 0) return 'Current'
  if (months === 1) return '1 month'
  return `${months} months`
}

/**
 * CSS class for FC flag styling
 */
const fcFlagClass = computed(() => {
  const flag = formatFcFlag(props.row?.fc_flag)
  if (flag === 'Yes') return 'text-danger'
  if (flag === 'No') return 'text-success'
  return ''
})

/**
 * CSS class for months delinquent styling
 */
const monthsDelinquentClass = computed(() => {
  const value = props.row?.months_dlq
  if (value == null || value === '' || isNaN(Number(value))) return ''
  
  const months = Number(value)
  if (months === 0) return 'text-success' // Current - green
  if (months <= 3) return 'text-warning' // 1-3 months - yellow
  return 'text-danger' // 4+ months - red
})

/**
 * Format valuation range (As-Is to ARV)
 */
function formatValuationRange(asisValue: any, arvValue: any): string {
  const asis = formatCurrency(asisValue)
  const arv = formatCurrency(arvValue)
  
  // If both values are missing, show single dash
  if (asis === '—' && arv === '—') return '—'
  
  // If one is missing, show the available one
  if (asis === '—') return arv
  if (arv === '—') return asis
  
  // If both available, show range
  if (asis === arv) return asis // Same value, no need for range
  return `${asis} - ${arv}`
}

/**
 * Badge tones
 * - Property Type uses centralized helper mapping (badgeTokens.getPropertyTypeBadgeTone)
 * - Occupancy mirrors grid enum colors: Occupied=success, Vacant=danger, Unknown=warning
 * - Asset Status mirrors grid enum colors: NPL=danger, REO=secondary, PERF=success, RPL=info
 * - Product Type uses a simple stable palette; adjust in badgeTokens if we standardize further
 */
const propertyTypeTone = computed<BadgeToneKey>(() => getPropertyTypeBadgeTone(props.row?.property_type))

const occupancyTone = computed<BadgeToneKey>(() => getOccupancyBadgeTone(props.row?.occupancy))
const occupancyLabel = computed<string>(() => {
  const v = (props.row?.occupancy ?? '').toString()
  if (!v) return '—'
  return v.toLowerCase() === 'unknown' ? 'Occ. Unknown' : v
})

const assetStatusTone = computed<BadgeToneKey>(() => getAssetStatusBadgeTone(props.row?.asset_status))

const productTypeTone = computed<BadgeToneKey>(() => getProductTypeBadgeTone(props.row?.product_type))
</script>

<style scoped>
/* Ensure consistent spacing and alignment */
.asset-snapshot .row {
  margin-left: 0;
  margin-right: 0;
}

.asset-snapshot .col-md-6 {
  padding-left: 0;
  padding-right: 0.75rem;
}

/* Responsive text sizing */
@media (max-width: 768px) {
  .asset-snapshot .col-md-6 {
    padding-right: 0;
    margin-bottom: 0.5rem;
  }
}
</style>
