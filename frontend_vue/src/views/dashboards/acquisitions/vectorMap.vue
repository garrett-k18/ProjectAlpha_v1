<template>
  <div class="card">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Asset Dispersion</h4>
      <div class="float-end">
        <b-dropdown toggle-class="arrow-none card-drop p-0" variant="dark" right>
          <template v-slot:button-content>
            <i class="mdi mdi-dots-vertical"></i>
          </template>
          <b-dropdown-item href="javascript:void(0);">Refresh Report</b-dropdown-item>
          <b-dropdown-item href="javascript:void(0);">Export Report</b-dropdown-item>
        </b-dropdown>
      </div>
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
          <!-- Column headers for upcoming metrics (chart reflects Count) -->
          <b-row class="mb-2">
            <b-col cols="3"><small class="text-muted fw-semibold">Count</small></b-col>
            <b-col cols="3" class="text-end"><small class="text-muted fw-semibold">Current Balance</small></b-col>
            <b-col cols="3" class="text-end"><small class="text-muted fw-semibold">Total Debt</small></b-col>
            <b-col cols="3" class="text-end"><small class="text-muted fw-semibold">Seller As-Is Value</small></b-col>
          </b-row>
          <!-- Loading / Error / Empty states for summaries -->
          <div v-if="summariesLoading" class="text-center my-2">
            <small class="text-muted">Loading state summaries…</small>
          </div>
          <div v-else-if="summariesError" class="text-danger my-2">
            <small>{{ summariesError }}</small>
          </div>
          <div v-else-if="topCountsVal.counts.length === 0 && hasBothSelections" class="text-muted my-2">
            <small>No state data for this selection.</small>
          </div>

          <!-- Updated to show Top 10 States by COUNT (not percentage) -->
          <BaseApexChart :key="chartKey" :height="320" :series="chartSeries" :options="chartOptions"/>
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
import BaseApexChart from "@/components/base-apex-chart.vue";
import { useAcqSelectionsStore } from "@/stores/acqSelections";
import { useStateSummariesStore } from "@/stores/stateSummaries";
// no-op

export default {
  components: { BaseApexChart, BaseVectorMap },
  // Use setup to access Pinia stores while keeping an Options API component
  setup() {
    const acqStore = useAcqSelectionsStore();
    const summariesStore = useStateSummariesStore();

    // Access getters/state directly to avoid TS lint friction around storeToRefs<any>
    const topCounts = summariesStore.topCounts
    const summariesLoading = summariesStore.loading
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
        // Allow selecting markers (visual feedback)
        markersSelectable: true
      }
      ,
      // Local version to force remount on marker updates
      mapVersion: 0
    }
  },
  computed: {
    /**
     * topCountsVal
     * Normalizes store's computed getter regardless of ref auto-unwrapping.
     */
    topCountsVal(): { labels: string[]; counts: number[]; maxCount: number } {
      const tc: any = (this as any).topCounts
      const val = (tc && typeof tc.value !== 'undefined') ? tc.value : tc
      return val || { labels: [], counts: [], maxCount: 0 }
    },
    /**
     * selectionKey and flags proxied from the store to ensure reactivity
     */
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
    /**
     * chartKey
     * Force remount of ApexChart when labels/counts change to avoid stale options.
     */
    chartKey(): string {
      const tc = this.topCountsVal
      const labels = Array.isArray(tc.labels) ? tc.labels.join('|') : ''
      const counts = Array.isArray(tc.counts) ? tc.counts.join('|') : ''
      return `${this.selectionKey}:${labels}:${counts}`
    },
    /**
     * maxCount
     * The maximum count across topStates, used to set axis range and integer ticks.
     */
    maxCount(): number {
      const arr = this.topCountsVal.counts
      if (!arr || arr.length === 0) return 0
      return Math.max(...arr)
    },

    /**
     * chartSeries
     * ApexCharts series for Top 10 States by count (integers)
     */
    chartSeries(): Array<{ name: string; data: number[] }> {
      return [
        { name: 'Count', data: this.topCountsVal.counts }
      ]
    },

    /**
     * chartOptions
     * ApexCharts options configured for horizontal bar and integer count labels
     */
    chartOptions(): Record<string, any> {
      const max = this.maxCount
      const hasCats = (this.topCountsVal.labels || []).length > 0
      // Compute a "nice" rounded-up max so tiny values (e.g., 1) remain near 0 visually
      const niceCeil = (x: number): number => {
        if (!x || x <= 0) return 0
        if (x <= 10) return 10
        const mag = Math.pow(10, Math.floor(Math.log10(x)))
        const n = x / mag
        let step: number
        if (n <= 1) step = 1
        else if (n <= 2) step = 2
        else if (n <= 5) step = 5
        else step = 10
        return step * mag
      }
      // Baseline so single small counts (e.g., 1) render near 0 instead of spanning too much
      const BASELINE_MAX = 100
      const axisMax = max > 0 ? Math.max(niceCeil(max), BASELINE_MAX) : BASELINE_MAX
      // Keep integer ticks; fewer ticks for large ranges
      const tickAmount = axisMax <= 10 ? axisMax : 5
      return {
        chart: {
          type: 'bar',
          height: 320,
          toolbar: { show: false },
        },
        plotOptions: {
          // Make the horizontal bar extremely thin, roughly equal to y-axis label height
          // Docs: https://apexcharts.com/docs/options/plotoptions/bar/#barHeight
          // Use a fixed pixel value so single-bar charts don't get fat due to % of available height
          bar: {
            horizontal: true,
            barHeight: '12px',
            // Place the data label text inside the bar for a clean look
            // Docs: https://apexcharts.com/docs/options/plotoptions/bar/#datalabels
            dataLabels: { position: 'center' }
          }
        },
        colors: ['#727cf5'],
        // Disable data labels to avoid numbers on bars; values are visible in tooltip
        // Docs: https://apexcharts.com/docs/options/datalabels/
        dataLabels: {
          enabled: false,
        },
        xaxis: {
          categories: this.topCountsVal.labels,
          min: 0,
          // Fix to a rounded-up nice max with a minimum baseline to keep tiny bars tiny
          max: axisMax,
          tickAmount,
          axisBorder: { show: false },
          axisTicks: { show: false },
          labels: {
            // Hide numeric x-axis tick labels; we show values inside bars instead
            show: false,
            style: { fontSize: '12px' }
          }
        },
        yaxis: {
          labels: {
            show: hasCats,
            offsetY: 0,
            style: { fontSize: '12px', colors: ['#343a40'] },
            formatter: (val: string) => hasCats ? String(val) : ''
          }
        },
        grid: {
          strokeDashArray: 3,
          borderColor: 'rgba(108, 117, 125, 0.2)'
        },
        tooltip: {
          y: {
            // Integer tooltips
            formatter: (val: number) => Math.round(val).toString()
          }
        }
      }
    }
  },
  mounted() {
    // Debug: verify labels we pass to ApexCharts
    console.debug('[VectorMap] initial topCounts.labels', this.topCountsVal.labels)
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
    // Log when topCountsVal updates to verify labels and counts
    topCountsVal(val) {
      try {
        console.debug('[VectorMap] topCounts updated', { labels: val?.labels, countsLen: val?.counts?.length })
      } catch {}
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
