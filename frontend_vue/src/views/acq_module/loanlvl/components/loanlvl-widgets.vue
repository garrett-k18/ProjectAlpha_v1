<template>
  <!-- Loan-level snapshot KPIs: modular widget row -->
  <!-- Row 1: 6 widgets across on lg (12/6=2) -->
  <b-row class="g-1 mb-1">
    <!-- Property Address (top-left) -->
    <b-col lg="2" md="4" sm="6">
      <WidgetStatIcon
        icon="mdi-home-map-marker"
        title="Property Address"
        :number="addressStr"
        color="secondary"
        subtext=""
        :showFooter="false"
        :dense="true"
        titleClass="small"
        numberClass="fs-5"
        :iconSizePx="14"
        :iconBoxPx="24"
      />
    </b-col>
    <b-col lg="2" md="4" sm="6">
      <WidgetStatIcon
        icon="mdi-cash-multiple"
        title="Current Balance"
        :number="currentBalanceStr"
        color="success"
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
    <b-col lg="2" md="4" sm="6">
      <WidgetStatIcon
        icon="mdi-flag"
        title="Asset Status"
        :number="assetStatusStr"
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
    <!-- keep first row at 6 items; Original Balance moved to second row -->
  </b-row>

  <!-- Row 2: additional condensed widgets -->
  <b-row class="g-1 mb-2">
    <b-col lg="2" md="4" sm="6">
      <WidgetStatIcon
        icon="mdi-cash"
        title="Original Balance"
        :number="originalBalanceStr"
        color="primary"
        subtext=""
        :showFooter="false"
        :dense="true"
        titleClass="small"
        numberClass="fs-5"
        :iconSizePx="14"
        :iconBoxPx="24"
      />
    </b-col>
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
        numberClass="fs-5"
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
        numberClass="fs-5"
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
const addressStr = computed<string>(() => {
  const addr = props.row?.street_address
  const city = props.row?.city
  const state = props.row?.state
  const zip = props.row?.zip
  const parts = [addr, city, state, zip].filter(Boolean)
  return parts.length ? String(parts.join(', ')) : '—'
})
const originalBalanceStr = computed<string>(() => fmtInt(props.row?.original_balance))
const sellerAsIsStr = computed<string>(() => fmtInt(props.row?.seller_asis_value ?? props.row?.seller_as_is))
const sellerArvStr = computed<string>(() => fmtInt(props.row?.seller_arv_value ?? props.row?.seller_arv))
const assetStatusStr = computed<string>(() => (props.row?.asset_status ? String(props.row.asset_status) : '—'))
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
/* Loan-level KPI widgets — manual height tuning only for this component.
   We use :deep to reach the child WidgetStatIcon markup (.widget-flat), while
   keeping changes scoped so dashboard tiles remain unaffected. */

/* Outer card height envelope (soft constraint) */
:deep(.widget-flat) {
  min-height: 128px; /* adjust to taste: 120–136px range works well */
}

/* Inner white area height and layout */
:deep(.widget-flat .card-body) {
  min-height: 72px;          /* allow inner to condense */
  display: flex;
  flex-direction: column;    /* stack title then value line */
  justify-content: flex-start; /* avoid big gaps between title/value */
  padding-top: 0.25rem;      /* tighter vertical padding */
  padding-bottom: 0.25rem;
  position: relative;        /* allow absolute-positioning of the icon */
}

/* Title spacing (h5) */
:deep(.widget-flat .card-body h5.text-muted.fw-normal.mt-0) {
  margin-bottom: 0.125rem;   /* tighter gap before value line */
}

/* Value line (h3) sizing so numbers/pills align without affecting height */
:deep(.widget-flat .card-body h3.mt-3) {
  line-height: 1;            /* avoid extra whitespace */
  margin-top: 0.25rem;       /* tighter spacing from title */
  margin-bottom: 0rem;       /* remove extra bottom gap */
  white-space: nowrap;       /* prevent wrapping that changes height */
}

/* Pin the widget icon to the top-right consistently (float ignored in flex) */
:deep(.widget-flat .card-body > .float-end) {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  margin: 0 !important;
}
/* Also pin the icon itself in case the wrapper gets affected by floats/utilities */
:deep(.widget-flat .card-body .float-end .widget-icon) {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  left: auto !important;
}
</style>
