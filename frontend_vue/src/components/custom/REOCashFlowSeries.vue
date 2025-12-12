<template>
  <!--
    WHAT: REO Cash Flow Series component (wrapper for shared component)
    WHY: Fetch and format REO-specific cash flow data for display
    WHERE: Used in REOSaleModelCard.vue and other REO modeling views
    HOW: Fetches data from API, transforms to shared component format, handles scenario toggle
  -->
  <CashFlowSeriesTable
    title="Cash Flows"
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
    :highlightPeriod="finalPeriod"
    :jumpToPeriod="finalPeriod"
    jumpButtonLabel="Jump to Sale"
    :showScenarioToggle="false"
    :initialScenario="scenario"
    :showTimelineSummary="false"
    :loading="loading"
    :error="error"
    @scenario-changed="handleScenarioChange"
  />
</template>

<script setup lang="ts">
/**
 * WHAT: REO Cash Flow Series wrapper component
 * WHY: Fetch and format REO cash flow data for the shared table component
 * HOW: API fetch → data transformation → pass to CashFlowSeriesTable
 */
import { ref, computed, watch, onMounted } from 'vue'
import http from '@/lib/http'
import CashFlowSeriesTable from '@/components/shared/CashFlowSeriesTable.vue'

// WHAT: Component props
const props = defineProps<{
  assetId: string | number | null
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

// WHAT: Fetch cash flow data from API
async function fetchCashFlowData() {
  if (!props.assetId) {
    error.value = 'Asset ID is required'
    return
  }

  loading.value = true
  error.value = null

  try {
    const response = await http.get(`/acq/assets/${props.assetId}/reo-cashflow-series/`, {
      params: {
        scenario: scenario.value
      }
    })
    
    cashFlowData.value = response.data
    console.log('[REOCashFlowSeries] Loaded cash flow data:', response.data)
  } catch (e: any) {
    console.error('[REOCashFlowSeries] Failed to fetch cash flow data:', e)
    error.value = e?.response?.data?.detail || e?.message || 'Failed to load cash flow data'
    cashFlowData.value = null
  } finally {
    loading.value = false
  }
}

// WHAT: Handle scenario change
function handleScenarioChange(newScenario: 'as_is' | 'arv') {
  scenario.value = newScenario
  fetchCashFlowData()
}

// WHAT: Watch for asset ID changes
watch(() => props.assetId, (newId) => {
  if (newId) {
    fetchCashFlowData()
  }
}, { immediate: true })

// WHAT: Watch for initial scenario prop changes
watch(() => props.initialScenario, (newScenario) => {
  if (newScenario) {
    scenario.value = newScenario
    fetchCashFlowData()
  }
})

// WHAT: Initial data fetch on mount
onMounted(() => {
  if (props.assetId) {
    fetchCashFlowData()
  }
})
</script>

<style scoped>
/* Component-specific styles can go here if needed */
</style>
