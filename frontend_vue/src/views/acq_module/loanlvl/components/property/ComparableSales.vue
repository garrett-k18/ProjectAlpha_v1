<template>
  <!--
    ComparableSales.vue
    - Displays recent comparable property sales in the area
    - Shows address, sale date, price, beds/baths, sq ft, and price per sq ft
    - Responsive table with hover effects
    - Uses Bootstrap/Hyper UI card pattern
  -->
  <div class="card">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title mb-0">Comparable Sales</h4>
      <button class="btn btn-sm btn-light">
        <i class="mdi mdi-refresh"></i> Refresh
      </button>
    </div>
    <div class="card-body">
      <div class="table-responsive">
        <table class="table table-sm table-hover align-middle mb-0">
          <thead class="table-light">
            <tr>
              <th>Address</th>
              <th>Sale Date</th>
              <th class="text-end">Sale Price</th>
              <th class="text-end">Beds/Baths</th>
              <th class="text-end">Sq Ft</th>
              <th class="text-end">$/Sq Ft</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(comp, idx) in comparableSales" :key="idx">
              <td>
                <span class="fw-semibold">{{ comp.address }}</span>
                <br>
                <small class="text-muted">{{ comp.distance }} mi away</small>
              </td>
              <td>{{ comp.saleDate }}</td>
              <td class="text-end fw-semibold">{{ formatCurrency(comp.salePrice) }}</td>
              <td class="text-end">{{ comp.beds }}/{{ comp.baths }}</td>
              <td class="text-end">{{ formatNumber(comp.sqFt) }}</td>
              <td class="text-end">
                <span class="badge bg-light text-dark">{{ formatCurrency(comp.pricePerSqFt) }}</span>
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
 * ComparableSales.vue
 * 
 * Displays recent comparable property sales in the area.
 * Shows key metrics for comparison: price, size, price per sq ft.
 * TODO: Wire to backend comps API when available.
 */
import { computed, withDefaults } from 'vue'

// Props definition
const props = withDefaults(defineProps<{
  row?: Record<string, any> | null
  assetId?: string | number | null
}>(), {
  row: null,
  assetId: null,
})

// Comparable Sales - Recent sales in the area
const comparableSales = computed(() => [
  {
    address: '912 11th St',
    distance: 0.2,
    saleDate: '01/15/2024',
    salePrice: 265000,
    beds: 3,
    baths: 2,
    sqFt: 1200,
    pricePerSqFt: 221
  },
  {
    address: '1105 Oak Ave',
    distance: 0.4,
    saleDate: '12/08/2023',
    salePrice: 248000,
    beds: 2,
    baths: 1,
    sqFt: 950,
    pricePerSqFt: 261
  },
  {
    address: '808 Pine St',
    distance: 0.6,
    saleDate: '11/22/2023',
    salePrice: 275000,
    beds: 3,
    baths: 2,
    sqFt: 1350,
    pricePerSqFt: 204
  }
])

// Formatting helpers
function formatCurrency(value: number | null | undefined): string {
  if (value == null) return '—'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value)
}

function formatNumber(value: number | null | undefined): string {
  if (value == null) return '—'
  return new Intl.NumberFormat('en-US').format(value)
}
</script>
