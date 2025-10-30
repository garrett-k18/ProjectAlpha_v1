<template>
  <!--
    DemographicsGrid.vue
    - Hyper UI/Bootstrap-styled card that displays a small, readable grid/table
      for community demographics around a subject property.
    - Columns represent distance rings (1, 3, 5 miles). Rows represent metrics.
    - For now this is populated with placeholder values; data wiring comes later.
  -->
  <div class="card">
    <!-- Header patterned after Hyper UI cards used across the dashboards -->
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title mb-0">Demographics</h4>
     </div>

    <!-- Body: compact table with responsive wrapper -->
    <div class="card-body">
      <!-- Optional loading placeholder rows -->
      <div v-if="loading" class="mb-2">
        <div v-for="n in 4" :key="n" class="placeholder-glow mb-1">
          <span class="placeholder col-12" style="height: 18px"></span>
        </div>
      </div>
      <div class="table-responsive">
        <table class="table table-sm align-middle mb-0">
          <thead>
            <tr>
              <th scope="col" class="w-50">Metric</th>
              <th scope="col" class="text-end">1 Mile</th>
              <th scope="col" class="text-end">3 Miles</th>
              <th scope="col" class="text-end">5 Miles</th>
            </tr>
          </thead>
          <tbody>
            <!-- Render each demographic row; use a deterministic key by metric name -->
            <tr v-for="r in rowsToRender" :key="r.metric">
              <td class="fw-semibold">{{ r.metric }}</td>
              <td class="text-end">{{ formatCell(r.one, r.formatter) }}</td>
              <td class="text-end">{{ formatCell(r.three, r.formatter) }}</td>
              <td class="text-end">{{ formatCell(r.five, r.formatter) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// ----------------------------------------------------------------------------------
// DemographicsGrid.vue (script setup, TypeScript)
// ----------------------------------------------------------------------------------
// We keep props for future data wiring to remain consistent with other tabs:
//  - row: the selected asset/loan row data
//  - productId: the loan/product identifier
// These are not used yet but will be leveraged to fetch/compute real values later.
// ----------------------------------------------------------------------------------
import { withDefaults, defineProps, computed } from 'vue'

// Props (kept optional and unused for now)
withDefaults(defineProps<{
  /** Full row for the current asset. Reserved for future data wiring. */
  row?: Record<string, any> | null
  /** Loan/product identifier. Reserved for future data wiring. */
  productId?: string | number | null
  /** Show loading placeholders (parent can toggle) */
  loading?: boolean
}>(), {
  row: null,
  productId: null,
  loading: false,
})

// Row shape for our grid. "formatter" determines how to render numeric values.
interface DemographicRow {
  /** Label for the metric, e.g. "Population" */
  metric: string
  /** 1-mile value */
  one: number | string | null
  /** 3-mile value */
  three: number | string | null
  /** 5-mile value */
  five: number | string | null
  /** Optional formatter: number, percent, currency, age, decimal1 */
  formatter?: 'number' | 'percent' | 'currency' | 'age' | 'decimal1'
}

// Placeholder dataset. Replace with AI/provider results later.
const sampleRows: DemographicRow[] = [
  // Core population + households
  { metric: 'Population', one: 12450, three: 48790, five: 112340, formatter: 'number' },
  { metric: 'Households', one: 4510, three: 17230, five: 40320, formatter: 'number' },
  { metric: 'Avg Household Size', one: 2.74, three: 2.68, five: 2.65, formatter: 'decimal1' },
  { metric: 'Median Age', one: 35.1, three: 36.4, five: 37.2, formatter: 'age' },

  // Income / housing economics
  { metric: 'Median Household Income', one: 64500, three: 61200, five: 59850, formatter: 'currency' },
  { metric: 'Median Home Value', one: 311000, three: 298500, five: 285000, formatter: 'currency' },
  { metric: 'Average Monthly Rent', one: 1550, three: 1495, five: 1450, formatter: 'currency' },

  // Education / tenure (removed some metrics per request)

  // Labor / growth
  { metric: 'Unemployment Rate', one: 0.047, three: 0.051, five: 0.053, formatter: 'percent' },
  { metric: '5-Year Population Growth', one: 0.061, three: 0.055, five: 0.049, formatter: 'percent' },

  // Density / daytime population
  { metric: 'Population Density (per sq mi)', one: 5120.3, three: 4285.8, five: 3721.6, formatter: 'decimal1' },
]

// rowsToRender is a computed wrapper in case we need to map/augment later.
const rowsToRender = computed<DemographicRow[]>(() => sampleRows)

// -------------------------
// Formatting helpers
// -------------------------
/**
 * formatCell
 * Formats a cell based on its formatter type. Returns a string for display.
 */
function formatCell(v: number | string | null, fmt: DemographicRow['formatter']): string {
  // Handle null/undefined gracefully
  if (v === null || typeof v === 'undefined' || v === '') return '-'

  // If a string is provided, return as-is
  if (typeof v === 'string') return v

  // Normalize formatter: default to 'number' when undefined
  const useFmt: Exclude<DemographicRow['formatter'], undefined> = (fmt ?? 'number')

  // Ensure we operate on a number for numeric renderers
  const num = Number(v)

  // For numbers, switch on formatter
  switch (useFmt) {
    case 'currency':
      // Use Intl.NumberFormat for currency formatting (USD). See MDN docs.
      return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(num)
    case 'percent':
      // Render as percentage with 1 decimal place (e.g., 0.345 => 34.5%)
      return `${(num * 100).toFixed(1)}%`
    case 'age':
      // Ages shown to 1 decimal place
      return `${num.toFixed(1)} yrs`
    case 'decimal1':
      // Generic 1-decimal numeric formatting (e.g., density, avg household size)
      return new Intl.NumberFormat('en-US', { maximumFractionDigits: 1, minimumFractionDigits: 1 }).format(num)
    case 'number':
    default:
      // Plain number with thousands separator, 0 decimals
      return new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 }).format(num)
  }
}
</script>

<style scoped>
/* Keep styles minimal and rely on utility classes from Bootstrap/Hyper UI */
</style>
