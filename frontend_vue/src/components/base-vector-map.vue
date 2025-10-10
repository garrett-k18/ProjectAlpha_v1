<template>
  <div :id="id" :style="`height: ${mapHeight}px`"></div>
</template>

<script lang="ts">
// Modern replacement: jsVectorMap (no jQuery dependency)
// Docs: https://github.com/themustafaomar/jsvectormap
import jsVectorMap from 'jsvectormap'
// Import map assets
import 'jsvectormap/dist/maps/world.js'
// Import custom US map (downloaded separately and stored in assets)
import '@/assets/maps/us-mill-en.js'

export default {
  props: {
    id: {
      type: String,
      require: true
    },
    mapHeight: {
      type: Number,
      default: 217,
    },
    options: {
      type: Object,
      require: true
    },
    // Optional markers array. Format: [{ latLng: [lat, lng], name: string }, ...]
    // jVectorMap docs: https://jvectormap.com/documentation/javascript-api/#markers
    markers: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      mapInstance: null as any,
    }
  },
  mounted() {
    if (this.id) {
      this.renderMap()
    }
  },
  beforeUnmount() {
    // Clean up any existing jsVectorMap instance to avoid memory leaks
    try {
      if (this.mapInstance && typeof this.mapInstance.destroy === 'function') {
        this.mapInstance.destroy()
      }
      this.mapInstance = null
    } catch (e) {
      console.debug('[BaseVectorMap] beforeUnmount cleanup failed (non-fatal)', e)
    }
  },
  watch: {
    // Re-render the map when options or markers change.
    options: {
      handler() {
        this.renderMap()
      },
      deep: true
    },
    markers: {
      handler() {
        this.renderMap()
      },
      deep: true
    }
  },
  methods: {
    renderMap() {
      const selector = `#${this.id}`
      const base = this.options || {}
      // Normalize markers to jsVectorMap shape: { name, coords: [lat, lng] }
      const raw = Array.isArray(this.markers) ? this.markers as any[] : []
      const normalized = raw
        .map((m: any) => {
          const coords = Array.isArray(m?.coords) ? m.coords : m?.latLng
          const lat = Array.isArray(coords) ? Number(coords[0]) : NaN
          const lng = Array.isArray(coords) ? Number(coords[1]) : NaN
          if (!Number.isFinite(lat) || !Number.isFinite(lng)) return null
          return { name: m?.name, coords: [lat, lng], id: m?.id }
        })
        .filter(Boolean)
      // Merge into options without mutating parent
      const opts: any = { ...base, markers: normalized }

      // Destroy previous instance if any
      try {
        if (this.mapInstance && typeof this.mapInstance.destroy === 'function') {
          this.mapInstance.destroy()
        }
        this.mapInstance = null
      } catch (e) {
        console.warn('[BaseVectorMap] previous map destroy failed', e)
      }

      // Initialize jsVectorMap
      try {
        console.debug('[BaseVectorMap] render', {
          id: this.id,
          map: opts?.map,
          markersCount: Array.isArray(this.markers) ? this.markers.length : 0,
          firstMarker: Array.isArray(this.markers) ? this.markers[0] : null,
        })
        this.mapInstance = new jsVectorMap({
          selector,
          ...opts,
        })
        // Optional focus handling to zoom into regions (e.g., US) when using world map
        if (opts && (opts as any).focusOn && this.mapInstance && typeof this.mapInstance.setFocus === 'function') {
          try {
            this.mapInstance.setFocus((opts as any).focusOn)
          } catch (err) {
            console.warn('[BaseVectorMap] setFocus failed', err)
          }
        }
        // Optional pre-selected regions (e.g., highlight only US)
        const preSel = (opts as any)?.selectedRegions
        if (preSel && Array.isArray(preSel)) {
          try {
            // Try common APIs supported by jsVectorMap versions
            if (typeof (this.mapInstance as any).setSelectedRegions === 'function') {
              ;(this.mapInstance as any).setSelectedRegions(preSel)
            } else if (typeof (this.mapInstance as any).setSelected === 'function') {
              ;(this.mapInstance as any).setSelected('regions', preSel)
            }
          } catch (err) {
            console.warn('[BaseVectorMap] setSelectedRegions failed', err)
          }
        }
      } catch (e) {
        console.error('[BaseVectorMap] jsVectorMap init failed', e, opts)
      }
    }
  }
}
</script>