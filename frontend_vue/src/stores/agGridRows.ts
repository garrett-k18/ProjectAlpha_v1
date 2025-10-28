// src/stores/agGridRows.ts
// Pinia store for AG Grid row data, cached per sellerId:tradeId pair
// Documentation reviewed:
// - Pinia Core Concepts (defineStore, state/getters/actions): https://pinia.vuejs.org/core-concepts/
// - Axios Instances & Interceptors: https://axios-http.com/docs/instance
// - Vue 3 Reactivity (ref/computed): https://vuejs.org/guide/essentials/reactivity-fundamentals.html
// - AG Grid data updates best practices: https://www.ag-grid.com/vue-data-grid/data-update/
//
// Purpose:
// - Centralize fetching and caching of AG Grid rows to avoid redundant backend calls
// - Provide a simple API for components to load/reset/clear cached grid data
// - Keep concerns separated from selections and geocoded markers (handled by acqSelections store)

import { defineStore } from 'pinia'
import { ref } from 'vue'
import http from '@/lib/http'

// Strongly type rows as a record map of field -> value
export type GridRow = Record<string, unknown>

export const useAgGridRowsStore = defineStore('agGridRows', () => {
  // ---------------------------------------------------------------------------
  // Reactive state
  // ---------------------------------------------------------------------------
  // rows: the current dataset bound to the grid component
  const rows = ref<GridRow[]>([])
  // loadingRows: indicates when a fetch is in progress (can drive UI spinners)
  const loadingRows = ref<boolean>(false)
  // errorRows: last error message from a fetch attempt, if any
  const errorRows = ref<string | null>(null)
  // lastKey: tracks last successfully loaded selection pair to dedupe re-fetches
  const lastKey = ref<string | null>(null)
  // cache: memoizes datasets per selection key (e.g., "123:456") to avoid refetch
  const cache = ref<Map<string, GridRow[]>>(new Map())
  // Abort controller to cancel prior in-flight requests when selection changes
  let currentController: AbortController | null = null
  // Track which key is currently in flight to avoid clearing loading incorrectly
  let inFlightKey: string | null = null

  // ---------------------------------------------------------------------------
  // Helpers
  // ---------------------------------------------------------------------------
  // keyFor: builds a stable cache key for a sellerId + tradeId + view
  function keyFor(sellerId: number, tradeId: number, view: string = 'snapshot'): string {
    return `${sellerId}:${tradeId}:${view}`
  }

  // setRows: atomically update current rows and remember the key we loaded
  function setRows(data: GridRow[], key: string): void {
    rows.value = Array.isArray(data) ? data : []
    lastKey.value = key
  }

  // ---------------------------------------------------------------------------
  // Actions
  // ---------------------------------------------------------------------------
  /**
   * fetchRows
   * Loads grid rows for a given sellerId, tradeId, and view.
   * - Uses Axios instance with baseURL (e.g., "/api").
   * - Returns cached data immediately when available.
   * - Sets loading and error flags appropriately.
   * - Passes view parameter to backend for drop status filtering
   */
  async function fetchRows(sellerId: number, tradeId: number, view: string = 'snapshot'): Promise<void> {
    // Defensive: require both IDs
    if (!sellerId || !tradeId) {
      resetRows()
      return
    }

    const key = keyFor(sellerId, tradeId, view)

    // Serve from cache if available
    const cached = cache.value.get(key)
    if (cached && cached.length > 0) {
      setRows(cached, key)
      errorRows.value = null
      return
    }

    // Dedupe: if the same key is already loaded and rows exist, skip
    if (lastKey.value === key && rows.value.length > 0) {
      return
    }

    loadingRows.value = true
    errorRows.value = null
    try {
      // Cancel previous request if it targets a different key
      if (currentController && inFlightKey && inFlightKey !== key) {
        try { currentController.abort() } catch {}
      }
      currentController = new AbortController()
      inFlightKey = key
      // Use a leading slash so Axios baseURL (e.g., '/api') joins correctly.
      // Endpoint implemented by Django: GET /api/acq/raw-data/<sellerId>/<tradeId>/?view=<view>
      // Now returns paginated DRF response: { results: [...], count, next, previous }
      // Pass view parameter to filter by drop status
      // Request large page_size to get all assets (backend max is 500)
      const resp = await http.get<{ results: GridRow[]; count: number; next: string | null; previous: string | null }>(`/acq/raw-data/${sellerId}/${tradeId}/`, {
        params: { view, page_size: 500 },
        signal: currentController.signal as any,
        timeout: 20000,
      })
      // Extract results from paginated response (fallback to empty array)
      const data = Array.isArray(resp.data?.results) ? resp.data.results : []

      // Update current rows and cache
      setRows(data, key)
      cache.value.set(key, data)
    } catch (e: any) {
      // Suppress cancellation errors from AbortController/Axios
      const isCanceled = e?.code === 'ERR_CANCELED' || e?.name === 'CanceledError' || e?.message === 'canceled'
      if (isCanceled) {
        // Do not overwrite current rows on cancel
        // console.debug('[agGridRows] fetchRows canceled', { sellerId, tradeId })
      } else {
        // Capture error message and clear current rows
        errorRows.value = e?.message || 'Failed to fetch grid rows'
        rows.value = []
        lastKey.value = null
      }
    } finally {
      if (inFlightKey === key) {
        loadingRows.value = false
        currentController = null
        inFlightKey = null
      }
    }
  }

  /**
   * resetRows
   * Clears current rows and error/loading flags.
   * Cache is preserved (explicitly call clearCache to flush memory).
   */
  function resetRows(): void {
    rows.value = []
    loadingRows.value = false
    errorRows.value = null
    // Note: keep lastKey so components can decide whether to bypass fetch
    // or you may reset it to null to force re-fetch on next trigger.
    lastKey.value = null
  }

  /**
   * clearCache
   * Removes all cached datasets. Useful if the backend data has changed
   * (e.g., after edits) and you want to ensure fresh loads.
   */
  function clearCache(): void {
    cache.value.clear()
  }

  return {
    // state
    rows,
    loadingRows,
    errorRows,
    lastKey,
    cache,
    // actions
    fetchRows,
    resetRows,
    clearCache,
  }
})
