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
            <!-- Reserved for future field -->
          </div>
        </div>

        <!-- Valuation Range -->
        <div class="mb-3">
          <div class="d-flex align-items-baseline gap-2">
            <span class="text-muted">Seller Valuation Range:</span>
            <span class="fw-bold">{{ formatValuationRange(row?.seller_asis_value, row?.seller_arv_value) }}</span>
          </div>
        </div>

        <!-- Smart Analysis Section -->
        <div class="border-top pt-3">
          <div class="d-flex align-items-center gap-2 mb-2">
            <i class="mdi mdi-brain text-primary"></i>
            <span class="fw-semibold text-primary">Smart Analysis</span>
            <div v-if="loadingRecommendations" class="spinner-border spinner-border-sm text-primary ms-auto" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
          </div>
          
          <!-- Loading state -->
          <div v-if="loadingRecommendations" class="text-center py-2">
            <span class="text-muted small">Analyzing asset characteristics...</span>
          </div>

          <!-- Asset Metrics Display - All on one line -->
          <div v-else-if="recommendations && recommendations.metrics" class="mb-2">
            <div class="d-flex flex-wrap gap-1 align-items-center">
              <!-- Delinquency Status - Always show -->
              <span v-if="recommendations.metrics.is_delinquent" class="badge bg-warning">
                <i class="mdi mdi-clock-alert me-1"></i>{{ recommendations.metrics.delinquency_months }}mo DLQ
              </span>
              <span v-else class="badge bg-success">
                <i class="mdi mdi-check me-1"></i>Current
              </span>
              
              <!-- FC Flag Status - Always show -->
              <span v-if="recommendations.metrics.is_foreclosure" class="badge bg-danger">
                <i class="mdi mdi-gavel me-1"></i>FC Active
              </span>
              <span v-else class="badge bg-light text-dark border">
                <i class="mdi mdi-shield-check me-1"></i>No FC
              </span>
              
              <!-- Equity Position -->
              <span v-if="recommendations.metrics.has_equity" class="badge bg-success">
                <i class="mdi mdi-trending-up me-1"></i>Has Equity
              </span>
              <span v-else-if="recommendations.metrics.has_equity === false" class="badge bg-danger">
                <i class="mdi mdi-trending-down me-1"></i>Underwater
              </span>
              
              <!-- Financial Metrics - Same line -->
              <span v-if="recommendations.metrics.ltv !== null" class="badge bg-light text-dark border small">
                LTV: <strong>{{ recommendations.metrics.ltv.toFixed(1) }}%</strong>
              </span>
              <span v-if="recommendations.metrics.tdtv !== null" class="badge bg-light text-dark border small">
                TDTV: <strong>{{ recommendations.metrics.tdtv.toFixed(1) }}%</strong>
              </span>
            </div>
          </div>
          
          <!-- Fallback display when no recommendations loaded yet -->
          <div v-else-if="!loadingRecommendations" class="mb-2">
            <div class="d-flex flex-wrap gap-1 align-items-center mb-2">
              <!-- Show basic info from row data as fallback -->
              <span v-if="row?.months_dlq && row.months_dlq > 0" class="badge bg-warning">
                <i class="mdi mdi-clock-alert me-1"></i>{{ row.months_dlq }}mo DLQ
              </span>
              <span v-else class="badge bg-success">
                <i class="mdi mdi-check me-1"></i>Current
              </span>
              
              <span v-if="row?.fc_flag" class="badge bg-danger">
                <i class="mdi mdi-gavel me-1"></i>FC Active
              </span>
              <span v-else class="badge bg-light text-dark border">
                <i class="mdi mdi-shield-check me-1"></i>No FC
              </span>
              
              <small class="text-muted ms-2">Loading detailed analysis...</small>
            </div>
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

// Props - row object containing asset data and recommendations
const props = defineProps<{
  row?: Record<string, any> | null
  recommendations?: any | null
  loadingRecommendations?: boolean
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
