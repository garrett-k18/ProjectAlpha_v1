// src/stores/tradeAssumptions.ts
// Pinia store for trade level assumptions data

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import http from '@/lib/http'

// Interface for trade level assumptions data
export interface TradeAssumption {
  id?: number;
  trade_id: number;
  bid_date: string | null; // ISO format
  settlement_date: string | null; // ISO format
  pctUPB?: string | null;
  target_irr?: string | null;
  discount_rate?: string | null;
  perf_rpl_hold_period?: number | null;
  servicing_transfer_date?: string | null;
  mod_rate?: string | null;
  mod_term?: number | null;
  mod_balance?: string | null;
  mod_date?: string | null;
  mod_maturity_date?: string | null;
}

export const useTradeAssumptionsStore = defineStore('tradeAssumptions', () => {
  // State
  const assumptions = ref<TradeAssumption | null>(null)
  const loading = ref<boolean>(false)
  const error = ref<string | null>(null)
  const lastTradeId = ref<number | null>(null)

  // Getters
  const hasAssumptions = computed<boolean>(() => assumptions.value !== null)
  const bidDate = computed<string | null>(() => assumptions.value?.bid_date || null)
  const settlementDate = computed<string | null>(() => assumptions.value?.settlement_date || null)

  /**
   * Fetch trade level assumptions for a specific trade
   * @param tradeId The ID of the trade
   */
  async function fetchAssumptions(tradeId: number): Promise<void> {
    if (!tradeId) {
      resetState()
      return
    }

    // Skip if we already have data for this trade
    if (lastTradeId.value === tradeId && assumptions.value) {
      return
    }

    loading.value = true
    error.value = null

    try {
      const response = await http.get(`/acq/trade-assumptions/${tradeId}/`)
      assumptions.value = response.data
      lastTradeId.value = tradeId
    } catch (e: any) {
      console.error('[tradeAssumptions] Failed to fetch assumptions:', e)
      error.value = e?.message || 'Failed to load trade assumptions'
      assumptions.value = null
    } finally {
      loading.value = false
    }
  }

  /**
   * Update trade level assumptions
   * @param tradeId The ID of the trade
   * @param data The assumption data to update
   */
  async function updateAssumptions(tradeId: number, data: Partial<TradeAssumption>): Promise<boolean> {
    if (!tradeId) {
      return false
    }

    loading.value = true
    error.value = null

    try {
      const response = await http.post(`/acq/trade-assumptions/${tradeId}/update/`, data)
      
      if (response.data && response.data.success) {
        // Update the local state with the returned data
        assumptions.value = {
          ...assumptions.value,
          ...response.data
        }
        return true
      }
      return false
    } catch (e: any) {
      console.error('[tradeAssumptions] Failed to update assumptions:', e)
      error.value = e?.message || 'Failed to update trade assumptions'
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * Reset the store state
   */
  function resetState(): void {
    assumptions.value = null
    loading.value = false
    error.value = null
    lastTradeId.value = null
  }

  return {
    // State
    assumptions,
    loading,
    error,
    lastTradeId,
    
    // Getters
    hasAssumptions,
    bidDate,
    settlementDate,
    
    // Actions
    fetchAssumptions,
    updateAssumptions,
    resetState
  }
})
