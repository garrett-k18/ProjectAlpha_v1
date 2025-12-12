<template>
  <!--
    WHAT: Shared Cash Flow Series component - horizontal time-series grid
    WHY: Reusable component for displaying period-by-period cash flows across modules
    HOW: Periods as columns, line items as rows, expandable sections
    WHERE: Used in ACQ module (REO model), AM module (Performance tab), anywhere else needed
  -->
  <div class="cash-flow-series-container">
    <!-- WHAT: Header with title and controls -->
    <div class="d-flex justify-content-between align-items-center mb-3">
      <div>
        <h5 class="card-title mb-0">{{ title }}</h5>
        <small v-if="subtitle" class="text-muted">{{ subtitle }}</small>
      </div>
      <div class="d-flex gap-2 align-items-center">
        <!-- WHAT: Scenario Toggle (optional, for REO) -->
        <select 
          v-if="showScenarioToggle" 
          v-model="currentScenario" 
          class="form-select form-select-sm" 
          style="width: auto; min-width: 100px;"
          @change="$emit('scenario-changed', currentScenario)"
        >
          <option value="as_is">As-Is</option>
          <option value="arv">ARV</option>
        </select>
        
        <!-- WHAT: Jump to specific period (e.g. current period, sale period) -->
        <button 
          v-if="jumpToPeriod !== null" 
          class="btn btn-sm btn-outline-primary" 
          @click="scrollToTarget"
        >
          <i class="mdi mdi-calendar-today me-1"></i>
          {{ jumpButtonLabel }}
        </button>
      </div>
    </div>

    <!-- WHAT: Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
      <span class="ms-2 text-muted">Loading cash flow data...</span>
    </div>

    <!-- WHAT: Error State -->
    <div v-else-if="error" class="alert alert-danger">
      <i class="mdi mdi-alert-circle me-2"></i>
      {{ error }}
    </div>

    <!-- WHAT: Horizontal scrolling table wrapper -->
    <div v-else class="table-responsive cash-flow-table-wrapper" ref="tableContainer">
      <table class="table table-sm table-bordered cash-flow-table mb-0">
        <thead class="sticky-header">
          <!-- WHAT: Row 1 - Period numbers/labels -->
          <tr style="border-bottom: none !important;">
            <th class="sticky-col line-item-col bg-light" style="border-bottom: none !important;">
              Period
            </th>
            <th 
              v-for="(period, index) in periods" 
              :key="`period-${index}`"
              :class="{
                'highlight-period': period === highlightPeriod,
                'bg-primary-subtle': period === 0,
                'bg-success-subtle': period === finalPeriod
              }"
              class="text-center period-col bg-light"
              style="border-bottom: none !important;"
            >
              {{ periodLabels[index] }}
            </th>
          </tr>
          
          <!-- WHAT: Row 2 - Period dates/descriptions -->
          <tr style="border-top: none !important;">
            <th class="sticky-col line-item-col bg-light" style="border-top: none !important;">
              {{ dateLabel }}
            </th>
            <th 
              v-for="(period, index) in periods" 
              :key="`date-${index}`"
              :class="{
                'highlight-period': period === highlightPeriod,
                'bg-primary-subtle': period === 0,
                'bg-success-subtle': period === finalPeriod
              }"
              class="text-center period-col bg-light"
              style="border-top: none !important;"
            >
              {{ periodDates[index] }}
            </th>
          </tr>
        </thead>

        <tbody>
          <!-- WHAT: Net Cash Flow (master row, clickable to toggle all details) -->
          <tr class="section-header clickable" @click="toggleAllSections">
            <td class="sticky-col fw-bold">
              <i :class="showDetails ? 'mdi mdi-chevron-down' : 'mdi mdi-chevron-right'" class="me-2"></i>
              Net Cash Flow
            </td>
            <td 
              v-for="(period, index) in periods" 
              :key="`net-${index}`" 
              class="text-center fw-bold"
              :class="{
                'text-success': netCashFlowArray[index] > 0,
                'text-danger': netCashFlowArray[index] < 0
              }"
            >
              {{ formatCurrency(netCashFlowArray[index]) }}
            </td>
          </tr>

          <!-- WHAT: Inflows and Outflows sections (show when expanded) -->
          <template v-if="showDetails">
            <!-- WHAT: Inflows Section (collapsible) -->
            <tr class="section-header clickable" @click="toggleSection('inflows')">
              <td class="sticky-col fw-bold ps-4">
                <i :class="showInflows ? 'mdi mdi-chevron-down' : 'mdi mdi-chevron-right'" class="me-2"></i>
                Total Inflows
              </td>
              <td 
                v-for="(period, index) in periods" 
                :key="`inflows-${index}`" 
                class="text-center fw-semibold text-success"
              >
                {{ formatCurrency(totalInflowsArray[index]) }}
              </td>
            </tr>
            
            <!-- WHAT: Inflow line items (show when inflows expanded) -->
            <template v-if="showInflows">
              <tr v-for="lineItem in inflowLineItems" :key="lineItem.key">
                <td class="sticky-col ps-5 small text-muted">{{ lineItem.label }}</td>
                <td 
                  v-for="(period, index) in periods" 
                  :key="`${lineItem.key}-${index}`" 
                  class="text-center small"
                >
                  {{ formatCurrency(lineItem.values[index]) }}
                </td>
              </tr>
            </template>

            <!-- WHAT: Outflows Section (collapsible) -->
            <tr class="section-header clickable" @click="toggleSection('outflows')">
              <td class="sticky-col fw-bold ps-4">
                <i :class="showOutflows ? 'mdi mdi-chevron-down' : 'mdi mdi-chevron-right'" class="me-2"></i>
                Total Outflows
              </td>
              <td 
                v-for="(period, index) in periods" 
                :key="`outflows-${index}`" 
                class="text-center fw-semibold text-danger"
              >
                {{ formatExpense(totalOutflowsArray[index]) }}
              </td>
            </tr>
            
            <!-- WHAT: Outflow line items (show when outflows expanded) -->
            <template v-if="showOutflows">
              <tr v-for="lineItem in outflowLineItems" :key="lineItem.key">
                <td class="sticky-col ps-5 small text-muted">{{ lineItem.label }}</td>
                <td 
                  v-for="(period, index) in periods" 
                  :key="`${lineItem.key}-${index}`" 
                  class="text-center small"
                >
                  {{ formatExpense(lineItem.values[index]) }}
                </td>
              </tr>
            </template>
          </template>

          <!-- WHAT: Cumulative Cash Flow Row (optional) -->
          <tr v-if="showCumulative" class="section-header">
            <td class="sticky-col fw-bold border-top-2">
              Cumulative Cash Flow
            </td>
            <td 
              v-for="(period, index) in periods" 
              :key="`cumulative-${index}`" 
              class="text-center fw-bold border-top-2"
              :class="{
                'text-success': cumulativeCashFlowArray[index] >= 0,
                'text-danger': cumulativeCashFlowArray[index] < 0
              }"
            >
              {{ formatCurrency(cumulativeCashFlowArray[index]) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- WHAT: Timeline Summary (optional, for REO) -->
    <div v-if="showTimelineSummary && timelineSummary" class="mt-3 p-2 bg-light rounded">
      <small class="fw-semibold text-muted d-block mb-2">Timeline Summary:</small>
      <div class="row g-2">
        <div v-for="(phase, key) in timelineSummary" :key="key" class="col-auto">
          <small>
            <strong>{{ phase.label }}:</strong> 
            Periods {{ phase.start_period }}-{{ phase.end_period }}
            ({{ phase.duration_months }} months)
          </small>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * WHAT: Shared Cash Flow Series component
 * WHY: Reusable horizontal time-series grid for any module
 * HOW: Accept arrays of data via props, display in scrollable table with expand/collapse
 */
import { ref, computed, watch } from 'vue'

// WHAT: Component props
interface LineItem {
  key: string
  label: string
  values: number[]
}

interface TimelinePhase {
  label: string
  start_period: number
  end_period: number
  duration_months: number
}

const props = withDefaults(defineProps<{
  // WHAT: Display configuration
  title?: string
  subtitle?: string
  dateLabel?: string
  
  // WHAT: Period data (required)
  periods: number[]  // Array of period numbers [0, 1, 2, ..., N]
  periodLabels: string[]  // Labels for each period ["Period 0", "Month 1", ...]
  periodDates: string[]  // Dates/descriptions for each period ["Settlement", "Jan 2024", ...]
  
  // WHAT: Cash flow data (required)
  netCashFlowArray: number[]  // Net cash flow per period
  totalInflowsArray: number[]  // Total inflows per period
  totalOutflowsArray: number[]  // Total outflows per period
  
  // WHAT: Line item details (optional, for expand/collapse)
  inflowLineItems?: LineItem[]  // Individual inflow categories
  outflowLineItems?: LineItem[]  // Individual outflow categories
  
  // WHAT: Optional features
  cumulativeCashFlowArray?: number[]  // Cumulative cash flow per period
  showCumulative?: boolean  // Show cumulative row
  highlightPeriod?: number | null  // Period to highlight (e.g., current period)
  jumpToPeriod?: number | null  // Period to jump to on button click
  jumpButtonLabel?: string  // Label for jump button
  
  // WHAT: Scenario toggle (for REO)
  showScenarioToggle?: boolean  // Show As-Is/ARV toggle
  initialScenario?: 'as_is' | 'arv'  // Initial scenario selection
  
  // WHAT: Timeline summary (for REO)
  showTimelineSummary?: boolean  // Show timeline phase summary
  timelineSummary?: Record<string, TimelinePhase>  // Timeline phases
  
  // WHAT: Loading/error states
  loading?: boolean
  error?: string | null
}>(), {
  title: 'Cash Flows',
  subtitle: '',
  dateLabel: 'Date',
  inflowLineItems: () => [],
  outflowLineItems: () => [],
  cumulativeCashFlowArray: () => [],
  showCumulative: false,
  highlightPeriod: null,
  jumpToPeriod: null,
  jumpButtonLabel: 'Jump to Period',
  showScenarioToggle: false,
  initialScenario: 'as_is',
  showTimelineSummary: false,
  timelineSummary: undefined,
  loading: false,
  error: null,
})

// WHAT: Component emits
const emit = defineEmits<{
  'scenario-changed': [scenario: 'as_is' | 'arv']
}>()

// WHAT: Reactive state
const tableContainer = ref<HTMLElement | null>(null)
const showDetails = ref(false) // Master toggle for inflows/outflows visibility
const showInflows = ref(false)
const showOutflows = ref(false)
const currentScenario = ref<'as_is' | 'arv'>(props.initialScenario)

// WHAT: Computed final period
const finalPeriod = computed(() => {
  return props.periods.length > 0 ? props.periods[props.periods.length - 1] : null
})

// WHAT: Format currency with accounting style (negative in parentheses)
function formatCurrency(value: number | null | undefined): string {
  if (value === null || value === undefined || value === 0) return '—'
  
  const abs = Math.abs(value)
  const formatted = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(abs)
  
  return value < 0 ? `(${formatted})` : formatted
}

// WHAT: Format expenses as negative (always in parentheses)
function formatExpense(value: number | null | undefined): string {
  if (value === null || value === undefined || value === 0) return '—'
  return formatCurrency(-Math.abs(value))
}

// WHAT: Toggle individual sections
function toggleSection(section: 'inflows' | 'outflows') {
  if (section === 'inflows') {
    showInflows.value = !showInflows.value
  } else {
    showOutflows.value = !showOutflows.value
  }
}

// WHAT: Toggle all sections (master toggle)
function toggleAllSections() {
  showDetails.value = !showDetails.value
  if (!showDetails.value) {
    showInflows.value = false
    showOutflows.value = false
  }
}

// WHAT: Scroll to target period
function scrollToTarget() {
  if (!tableContainer.value || props.jumpToPeriod === null) return
  
  const periodIndex = props.periods.indexOf(props.jumpToPeriod)
  if (periodIndex === -1) return
  
  const columnWidth = 120
  const scrollPosition = periodIndex * columnWidth
  tableContainer.value.scrollLeft = scrollPosition
}

// WHAT: Watch for scenario prop changes
watch(() => props.initialScenario, (newScenario) => {
  currentScenario.value = newScenario
})
</script>

<style scoped>
/* 
  ============================================================================
  SHARED CASH FLOW SERIES STYLING
  ============================================================================
  
  WHAT: Styles for horizontal time-series cash flow table
  WHY: Sticky column/header, expandable sections, period highlighting
  
  ============================================================================
*/

.cash-flow-series-container {
  width: 100%;
}

/* Table responsive wrapper with border */
.table-responsive.cash-flow-table-wrapper {
  max-height: 600px;
  overflow-x: auto;
  overflow-y: auto;
  position: relative;
  border: 1px solid #dee2e6;
  border-radius: 0.375rem;
  background-color: white;
}

.cash-flow-table {
  min-width: 100%;
  margin-bottom: 0;
  font-size: 0.875rem;
  background-color: white;
}

.cash-flow-table td {
  padding: 0.5rem 0.75rem;
  vertical-align: middle;
  line-height: 1.4;
}

.cash-flow-table td:not(.sticky-col) {
  white-space: nowrap;
}

.cash-flow-table th {
  padding: 0.5rem 0.75rem;
  vertical-align: middle;
  white-space: nowrap;
}

.cash-flow-table tbody tr {
  height: auto;
  min-height: 2.5rem;
}


/* Sticky header rows */
.sticky-header {
  position: sticky;
  top: 0;
  z-index: 10;
  background-color: #f8f9fa;
}

.sticky-header th {
  font-weight: 600;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #495057;
}

/* Sticky first column */
.sticky-col {
  position: sticky;
  left: 0;
  z-index: 5;
  background-color: white;
  border-right: 2px solid #dee2e6 !important;
  box-shadow: 2px 0 4px rgba(0,0,0,0.08);
}

.sticky-header .sticky-col {
  z-index: 15;
  background-color: #f8f9fa !important;
}

.cash-flow-table tbody .sticky-col {
  background-color: white !important;
}

.line-item-col {
  min-width: 200px;
  max-width: 200px;
  white-space: normal;
  word-wrap: break-word;
}

.period-col {
  min-width: 120px;
  max-width: 120px;
  white-space: nowrap;
}

/* Period highlighting */
.highlight-period {
  border-left: 3px solid #0d6efd !important;
  border-right: 3px solid #0d6efd !important;
  border-top: 3px solid #0d6efd !important;
  border-bottom: 3px solid #0d6efd !important;
  font-weight: bold !important;
  background-color: #e7f1ff !important;
}

/* Section header styling */
.section-header td {
  font-weight: 600;
  background-color: #f8f9fa;
}

.section-header .sticky-col {
  background-color: #f8f9fa !important;
}

.clickable {
  cursor: pointer;
  user-select: none;
  transition: background-color 0.15s ease;
}

.clickable:hover {
  background-color: #e9ecef !important;
}

.clickable:hover .sticky-col {
  background-color: #e9ecef !important;
}

.cash-flow-table tbody tr:hover {
  background-color: #f8f9fa;
}

.cash-flow-table tbody tr:hover .sticky-col {
  background-color: #f8f9fa !important;
}

.border-top-2 {
  border-top: 2px solid #dee2e6 !important;
}

/* Remove border between header rows */
:deep(.cash-flow-table thead.sticky-header tr:first-child th) {
  border-bottom: none !important;
  padding-bottom: 0.25rem !important;
}

:deep(.cash-flow-table thead.sticky-header tr:nth-child(2) th) {
  border-top: none !important;
  padding-top: 0.25rem !important;
}
</style>
