<template>
  <!-- Loan-level snapshot KPIs: modular widget row -->
  <!-- Row 1: 6 widgets across on lg (12/6=2) -->
  <b-row class="g-1 mb-1">
    <b-col lg="2" md="4" sm="6">
      <!-- Custom card to allow badge styling like AG Grid's categorical pills -->
      <div class="card widget-flat">
        <div class="card-body py-2 px-3">
          <div class="float-end">
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
        <div class="card-body py-2 px-3">
          <div class="float-end">
            <i class="mdi mdi-cash-multiple widget-icon" :style="{ fontSize: '14px', height: '24px', width: '24px', lineHeight: '24px' }"></i>
          </div>
          <h5 class="text-muted fw-normal mt-0 small" title="Current Balance">Current Balance</h5>
          <div class="value-row d-flex align-items-baseline">
            <span class="fs-4 fw-semibold">{{ currentBalanceStr }}</span>
            <span class="text-muted d-inline-flex align-items-baseline ms-2 fs-5 fst-italic">
              <span :class="['me-1', ltvColorClass]">{{ ltvIntStr }}</span>
              <span class="text-nowrap">LTV</span>
            </span>
          </div>
        </div>
      </div>
    </b-col>
    <b-col lg="2" md="4" sm="6">
      <WidgetStatIcon
        icon="mdi-finance"
        title="Total Debt"
        :number="totalDebtStr"
        color="danger"
        subtext=""
        :showFooter="false"
        :dense="true"
        titleClass="small"
        numberClass="fs-4"
        :iconSizePx="14"
        :iconBoxPx="24"
      />
    </b-col>
    <b-col lg="2" md="4" sm="6">
      <WidgetStatIcon
        icon="mdi-percent"
        title="Interest Rate"
        :number="interestRateStr"
        color="info"
        subtext=""
        :showFooter="false"
        :dense="true"
        titleClass="small"
        numberClass="fs-4"
        :iconSizePx="14"
        :iconBoxPx="24"
      />
    </b-col>
    <b-col lg="2" md="4" sm="6">
      <WidgetStatIcon
        icon="mdi-calendar-clock"
        title="Months DLQ"
        :number="monthsDlqStr"
        color="warning"
        subtext=""
        :showFooter="false"
        :dense="true"
        titleClass="small"
        numberClass="fs-4"
        :iconSizePx="14"
        :iconBoxPx="24"
      />
    </b-col>
    
  </b-row>

  <!-- Row 2: additional condensed widgets -->
  <b-row class="g-1 mb-2">
    <b-col lg="2" md="4" sm="6">
      <WidgetStatIcon
        icon="mdi-calendar"
        title="Next Due"
        :number="nextDueStr"
        color="secondary"
        subtext=""
        :showFooter="false"
        :dense="true"
        titleClass="small"
        numberClass="fs-4"
        :iconSizePx="14"
        :iconBoxPx="24"
      />
    </b-col>
    <b-col lg="2" md="4" sm="6">
      <WidgetStatIcon
        icon="mdi-calendar-check"
        title="Maturity"
        :number="maturityStr"
        color="secondary"
        subtext=""
        :showFooter="false"
        :dense="true"
        titleClass="small"
        numberClass="fs-4"
        :iconSizePx="14"
        :iconBoxPx="24"
      />
    </b-col>
    <!-- Keep layout flexible: leftover cols stay empty on lg -->
  </b-row>
</template>

<script setup lang="ts">
// loanlvl-widgets.vue
// Renders a row of KPI widgets for the loan snapshot context.
// Props: row (partial SellerRawData)

import { computed, withDefaults, defineProps } from 'vue'
import WidgetStatIcon from '@/components/widgets/widget-stat-icon.vue'

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

// Additional fields for more widgets
const sellerAsIsStr = computed<string>(() => fmtInt(props.row?.seller_asis_value ?? props.row?.seller_as_is))
const sellerArvStr = computed<string>(() => fmtInt(props.row?.seller_arv_value ?? props.row?.seller_arv))
const assetStatusStr = computed<string>(() => (props.row?.asset_status ? String(props.row.asset_status) : '—'))

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
    'Default': { label: 'Default', color: 'bg-danger' },
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
const nextDueStr = computed<string>(() => {
  const v = props.row?.next_due_date
  if (!v) return '—'
  try { return new Date(v).toLocaleDateString('en-US') } catch { return '—' }
})
const maturityStr = computed<string>(() => {
  const v = props.row?.mod_maturity_date ?? props.row?.current_maturity_date ?? props.row?.original_maturity_date
  if (!v) return '—'
  try { return new Date(v).toLocaleDateString('en-US') } catch { return '—' }
})
</script>

<style scoped>
/* Normalize the vertical space of the value row across all KPI cards so card
   height stays consistent regardless of content like badges or suffixes. */
.widget-flat {
  height: 128px; /* unify overall card height */
}
.widget-flat .card-body {
  height: 96px; /* lock inner white area height across all KPI cards */
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.widget-flat .card-body .mt-3.mb-1 {
  height: 2.5rem; /* fixed row height to avoid jitter */
  display: flex;
  align-items: center;      /* match vertical centering across cards */
  line-height: 1;           /* remove extra whitespace from larger fonts */
  white-space: nowrap;      /* keep value + suffix on one line */
}
.value-row span { white-space: nowrap; }
</style>
