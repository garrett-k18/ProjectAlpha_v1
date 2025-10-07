<template>
  <!--
    HistoricalCashFlowTable.vue
    WHAT: Reusable component to display historical property cash flow data by year
    WHY: Provides clean table format for analyzing historical operating performance (NOI, EGI, Opex)
    HOW: Uses Hyper UI table-centered styling with Bootstrap classes for responsive layout
    
    Props:
    - cashFlowData: Array of cash flow objects with annual operating data
    - title: string - card header title (optional, can be empty if wrapped in parent card)
    - loading: boolean - show loading spinner
  -->
  <div>
    <!-- Loading state -->
    <div v-if="loading" class="text-muted text-center py-3">
      <div class="spinner-border spinner-border-sm me-2" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      Loading cash flow data...
    </div>
    
    <!-- Empty state -->
    <div v-else-if="!cashFlowData || cashFlowData.length === 0" class="text-muted text-center py-3">
      No historical cash flow data available.
    </div>
    
    <!-- Expand/Collapse All Button -->
    <div v-else>
      <div class="d-flex justify-content-end mb-2">
        <button 
          type="button"
          class="btn btn-sm btn-outline-secondary"
          @click="toggleAllSections"
        >
          <i :class="allExpanded ? 'mdi mdi-chevron-up' : 'mdi mdi-chevron-down'" class="me-1"></i>
          {{ allExpanded ? 'Collapse All' : 'Expand All' }}
        </button>
      </div>

      <!-- Data table with collapsible sections -->
      <div class="table-responsive">
        <table class="table table-centered table-sm mb-0">
          <thead class="table-light">
            <tr>
              <!-- First column is metric name -->
              <th class="text-start">Metric</th>
              <!-- Subsequent columns are years -->
              <th v-for="row in cashFlowData" :key="`year-${row.year}`" class="text-end">
                <strong>{{ row.year }}</strong>
              </th>
            </tr>
          </thead>
          <tbody>
            <!-- SECTION 1: Total Gross Revenue (collapsible parent) -->
            <tr 
              @click="grossRevenueCollapsed = !grossRevenueCollapsed" 
              class="parent-row cursor-pointer bg-light"
            >
              <td class="fw-bold ps-3">
                <i :class="grossRevenueCollapsed ? 'mdi mdi-chevron-right' : 'mdi mdi-chevron-down'" class="me-1"></i>
                Total Gross Revenue (EGI)
              </td>
              <td v-for="row in cashFlowData" :key="`egi-total-${row.year}`" class="text-end fw-bold">
                {{ formatCurrency(row.effective_gross_income) }}
              </td>
            </tr>

            <!-- Sub-items: Gross Potential Rent Revenue -->
            <tr v-show="!grossRevenueCollapsed" class="bg-light">
              <td class="small text-muted ps-5">Gross Potential Rent Revenue</td>
              <td v-for="row in cashFlowData" :key="`gpr-${row.year}`" class="text-end small">
                {{ formatCurrency(row.gross_potential_rent_revenue) }}
              </td>
            </tr>

            <!-- Sub-items: Vacancy % / Loss -->
            <tr v-show="!grossRevenueCollapsed" class="bg-light">
              <td class="small text-muted ps-5">Vacancy % / Loss</td>
              <td v-for="row in cashFlowData" :key="`vl-${row.year}`" class="text-end small text-danger">
                {{ formatPercent(row.vacancy_pct) }} / {{ formatCurrency(row.vacancy_loss) }}
              </td>
            </tr>

            <!-- Sub-items: Effective Gross Rent Revenue -->
            <tr v-show="!grossRevenueCollapsed" class="bg-light">
              <td class="small text-muted ps-5 fw-semibold">Effective Gross Rent Revenue</td>
              <td v-for="row in cashFlowData" :key="`egrr-sub-${row.year}`" class="text-end small fw-semibold">
                {{ formatCurrency(row.effective_gross_rent_revenue) }}
              </td>
            </tr>

            <!-- Sub-items: Other Income -->
            <tr v-show="!grossRevenueCollapsed" class="bg-light">
              <td class="small text-muted ps-5">Other Income</td>
              <td v-for="row in cashFlowData" :key="`oi-${row.year}`" class="text-end small">
                {{ formatCurrency(row.other_income) }}
              </td>
            </tr>

            <!-- Sub-items: CAM Income -->
            <tr v-show="!grossRevenueCollapsed" class="bg-light">
              <td class="small text-muted ps-5">CAM Income</td>
              <td v-for="row in cashFlowData" :key="`cam-${row.year}`" class="text-end small">
                {{ formatCurrency(row.cam_income) }}
              </td>
            </tr>

            <!-- SECTION 2: Total Operating Expenses (collapsible parent) -->
            <tr 
              @click="expensesCollapsed = !expensesCollapsed" 
              class="parent-row cursor-pointer"
            >
              <td class="fw-bold ps-3">
                <i :class="expensesCollapsed ? 'mdi mdi-chevron-right' : 'mdi mdi-chevron-down'" class="me-1"></i>
                Total Operating Expenses
              </td>
              <td v-for="row in cashFlowData" :key="`opex-total-${row.year}`" class="text-end fw-bold">
                {{ formatCurrency(row.total_operating_expenses) }}
              </td>
            </tr>

            <!-- Expense Sub-items -->
            <tr v-show="!expensesCollapsed">
              <td class="small text-muted ps-5">Admin</td>
              <td v-for="row in cashFlowData" :key="`admin-${row.year}`" class="text-end small">
                {{ formatCurrency(row.admin) }}
              </td>
            </tr>
            <tr v-show="!expensesCollapsed">
              <td class="small text-muted ps-5">Insurance</td>
              <td v-for="row in cashFlowData" :key="`insurance-${row.year}`" class="text-end small">
                {{ formatCurrency(row.insurance) }}
              </td>
            </tr>
            <tr v-show="!expensesCollapsed">
              <td class="small text-muted ps-5">Utilities - Water</td>
              <td v-for="row in cashFlowData" :key="`water-${row.year}`" class="text-end small">
                {{ formatCurrency(row.utilities_water) }}
              </td>
            </tr>
            <tr v-show="!expensesCollapsed">
              <td class="small text-muted ps-5">Utilities - Sewer</td>
              <td v-for="row in cashFlowData" :key="`sewer-${row.year}`" class="text-end small">
                {{ formatCurrency(row.utilities_sewer) }}
              </td>
            </tr>
            <tr v-show="!expensesCollapsed">
              <td class="small text-muted ps-5">Utilities - Electric</td>
              <td v-for="row in cashFlowData" :key="`electric-${row.year}`" class="text-end small">
                {{ formatCurrency(row.utilities_electric) }}
              </td>
            </tr>
            <tr v-show="!expensesCollapsed">
              <td class="small text-muted ps-5">Utilities - Gas</td>
              <td v-for="row in cashFlowData" :key="`gas-${row.year}`" class="text-end small">
                {{ formatCurrency(row.utilities_gas) }}
              </td>
            </tr>
            <tr v-show="!expensesCollapsed">
              <td class="small text-muted ps-5">Trash</td>
              <td v-for="row in cashFlowData" :key="`trash-${row.year}`" class="text-end small">
                {{ formatCurrency(row.trash) }}
              </td>
            </tr>
            <tr v-show="!expensesCollapsed">
              <td class="small text-muted ps-5">Utilities - Other</td>
              <td v-for="row in cashFlowData" :key="`util-other-${row.year}`" class="text-end small">
                {{ formatCurrency(row.utilities_other) }}
              </td>
            </tr>
            <tr v-show="!expensesCollapsed">
              <td class="small text-muted ps-5">Property Management</td>
              <td v-for="row in cashFlowData" :key="`pm-${row.year}`" class="text-end small">
                {{ formatCurrency(row.property_management) }}
              </td>
            </tr>
            <tr v-show="!expensesCollapsed">
              <td class="small text-muted ps-5">Repairs & Maintenance</td>
              <td v-for="row in cashFlowData" :key="`repairs-${row.year}`" class="text-end small">
                {{ formatCurrency(row.repairs_maintenance) }}
              </td>
            </tr>
            <tr v-show="!expensesCollapsed">
              <td class="small text-muted ps-5">Marketing</td>
              <td v-for="row in cashFlowData" :key="`marketing-${row.year}`" class="text-end small">
                {{ formatCurrency(row.marketing) }}
              </td>
            </tr>
            <tr v-show="!expensesCollapsed">
              <td class="small text-muted ps-5">Property Taxes</td>
              <td v-for="row in cashFlowData" :key="`taxes-${row.year}`" class="text-end small">
                {{ formatCurrency(row.property_taxes) }}
              </td>
            </tr>
            <tr v-show="!expensesCollapsed">
              <td class="small text-muted ps-5">HOA Fees</td>
              <td v-for="row in cashFlowData" :key="`hoa-${row.year}`" class="text-end small">
                {{ formatCurrency(row.hoa_fees) }}
              </td>
            </tr>
            <tr v-show="!expensesCollapsed">
              <td class="small text-muted ps-5">Security</td>
              <td v-for="row in cashFlowData" :key="`security-${row.year}`" class="text-end small">
                {{ formatCurrency(row.security_property_preservation) }}
              </td>
            </tr>
            <tr v-show="!expensesCollapsed">
              <td class="small text-muted ps-5">Landscaping</td>
              <td v-for="row in cashFlowData" :key="`landscaping-${row.year}`" class="text-end small">
                {{ formatCurrency(row.landscaping) }}
              </td>
            </tr>
            <tr v-show="!expensesCollapsed">
              <td class="small text-muted ps-5">Pool Maintenance</td>
              <td v-for="row in cashFlowData" :key="`pool-${row.year}`" class="text-end small">
                {{ formatCurrency(row.pool_maintenance) }}
              </td>
            </tr>
            <tr v-show="!expensesCollapsed">
              <td class="small text-muted ps-5">Other Expenses</td>
              <td v-for="row in cashFlowData" :key="`other-${row.year}`" class="text-end small">
                {{ formatCurrency(row.other_expense) }}
              </td>
            </tr>

            <!-- Bottom Line Metrics (always visible) -->
            <tr class="bg-light border-top border-2">
              <td class="fw-bold ps-3">Net Operating Income (NOI)</td>
              <td v-for="row in cashFlowData" :key="`noi-${row.year}`" class="text-end fw-bold">
                {{ formatCurrency(row.net_operating_income) }}
              </td>
            </tr>
            <tr>
              <td class="ps-3">Operating Expense Ratio (OER %)</td>
              <td v-for="row in cashFlowData" :key="`oer-${row.year}`" class="text-end">
                {{ formatPercent(row.operating_expense_ratio) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * HistoricalCashFlowTable Component
 * 
 * WHAT: Displays historical property cash flow data in a formatted table with collapsible sections
 * WHY: Centralizes cash flow display logic for reuse across commercial analysis
 * HOW: Accepts cash flow array from parent, formats all fields using backend calculations
 * 
 * Props:
 * - cashFlowData: Array<CashFlowRow> - list of annual cash flow records
 * - title?: string - card header title (optional, can be empty if wrapped in parent card)
 * - loading?: boolean - loading state
 */

// Import ref from Vue for reactive state
import { ref } from 'vue'

// Props interface for strong typing
// All calculated fields come from backend model methods for consistency
interface CashFlowRow {
  id?: number
  year?: number
  // Income
  gross_potential_rent_revenue?: number  // User-entered: gross potential rent for year
  cam_income?: number
  other_income?: number
  vacancy_pct?: number  // User-entered: vacancy percentage (e.g., 5.00 for 5%)
  vacancy_loss?: number  // Backend calc: gross_potential_rent_revenue * (vacancy_pct / 100)
  effective_gross_rent_revenue?: number  // Backend calc: gross_potential_rent_revenue - vacancy_loss
  // Operating Expenses
  admin?: number
  insurance?: number
  utilities_water?: number
  utilities_sewer?: number
  utilities_electric?: number
  utilities_gas?: number
  trash?: number
  utilities_other?: number
  property_management?: number
  repairs_maintenance?: number
  marketing?: number
  property_taxes?: number
  hoa_fees?: number
  security_property_preservation?: number
  landscaping?: number
  pool_maintenance?: number
  other_expense?: number
  // Backend-calculated fields
  effective_gross_income?: number  // Backend calc: effective_gross_rent_revenue + other_income + cam_income
  total_operating_expenses?: number  // Backend calc: sum of all expense fields
  net_operating_income?: number  // Backend calc: EGI - Total Opex
  operating_expense_ratio?: number  // Backend calc: (Total Opex / EGI) * 100
  notes?: string
}

// Define props with defaults
const props = withDefaults(defineProps<{
  cashFlowData: CashFlowRow[]
  title?: string
  loading?: boolean
}>(), {
  title: 'Historical Cash Flow',
  loading: false,
})

// Collapsible section states
const grossRevenueCollapsed = ref(false)
const expensesCollapsed = ref(false)
const allExpanded = ref(false)

// WHAT: Toggle all collapsible sections at once
// WHY: Convenience function for expand/collapse all
// HOW: Set all collapse states to same value
function toggleAllSections() {
  allExpanded.value = !allExpanded.value
  grossRevenueCollapsed.value = allExpanded.value
  expensesCollapsed.value = allExpanded.value
}

// WHAT: Format currency as USD with no decimals
// WHY: Standard currency display for cash flow amounts
// HOW: Use toLocaleString with currency formatter
function formatCurrency(value: number | null | undefined): string {
  const num = Number(value ?? 0)
  return Number.isFinite(num) 
    ? num.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })
    : '-'
}

// WHAT: Format percentage with 2 decimals
// WHY: Display OER and other ratios consistently
// HOW: Use toLocaleString with fixed decimal places
function formatPercent(value: number | null | undefined): string {
  const num = Number(value ?? 0)
  return Number.isFinite(num) 
    ? `${num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}%`
    : '-'
}
</script>

<style scoped>
/**
 * Scoped styles for HistoricalCashFlowTable
 * WHAT: Minimal overrides; rely on Hyper UI Bootstrap classes
 * WHY: Keeps component consistent with global theme
 * HOW: Add collapsible row styling matching PLMetrics pattern
 */

/* Hyper UI table-centered already provides clean styling */
/* Highlight key metrics */
.bg-light {
  background-color: #f8f9fa !important;
}

/* Parent row styling (collapsible headers) */
.parent-row {
  background-color: #fafbfc;
}

.parent-row:hover {
  background-color: #f1f3f5;
}

/* Cursor pointer for clickable rows */
.cursor-pointer {
  cursor: pointer;
}

/* Sub-item indentation */
.ps-5 {
  padding-left: 3rem !important;
}
</style>
