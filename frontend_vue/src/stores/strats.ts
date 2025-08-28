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
  const bandsByKey = ref<Record<string, StratBand[]>>({})
  const loading = ref<boolean>(false)
  const error = ref<string | null>(null)
  const lastKey = ref<string | null>(null)

  function reset(): void {
    loading.value = false
    error.value = null
    lastKey.value = null
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

  function getBands(sellerId: number | null, tradeId: number | null): StratBand[] {
    if (!sellerId || !tradeId) return []
    const key = `${sellerId}:${tradeId}`
    return bandsByKey.value[key] || []
  }

  function clearCache(): void {
    bandsByKey.value = {}
    reset()
  }

  return {
    // state
    bandsByKey,
    loading,
    error,
    lastKey,
    // actions
    fetchBands,
    clearCache,
    reset,
    // getters/helpers
    getBands,
  }
})
