<template>
  <!--
    foreclosure.vue
    - Reusable card that displays foreclosure-related fields from SellerRawData.
    - Accepts either a full `row` object or, if absent, fetches data by `productId`.
    - Uses Hyper UI/Bootstrap card styling with acquisitions-consistent header.
  -->
  <div class="card h-100">
    <!-- Header follows acquisitions dashboard pattern: card-header + h4.header-title -->
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Foreclosure</h4>
    </div>

    <!-- Body uses pt-0 to align spacing with other cards -->
    <div class="card-body pt-0">
      <!-- Empty state when nothing is available to display -->
      <div v-if="!hasAnyData" class="text-muted text-center py-3">
        No foreclosure data available.
      </div>

      <!-- Details grid; each field shown only if present -->
      <div v-else class="row g-3">
        <!-- Column 1 -->
        <div class="col-md-6">
          <!-- FC Flag -->
          <div class="mb-2">
            <small class="text-muted d-block">Foreclosure Flag</small>
            <span v-if="rowActive?.fc_flag" class="badge bg-danger-subtle text-danger">Yes</span>
            <span v-else class="badge bg-secondary-subtle text-secondary">No</span>
          </div>

          <!-- First Legal Date -->
          <div v-if="rowActive?.fc_first_legal_date" class="mb-2">
            <small class="text-muted d-block">First Legal Date</small>
            <span class="fw-semibold text-dark">{{ formatDate(rowActive?.fc_first_legal_date) }}</span>
          </div>

          <!-- Referred Date -->
          <div v-if="rowActive?.fc_referred_date" class="mb-2">
            <small class="text-muted d-block">Referred Date</small>
            <span class="fw-semibold text-dark">{{ formatDate(rowActive?.fc_referred_date) }}</span>
          </div>
        </div>

        <!-- Column 2 -->
        <div class="col-md-6">
          <!-- Judgement Date -->
          <div v-if="rowActive?.fc_judgement_date" class="mb-2">
            <small class="text-muted d-block">Judgement Date</small>
            <span class="fw-semibold text-dark">{{ formatDate(rowActive?.fc_judgement_date) }}</span>
          </div>

          <!-- Scheduled Sale Date -->
          <div v-if="rowActive?.fc_scheduled_sale_date" class="mb-2">
            <small class="text-muted d-block">Scheduled Sale Date</small>
            <span class="fw-semibold text-dark">{{ formatDate(rowActive?.fc_scheduled_sale_date) }}</span>
          </div>

          <!-- Sale Date -->
          <div v-if="rowActive?.fc_sale_date" class="mb-2">
            <small class="text-muted d-block">Sale Date</small>
            <span class="fw-semibold text-dark">{{ formatDate(rowActive?.fc_sale_date) }}</span>
          </div>

          <!-- Starting Bid/Amount -->
          <div v-if="rowActive?.fc_starting != null" class="mb-2">
            <small class="text-muted d-block">Starting Amount</small>
            <span class="fw-semibold text-dark">{{ formatCurrency(rowActive?.fc_starting) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
/**
 * foreclosure.vue
 * - Displays foreclosure fields for a loan from SellerRawData:
 *   fc_flag, fc_first_legal_date, fc_referred_date, fc_judgement_date,
 *   fc_scheduled_sale_date, fc_sale_date, fc_starting.
 * - Props allow passing a `row` directly or fetching by `productId`.
 * - Uses Hyper UI header pattern (h4.header-title) and consistent spacing (pt-0 body).
 */
import { defineComponent, computed, ref, watch } from 'vue'
import type { PropType } from 'vue'
import http from '@/lib/http'

export default defineComponent({
  name: 'Foreclosure',
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

    const formatDate = (v: any) => (v ? new Date(v).toLocaleDateString('en-US') : 'N/A')

    // Derived flag indicating whether there is any foreclosure data to display
    const hasAnyData = computed<boolean>(() => {
      const r = rowActive.value
      return !!(
        r && (
          r.fc_flag != null ||
          r.fc_first_legal_date ||
          r.fc_referred_date ||
          r.fc_judgement_date ||
          r.fc_scheduled_sale_date ||
          r.fc_sale_date ||
          r.fc_starting != null
        )
      )
    })

    // Fetch helper that gets the row by id from the backend API
    async function loadRowById(id: number) {
      try {
        const res = await http.get(`/acq/raw-data/by-id/${id}/`)
        fetchedRow.value = res.data && Object.keys(res.data).length ? res.data : null
        // eslint-disable-next-line no-console
        console.debug('[Foreclosure] loaded row for', id)
      } catch (err) {
        // eslint-disable-next-line no-console
        console.warn('[Foreclosure] failed to load row for', id, err)
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
      formatDate,
    }
  },
})
</script>

<style scoped>
/* Rely on Hyper UI/Bootstrap utility classes for styling; no custom CSS needed */
</style>
