<template>
  <!--
    WHAT: Cash Flow Series time-series grid component
    WHY: Display period-by-period cash flow data for loan-level analysis
    HOW: Horizontal scrolling table with periods as columns, P&L line items as rows
    WHERE: Used in PerformanceTab.vue (frontend_vue/src/views/am_module/loanlvl/tabs/PerformanceTab.vue)
  -->
  <div class="cash-flow-series-container">
    <!-- WHAT: Header with title and controls -->
    <div class="d-flex justify-content-between align-items-center mb-3">
      <div>
        <h5 class="mb-1">Cash Flows</h5>
      </div>
      <div class="d-flex gap-2">
        <!-- 
          TODO: IMPLEMENT UNDERWRITTEN VS REALIZED COMPARISON
          1. Update API to return net_cash_flow_underwritten (from cf_p0-p30 in BlendedOutcomeModel)
          2. Calculate variance (realized - underwritten) in API response
          3. Add conditional rendering based on viewMode:
             - 'realized': Show only realized Net Cash Flow row (current behavior)
             - 'underwritten': Show only underwritten Net Cash Flow row
             - 'both': Show stacked rows: Underwritten, Realized, Variance (with color coding)
          4. Line items (inflows/outflows) remain realized-only until underwritten line items are added
          5. Variance row should use red for negative, green for positive
        -->
        <select v-model="viewMode" class="form-select form-select-sm" style="width: auto;">
          <option value="realized">Realized</option>
          <option value="underwritten">Underwritten</option>
          <option value="both">Both (with Variance)</option>
        </select>
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
          <!-- 
            STYLING NOTES:
            - Background color: #f0f7ff (subtle blue tint, matches PLMetrics.vue .underwritten-col line 1731)
            - Border removal: border-bottom: none removes line between Period # and Date rows
            - Why inline styles: Bootstrap's table-bordered class overrides scoped CSS, so we use inline styles with !important
            - To change header color: Update background-color here AND in PLMetrics.vue .underwritten-col
            - To restore border: Remove "border-bottom: none !important;" from inline styles below
          -->
          <tr style="border-bottom: none !important;">
            <th class="sticky-col line-item-col" style="background-color: #f0f7ff !important; border-bottom: none !important;">Period</th>
            <th 
              v-for="period in periods" 
              :key="`period-${period.period_number}`"
              :class="{'current-period': period.is_current}"
              class="text-center period-col"
              style="background-color: #f0f7ff !important; border-bottom: none !important;"
            >
              {{ period.period_number }}
            </th>
          </tr>
          
          <!-- WHAT: Row 2 - Period dates -->
          <!-- 
            STYLING NOTES:
            - Background color: #f0f7ff (subtle blue tint, matches PLMetrics.vue .underwritten-col line 1731)
            - Border removal: border-top: none removes line between Period # and Date rows (matches border-bottom on row above)
            - Why inline styles: Bootstrap's table-bordered class overrides scoped CSS, so we use inline styles with !important
            - To change header color: Update background-color here AND in PLMetrics.vue .underwritten-col
            - To restore border: Remove "border-top: none !important;" from inline styles below
          -->
          <tr style="border-top: none !important;">
            <th class="sticky-col line-item-col" style="background-color: #f0f7ff !important; border-top: none !important;">Date</th>
            <th 
              v-for="period in periods" 
              :key="`date-${period.period_number}`"
              :class="{'current-period': period.is_current}"
              class="text-center period-col"
              style="background-color: #f0f7ff !important; border-top: none !important;"
            >
              {{ formatDate(period.period_date) }}
            </th>
          </tr>
        </thead>

        <tbody>
          <!-- WHAT: Net Cash Flow (clickable to toggle inflows/outflows) -->
          <tr class="section-header clickable" @click="toggleAllSections">
            <td class="sticky-col fw-bold">
              <i :class="showNetCashFlow ? 'mdi mdi-chevron-down' : 'mdi mdi-chevron-right'" class="me-2"></i>
              Net Cash Flow
            </td>
            <td v-for="period in periods" :key="`net-${period.period_number}`" class="text-end fw-bold">
              {{ fmtCurrency(period.net_cash_flow) }}
            </td>
          </tr>

          <!-- WHAT: Inflows and Outflows sections (only show when Net Cash Flow is expanded) -->
          <template v-if="showNetCashFlow">
            <!-- WHAT: Inflows Section (collapsible) -->
            <tr class="section-header clickable" @click="toggleSection('inflows')">
            <td class="sticky-col fw-bold ps-4">
              <i :class="showInflows ? 'mdi mdi-chevron-down' : 'mdi mdi-chevron-right'" class="me-2"></i>
              Total Inflows
            </td>
            <td v-for="period in periods" :key="`income-${period.period_number}`" class="text-end fw-semibold">
              {{ fmtCurrency(period.total_income) }}
            </td>
          </tr>
          <template v-if="showInflows">
            <tr>
              <td class="sticky-col ps-5 small text-muted">Principal</td>
              <td v-for="period in periods" :key="`principal-${period.period_number}`" class="text-end small">
                {{ fmtCurrency(period.income_principal) }}
              </td>
            </tr>
            <tr>
              <td class="sticky-col ps-5 small text-muted">Interest</td>
              <td v-for="period in periods" :key="`interest-${period.period_number}`" class="text-end small">
                {{ fmtCurrency(period.income_interest) }}
              </td>
            </tr>
            <tr>
              <td class="sticky-col ps-5 small text-muted">Rent</td>
              <td v-for="period in periods" :key="`rent-${period.period_number}`" class="text-end small">
                {{ fmtCurrency(period.income_rent) }}
              </td>
            </tr>
            <tr>
              <td class="sticky-col ps-5 small text-muted">CAM</td>
              <td v-for="period in periods" :key="`cam-${period.period_number}`" class="text-end small">
                {{ fmtCurrency(period.income_cam) }}
              </td>
            </tr>
            <tr>
              <td class="sticky-col ps-5 small text-muted">Mod Down Payment</td>
              <td v-for="period in periods" :key="`mod-${period.period_number}`" class="text-end small">
                {{ fmtCurrency(period.income_mod_down_payment) }}
              </td>
            </tr>
            <tr>
              <td class="sticky-col ps-5 small text-muted">Liquidation Proceeds</td>
              <td v-for="period in periods" :key="`proceeds-${period.period_number}`" class="text-end small">
                {{ fmtCurrency(period.net_liquidation_proceeds) }}
              </td>
            </tr>
          </template>

          <!-- WHAT: Outflows Section (collapsible) -->
          <tr class="section-header clickable" @click="toggleSection('outflows')">
            <td class="sticky-col fw-bold ps-4">
              <i :class="showOutflows ? 'mdi mdi-chevron-down' : 'mdi mdi-chevron-right'" class="me-2"></i>
              Total Outflows
            </td>
            <td v-for="period in periods" :key="`expenses-${period.period_number}`" class="text-end fw-semibold">
              {{ fmtExpense(period.total_expenses) }}
            </td>
          </tr>
          <template v-if="showOutflows">
            <!-- Purchase Cost (Period 0 only) -->
            <tr>
              <td class="sticky-col ps-5 small text-muted">Purchase Price</td>
              <td v-for="period in periods" :key="`purchase-${period.period_number}`" class="text-end small">
                {{ period.period_number === 0 ? fmtExpense(period.purchase_price) : '-' }}
              </td>
            </tr>
            
            <!-- Acquisition Costs -->
            <tr>
              <td class="sticky-col ps-5 small text-muted">Due Diligence</td>
              <td v-for="period in periods" :key="`dd-${period.period_number}`" class="text-end small">
                {{ fmtExpense(period.acq_due_diligence_expenses) }}
              </td>
            </tr>
            <tr>
              <td class="sticky-col ps-5 small text-muted">Acq Legal</td>
              <td v-for="period in periods" :key="`acq-legal-${period.period_number}`" class="text-end small">
                {{ fmtExpense(period.acq_legal_expenses) }}
              </td>
            </tr>
            <tr>
              <td class="sticky-col ps-5 small text-muted">Title</td>
              <td v-for="period in periods" :key="`title-${period.period_number}`" class="text-end small">
                {{ fmtExpense(period.acq_title_expenses) }}
              </td>
            </tr>
            
            <!-- Operating Expenses -->
            <tr>
              <td class="sticky-col ps-5 small text-muted">Servicing</td>
              <td v-for="period in periods" :key="`servicing-${period.period_number}`" class="text-end small">
                {{ fmtExpense(period.servicing_expenses) }}
              </td>
            </tr>
            <tr>
              <td class="sticky-col ps-5 small text-muted">AM Fees</td>
              <td v-for="period in periods" :key="`am-${period.period_number}`" class="text-end small">
                {{ fmtExpense(period.am_fees_expenses) }}
              </td>
            </tr>
            <tr>
              <td class="sticky-col ps-5 small text-muted">Property Tax</td>
              <td v-for="period in periods" :key="`tax-${period.period_number}`" class="text-end small">
                {{ fmtExpense(period.property_tax_expenses) }}
              </td>
            </tr>
            <tr>
              <td class="sticky-col ps-5 small text-muted">Insurance</td>
              <td v-for="period in periods" :key="`insurance-${period.period_number}`" class="text-end small">
                {{ fmtExpense(period.property_insurance_expenses) }}
              </td>
            </tr>
            
            <!-- Legal/DIL Costs -->
            <tr>
              <td class="sticky-col ps-5 small text-muted">Foreclosure Legal</td>
              <td v-for="period in periods" :key="`fc-${period.period_number}`" class="text-end small">
                {{ fmtExpense(period.legal_foreclosure_expenses) }}
              </td>
            </tr>
            <tr>
              <td class="sticky-col ps-5 small text-muted">Bankruptcy Legal</td>
              <td v-for="period in periods" :key="`bk-${period.period_number}`" class="text-end small">
                {{ fmtExpense(period.legal_bankruptcy_expenses) }}
              </td>
            </tr>
            
            <!-- REO Expenses -->
            <tr>
              <td class="sticky-col ps-5 small text-muted">HOA</td>
              <td v-for="period in periods" :key="`hoa-${period.period_number}`" class="text-end small">
                {{ fmtExpense(period.reo_hoa_expenses) }}
              </td>
            </tr>
            <tr>
              <td class="sticky-col ps-5 small text-muted">Utilities</td>
              <td v-for="period in periods" :key="`util-${period.period_number}`" class="text-end small">
                {{ fmtExpense(period.reo_utilities_expenses) }}
              </td>
            </tr>
            <tr>
              <td class="sticky-col ps-5 small text-muted">Renovation</td>
              <td v-for="period in periods" :key="`reno-${period.period_number}`" class="text-end small">
                {{ fmtExpense(period.reo_renovation_expenses) }}
              </td>
            </tr>
            <tr>
              <td class="sticky-col ps-5 small text-muted">Property Preservation</td>
              <td v-for="period in periods" :key="`pres-${period.period_number}`" class="text-end small">
                {{ fmtExpense(period.reo_property_preservation_expenses) }}
              </td>
            </tr>
            
            <!-- CRE Expenses -->
            <tr>
              <td class="sticky-col ps-5 small text-muted">Marketing</td>
              <td v-for="period in periods" :key="`mkt-${period.period_number}`" class="text-end small">
                {{ fmtExpense(period.cre_marketing_expenses) }}
              </td>
            </tr>
            <tr>
              <td class="sticky-col ps-5 small text-muted">Maintenance</td>
              <td v-for="period in periods" :key="`maint-${period.period_number}`" class="text-end small">
                {{ fmtExpense(period.cre_maintenance_expenses) }}
              </td>
            </tr>
          </template>
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
// WHY: Need asset hub ID to fetch cash flow data
const props = withDefaults(defineProps<{
  assetHubId?: string | number | null
}>(), {
  assetHubId: null
})

// WHAT: Reactive state
const periods = ref<any[]>([])
const purchaseDate = ref<string | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const tableContainer = ref<HTMLElement | null>(null)
const showNetCashFlow = ref(false) // Master toggle for inflows/outflows visibility
const showInflows = ref(false)
const showOutflows = ref(false)
const viewMode = ref<'realized' | 'underwritten' | 'both'>('realized') // TODO: Implement comparison logic

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
  if (!props.assetHubId) return
  
  loading.value = true
  error.value = null
  
  try {
    const response = await axios.get(`/api/am/cash-flow-series/${props.assetHubId}/`)
    
    if (response.data) {
      periods.value = response.data.periods || []
      purchaseDate.value = response.data.purchase_date || null
      
      // Mark current period for highlighting
      const currentDate = currentPeriodDate.value
      periods.value.forEach(period => {
        period.is_current = period.period_date === currentDate
      })
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to load cash flow data'
  } finally {
    loading.value = false
  }
}


// Format currency with negative numbers in parentheses (accounting format)
function fmtCurrency(value: number | null | undefined): string {
  if (value === null || value === undefined || value === 0) return '-'
  
  const abs = Math.abs(value)
  const formatted = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(abs)
  
  return value < 0 ? `(${formatted})` : formatted
}

// Format expenses as negative (in parentheses)
function fmtExpense(value: number | null | undefined): string {
  if (value === null || value === undefined || value === 0) return '-'
  return fmtCurrency(-Math.abs(value))
}

// Format date as 'Mon YYYY'
function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })
}

function toggleSection(section: 'inflows' | 'outflows') {
  if (section === 'inflows') {
    showInflows.value = !showInflows.value
  } else {
    showOutflows.value = !showOutflows.value
  }
}

function toggleAllSections() {
  showNetCashFlow.value = !showNetCashFlow.value
  if (!showNetCashFlow.value) {
    showInflows.value = false
    showOutflows.value = false
  }
}

function scrollToCurrentPeriod() {
  if (!tableContainer.value) return
  const currentPeriodIndex = periods.value.findIndex(p => p.is_current)
  if (currentPeriodIndex === -1) return
  
  const columnWidth = 120
  const scrollPosition = currentPeriodIndex * columnWidth
  tableContainer.value.scrollLeft = scrollPosition
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

<style scoped>
/* 
  ============================================================================
  CASH FLOW SERIES STYLING
  ============================================================================
  
  WHAT: Custom styles for time-series cash flow table
  WHY: Horizontal scrolling with sticky first column and header
  
  COLOR CUSTOMIZATION:
  - Header background: #f0f7ff (matches PLMetrics.vue .underwritten-col)
  - Current period: 3px black border with bold text
  
  ============================================================================
*/

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

/* Sticky header rows */
.sticky-header {
  position: sticky;
  top: 0;
  z-index: 10;
  background-color: #f8f9fa;
}

/* Remove border between Period # and Date rows */
:deep(.cash-flow-table thead.sticky-header tr:first-child th) {
  border-bottom: none !important;
  padding-bottom: 0.25rem !important;
}

:deep(.cash-flow-table thead.sticky-header tr:nth-child(2) th) {
  border-top: none !important;
  padding-top: 0.25rem !important;
}

:deep(.table-bordered thead tr:first-child th) {
  border-bottom: none !important;
}

:deep(.table-bordered thead tr:nth-child(2) th) {
  border-top: none !important;
}

:deep(.table.table-bordered thead tr:first-child > th) {
  border-bottom-width: 0 !important;
}

:deep(.table.table-bordered thead tr:nth-child(2) > th) {
  border-top-width: 0 !important;
}

/* Sticky first column */
.sticky-col {
  position: sticky;
  left: 0;
  z-index: 5;
  background-color: white;
  border-right: 2px solid #dee2e6 !important;
  box-shadow: 2px 0 5px rgba(0,0,0,0.1);
}

.sticky-header .sticky-col {
  z-index: 15;
}

.cash-flow-table tbody .sticky-col {
  background-color: white !important;
}

.line-item-col {
  min-width: 200px;
  max-width: 200px;
}

.period-col {
  min-width: 120px;
  max-width: 120px;
  white-space: nowrap;
}

/* Current period highlighting */
.current-period {
  border-left: 3px solid #000 !important;
  border-right: 3px solid #000 !important;
  border-top: 3px solid #000 !important;
  border-bottom: 3px solid #000 !important;
  font-weight: bold !important;
}

thead .current-period {
  border-top: 3px solid #000 !important;
}

tbody tr:last-child .current-period {
  border-bottom: 3px solid #000 !important;
}

.section-header td {
  font-weight: 600;
}

.section-header .sticky-col {
  background-color: white !important;
}

.clickable {
  cursor: pointer;
  user-select: none;
}

.clickable:hover {
  opacity: 0.9;
}

.cash-flow-table tbody tr:hover {
  background-color: #f8f9fa;
}
</style>
