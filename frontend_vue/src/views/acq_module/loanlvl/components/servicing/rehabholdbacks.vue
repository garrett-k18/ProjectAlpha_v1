<template>
  <!--
    rehabholdbacks.vue
    - Reusable card for Rehab Holdbacks and related reserve/flag fields.
    - Accepts either a full `row` object or, if absent, fetches data by `productId`.
    - Uses Hyper UI/Bootstrap card styling with acquisitions-consistent header.

    NOTE: Backend model fields for these values are not yet confirmed in seller.py.
    This component will display values if present on the provided row using the
    following expected keys (snake_case to match Django conventions):
      - holdback_at_origination
      - current_holdback_remaining
      - holdback_disbursed
      - interest_reserves
      - dutch_flag
    If keys are missing, an empty state is shown. Once backend fields are added,
    this component will automatically render them when fetched by productId or
    passed in via the `row` prop.
  -->
  <div class="card h-100">
    <!-- Header -->
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Rehab Holdbacks</h4>
    </div>

    <!-- Body -->
    <div class="card-body pt-0">
      <div v-if="!hasAnyData" class="text-muted text-center py-3">
        No holdback/reserve data available.
      </div>

      <div v-else class="row g-3">
        <!-- Column 1 -->
        <div class="col-md-6">
          <!-- Holdback at Origination -->
          <div v-if="rowActive?.holdback_at_origination != null" class="mb-2">
            <small class="text-muted d-block">Holdback at Origination</small>
            <span class="fw-semibold text-dark">{{ formatCurrency(rowActive?.holdback_at_origination) }}</span>
          </div>

          <!-- Current Holdback Remaining -->
          <div v-if="rowActive?.current_holdback_remaining != null" class="mb-2">
            <small class="text-muted d-block">Current Holdback Remaining</small>
            <span class="fw-semibold text-dark">{{ formatCurrency(rowActive?.current_holdback_remaining) }}</span>
          </div>
        </div>

        <!-- Column 2 -->
        <div class="col-md-6">
          <!-- Holdback Disbursed -->
          <div v-if="rowActive?.holdback_disbursed != null" class="mb-2">
            <small class="text-muted d-block">Holdback Disbursed</small>
            <span class="fw-semibold text-dark">{{ formatCurrency(rowActive?.holdback_disbursed) }}</span>
          </div>

          <!-- Interest Reserves -->
          <div v-if="rowActive?.interest_reserves != null" class="mb-2">
            <small class="text-muted d-block">Interest Reserves</small>
            <span class="fw-semibold text-dark">{{ formatCurrency(rowActive?.interest_reserves) }}</span>
          </div>

          <!-- Dutch Flag -->
          <div v-if="rowActive?.dutch_flag != null" class="mb-2">
            <small class="text-muted d-block">Dutch Flag</small>
            <span v-if="rowActive?.dutch_flag" class="badge bg-info-subtle text-info">Yes</span>
            <span v-else class="badge bg-secondary-subtle text-secondary">No</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
/**
 * rehabholdbacks.vue
 * - Displays holdback/reserve fields for a loan (expected keys on row):
 *   holdback_at_origination, current_holdback_remaining, holdback_disbursed,
 *   interest_reserves, dutch_flag.
 * - Props allow passing a `row` directly or fetching by `productId`.
 * - Uses Hyper UI header pattern (h4.header-title) and consistent spacing (pt-0 body).
 */
import { defineComponent, computed, ref, watch } from 'vue'
import type { PropType } from 'vue'
import http from '@/lib/http'

export default defineComponent({
  name: 'RehabHoldbacks',
  props: {
    row: {
      type: Object as PropType<Record<string, any> | null>,
      default: null,
    },
    productId: {
      type: [String, Number] as PropType<string | number | null>,
      default: null,
    },
  },
  setup(props) {
    // Local fetched row
    const fetchedRow = ref<Record<string, any> | null>(null)

    // Active row from prop or fetch
    const rowActive = computed(() => props.row ?? fetchedRow.value)

    // Any presence check for display
    const hasAnyData = computed<boolean>(() => {
      const r = rowActive.value
      return !!(
        r && (
          r.holdback_at_origination != null ||
          r.current_holdback_remaining != null ||
          r.holdback_disbursed != null ||
          r.interest_reserves != null ||
          r.dutch_flag != null
        )
      )
    })

    // Fetch helper
    async function loadRowById(id: number) {
      try {
        const res = await http.get(`/acq/raw-data/by-id/${id}/`)
        fetchedRow.value = res.data && Object.keys(res.data).length ? res.data : null
        // eslint-disable-next-line no-console
        console.debug('[RehabHoldbacks] loaded row for', id)
      } catch (err) {
        // eslint-disable-next-line no-console
        console.warn('[RehabHoldbacks] failed to load row for', id, err)
        fetchedRow.value = null
      }
    }

    // Watch productId
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

    // Currency formatting (display-only, no decimals)
    const formatCurrency = (v: any) => {
      if (v != null && !isNaN(v)) {
        return new Intl.NumberFormat('en-US', {
          style: 'decimal',
          minimumFractionDigits: 0,
          maximumFractionDigits: 0,
        }).format(Number(v))
      }
      return 'N/A'
    }

    return { rowActive, hasAnyData, formatCurrency }
  },
})
</script>

<style scoped>
/* Rely on Hyper UI/Bootstrap utility classes for styling; no custom CSS needed */
</style>
