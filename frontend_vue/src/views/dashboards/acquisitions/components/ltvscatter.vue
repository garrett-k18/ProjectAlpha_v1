<template>
  <div class="card h-100">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">LTV Scatter Chart</h4>
      <div class="d-flex align-items-center">
        <div v-if="isLoading" class="me-2">
          <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
    </div>

    <div class="card-body pt-0">
      <div v-if="!hasData && !isLoading" class="text-center py-5">
        <p class="text-muted">No data available for selected pool</p>
      </div>
      <div v-else>
        <apexchart
          type="scatter"
          height="350"
          :options="chartOptions"
          :series="series"
        ></apexchart>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed, ref, watch } from 'vue'
import { useAcqSelectionsStore } from '@/stores/acqSelections'
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
        aspectRatio: 1
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
        position: 'left',
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
      dataLabels: {
        enabled: false
      }
    })

    // Track last selection (optional – used for logging/stability)
    let lastKey: string | null = null
    // Keep a controller to cancel in-flight requests when selection changes
    let currentController: AbortController | null = null

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
          const data = await fetchLtvScatterData(newSellerId, newTradeId)
          // formatDataForChart handles distributing the data into the three series
          formatDataForChart(data)
        } catch (error) {
          console.error('Error fetching LTV scatter data:', error)
          // Clear all series on error
          series.value[0].data = []
          series.value[1].data = []
          series.value[2].data = []
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
      hasData
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
:deep(.apexcharts-canvas) {
  position: relative;
}

:deep(.apexcharts-legend.apx-legend-position-left) {
  top: 50% !important;
  transform: translateY(-50%) !important;
}
</style>