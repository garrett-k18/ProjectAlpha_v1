<template>
  <!-- Loan-level snapshot KPIs: modular widget row -->
  <!-- Single row: 6 widgets across on lg (12/6=2). Next Due moved here. -->
  <b-row class="g-1 mb-1">
    <b-col lg="2" md="4" sm="6">
      <!-- Custom card to allow badge styling like AG Grid's categorical pills -->
      <div class="card widget-flat">
        <div class="card-body py-2 px-3 position-relative">
          <div class="position-absolute top-0 end-0 me-2 mt-2">
            <i class="mdi mdi-flag widget-icon" :style="{ fontSize: '14px', height: '24px', width: '24px', lineHeight: '24px' }"></i>
          </div>
          <h5 class="text-muted fw-normal mt-0 small" title="Asset Status">Asset Status</h5>
          <div class="value-row">
            <span v-if="assetStatusBadge" class="badge rounded-pill px-3 py-1 fs-6 fw-semibold" :class="assetStatusBadge.color">{{ assetStatusBadge.label }}</span>
            <span v-else>—</span>
          </div>
        </div>
      </div>
    </b-col>
    <b-col lg="2" md="4" sm="6">
      <!-- Custom Current Balance card to append LTV suffix like dashboard widgets -->
      <div class="card widget-flat">
        <div class="card-body py-2 px-3 position-relative">
          <div class="position-absolute top-0 end-0 me-2 mt-2">
            <i class="mdi mdi-cash-multiple widget-icon" :style="{ fontSize: '14px', height: '24px', width: '24px', lineHeight: '24px' }"></i>
          </div>
          <h5 class="text-muted fw-normal mt-0 small" title="Current Balance">Current Balance</h5>
          <div class="value-row d-flex align-items-baseline">
            <h3 class="mt-1 mb-1 fs-4">{{ currentBalanceStr }}</h3>
            <span class="text-muted d-inline-flex align-items-baseline ms-2 fs-5 fst-italic">
              <span :class="['me-1', ltvColorClass]">{{ ltvIntStr }}</span>
              <span class="text-nowrap">LTV</span>
            </span>
          </div>
        </div>
      </div>
    </b-col>
    <b-col lg="2" md="4" sm="6">
      <!-- Custom Total Debt card to append TDTV suffix mirroring Current Balance card -->
      <div class="card widget-flat">
        <div class="card-body py-2 px-3 position-relative">
          <div class="position-absolute top-0 end-0 me-2 mt-2">
            <i class="mdi mdi-finance widget-icon" :style="{ fontSize: '14px', height: '24px', width: '24px', lineHeight: '24px' }"></i>
          </div>
          <h5 class="text-muted fw-normal mt-0 small" title="Total Debt">Total Debt</h5>
          <div class="value-row d-flex align-items-baseline">
            <h3 class="mt-1 mb-1 fs-4">{{ totalDebtStr }}</h3>
            <span class="text-muted d-inline-flex align-items-baseline ms-2 fs-5 fst-italic">
              <span :class="['me-1', tdtvColorClass]">{{ tdtvIntStr }}</span>
              <span class="text-nowrap">TDTV</span>
            </span>
          </div>
        </div>
      </div>
    </b-col>
    <b-col lg="2" md="4" sm="6">
      <!-- Custom Seller As-Is / Seller ARV card to mirror spacing of Current Balance/Total Debt -->
      <div class="card widget-flat">
        <div class="card-body py-2 px-3 position-relative">
          <div class="position-absolute top-0 end-0 me-2 mt-2">
            <i class="mdi mdi-home-city widget-icon" :style="{ fontSize: '14px', height: '24px', width: '24px', lineHeight: '24px' }"></i>
          </div>
          <h5 class="text-muted fw-normal mt-0 small" title="Seller As-Is / Seller ARV">Seller As-Is / Seller ARV</h5>
          <div class="value-row d-flex align-items-baseline">
            <h3 class="mt-1 mb-1 fs-4">{{ sellerAsIsAndArvStr }}</h3>
            <!-- Invisible suffix placeholder to maintain identical spacing structure -->
            <span class="text-muted d-inline-flex align-items-baseline ms-2 fs-5 fst-italic">
              <span class="me-1 invisible">00%</span>
              <span class="text-nowrap invisible">SUFFIX</span>
            </span>
          </div>
        </div>
      </div>
    </b-col>
    <b-col lg="2" md="4" sm="6">
      <!-- Custom Interest Rate card to mirror spacing of Current Balance/Total Debt -->
      <div class="card widget-flat">
        <div class="card-body py-2 px-3 position-relative">
          <div class="position-absolute top-0 end-0 me-2 mt-2">
            <i class="mdi mdi-percent widget-icon" :style="{ fontSize: '14px', height: '24px', width: '24px', lineHeight: '24px' }"></i>
          </div>
          <h5 class="text-muted fw-normal mt-0 small" title="Interest Rate">Interest Rate</h5>
          <div class="value-row d-flex align-items-baseline">
            <h3 class="mt-1 mb-1 fs-4">{{ interestRateStr }}</h3>
            <!-- Invisible suffix placeholder to maintain identical spacing structure -->
            <span class="text-muted d-inline-flex align-items-baseline ms-2 fs-5 fst-italic">
              <span class="me-1 invisible">00%</span>
              <span class="text-nowrap invisible">SUFFIX</span>
            </span>
          </div>
        </div>
      </div>
    </b-col>
    <b-col lg="2" md="4" sm="6">
      <!-- Custom Next Due / Months DLQ card to mirror spacing -->
      <div class="card widget-flat">
        <div class="card-body py-2 px-3 position-relative">
          <div class="position-absolute top-0 end-0 me-2 mt-2">
            <i class="mdi mdi-calendar widget-icon" :style="{ fontSize: '14px', height: '24px', width: '24px', lineHeight: '24px' }"></i>
          </div>
          <h5 class="text-muted fw-normal mt-0 small" title="Next Due / Months DLQ">Next Due / Months DLQ</h5>
          <div class="value-row d-flex align-items-baseline">
            <h3 class="mt-1 mb-1 fs-4">{{ nextDueAndDlqStr }}</h3>
            <!-- Invisible suffix placeholder to maintain identical spacing structure -->
            <span class="text-muted d-inline-flex align-items-baseline ms-2 fs-5 fst-italic">
              <span class="me-1 invisible">00%</span>
              <span class="text-nowrap invisible">SUFFIX</span>
            </span>
          </div>
        </div>
      </div>
    </b-col>
  </b-row>
</template>

<script setup lang="ts">
// loanlvl-widgets.vue
// Renders a row of KPI widgets for the loan snapshot context.
// Props: row (partial SellerRawData)

import { computed, withDefaults, defineProps } from 'vue'

const props = withDefaults(defineProps<{ row?: Record<string, any> | null }>(), {
  row: null,
})

const dash = '—'
const fmtInt = (v: any): string => {
  const n = Number(v)
  return Number.isFinite(n)
    ? new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 }).format(n)
    : dash
}
const fmtPercent = (v: any): string => {
  if (v === null || v === undefined || v === '') return dash
  let n = Number(v)
  if (!Number.isFinite(n)) return dash
  if (Math.abs(n) <= 1) n = n * 100
  return `${n.toFixed(2)}%`
}

const currentBalanceStr = computed<string>(() => fmtInt(props.row?.current_balance))
const totalDebtStr = computed<string>(() => fmtInt(props.row?.total_debt))
const monthsDlqStr = computed<string>(() => fmtInt(props.row?.months_dlq))
const interestRateStr = computed<string>(() => fmtPercent(props.row?.interest_rate))
// Combined "Next Due / Months DLQ" display (e.g., "9/29/2025 / 0")
const nextDueAndDlqStr = computed<string>(() => `${nextDueStr.value} / ${monthsDlqStr.value}`)

// Additional fields for more widgets
const sellerAsIsStr = computed<string>(() => fmtInt(props.row?.seller_asis_value ?? props.row?.seller_as_is))
const sellerArvStr = computed<string>(() => fmtInt(props.row?.seller_arv_value ?? props.row?.seller_arv))
const assetStatusStr = computed<string>(() => (props.row?.asset_status ? String(props.row.asset_status) : '—'))
// Combined "Seller As-Is / Seller ARV" display (e.g., "541,408 / 612,000")
const sellerAsIsAndArvStr = computed<string>(() => `${sellerAsIsStr.value} / ${sellerArvStr.value}`)

// Map asset_status to badge label/color consistent with AG Grid enum mapping
const assetStatusBadge = computed<{ label: string; color: string } | null>(() => {
  const raw = (props.row?.asset_status ?? '').toString().trim()
  if (!raw) return null
  const map: Record<string, { label: string; color: string }> = {
    // Performing / Current
    'PERF': { label: 'PERF', color: 'bg-success' },
    'Performing': { label: 'Performing', color: 'bg-success' },
    'Current': { label: 'Current', color: 'bg-success' },
    // Re-Performing
    'RPL': { label: 'RPL', color: 'bg-info' },
    'Re-Performing': { label: 'Re-Performing', color: 'bg-info' },
    // Non-Performing / Delinquent / Default / Foreclosure
    'NPL': { label: 'NPL', color: 'bg-danger' },
    'Non-Performing': { label: 'Non-Performing', color: 'bg-danger' },
    'Delinquent': { label: 'Delinquent', color: 'bg-danger' },
    'Default': { label: 'Default', color: 'bg-warning text-dark' },
    'Foreclosure': { label: 'Foreclosure', color: 'bg-danger' },
    // REO
    'REO': { label: 'REO', color: 'bg-warning' },
  }
  return map[raw] || { label: raw, color: 'bg-warning text-dark' }
})
// LTV helpers: Current Balance / Seller As-Is (percentage integer)
const ltvPct = computed<number | null>(() => {
  const upb = Number(props.row?.current_balance)
  const asis = Number(props.row?.seller_asis_value ?? props.row?.seller_as_is)
  if (!Number.isFinite(upb) || !Number.isFinite(asis) || asis === 0) return null
  return (upb / asis) * 100
})
const ltvIntStr = computed<string>(() => {
  if (ltvPct.value === null) return '—'
  return `${Math.round(ltvPct.value)}%`
})
const ltvColorClass = computed<string>(() => {
  const v = ltvPct.value
  if (v === null) return 'text-warning text-opacity-75'
  if (v > 100) return 'text-danger'
  if (v >= 90) return 'text-warning'
  return 'text-success'
})

// TDTV helpers: Total Debt / Seller As-Is (percentage integer)
// - Mirrors the LTV computations above but uses total_debt as the numerator.
// - We guard against NaN and division by zero to keep UI resilient.
const tdtvPct = computed<number | null>(() => {
  const td = Number(props.row?.total_debt) // numerator: total debt
  const asis = Number(props.row?.seller_asis_value ?? props.row?.seller_as_is) // denominator: seller as-is value
  if (!Number.isFinite(td) || !Number.isFinite(asis) || asis === 0) return null
  return (td / asis) * 100
})
// Present TDTV as an integer percentage like "95%"; em-dash when not computable
const tdtvIntStr = computed<string>(() => {
  if (tdtvPct.value === null) return '—'
  return `${Math.round(tdtvPct.value)}%`
})
// Apply same color thresholds as LTV for visual consistency
const tdtvColorClass = computed<string>(() => {
  const v = tdtvPct.value
  if (v === null) return 'text-warning text-opacity-75'
  if (v > 100) return 'text-danger'
  if (v >= 90) return 'text-warning'
  return 'text-success'
})
const nextDueStr = computed<string>(() => {
  const v = props.row?.next_due_date
  if (!v) return '—'
  try { return new Date(v).toLocaleDateString('en-US') } catch { return '—' }
})
</script>

<style scoped>
/* Normalize the vertical space of the value row across all KPI cards so card
   height stays consistent regardless of content like badges or suffixes. */
.widget-flat {
  min-height: 96px; /* slightly condensed overall card height */
}
:deep(.widget-flat .card-body) {
  min-height: 72px; /* allow content to condense */
  display: flex;
  flex-direction: column;
  justify-content: flex-start; /* avoid large gap between title and value */
  position: relative; /* allow absolute-positioning of the icon wrapper */
  padding-top: 0.25rem;
  padding-bottom: 0.25rem;
}
.widget-flat .card-body .mt-3.mb-1 {
  min-height: 1.75rem; /* tighter value row */
  display: flex;
  align-items: baseline;
  line-height: 1;           /* remove extra whitespace from larger fonts */
  white-space: nowrap;      /* keep value + suffix on one line */
  margin-top: 0.25rem;      /* reduce gap from title */
  margin-bottom: 0;         /* remove bottom gap */
}
.value-row span { white-space: nowrap; }
/* Ensure our custom value-row follows the condensed spacing too */
.value-row {
  margin-top: 0.25rem;
  margin-bottom: 0;
}

/* Pin the icon wrapper to the top-right so flex/float do not shift it */
:deep(.widget-flat .card-body > .float-end) {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  margin: 0 !important;
  z-index: 2;
  pointer-events: none;
}
:deep(.widget-flat .card-body .float-end .widget-icon) {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  left: auto !important;
}
/* Also ensure the utility-based absolute wrapper we used on custom cards behaves the same */
:deep(.widget-flat .card-body .position-absolute.top-0.end-0) {
  z-index: 2;
  pointer-events: none;
}
</style>
