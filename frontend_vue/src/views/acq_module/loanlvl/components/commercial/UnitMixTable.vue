<template>
  <!--
    UnitMixTable.vue
    WHAT: Reusable component to display subject or comparable property unit mix data
    WHY: Provides a clean, consistent table format for commercial unit mix analysis
    HOW: Uses Hyper UI table-centered styling with Bootstrap classes for responsive layout
  -->
  <div class="card">
    <div class="card-header d-flex align-items-center justify-content-between">
      <!-- Title prop allows parent to customize header -->
      <h5 class="card-title mb-0">{{ title }}</h5>
      <!-- Optional slot for actions (e.g., add/edit buttons) -->
      <slot name="actions"></slot>
    </div>
    <div class="card-body">
      <!-- Loading state -->
      <div v-if="loading" class="text-muted text-center py-3">
        <div class="spinner-border spinner-border-sm me-2" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        Loading unit mix data...
      </div>
      
      <!-- Empty state -->
      <div v-else-if="!unitMixData || unitMixData.length === 0" class="text-muted text-center py-3">
        No unit mix data available.
      </div>
      
      <!-- Data table (Hyper UI theme - table-centered from screenshot) -->
      <div v-else class="table-responsive">
        <table class="table table-centered mb-0">
          <thead>
            <tr>
              <!-- Column headers for unit mix data -->
              <th>Unit Type</th>
              <th class="text-end">Count</th>
              <th class="text-end">Avg Square Feet</th>
              <th class="text-end">Average Rent</th>
              <th class="text-end">Total Monthly Rent</th>
              <!-- Optional: Rent per sqft calculated column -->
              <th v-if="showRentPerSqft" class="text-end">Rent/Sqft</th>
            </tr>
          </thead>
          <tbody>
            <!-- Loop through unit mix rows -->
            <tr v-for="(unit, index) in unitMixData" :key="`unit-${index}`">
              <!-- Unit Type: e.g., "1 Bed / 1 Bath", "Studio", "2 Bed / 2 Bath" -->
              <td>{{ unit.unit_type || '-' }}</td>
              
              <!-- Count: number of units of this type -->
              <td class="text-end">{{ formatCount(unit.unit_count) }}</td>
              
              <!-- Avg Square Feet: average sqft for this unit type -->
              <td class="text-end">{{ formatNumber(unit.unit_avg_sqft) }}</td>
              
              <!-- Average Rent: average monthly rent for this unit type -->
              <td class="text-end">{{ formatCurrency(unit.unit_avg_rent) }}</td>
              
              <!-- Total Monthly Rent: count × avg rent (from backend or calculated) -->
              <td class="text-end">{{ formatCurrency(getTotalMonthlyRent(unit)) }}</td>
              
              <!-- Optional: Rent per sqft (from backend) -->
              <td v-if="showRentPerSqft" class="text-end">
                {{ formatCurrencyWithDecimals(getRentPerSqft(unit)) }}
              </td>
            </tr>
            
            <!-- Optional: Totals row -->
            <tr v-if="showTotals" class="table-active fw-bold">
              <td>Total</td>
              <td class="text-end">{{ formatCount(totalCount) }}</td>
              <td></td>
              <td></td>
              <td class="text-end">{{ formatCurrency(totalMonthlyRent) }}</td>
              <td v-if="showRentPerSqft"></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * UnitMixTable.vue - Reusable component for displaying unit mix data
 * 
 * WHAT: Displays unit type breakdown with counts, avg sqft, and avg rent
 * WHY: Centralizes unit mix table logic for subject properties and comps
 * HOW: Accepts array of unit mix objects via props, formats with Hyper UI styles
 * 
 * Props:
 * - unitMixData: Array of unit mix objects with fields:
 *   - unit_type: string (e.g., "1 Bed / 1 Bath")
 *   - unit_count: number
 *   - unit_avg_sqft: number
 *   - unit_avg_rent: number (monthly)
 *   - price_sqft: number (optional, rent per sqft)
 * - title: string - card header title
 * - loading: boolean - show loading spinner
 * - showRentPerSqft: boolean - show calculated rent/sqft column
 * - showTotals: boolean - show totals row at bottom
 */

import { computed } from 'vue'

// Props interface for strong typing
// All calculated fields come from backend model methods for consistency
interface UnitMixRow {
  unit_type?: string
  unit_count?: number
  unit_avg_sqft?: number
  unit_avg_rent?: number
  price_sqft?: number  // Backend calc: unit_avg_rent / unit_avg_sqft
  total_sqft?: number  // Backend calc: unit_count * unit_avg_sqft
  total_monthly_rent?: number  // Backend calc: unit_count * unit_avg_rent
  total_annual_rent?: number  // Backend calc: total_monthly_rent * 12
}

// Define props with defaults
const props = withDefaults(defineProps<{
  unitMixData: UnitMixRow[]
  title?: string
  loading?: boolean
  showRentPerSqft?: boolean
  showTotals?: boolean
}>(), {
  title: 'Unit Mix',
  loading: false,
  showRentPerSqft: true,
  showTotals: true,
})

// WHAT: Format count as integer with commas
// WHY: Consistency with other numeric displays
// HOW: Use toLocaleString for comma formatting
function formatCount(value: number | null | undefined): string {
  const num = Number(value ?? 0)
  return Number.isFinite(num) ? num.toLocaleString('en-US', { maximumFractionDigits: 0 }) : '-'
}

// WHAT: Format numeric value with commas
// WHY: Readability for large square footage numbers
// HOW: Use toLocaleString with no decimals
function formatNumber(value: number | null | undefined): string {
  const num = Number(value ?? 0)
  return Number.isFinite(num) ? num.toLocaleString('en-US', { maximumFractionDigits: 0 }) : '-'
}

// WHAT: Format currency as USD with no decimals
// WHY: Standard currency display for rent amounts
// HOW: Use toLocaleString with currency formatter
function formatCurrency(value: number | null | undefined): string {
  const num = Number(value ?? 0)
  return Number.isFinite(num) 
    ? num.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })
    : '-'
}

// WHAT: Format currency with 2 decimals (for rent per sqft)
// WHY: Rent per sqft needs decimal precision (e.g., $1.24/sqft)
// HOW: Use toLocaleString with 2 decimal places
function formatCurrencyWithDecimals(value: number | null | undefined): string {
  const num = Number(value ?? 0)
  return Number.isFinite(num) 
    ? num.toLocaleString('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 2, maximumFractionDigits: 2 })
    : '-'
}

// WHAT: Get total monthly rent for a unit type (from backend)
// WHY: All calculations come from backend model methods for audit consistency
// HOW: Return backend total_monthly_rent directly
function getTotalMonthlyRent(unit: UnitMixRow): number {
  return Number(unit.total_monthly_rent ?? 0)
}

// WHAT: Get rent per sqft for a unit (from backend)
// WHY: All calculations come from backend model methods for audit consistency
// HOW: Return backend price_sqft directly
function getRentPerSqft(unit: UnitMixRow): number {
  return Number(unit.price_sqft ?? 0)
}

// WHAT: Compute total unit count across all types
// WHY: Summary metric for totals row
// HOW: Sum all unit_count values
const totalCount = computed(() => {
  if (!props.unitMixData) return 0
  return props.unitMixData.reduce((sum, u) => sum + (Number(u.unit_count) || 0), 0)
})

// WHAT: Sum total monthly rent from backend calculations
// WHY: All calculations come from backend; frontend only sums for totals row
// HOW: Sum total_monthly_rent field from each unit type (backend calc: count × avg_rent)
const totalMonthlyRent = computed(() => {
  if (!props.unitMixData) return 0
  return props.unitMixData.reduce((sum, u) => sum + Number(u.total_monthly_rent || 0), 0)
})
</script>

<style scoped>
/**
 * Scoped styles for UnitMixTable
 * WHAT: Minimal overrides; rely on Hyper UI Bootstrap classes
 * WHY: Keeps component consistent with global theme
 * HOW: Only add custom styles if needed for specific layout adjustments
 */

/* Optional: add hover effect to rows for better UX */
.table tbody tr:hover {
  background-color: rgba(0, 0, 0, 0.02);
}

/* Ensure card title has proper weight */
.card-title {
  font-weight: 600;
}
</style>
