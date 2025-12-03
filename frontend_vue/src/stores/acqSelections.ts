// src/stores/acqSelections.ts
// Pinia store for acquisitions selections (seller/trade) and geocoded markers
// Docs reviewed:
// - Pinia: https://pinia.vuejs.org/core-concepts/
// - Axios instances: https://axios-http.com/docs/instance
// - jVectorMap markers: https://jvectormap.com/documentation/javascript-api/#markers

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import http from '@/lib/http'

// Backend marker shape returned by Django view
export interface BackendMarker {
  // numeric latitude from Google Geocoding result
  lat: number
  // numeric longitude from Google Geocoding result
  lng: number
  // human-readable label, currently the full address string
  name: string
  // internal row id representative for the address (if multiple rows share the address)
  id: number
}

// Shared option payloads consumed by dropdown selectors
export interface SellerOption {
  id: number
  name: string
}

export interface TradeOption {
  id: number
  trade_name: string
}

// jVectorMap marker shape expected by the map component
export interface VectorMarker {
  // [lat, lng] tuple per jVectorMap API
  latLng: [number, number]
  // label string visible on hover
  name: string
  // keep id for traceability if needed by future click handlers
  id?: number
}

export const useAcqSelectionsStore = defineStore('acqSelections', () => {
  // ---------------------------------------------------------------------------
  // Selections: which seller and trade the user has chosen
  // ---------------------------------------------------------------------------
  const selectedSellerId = ref<number | null>(null) // current seller id or null
  const selectedTradeId = ref<number | null>(null)  // current trade id or null

  // ---------------------------------------------------------------------------
  // Markers state: backend results, loading, and error flags
  // ---------------------------------------------------------------------------
  const markers = ref<BackendMarker[]>([])          // raw markers from backend
  const loadingMarkers = ref<boolean>(false)        // network activity flag
  const errorMarkers = ref<string | null>(null)     // last error message (if any)

  // ---------------------------------------------------------------------------
  // Dropdown option caches shared across acquisitions UI
  // ---------------------------------------------------------------------------
  const sellerOptions = ref<SellerOption[]>([])
  const tradeOptions = ref<TradeOption[]>([])
  const sellerOptionsLoading = ref<boolean>(false)
  const tradeOptionsLoading = ref<boolean>(false)
  const sellerOptionsError = ref<string | null>(null)
  const tradeOptionsError = ref<string | null>(null)

  // Cache the last selection pair to avoid duplicate fetches
  const lastKey = ref<string | null>(null)          // e.g., "sellerId:tradeId"
  // Abort controller to cancel previous marker requests when selection changes
  let currentController: AbortController | null = null
  let inFlightKey: string | null = null

  // ---------------------------------------------------------------------------
  // Trade status state fetched from backend for the selected trade
  // ---------------------------------------------------------------------------
  const tradeStatusValue = ref<string | null>(null)
  const tradeStatusOptions = ref<Array<{ value: string; label: string }>>([])
  const tradeStatusLoading = ref<boolean>(false)
  const tradeStatusError = ref<string | null>(null)

  // Derived: whether we have both ids selected
  const hasBothSelections = computed<boolean>(() => !!selectedSellerId.value && !!selectedTradeId.value)

  // Stable key string for the current selection pair
  const selectionKey = computed<string>(() => `${selectedSellerId.value ?? 'null'}:${selectedTradeId.value ?? 'null'}`)

  // Transform backend markers into jVectorMap shape
  const vectorMarkers = computed<VectorMarker[]>(() =>
    (markers.value || []).map((m) => ({ latLng: [m.lat, m.lng], name: m.name, id: m.id }))
  )

  // ---------------------------------------------------------------------------
  // Mutators for selections and markers
  // ---------------------------------------------------------------------------
  function clearTradeOptions(): void {
    tradeOptions.value = []
    tradeOptionsError.value = null
    tradeOptionsLoading.value = false
  }

  function setSeller(id: number | null): void {
    // update seller id; clear trade if seller changes
    const changed = selectedSellerId.value !== id
    selectedSellerId.value = id
    if (changed) {
      selectedTradeId.value = null
      resetMarkers()
      resetTradeStatus() // ensure trade status UI clears when seller context changes
      if (id) {
        void fetchTradeOptions(id)
      } else {
        clearTradeOptions()
      }
    }
  }

  async function fetchTradeStatus(): Promise<void> {
    if (!selectedTradeId.value) {
      resetTradeStatus()
      return
    }
    tradeStatusLoading.value = true
    tradeStatusError.value = null
    try {
      const tradeId = selectedTradeId.value as number
      const resp = await http.get(`/acq/trades/${tradeId}/status/`, { timeout: 10000 })
      tradeStatusValue.value = resp.data?.status ?? null
      tradeStatusOptions.value = Array.isArray(resp.data?.options) ? resp.data.options : []
    } catch (e: any) {
      console.error('[acqSelections] fetchTradeStatus failed', e)
      tradeStatusError.value = e?.message || 'Failed to load trade status'
      tradeStatusOptions.value = []
    } finally {
      tradeStatusLoading.value = false
    }
  }

  async function updateTradeStatus(nextStatus: string): Promise<boolean> {
    if (!selectedTradeId.value) {
      return false
    }
    tradeStatusLoading.value = true
    tradeStatusError.value = null
    try {
      const tradeId = selectedTradeId.value as number
      const resp = await http.post(`/acq/trades/${tradeId}/status/update/`, { status: nextStatus }, { timeout: 10000 })
      tradeStatusValue.value = resp.data?.status ?? nextStatus
      tradeStatusOptions.value = Array.isArray(resp.data?.options) ? resp.data.options : tradeStatusOptions.value
      return true
    } catch (e: any) {
      console.error('[acqSelections] updateTradeStatus failed', e)
      tradeStatusError.value = e?.message || 'Failed to update trade status'
      return false
    } finally {
      tradeStatusLoading.value = false
    }
  }

  function setTrade(id: number | null): void {
    selectedTradeId.value = id
    if (id === null) {
      resetMarkers()
      resetTradeStatus() // reset lifecycle selector when trade deselected
    } else {
      tradeStatusValue.value = null // prime status value so loading states show correctly while fetching
    }
  }

  function resetMarkers(): void {
    markers.value = []
    errorMarkers.value = null
    loadingMarkers.value = false
    lastKey.value = null
  }

  function resetTradeStatus(): void {
    tradeStatusValue.value = null
    tradeStatusOptions.value = []
    tradeStatusLoading.value = false
    tradeStatusError.value = null
  }

  async function fetchSellerOptions(force = false): Promise<SellerOption[]> {
    if (!force && sellerOptions.value.length > 0) {
      return sellerOptions.value
    }

    sellerOptionsLoading.value = true
    sellerOptionsError.value = null
    try {
      const resp = await http.get<SellerOption[]>('/acq/sellers/', { timeout: 10000 })
      const payload = Array.isArray(resp.data) ? resp.data : []
      sellerOptions.value = payload.map((option: any) => {
        const rawName = option.name ?? option.seller_name ?? ''
        return {
          id: option.id,
          name: String(rawName).toUpperCase(),
        }
      })
      return sellerOptions.value
    } catch (e: any) {
      sellerOptionsError.value = e?.message || 'Failed to load sellers'
      sellerOptions.value = []
      return []
    } finally {
      sellerOptionsLoading.value = false
    }
  }

  async function fetchTradeOptions(sellerId: number, force = false): Promise<TradeOption[]> {
    if (!sellerId) {
      clearTradeOptions()
      return []
    }

    if (!force && tradeOptions.value.length > 0 && selectedSellerId.value === sellerId) {
      return tradeOptions.value
    }

    tradeOptionsLoading.value = true
    tradeOptionsError.value = null
    try {
      const resp = await http.get<TradeOption[]>(`/acq/trades/${sellerId}/`, { timeout: 10000 })
      tradeOptions.value = Array.isArray(resp.data) ? resp.data : []
      return tradeOptions.value
    } catch (e: any) {
      tradeOptionsError.value = e?.message || 'Failed to load trades'
      tradeOptions.value = []
      return []
    } finally {
      tradeOptionsLoading.value = false
    }
  }

  async function refreshOptions(): Promise<void> {
    await fetchSellerOptions(true)
    if (selectedSellerId.value) {
      await fetchTradeOptions(selectedSellerId.value, true)
    }
  }

  // ---------------------------------------------------------------------------
  // Network: fetch geocoded markers for the current selection
  // GET /acq/geocode/markers/<seller_id>/<trade_id>/ (baseURL handled by http)
  // ---------------------------------------------------------------------------
  async function fetchMarkers(): Promise<void> {
    // require both selections
    if (!hasBothSelections.value) {
      resetMarkers()
      resetTradeStatus()
      return
    }

    // dedupe: avoid refetch if selection didn't change
    if (lastKey.value === selectionKey.value && markers.value.length > 0) {
      return
    }

    loadingMarkers.value = true
    errorMarkers.value = null
    try {
      const sid = selectedSellerId.value as number
      const tid = selectedTradeId.value as number
      const key = `${sid}:${tid}`
      // Cancel prior in-flight if for different key
      if (currentController && inFlightKey && inFlightKey !== key) {
        try { currentController.abort() } catch {}
      }
      currentController = new AbortController()
      inFlightKey = key
      // IMPORTANT: Use a leading slash so Axios correctly joins with baseURL.
      // If baseURL is '/api', then '/acq/..' becomes '/api/acq/..' (correct).
      // Without the leading slash, it would become '/apiacq/..' (incorrect).
      console.debug('[acqSelections] fetching markers', { sellerId: sid, tradeId: tid })
      const resp = await http.get(`/acq/geocode/markers/${sid}/${tid}/`, {
        signal: currentController.signal as any,
        timeout: 120000,  // 2 minutes for initial geocoding of large datasets (658 addresses)
      })
      const data = resp.data as { markers: BackendMarker[]; count: number; source: string; error?: string }
      markers.value = Array.isArray(data.markers) ? data.markers : []
      console.debug('[acqSelections] fetched markers', { count: markers.value.length, source: (data as any)?.source })
      if (data.error) {
        errorMarkers.value = data.error
        console.warn('[acqSelections] backend reported error', data.error)
      }
      lastKey.value = selectionKey.value
    } catch (e: any) {
      const isCanceled = e?.code === 'ERR_CANCELED' || e?.name === 'CanceledError' || e?.message === 'canceled'
      if (isCanceled) {
        // Do not overwrite current state on cancel
        console.debug('[acqSelections] fetch markers canceled')
      } else {
        errorMarkers.value = e?.message || 'Failed to fetch markers'
        markers.value = []
        console.error('[acqSelections] fetch markers failed', e)
        lastKey.value = null
      }
    } finally {
      if (inFlightKey === selectionKey.value) {
        loadingMarkers.value = false
        currentController = null
        inFlightKey = null
      }
    }
  }

  return {
    // state
    selectedSellerId,
    selectedTradeId,
    markers,
    loadingMarkers,
    errorMarkers,
    lastKey,
    tradeStatusValue,
    tradeStatusOptions,
    tradeStatusLoading,
    tradeStatusError,
    sellerOptions,
    tradeOptions,
    sellerOptionsLoading,
    tradeOptionsLoading,
    sellerOptionsError,
    tradeOptionsError,
    // getters
    hasBothSelections,
    selectionKey,
    vectorMarkers,
    // actions
    setSeller,
    setTrade,
    resetMarkers,
    resetTradeStatus,
    fetchMarkers,
    fetchTradeStatus,
    updateTradeStatus,
    fetchSellerOptions,
    fetchTradeOptions,
    refreshOptions,
  }
})
