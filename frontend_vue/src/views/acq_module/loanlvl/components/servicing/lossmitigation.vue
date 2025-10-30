<template>
  <!--
    lossmitigation.vue
    - Reusable card that displays loan modification (loss mitigation) fields from SellerRawData.
    - Accepts either a full `row` object or, if absent, fetches data by `productId`.
    - Uses Hyper UI/Bootstrap card styling with acquisitions-consistent header.
  -->
  <div class="card h-100">
    <!-- Header follows acquisitions dashboard pattern: card-header + h4.header-title -->
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Loss Mitigation</h4>
    </div>

    <!-- Body uses pt-0 to align spacing with other cards -->
    <div class="card-body pt-0">
      <!-- Empty state when nothing is available to display -->
      <div v-if="!hasAnyData" class="text-muted text-center py-3">
        No modification data available.
      </div>

      <!-- Details grid; each field shown only if present -->
      <div v-else class="row g-3">
        <!-- Column 1 -->
        <div class="col-md-6">
          <!-- Modification Flag -->
          <div class="mb-2">
            <small class="text-muted d-block">Modification Flag</small>
            <span v-if="rowActive?.mod_flag" class="badge bg-info-subtle text-info">Yes</span>
            <span v-else class="badge bg-secondary-subtle text-secondary">No</span>
          </div>

          <!-- Modification Date -->
          <div v-if="rowActive?.mod_date" class="mb-2">
            <small class="text-muted d-block">Modification Date</small>
            <span class="fw-semibold text-dark">{{ formatDate(rowActive?.mod_date) }}</span>
          </div>

          <!-- Modification Maturity Date -->
          <div v-if="rowActive?.mod_maturity_date" class="mb-2">
            <small class="text-muted d-block">Modified Maturity Date</small>
            <span class="fw-semibold text-dark">{{ formatDate(rowActive?.mod_maturity_date) }}</span>
          </div>
        </div>

        <!-- Column 2 -->
        <div class="col-md-6">
          <!-- Modification Term (months) -->
          <div v-if="rowActive?.mod_term != null" class="mb-2">
            <small class="text-muted d-block">Modified Term</small>
            <span class="fw-semibold text-dark">{{ rowActive?.mod_term }} months</span>
          </div>

          <!-- Modification Rate (%) -->
          <div v-if="rowActive?.mod_rate != null" class="mb-2">
            <small class="text-muted d-block">Modified Rate</small>
            <span class="fw-semibold text-dark">{{ formatPercent(rowActive?.mod_rate) }}</span>
          </div>

          <!-- Modification Initial Balance -->
          <div v-if="rowActive?.mod_initial_balance != null" class="mb-2">
            <small class="text-muted d-block">Modified Initial Balance</small>
            <span class="fw-semibold text-dark">{{ formatCurrency(rowActive?.mod_initial_balance) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
/**
 * lossmitigation.vue
 * - Displays modification/loss mitigation fields for a loan from SellerRawData:
 *   mod_flag, mod_date, mod_maturity_date, mod_term, mod_rate, mod_initial_balance.
 * - Props allow passing a `row` directly or fetching by `productId`.
 * - Uses Hyper UI header pattern (h4.header-title) and consistent spacing (pt-0 body).
 */
import { defineComponent, computed, ref, watch } from 'vue'
import type { PropType } from 'vue'
import http from '@/lib/http'

export default defineComponent({
  name: 'LossMitigation',
  props: {
    // Full record if already available upstream
    row: {
      type: Object as PropType<Record<string, any> | null>,
      default: null,
    },
    // Product ID used to fetch the row from API when `row` is not provided
    productId: {
      type: [String, Number] as PropType<string | number | null>,
      default: null,
    },
  },
  setup(props) {
    // Local state to store a fetched row as a fallback
    const fetchedRow = ref<Record<string, any> | null>(null)

    // Active row: prefer the `row` prop; otherwise use `fetchedRow`
    const rowActive = computed(() => props.row ?? fetchedRow.value)

    // Formatting helpers for display-only fields
    const formatCurrency = (v: any) => {
      // Convert to number if possible and format without decimals for consistency
      if (v != null && !isNaN(v)) {
        return new Intl.NumberFormat('en-US', {
          style: 'decimal',
          minimumFractionDigits: 0,
          maximumFractionDigits: 0,
        }).format(Number(v))
      }
      return 'N/A'
    }

    const formatPercent = (v: any) => {
      // Backend likely stores decimal form (e.g., 0.04125 => 4.125%)
      if (v != null && !isNaN(v)) {
        return new Intl.NumberFormat('en-US', {
          style: 'percent',
          minimumFractionDigits: 3,
          maximumFractionDigits: 3,
        }).format(Number(v))
      }
      return 'N/A'
    }

    const formatDate = (v: any) => (v ? new Date(v).toLocaleDateString('en-US') : 'N/A')

    // Derived flag indicating whether there is any modification data to display
    const hasAnyData = computed<boolean>(() => {
      const r = rowActive.value
      return !!(
        r && (
          r.mod_flag != null ||
          r.mod_date ||
          r.mod_maturity_date ||
          r.mod_term != null ||
          r.mod_rate != null ||
          r.mod_initial_balance != null
        )
      )
    })

    // Fetch helper that gets the row by id from the backend API
    async function loadRowById(id: number) {
      try {
        const res = await http.get(`/acq/raw-data/by-id/${id}/`)
        fetchedRow.value = res.data && Object.keys(res.data).length ? res.data : null
        // eslint-disable-next-line no-console
        console.debug('[LossMitigation] loaded row for', id)
      } catch (err) {
        // eslint-disable-next-line no-console
        console.warn('[LossMitigation] failed to load row for', id, err)
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
      formatCurrency,
      formatPercent,
      formatDate,
    }
  },
})
</script>

<style scoped>
/* Rely on Hyper UI/Bootstrap utility classes for styling; no custom CSS needed */
</style>
