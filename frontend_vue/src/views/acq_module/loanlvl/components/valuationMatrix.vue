<template>
  <!-- Valuation matrix card; overflow hidden to respect modal border radius -->
  <div class="card overflow-hidden">
    <div class="card-body">
      <!-- Responsive table; keep mb-0 so card padding controls vertical rhythm -->
      <div class="table-responsive mb-0">
        <table class="table table-bordered table-centered mb-0">
          <thead class="table-light">
            <tr>
              <th>Source</th>
              <th>As-Is</th>
              <th>ARV</th>
              <th>Rehab Est.</th>
            </tr>
          </thead>
          <tbody>
            <!-- Render each row using props for modularity -->
            <tr v-for="(r, idx) in rows" :key="idx">
              <td>{{ r.outlet }}</td>
              <td>{{ r.price }}</td>
              <td>
                <div class="progress-w-percent mb-0">
                  <span class="progress-value">{{ r.stock }} </span>
                  <div class="progress progress-sm">
                    <div
                      class="progress-bar"
                      :class="`bg-${r.progressVariant}`"
                      role="progressbar"
                      :style="{ width: `${r.progressPercent}%` }"
                      :aria-valuenow="r.progressPercent"
                      aria-valuemin="0"
                      aria-valuemax="100"
                    ></div>
                  </div>
                </div>
              </td>
              <td>{{ r.revenue }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// valuationMatrix.vue
// Purpose: Reusable Hyper UI/Bootstrap card with a valuation table.
// Notes: Designed to be data-agnostic; accepts a list of rows but ships with
// sample defaults that match the previous inline markup.

import { withDefaults, defineProps } from 'vue'

/**
 * Row model for the pricing/stock table.
 * - outlet: display name of the outlet/location
 * - price: formatted price string (e.g., "$139.58")
 * - stock: numeric stock units displayed next to the progress bar
 * - progressPercent: percent width for the progress bar (0-100)
 * - progressVariant: Bootstrap color variant for the progress bar
 * - revenue: formatted revenue string (e.g., "$1,89,547")
 */
export type PricingRow = {
  outlet: string
  price: string
  stock: number
  progressPercent: number
  progressVariant: 'primary' | 'secondary' | 'success' | 'danger' | 'warning' | 'info' | 'dark'
  revenue: string
}

const props = withDefaults(defineProps<{ rows?: PricingRow[] }>(), {
  rows: () => [
    {
      outlet: 'Internal Reconciled',
      price: '$139.58',
      stock: 478,
      progressPercent: 56,
      progressVariant: 'success',
      revenue: '$1,89,547',
    },
    {
      outlet: 'Seller Values',
      price: '$149.99',
      stock: 73,
      progressPercent: 16,
      progressVariant: 'danger',
      revenue: '$87,245',
    },
    {
      outlet: 'Local Agent',
      price: '$135.87',
      stock: 781,
      progressPercent: 72,
      progressVariant: 'success',
      revenue: '$5,87,478',
    },
    {
      outlet: '3rd Party BPO',
      price: '$159.89',
      stock: 815,
      progressPercent: 89,
      progressVariant: 'success',
      revenue: '$55,781',
    },
  ],
})

// Expose rows for template (kept for clarity; script setup exposes props automatically)
const { rows } = props
</script>

<style scoped>
/* Uses Bootstrap/Hyper UI built-ins only; no custom styles necessary. */
</style>
