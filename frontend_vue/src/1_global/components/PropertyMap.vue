<template>
  <!--
    PropertyMap.vue
    Purpose: Display a Google Map centered on the property's geocoded address.
    Works with either a provided `row` object (modal context) or a `productId`
    (full-page context, where this component will fetch the row itself).
    Uses vue3-google-map and a Vite env API key.
  -->
  <div class="card">
    <div class="card-body d-flex flex-column p-0">
      <!-- Map fills entire card body (no header) -->
      <div class="flex-grow-1">
        <GoogleMap
          v-if="apiKey && mapCenter"
          :api-key="apiKey"
          :zoom="zoom"
          :center="mapCenter"
          :street-view-control="true"
          :map-type-control="true"
          :map-type-id="defaultMapType"
          :fullscreen-control="true"
          :zoom-control="true"
          :clickable-icons="false"
          :disable-default-ui="false"
          :style="{ height: typeof height === 'number' ? `${height}px` : (height || '100%'), width: '100%' }"
        >
          <Marker v-if="showMarker && markerPosition" :options="{ position: markerPosition }" />
        </GoogleMap>
        <div v-else class="text-muted small d-flex align-items-center justify-content-center h-100">Loading map…</div>

        <div v-if="geocodeError" class="text-danger small m-2">{{ geocodeError }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Imports at the top: Vue 3 Composition API and vue3-google-map components.
import { computed, ref, watch, watchEffect, withDefaults, defineProps } from 'vue'
import { GoogleMap, Marker } from 'vue3-google-map'
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
})

// Read API key from Vite env. This is required by vue3-google-map to load Maps JS API.
const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY as string | undefined

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
