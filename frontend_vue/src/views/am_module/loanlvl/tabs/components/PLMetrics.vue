<template>
  <!-- WHAT: Reusable P&L Metrics component with 3-column grid comparing Underwritten vs Realized -->
  <!-- WHY: Modular component for performance metrics that can be imported anywhere -->
  <!-- HOW: Clean grid layout with Purchase Cost, Acq Costs, Gross Cost, Expenses, Income, Proceeds -->
  <!-- WHERE: Used in PerformanceTab.vue (frontend_vue/src/views/am_module/loanlvl/tabs/PerformanceTab.vue) -->
  <div>
    <!-- 3-Column Grid Layout: Headers | Underwritten | Realized -->
    <div class="table-responsive">
      <table class="table table-bordered align-middle mb-0 performance-grid">
        <!-- Header Row -->
        <thead class="table-light">
          <tr>
            <th scope="col" class="metric-header">Metric</th>
            <th scope="col" class="text-center underwritten-col">Underwritten</th>
            <th scope="col" class="text-center realized-col">Realized</th>
          </tr>
        </thead>
        <tbody>
          <!-- Purchase Cost -->
          <tr>
            <td class="fw-semibold ps-3">Purchase Cost</td>
            <td class="text-end underwritten-col">{{ fmtCurrency(metrics.purchaseCost.underwritten) }}</td>
            <td class="text-end realized-col">{{ fmtCurrency(metrics.purchaseCost.realized) }}</td>
          </tr>

          <!-- Acq Costs -->
          <tr>
            <td class="fw-semibold ps-3">Acq Costs</td>
            <td class="text-end underwritten-col">{{ fmtCurrency(metrics.acqCosts.underwritten) }}</td>
            <td class="text-end realized-col">{{ fmtCurrency(metrics.acqCosts.realized) }}</td>
          </tr>

          <!-- Gross Cost (calculated) -->
          <tr class="table-secondary">
            <td class="fw-bold ps-3">Gross Cost</td>
            <td class="text-end fw-bold underwritten-col">{{ fmtCurrency(grossCost.underwritten) }}</td>
            <td class="text-end fw-bold realized-col">{{ fmtCurrency(grossCost.realized) }}</td>
          </tr>

          <!-- Spacer -->
          <tr class="spacer-row">
            <td colspan="3"></td>
          </tr>

          <!-- Expenses -->
          <tr>
            <td class="fw-semibold ps-3">Expenses</td>
            <td class="text-end underwritten-col">{{ fmtCurrency(metrics.expenses.underwritten) }}</td>
            <td class="text-end realized-col">{{ fmtCurrency(metrics.expenses.realized) }}</td>
          </tr>

          <!-- Income -->
          <tr>
            <td class="fw-semibold ps-3">Income</td>
            <td class="text-end underwritten-col">{{ fmtCurrency(metrics.income.underwritten) }}</td>
            <td class="text-end realized-col">{{ fmtCurrency(metrics.income.realized) }}</td>
          </tr>

          <!-- Proceeds -->
          <tr>
            <td class="fw-semibold ps-3">Proceeds</td>
            <td class="text-end underwritten-col">{{ fmtCurrency(metrics.proceeds.underwritten) }}</td>
            <td class="text-end realized-col">{{ fmtCurrency(metrics.proceeds.realized) }}</td>
          </tr>

          <!-- Spacer -->
          <tr class="spacer-row">
            <td colspan="3"></td>
          </tr>

          <!-- Net P&L (calculated) -->
          <tr class="table-success">
            <td class="fw-bold ps-3">Net P&L</td>
            <td class="text-end fw-bold underwritten-col">{{ fmtCurrency(netPL.underwritten) }}</td>
            <td class="text-end fw-bold realized-col">{{ fmtCurrency(netPL.realized) }}</td>
          </tr>

          <!-- Variance (Realized vs Underwritten) -->
          <tr class="table-info">
            <td class="fw-bold ps-3">Variance</td>
            <td class="text-center text-muted small">—</td>
            <td class="text-end fw-bold realized-col" :class="varianceClass">
              {{ fmtCurrency(variance) }}
              <i v-if="variance > 0" class="mdi mdi-arrow-up-circle ms-1"></i>
              <i v-else-if="variance < 0" class="mdi mdi-arrow-down-circle ms-1"></i>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Quick Stats Summary Cards -->
    <div class="row g-2 mt-3">
      <div class="col-md-4">
        <div class="p-2 rounded bg-light border">
          <div class="small text-muted">ROI (Underwritten)</div>
          <div class="fs-5 fw-semibold">{{ roiUnderwritten }}%</div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="p-2 rounded bg-light border">
          <div class="small text-muted">ROI (Realized)</div>
          <div class="fs-5 fw-semibold">{{ roiRealized }}%</div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="p-2 rounded bg-light border">
          <div class="small text-muted">Variance</div>
          <div class="fs-5 fw-semibold" :class="varianceClass">{{ variancePercent }}%</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// WHAT: Reusable P&L metrics component with Underwritten vs Realized comparison
// WHY: Modular component for easy reuse across different views
// HOW: Reactive data structure with computed totals, variance, and ROI calculations
// NOTE: Placeholder data - wire to backend API later (AcqModel for underwritten, TBD for realized)
import { withDefaults, defineProps, reactive, computed } from 'vue'

// WHAT: Props interface for component
// WHY: Accept row data from parent to load metrics
// HOW: Optional row and productId props
withDefaults(defineProps<{ 
  row?: Record<string, any> | null
  productId?: string | number | null 
}>(), {
  row: null,
  productId: null,
})

// WHAT: Main metrics object with underwritten vs realized values
// WHY: Separate columns for comparison; each metric has two values
// HOW: Replace with API data from backend (AcqModel for underwritten, TBD for realized)
const metrics = reactive({
  // Purchase Cost (actual purchase price)
  purchaseCost: {
    underwritten: 0,
    realized: 0,
  },
  // Acq Costs (closing costs, fees, etc.)
  acqCosts: {
    underwritten: 0,
    realized: 0,
  },
  // Expenses (holding costs, rehab, etc.)
  expenses: {
    underwritten: 0,
    realized: 0,
  },
  // Income (rental income, etc.)
  income: {
    underwritten: 0,
    realized: 0,
  },
  // Proceeds (sale proceeds)
  proceeds: {
    underwritten: 0,
    realized: 0,
  },
})

// WHAT: Computed Gross Cost = Purchase Cost + Acq Costs
// WHY: Common metric for total acquisition basis
// HOW: Sum both underwritten and realized values
const grossCost = computed(() => ({
  underwritten: metrics.purchaseCost.underwritten + metrics.acqCosts.underwritten,
  realized: metrics.purchaseCost.realized + metrics.acqCosts.realized,
}))

// WHAT: Computed Net P&L = (Income + Proceeds) - (Gross Cost + Expenses)
// WHY: Final bottom-line profit/loss metric
// HOW: Calculate for both underwritten and realized scenarios
const netPL = computed(() => ({
  underwritten: (metrics.income.underwritten + metrics.proceeds.underwritten) 
                - (grossCost.value.underwritten + metrics.expenses.underwritten),
  realized: (metrics.income.realized + metrics.proceeds.realized) 
            - (grossCost.value.realized + metrics.expenses.realized),
}))

// WHAT: Variance = Realized Net P&L - Underwritten Net P&L
// WHY: Shows how much better/worse we did vs projection
// HOW: Subtract underwritten from realized Net P&L
const variance = computed(() => netPL.value.realized - netPL.value.underwritten)

// WHAT: Dynamic CSS class for variance (green if positive, red if negative)
// WHY: Visual indicator of performance vs underwriting
// HOW: Return Bootstrap text color classes based on variance sign
const varianceClass = computed(() => {
  if (variance.value > 0) return 'text-success'
  if (variance.value < 0) return 'text-danger'
  return ''
})

// WHAT: ROI calculations (Net P&L / Gross Cost * 100)
// WHY: Standard return on investment metric in percentage
// HOW: Divide Net P&L by Gross Cost, multiply by 100, format to 1 decimal
const roiUnderwritten = computed(() => {
  if (grossCost.value.underwritten === 0) return 0
  return ((netPL.value.underwritten / grossCost.value.underwritten) * 100).toFixed(1)
})

const roiRealized = computed(() => {
  if (grossCost.value.realized === 0) return 0
  return ((netPL.value.realized / grossCost.value.realized) * 100).toFixed(1)
})

// WHAT: Variance as percentage relative to underwritten
// WHY: Relative variance is more meaningful than absolute dollar amount
// HOW: Divide variance by absolute underwritten Net P&L, multiply by 100
const variancePercent = computed(() => {
  if (netPL.value.underwritten === 0) return 0
  return ((variance.value / Math.abs(netPL.value.underwritten)) * 100).toFixed(1)
})

// WHAT: Currency formatter helper function
// WHY: Consistent USD formatting across all currency fields
// HOW: Uses Intl.NumberFormat with USD currency and no decimals
function fmtCurrency(v: number | null | undefined): string {
  const n = Number(v || 0)
  return new Intl.NumberFormat(undefined, { 
    style: 'currency', 
    currency: 'USD', 
    maximumFractionDigits: 0 
  }).format(n)
}
</script>

<style scoped>
/* WHAT: Custom styles for 3-column performance grid */
/* WHY: Make the grid easy to scan with clear visual hierarchy */
/* HOW: Column colors, spacing, and hover effects per Hyper UI patterns */

/* Table cell padding */
.performance-grid > :not(caption) > * > * { 
  padding: .625rem 1rem; 
}

/* Metric header column styling */
.metric-header {
  min-width: 180px;
  font-weight: 600;
}

/* Underwritten column styling - subtle blue tint */
.underwritten-col {
  background-color: #f0f7ff;
  min-width: 140px;
  font-weight: 500;
}

/* Realized column styling - subtle green tint */
.realized-col {
  background-color: #f0fdf4;
  min-width: 140px;
  font-weight: 500;
}

/* Spacer rows for visual separation */
.spacer-row {
  height: 8px;
  background: transparent;
}

.spacer-row td {
  border: none !important;
  padding: 4px !important;
}

/* Hover effect for data rows */
.performance-grid tbody tr:not(.spacer-row):hover {
  background-color: rgba(0, 0, 0, 0.02);
}

/* Calculated totals get extra emphasis */
.table-secondary td,
.table-success td,
.table-info td {
  font-size: 0.95rem;
}

/* Bordered table for clear grid structure */
.table-bordered th,
.table-bordered td {
  border-color: #dee2e6;
}
</style>
