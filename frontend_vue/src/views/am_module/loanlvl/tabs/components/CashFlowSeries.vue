<template>
  <!--
    WHAT: Cash Flow Series time-series grid component
    WHY: Display period-by-period cash flow data for loan-level analysis
    HOW: Horizontal scrolling table with periods as columns, P&L line items as rows
    WHERE: Used in PerformanceTab.vue (frontend_vue/src/views/am_module/loanlvl/tabs/PerformanceTab.vue)
  -->
  <div class="cash-flow-series-container">
    <!-- WHAT: Header with purchase date and period range -->
    <div class="d-flex justify-content-between align-items-center mb-3">
      <div>
        <h5 class="mb-1">Cash Flow Series</h5>
        <small class="text-muted" v-if="purchaseDate">
          Purchase Date: {{ formatDate(purchaseDate) }} | 
          Periods: 0 (Acquisition) - {{ maxPeriod }} ({{ formatDate(currentPeriodDate) }})
        </small>
      </div>
      <div>
        <button class="btn btn-sm btn-outline-secondary" @click="scrollToCurrentPeriod">
          <i class="mdi mdi-calendar-today me-1"></i>
          Jump to Current Period
        </button>
      </div>
    </div>

    <!-- WHAT: Horizontal scrolling table wrapper -->
    <!-- WHY: Allow viewing many periods without overwhelming the page -->
    <div class="table-responsive" ref="tableContainer">
      <table class="table table-sm table-bordered cash-flow-table">
        <thead class="sticky-header">
          <!-- WHAT: Row 1 - Period numbers -->
          <tr class="bg-light">
            <th class="sticky-col line-item-col">Period #</th>
            <th 
              v-for="period in periods" 
              :key="`period-${period.period_number}`"
              :class="{'current-period': period.is_current}"
              class="text-center period-col"
            >
              P{{ period.period_number }}
            </th>
          </tr>
          
          <!-- WHAT: Row 2 - Period dates -->
          <tr class="bg-light">
            <th class="sticky-col line-item-col">Date</th>
            <th 
              v-for="period in periods" 
              :key="`date-${period.period_number}`"
              :class="{'current-period': period.is_current}"
              class="text-center period-col"
            >
              {{ formatDate(period.period_date) }}
            </th>
          </tr>
        </thead>

        <tbody>
          <!-- WHAT: Net Cash Flow (default view - always visible) -->
          <tr class="section-header bg-primary-subtle">
            <td class="sticky-col fw-bold">Net Cash Flow</td>
            <td v-for="period in periods" :key="`net-${period.period_number}`" class="text-end fw-bold">
              {{ fmtCurrency(period.net_cash_flow) }}
            </td>
          </tr>

          <!-- WHAT: Inflows Section (collapsible) -->
          <tr class="section-header bg-success-subtle clickable" @click="toggleSection('inflows')">
            <td class="sticky-col fw-bold">
              <i :class="showInflows ? 'mdi mdi-chevron-down' : 'mdi mdi-chevron-right'" class="me-2"></i>
              Total Inflows
            </td>
            <td v-for="period in periods" :key="`income-${period.period_number}`" class="text-end fw-semibold">
              {{ fmtCurrency(period.total_income) }}
            </td>
          </tr>
          <template v-if="showInflows">
            <tr>
              <td class="sticky-col ps-4 small text-muted">Principal</td>
              <td v-for="period in periods" :key="`principal-${period.period_number}`" class="text-end small">
                {{ fmtCurrency(period.income_principal) }}
              </td>
            </tr>
            <tr>
              <td class="sticky-col ps-4 small text-muted">Interest</td>
              <td v-for="period in periods" :key="`interest-${period.period_number}`" class="text-end small">
                {{ fmtCurrency(period.income_interest) }}
              </td>
            </tr>
            <tr>
              <td class="sticky-col ps-4 small text-muted">Rent</td>
              <td v-for="period in periods" :key="`rent-${period.period_number}`" class="text-end small">
                {{ fmtCurrency(period.income_rent) }}
              </td>
            </tr>
            <tr>
              <td class="sticky-col ps-4 small text-muted">CAM</td>
              <td v-for="period in periods" :key="`cam-${period.period_number}`" class="text-end small">
                {{ fmtCurrency(period.income_cam) }}
              </td>
            </tr>
            <tr>
              <td class="sticky-col ps-4 small text-muted">Mod Down Payment</td>
              <td v-for="period in periods" :key="`mod-${period.period_number}`" class="text-end small">
                {{ fmtCurrency(period.income_mod_down_payment) }}
              </td>
            </tr>
            <tr>
              <td class="sticky-col ps-4 small text-muted">Liquidation Proceeds</td>
              <td v-for="period in periods" :key="`proceeds-${period.period_number}`" class="text-end small">
                {{ fmtCurrency(period.net_liquidation_proceeds) }}
              </td>
            </tr>
          </template>

          <!-- WHAT: Outflows Section (collapsible) -->
          <tr class="section-header bg-danger-subtle clickable" @click="toggleSection('outflows')">
            <td class="sticky-col fw-bold">
              <i :class="showOutflows ? 'mdi mdi-chevron-down' : 'mdi mdi-chevron-right'" class="me-2"></i>
              Total Outflows
            </td>
            <td v-for="period in periods" :key="`expenses-${period.period_number}`" class="text-end fw-semibold">
              {{ fmtCurrency(period.total_expenses) }}
            </td>
          </tr>
          <template v-if="showOutflows">
            <!-- Purchase Cost (Period 0 only) -->
            <tr>
              <td class="sticky-col ps-4 small text-muted">Purchase Price</td>
              <td v-for="period in periods" :key="`purchase-${period.period_number}`" class="text-end small">
                {{ period.period_number === 0 ? fmtCurrency(period.purchase_price) : '-' }}
              </td>
            </tr>
            
            <!-- Acquisition Costs -->
            <tr>
              <td class="sticky-col ps-4 small text-muted">Due Diligence</td>
              <td v-for="period in periods" :key="`dd-${period.period_number}`" class="text-end small">
                {{ fmtCurrency(period.acq_due_diligence_expenses) }}
              </td>
            </tr>
            <tr>
              <td class="sticky-col ps-4 small text-muted">Acq Legal</td>
              <td v-for="period in periods" :key="`acq-legal-${period.period_number}`" class="text-end small">
                {{ fmtCurrency(period.acq_legal_expenses) }}
              </td>
            </tr>
            <tr>
              <td class="sticky-col ps-4 small text-muted">Title</td>
              <td v-for="period in periods" :key="`title-${period.period_number}`" class="text-end small">
                {{ fmtCurrency(period.acq_title_expenses) }}
              </td>
            </tr>
            
            <!-- Operating Expenses -->
            <tr>
              <td class="sticky-col ps-4 small text-muted">Servicing</td>
              <td v-for="period in periods" :key="`servicing-${period.period_number}`" class="text-end small">
                {{ fmtCurrency(period.servicing_expenses) }}
              </td>
            </tr>
            <tr>
              <td class="sticky-col ps-4 small text-muted">AM Fees</td>
              <td v-for="period in periods" :key="`am-${period.period_number}`" class="text-end small">
                {{ fmtCurrency(period.am_fees_expenses) }}
              </td>
            </tr>
            <tr>
              <td class="sticky-col ps-4 small text-muted">Property Tax</td>
              <td v-for="period in periods" :key="`tax-${period.period_number}`" class="text-end small">
                {{ fmtCurrency(period.property_tax_expenses) }}
              </td>
            </tr>
            <tr>
              <td class="sticky-col ps-4 small text-muted">Insurance</td>
              <td v-for="period in periods" :key="`insurance-${period.period_number}`" class="text-end small">
                {{ fmtCurrency(period.property_insurance_expenses) }}
              </td>
            </tr>
            
            <!-- Legal/DIL Costs -->
            <tr>
              <td class="sticky-col ps-4 small text-muted">Foreclosure Legal</td>
              <td v-for="period in periods" :key="`fc-${period.period_number}`" class="text-end small">
                {{ fmtCurrency(period.legal_foreclosure_expenses) }}
              </td>
            </tr>
            <tr>
              <td class="sticky-col ps-4 small text-muted">Bankruptcy Legal</td>
              <td v-for="period in periods" :key="`bk-${period.period_number}`" class="text-end small">
                {{ fmtCurrency(period.legal_bankruptcy_expenses) }}
              </td>
            </tr>
            
            <!-- REO Expenses -->
            <tr>
              <td class="sticky-col ps-4 small text-muted">HOA</td>
              <td v-for="period in periods" :key="`hoa-${period.period_number}`" class="text-end small">
                {{ fmtCurrency(period.reo_hoa_expenses) }}
              </td>
            </tr>
            <tr>
              <td class="sticky-col ps-4 small text-muted">Utilities</td>
              <td v-for="period in periods" :key="`util-${period.period_number}`" class="text-end small">
                {{ fmtCurrency(period.reo_utilities_expenses) }}
              </td>
            </tr>
            <tr>
              <td class="sticky-col ps-4 small text-muted">Renovation</td>
              <td v-for="period in periods" :key="`reno-${period.period_number}`" class="text-end small">
                {{ fmtCurrency(period.reo_renovation_expenses) }}
              </td>
            </tr>
            <tr>
              <td class="sticky-col ps-4 small text-muted">Property Preservation</td>
              <td v-for="period in periods" :key="`pres-${period.period_number}`" class="text-end small">
                {{ fmtCurrency(period.reo_property_preservation_expenses) }}
              </td>
            </tr>
            
            <!-- CRE Expenses -->
            <tr>
              <td class="sticky-col ps-4 small text-muted">Marketing</td>
              <td v-for="period in periods" :key="`mkt-${period.period_number}`" class="text-end small">
                {{ fmtCurrency(period.cre_marketing_expenses) }}
              </td>
            </tr>
            <tr>
              <td class="sticky-col ps-4 small text-muted">Maintenance</td>
              <td v-for="period in periods" :key="`maint-${period.period_number}`" class="text-end small">
                {{ fmtCurrency(period.cre_maintenance_expenses) }}
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>

    <!-- WHAT: Loading/Error states -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading cash flow data...</span>
      </div>
    </div>
    <div v-if="error" class="alert alert-danger">
      <i class="mdi mdi-alert-circle me-2"></i>
      {{ error }}
    </div>
    <div v-if="!loading && periods.length === 0" class="alert alert-info">
      <i class="mdi mdi-information me-2"></i>
      No cash flow data available for this asset. (Asset ID: {{ productId }})
    </div>
    
    <!-- DEBUG: Show period count -->
    <div v-if="!loading && periods.length > 0" class="alert alert-success mt-3">
      <strong>DEBUG:</strong> Loaded {{ periods.length }} periods for asset {{ productId }}
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * WHAT: Cash Flow Series component for time-series P&L display
 * WHY: Show period-by-period cash flows for detailed analysis
 * HOW: Fetch data from API, calculate current period from purchase date, display in scrollable grid
 */
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'

// WHAT: Component props
// WHY: Need asset ID to fetch cash flow data
const props = withDefaults(defineProps<{
  productId?: string | number | null
}>(), {
  productId: null
})

// WHAT: Reactive state
const periods = ref<any[]>([])
const purchaseDate = ref<string | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const tableContainer = ref<HTMLElement | null>(null)
const showInflows = ref(false)
const showOutflows = ref(false)

// WHAT: Calculate current period based on purchase date
// WHY: Highlight which period we're currently in
// HOW: Compare purchase date + months to today's date
const currentPeriodDate = computed(() => {
  if (!purchaseDate.value) return null
  const purchase = new Date(purchaseDate.value)
  const today = new Date()
  const monthsDiff = (today.getFullYear() - purchase.getFullYear()) * 12 + 
                     (today.getMonth() - purchase.getMonth())
  const currentPeriod = new Date(purchase)
  currentPeriod.setMonth(currentPeriod.getMonth() + monthsDiff)
  return currentPeriod.toISOString().split('T')[0]
})

// WHAT: Maximum period number in dataset
const maxPeriod = computed(() => {
  if (periods.value.length === 0) return 0
  return Math.max(...periods.value.map(p => p.period_number))
})

// WHAT: Fetch cash flow series data from API
// WHY: Load period-by-period data for display
// HOW: GET request to /api/am/cash-flow-series/{asset_id}/
async function fetchCashFlowData() {
  if (!props.productId) return
  
  loading.value = true
  error.value = null
  
  try {
    // WHAT: Fetch cash flow series data
    const response = await axios.get(`/api/am/cash-flow-series/${props.productId}/`)
    
    console.log('Cash Flow API Response:', response.data)
    
    if (response.data) {
      periods.value = response.data.periods || []
      purchaseDate.value = response.data.purchase_date || null
      
      console.log('Periods loaded:', periods.value.length)
      console.log('Purchase date:', purchaseDate.value)
      
      // WHAT: Mark current period
      // WHY: Visual indicator of where we are in the timeline
      const currentDate = currentPeriodDate.value
      periods.value.forEach(period => {
        period.is_current = period.period_date === currentDate
      })
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to load cash flow data'
    console.error('Error fetching cash flow data:', err)
  } finally {
    loading.value = false
  }
}

// WHAT: Calculate total acquisition costs
// WHY: Sum all acquisition expense fields
function getAcqTotal(period: any): number {
  return (period.acq_due_diligence_expenses || 0) +
         (period.acq_legal_expenses || 0) +
         (period.acq_title_expenses || 0) +
         (period.acq_other_expenses || 0)
}

// WHAT: Format currency values
// WHY: Consistent display of monetary amounts
function fmtCurrency(value: number | null | undefined): string {
  if (value === null || value === undefined || value === 0) return '-'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value)
}

// WHAT: Format date values
// WHY: Consistent date display (MM/YYYY)
function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })
}

// WHAT: Toggle section visibility
// WHY: Collapse/expand inflows and outflows details
function toggleSection(section: 'inflows' | 'outflows') {
  if (section === 'inflows') {
    showInflows.value = !showInflows.value
  } else {
    showOutflows.value = !showOutflows.value
  }
}

// WHAT: Scroll to current period column
// WHY: Quick navigation to "today" in the timeline
function scrollToCurrentPeriod() {
  if (!tableContainer.value) return
  const currentPeriodIndex = periods.value.findIndex(p => p.is_current)
  if (currentPeriodIndex === -1) return
  
  // WHAT: Calculate scroll position (approximate)
  const columnWidth = 120 // Approximate width of each period column
  const scrollPosition = currentPeriodIndex * columnWidth
  tableContainer.value.scrollLeft = scrollPosition
}

// WHAT: Fetch data on mount and when productId changes
onMounted(() => {
  fetchCashFlowData()
})

watch(() => props.productId, () => {
  fetchCashFlowData()
})
</script>

<style scoped>
/* WHAT: Cash flow series table styling */
/* WHY: Horizontal scrolling with sticky first column and header */

.cash-flow-series-container {
  width: 100%;
}

.table-responsive {
  max-height: 600px;
  overflow-x: auto;
  overflow-y: auto;
  position: relative;
}

.cash-flow-table {
  min-width: 100%;
  margin-bottom: 0;
  font-size: 0.875rem;
}

/* WHAT: Sticky header rows */
/* WHY: Keep period numbers and dates visible while scrolling */
.sticky-header {
  position: sticky;
  top: 0;
  z-index: 10;
  background-color: #f8f9fa;
}

/* WHAT: Sticky first column (line item names) */
/* WHY: Keep row labels visible while scrolling horizontally */
.sticky-col {
  position: sticky;
  left: 0;
  z-index: 5;
  background-color: white;
  border-right: 2px solid #dee2e6 !important;
}

.sticky-header .sticky-col {
  z-index: 15;
  background-color: #f8f9fa;
}

/* WHAT: Column widths */
.line-item-col {
  min-width: 200px;
  max-width: 200px;
}

.period-col {
  min-width: 120px;
  max-width: 120px;
  white-space: nowrap;
}

/* WHAT: Current period highlighting */
/* WHY: Visual indicator of current month */
.current-period {
  background-color: #fff3cd !important;
  border-left: 3px solid #ffc107 !important;
  border-right: 3px solid #ffc107 !important;
}

/* WHAT: Section headers */
.section-header td {
  background-color: #f8f9fa;
  font-weight: 600;
}

/* WHAT: Clickable section headers */
.clickable {
  cursor: pointer;
  user-select: none;
}

.clickable:hover {
  opacity: 0.9;
}

/* WHAT: Hover effects */
.cash-flow-table tbody tr:hover {
  background-color: #f8f9fa;
}
</style>
