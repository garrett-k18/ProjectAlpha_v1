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
      // Destroy previous map instance by clearing container and recreating
      // This approach avoids relying on internal mapObject methods.
      $(el).empty()
      $(el).vectorMap(opts)
    }
  }
}
</script>