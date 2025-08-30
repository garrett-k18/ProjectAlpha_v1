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
  const wacBandsByKey = ref<Record<string, StratBand[]>>({}) // interest_rate (WAC) bands cache
  const propertyTypeBandsByKey = ref<Record<string, StratBand[]>>({}) // property_type bands cache
  const occupancyBandsByKey = ref<Record<string, StratBand[]>>({}) // occupancy bands cache
  const loading = ref<boolean>(false)          // current_balance loading
  const error = ref<string | null>(null)       // current_balance error
  const lastKey = ref<string | null>(null)     // last current_balance key
  const loadingTD = ref<boolean>(false)        // total_debt loading
  const errorTD = ref<string | null>(null)     // total_debt error
  const lastDebtKey = ref<string | null>(null) // last total_debt key
  const loadingAsis = ref<boolean>(false)      // seller_asis_value loading
  const errorAsis = ref<string | null>(null)   // seller_asis_value error
  const lastAsisKey = ref<string | null>(null) // last seller_asis_value key
  const loadingWac = ref<boolean>(false)       // WAC loading
  const errorWac = ref<string | null>(null)    // WAC error
  const lastWacKey = ref<string | null>(null)  // last WAC key
  const loadingPropertyType = ref<boolean>(false) // property_type loading
  const errorPropertyType = ref<string | null>(null) // property_type error
  const lastPropertyTypeKey = ref<string | null>(null) // last property_type key
  const loadingOccupancy = ref<boolean>(false) // occupancy loading
  const errorOccupancy = ref<string | null>(null) // occupancy error
  const lastOccupancyKey = ref<string | null>(null) // last occupancy key

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
    loadingWac.value = false
    errorWac.value = null
    lastWacKey.value = null
    loadingPropertyType.value = false
    errorPropertyType.value = null
    lastPropertyTypeKey.value = null
    loadingOccupancy.value = false
    errorOccupancy.value = null
    lastOccupancyKey.value = null
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

  // Fetch Interest Rate (WAC) stratification bands for a selection
  async function fetchBandsWac(sellerId: number, tradeId: number): Promise<StratBand[]> {
    const key = `${sellerId}:${tradeId}`
    // Use cached payload if already fetched for this selection
    if (wacBandsByKey.value[key]) return wacBandsByKey.value[key]

    loadingWac.value = true
    errorWac.value = null
    try {
      // Backend endpoint alias: /acq/summary/strat/interest-rate/{sellerId}/{tradeId}/
      const resp = await http.get(`/acq/summary/strat/interest-rate/${sellerId}/${tradeId}/`)
      const data = Array.isArray(resp.data) ? (resp.data as StratBand[]) : []
      wacBandsByKey.value[key] = data
      lastWacKey.value = key
      return data
    } catch (e: any) {
      // Prefer server-provided error message if present
      errorWac.value = e?.response?.data?.error || e?.message || 'Failed to fetch WAC stratification'
      lastWacKey.value = null
      wacBandsByKey.value[key] = []
      return []
    } finally {
      loadingWac.value = false
    }
  }

  // Fetch Property Type stratification bands for a selection (categorical)
  // Docs reviewed:
  // - Pinia actions/getters: https://pinia.vuejs.org/core-concepts/
  // - Axios: https://axios-http.com/docs/api_intro
  async function fetchBandsPropertyType(sellerId: number, tradeId: number): Promise<StratBand[]> {
    const key = `${sellerId}:${tradeId}`
    // Serve from cache when available
    if (propertyTypeBandsByKey.value[key]) return propertyTypeBandsByKey.value[key]

    loadingPropertyType.value = true
    errorPropertyType.value = null
    try {
      const resp = await http.get(`/acq/summary/strat/property-type/${sellerId}/${tradeId}/`)
      const data = Array.isArray(resp.data) ? (resp.data as StratBand[]) : []
      propertyTypeBandsByKey.value[key] = data
      lastPropertyTypeKey.value = key
      return data
    } catch (e: any) {
      errorPropertyType.value = e?.response?.data?.error || e?.message || 'Failed to fetch Property Type stratification'
      lastPropertyTypeKey.value = null
      propertyTypeBandsByKey.value[key] = []
      return []
    } finally {
      loadingPropertyType.value = false
    }
  }

  // Fetch Occupancy stratification bands for a selection (categorical)
  // Docs reviewed:
  // - Pinia actions/getters: https://pinia.vuejs.org/core-concepts/
  // - Axios: https://axios-http.com/docs/api_intro
  async function fetchBandsOccupancy(sellerId: number, tradeId: number): Promise<StratBand[]> {
    const key = `${sellerId}:${tradeId}`
    // Serve from cache when available
    if (occupancyBandsByKey.value[key]) return occupancyBandsByKey.value[key]

    loadingOccupancy.value = true
    errorOccupancy.value = null
    try {
      const resp = await http.get(`/acq/summary/strat/occupancy/${sellerId}/${tradeId}/`)
      const data = Array.isArray(resp.data) ? (resp.data as StratBand[]) : []
      occupancyBandsByKey.value[key] = data
      lastOccupancyKey.value = key
      return data
    } catch (e: any) {
      errorOccupancy.value = e?.response?.data?.error || e?.message || 'Failed to fetch Occupancy stratification'
      lastOccupancyKey.value = null
      occupancyBandsByKey.value[key] = []
      return []
    } finally {
      loadingOccupancy.value = false
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

  // Getter for WAC bands
  function getBandsWac(sellerId: number | null, tradeId: number | null): StratBand[] {
    if (!sellerId || !tradeId) return []
    const key = `${sellerId}:${tradeId}`
    return wacBandsByKey.value[key] || []
  }

  // Getter for Property Type bands
  function getBandsPropertyType(sellerId: number | null, tradeId: number | null): StratBand[] {
    if (!sellerId || !tradeId) return []
    const key = `${sellerId}:${tradeId}`
    return propertyTypeBandsByKey.value[key] || []
  }

  // Getter for Occupancy bands
  function getBandsOccupancy(sellerId: number | null, tradeId: number | null): StratBand[] {
    if (!sellerId || !tradeId) return []
    const key = `${sellerId}:${tradeId}`
    return occupancyBandsByKey.value[key] || []
  }

  function clearCache(): void {
    bandsByKey.value = {}
    debtBandsByKey.value = {}
    asisBandsByKey.value = {}
    wacBandsByKey.value = {}
    propertyTypeBandsByKey.value = {}
    occupancyBandsByKey.value = {}
    reset()
  }

  return {
    // state
    bandsByKey,
    debtBandsByKey,
    asisBandsByKey,
    wacBandsByKey,
    propertyTypeBandsByKey,
    occupancyBandsByKey,
    loading,
    error,
    lastKey,
    loadingTD,
    errorTD,
    lastDebtKey,
    loadingAsis,
    errorAsis,
    lastAsisKey,
    loadingWac,
    errorWac,
    lastWacKey,
    loadingPropertyType,
    errorPropertyType,
    lastPropertyTypeKey,
    loadingOccupancy,
    errorOccupancy,
    lastOccupancyKey,
    // actions
    fetchBands,
    fetchBandsTotalDebt,
    fetchBandsSellerAsIs,
    fetchBandsWac,
    fetchBandsPropertyType,
    fetchBandsOccupancy,
    clearCache,
    reset,
    // getters/helpers
    getBands,
    getBandsTotalDebt,
    getBandsSellerAsIs,
    getBandsWac,
    getBandsPropertyType,
    getBandsOccupancy,
  }
})
