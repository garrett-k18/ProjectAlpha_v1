// src/stores/stateSummaries.ts
// Pinia store for state-level aggregations (counts and sums) per seller+trade
// Documentation reviewed:
// - Pinia Core Concepts: https://pinia.vuejs.org/core-concepts/
// - Axios Instances & Interceptors: https://axios-http.com/docs/instance
// - Vue Reactivity (ref/computed): https://vuejs.org/guide/essentials/reactivity-fundamentals.html
// - ApexCharts Vue (for consumers): https://apexcharts.com/docs/vue-charts/
//
// Purpose:
// - Centralize fetching/caching of backend state summaries so multiple components
//   can consume consistent, reactive data without duplicating HTTP logic.
// - Enforce data siloing by requiring both sellerId and tradeId.
// - Provide derived getters (e.g., Top 10 states by count) ready for charts.

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import http from '@/lib/http'

// ----------------------------------------------------------------------------
// Types: shape of backend responses
// ----------------------------------------------------------------------------
export interface StateCountRow {
  // Two-letter state code (normalized to uppercase by backend model save hook)
  state: string
  // Integer count of rows in this state for the selection
  count: number
}

export interface SumCurrentBalanceRow { state: string; sum_current_balance: string }
export interface SumTotalDebtRow { state: string; sum_total_debt: string }
export interface SumSellerAsIsValueRow { state: string; sum_seller_asis_value: string }

// Internal normalized sums as number for charting convenience
interface StateSums {
  currentBalance: Map<string, number>
  totalDebt: Map<string, number>
  sellerAsIs: Map<string, number>
}

// Cached payload per key
interface SummaryPayload {
  counts: StateCountRow[]
  sums: StateSums
}

function keyFor(sellerId: number, tradeId: number): string {
  return `${sellerId}:${tradeId}`
}

function parseDecimalString(val: unknown): number {
  // Parse strings like "123.45" to numbers; fallback to 0 on invalid
  const n = typeof val === 'number' ? val : parseFloat(String(val))
  return Number.isFinite(n) ? n : 0
}

export const useStateSummariesStore = defineStore('stateSummaries', () => {
  // --------------------------------------------------------------------------
  // Reactive state
  // --------------------------------------------------------------------------
  const countsByState = ref<StateCountRow[]>([])
  const sumsByState = ref<StateSums>({
    currentBalance: new Map<string, number>(),
    totalDebt: new Map<string, number>(),
    sellerAsIs: new Map<string, number>(),
  })
  const loading = ref<boolean>(false)
  const error = ref<string | null>(null)
  const lastKey = ref<string | null>(null)
  const cache = ref<Map<string, SummaryPayload>>(new Map())

  // --------------------------------------------------------------------------
  // Derived getters
  // --------------------------------------------------------------------------
  const topCounts = computed<{ labels: string[]; counts: number[]; maxCount: number }>(() => {
    // Sort counts desc and take top 10
    const sorted = [...countsByState.value].sort((a, b) => (b.count || 0) - (a.count || 0)).slice(0, 10)
    const labels = sorted.map(r => (r.state || '').toString().trim().toUpperCase()).filter(Boolean)
    const counts = sorted.map(r => Number(r.count) || 0)
    const maxCount = counts.length ? Math.max(...counts) : 0
    return { labels, counts, maxCount }
  })

  // Convenience getter: access a specific state's sums (numbers)
  function sumsFor(stateCode: string): { currentBalance: number; totalDebt: number; sellerAsIs: number } {
    const st = (stateCode || '').toString().trim().toUpperCase()
    return {
      currentBalance: sumsByState.value.currentBalance.get(st) || 0,
      totalDebt: sumsByState.value.totalDebt.get(st) || 0,
      sellerAsIs: sumsByState.value.sellerAsIs.get(st) || 0,
    }
  }

  // --------------------------------------------------------------------------
  // Actions
  // --------------------------------------------------------------------------
  function reset(): void {
    countsByState.value = []
    sumsByState.value = {
      currentBalance: new Map<string, number>(),
      totalDebt: new Map<string, number>(),
      sellerAsIs: new Map<string, number>(),
    }
    loading.value = false
    error.value = null
    lastKey.value = null
  }

  async function fetchAll(sellerId: number, tradeId: number): Promise<void> {
    // Require both IDs to enforce siloing
    if (!sellerId || !tradeId) {
      reset()
      return
    }

    const key = keyFor(sellerId, tradeId)

    // Serve from cache if present
    const cached = cache.value.get(key)
    if (cached) {
      countsByState.value = cached.counts
      sumsByState.value = cached.sums
      lastKey.value = key
      error.value = null
      return
    }

    // Dedupe if same key already active and we have data
    if (lastKey.value === key && countsByState.value.length > 0) {
      return
    }

    loading.value = true
    error.value = null
    try {
      console.debug('[stateSummaries] fetchAll start', { sellerId, tradeId })
      // Use leading slash so Axios correctly joins with baseURL.
      const [countResp, scbResp, stdResp, savResp] = await Promise.all([
        http.get<StateCountRow[]>(`/acq/summary/state/count-by/${sellerId}/${tradeId}/`),
        http.get<SumCurrentBalanceRow[]>(`/acq/summary/state/sum-current-balance/${sellerId}/${tradeId}/`),
        http.get<SumTotalDebtRow[]>(`/acq/summary/state/sum-total-debt/${sellerId}/${tradeId}/`),
        http.get<SumSellerAsIsValueRow[]>(`/acq/summary/state/sum-seller-asis-value/${sellerId}/${tradeId}/`),
      ])

      const counts = Array.isArray(countResp.data) ? countResp.data.map(r => ({
        state: (r.state || '').toString().trim().toUpperCase(),
        count: Number(r.count) || 0,
      })) : []

      // Normalize sums into Maps keyed by state
      const mkMap = <T extends { state: string }>(rows: T[], pick: (row: T) => number) => {
        const m = new Map<string, number>()
        for (const r of rows || []) {
          const st = (r.state || '').toString().trim().toUpperCase()
          if (!st) continue
          m.set(st, (m.get(st) || 0) + pick(r))
        }
        return m
      }

      const scbRows = Array.isArray(scbResp.data) ? scbResp.data : []
      const stdRows = Array.isArray(stdResp.data) ? stdResp.data : []
      const savRows = Array.isArray(savResp.data) ? savResp.data : []

      const sums: StateSums = {
        currentBalance: mkMap(scbRows, (r: any) => parseDecimalString(r.sum_current_balance)),
        totalDebt: mkMap(stdRows, (r: any) => parseDecimalString(r.sum_total_debt)),
        sellerAsIs: mkMap(savRows, (r: any) => parseDecimalString(r.sum_seller_asis_value)),
      }
      console.debug('[stateSummaries] fetchAll results', {
        countsLen: counts.length,
        firstCount: counts[0],
        labelsPreview: counts.slice(0, 5).map(c => c.state),
      })
      countsByState.value = counts
      sumsByState.value = sums
      lastKey.value = key
      cache.value.set(key, { counts, sums })
    } catch (e: any) {
      error.value = e?.message || 'Failed to fetch state summaries'
      console.error('[stateSummaries] fetchAll error', e)
      countsByState.value = []
      sumsByState.value = {
        currentBalance: new Map<string, number>(),
        totalDebt: new Map<string, number>(),
        sellerAsIs: new Map<string, number>(),
      }
      lastKey.value = null
    } finally {
      loading.value = false
      console.debug('[stateSummaries] fetchAll end', { sellerId, tradeId, loaded: countsByState.value.length })
    }
  }

  function clearCache(): void {
    cache.value.clear()
  }

  return {
    // state
    countsByState,
    sumsByState,
    loading,
    error,
    lastKey,
    cache,
    // getters
    topCounts,
    sumsFor,
    // actions
    fetchAll,
    reset,
    clearCache,
  }
})
