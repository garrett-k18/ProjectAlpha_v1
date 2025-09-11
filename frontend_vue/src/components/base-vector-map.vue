<template>
  <div :id="id" :style="`height: ${mapHeight}px`"></div>
</template>

<script lang="ts">
import $ from 'jquery'
import "admin-resources/jquery.vectormap/jquery-jvectormap-1.2.2.min.js";
import "admin-resources/jquery.vectormap/maps/jquery-jvectormap-world-mill-en.js";
import "admin-resources/jquery.vectormap/maps/jquery-jvectormap-us-merc-en.js";
import "admin-resources/jquery.vectormap/maps/jquery-jvectormap-in-mill-en.js";
import "admin-resources/jquery.vectormap/maps/jquery-jvectormap-au-mill-en.js";
import "admin-resources/jquery.vectormap/maps/jquery-jvectormap-uk-mill-en.js";
import "admin-resources/jquery.vectormap/maps/jquery-jvectormap-us-il-chicago-mill-en.js";
import "admin-resources/jquery.vectormap/maps/jquery-jvectormap-ca-lcc-en.js";
import "admin-resources/jquery.vectormap/maps/jquery-jvectormap-europe-mill-en.js";
import "admin-resources/jquery.vectormap/maps/jquery-jvectormap-fr-merc-en.js";
import "admin-resources/jquery.vectormap/maps/jquery-jvectormap-es-merc.js";
import "admin-resources/jquery.vectormap/maps/jquery-jvectormap-es-mill.js";

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
  mounted() {
    if (this.id) {
      this.renderMap()
    }
  },
  beforeUnmount() {
    // Clean up any existing jVectorMap instance to avoid memory leaks
    try {
      const $el = $("#" + this.id)
      const existing = ($el as any).data('mapObject')
      if (existing && typeof existing.remove === 'function') {
        existing.remove()
      }
      $el.empty()
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
      const el = `#${this.id}`
      const base = this.options || {}
      // Merge markers into options without mutating parent object
      const opts = { ...base, markers: this.markers }

      const $el = $(el)
      // Try to remove any existing map instance first (per jVectorMap API)
      // Docs: https://jvectormap.com/documentation/javascript-api/#destroy
      try {
        const existing = ($el as any).data('mapObject')
        if (existing && typeof existing.remove === 'function') {
          existing.remove()
        }
      } catch (e) {
        // Non-fatal cleanup failure
        console.warn('[BaseVectorMap] previous map remove failed', e)
      }

      // Clear container then initialize
      $el.empty()
      try {
        console.debug('[BaseVectorMap] render', {
          id: this.id,
          map: (opts as any)?.map,
          markersCount: Array.isArray(this.markers) ? this.markers.length : 0,
          firstMarker: Array.isArray(this.markers) ? this.markers[0] : null,
        })
        ;($el as any).vectorMap(opts)
      } catch (e) {
        console.error('[BaseVectorMap] vectorMap init failed', e, opts)
      }
    }
  }
}
</script>