<template>
  <div class="card h-100 w-100 mb-0 d-flex flex-column">
    <!-- Purchase Summary Section -->
    <div class="card-header d-flex justify-content-between align-items-center">
      <h4 class="header-title">Purchase Summary</h4>
    </div>
    <div class="card-body pt-0 pb-3">
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
          <small class="text-muted d-block">UPB at Purchase</small>
          <span class="fw-semibold text-dark">{{ currentBalance }}</span>
        </div>
        <div class="col-md-6">
          <small class="text-muted d-block">Bid % UPB</small>
          <span class="fw-semibold text-dark">{{ bidPctUpb }}</span>
        </div>
        <div class="col-md-6">
          <small class="text-muted d-block">Total Debt at Purchase</small>
          <span class="fw-semibold text-dark">{{ totalDebt }}</span>
        </div>
        <div class="col-md-6">
          <small class="text-muted d-block">Bid % TD</small>
          <span class="fw-semibold text-dark">{{ bidPctTotalDebt }}</span>
        </div>
        <div class="col-md-6">
          <small class="text-muted d-block">Seller As-Is at Purchase</small>
          <span class="fw-semibold text-dark">{{ sellerAsIs }}</span>
        </div>
        <div class="col-md-6">
          <small class="text-muted d-block">Bid % Seller As-Is</small>
          <span class="fw-semibold text-dark">{{ bidPctSellerAsIs }}</span>
        </div>
      </div>
    </div>

    <!-- Visual separator between sections -->
    <div class="border-top mx-3"></div>

    <!-- Underwriting Summary Section -->
    <div class="card-header d-flex justify-content-between align-items-center">
      <h4 class="header-title">Underwriting Summary</h4>
    </div>
    <div class="card-body pt-0 pb-3 flex-grow-1">
      <!-- Proj. Exit with duration -->
      <div class="d-flex justify-content-between align-items-center mb-2">
        <small class="text-muted">Proj. Exit</small>
        <span class="fw-semibold text-dark">
          <span v-if="projectedLiquidation">{{ projectedLiquidation }}</span>
          <span v-else>{{ blankDisplay }}</span>
          <i v-if="projectedHoldDuration" class="text-muted small ms-1">
            {{ projectedHoldDuration }} mo
          </i>
        </span>
      </div>

      <!-- Divider -->
      <div class="border-top my-2"></div>

      <!-- P&L Story: Gross Proceeds -->
      <div class="d-flex justify-content-between align-items-center mb-2">
        <small class="text-muted">Gross Proceeds</small>
        <span class="fw-semibold text-dark">{{ projectedGrossProceeds }}</span>
      </div>

      <!-- Gross Cost (negative) -->
      <div class="d-flex justify-content-between align-items-center mb-2">
        <small class="text-muted">Gross Cost</small>
        <span class="fw-semibold text-danger">{{ projectedGrossCostNegative }}</span>
      </div>

      <!-- Divider before Net P&L -->
      <div class="border-top my-2"></div>

      <!-- Net P&L (color-coded) -->
      <div class="d-flex justify-content-between align-items-center mb-2">
        <small class="text-muted fw-bold">Net P&amp;L</small>
        <span class="fw-bold" :class="netPlClass">{{ netPl }}</span>
      </div>

      <!-- Divider before returns -->
      <div class="border-top my-2"></div>

      <!-- IRR / MOIC on one line -->
      <div class="d-flex justify-content-between align-items-center">
        <small class="text-muted">IRR / MOIC</small>
        <span class="fw-semibold text-dark">{{ irrMoicDisplay }}</span>
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

// WHAT: Render decimal values as percentage strings for IRR display
const formatPercent = (value: unknown): string => {
  const numeric = maybeNumber(value)
  if (numeric === null) return blankDisplay
  return `${(numeric * 100).toFixed(2)}%`
}

// WHAT: Render percent values stored as 0-100 (not decimals)
const formatPercentWhole = (value: unknown): string => {
  const numeric = maybeNumber(value)
  if (numeric === null) return blankDisplay
  return `${numeric.toFixed(2)}%`
}

// WHAT: Provide consistent numeric formatting for MOIC and other ratios
const formatNumber = (value: unknown, digits = 2): string => {
  const numeric = maybeNumber(value)
  if (numeric === null) return blankDisplay
  return numeric.toFixed(digits)
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
const currentBalance = computed(() => formatCurrency(props.row?.current_balance))
const totalDebt = computed(() => formatCurrency(props.row?.total_debt))
const sellerAsIs = computed(() => formatCurrency(props.row?.seller_asis_value))
const bidPctUpb = computed(() => formatPercentWhole(props.row?.bid_pct_upb))
const bidPctTotalDebt = computed(() => formatPercentWhole(props.row?.bid_pct_td))
const bidPctSellerAsIs = computed(() => formatPercentWhole(props.row?.bid_pct_sellerasis))
const initialUwRange = computed(() => {
  const asIs = formatCurrency(props.row?.internal_initial_uw_asis_value)
  const arv = formatCurrency(props.row?.internal_initial_uw_arv_value)

  if (!asIs && !arv) return blankDisplay
  if (asIs && arv) return `${asIs} - ${arv}`
  return asIs || arv
})
const projectedLiquidation = computed(() => formatDate(props.row?.exit_date)) // WHAT: Surface projected liquidation date from blended outcome model
const projectedHoldDuration = computed(() => {
  // WHAT: Try to get pre-calculated hold duration from model first
  const duration = maybeNumber(props.row?.expected_hold_duration ?? props.row?.total_hold)
  if (duration !== null) return String(Math.ceil(duration))

  // WHY: Fallback to manual calculation if the model field is empty but dates are present
  // HOW: Calculate month difference between purchase_date and exit_date
  if (props.row?.purchase_date && props.row?.exit_date) {
    try {
      const start = new Date(String(props.row.purchase_date))
      const end = new Date(String(props.row.exit_date))
      if (!isNaN(start.getTime()) && !isNaN(end.getTime())) {
        let months = (end.getFullYear() - start.getFullYear()) * 12 + (end.getMonth() - start.getMonth())
        
        // WHAT: "Round up" logic
        // WHY: If there are ANY extra days into the next month, count it as a full month
        if (end.getDate() > start.getDate()) {
          months += 1
        }
        
        return months > 0 ? String(months) : ''
      }
    } catch (e) {
      /* ignore calculation errors */
    }
  }
  return ''
})
const projectedGrossProceeds = computed(() => formatCurrency(props.row?.expected_gross_proceeds)) // WHAT: Render modeled gross proceeds estimate
const projectedGrossCost = computed(() => formatCurrency(props.row?.expected_gross_cost)) // WHAT: Show modeled gross cost from the blended outcome model
const projectedIrr = computed(() => formatPercent(props.row?.expected_irr)) // WHAT: Format modeled IRR as percentage text
const moic = computed(() => formatNumber(props.row?.expected_moic)) // WHAT: Format MOIC ratio for quick review

// WHAT: Format negative values with parentheses for P&L story
const projectedGrossCostNegative = computed(() => {
  const value = maybeNumber(props.row?.expected_gross_cost)
  if (value === null) return blankDisplay
  return `(${formatCurrency(value)})`
})

// WHAT: Calculate Net P&L from Gross Proceeds - Gross Cost
const netPl = computed(() => {
  const proceeds = maybeNumber(props.row?.expected_gross_proceeds)
  const cost = maybeNumber(props.row?.expected_gross_cost)
  
  if (proceeds === null && cost === null) return blankDisplay
  
  const netValue = (proceeds ?? 0) - (cost ?? 0)
  return formatCurrency(netValue)
})

// WHAT: Color class for Net P&L based on positive/negative value
const netPlClass = computed(() => {
  const proceeds = maybeNumber(props.row?.expected_gross_proceeds)
  const cost = maybeNumber(props.row?.expected_gross_cost)
  
  if (proceeds === null && cost === null) return 'text-dark'
  
  const netValue = (proceeds ?? 0) - (cost ?? 0)
  return netValue >= 0 ? 'text-success' : 'text-danger'
})

// WHAT: Combined IRR / MOIC display on one line
const irrMoicDisplay = computed(() => {
  const irr = projectedIrr.value
  const moicVal = moic.value
  
  if (!irr && !moicVal) return blankDisplay
  
  const moicFormatted = moicVal ? `${moicVal}x` : ''
  
  if (irr && moicFormatted) return `${irr} / ${moicFormatted}`
  return irr || moicFormatted
})
</script>
