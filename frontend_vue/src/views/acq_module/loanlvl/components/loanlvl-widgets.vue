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
