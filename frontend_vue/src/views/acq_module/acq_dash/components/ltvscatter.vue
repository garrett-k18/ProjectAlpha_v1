<template>
  <div class="card d-flex flex-column w-100">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">LTV Scatter Chart</h4>
      <div class="d-flex align-items-center">
        <div v-if="isLoading" class="me-2">
          <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
    </div>

    <div class="card-body pt-0 position-relative" ref="containerRef">
      <!-- Always render chart container so ApexCharts mounts even with empty data -->
      <div class="w-100" style="min-width: 0; min-height: 350px;">
        <apexchart
          type="scatter"
          :width="containerWidth > 0 ? containerWidth : '100%'"
          height="350"
          :options="chartOptions"
          :series="series"
          :key="chartKey"
          v-show="containerReady"
        ></apexchart>
      </div>
      <!-- Overlay helper when there is no data and not loading -->
      <div v-if="!hasData && !isLoading" class="position-absolute top-50 start-50 translate-middle text-muted">
        No data available for selected pool
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed, ref, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
// ApexCharts core API for imperative updates (resize/exec)
// Docs: https://apexcharts.com/docs/methods/#exec
import ApexCharts from 'apexcharts'
import { useAcqSelectionsStore } from '@/stores/acqSelections'
import { useAgGridRowsStore } from '@/stores/agGridRows'
import { storeToRefs } from 'pinia'
// Use the centralized Axios instance which already has baseURL and interceptors
// Docs: https://axios-http.com/docs/instance
import http from '@/lib/http'

export default defineComponent({
  name: 'LtvScatterChart',

  setup() {
    // Get global selections from store
    const acqStore = useAcqSelectionsStore()
    const { selectedSellerId, selectedTradeId } = storeToRefs(acqStore)
    // Access cached grid rows for fallback rendering when API has no data
    const agRowsStore = useAgGridRowsStore()
    const { rows: gridRows } = storeToRefs(agRowsStore)
    
    // Loading state
    const isLoading = ref(false)
    
    // Define interface for loan data structure
    interface LoanItem {
      id: string;
      seller_asis_value: number;
      current_balance: number;
      ltv: number;
    }
    
    // Interface for backend API response
    interface ApiLoanItem {
      id: string;
      seller_asis_value: string; // Decimal values come as strings from JSON
      current_balance: string;
      ltv: string;
    }
    
    // Interface for chart axis configuration
    interface AxisOptions {
      title: { text: string; style: { fontWeight: number } };
      min: number;
      max?: number; // Optional max that can be set dynamically
      tickAmount: number;
      labels: { formatter: (val: number) => string };
      tooltip?: { enabled: boolean };
      forceNiceScale?: boolean;
    }
    
    // Chart options configuration with full type definition
    const chartOptions = ref({
      chart: {
        id: 'ltv-scatter',
        height: 350,
        toolbar: {
          show: true,
          tools: {
            download: true,
            selection: true,
            zoom: true,
            zoomin: true,
            zoomout: true,
            pan: true,
            reset: true
          }
        },
        zoom: {
          enabled: true,
          type: 'xy'
        },
        // Disable animations to avoid jank with large point counts
        animations: {
          enabled: false
        },
        // Set aspect ratio to make X and Y scales look the same
        aspectRatio: 1,
        // Show a friendly message when there is no series data
        // Docs: https://apexcharts.com/docs/options/no-data/
        // Note: some wrappers support noData at root level; placing under chart works reliably
        // with vue3-apexcharts via updateOptions
      },
      noData: {
        text: 'No data available',
        align: 'center',
        verticalAlign: 'middle',
        style: {
          color: '#6c757d',
        }
      },
      xaxis: {
        title: {
          text: 'Seller As-Is Value ($)',
          style: {
            fontWeight: 500
          }
        },
        min: 0,                 // Start x-axis at 0
        max: undefined,         // Will be set dynamically
        tickAmount: 6,          // Fewer, friendlier tick marks
        labels: {
          formatter: function(val: number): string {
            // Round to nearest 25K
            const roundedVal = Math.round(val / 25000) * 25000
            // Format as $500K instead of $500,000
            return '$' + (roundedVal >= 1000000 
              ? (roundedVal / 1000000).toFixed(1) + 'M' 
              : (roundedVal / 1000).toFixed(0) + 'K')
          }
        },
        tooltip: {
          enabled: false
        }
      },
      yaxis: {
        title: {
          text: 'Current Balance ($)',
          style: {
            fontWeight: 500
          }
        },
        min: 0,                 // Start y-axis at 0
        max: undefined,         // Will be dynamically set to match x-axis scale
        tickAmount: 6,          // Fewer, friendlier tick marks
        labels: {
          formatter: function(val: number): string {
            // Round to nearest 25K
            const roundedVal = Math.round(val / 25000) * 25000
            // Format as $500K instead of $500,000
            return '$' + (roundedVal >= 1000000 
              ? (roundedVal / 1000000).toFixed(1) + 'M' 
              : (roundedVal / 1000).toFixed(0) + 'K')
          }
        },
        forceNiceScale: true    // Force nice round numbers
      },
      tooltip: {
        custom: function({ series, seriesIndex, dataPointIndex, w }: {
          series: any,
          seriesIndex: number,
          dataPointIndex: number,
          w: any
        }): string {
          const data = w.config.series[seriesIndex].data[dataPointIndex]
          return `
            <div class="p-2">
              <div><strong>LTV:</strong> ${data[2]}%</div>
              <div><strong>Current Balance:</strong> $${new Intl.NumberFormat('en-US').format(data[1])}</div>
              <div><strong>Seller As-Is Value:</strong> $${new Intl.NumberFormat('en-US').format(data[0])}</div>
            </div>
          `
        }
      },
      markers: {
        // Smaller markers render significantly faster with thousands of points
        size: 4,
        shape: "circle",
        hover: {
          size: 6
        }
      },
      // Colors are now set per series
      grid: {
        borderColor: '#f1f3fa'
      },
      legend: {
        position: 'top',
        offsetY: 0,
        fontSize: '14px',
        markers: {
          width: 12,
          height: 12,
          radius: 6
        },
        itemMargin: {
          horizontal: 5,
          vertical: 8
        }
      },
      // Responsive overrides: move legend to top when width is constrained (two-column layout)
      responsive: [
        {
          breakpoint: 1400,
          options: {
            legend: {
              position: 'top',
              horizontalAlign: 'left',
              offsetY: 0,
            },
          }
        }
      ],
      dataLabels: {
        enabled: false
      }
    })

    // Track last selection (optional – used for logging/stability)
    let lastKey: string | null = null
    // Keep a controller to cancel in-flight requests when selection changes
    let currentController: AbortController | null = null
    // Key to force <apexchart> to remount when needed
    const chartKey = ref(0)
    // True when the container has a non-zero width so ApexCharts can compute layout
    const containerReady = ref(false)
    const containerWidth = ref(0)

    // Ensure container has a non-zero width before mounting/resizing the chart
    function ensureContainerReady(): void {
      try {
        const w = containerRef.value?.clientWidth || 0
        if (w > 0) {
          containerWidth.value = w
          if (!containerReady.value) {
            containerReady.value = true
            chartKey.value++
          }
          // Hint width/height to ApexCharts to avoid NaN during transitions
          try {
            ApexCharts.exec('ltv-scatter', 'updateOptions', { chart: { width: containerWidth.value, height: 350 } }, false, true)
          } catch {}
        }
      } catch {}
    }

    // Resize handling to ensure the chart expands when its container changes size
    const containerRef = ref<HTMLElement | null>(null)
    let ro: ResizeObserver | null = null
    let rafId: number | null = null

    function kickContainerMeasureLoop(maxTries = 30): void {
      let tries = 0
      const tick = () => {
        tries++
        ensureContainerReady()
        if (!containerReady.value && tries < maxTries) {
          rafId = requestAnimationFrame(tick)
        }
      }
      rafId = requestAnimationFrame(tick)
    }

    onMounted(() => {
      // Kick an initial resize so ApexCharts recalculates width after layout
      nextTick(() => {
        try { window.dispatchEvent(new Event('resize')) } catch {}
        // If container has width, allow chart to mount (and only then bump key)
        ensureContainerReady()
      })
      if (typeof window !== 'undefined' && 'ResizeObserver' in window) {
        ro = new ResizeObserver(() => {
          // Force chart to recompute dimensions; exec is more reliable than window resize alone
          ensureContainerReady()
          if (containerReady.value) {
            try { ApexCharts.exec('ltv-scatter', 'updateOptions', { chart: { width: containerWidth.value, height: 350 } }, false, true) } catch {}
            try { ApexCharts.exec('ltv-scatter', 'resize') } catch {}
            try { window.dispatchEvent(new Event('resize')) } catch {}
          }
        })
        if (containerRef.value) ro.observe(containerRef.value)
      }
      // If still not ready after initial mount, poll a few frames until width appears
      if (!containerReady.value) kickContainerMeasureLoop()
    })

    onBeforeUnmount(() => {
      try {
        if (ro && containerRef.value) ro.unobserve(containerRef.value)
      } catch {}
      ro = null
      if (rafId != null) { try { cancelAnimationFrame(rafId) } catch {} finally { rafId = null } }
    })

    // Maximum number of points to render; prevents UI stalls on very large pools
    const MAX_POINTS = 3000

    // Evenly sample an array down to at most `max` elements.
    // This preserves distribution without the cost of full reservoir sampling.
    function sampleEvenly<T>(arr: T[], max: number): T[] {
      const n = arr.length
      if (n <= max) return arr
      const step = n / max
      const out: T[] = []
      for (let i = 0; i < max; i++) {
        out.push(arr[Math.floor(i * step)])
      }
      return out
    }

    // Function to fetch LTV scatter data from API with cancellation and timeout
    const fetchLtvScatterData = async (sellerId: number | null, tradeId: number | null): Promise<LoanItem[]> => {
      if (!sellerId || !tradeId) return []

      const key = `${sellerId}:${tradeId}`

      // Cancel any previous in-flight request to keep UI responsive
      if (currentController) {
        try { currentController.abort() } catch {}
      }
      currentController = new AbortController()

      // Leading slash ensures correct join with baseURL '/api' -> '/api/acq/...'
      const url = `/acq/summary/ltv-scatter/${sellerId}/${tradeId}/`
      const resp = await http.get<ApiLoanItem[]>(url, {
        signal: currentController.signal as any,
        timeout: 15000, // fail fast if backend is slow
      })

      lastKey = key

      // Convert API response to our internal format
      // API returns strings for decimal values, convert to numbers
      const items = (resp.data || []).map((item: ApiLoanItem) => ({
        id: item.id,
        seller_asis_value: parseFloat(item.seller_asis_value),
        current_balance: parseFloat(item.current_balance),
        ltv: parseFloat(item.ltv)
      })) as LoanItem[]

      // Guardrail: sample to MAX_POINTS to avoid rendering too many points at once
      const sampled = sampleEvenly(items, MAX_POINTS)
      if (items.length > sampled.length) {
        // Optional: log for visibility during dev
        console.debug('[LtvScatter] sampled', { original: items.length, shown: sampled.length })
      }
      return sampled
    }

    // Build a fallback dataset from AG Grid cached rows if API returns nothing
    function fallbackFromGridRows(): LoanItem[] {
      try {
        const rows: any[] = Array.isArray(gridRows.value) ? gridRows.value : []
        const mapped: LoanItem[] = []
        for (const r of rows) {
          const asisRaw = r?.seller_asis_value ?? r?.sellerAsIsValue ?? r?.asis_value
          const balRaw = r?.current_balance ?? r?.currentBalance ?? r?.cur_balance
          const ltvRaw = r?.ltv ?? r?.LTV
          const asis = typeof asisRaw === 'number' ? asisRaw : parseFloat(String(asisRaw).replace(/[^0-9.\-]/g, ''))
          const bal = typeof balRaw === 'number' ? balRaw : parseFloat(String(balRaw).replace(/[^0-9.\-]/g, ''))
          let ltv = typeof ltvRaw === 'number' ? ltvRaw : parseFloat(String(ltvRaw).replace(/[^0-9.\-]/g, ''))
          if (!Number.isFinite(ltv) && Number.isFinite(asis) && asis > 0 && Number.isFinite(bal)) {
            ltv = (bal / asis) * 100
          }
          if (Number.isFinite(asis) && Number.isFinite(bal) && Number.isFinite(ltv)) {
            mapped.push({ id: String(r?.id ?? r?.loan_id ?? mapped.length), seller_asis_value: asis, current_balance: bal, ltv })
          }
        }
        const sampled = sampleEvenly(mapped, MAX_POINTS)
        console.debug('[LtvScatter] fallback from grid rows', { rows: rows.length, used: sampled.length })
        return sampled
      } catch (e) {
        console.warn('[LtvScatter] fallbackFromGridRows failed', e)
        return []
      }
    }


    // Format data for ApexCharts and determine axis ranges
    const formatDataForChart = (data: LoanItem[]): [number, number, number][] => {
      if (!data.length) return [] as [number, number, number][]
      
      // Format data for chart and group by LTV category
      const lowLtvData: [number, number, number][] = []
      const midLtvData: [number, number, number][] = []
      const highLtvData: [number, number, number][] = []
      
      // Distribute data into the three LTV ranges
      data.forEach(item => {
        const ltv = parseFloat(item.ltv.toFixed(1))
        const point: [number, number, number] = [
          item.seller_asis_value,  // X-axis: Seller As-Is value
          item.current_balance,    // Y-axis: Current Balance
          ltv                      // Z-axis: LTV (shown in tooltip)
        ]
        
        // Sort into appropriate series based on LTV value
        if (ltv > 100) {
          highLtvData.push(point)
        } else if (ltv >= 90) {
          midLtvData.push(point)
        } else {
          lowLtvData.push(point)
        }
      })
      
      // Update all three series
      series.value[0].data = lowLtvData
      series.value[1].data = midLtvData
      series.value[2].data = highLtvData
      
      // Combine for max calculation
      const formattedData = [...lowLtvData, ...midLtvData, ...highLtvData]
      
      // Find the maximum values for both axes to ensure equal scale
      let maxX = 0
      let maxY = 0
      formattedData.forEach(point => {
        maxX = Math.max(maxX, point[0])
        maxY = Math.max(maxY, point[1])
      })
      
      // Use the larger of the two maximums to set the scale
      const maxValue = Math.max(maxX, maxY)
      // Round up to nearest 100K for clean axis
      const maxAxisValue = Math.ceil(maxValue / 100000) * 100000
      
      // Update chart options with equal min/max for both axes
      // Use type assertion to handle the TypeScript error for max values
      const xaxis = chartOptions.value.xaxis as any
      const yaxis = chartOptions.value.yaxis as any
      xaxis.max = maxAxisValue
      yaxis.max = maxAxisValue
      
      return formattedData
    }

    // Define type for chart series data
    type ScatterDataType = [number, number, number][]
    
    // Chart series with empty initial data - using color groups based on LTV
    const series = ref([
      {
        name: 'LTV < 90%',
        color: '#47ad77', // Green
        data: [] as ScatterDataType
      },
      {
        // Legend text requirement: display as "LTV 90%-100%" (avoid special ≤ chars)
        name: 'LTV 90%-100%',
        color: '#ffbc00', // Yellow/amber
        data: [] as ScatterDataType
      },
      {
        name: 'LTV > 100%',
        color: '#fa5c7c', // Red
        data: [] as ScatterDataType
      }
    ])

    // Check if we have data across all series
    const hasData = computed(() => {
      return series.value[0].data.length > 0 || 
             series.value[1].data.length > 0 || 
             series.value[2].data.length > 0
    })
    
    // Watch for changes in selections to update chart data
    watch([() => selectedSellerId.value, () => selectedTradeId.value], async ([newSellerId, newTradeId]) => {
      if (newSellerId && newTradeId) {
        isLoading.value = true
        try {
          // Fetch real data from API
          let data = await fetchLtvScatterData(newSellerId, newTradeId)
          if (!data.length) {
            // Try fallback using cached AG Grid rows
            data = fallbackFromGridRows()
          }
          // formatDataForChart handles distributing the data into the three series
          formatDataForChart(data)
          // After series/options updates, nudge a resize so chart fills parent
          nextTick(() => {
            if (containerReady.value) {
              try { ApexCharts.exec('ltv-scatter', 'updateOptions', {}, false, true) } catch {}
              try { ApexCharts.exec('ltv-scatter', 'resize') } catch {}
              try { window.dispatchEvent(new Event('resize')) } catch {}
            } else {
              // Defer mounting until container is measurable
              ensureContainerReady()
            }
          })
        } catch (error) {
          console.error('Error fetching LTV scatter data:', error)
          // Clear all series on error
          let fb = fallbackFromGridRows()
          if (fb.length) {
            formatDataForChart(fb)
          } else {
            series.value[0].data = []
            series.value[1].data = []
            series.value[2].data = []
          }
        } finally {
          isLoading.value = false
        }
      } else {
        // Reset data when no selection for all series
        // Also clear lastKey so next valid selection triggers a real fetch
        lastKey = null
        // Cancel any in-flight request when selection becomes incomplete
        if (currentController) { try { currentController.abort() } catch {} finally { currentController = null } }
        series.value[0].data = []
        series.value[1].data = []
        series.value[2].data = []
      }
    }, { immediate: true })

    return {
      chartOptions,
      series,
      isLoading,
      hasData,
      containerRef,
      chartKey,
      containerReady,
      containerWidth,
    }
  }
})
</script>

<style scoped>
/* CUSTOM OVERRIDE: Vertically center the ApexCharts legend when positioned on the left.
   Why: ApexCharts supports legend.position (top/bottom/left/right) and offsetX/offsetY but
   does NOT provide an automatic vertical-centering option for left/right positions.
   This scoped CSS uses Vue's :deep() selector to target chart-internal DOM safely.
   Keeping this local ensures we don't leak styles across other charts. */
:host { display: block; }
:deep(.apexcharts-canvas) {
  position: relative;
}

:deep(.apexcharts-legend.apx-legend-position-left) {
  top: 50% !important;
  transform: translateY(-50%) !important;
}
</style>