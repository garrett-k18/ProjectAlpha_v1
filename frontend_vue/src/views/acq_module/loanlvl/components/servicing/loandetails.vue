<template>
    <!--
      LoanDetails.vue
      - Reusable card to display SellerRawData loan details.
      - Accepts either a full row object via prop `row` or, if absent, fetches it by `productId`.
      - Uses Bootstrap/Hyper UI card styling.
    -->
    <div class="card h-100">
      <div class="d-flex card-header justify-content-between align-items-center">
        <h4 class="header-title">Loan Details</h4>
      </div>

      <div class="card-body pt-0">
        <!-- Nothing to show -->
        <div v-if="!hasAnyData" class="text-muted text-center py-3">
          No loan details available.
        </div>

        <!-- Fields grid -->
        <div v-else class="row g-3">
          <!-- Column 1 -->
          <div class="col-md-6">
            <div v-if="rowActive?.current_balance" class="mb-2">
              <small class="text-muted d-block">Current Balance</small>
              <span class="fw-semibold text-dark">{{ formatCurrency(rowActive?.current_balance) }}</span>
            </div>
  
            <div v-if="rowActive?.deferred_balance" class="mb-2">
              <small class="text-muted d-block">Deferred Balance</small>
              <span class="fw-semibold text-dark">{{ formatCurrency(rowActive?.deferred_balance) }}</span>
            </div>
  
            <div v-if="rowActive?.interest_rate != null" class="mb-2">
              <small class="text-muted d-block">Interest Rate</small>
              <span class="fw-semibold text-dark">{{ formatPercent(rowActive?.interest_rate) }}</span>
            </div>
  
            <div v-if="rowActive?.default_rate != null" class="mb-2">
              <small class="text-muted d-block">Default Rate</small>
              <span class="fw-semibold text-dark">{{ formatPercent(rowActive?.default_rate) }}</span>
            </div>
          </div>
  
          <!-- Column 2 -->
          <div class="col-md-6">
            <div v-if="rowActive?.next_due_date" class="mb-2">
              <small class="text-muted d-block">Next Due Date</small>
              <span class="fw-semibold text-dark">{{ formatDate(rowActive?.next_due_date) }}</span>
            </div>
  
            <div v-if="rowActive?.last_paid_date" class="mb-2">
              <small class="text-muted d-block">Last Paid Date</small>
              <span class="fw-semibold text-dark">{{ formatDate(rowActive?.last_paid_date) }}</span>
            </div>
  
            <div v-if="rowActive?.current_maturity_date" class="mb-2">
              <small class="text-muted d-block">Current Maturity Date</small>
              <span class="fw-semibold text-dark">{{ formatDate(rowActive?.current_maturity_date) }}</span>
            </div>
  
            <div v-if="rowActive?.current_term != null" class="mb-2">
              <small class="text-muted d-block">Current Term</small>
              <span class="fw-semibold text-dark">{{ rowActive?.current_term }} months</span>
            </div>
          </div>
  
          <!-- Full-width rows -->
          <div class="col-12">
            <div class="row g-3">
              <div class="col-md-6" v-if="rowActive?.months_dlq != null">
                <small class="text-muted d-block">Months DLQ</small>
                <span class="fw-semibold text-dark">{{ rowActive?.months_dlq }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script lang="ts">
  /**
   * LoanDetails.vue
   * - Displays SellerRawData loan details
   * - Props: row (optional), productId (optional)
   * - If row is missing and productId is provided, fetches the row by id from backend
   */
  import { defineComponent, computed, ref, watch } from 'vue'
  import type { PropType } from 'vue'
  import http from '../../../../../lib/http' // centralized Axios instance
  
  export default defineComponent({
    name: 'LoanDetails',
    props: {
      row: {
        type: Object as PropType<Record<string, any> | null>,
        default: null
      },
      productId: {
        type: [String, Number] as PropType<string | number | null>,
        default: null
      }
    },
    setup(props) {
      // Fallback-fetched row when only productId is provided
      const fetchedRow = ref<Record<string, any> | null>(null)
  
      // Active row: prefer explicit prop row, fallback to fetchedRow
      const rowActive = computed(() => props.row ?? fetchedRow.value)
  
      // Simple formatters for display-only values
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
  
      const formatPercent = (v: any) => {
        if (v != null && !isNaN(v)) {
          // Back-end stores e.g. 0.0416 for 4.160%
          return new Intl.NumberFormat('en-US', {
            style: 'percent',
            minimumFractionDigits: 3,
            maximumFractionDigits: 3,
          }).format(Number(v))
        }
        return 'N/A'
      }
  
      const formatDate = (v: any) => {
        if (v) return new Date(v).toLocaleDateString('en-US')
        return 'N/A'
      }
  
      // Derived flag: is there anything to show?
      const hasAnyData = computed<boolean>(() => {
        const r = rowActive.value
        return !!(r && (
          r.current_balance ||
          r.deferred_balance ||
          r.interest_rate != null ||
          r.default_rate != null ||
          r.next_due_date ||
          r.last_paid_date ||
          r.current_maturity_date ||
          r.current_term != null ||
          r.months_dlq != null
        ))
      })
  
      // Fetch helper
      async function loadRowById(id: number) {
        try {
          const res = await http.get(`/acq/raw-data/by-id/${id}/`)
          fetchedRow.value = res.data && Object.keys(res.data).length ? res.data : null
          // eslint-disable-next-line no-console
          console.debug('[LoanDetails] loaded row for', id)
        } catch (err) {
          // eslint-disable-next-line no-console
          console.warn('[LoanDetails] failed to load row for', id, err)
          fetchedRow.value = null
        }
      }
  
      // Watch productId; fetch when not provided a row
      watch(() => props.productId, (raw) => {
        const id = raw != null ? Number(raw) : NaN
        if (!props.row && Number.isFinite(id)) {
          loadRowById(id)
        } else if (!Number.isFinite(id)) {
          fetchedRow.value = null
        }
      }, { immediate: true })
  
      return {
        rowActive,
        hasAnyData,
        formatCurrency,
        formatPercent,
        formatDate,
      }
    }
  })
  </script>
  
  <style scoped>
  /* No custom CSS needed; rely on Hyper UI/Bootstrap classes */
  </style>