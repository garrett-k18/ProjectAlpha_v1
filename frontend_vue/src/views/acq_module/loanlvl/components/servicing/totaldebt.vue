<template>
  <!--
    TotalDebt.vue
    - Reusable card that displays Total Debt and its breakdown.
    - Accepts either a full row object via prop `row` or, if absent, fetches it by `productId`.
    - Styling follows Hyper UI/Bootstrap conventions, matching acquisitions dashboard headers.
  -->
  <div class="card h-100">
    <!-- Header uses acquisitions dashboard pattern -->
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Total Debt</h4>
    </div>

    <div class="card-body pt-0">
      <!-- Empty state when there is no data to show -->
      <div v-if="!hasAnyData" class="text-muted text-center py-3">
        No debt data available.
      </div>

      <div v-else class="row g-3">
        <!-- Total row -->
        <div class="col-12">
          <div class="d-flex justify-content-between align-items-center border rounded p-2 bg-light">
            <span class="text-muted">Total Debt</span>
            <span class="fw-semibold text-dark">{{ formatCurrency(totalDebtDisplay) }}</span>
          </div>
          <small v-if="showsComputedNote" class="text-muted d-block mt-1">
            Computed from breakdown fields because backend total_debt is not provided.
          </small>
          <small v-else-if="showsMismatchNote" class="text-muted d-block mt-1">
            Note: Breakdown sum differs from backend-provided total.
          </small>
        </div>

        <!-- Breakdown grid (2 columns on md+) -->
        <div class="col-md-6" v-if="rowActive?.accrued_note_interest != null">
          <small class="text-muted d-block">Accrued Note Interest</small>
          <span class="fw-semibold text-dark">{{ formatCurrency(rowActive?.accrued_note_interest) }}</span>
        </div>

        <div class="col-md-6" v-if="rowActive?.accrued_default_interest != null">
          <small class="text-muted d-block">Accrued Default Interest</small>
          <span class="fw-semibold text-dark">{{ formatCurrency(rowActive?.accrued_default_interest) }}</span>
        </div>

        <div class="col-md-6" v-if="rowActive?.escrow_balance != null">
          <small class="text-muted d-block">Escrow Balance</small>
          <span class="fw-semibold text-dark">{{ formatCurrency(rowActive?.escrow_balance) }}</span>
        </div>

        <div class="col-md-6" v-if="rowActive?.escrow_advance != null">
          <small class="text-muted d-block">Escrow Advance</small>
          <span class="fw-semibold text-dark">{{ formatCurrency(rowActive?.escrow_advance) }}</span>
        </div>

        <div class="col-md-6" v-if="rowActive?.recoverable_corp_advance != null">
          <small class="text-muted d-block">Recoverable Corp Advance</small>
          <span class="fw-semibold text-dark">{{ formatCurrency(rowActive?.recoverable_corp_advance) }}</span>
        </div>

        <div class="col-md-6" v-if="rowActive?.late_fees != null">
          <small class="text-muted d-block">Late Fees</small>
          <span class="fw-semibold text-dark">{{ formatCurrency(rowActive?.late_fees) }}</span>
        </div>

        <div class="col-md-6" v-if="rowActive?.other_fees != null">
          <small class="text-muted d-block">Other Fees</small>
          <span class="fw-semibold text-dark">{{ formatCurrency(rowActive?.other_fees) }}</span>
        </div>

        <div class="col-md-6" v-if="rowActive?.suspense_balance != null">
          <small class="text-muted d-block">Suspense Balance</small>
          <span class="fw-semibold text-dark">{{ formatCurrency(rowActive?.suspense_balance) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
/**
 * TotalDebt.vue
 * - Displays Total Debt for a loan, with a breakdown of contributing amounts from SellerRawData.
 * - Props:
 *    - row?: a full SellerRawData-like record
 *    - productId?: the identifier used to fetch the row when `row` is not supplied
 * - Behavior:
 *    - If `row` is not provided but `productId` is, component fetches `/acq/raw-data/by-id/<id>/`.
 *    - Total displays `row.total_debt` if present; otherwise, it's computed from breakdown fields.
 * - Styling:
 *    - Uses Hyper UI/Bootstrap classes with `h4.header-title` in card-header to match acquisitions dashboard.
 */
import { defineComponent, computed, ref, watch } from 'vue'
import type { PropType } from 'vue'
import http from '@/lib/http' // centralized Axios instance used across the app

export default defineComponent({
  name: 'TotalDebt',
  props: {
    // `row` contains all fields needed to render without additional fetches
    row: {
      type: Object as PropType<Record<string, any> | null>,
      default: null,
    },
    // `productId` used to fetch when `row` is not supplied
    productId: {
      type: [String, Number] as PropType<string | number | null>,
      default: null,
    },
  },
  setup(props) {
    // Holds data fetched by id if `row` is not provided by the parent
    const fetchedRow = ref<Record<string, any> | null>(null)

    // Active row prioritizes the directly provided `row`; falls back to fetched data
    const rowActive = computed(() => props.row ?? fetchedRow.value)

    // Helper: parse a numeric-like value safely into a number or NaN
    const toNumber = (v: any): number => (v != null && !isNaN(v) ? Number(v) : NaN)

    // Calculate the breakdown sum used for a computed total when `total_debt` isn't provided
    const breakdownSum = computed<number>(() => {
      const r = rowActive.value
      if (!r) return 0
      const parts = [
        toNumber(r.accrued_note_interest),
        toNumber(r.accrued_default_interest),
        toNumber(r.escrow_balance),
        toNumber(r.escrow_advance),
        toNumber(r.recoverable_corp_advance),
        toNumber(r.late_fees),
        toNumber(r.other_fees),
        toNumber(r.suspense_balance),
      ]
      return parts.reduce((acc, n) => (Number.isFinite(n) ? acc + n : acc), 0)
    })

    // Raw total provided by backend, if any
    const backendTotal = computed<number | null>(() => {
      const r = rowActive.value
      const n = toNumber(r?.total_debt)
      return Number.isFinite(n) ? n : null
    })

    // Value to display as the total debt
    const totalDebtDisplay = computed<number>(() => backendTotal.value ?? breakdownSum.value)

    // Whether we are showing a computed note due to missing backend total
    const showsComputedNote = computed<boolean>(() => backendTotal.value == null && breakdownSum.value > 0)

    // Whether the sum of breakdown differs materially from backend provided total
    const showsMismatchNote = computed<boolean>(() => {
      if (backendTotal.value == null) return false
      const diff = Math.abs(backendTotal.value - breakdownSum.value)
      return diff >= 1 // 1 unit tolerance to avoid noise
    })

    // Simple currency formatter for display-only values (no decimals per platform standard)
    const formatCurrency = (v: any) => {
      const n = toNumber(v)
      if (Number.isFinite(n)) {
        return new Intl.NumberFormat('en-US', {
          style: 'decimal',
          minimumFractionDigits: 0,
          maximumFractionDigits: 0,
        }).format(n)
      }
      return 'N/A'
    }

    // True if there is anything worth showing
    const hasAnyData = computed<boolean>(() => {
      const r = rowActive.value
      return !!(
        r && (
          r.total_debt != null ||
          r.accrued_note_interest != null ||
          r.accrued_default_interest != null ||
          r.escrow_balance != null ||
          r.escrow_advance != null ||
          r.recoverable_corp_advance != null ||
          r.late_fees != null ||
          r.other_fees != null ||
          r.suspense_balance != null
        )
      )
    })

    // Fetch helper: loads the row by product id
    async function loadRowById(id: number) {
      try {
        const res = await http.get(`/acq/raw-data/by-id/${id}/`)
        fetchedRow.value = res.data && Object.keys(res.data).length ? res.data : null
        // eslint-disable-next-line no-console
        console.debug('[TotalDebt] loaded row for', id)
      } catch (err) {
        // eslint-disable-next-line no-console
        console.warn('[TotalDebt] failed to load row for', id, err)
        fetchedRow.value = null
      }
    }

    // Watch for productId changes; fetch when appropriate
    watch(
      () => props.productId,
      (raw) => {
        const id = raw != null ? Number(raw) : NaN
        if (!props.row && Number.isFinite(id)) {
          loadRowById(id)
        } else if (!Number.isFinite(id)) {
          fetchedRow.value = null
        }
      },
      { immediate: true }
    )

    return {
      rowActive,
      hasAnyData,
      totalDebtDisplay,
      showsComputedNote,
      showsMismatchNote,
      formatCurrency,
    }
  },
})
</script>

<style scoped>
/* Rely on Hyper UI/Bootstrap utility classes for layout and typography */
</style>
