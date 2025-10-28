<template>
  <!--
    Widgets (Acquisitions dashboard)
    Renders four top-level tiles showing aggregated pool metrics for the
    currently selected Seller + Trade. Pulls live data from the backend
    via a single API call to /acq/summary/pool/<seller_id>/<trade_id>/.

    Design notes:
    - Uses the same card/tile markup style already present in the page
      for visual consistency (Hyper UI theme styles should still apply).
    - Shows a lightweight loading state per tile while fetching.
    - Component is modular so other widget groups can be added later.
  -->
  <b-row class="g-2 mb-1">
    <!-- Assets count tile -->
    <b-col xl="3" lg="6">
      <div class="card tilebox-one mb-0">
        <div class="card-body pt-3 pb-2 px-3">
          <!-- Grid of items icon to suggest count of assets -->
          <i class="uil uil-apps float-end" aria-hidden="true"></i>
          <h6 class="text-uppercase mt-0">Assets</h6>
          <h2 class="my-2" id="assets-count">
            <span v-if="loading">...</span>
            <span v-else class="fs-3 fs-lg-1">{{ assetsFormatted }}</span>
          </h2>
        </div>
      </div>
    </b-col>

    <!-- Current Balance tile -->
    <b-col xl="3" lg="6">
      <div class="card tilebox-one mb-0">
        <div class="card-body pt-3 pb-2 px-3">
          <i class="uil uil-dollar-sign float-end" aria-hidden="true"></i>
          <h6 class="text-uppercase mt-0">Current Balance</h6>
          <h2 class="my-2 d-flex align-items-baseline" id="current-balance">
            <span v-if="loading">...</span>
            <span v-else class="fs-3 fs-lg-1">{{ currencyCompact(currentBalanceNum) }}</span>
            <span class="text-muted d-inline-flex align-items-baseline ms-2 fs-4 fst-italic">
              <span :class="['me-1', ltvClass(upbLtvPct)]">{{ loading ? '...' : percentInt(upbLtvPct) }}</span>
              <span class="text-nowrap">LTV</span>
            </span>
          </h2>
        </div>
      </div>
    </b-col>

    <!-- Total Debt tile -->
    <b-col xl="3" lg="6">
      <div class="card tilebox-one mb-0">
        <div class="card-body pt-3 pb-2 px-3">
          <i class="uil uil-chart-line float-end" aria-hidden="true"></i>
          <h6 class="text-uppercase mt-0">Total Debt</h6>
          <h2 class="my-2 d-flex align-items-baseline" id="total-debt">
            <span v-if="loading">...</span>
            <span v-else class="fs-3 fs-lg-1">{{ currencyCompact(totalDebtNum) }}</span>
            <span class="text-muted d-inline-flex align-items-baseline ms-2 fs-4 fst-italic">
              <span :class="['me-1', ltvClass(tdLtvPct)]">{{ loading ? '...' : percentInt(tdLtvPct) }}</span>
              <span class="text-nowrap">TDTV</span>
            </span>
          </h2>
        </div>
      </div>
    </b-col>

    <!-- Seller As-is Value tile -->
    <b-col xl="3" lg="6">
      <div class="card tilebox-one mb-0">
        <div class="card-body pt-3 pb-2 px-3">
          <i class="uil uil-home float-end" aria-hidden="true"></i>
          <h6 class="text-uppercase mt-0">Seller As-is Value</h6>
          <h2 class="my-2" id="seller-asis-value">
            <span v-if="loading">...</span>
            <span v-else class="fs-3 fs-lg-1">{{ currencyCompact(sellerAsIsValueNum) }}</span>
          </h2>
        </div>
      </div>
    </b-col>
  </b-row>
</template>

<script lang="ts">
// Widgets component logic (Acquisitions dashboard)
// Docs reviewed:
// - Pinia Core Concepts: https://pinia.vuejs.org/core-concepts/
// - Vue Watchers: https://vuejs.org/guide/essentials/watchers.html
// - Axios Instance (local http.ts): https://axios-http.com/docs/instance
import { defineComponent, ref, watch, computed } from 'vue'
import { useAcqSelectionsStore } from '@/stores/acqSelections'
import { storeToRefs } from 'pinia'
import http from '@/lib/http'

// Response shape returned by backend get_pool_summary
interface PoolSummaryResponse {
  assets: number
  current_balance: string | number // Django may serialize Decimal as string; keep flexible
  total_debt: string | number
  seller_asis_value: string | number
  upb_ltv_percent?: string | number
  td_ltv_percent?: string | number
}

export default defineComponent({
  name: 'Widgets',
  setup() {
    // ---------------------------------------------------------------------------
    // Selection state from Pinia store (seller and trade IDs)
    // ---------------------------------------------------------------------------
    const acqStore = useAcqSelectionsStore()
    const { selectedSellerId, selectedTradeId } = storeToRefs(acqStore)

    // ---------------------------------------------------------------------------
    // Local reactive state for the four metrics and loading flag
    // ---------------------------------------------------------------------------
    const loading = ref<boolean>(false)
    const assets = ref<number>(0)
    const currentBalanceNum = ref<number>(0)
    const totalDebtNum = ref<number>(0)
    const sellerAsIsValueNum = ref<number>(0)
    const upbLtvPct = ref<number>(0)
    const tdLtvPct = ref<number>(0)

    // ---------------------------------------------------------------------------
    // Formatting utilities
    // ---------------------------------------------------------------------------
    const assetsFormatted = computed<string>(() => new Intl.NumberFormat().format(assets.value))

    function currency(n: number): string {
      // Return a USD currency formatted string with 2 decimals
      // Note: We keep formatting localized so caller can replace if needed
      try {
        return new Intl.NumberFormat(undefined, { style: 'currency', currency: 'USD', minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(n)
      } catch (_e) {
        // Fallback minimal formatting
        return `$${(n || 0).toFixed(2)}`
      }
    }

    // Percent formatter (e.g., 12.34%)
    function percent(n: number): string {
      try {
        return `${(n ?? 0).toFixed(2)}%`
      } catch (_e) {
        return `${Number(n || 0).toFixed(2)}%`
      }
    }

    // Integer percentage formatter (no decimals)
    function percentInt(n: number): string {
      const v = Math.round(Number(n || 0))
      return `${v}%`
    }

    // LTV color thresholds: >100 red, 90-100 yellow, <90 green
    function ltvClass(n: number): string {
      const v = Number(n || 0)
      if (v > 100) return 'text-danger'
      if (v >= 90) return 'text-warning'
      return 'text-success'
    }

    /**
     * currencyCompact
     * Formats a number as compact USD with finance-style suffixes.
     * Examples: 1_200_000 -> "$1.2MM"; 300_000 -> "$300k"; 950 -> "$950".
     * - Uses "MM" for millions, "B" for billions, and "k" for thousands.
     * - Preserves sign for negative amounts.
     */
    function currencyCompact(n: number): string {
      const sign = n < 0 ? '-' : ''
      const abs = Math.abs(n || 0)

      // Billions
      if (abs >= 1_000_000_000) {
        const val = Math.round((abs / 1_000_000_000) * 10) / 10 // 1 decimal
        return `${sign}$${val}B`
      }
      // Millions
      if (abs >= 1_000_000) {
        const val = Math.round((abs / 1_000_000) * 10) / 10 // 1 decimal
        return `${sign}$${val}MM`
      }
      // Thousands
      if (abs >= 1_000) {
        const val = Math.round((abs / 1_000) * 10) / 10 // 1 decimal
        // If integer after rounding (e.g., 300.0), omit .0 for cleaner look
        const str = Number.isInteger(val) ? String(val.toFixed(0)) : String(val)
        return `${sign}$${str}k`
      }
      // For small numbers, show regular currency with 0 decimals
      try {
        return `${sign}${new Intl.NumberFormat(undefined, { style: 'currency', currency: 'USD', minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(abs)}`
      } catch (_e) {
        return `${sign}$${Math.round(abs)}`
      }
    }

    // ---------------------------------------------------------------------------
    // Fetch function: calls backend one-shot aggregate API
    // ---------------------------------------------------------------------------
    async function fetchSummary(): Promise<void> {
      // Require both seller and trade IDs
      if (!selectedSellerId.value || !selectedTradeId.value) {
        assets.value = 0
        currentBalanceNum.value = 0
        totalDebtNum.value = 0
        sellerAsIsValueNum.value = 0
        upbLtvPct.value = 0
        tdLtvPct.value = 0
        return
      }

      loading.value = true
      try {
        const sid = selectedSellerId.value as number
        const tid = selectedTradeId.value as number
        // Leading slash ensures correct join with baseURL
        const resp = await http.get<PoolSummaryResponse>(`/acq/summary/pool/${sid}/${tid}/`)
        const data = resp.data
        // Parse possible string Decimals to numbers safely
        assets.value = Number(data.assets || 0)
        currentBalanceNum.value = Number((data.current_balance as any) || 0)
        totalDebtNum.value = Number((data.total_debt as any) || 0)
        sellerAsIsValueNum.value = Number((data.seller_asis_value as any) || 0)
        upbLtvPct.value = Number((data.upb_ltv_percent as any) || 0)
        tdLtvPct.value = Number((data.td_ltv_percent as any) || 0)
      } catch (e) {
        // Non-fatal: clear values and keep UI stable
        console.error('[Widgets] fetch summary failed', e)
        assets.value = 0
        currentBalanceNum.value = 0
        totalDebtNum.value = 0
        sellerAsIsValueNum.value = 0
        upbLtvPct.value = 0
        tdLtvPct.value = 0
      } finally {
        loading.value = false
      }
    }

    // Watch for changes in selection and fetch (run immediately too)
    watch([selectedSellerId, selectedTradeId], fetchSummary, { immediate: true })

    return {
      // state
      loading,
      assetsFormatted,
      currentBalanceNum,
      totalDebtNum,
      sellerAsIsValueNum,
      upbLtvPct,
      tdLtvPct,
      // methods
      currency,
      percent,
      percentInt,
      ltvClass,
      currencyCompact,
    }
  },
})
</script>

<style scoped>
/* Minimal: keep theme defaults, but normalize the inner row spacing so
   all tiles visually align regardless of suffix (LTV/TDTV) presence. */
.tilebox-one .card-body h6.text-uppercase.mt-0 { margin-bottom: 0.25rem; }
.tilebox-one .card-body h2.my-2 {
  display: flex;
  align-items: baseline;
  min-height: 2.25rem;   /* ensure equal value-row height */
  margin-top: 0.5rem;    /* consistent spacing from title */
  margin-bottom: 0.25rem;
  white-space: nowrap;   /* prevent wrapping that creates uneven height */
}
.tilebox-one .card-body h2.my-2 span { white-space: nowrap; }
</style>
