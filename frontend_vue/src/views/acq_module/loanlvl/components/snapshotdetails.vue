<template>
  <!-- Display property details horizontally using Bootstrap grid system from Hyper UI -->
  <div class="card">
    <div class="card-body">
      <h5 class="card-title mb-3">Property Details</h5>
      
      <!-- Horizontal layout using Bootstrap rows and columns -->
      <div class="row g-3">
        <!-- Combined address field displayed as two lines -->
        <div v-if="row?.street_address || row?.city || row?.state || row?.zip" class="col-md-6 col-lg-4">
          <div class="d-flex flex-column">
            <small class="text-muted fw-bold">ADDRESS</small>
            <div class="text-dark">
              <div v-if="row?.street_address">{{ row.street_address }}</div>
              <div v-if="row?.city || row?.state || row?.zip">{{ row.city }}, {{ row.state }} {{ row.zip }}</div>
            </div>
          </div>
        </div>
        
        <!-- Asset status field -->
        <div v-if="row?.asset_status" class="col-md-6 col-lg-4">
          <div class="d-flex flex-column">
            <small class="text-muted fw-bold">ASSET STATUS</small>
            <span class="text-dark">{{ row.asset_status }}</span>
          </div>
        </div>
        
        <!-- Current balance field -->
        <div v-if="row?.current_balance" class="col-md-6 col-lg-4">
          <div class="d-flex flex-column">
            <small class="text-muted fw-bold">CURRENT BALANCE</small>
            <span class="text-dark fw-semibold">{{ formattedBalance }}</span>
          </div>
        </div>
        
        <!-- Interest rate field -->
        <div v-if="row?.interest_rate" class="col-md-6 col-lg-4">
          <div class="d-flex flex-column">
            <small class="text-muted fw-bold">INTEREST RATE</small>
            <span class="text-dark">{{ formattedInterestRate }}</span>
          </div>
        </div>
        
        <!-- Next due date field -->
        <div v-if="row?.next_due_date" class="col-md-6 col-lg-4">
          <div class="d-flex flex-column">
            <small class="text-muted fw-bold">NEXT DUE DATE</small>
            <span class="text-dark">{{ formattedDueDate }}</span>
          </div>
        </div>
        
        <!-- Months delinquent field -->
        <div v-if="row?.months_dlq" class="col-md-6 col-lg-4">
          <div class="d-flex flex-column">
            <small class="text-muted fw-bold">MONTHS DLQ</small>
            <span class="text-dark">{{ row.months_dlq }}</span>
          </div>
        </div>
        
        <!-- Total debt field -->
        <div v-if="row?.total_debt" class="col-md-6 col-lg-4">
          <div class="d-flex flex-column">
            <small class="text-muted fw-bold">TOTAL DEBT</small>
            <span class="text-dark fw-semibold">{{ formattedTotalDebt }}</span>
          </div>
        </div>
        
        <!-- Seller ARV value field -->
        <div v-if="row?.seller_arv_value" class="col-md-6 col-lg-4">
          <div class="d-flex flex-column">
            <small class="text-muted fw-bold">SELLER ARV</small>
            <span class="text-dark fw-semibold">{{ formattedArvValue }}</span>
          </div>
        </div>
        
        <!-- Seller as-is value field -->
        <div v-if="row?.seller_asis_value" class="col-md-6 col-lg-4">
          <div class="d-flex flex-column">
            <small class="text-muted fw-bold">SELLER AS-IS</small>
            <span class="text-dark fw-semibold">{{ formattedAsIsValue }}</span>
          </div>
        </div>
      </div>
      
      <!-- Fallback message if no data is provided -->
      <div v-if="!hasAnyData" class="text-muted text-center py-3">
        No property details available.
      </div>
    </div>
  </div>
</template>

<script lang="ts">
/**
 * SnapshotDetails.vue
 * Purpose: A reusable Vue component to display key property details from a SellerRawData object.
 * This component is designed to be modular and can be imported into any Vue template where property details are needed.
 * It uses Bootstrap card components for styling, adhering to the Hyper UI library's conventions.
 * Props:
 * - row: An object containing SellerRawData fields. This should be passed from the parent component.
 * Computed Properties:
 * - formattedBalance: Formats the current_balance field as US currency using Intl.NumberFormat.
 * Best Practices:
 * - Gracefully handles missing data with v-if directives to avoid errors.
 * - Uses optional chaining (?.) to safely access nested properties.
 * - Ensures modularity by defining a clear interface and avoiding side effects.
 */

import { defineComponent, computed, ref, watch } from 'vue'
import type { PropType } from 'vue'
// Centralized Axios instance (Vite baseURL proxies to Django in dev)
import http from '@/lib/http'

export default defineComponent({
  name: 'SnapshotDetails', // Component name for easy identification in Vue DevTools
  props: {
    /**
     * The data row from SellerRawData, containing fields like street_address, city, state, zip, current_balance.
     * Type is Record<string, any> for flexibility, but ideally should match the SellerRawData model defined in the backend.
     * Default is null to handle cases where no data is provided.
     */
    row: {
      type: Object as PropType<Record<string, any> | null>,
      default: null
    },
    /**
     * Optional identifier for the SellerRawData row. When provided and `row` is
     * not passed (e.g., full-page navigation), this component will fetch the row
     * from the backend for self-sufficiency, mirroring how other tabs handle
     * full-page vs modal contexts.
     */
    productId: {
      type: [String, Number] as PropType<string | number | null>,
      default: null,
    }
  },
  setup(props) {
    /**
     * Helper function to format currency values consistently.
     * Uses Intl.NumberFormat with US locale and USD currency for proper formatting.
     * Returns 'N/A' if value is not available or null.
     */
    const formatCurrency = (value: any) => {
      if (value != null && !isNaN(value)) {
        return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value)
      }
      return 'N/A'
    }

    /**
     * Helper function to format date values consistently.
     * Returns formatted date string or 'N/A' if not available.
     */
    const formatDate = (dateValue: any) => {
      if (dateValue) {
        return new Date(dateValue).toLocaleDateString('en-US')
      }
      return 'N/A'
    }

    /**
     * Helper function to format percentage values consistently.
     * Returns formatted percentage string or 'N/A' if not available.
     */
    const formatPercentage = (value: any) => {
      if (value != null && !isNaN(value)) {
        return `${(value * 100).toFixed(4)}%`
      }
      return 'N/A'
    }

    // Local state for fallback-fetched row (used only when prop `row` is not provided)
    const fetchedRow = ref<Record<string, any> | null>(null)

    /**
     * Normalize access to the active row: prefer explicit prop `row` (modal),
     * otherwise fallback to `fetchedRow` (full-page). Expose as `row` so the
     * existing template bindings remain unchanged.
     */
    const row = computed<Record<string, any> | null>(() => props.row ?? fetchedRow.value)

    // Computed properties for formatting various fields
    const formattedBalance = computed(() => formatCurrency(row.value?.current_balance))
    const formattedTotalDebt = computed(() => formatCurrency(row.value?.total_debt))
    const formattedArvValue = computed(() => formatCurrency(row.value?.seller_arv_value))
    const formattedAsIsValue = computed(() => formatCurrency(row.value?.seller_asis_value))
    const formattedInterestRate = computed(() => formatPercentage(row.value?.interest_rate))
    const formattedDueDate = computed(() => formatDate(row.value?.next_due_date))

    /**
     * Computed property to check if any data is available for display.
     * Used to determine whether to show the fallback message.
     */
    const hasAnyData = computed(() => {
      const r = row.value
      return !!(r && (
        r.street_address ||
        r.city ||
        r.state ||
        r.zip ||
        r.asset_status ||
        r.current_balance ||
        r.interest_rate ||
        r.next_due_date ||
        r.months_dlq ||
        r.total_debt ||
        r.seller_arv_value ||
        r.seller_asis_value
      ))
    })

    /**
     * Fetch helper: load a SellerRawData row by id. Returns {} when not found; we
     * normalize to null for simpler checks.
     */
    async function loadRowById(id: number) {
      try {
        const res = await http.get(`/acq/raw-data/by-id/${id}/`)
        fetchedRow.value = res.data && Object.keys(res.data).length ? res.data : null
        // eslint-disable-next-line no-console
        console.debug('[SnapshotDetails] loaded row for', id)
      } catch (err) {
        // eslint-disable-next-line no-console
        console.warn('[SnapshotDetails] failed to load row for', id, err)
        fetchedRow.value = null
      }
    }

    // Trigger fallback fetch on productId change when no prop `row` is provided
    watch(() => props.productId, (raw) => {
      const id = raw != null ? Number(raw) : NaN
      if (!props.row && Number.isFinite(id)) {
        loadRowById(id)
      }
    }, { immediate: true })

    return {
      row,
      formattedBalance,
      formattedTotalDebt,
      formattedArvValue,
      formattedAsIsValue,
      formattedInterestRate,
      formattedDueDate,
      hasAnyData
    }
  }
})
</script>