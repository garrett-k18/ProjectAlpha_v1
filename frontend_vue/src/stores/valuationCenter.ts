/**
 * Pinia store for Valuation Center data.
 * 
 * WHAT: Manages valuation center row data and update operations
 * WHY: Dedicated store for valuation center, separate from AG Grid data
 * HOW: Fetch from /valuation-center/ endpoint, cache per seller/trade
 * 
 * Used by: ValuationCenter.vue and its tabs (Overview, Reconciliation, Brokers)
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import http from '@/lib/http'

// -----------------------------------------------------------------------------
// Types
// -----------------------------------------------------------------------------

export interface ValuationRow {
  // Asset identifiers
  id: number
  asset_hub_id: number
  sellertape_id: string
  
  // Location
  street_address: string
  city: string
  state: string
  zip: string
  
  // Loan info
  current_balance: number | null
  total_debt: number | null
  
  // Seller values
  seller_asis_value: number | null
  seller_arv_value: number | null
  
  // Internal Initial UW valuation
  internal_initial_uw_asis_value: number | null
  internal_initial_uw_arv_value: number | null
  internal_initial_uw_grade: string | null
  internal_initial_uw_notes: string | null
  
  // Broker valuation
  broker_asis_value: number | null
  broker_arv_value: number | null
  broker_rehab_est: number | null
  broker_recommend_rehab: boolean | null
  broker_notes: string | null
}

export interface ValuationUpdatePayload {
  source: 'internalInitialUW' | 'broker'
  asis_value?: number | null
  arv_value?: number | null
  grade_code?: string | null
  rehab_est_total?: number | null
  recommend_rehab?: boolean | null
  notes?: string | null
}

// -----------------------------------------------------------------------------
// Store
// -----------------------------------------------------------------------------

export const useValuationCenterStore = defineStore('valuationCenter', () => {
  // ---------------------------------------------------------------------------
  // State
  // ---------------------------------------------------------------------------
  
  /** Current rows for the valuation center */
  const rows = ref<ValuationRow[]>([])
  
  /** Loading state */
  const loading = ref(false)
  
  /** Error message if fetch failed */
  const error = ref<string | null>(null)
  
  /** Cache key for current data (seller:trade) */
  const cacheKey = ref<string | null>(null)
  
  // ---------------------------------------------------------------------------
  // Computed
  // ---------------------------------------------------------------------------
  
  /** Total number of rows */
  const rowCount = computed(() => rows.value.length)
  
  /** Check if data is loaded */
  const hasData = computed(() => rows.value.length > 0)
  
  // ---------------------------------------------------------------------------
  // Actions
  // ---------------------------------------------------------------------------
  
  /**
   * Fetch valuation center data for a seller/trade.
   * 
   * WHAT: Load all assets with valuation data
   * WHY: Populate valuation center tabs
   * HOW: GET /api/acq/valuation-center/{seller}/{trade}/
   */
  async function fetchRows(sellerId: number, tradeId: number): Promise<void> {
    const key = `${sellerId}:${tradeId}`
    
    console.log('[valuationCenter] fetchRows', { sellerId, tradeId })
    
    // Skip if already loaded for this seller/trade
    if (cacheKey.value === key && rows.value.length > 0) {
      console.log('[valuationCenter] Using cached data')
      return
    }
    
    loading.value = true
    error.value = null
    
    try {
      // Fetch all pages
      const allRows: ValuationRow[] = []
      let nextUrl: string | null = `/acq/valuation-center/${sellerId}/${tradeId}/?page_size=2000`
      
      while (nextUrl) {
        console.log('[valuationCenter] Fetching:', nextUrl)
        
        const resp = await http.get<{
          results: ValuationRow[]
          count: number
          next: string | null
        }>(nextUrl)
        
        const pageResults = resp.data?.results || []
        allRows.push(...pageResults)
        
        console.log('[valuationCenter] Got', pageResults.length, 'rows, total:', allRows.length)
        
        // Handle next page URL
        const nextPage: string | null = resp.data?.next || null
        if (nextPage) {
          try {
            const parsedUrl = new URL(nextPage)
            nextUrl = parsedUrl.pathname + parsedUrl.search
          } catch {
            nextUrl = nextPage.startsWith('/') ? nextPage : null
          }
        } else {
          nextUrl = null
        }
      }
      
      rows.value = allRows
      cacheKey.value = key
      
      console.log('[valuationCenter] Loaded', allRows.length, 'total rows')
      
      // Log sample row for debugging
      if (allRows.length > 0) {
        console.log('[valuationCenter] Sample row:', {
          id: allRows[0].id,
          internal_initial_uw_grade: allRows[0].internal_initial_uw_grade,
          broker_rehab_est: allRows[0].broker_rehab_est,
        })
      }
      
    } catch (e: any) {
      console.error('[valuationCenter] Fetch failed:', e)
      error.value = e?.message || 'Failed to fetch valuation data'
      rows.value = []
      cacheKey.value = null
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Update valuation for an asset.
   * 
   * WHAT: Save grade, values, or rehab data
   * WHY: Allow users to edit valuations in the UI
   * HOW: PUT /api/acq/valuation-center/{asset_id}/
   */
  async function updateValuation(
    assetId: number,
    payload: ValuationUpdatePayload
  ): Promise<boolean> {
    console.log('[valuationCenter] updateValuation', { assetId, payload })
    
    try {
      const resp = await http.put(`/acq/valuation-center/${assetId}/`, payload)
      console.log('[valuationCenter] Update response:', resp.data)
      
      // Optimistically update local row
      const row = rows.value.find(r => r.id === assetId)
      if (row) {
        if (payload.source === 'internalInitialUW') {
          if (payload.asis_value !== undefined) row.internal_initial_uw_asis_value = payload.asis_value
          if (payload.arv_value !== undefined) row.internal_initial_uw_arv_value = payload.arv_value
          if (payload.grade_code !== undefined) row.internal_initial_uw_grade = payload.grade_code
          if (payload.notes !== undefined) row.internal_initial_uw_notes = payload.notes
        } else if (payload.source === 'broker') {
          if (payload.asis_value !== undefined) row.broker_asis_value = payload.asis_value
          if (payload.arv_value !== undefined) row.broker_arv_value = payload.arv_value
          if (payload.rehab_est_total !== undefined) row.broker_rehab_est = payload.rehab_est_total
          if (payload.recommend_rehab !== undefined) row.broker_recommend_rehab = payload.recommend_rehab
          if (payload.notes !== undefined) row.broker_notes = payload.notes
        }
      }
      
      return true
    } catch (e: any) {
      console.error('[valuationCenter] Update failed:', e?.response?.data || e)
      return false
    }
  }
  
  /**
   * Save grade for an asset.
   * Convenience wrapper for updateValuation.
   */
  async function saveGrade(assetId: number, gradeCode: string | null): Promise<boolean> {
    return updateValuation(assetId, {
      source: 'internalInitialUW',
      grade_code: gradeCode,
    })
  }
  
  /**
   * Save internal UW value for an asset.
   * Convenience wrapper for updateValuation.
   */
  async function saveInternalUWValue(
    assetId: number,
    field: 'asis' | 'arv',
    value: number | null
  ): Promise<boolean> {
    const payload: ValuationUpdatePayload = { source: 'internalInitialUW' }
    if (field === 'asis') {
      payload.asis_value = value
    } else {
      payload.arv_value = value
    }
    return updateValuation(assetId, payload)
  }
  
  /**
   * Save broker rehab estimate for an asset.
   * Convenience wrapper for updateValuation.
   */
  async function saveBrokerRehab(assetId: number, value: number | null): Promise<boolean> {
    return updateValuation(assetId, {
      source: 'broker',
      rehab_est_total: value,
    })
  }
  
  /**
   * Save broker recommend rehab flag for an asset.
   * Convenience wrapper for updateValuation.
   */
  async function saveBrokerRecommendRehab(assetId: number, value: boolean): Promise<boolean> {
    return updateValuation(assetId, {
      source: 'broker',
      recommend_rehab: value,
    })
  }
  
  /**
   * Clear cached data to force fresh fetch.
   */
  function clearCache(): void {
    console.log('[valuationCenter] clearCache')
    cacheKey.value = null
  }
  
  /**
   * Force refresh data for current seller/trade.
   */
  async function refresh(sellerId: number, tradeId: number): Promise<void> {
    clearCache()
    await fetchRows(sellerId, tradeId)
  }
  
  // ---------------------------------------------------------------------------
  // Return
  // ---------------------------------------------------------------------------
  
  return {
    // State
    rows,
    loading,
    error,
    
    // Computed
    rowCount,
    hasData,
    
    // Actions
    fetchRows,
    updateValuation,
    saveGrade,
    saveInternalUWValue,
    saveBrokerRehab,
    saveBrokerRecommendRehab,
    clearCache,
    refresh,
  }
})
