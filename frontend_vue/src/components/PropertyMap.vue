<template>
  <!--
    <!--
    PropertyMap.vue
    Purpose: Display a Google Map centered on the property's geocoded address.
    Works with either a provided `row` object (modal context) or a `productId`
    (full-page context, where this component will fetch the row itself).
    Uses vue3-google-map with an external async loader and a Vite env API key.
    Useful in Asset Management -> Loan-Level -> Snapshot tab.
    -->
  -->
  <div :class="bare ? '' : 'card'">
    <div :class="['d-flex', 'flex-column', 'p-0', 'h-100', 'position-relative', bare ? '' : 'card-body pt-0']">
      <!-- Map fills entire card body (no header) -->
      <div :class="['position-absolute', 'top-0', 'bottom-0', 'start-0', 'end-0']" :style="containerStyle">
        <template v-if="viewMode === 'map'">
          <GoogleMap
            :api-promise="googleApiPromise"
            :zoom="zoom"
            :center="effectiveCenter"
            :street-view-control="true"
            :map-type-control="true"
            :map-type-id="defaultMapType"
            :fullscreen-control="true"
            :zoom-control="true"
            :clickable-icons="false"
            :disable-default-ui="false"
            :map-id="mapId"
            :style="{ height: '100%', width: '100%' }"
          >
            <!-- Use AdvancedMarker when a vector Map ID is configured; otherwise fall back to legacy Marker -->
            <AdvancedMarker v-if="showMarker && markerPosition && useAdvanced" :options="{ position: markerPosition }" />
            <Marker v-else-if="showMarker && markerPosition" :options="{ position: markerPosition }" />
          </GoogleMap>
        </template>
        <template v-else>
          <!-- Street-only view via Google Maps Embed API. Requires the same API key to have Embed API enabled. -->
          <iframe
            v-if="panoramaPosition && embedStreetUrl"
            :src="embedStreetUrl"
            style="border:0; height: 100%; width: 100%;"
            allowfullscreen
            loading="lazy"
            referrerpolicy="no-referrer-when-downgrade"
          ></iframe>
          <div v-else class="text-muted small m-2">Street View not available for this location.</div>
        </template>
        <div v-if="geocodeError" class="text-danger small m-2">{{ geocodeError }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Imports at the top: Vue 3 Composition API and vue3-google-map components.
import { computed, ref, watch, watchEffect, withDefaults, defineProps } from 'vue'
import { GoogleMap, Marker, AdvancedMarker } from 'vue3-google-map'
import { googleApiPromise } from '@/lib/googleMapsLoader'
import http from '@/lib/http'

// Narrow type for Google Map type id to avoid stringly-typed usage
type MapType = 'roadmap' | 'satellite' | 'hybrid' | 'terrain'

// Props with defaults. Keep this component reusable and self-sufficient.
const props = withDefaults(defineProps<{
  // Optional backing data row (modal usage)
  row?: Record<string, any> | null
  // Optional id to fetch the row (full-page usage)
  productId?: string | number | null
  // Optional address parts; if not supplied, derived from row
  address?: string | null
  city?: string | null
  state?: string | null
  zip?: string | null
  // Map presentation
  zoom?: number
  height?: number | string
  showMarker?: boolean
  /** Default base map type; allows built-in toggle to Satellite/Map without custom JS */
  defaultMapType?: MapType
  /** When true, render without the outer card wrapper for embedding inside existing cards */
  bare?: boolean
  /** When 'street', render Street View panorama instead of map */
  viewMode?: 'map' | 'street'
}>(), {
  row: null,
  productId: null,
  address: null,
  city: null,
  state: null,
  zip: null,
  zoom: 14,
  height: 300,
  showMarker: true,
  defaultMapType: 'roadmap',
  bare: false,
  viewMode: 'map',
})

// Read API key from Vite env (kept for potential future usage)
const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY as string | undefined
// Vector Map ID enables AdvancedMarker and vector basemap styling
const mapId = import.meta.env.VITE_GMAPS_MAP_ID as string | undefined
// Prefer AdvancedMarker when a Map ID is available; otherwise fall back
const useAdvanced = computed<boolean>(() => {
  return !!mapId
})

// Local state for fallback-fetched row when `row` prop is not provided
const fetchedRow = ref<Record<string, any> | null>(null)

// Effective row resolves to `props.row` (modal) or fetchedRow (full-page)
const effectiveRow = computed(() => props.row ?? fetchedRow.value)

// Build a single-line address string from explicit props or from the row
const fullAddress = computed<string | null>(() => {
  // Prefer explicit address inputs if provided
  const addr = props.address ?? effectiveRow.value?.street_address
  const city = props.city ?? effectiveRow.value?.city
  const state = props.state ?? effectiveRow.value?.state
  const zip = props.zip ?? effectiveRow.value?.zip

  if (!addr && !city && !state && !zip) return null
  return [addr, city, state, zip].filter(Boolean).join(', ')
})

// Map center and marker position. Start as null until geocode resolves.
const mapCenter = ref<{ lat: number; lng: number } | null>(null)
const markerPosition = ref<{ lat: number; lng: number } | null>(null)
const geocodeError = ref<string>('')

// Resolve a concrete CSS height for the container so loading/fallback also have space
const containerStyle = computed(() => {
  const h = props.height
  const heightCss = typeof h === 'number' ? `${h}px` : (h || '300px')
  return { height: heightCss, width: '100%' }
})

// Provide a sane default center so the map can render immediately
const defaultCenter = { lat: 39.5, lng: -98.35 } // Approximate center of the contiguous US
const effectiveCenter = computed(() => mapCenter.value ?? defaultCenter)

// Street View uses a LatLng position; prefer precise marker, fallback to effective center
const panoramaPosition = computed(() => markerPosition.value ?? effectiveCenter.value)

// Build Google Maps Embed API Street View URL when in 'street' mode
const embedStreetUrl = computed<string | null>(() => {
  if (props.viewMode !== 'street' || !apiKey || !panoramaPosition.value) return null
  const { lat, lng } = panoramaPosition.value
  // Customize POV/fov if desired; defaults are fine
  const params = new URLSearchParams({
    key: apiKey,
    location: `${lat},${lng}`,
    // fov: '80', heading: '0', pitch: '0' // optional
  })
  return `https://www.google.com/maps/embed/v1/streetview?${params.toString()}`
})

// Fetch the row by id when needed
async function loadRowById(id: number) {
  try {
    const res = await http.get(`/acq/raw-data/by-id/${id}/`)
    fetchedRow.value = res.data && Object.keys(res.data).length ? res.data : null
    // eslint-disable-next-line no-console
    console.debug('[PropertyMap] loaded row for', id)
  } catch (err) {
    // eslint-disable-next-line no-console
    console.warn('[PropertyMap] failed to load row for', id, err)
    fetchedRow.value = null
  }
}

// Trigger fetch if we have no row but do have an id
watch(
  () => props.productId,
  (raw) => {
    const id = raw != null ? Number(raw) : NaN
    if (!props.row && Number.isFinite(id)) {
      loadRowById(id)
    }
  },
  { immediate: true }
)

// Geocode helper using Google Geocoding REST API for reliability
async function geocode(address: string) {
  // Clear previous state
  geocodeError.value = ''
  mapCenter.value = null
  markerPosition.value = null

  if (!apiKey) {
    geocodeError.value = 'Missing Google Maps API key (VITE_GOOGLE_MAPS_API_KEY).'
    return
  }
  try {
    const url = `https://maps.googleapis.com/maps/api/geocode/json?address=${encodeURIComponent(address)}&key=${apiKey}`
    const resp = await fetch(url)
    const data = await resp.json()
    if (data.status !== 'OK' || !data.results?.length) {
      geocodeError.value = `Geocoding failed: ${data.status}`
      return
    }
    const loc = data.results[0].geometry.location
    mapCenter.value = { lat: loc.lat, lng: loc.lng }
    markerPosition.value = { lat: loc.lat, lng: loc.lng }
  } catch (e: any) {
    geocodeError.value = 'Failed to contact Geocoding API.'
  }
}

// Whenever the fullAddress becomes available/changes, geocode it
watchEffect(() => {
  if (fullAddress.value) {
    geocode(fullAddress.value)
  }
})
</script>
