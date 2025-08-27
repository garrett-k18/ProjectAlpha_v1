<template>
  <div class="card">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">State Stats</h4>
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
          <!-- Updated to show Top 10 States by COUNT (not percentage) -->
          <BaseApexChart :height="320" :series="chartSeries" :options="chartOptions"/>
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
import { useAgGridRowsStore } from "@/stores/agGridRows";
import { storeToRefs } from 'pinia'
import type { GridRow } from '@/stores/agGridRows'

export default {
  components: { BaseApexChart, BaseVectorMap },
  // Use setup to access Pinia stores while keeping an Options API component
  setup() {
    const acqStore = useAcqSelectionsStore();
    const gridRowsStore = useAgGridRowsStore();

    const { rows: gridRows } = storeToRefs(gridRowsStore);

    return {
      // Expose the store instance to use its reactive state/getters directly
      acqStore,
      // Actions
      fetchMarkers: acqStore.fetchMarkers,
      fetchRows: gridRowsStore.fetchRows,
      // Row dataset to aggregate Top 10 States
      gridRows,
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
     * selectionKey and flags proxied from the store to ensure reactivity
     */
    selectionKey(): string {
      return this.acqStore.selectionKey
    },
    hasBothSelections(): boolean {
      return this.acqStore.hasBothSelections
    },
    selectedSellerId(): number | null {
      return this.acqStore.selectedSellerId
    },
    selectedTradeId(): number | null {
      return this.acqStore.selectedTradeId
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
     * topStates
     * Aggregates the current grid rows by 'state' and returns the top 10.
     * Ensures integer counts only.
     */
    topStates(): { labels: string[]; counts: number[] } {
      const rows = (this.gridRows as GridRow[]) || []
      const counts = new Map<string, number>()

      for (const r of rows) {
        // Normalize the state value to a 2-char uppercase code when possible
        const raw = String((r as any)?.state ?? '').trim().toUpperCase()
        if (!raw) continue
        counts.set(raw, (counts.get(raw) || 0) + 1)
      }

      // Sort by count desc, take top 10
      const sorted = Array.from(counts.entries()).sort((a, b) => b[1] - a[1]).slice(0, 10)
      const labels = sorted.map(([st]) => st)
      const values = sorted.map(([, c]) => c)
      return { labels, counts: values }
    },

    /**
     * maxCount
     * The maximum count across topStates, used to set axis range and integer ticks.
     */
    maxCount(): number {
      const arr = this.topStates.counts
      if (!arr || arr.length === 0) return 0
      return Math.max(...arr)
    },

    /**
     * chartSeries
     * ApexCharts series for Top 10 States by count (integers)
     */
    chartSeries(): Array<{ name: string; data: number[] }> {
      return [
        { name: 'Count', data: this.topStates.counts }
      ]
    },

    /**
     * chartOptions
     * ApexCharts options configured for horizontal bar and integer count labels
     */
    chartOptions(): Record<string, any> {
      const max = this.maxCount
      // Prefer integer tick steps. If max is small, align tickAmount to max for step=1.
      const tickAmount = max > 0 ? (max <= 10 ? max : 10) : 4
      return {
        chart: {
          type: 'bar',
          height: 320,
          toolbar: { show: false },
        },
        plotOptions: {
          bar: { horizontal: true }
        },
        colors: ['#727cf5'],
        dataLabels: { enabled: false },
        xaxis: {
          categories: this.topStates.labels,
          min: 0,
          // When max is 0, let Apex auto-scale; otherwise fix to max to avoid fractional normalization
          ...(max > 0 ? { max } : {}),
          tickAmount,
          axisBorder: { show: false },
          labels: {
            // Force integer labels on the axis
            formatter: (val: number | string) => {
              const num = typeof val === 'number' ? val : parseFloat(String(val))
              if (Number.isNaN(num)) return String(val)
              return Math.round(num).toString()
            }
          }
        },
        tooltip: {
          y: {
            // Integer tooltips
            formatter: (val: number) => Math.round(val).toString()
          }
        },
        grid: { strokeDashArray: [5] }
      }
    }
  },
  mounted() {
    // Initial fetch once mounted, if both seller and trade are selected
    this.fetchMarkersIfReady();
    this.fetchRowsIfReady();
  },
  watch: {
    // When the seller/trade selection pair changes, keep data in sync
    selectionKey() {
      this.fetchMarkersIfReady();
      this.fetchRowsIfReady();
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
        this.fetchMarkers();
      }
    },
    // Ensure grid rows are available for aggregation (uses cached store data when present)
    fetchRowsIfReady() {
      if (this.hasBothSelections) {
        const sid = this.selectedSellerId as number
        const tid = this.selectedTradeId as number
        if (sid && tid) {
          this.fetchRows(sid, tid)
        }
      }
    }
  }
}
</script>
