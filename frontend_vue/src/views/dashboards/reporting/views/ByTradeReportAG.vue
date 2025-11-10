<template>
  <!--
    By Trade Report - AG Grid Implementation
    
    WHAT: Performance analysis by trade using AG Grid for maximum flexibility
    WHY: Users can customize columns, filter, sort, and export data easily
    WHERE: Reporting Dashboard > By Trade view
    
    FEATURES:
    - Chart visualization (Bar/Line/Pie)
    - AG Grid with column management
    - Custom cell renderers (currency, badges, LTV)
    - Export to CSV/Excel
    - Row click for drill-down
    - Quick filter search
  -->
  <div>
    <!-- Chart Card -->
    <div class="card">
      <div class="d-flex card-header justify-content-between align-items-center">
        <h4 class="header-title">
          <i class="mdi mdi-chart-bar me-2"></i>
          Performance by Trade
        </h4>
        <div class="dropdown">
          <button
            class="btn btn-sm btn-outline-primary dropdown-toggle"
            type="button"
            data-bs-toggle="dropdown"
          >
            <i class="mdi mdi-chart-bar me-1"></i>
            {{ chartType === 'bar' ? 'Bar' : chartType === 'line' ? 'Line' : 'Pie' }} Chart
          </button>
          <ul class="dropdown-menu dropdown-menu-end">
            <li>
              <a class="dropdown-item" href="#" @click.prevent="chartType = 'bar'">
                <i class="mdi mdi-chart-bar me-2"></i>
                Bar Chart
              </a>
            </li>
            <li>
              <a class="dropdown-item" href="#" @click.prevent="chartType = 'line'">
                <i class="mdi mdi-chart-line me-2"></i>
                Line Chart
              </a>
            </li>
            <li>
              <a class="dropdown-item" href="#" @click.prevent="chartType = 'pie'">
                <i class="mdi mdi-chart-pie me-2"></i>
                Pie Chart
              </a>
            </li>
          </ul>
        </div>
      </div>

      <div class="card-body pt-2">
        <div v-if="loadingChart" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading chart...</span>
          </div>
          <p class="text-muted mt-2">Loading trade performance data...</p>
        </div>

        <div v-else-if="!chartData || chartData.length === 0" class="text-center py-5 text-muted">
          <i class="mdi mdi-chart-bar-stacked fs-1 mb-3 d-block"></i>
          <p>No trade data available. Adjust filters to see results.</p>
        </div>

        <div v-else>
          <div class="chart-container" style="min-height: 400px;">
            <canvas ref="chartCanvas"></canvas>
          </div>
          
          <div class="text-center mt-3">
            <small class="text-muted">
              <i class="mdi mdi-information-outline me-1"></i>
              Click any bar to view detailed trade analysis
            </small>
          </div>
        </div>
      </div>
    </div>

    <!-- AG Grid Card -->
    <div class="card mt-3">
      <div class="card-header">
        <h4 class="header-title mb-0">
          <i class="mdi mdi-table me-2"></i>
          Trade Details
        </h4>
        <p class="text-muted small mb-0 mt-1">
          Customize columns, filter data, and export to CSV/Excel
        </p>
      </div>

      <div class="card-body">
        <ReportingAgGrid
          ref="agGridRef"
          :column-defs="columnDefs"
          :row-data="gridData"
          :loading="loadingGrid"
          grid-height="600px"
          :pagination="true"
          :page-size="25"
          row-selection="single"
          @row-clicked="handleRowClick"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * WHAT: By Trade Report with AG Grid implementation
 * WHY: Showcase how to integrate AG Grid into reporting views
 * HOW: Use ReportingAgGrid component with custom column definitions
 */
import { ref, watch, nextTick, onMounted } from 'vue'
import { Chart, registerables } from 'chart.js'
import type { ColDef, ValueFormatterParams } from 'ag-grid-community'
import ReportingAgGrid from '../components/ReportingAgGrid.vue'

Chart.register(...registerables)

// WHAT: Value formatters (match existing grid patterns)
// WHY: Consistent formatting across all reporting grids
function currencyFormatter(params: ValueFormatterParams): string {
  const v = params.value
  const num = typeof v === 'number' ? v : parseFloat(String(v))
  if (Number.isNaN(num)) return v == null ? '' : String(v)
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(num)
}

function percentFormatter(params: ValueFormatterParams): string {
  const v = params.value
  if (v == null || v === '') return ''
  return `${Number(v).toFixed(1)}%`
}

function numberFormatter(params: ValueFormatterParams): string {
  const v = params.value
  if (v == null || v === '') return ''
  return new Intl.NumberFormat('en-US').format(Number(v))
}

function dateFormatter(params: ValueFormatterParams): string {
  const v = params.value
  if (!v) return ''
  const d = new Date(String(v))
  if (isNaN(d.getTime())) return String(v)
  return new Intl.DateTimeFormat('en-US', { year: 'numeric', month: '2-digit', day: '2-digit' }).format(d)
}

// WHAT: Component props
// WHY: Receive data from parent reporting dashboard
const props = defineProps<{
  chartData: any[]
  gridData: any[]
  loadingChart: boolean
  loadingGrid: boolean
}>()

// WHAT: Component emits
// WHY: Notify parent when user drills down
const emit = defineEmits<{
  (e: 'drill-down', payload: { type: string; data: any }): void
}>()

// WHAT: Chart references
const chartCanvas = ref<HTMLCanvasElement | null>(null)
const chartInstance = ref<Chart<any, any, any> | null>(null)
const chartType = ref<'bar' | 'line' | 'pie'>('bar')

// WHAT: AG Grid reference
// WHY: Access grid API for programmatic control
const agGridRef = ref<InstanceType<typeof ReportingAgGrid> | null>(null)

/**
 * WHAT: AG Grid column definitions
 * WHY: Define all columns with formatters (matches existing grid patterns)
 * 
 * COLUMN FEATURES:
 * - Trade Name: Pinned left, sortable, filterable
 * - Asset Count: Number formatter, center-aligned
 * - Total UPB: Currency formatter
 * - Avg LTV: Percentage formatter with color via cellClass callback
 * - Status: Text with filter
 * - Bid Date: Date formatter
 * - Seller: Text field
 * - State Count: Number formatter
 */
const columnDefs = ref<ColDef[]>([
  {
    headerName: 'Trade Name',
    field: 'trade_name',
    pinned: 'left',           // WHAT: Pin to left side
    width: 250,               // WHAT: Fixed width
    sortable: true,
    filter: 'agTextColumnFilter',
    checkboxSelection: true, // WHAT: Add checkbox for row selection
    headerCheckboxSelection: true,
    headerClass: 'ag-left-aligned-header text-start', // WHAT: Left-align header
    cellClass: 'ag-left-aligned-cell text-start fw-semibold', // WHAT: Left-align cell, bold text
  },
  {
    headerName: 'Asset Count',
    field: 'asset_count',
    width: 130,
    sortable: true,
    filter: 'agNumberColumnFilter',
    valueFormatter: numberFormatter,
  },
  {
    headerName: 'Total UPB',
    field: 'total_upb',
    width: 150,
    sortable: true,
    filter: 'agNumberColumnFilter',
    valueFormatter: currencyFormatter,
    comparator: (valueA: number, valueB: number) => valueA - valueB, // WHAT: Numeric sorting
  },
  {
    headerName: 'Avg LTV',
    field: 'avg_ltv',
    width: 120,
    sortable: true,
    filter: 'agNumberColumnFilter',
    valueFormatter: percentFormatter,
    cellClass: (params) => {
      // WHAT: Color-code LTV by risk level (matches existing pattern)
      const ltv = params.value
      if (ltv > 100) return 'text-danger fw-bold'
      if (ltv >= 90) return 'text-warning fw-semibold'
      return 'text-success'
    },
  },
  {
    headerName: 'Status',
    field: 'status',
    width: 140,
    sortable: true,
    filter: 'agSetColumnFilter', // WHAT: Multi-select filter for statuses
  },
  {
    headerName: 'Bid Date',
    field: 'bid_date',
    width: 130,
    sortable: true,
    filter: 'agDateColumnFilter',
    valueFormatter: dateFormatter,
  },
  {
    headerName: 'Seller',
    field: 'seller',
    width: 180,
    sortable: true,
    filter: 'agTextColumnFilter',
    headerClass: 'ag-left-aligned-header text-start',
    cellClass: 'ag-left-aligned-cell text-start',
  },
  {
    headerName: 'State Count',
    field: 'state_count',
    width: 130,
    sortable: true,
    filter: 'agNumberColumnFilter',
    valueFormatter: numberFormatter,
  },
  {
    headerName: 'Delinquency Rate',
    field: 'delinquency_rate',
    width: 160,
    sortable: true,
    filter: 'agNumberColumnFilter',
    valueFormatter: percentFormatter,
  },
  {
    headerName: 'Last Updated',
    field: 'last_updated',
    width: 140,
    sortable: true,
    filter: 'agDateColumnFilter',
    valueFormatter: dateFormatter,
    hide: true, // WHAT: Hidden by default, user can show via column panel
  },
])

/**
 * WHAT: Render chart visualization
 * WHY: Display trade performance in visual format
 */
function renderChart(): void {
  if (!chartCanvas.value || !props.chartData || props.chartData.length === 0) return

  if (chartInstance.value) {
    chartInstance.value.destroy()
  }

  const ctx = chartCanvas.value.getContext('2d')
  if (!ctx) return

  chartInstance.value = new Chart(ctx, {
    type: chartType.value,
    data: {
      labels: props.chartData.map(d => d.x),
      datasets: [{
        label: 'Total UPB ($MM)',
        data: props.chartData.map(d => d.y),
        backgroundColor: chartType.value === 'pie' 
          ? ['#727cf5', '#0acf97', '#fa5c7c', '#ffbc00', '#39afd1']
          : 'rgba(54, 162, 235, 0.6)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      onClick: (event, elements) => {
        if (elements.length > 0) {
          const index = elements[0].index
          const clickedData = props.chartData[index]
          handleChartClick(clickedData)
        }
      },
      scales: chartType.value !== 'pie' ? {
        y: {
          beginAtZero: true,
          ticks: {
            callback: (value) => `$${(Number(value) / 1_000_000).toFixed(1)}MM`
          }
        }
      } : undefined,
      plugins: {
        legend: {
          display: chartType.value === 'pie',
          position: 'bottom',
        },
        tooltip: {
          callbacks: {
            label: (context) => {
              if (chartType.value === 'pie') {
                const total = context.dataset.data.reduce((sum: number, val: any) => sum + (val || 0), 0)
                const percentage = ((context.parsed / total) * 100).toFixed(1)
                return `${context.label}: $${(context.parsed / 1_000_000).toFixed(2)}MM (${percentage}%)`
              }
              return `UPB: $${(context.parsed.y / 1_000_000).toFixed(2)}MM`
            }
          }
        }
      }
    }
  })
}

/**
 * WHAT: Handle chart click
 * WHY: Drill down when user clicks bar/pie slice
 */
function handleChartClick(data: any): void {
  console.log('[ByTradeReport] Chart clicked:', data)
  emit('drill-down', { type: 'trade', data })
}

/**
 * WHAT: Handle grid row click
 * WHY: Drill down when user clicks table row
 */
function handleRowClick(row: any): void {
  console.log('[ByTradeReport] Row clicked:', row)
  emit('drill-down', { type: 'trade', data: row })
}

// WHAT: Watch for chart data changes and re-render
watch([() => props.chartData, chartType], async () => {
  await nextTick()
  renderChart()
})

// WHAT: Render chart on mount
onMounted(async () => {
  await nextTick()
  renderChart()
})
</script>

<style scoped>
/**
 * WHAT: Chart container styles
 * WHY: Proper sizing and positioning for Chart.js
 */
.chart-container {
  position: relative;
  width: 100%;
}

/**
 * WHAT: Custom AG Grid styles
 * WHY: Match Hyper UI theme
 */
:deep(.ag-theme-alpine) {
  font-family: inherit;
}
</style>

