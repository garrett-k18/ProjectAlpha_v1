<template>
  <!--
    RentRollTable.vue
    WHAT: Reusable component to display subject or comparable property rent roll data
    WHY: Provides a clean, consistent table format for unit-level lease analysis
    HOW: Uses Hyper UI table-centered styling with Bootstrap classes for responsive layout
    
    Props:
    - rentRollData: Array of rent roll objects with unit-level lease details
    - title: string - card header title
    - loading: boolean - show loading spinner
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
        Loading rent roll data...
      </div>
      
      <!-- Empty state -->
      <div v-else-if="!rentRollData || rentRollData.length === 0" class="text-muted text-center py-3">
        No rent roll data available.
      </div>
      
      <!-- Data table (Hyper UI theme - table-centered) -->
      <div v-else class="table-responsive">
        <table class="table table-centered mb-0">
          <thead>
            <tr>
              <!-- Column headers for rent roll data -->
              <th>Tenant</th>
              <th>Unit</th>
              <th class="text-end">Sq Feet</th>
              <th class="text-end">Monthly Rent</th>
              <th class="text-end">Rent/Sqft</th>
              <th class="text-end">Annual Rent</th>
              <th class="text-end">Lease Start</th>
              <th class="text-end">Lease End</th>
              <th class="text-end">Term (Mo)</th>
              <th>Lease Type</th>
            </tr>
          </thead>
          <tbody>
            <!-- Loop through rent roll rows -->
            <tr v-for="(unit, index) in rentRollData" :key="`unit-${index}`">
              <!-- Tenant Name -->
              <td>{{ unit.tenant_name || '-' }}</td>
              
              <!-- Unit Name/Number -->
              <td>{{ unit.unit_name || '-' }}</td>
              
              <!-- Square Feet -->
              <td class="text-end">{{ formatNumber(unit.sq_feet) }}</td>
              
              <!-- Monthly Rent -->
              <td class="text-end">{{ formatCurrency(unit.rent) }}</td>
              
              <!-- Rent per Sqft (from backend calculation) -->
              <td class="text-end">{{ formatCurrencyWithDecimals(unit.price_per_sqft) }}</td>
              
              <!-- Annual Rent (from backend calculation) -->
              <td class="text-end">{{ formatCurrency(unit.annual_rent) }}</td>
              
              <!-- Lease Start Date -->
              <td class="text-end">{{ formatDate(unit.lease_start_date) }}</td>
              
              <!-- Lease End Date -->
              <td class="text-end">{{ formatDate(unit.lease_end_date) }}</td>
              
              <!-- Lease Term (months) -->
              <td class="text-end">{{ formatCount(unit.lease_term_months) }}</td>
              
              <!-- Lease Type -->
              <td>{{ unit.lease_type || '-' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * RentRollTable Component
 * 
 * WHAT: Displays rent roll (unit-level lease) data in a formatted table
 * WHY: Centralizes rent roll display logic for reuse across commercial analysis
 * HOW: Accepts rent roll array from parent, formats all fields using backend calculations
 * 
 * Props:
 * - rentRollData: Array<RentRollRow> - list of rent roll units
 * - title: string - card header title
 * - loading: boolean - loading state
 */

// Props interface for strong typing
// All calculated fields come from backend model methods for consistency
interface RentRollRow {
  id?: number
  tenant_name?: string
  unit_name?: string
  sq_feet?: number
  rent?: number
  lease_start_date?: string
  lease_end_date?: string
  lease_term_months?: number
  lease_type?: string
  rent_increase_pct?: number
  notes?: string
  // Backend-calculated fields
  price_per_sqft?: number  // Backend calc: rent / sq_feet
  annual_rent?: number  // Backend calc: rent * 12
  cam_per_sqft?: number  // Backend calc: cam_month / sq_feet
  annual_cam?: number  // Backend calc: cam_month * 12
}

// Define props with defaults
const props = withDefaults(defineProps<{
  rentRollData: RentRollRow[]
  title?: string
  loading?: boolean
}>(), {
  title: 'Rent Roll',
  loading: false,
})

// WHAT: Format count/integer with commas, no decimals
// WHY: Clean numeric display for counts and whole numbers
// HOW: Use toLocaleString with no fraction digits
function formatCount(value: number | null | undefined): string {
  const num = Number(value ?? 0)
  return Number.isFinite(num) ? num.toLocaleString('en-US', { maximumFractionDigits: 0 }) : '-'
}

// WHAT: Format number with commas (for sqft, etc)
// WHY: Readable numeric formatting
// HOW: Use toLocaleString
function formatNumber(value: number | null | undefined): string {
  const num = Number(value ?? 0)
  return Number.isFinite(num) ? num.toLocaleString('en-US') : '-'
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

// WHAT: Format date from backend (YYYY-MM-DD)
// WHY: Readable date display for lease dates
// HOW: Parse backend date string and format as locale date
function formatDate(value: string | null | undefined): string {
  if (!value) return '-'
  try {
    return new Date(value).toLocaleDateString()
  } catch {
    return String(value)
  }
}
</script>

<style scoped>
/**
 * Scoped styles for RentRollTable
 * WHAT: Minimal overrides; rely on Hyper UI Bootstrap classes
 * WHY: Keeps component consistent with global theme
 * HOW: Only add custom styles if needed for specific layout adjustments
 */

/* Hyper UI table-centered already provides clean styling */
/* Add any component-specific overrides here if needed */
</style>
