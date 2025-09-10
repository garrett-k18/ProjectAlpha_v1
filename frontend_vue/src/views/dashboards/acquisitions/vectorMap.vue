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
            :key="mapKey"
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
// Vector map + Top 10 States chart (counts) for the acquisitions dashboard
// Docs reviewed:
// - Pinia: https://pinia.vuejs.org/core-concepts/
// - Vue Options API with setup: https://vuejs.org/api/options-state.html#setup
// - jVectorMap API (markers/options): https://jvectormap.com/documentation/javascript-api/
// - ApexCharts Vue: https://apexcharts.com/docs/vue-charts/

import BaseVectorMap from "@/components/base-vector-map.vue";
import StratsStates from "./strats/strats-states.vue";
import { useAcqSelectionsStore } from "@/stores/acqSelections";
import { useStateSummariesStore } from "@/stores/stateSummaries";
// no-op

export default {
  components: { BaseVectorMap, StratsStates },
  // Use setup to access Pinia stores while keeping an Options API component
  setup() {
    const acqStore = useAcqSelectionsStore();
    const summariesStore = useStateSummariesStore();

    // Access getters/state directly to avoid TS lint friction around storeToRefs<any>
    const topCounts = summariesStore.topCounts // retained for potential future use
    const summariesLoading = summariesStore.loading // retained; embedded table will fetch/cached
    const summariesError = summariesStore.error

    return {
      // Expose the store instance to use its reactive state/getters directly
      acqStore,
      // Actions
      fetchMarkers: acqStore.fetchMarkers,
      fetchSummaries: summariesStore.fetchAll,
      // State summaries
      topCounts,
      summariesLoading,
      summariesError,
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
      // Local version to force remount on marker updates
      mapVersion: 0
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
    mapKey(): string {
      const len = Array.isArray(this.markersForMap) ? this.markersForMap.length : 0
      return `${this.selectionKey}:${len}:${this.mapVersion}`
    },
    
  },
  mounted() {
    // Initial fetch once mounted, if both seller and trade are selected
    this.fetchMarkersIfReady();
    this.fetchSummariesIfReady();
  },
  watch: {
    // When the seller/trade selection pair changes, keep data in sync
    selectionKey() {
      this.fetchMarkersIfReady();
      this.fetchSummariesIfReady();
    },
    // When the raw markers array in the store changes, bump version to force remount
    'acqStore.markers': {
      handler(newVal: any[]) {
        const len = Array.isArray(newVal) ? newVal.length : (Array.isArray((newVal as any)?.value) ? (newVal as any).value.length : 0)
        console.debug('[VectorMap] store markers changed', { len })
        this.mapVersion++
      },
      deep: false
    }
  },
  methods: {
    // Fetch markers only when both selections are present.
    fetchMarkersIfReady() {
      if (this.hasBothSelections) {
        console.debug('[VectorMap] fetchMarkersIfReady calling fetchMarkers')
        this.fetchMarkers();
      }
    },
    // Ensure state summaries are available for chart
    fetchSummariesIfReady() {
      if (this.hasBothSelections) {
        const sid = this.selectedSellerId as number
        const tid = this.selectedTradeId as number
        if (sid && tid) {
          console.debug('[VectorMap] fetchSummariesIfReady calling fetchSummaries', { sid, tid })
          this.fetchSummaries(sid, tid)
        }
      }
    }
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
