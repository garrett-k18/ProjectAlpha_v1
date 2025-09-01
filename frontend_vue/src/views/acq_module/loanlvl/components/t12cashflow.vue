<template>
  <!--
    t12cashflow.vue
    - Reusable Trailing 12 Months Cash Flow card component.
    - Renders a compact 3-row grid using a Bootstrap table for consistency:
      Row 1: Header periods [0..N-1] (default N=13 for periods 0..12)
      Row 2: Payment Type Flag per period (0 = none, 1 = partial, 2 = full)
      Row 3: Payment Amount per period (display formatted)
    - Accepts optional props to drive data; if not provided, shows zeros and computed flags.
    - Uses Hyper UI/Bootstrap card pattern with acquisitions header style.
  -->
  <div class="card h-100">
    <!-- Header: title left, As-of date right -->
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title mb-0">T12 Cash Flow</h4>
      <div class="text-muted small">
        <span class="me-1">As of:</span>
        <strong>{{ asOfDisplay }}</strong>
      </div>
    </div>

    <div class="card-body pt-0">
      <!-- Legend / note -->
      <div class="d-flex justify-content-start align-items-center mb-2">
        <div class="small text-muted">
          <span class="me-3"><span class="legend-dot bg-secondary"></span> 0 = None</span>
          <span class="me-3"><span class="legend-dot bg-warning"></span> 1 = Partial</span>
          <span><span class="legend-dot bg-success"></span> 2 = Full</span>
        </div>
      </div>

      <!-- Compact grid using a table for clean alignment -->
      <div class="table-responsive">
        <table class="table table-sm mb-0 align-middle">
          <thead>
            <tr>
              <th class="text-muted fw-normal">Period</th>
              <th v-for="p in periodIndices" :key="`h-${p}`" class="text-center">{{ p }}</th>
            </tr>
          </thead>
          <tbody>
            <!-- Row 2: Payment Type Flag -->
            <tr>
              <td class="text-muted">Payment Type</td>
              <td v-for="p in periodIndices" :key="`f-${p}`" class="text-center">
                <!-- Use colored dot + numeric flag for clarity -->
                <span :class="flagDotClass(computedFlags[p])" class="flag-dot me-1"></span>
                <span class="fw-semibold">{{ computedFlags[p] }}</span>
              </td>
            </tr>

            <!-- Row 3: Payment Amount -->
            <tr>
              <td class="text-muted">Amount</td>
              <td v-for="p in periodIndices" :key="`a-${p}`" class="text-center">
                <span class="fw-semibold">{{ formatCurrency(paymentAmountsSafe[p]) }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
/**
 * t12cashflow.vue
 * - Displays a 3-row T12 cash flow grid.
 * - Props:
 *   - periodsCount: how many periods to show (default 13 => periods 0..12 inclusive)
 *   - paymentAmounts: amount per period; missing values default to 0
 *   - paymentFlags: optional precomputed flags per period (0 none, 1 partial, 2 full)
 *   - fullAmount: optional; when paymentFlags not provided, classify as 2 if amount >= fullAmount (with tolerance), else 1 for positive amounts
 *   - asOf: date string to show in header; defaults to today if not provided
 *
 * - Notes:
 *   - This component is display-only and framework-agnostic. It does not fetch data.
 *   - For future integration, pass arrays from an API or parent computed props.
 */
import { defineComponent, computed } from 'vue'
import type { PropType } from 'vue'

export default defineComponent({
  name: 'T12CashFlow',
  props: {
    periodsCount: { type: Number, default: 13 },
    paymentAmounts: { type: Array as PropType<Array<number | null | undefined>>, default: () => [] },
    paymentFlags: { type: Array as PropType<Array<0 | 1 | 2 | null | undefined>>, default: () => [] },
    fullAmount: { type: Number as PropType<number | null>, default: null },
    asOf: { type: [String, Date] as PropType<string | Date | null>, default: null },
  },
  setup(props) {
    // Generate [0..N-1]
    const periodIndices = computed<number[]>(() => Array.from({ length: Math.max(0, props.periodsCount) }, (_, i) => i))

    // Display as-of date; fallback to today if not provided
    const asOfDisplay = computed<string>(() => {
      const val = props.asOf ? new Date(props.asOf) : new Date()
      return isNaN(val.getTime()) ? 'N/A' : val.toLocaleDateString('en-US')
    })

    // Ensure we have an amount per index; fallback to 0
    const paymentAmountsSafe = computed<number[]>(() => {
      const out: number[] = []
      const arr = props.paymentAmounts ?? []
      for (let i = 0; i < (props.periodsCount || 0); i++) {
        const raw = arr[i]
        out.push(typeof raw === 'number' && isFinite(raw) ? raw : 0)
      }
      return out
    })

    // Compute flags if not provided or missing; rules:
    // - 0 if amount <= 0
    // - 2 if fullAmount provided and amount >= fullAmount - tolerance
    // - else 1 for positive non-full amounts
    const computedFlags = computed<(0 | 1 | 2)[]>(() => {
      const provided = props.paymentFlags ?? []
      const out: (0 | 1 | 2)[] = []
      const tol = 0.005 // tolerance for floating rounding when comparing to full
      const full = typeof props.fullAmount === 'number' && isFinite(props.fullAmount) ? props.fullAmount : null
      for (let i = 0; i < (props.periodsCount || 0); i++) {
        const given = provided[i]
        if (given === 0 || given === 1 || given === 2) {
          out.push(given)
          continue
        }
        const amt = paymentAmountsSafe.value[i]
        if (!amt || amt <= 0) {
          out.push(0)
        } else if (full != null && amt >= full - tol) {
          out.push(2)
        } else {
          out.push(1)
        }
      }
      return out
    })

    // Formatting helpers
    const formatCurrency = (v: any) => {
      if (v != null && !isNaN(v)) {
        return new Intl.NumberFormat('en-US', {
          style: 'decimal',
          minimumFractionDigits: 0,
          maximumFractionDigits: 0,
        }).format(Number(v))
      }
      return '0'
    }

    // Map flag value to a small colored dot class
    const flagDotClass = (flag: 0 | 1 | 2) => {
      switch (flag) {
        case 2:
          return 'bg-success'
        case 1:
          return 'bg-warning'
        default:
          return 'bg-secondary'
      }
    }

    return {
      periodIndices,
      asOfDisplay,
      paymentAmountsSafe,
      computedFlags,
      formatCurrency,
      flagDotClass,
    }
  },
})
</script>

<style scoped>
/* Legend colored dot */
.legend-dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; }
/* Flag dot in table cells */
.flag-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; }
</style>
