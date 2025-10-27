<template>
  <!-- 
    WHAT: Performance stat widgets using Hyper UI template style
    WHY: Display key cash flow metrics at top of Performance tab
    WHERE: Used in PerformanceTab.vue above Performance Summary table
    STYLE: Matches widget-stat-icon.vue from Hyper UI template
  -->
  <b-row class="mb-4">
    <b-col sm="6" md="3" v-for="widget in widgetsData" :key="widget.title">
      <StatIcon
        :icon="widget.icon"
        :title="widget.title"
        :number="widget.number"
        :subtext="widget.subtext"
        :color="widget.color"
        :showFooter="false"
      />
    </b-col>
  </b-row>
</template>

<script setup lang="ts">
/**
 * WHAT: Performance widgets component for cash flow metrics
 * WHY: Reusable stat cards matching Hyper UI template design
 * HOW: Uses StatIcon component from @/components/widgets/widget-stat-icon.vue
 * WHERE: Displayed at top of PerformanceTab.vue
 */
import { ref, computed, onMounted, watch } from 'vue'
import StatIcon from '@/components/widgets/widget-stat-icon.vue'
import axios from 'axios'

const props = withDefaults(defineProps<{
  assetHubId?: string | number | null
}>(), {
  assetHubId: null
})

// WHAT: Raw data from API
const periods = ref<any[]>([])
const purchaseDate = ref<string | null>(null)

// WHAT: Calculate total inflows across all periods
const totalInflows = computed(() => {
  return periods.value.reduce((sum, p) => sum + (p.total_income || 0), 0)
})

// WHAT: Calculate total outflows across all periods
const totalOutflows = computed(() => {
  return periods.value.reduce((sum, p) => sum + (p.total_expenses || 0), 0)
})

// WHAT: Calculate net cash flow total across all periods
const netCashFlowTotal = computed(() => {
  return periods.value.reduce((sum, p) => sum + (p.net_cash_flow || 0), 0)
})

// WHAT: Format currency
function fmtCurrency(n: number | null | undefined): string {
  if (n == null) return '$0'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(n)
}

// WHAT: Widget data array matching Hyper UI template format
// WHY: StatIcon component expects this structure
const widgetsData = computed(() => [
  {
    icon: 'mdi-percent',
    number: fmtCurrency(totalInflows.value),
    title: 'IRR',
    color: 'success',
    subtext: '',
  },
  {
    icon: 'mdi-cash-multiple',
    number: fmtCurrency(totalOutflows.value),
    title: 'NPV',
    color: 'primary',
    subtext: '',
  },
  {
    icon: 'mdi-chart-line',
    number: fmtCurrency(netCashFlowTotal.value),
    title: 'Net Cash Flow',
    color: netCashFlowTotal.value >= 0 ? 'success' : 'danger',
    subtext: '',
  },
  {
    icon: 'mdi-calendar-range',
    number: periods.value.length.toString(),
    title: 'Total Periods',
    color: 'primary',
    subtext: '',
  },
])

// WHAT: Fetch cash flow data from API
// WHY: Need period data to calculate totals
async function fetchCashFlowData() {
  if (!props.assetHubId) return
  
  try {
    const response = await axios.get(`/api/am/cash-flow-series/${props.assetHubId}/`)
    if (response.data) {
      periods.value = response.data.periods || []
      purchaseDate.value = response.data.purchase_date || null
    }
  } catch (err) {
    console.error('Failed to load cash flow data for widgets:', err)
  }
}

// WHAT: Fetch data on mount if assetHubId is available
// WHY: Prevent unnecessary API calls when component loads without context
onMounted(() => {
  if (props.assetHubId) {
    fetchCashFlowData()
  }
})

// WHAT: Watch for assetHubId changes
// WHY: Refetch when user navigates to different asset
watch(() => props.assetHubId, (newId) => {
  if (newId) {
    fetchCashFlowData()
  }
})
</script>
