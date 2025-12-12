<template>
  <!--
    WHAT: Pooled Cash Flow Series component (wrapper for shared component)
    WHY: Fetch and format pooled/aggregated cash flow data for modeling center
    WHERE: Used in ModelingCenter.vue to show pool-level cash flows
    HOW: Fetches aggregated data from API, transforms to shared component format
  -->
  <CashFlowSeriesTable
    title="Pool Cash Flows"
    dateLabel="Date"
    :periods="periods"
    :periodLabels="periodLabels"
    :periodDates="periodDates"
    :netCashFlowArray="netCashFlowArray"
    :totalInflowsArray="totalInflowsArray"
    :totalOutflowsArray="totalOutflowsArray"
    :inflowLineItems="inflowLineItems"
    :outflowLineItems="outflowLineItems"
    :cumulativeCashFlowArray="cumulativeCashFlowArray"
    :showCumulative="true"
    :highlightPeriod="null"
    :jumpToPeriod="null"
    :showScenarioToggle="false"
    :initialScenario="scenario"
    :showTimelineSummary="false"
    :loading="loading"
    :error="error"
  />
</template>

<script setup lang="ts">
/**
 * WHAT: Pooled Cash Flow Series wrapper component
 * WHY: Fetch and format pooled cash flow data for the shared table component
 * HOW: API fetch → data transformation → pass to CashFlowSeriesTable
 */
import { ref, computed, watch, onMounted } from 'vue'
import http from '@/lib/http'
import CashFlowSeriesTable from '@/components/shared/CashFlowSeriesTable.vue'

// WHAT: Component props
const props = defineProps<{
  sellerId: string | number | null
  tradeId: string | number | null
  modelType?: 'reo_sale' | 'fc_sale'
  initialScenario?: 'as_is' | 'arv'
}>()

// WHAT: Component state
const loading = ref(false)
const error = ref<string | null>(null)
const cashFlowData = ref<any>(null)
const scenario = ref<'as_is' | 'arv'>(props.initialScenario || 'as_is')

// WHAT: Periods array
const periods = computed(() => cashFlowData.value?.periods || [])

// WHAT: Period labels (just numbers: 0, 1, 2, ...)
const periodLabels = computed(() => {
  if (!cashFlowData.value) return []
  return cashFlowData.value.periods.map((p: number) => p.toString())
})

// WHAT: Period dates (MM/YYYY format from backend)
const periodDates = computed(() => cashFlowData.value?.period_dates || [])

// WHAT: Final period (for highlighting)
const finalPeriod = computed(() => {
  if (!periods.value.length) return null
  return periods.value[periods.value.length - 1]
})

// WHAT: Cash flow arrays
const netCashFlowArray = computed(() => cashFlowData.value?.cash_flows?.net_cash_flow || [])
const cumulativeCashFlowArray = computed(() => cashFlowData.value?.cumulative_cash_flow || [])

// WHAT: Total inflows array
const totalInflowsArray = computed(() => {
  if (!cashFlowData.value) return []
  const proceeds = cashFlowData.value.cash_flows.proceeds || []
  return proceeds
})

// WHAT: Total outflows array
const totalOutflowsArray = computed(() => {
  if (!cashFlowData.value) return []
  const flows = cashFlowData.value.cash_flows
  
  // WHAT: Sum all outflow categories per period
  return periods.value.map((_: number, index: number) => {
    const total = 
      (flows.acquisition_price?.[index] || 0) +
      (flows.acq_costs?.[index] || 0) +
      (flows.servicing_fees?.[index] || 0) +
      (flows.taxes?.[index] || 0) +
      (flows.insurance?.[index] || 0) +
      (flows.legal_cost?.[index] || 0) +
      (flows.reo_holding_costs?.[index] || 0) +
      (flows.trashout_cost?.[index] || 0) +
      (flows.renovation_cost?.[index] || 0) +
      (flows.liquidation_fees?.[index] || 0)
    return total
  })
})

// WHAT: Inflow line items (just proceeds for now)
const inflowLineItems = computed(() => {
  if (!cashFlowData.value) return []
  return [
    {
      key: 'proceeds',
      label: 'Sale Proceeds',
      values: cashFlowData.value.cash_flows.proceeds || []
    }
  ]
})

// WHAT: Outflow line items (all expense categories)
const outflowLineItems = computed(() => {
  if (!cashFlowData.value) return []
  const flows = cashFlowData.value.cash_flows
  
  return [
    { key: 'acquisition_price', label: 'Acquisition Price', values: flows.acquisition_price || [] },
    { key: 'acq_costs', label: 'Acq Costs', values: flows.acq_costs || [] },
    { key: 'servicing_fees', label: 'Servicing Fees', values: flows.servicing_fees || [] },
    { key: 'taxes', label: 'Property Taxes', values: flows.taxes || [] },
    { key: 'insurance', label: 'Property Insurance', values: flows.insurance || [] },
    { key: 'legal_cost', label: 'Legal Costs', values: flows.legal_cost || [] },
    { key: 'reo_holding_costs', label: 'REO Holding Costs', values: flows.reo_holding_costs || [] },
    { key: 'trashout_cost', label: 'Trashout Cost', values: flows.trashout_cost || [] },
    { key: 'renovation_cost', label: 'Renovation Cost', values: flows.renovation_cost || [] },
    { key: 'liquidation_fees', label: 'Liquidation Fees', values: flows.liquidation_fees || [] },
  ]
})

// WHAT: Fetch pooled cash flow data from API
async function fetchCashFlowData() {
  if (!props.sellerId || !props.tradeId) {
    error.value = 'Seller ID and Trade ID are required'
    return
  }

  loading.value = true
  error.value = null

  try {
    // WHAT: Increased timeout for bulk cash flow calculation
    // WHY: Pooled cash flows require calculating cash flows for all assets, which can take time
    const response = await http.get(`/acq/modeling-center/${props.sellerId}/${props.tradeId}/pooled-cashflows/`, {
      params: {
        scenario: scenario.value,
        model_type: props.modelType || 'reo_sale'
      },
      timeout: 60000 // WHAT: 60 second timeout for bulk calculations
    })
    
    cashFlowData.value = response.data
    console.log('[PooledCashFlowSeries] Loaded pooled cash flow data:', response.data)
  } catch (e: any) {
    console.error('[PooledCashFlowSeries] Failed to fetch pooled cash flow data:', e)
    error.value = e?.response?.data?.detail || e?.message || 'Failed to load pooled cash flow data'
    cashFlowData.value = null
  } finally {
    loading.value = false
  }
}

// WHAT: Watch for seller/trade ID changes
watch([() => props.sellerId, () => props.tradeId], ([newSellerId, newTradeId]) => {
  if (newSellerId && newTradeId) {
    fetchCashFlowData()
  }
}, { immediate: true })

// WHAT: Watch for scenario prop changes
watch(() => props.initialScenario, (newScenario) => {
  if (newScenario) {
    scenario.value = newScenario
    if (props.sellerId && props.tradeId) {
      fetchCashFlowData()
    }
  }
}, { immediate: false })

// WHAT: Watch for model type changes
watch(() => props.modelType, () => {
  if (props.sellerId && props.tradeId) {
    fetchCashFlowData()
  }
})

// WHAT: Initial data fetch on mount
onMounted(() => {
  if (props.sellerId && props.tradeId) {
    fetchCashFlowData()
  }
})
</script>

<style scoped>
/* Component-specific styles can go here if needed */
</style>
