<template>
  <!--
    InvestmentMetrics.vue
    - Displays key investment performance metrics
    - Shows Cap Rate, Cash on Cash, ROI, and Break Even period
    - Includes estimated rent, tax, and insurance breakdown
    - Uses Bootstrap/Hyper UI card pattern
  -->
  <div class="card">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title mb-0">Investment Metrics</h4>
      <i class="mdi mdi-calculator text-muted"></i>
    </div>
    <div class="card-body">
      <div class="row g-2">
        <div class="col-6" v-for="(metric, idx) in investmentMetrics" :key="idx">
          <div class="border rounded p-2 text-center">
            <i :class="`mdi ${metric.icon} text-${metric.color} fs-3 mb-1`"></i>
            <h6 class="mb-0 text-muted small">{{ metric.label }}</h6>
            <h4 class="mb-0 mt-1" :class="`text-${metric.color}`">{{ metric.value }}</h4>
          </div>
        </div>
      </div>
      <div class="mt-3 pt-3 border-top">
        <div class="d-flex justify-content-between mb-2">
          <span class="text-muted">Estimated Monthly Rent</span>
          <span class="fw-semibold">{{ formatCurrency(estimatedRent) }}</span>
        </div>
        <div class="d-flex justify-content-between mb-2">
          <span class="text-muted">Annual Property Tax</span>
          <span class="fw-semibold">{{ formatCurrency(annualTax) }}</span>
        </div>
        <div class="d-flex justify-content-between">
          <span class="text-muted">Insurance (Est.)</span>
          <span class="fw-semibold">{{ formatCurrency(annualInsurance) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * InvestmentMetrics.vue
 * 
 * Displays key investment performance metrics for property analysis.
 * Shows ROI, cap rate, cash-on-cash return, and operating expenses.
 * TODO: Wire to backend financial modeling API when available.
 */
import { ref, withDefaults } from 'vue'

// Props definition
const props = withDefaults(defineProps<{
  row?: Record<string, any> | null
  assetId?: string | number | null
}>(), {
  row: null,
  assetId: null,
})

// Investment Metrics - Key financial indicators
const investmentMetrics = ref([
  { label: 'Cap Rate', value: '7.2%', icon: 'mdi-percent-outline', color: 'success' },
  { label: 'Cash on Cash', value: '9.5%', icon: 'mdi-cash-fast', color: 'primary' },
  { label: 'ROI', value: '12.3%', icon: 'mdi-trending-up', color: 'success' },
  { label: 'Break Even', value: '6.2 yrs', icon: 'mdi-clock-outline', color: 'info' }
])

const estimatedRent = ref(1850)
const annualTax = ref(6708)
const annualInsurance = ref(1200)

// Formatting helper for currency
function formatCurrency(value: number | null | undefined): string {
  if (value == null) return '—'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value)
}
</script>
