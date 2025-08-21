<template>
  <!-- Display property details horizontally using Bootstrap grid system from Hyper UI -->
  <div class="card">
    <div class="card-body d-flex flex-column">
      <!-- Header removed as requested -->
      
      <!-- Horizontal layout using Bootstrap rows and columns -->
      <div class="row g-3 align-items-stretch flex-grow-1">
        <!-- Column 1: Address + Current Balance + Total Debt + Seller As-Is + Seller ARV (stacked vertically, evenly spaced) -->
        <div v-if="hasCol1Data" class="col-md-6 col-lg-4 d-flex flex-column h-100">
          <div ref="col1Stack" class="d-flex flex-column justify-content-between gap-2 flex-fill h-100 pb-3 column-stack">
            <!-- Address block (label + value grouped as one item for even spacing) -->
            <div class="d-flex flex-column align-items-center text-center">
              <small class="text-muted fw-normal">Address</small>
              <div class="text-dark fw-semibold">
                <div v-if="row?.street_address">{{ row.street_address }}</div>
                <div v-if="row?.city || row?.state || row?.zip">{{ row.city }}, {{ row.state }} {{ row.zip }}</div>
              </div>
            </div>

            <!-- Stacked under Address: Current Balance -->
            <div v-if="row?.current_balance" class="d-flex flex-column align-items-center text-center">
              <small class="text-muted fw-normal">Current Balance</small>
              <span class="text-dark fw-semibold">{{ formattedBalance }}</span>
            </div>

            <!-- Stacked under Address: Total Debt -->
            <div v-if="row?.total_debt" class="d-flex flex-column align-items-center text-center">
              <small class="text-muted fw-normal">Total Debt</small>
              <span class="text-dark fw-semibold">{{ formattedTotalDebt }}</span>
            </div>

            <!-- Stacked under Address: Seller As-Is -->
            <div v-if="row?.seller_asis_value" class="d-flex flex-column align-items-center text-center">
              <small class="text-muted fw-normal">Seller As-Is</small>
              <span class="text-dark fw-semibold">{{ formattedAsIsValue }}</span>
            </div>

            <!-- Stacked under Address: Seller ARV -->
            <div v-if="row?.seller_arv_value" class="d-flex flex-column align-items-center text-center">
              <small class="text-muted fw-normal">Seller ARV</small>
              <span class="text-dark fw-semibold">{{ formattedArvValue }}</span>
            </div>
          </div>
        </div>
        
        <!-- Column 2: Asset Status + Months DLQ + Interest Rate + Next Due Date (stacked vertically) -->
        <div v-if="hasCol2Data" class="col-md-6 col-lg-4 d-flex flex-column h-100">
          <div ref="col2Stack" class="d-flex flex-column justify-content-between gap-2 flex-fill h-100 pb-3 column-stack">
            <div v-if="row?.asset_status" class="d-flex flex-column align-items-center text-center">
              <small class="text-muted fw-normal">Asset Status</small>
              <span :class="['badge', assetStatusBadgeClass, 'rounded-pill', 'm-0', 'mt-1', 'align-self-center']">{{ row.asset_status }}</span>
            </div>
            <div v-if="row?.months_dlq" class="d-flex flex-column align-items-center text-center">
              <small class="text-muted fw-normal">Months DLQ</small>
              <span class="text-dark fw-semibold">{{ row.months_dlq }}</span>
            </div>
            <div v-if="row?.interest_rate" class="d-flex flex-column align-items-center text-center">
              <small class="text-muted fw-normal">Interest Rate</small>
              <span class="text-dark fw-semibold">{{ formattedInterestRate }}</span>
            </div>
            <div v-if="row?.next_due_date" class="d-flex flex-column align-items-center text-center">
              <small class="text-muted fw-normal">Next Due Date</small>
              <span class="text-dark fw-semibold">{{ formattedDueDate }}</span>
            </div>
            <div v-if="row?.mod_maturity_date || row?.current_maturity_date || row?.original_maturity_date" class="d-flex flex-column align-items-center text-center">
              <small class="text-muted fw-normal">Maturity Date</small>
              <span class="text-dark fw-semibold">{{ formattedMaturityDate }}</span>
            </div>
          </div>
        </div>

        <!-- Column 3: Origination Date + Original Balance + FC Flag + BK Flag (stacked vertically, evenly spaced) -->
        <div v-if="hasCol3Data" class="col-md-6 col-lg-4 d-flex flex-column h-100">
          <div ref="col3Stack" class="d-flex flex-column justify-content-between gap-2 flex-fill h-100 pb-3 column-stack">
            <div v-if="row?.origination_date" class="d-flex flex-column align-items-center text-center">
              <small class="text-muted fw-normal">Origination Date</small>
              <span class="text-dark fw-semibold">{{ formattedOriginationDate }}</span>
            </div>
            <div v-if="row?.original_balance" class="d-flex flex-column align-items-center text-center">
              <small class="text-muted fw-normal">Original Balance</small>
              <span class="text-dark fw-semibold">{{ formattedOriginalBalance }}</span>
            </div>
            <div v-if="row?.fc_flag !== undefined && row?.fc_flag !== null" class="d-flex flex-column align-items-center text-center">
              <small class="text-muted fw-normal">FC Flag</small>
              <span :class="['badge', flagBadgeClass(row.fc_flag), 'rounded-pill', 'm-0', 'mt-1', 'align-self-center']">{{ formatFlag(row.fc_flag) }}</span>
            </div>
            <div v-if="row?.bk_flag !== undefined && row?.bk_flag !== null" class="d-flex flex-column align-items-center text-center">
              <small class="text-muted fw-normal">BK Flag</small>
              <span :class="['badge', flagBadgeClass(row.bk_flag), 'rounded-pill', 'm-0', 'mt-1', 'align-self-center']">{{ formatFlag(row.bk_flag) }}</span>
            </div>
          </div>
        </div>
        
        <!-- Current Balance moved under Address column -->
        <!-- Interest Rate moved under Column 2 -->
        
        <!-- Next Due Date moved under Column 2 -->
        
        <!-- Months DLQ moved under Column 2 -->
        
        <!-- Total Debt moved under Address column -->
        
        <!-- Seller ARV moved under Address column -->
        
        <!-- Seller As-Is moved under Address column -->
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

import { defineComponent, computed, ref, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
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
        // Grouped number with 0 decimals and NO currency symbol
        return new Intl.NumberFormat('en-US', {
          style: 'decimal',
          minimumFractionDigits: 0,
          maximumFractionDigits: 0,
        }).format(Number(value))
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
        // Interest rate with 3 decimals; expects decimal input (e.g., 0.0416)
        return new Intl.NumberFormat('en-US', {
          style: 'percent',
          minimumFractionDigits: 3,
          maximumFractionDigits: 3,
        }).format(Number(value))
      }
      return 'N/A'
    }

    /**
     * Helper to format boolean/flag-like values consistently to Yes/No.
     * Accepts booleans, 'Y'/'N', 'yes'/'no', 1/0. Returns 'N/A' if empty.
     */
    const formatFlag = (value: any) => {
      if (value === undefined || value === null || value === '') return 'N/A'
      // Normalize to string for broad matching
      const v = String(value).trim().toLowerCase()
      if (v === 'y' || v === 'yes' || v === 'true' || v === '1') return 'Yes'
      if (v === 'n' || v === 'no' || v === 'false' || v === '0') return 'No'
      if (value === true) return 'Yes'
      if (value === false) return 'No'
      // Fallback: any other non-empty value considered truthy
      return 'Yes'
    }

    /**
     * Map asset status values to Bootstrap 5.3 subtle badge classes used by Hyper UI.
     * Returns a pair of classes like 'bg-success-subtle text-success'. Defaults to secondary.
     */
    const assetStatusBadgeClass = computed<string>(() => {
      const raw = String(row.value?.asset_status ?? '').trim().toLowerCase()
      // Lookup map for common statuses (extend as needed)
      const map: Record<string, string> = {
        'performing': 'bg-success-subtle text-success',
        'current': 'bg-success-subtle text-success',
        'reperforming': 'bg-info-subtle text-info',
        'non-performing': 'bg-danger-subtle text-danger',
        'delinquent': 'bg-warning-subtle text-warning',
        'default': 'bg-danger-subtle text-danger',
        'foreclosure': 'bg-danger-subtle text-danger',
        'reo': 'bg-warning-subtle text-warning',
        'bankruptcy': 'bg-danger-subtle text-danger',
      }
      return map[raw] || 'bg-secondary-subtle text-secondary'
    })

    /**
     * Compute badge class for Yes/No-like flags (e.g., FC, BK).
     * Truthy => danger subtle (attention). Falsy => success subtle (clear).
     */
    const flagBadgeClass = (value: any): string => {
      const f = formatFlag(value)
      if (f === 'Yes') return 'bg-danger-subtle text-danger'
      if (f === 'No') return 'bg-success-subtle text-success'
      return 'bg-secondary-subtle text-secondary'
    }

    // Local state for fallback-fetched row (used only when prop `row` is not provided)
    const fetchedRow = ref<Record<string, any> | null>(null)

    // Refs to column stacks for dynamic height syncing
    const col1Stack = ref<HTMLElement | null>(null)
    const col2Stack = ref<HTMLElement | null>(null)
    const col3Stack = ref<HTMLElement | null>(null)

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
    // Prefer modified maturity date, then current, then original (whichever is available)
    const formattedMaturityDate = computed(() => {
      const raw = row.value?.mod_maturity_date ?? row.value?.current_maturity_date ?? row.value?.original_maturity_date
      return formatDate(raw)
    })
    const formattedOriginationDate = computed(() => formatDate(row.value?.origination_date))
    const formattedOriginalBalance = computed(() => formatCurrency(row.value?.original_balance))

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
        r.seller_asis_value ||
        r.mod_maturity_date || r.current_maturity_date || r.original_maturity_date ||
        r.origination_date ||
        r.original_balance ||
        r.fc_flag ||
        r.bk_flag
      ))
    })

    /**
     * Column guard: render Column 1 when ANY of its fields exist.
     * This prevents one field from depending on another (e.g., Address missing).
     * Fields covered: address parts, current_balance, total_debt, seller_asis_value, seller_arv_value.
     */
    const hasCol1Data = computed(() => {
      const r = row.value
      return !!(r && (
        r.street_address || r.city || r.state || r.zip ||
        r.current_balance || r.total_debt ||
        r.seller_asis_value || r.seller_arv_value
      ))
    })

    /**
     * Column guard: render Column 2 when ANY of its fields exist.
     * Fields covered: asset_status, months_dlq, interest_rate, next_due_date.
     */
    const hasCol2Data = computed(() => {
      const r = row.value
      return !!(r && (
        r.asset_status || r.months_dlq || r.interest_rate || r.next_due_date ||
        r.mod_maturity_date || r.current_maturity_date || r.original_maturity_date
      ))
    })

    /**
     * Column guard: render Column 3 when ANY of its fields exist.
     * Fields: origination_date, original_balance, fc_flag, bk_flag.
     */
    const hasCol3Data = computed(() => {
      const r = row.value
      return !!(r && (
        r.origination_date || r.original_balance || r.fc_flag || r.bk_flag
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

    /**
     * Dynamically sync the heights of both column stacks to the tallest one
     * at md+ breakpoints so the last item can anchor to the bottom.
     * Clears heights on smaller screens where columns stack vertically.
     */
    let ro1: ResizeObserver | null = null
    let ro2: ResizeObserver | null = null
    let ro3: ResizeObserver | null = null

    const applySyncHeights = () => {
      const isMdUp = typeof window !== 'undefined' && window.matchMedia('(min-width: 768px)').matches
      const els: HTMLElement[] = [col1Stack.value, col2Stack.value, col3Stack.value].filter(Boolean) as HTMLElement[]
      if (els.length === 0) return
      // Reset before measuring to avoid compounding
      els.forEach(el => { el.style.minHeight = '' })
      if (!isMdUp || els.length < 2) return
      const max = Math.max(...els.map(el => el.offsetHeight))
      els.forEach(el => { el.style.minHeight = `${max}px` })
    }

    onMounted(() => {
      // Observe size changes of each stack and window resizes
      if (typeof ResizeObserver !== 'undefined') {
        ro1 = new ResizeObserver(() => applySyncHeights())
        ro2 = new ResizeObserver(() => applySyncHeights())
        ro3 = new ResizeObserver(() => applySyncHeights())
        if (col1Stack.value) ro1.observe(col1Stack.value)
        if (col2Stack.value) ro2.observe(col2Stack.value)
        if (col3Stack.value) ro3.observe(col3Stack.value)
      }
      window.addEventListener('resize', applySyncHeights)
      // Next tick to ensure DOM is rendered before syncing
      nextTick(() => applySyncHeights())
    })

    onBeforeUnmount(() => {
      window.removeEventListener('resize', applySyncHeights)
      if (ro1 && col1Stack.value) ro1.unobserve(col1Stack.value)
      if (ro2 && col2Stack.value) ro2.unobserve(col2Stack.value)
      if (ro3 && col3Stack.value) ro3.unobserve(col3Stack.value)
      ro1 = null
      ro2 = null
      ro3 = null
    })

    return {
      row,
      formattedBalance,
      formattedTotalDebt,
      formattedArvValue,
      formattedAsIsValue,
      formattedInterestRate,
      formattedDueDate,
      formattedMaturityDate,
      formattedOriginationDate,
      formattedOriginalBalance,
      hasAnyData,
      hasCol1Data,
      hasCol2Data,
      hasCol3Data,
      col1Stack,
      col2Stack,
      col3Stack,
      formatFlag,
      assetStatusBadgeClass,
      flagBadgeClass
    }
  }
})
</script>

<style scoped>
/* column-stack: flex column that can consume available height in the column */
.column-stack { /* container for field blocks in a column */
  display: flex; /* ensure flex, even if utility classes change */
  flex-direction: column; /* vertical stacking of field groups */
  min-height: 100%; /* let it grow with its parent column height */
}

</style>