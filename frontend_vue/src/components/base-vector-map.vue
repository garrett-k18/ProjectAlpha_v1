<template>
  <div :id="id" :style="`height: ${mapHeight}px`"></div>
</template>

<script lang="ts">
// Modern replacement: jsVectorMap (no jQuery dependency)
// Docs: https://github.com/themustafaomar/jsvectormap
import jsVectorMap from 'jsvectormap'
import 'jsvectormap/dist/maps/world.js'
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
    markers: {
      type: Array,
      default: () => []
    },
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
    try {
      if (this.mapInstance && typeof this.mapInstance.destroy === 'function') {
        this.mapInstance.destroy()
      }
      this.mapInstance = null
    } catch (e) {
      console.debug('[BaseVectorMap] beforeUnmount cleanup failed', e)
    }
  },
  watch: {
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
      const raw = Array.isArray(this.markers) ? (this.markers as any[]) : []
      const normalized = raw
        .map((m: any) => {
          const coords = Array.isArray(m?.coords) ? m.coords : m?.latLng
          const lat = Array.isArray(coords) ? Number(coords[0]) : NaN
          const lng = Array.isArray(coords) ? Number(coords[1]) : NaN
          if (!Number.isFinite(lat) || !Number.isFinite(lng)) return null
          const marker: any = { name: m?.name, coords: [lat, lng], id: m?.id }
          if (m?.style && typeof m.style === 'object') {
            const styleObj: any = m.style
            if (styleObj.initial || styleObj.hover || styleObj.selected || styleObj.selectedHover) {
              marker.style = styleObj
            } else {
              marker.style = { initial: styleObj }
            }
          }

          if (typeof m?.count !== 'undefined' || typeof m?.data !== 'undefined') {
            marker.data = { ...((m?.data && typeof m.data === 'object') ? m.data : {}), count: m?.count }
          }
          return marker
        })
        .filter(Boolean)
      const opts: any = { ...base, markers: normalized }

      try {
        if (this.mapInstance && typeof this.mapInstance.destroy === 'function') {
          this.mapInstance.destroy()
        }
        this.mapInstance = null
      } catch (e) {
        console.warn('[BaseVectorMap] previous map destroy failed', e)
      }

      try {
        const el = document.querySelector(selector) as HTMLElement | null
        if (el) el.innerHTML = ''
      } catch (e) {
        console.debug('[BaseVectorMap] container clear non-fatal', e)
      }

      try {
        this.mapInstance = new jsVectorMap({
          selector,
          ...opts,
        })
        if (opts && (opts as any).focusOn && this.mapInstance && typeof this.mapInstance.setFocus === 'function') {
          try {
            this.mapInstance.setFocus((opts as any).focusOn)
          } catch (err) {
            console.warn('[BaseVectorMap] setFocus failed', err)
          }
        }
        const preSel = (opts as any)?.selectedRegions
        if (preSel && Array.isArray(preSel)) {
          try {
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
        console.error('[BaseVectorMap] render failed', e)
      }
    },
  },
}
</script>