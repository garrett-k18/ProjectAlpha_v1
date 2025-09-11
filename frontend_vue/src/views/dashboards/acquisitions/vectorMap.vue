<!-- This Vue component displays a map with markers for each state in the pool
     and a chart showing the states by count -->



<template>
  <div class="card">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Asset Dispersion</h4>
      <div class="d-flex align-items-center"><!-- controls removed by request --></div>
    </div>

    <div class="card-body pt-0">
      <b-row>
        <b-col lg="8">
          <BaseVectorMap
            id="acq-vector-map"
            class="mt-3 mb-3"
            :map-height="300"
            :options="mapOptions"
            :markers="markersForMap"
          />
        </b-col>
        <b-col lg="4" dir="ltr">
          <!-- Replace Apex chart with embedded state strat table (scrollable) -->
          <StratsStates :embedded="true" />
        </b-col>
      </b-row>
    </div>
  </div>
</template>

<script lang="ts">
// Vector map + embedded State Strat table for the acquisitions dashboard
// Docs reviewed:
// - Pinia: https://pinia.vuejs.org/core-concepts/
// - Vue Options API with setup: https://vuejs.org/api/options-state.html#setup
// - jVectorMap API (markers/options): https://jvectormap.com/documentation/javascript-api/
// - ApexCharts Vue: https://apexcharts.com/docs/vue-charts/

import BaseVectorMap from "@/components/base-vector-map.vue";
import StratsStates from "./strats/strats-states.vue";
import { useAcqSelectionsStore } from "@/stores/acqSelections";
// no-op

export default {
  components: { BaseVectorMap, StratsStates },
  // Use setup to access Pinia stores while keeping an Options API component
  setup() {
    const acqStore = useAcqSelectionsStore();

    return {
      // Expose the store instance to use its reactive state/getters directly
      acqStore,
      // Actions
      fetchMarkers: acqStore.fetchMarkers,
    };
  },
  data() {
    return {
      // jVectorMap options for US mercator map with visible markers
      mapOptions: {
        map: 'us_merc_en',
        normalizeFunction: 'polynomial',
        hoverOpacity: 0.7,
        hoverColor: false,
        regionStyle: {
          initial: {
            fill: '#91a6bd40'
          }
        },
        // High-visibility marker styling
        markerStyle: {
          initial: {
            r: 6,
            fill: '#e83e8c',
            stroke: '#ffffff',
            'stroke-width': 2,
            'fill-opacity': 1
          },
          hover: {
            fill: '#ff6fa8',
            'stroke-width': 2
          },
          selected: {
            fill: '#d63384'
          }
        },
        // Keep background transparent; disable scroll zoom
        backgroundColor: 'transparent',
        zoomOnScroll: false,
        zoomButtons: false,
        // Allow selecting markers (visual feedback)
        markersSelectable: true
      }
      ,
      // No explicit version; rely on BaseVectorMap internal updates
    }
  },
  computed: {
    /** selectionKey and flags proxied from the store to ensure reactivity */
    selectionKey(): string {
      const v = (this.acqStore as any).selectionKey
      return typeof v?.value !== 'undefined' ? v.value : v
    },
    hasBothSelections(): boolean {
      const v = (this.acqStore as any).hasBothSelections
      return typeof v?.value !== 'undefined' ? v.value : v
    },
    selectedSellerId(): number | null {
      const v = (this.acqStore as any).selectedSellerId
      return typeof v?.value !== 'undefined' ? v.value : v
    },
    selectedTradeId(): number | null {
      const v = (this.acqStore as any).selectedTradeId
      return typeof v?.value !== 'undefined' ? v.value : v
    },
    /**
     * mapKey
     * Force remount of BaseVectorMap when either selection changes or
     * markers length changes (ensures jVectorMap re-inits with markers).
     */
    // Build vector map markers from raw store markers to avoid getter unwrap issues
    markersForMap(): any[] {
      const raw = Array.isArray((this.acqStore as any).markers)
        ? (this.acqStore as any).markers
        : ((this.acqStore as any).markers?.value ?? [])
      const safe = Array.isArray(raw) ? raw : []
      const out = safe
        .map((m: any) => {
          const lat = typeof m?.lat === 'string' ? parseFloat(m.lat) : m?.lat
          const lng = typeof m?.lng === 'string' ? parseFloat(m.lng) : m?.lng
          return { latLng: [lat, lng], name: m?.name, id: m?.id }
        })
        .filter((mk: any) => Number.isFinite(mk.latLng?.[0]) && Number.isFinite(mk.latLng?.[1]))
      console.debug('[VectorMap] markersForMap', { rawCount: safe.length, count: out.length, first: out[0] })
      return out
    },
    
  },
  mounted() {
    // Initial fetch once mounted, if both seller and trade are selected
    this.fetchMarkersIfReady();
  },
  watch: {
    // When the seller/trade selection pair changes, keep data in sync
    selectionKey() {
      const key = this.selectionKey
      console.count(`[VectorMap] selectionKey changed`)
      this.fetchMarkersIfReady()
      // Note: summaries are fetched exclusively by <StratsStates/> embedded component
    },
    // Removed remount-on-markers-change to reduce re-render churn
  },
  methods: {
    // Fetch markers only when both selections are present.
    async fetchMarkersIfReady() {
      if (this.hasBothSelections) {
        const sid = this.selectedSellerId as number
        const tid = this.selectedTradeId as number
        const label = `[VectorMap] markers ${sid}:${tid}`
        console.time(label)
        try {
          console.debug('[VectorMap] fetchMarkersIfReady calling fetchMarkers', { sid, tid })
          await this.fetchMarkers()
        } finally {
          console.timeEnd(label)
        }
      }
    },
  }
}
</script>

<style scoped>
/* Hide jVectorMap zoom buttons for this specific map instance */
#acq-vector-map :deep(.jvectormap-zoomin),
#acq-vector-map :deep(.jvectormap-zoomout) {
  display: none !important;
}
</style>
