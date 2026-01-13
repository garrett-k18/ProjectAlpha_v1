// src/stores/assetDispersion.ts // WHAT: File header describing module purpose.
// Pinia store dedicated to Asset Management dispersion markers. // WHAT: High-level description for maintainers.
// Docs reviewed: https://pinia.vuejs.org/core-concepts/ and https://jsvectormap.com/documentation/javascript-api/#markers // WHAT: Reference documentation consulted per user requirement.

import { defineStore } from 'pinia' // WHAT: Import Pinia helper to declare the store factory.
import { computed, ref } from 'vue' // WHAT: Import Vue reactivity utilities for state and derived values.
import http from '@/lib/http' // WHAT: Import shared Axios instance configured with Django API base URL.

export interface AssetDispersionMarker { // WHAT: Strongly type the marker object passed directly to the map component.
  latLng: [number, number] // WHAT: Tuple capturing latitude/longitude in decimal degrees.
  name: string // WHAT: Marker label shown in tooltips.
  id: string // WHAT: Stable identifier for the marker used as key in Vue lists.
  count: number // WHAT: Number of assets represented by marker (fixed at 1 under single-pin mode).
  asset_hub_id: string | number // WHAT: Asset hub identifier for drill-downs.
  lat: number // WHAT: Raw latitude retained for summaries and debugging.
  lng: number // WHAT: Raw longitude retained for summaries and debugging.
  label?: string // WHAT: Optional descriptive label from backend, preserved for UI summaries.
  state?: string // WHAT: Two-letter state abbreviation used for aggregation in summaries.
  city?: string // WHAT: Optional city name for richer map tooltips.
  street_address?: string // WHAT: Optional street address for richer map tooltips.
} // WHAT: Close AssetDispersionMarker interface declaration.

export interface AssetDispersionQuery { // WHAT: Enumerate supported query params mirroring backend filter contract.
  q?: string // WHAT: Optional quick filter string synced with AG Grid search field.
  state?: string // WHAT: Optional state filter (two-letter abbreviation) to scope markers geographically.
  asset_status?: string // WHAT: Optional asset status filter ensuring parity with grid column filter.
  seller_name?: string // WHAT: Optional seller name filter allowing seller-specific dispersion overlays.
  trade_name?: string // WHAT: Optional trade name filter aligning with trade context selections.
  lifecycle_status?: string // WHAT: Optional lifecycle filter to focus on specific asset management stages.
} // WHAT: Close AssetDispersionQuery interface declaration.

export const useAssetDispersionStore = defineStore('assetDispersion', () => { // WHAT: Instantiate the Pinia store for dispersion markers.
  const markers = ref<AssetDispersionMarker[]>([]) // WHAT: Reactive array storing marker payloads fetched from Django.
  const loading = ref<boolean>(false) // WHAT: Reactive flag indicating whether the last fetch is in-flight.
  const error = ref<string | null>(null) // WHAT: Reactive error message for UI feedback on failed fetch attempts.
  const cache = ref<Map<string, AssetDispersionMarker[]>>(new Map()) // WHAT: Cache keyed by serialized query strings to avoid redundant API calls.
  const lastKey = ref<string | null>(null) // WHAT: Track the most recently used cache key for debugging and cache hits.

  function makeCacheKey(params: AssetDispersionQuery): string { // WHAT: Generate deterministic cache key from query filters.
    const entries = Object.entries(params) // WHAT: Convert query object into iterable key/value tuples.
    const filtered = entries.filter(([_, value]) => typeof value === 'string' && value.trim().length > 0) // WHAT: Retain only non-empty string parameters for caching.
    const pairs = filtered.map(([key, value]) => `${key}=${(value as string).trim()}`) // WHAT: Coerce each parameter into `key=value` form.
    const sorted = pairs.sort() // WHAT: Alphabetically sort pairs to ensure stable ordering regardless of input.
    return sorted.join('&') || 'all' // WHAT: Join pairs into single key or default to 'all' when no filters provided.
  } // WHAT: End makeCacheKey helper function.

  async function fetchMarkers(params: AssetDispersionQuery = {}): Promise<void> { // WHAT: Load markers from backend while honoring cache.
    const key = makeCacheKey(params) // WHAT: Resolve cache key for provided parameters.
    if (cache.value.has(key)) { // WHAT: Serve markers from cache when available to reduce API load.
      markers.value = cache.value.get(key) ?? [] // WHAT: Populate reactive markers array with cached payload.
      lastKey.value = key // WHAT: Record the cache key for transparency tools and debugging.
      error.value = null // WHAT: Reset error state because cached responses are successful by definition.
      return // WHAT: Exit early because no network request is required.
    } // WHAT: End cache shortcut branch.

    loading.value = true // WHAT: Set loading flag so UI can show spinner or skeleton states.
    error.value = null // WHAT: Clear previous errors before attempting a fresh request.
    try { // WHAT: Begin guarded block to capture network errors gracefully.
      const resp = await http.get<{ markers: AssetDispersionMarker[] }>('/am/dashboard/markers/', { params, timeout: 15000 }) // WHAT: Issue GET request to new Django endpoint with filters and timeout.
      const payload = Array.isArray(resp.data?.markers) ? resp.data.markers : [] // WHAT: Normalize backend response ensuring array semantics.
      const normalizedMarkers = payload.map((marker: any) => {
        const lat = Number(marker.lat)
        const lng = Number(marker.lng)

        const rawLabel = typeof marker.label === 'string' ? marker.label : ''
        const cityRaw = typeof marker.city === 'string' ? marker.city : ''
        const streetRaw = typeof marker.street_address === 'string' ? marker.street_address : ''

        const state = typeof marker.state === 'string' ? marker.state.strip?.() ?? marker.state : '' // WHAT: Cater for Python-provided strings while guarding against undefined.
        const normalizedState = typeof state === 'string' && state.trim().length > 0 ? state.trim().toUpperCase() : '' // WHAT: Normalize state abbreviation to uppercase for consistent grouping.

        const city = cityRaw.trim()
        const street_address = streetRaw.trim()

        const locality = [city, normalizedState].filter(Boolean).join(', ')
        const addressDisplay = [street_address, locality].filter(Boolean).join(', ')

        const name = rawLabel.trim().length > 0
          ? rawLabel.trim()
          : (addressDisplay || `${lat.toFixed(2)}, ${lng.toFixed(2)}`)

        return {
          latLng: [lat, lng] as [number, number],
          name,
          id: `${marker.asset_hub_id ?? lat}-${lng}`,
          count: Number(marker.count ?? 1),
          asset_hub_id: marker.asset_hub_id ?? '',
          lat,
          lng,
          label: rawLabel,
          state: normalizedState,
          city,
          street_address,
        }
      }) // WHAT: Transform raw backend payload into strongly typed markers.
      markers.value = normalizedMarkers // WHAT: Store freshly retrieved markers in reactive state.
      cache.value.set(key, normalizedMarkers) // WHAT: Memoize payload for subsequent identical requests.
      lastKey.value = key // WHAT: Update lastKey to reflect the key served by live response.
    } catch (err: any) { // WHAT: Handle network or parsing failures.
      error.value = err?.message ?? 'Failed to load asset dispersion markers' // WHAT: Persist readable error message for UI display.
      markers.value = [] // WHAT: Reset markers array so stale data is not rendered when an error occurs.
      lastKey.value = null // WHAT: Clear lastKey to signal that no cache result is associated with the failure.
    } finally { // WHAT: Execute regardless of success or failure to clean up loading state.
      loading.value = false // WHAT: Reset loading flag so spinners can stop rendering.
    } // WHAT: End try/catch/finally block for fetchMarkers.
  } // WHAT: Close fetchMarkers action.

  const vectorMarkers = computed(() => markers.value) // WHAT: Return markers as-is because each entry already matches the shape expected by BaseVectorMap.

  function clearCache(): void { // WHAT: Expose helper to purge cached payloads when backend data changes.
    cache.value.clear() // WHAT: Remove all cache entries to force fresh fetch on next request.
  } // WHAT: Close clearCache helper.

  return { // WHAT: Public API of the Pinia store exposing state, getters, and actions.
    markers, // WHAT: Export raw marker array for debugging or alternative UI consumption.
    loading, // WHAT: Export loading flag so components can show busy indicators.
    error, // WHAT: Export error message for inline notifications.
    vectorMarkers, // WHAT: Export computed markers ready for jsVectorMap consumption.
    fetchMarkers, // WHAT: Export action to load markers from backend with caching.
    clearCache, // WHAT: Export helper to clear cache manually when necessary.
    lastKey, // WHAT: Export last cache key for observability and dev tooling.
  } // WHAT: Close returned object literal.
}) // WHAT: Finalize store factory invocation.
