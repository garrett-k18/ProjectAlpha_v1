// src/stores/strats.ts
// Pinia store for dynamic stratification bands served by the backend.
// Docs reviewed:
// - Pinia: https://pinia.vuejs.org/core-concepts/
// - Axios Instances: https://axios-http.com/docs/instance
// - Vue reactivity: https://vuejs.org/guide/essentials/reactivity-fundamentals.html

import { defineStore } from 'pinia'
import { ref } from 'vue'
import http from '@/lib/http'

// Server band payload shape (from Django)
export interface StratBand {
  key: string
  index: number
  lower: string | null
  upper: string | null
  count: number
  sum_current_balance: string
  sum_total_debt: string
  sum_seller_asis_value: string
  label: string
}

export const useStratsStore = defineStore('strats', () => {
  // Cache by selection key "sellerId:tradeId"
  const bandsByKey = ref<Record<string, StratBand[]>>({}) // current_balance bands cache
  const debtBandsByKey = ref<Record<string, StratBand[]>>({}) // total_debt bands cache
  const asisBandsByKey = ref<Record<string, StratBand[]>>({}) // seller_asis_value bands cache
  const loading = ref<boolean>(false)          // current_balance loading
  const error = ref<string | null>(null)       // current_balance error
  const lastKey = ref<string | null>(null)     // last current_balance key
  const loadingTD = ref<boolean>(false)        // total_debt loading
  const errorTD = ref<string | null>(null)     // total_debt error
  const lastDebtKey = ref<string | null>(null) // last total_debt key
  const loadingAsis = ref<boolean>(false)      // seller_asis_value loading
  const errorAsis = ref<string | null>(null)   // seller_asis_value error
  const lastAsisKey = ref<string | null>(null) // last seller_asis_value key

  function reset(): void {
    loading.value = false
    error.value = null
    lastKey.value = null
    loadingTD.value = false
    errorTD.value = null
    lastDebtKey.value = null
    loadingAsis.value = false
    errorAsis.value = null
    lastAsisKey.value = null
  }

  async function fetchBands(sellerId: number, tradeId: number): Promise<StratBand[]> {
    const key = `${sellerId}:${tradeId}`
    // Return cached if available
    if (bandsByKey.value[key]) return bandsByKey.value[key]

    loading.value = true
    error.value = null
    try {
      const resp = await http.get(`/acq/summary/strat/current-balance/${sellerId}/${tradeId}/`)
      const data = Array.isArray(resp.data) ? (resp.data as StratBand[]) : []
      bandsByKey.value[key] = data
      lastKey.value = key
      return data
    } catch (e: any) {
      // Prefer server-provided error message when available
      error.value = e?.response?.data?.error || e?.message || 'Failed to fetch stratification'
      lastKey.value = null
      bandsByKey.value[key] = []
      return []
    } finally {
      loading.value = false
    }
  }

  // Fetch Total Debt stratification bands for a selection
  async function fetchBandsTotalDebt(sellerId: number, tradeId: number): Promise<StratBand[]> {
    const key = `${sellerId}:${tradeId}`
    if (debtBandsByKey.value[key]) return debtBandsByKey.value[key]

    loadingTD.value = true
    errorTD.value = null
    try {
      const resp = await http.get(`/acq/summary/strat/total-debt/${sellerId}/${tradeId}/`)
      const data = Array.isArray(resp.data) ? (resp.data as StratBand[]) : []
      debtBandsByKey.value[key] = data
      lastDebtKey.value = key
      return data
    } catch (e: any) {
      errorTD.value = e?.response?.data?.error || e?.message || 'Failed to fetch total debt stratification'
      lastDebtKey.value = null
      debtBandsByKey.value[key] = []
      return []
    } finally {
      loadingTD.value = false
    }
  }

  // Fetch Seller As-Is Value stratification bands for a selection
  async function fetchBandsSellerAsIs(sellerId: number, tradeId: number): Promise<StratBand[]> {
    const key = `${sellerId}:${tradeId}`
    if (asisBandsByKey.value[key]) return asisBandsByKey.value[key]

    loadingAsis.value = true
    errorAsis.value = null
    try {
      const resp = await http.get(`/acq/summary/strat/seller-asis-value/${sellerId}/${tradeId}/`)
      const data = Array.isArray(resp.data) ? (resp.data as StratBand[]) : []
      asisBandsByKey.value[key] = data
      lastAsisKey.value = key
      return data
    } catch (e: any) {
      errorAsis.value = e?.response?.data?.error || e?.message || 'Failed to fetch seller as-is stratification'
      lastAsisKey.value = null
      asisBandsByKey.value[key] = []
      return []
    } finally {
      loadingAsis.value = false
    }
  }

  function getBands(sellerId: number | null, tradeId: number | null): StratBand[] {
    if (!sellerId || !tradeId) return []
    const key = `${sellerId}:${tradeId}`
    return bandsByKey.value[key] || []
  }

  // Getter for Total Debt bands
  function getBandsTotalDebt(sellerId: number | null, tradeId: number | null): StratBand[] {
    if (!sellerId || !tradeId) return []
    const key = `${sellerId}:${tradeId}`
    return debtBandsByKey.value[key] || []
  }

  // Getter for Seller As-Is bands
  function getBandsSellerAsIs(sellerId: number | null, tradeId: number | null): StratBand[] {
    if (!sellerId || !tradeId) return []
    const key = `${sellerId}:${tradeId}`
    return asisBandsByKey.value[key] || []
  }

  function clearCache(): void {
    bandsByKey.value = {}
    debtBandsByKey.value = {}
    asisBandsByKey.value = {}
    reset()
  }

  return {
    // state
    bandsByKey,
    debtBandsByKey,
    asisBandsByKey,
    loading,
    error,
    lastKey,
    loadingTD,
    errorTD,
    lastDebtKey,
    loadingAsis,
    errorAsis,
    lastAsisKey,
    // actions
    fetchBands,
    fetchBandsTotalDebt,
    fetchBandsSellerAsIs,
    clearCache,
    reset,
    // getters/helpers
    getBands,
    getBandsTotalDebt,
    getBandsSellerAsIs,
  }
})
