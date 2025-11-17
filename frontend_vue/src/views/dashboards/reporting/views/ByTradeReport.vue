<template>
  <div>
    <div class="card">
      <div class="d-flex card-header justify-content-between align-items-center">
        <h4 class="header-title">Performance by Trade</h4>
        <div class="dropdown">
          <button
            class="btn btn-sm btn-outline-primary dropdown-toggle"
            type="button"
            data-bs-toggle="dropdown"
          >
            <i class="mdi mdi-chart-bar me-1"></i>
            Chart Type
          </button>
          <ul class="dropdown-menu">
            <li><a class="dropdown-item" href="#" @click.prevent="chartType = 'bar'">Bar Chart</a></li>
            <li><a class="dropdown-item" href="#" @click.prevent="chartType = 'line'">Line Chart</a></li>
            <li><a class="dropdown-item" href="#" @click.prevent="chartType = 'pie'">Pie Chart</a></li>
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
            <small class="text-muted">Click any bar to view detailed trade analysis</small>
          </div>
        </div>
      </div>
    </div>

    <!-- AG Grid Card -->
    <div class="card mt-3">
      <div class="card-header d-flex justify-content-between align-items-center">
        <div>
          <h4 class="header-title mb-0">
            <i class="mdi mdi-table me-2"></i>
            Trade Details
          </h4>
          <p class="text-muted small mb-0 mt-1">
            Customize columns, filter data, and export to CSV
          </p>
        </div>
        <div class="d-flex align-items-center gap-2">
          <span class="text-muted small">View:</span>
          <select
            v-model="currentGridView"
            class="form-select form-select-sm"
            style="min-width: 200px;"
          >
            <option value="servicing">Servicing</option>
            <option value="initial-underwriting">Initial Underwriting</option>
            <option value="performance">Performance</option>
            <option value="re-underwriting">Re-Underwriting</option>
          </select>
        </div>
      </div>

      <div class="card-body">
        <ReportingAgGrid
          ref="agGridRef"
          :column-defs="visibleColumnDefs"
          :row-data="gridData"
          :loading="loadingGrid"
          grid-height="600px"
          :pagination="true"
          :page-size="50"
          row-selection="single"
          @row-clicked="handleRowClickFromGrid"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * WHAT: By Trade Report with AG Grid
 * WHY: Provides users max flexibility to customize columns, filter, sort, export
 * HOW: Uses ReportingAgGrid component with custom column definitions
 */
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'
import type { ColDef, ValueFormatterParams } from 'ag-grid-community'
import ReportingAgGrid from '../components/ReportingAgGrid.vue'
import BadgeCell from '@/views/acq_module/acq_dash/components/BadgeCell.vue'

Chart.register(...registerables)

// WHAT: Component props - receive data from parent
const props = defineProps<{
  chartData: any[]
  gridData: any[]
  loadingChart: boolean
  loadingGrid: boolean
}>()

// WHAT: Component emits - notify parent on drill-down
const emit = defineEmits<{
  (e: 'drill-down', payload: { type: string; data: any }): void
}>()

// WHAT: Chart references
const chartCanvas = ref<HTMLCanvasElement | null>(null)
const chartInstance = ref<Chart<any, any, any> | null>(null)
const chartType = ref<'bar' | 'line' | 'pie'>('bar')

// WHAT: AG Grid reference
const agGridRef = ref<InstanceType<typeof ReportingAgGrid> | null>(null)

const currentGridView = ref<'servicing' | 'initial-underwriting' | 'performance' | 're-underwriting'>('servicing')

// WHAT: Value formatters (match existing grid patterns)
// WHY: Consistent formatting across all grids
function currencyFormatter(params: ValueFormatterParams): string {
  const v = params.value
  const num = typeof v === 'number' ? v : parseFloat(String(v))
  if (Number.isNaN(num)) return v == null ? '' : String(v)
  return new Intl.NumberFormat('en-US', { 
    style: 'currency', 
    currency: 'USD', 
    maximumFractionDigits: 0 
  }).format(num)
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
  return new Intl.DateTimeFormat('en-US', { 
    year: 'numeric', 
    month: '2-digit', 
    day: '2-digit' 
  }).format(d)
}

/**
 * WHAT: AG Grid column definitions
 * WHY: Define the core columns for trade reporting
 * HOW: Users can show/hide any column via the column panel
 */
const baseColumnDefs = ref<ColDef[]>([
  {
    headerName: 'Trade Name',
    field: 'trade_name',
    pinned: 'left',
    width: 250,
    headerClass: 'ag-left-aligned-header text-start',
    cellClass: 'ag-left-aligned-cell text-start fw-semibold',
  },
  {
    headerName: 'Address',
    field: 'street_address',
    width: 260,
    pinned: 'left',
    headerClass: 'ag-left-aligned-header text-start',
    cellClass: 'ag-left-aligned-cell text-start',
  },
  {
    headerName: 'City',
    field: 'city',
    width: 180,
    pinned: 'left',
    headerClass: 'ag-left-aligned-header text-start',
    cellClass: 'ag-left-aligned-cell text-start',
  },
  {
    headerName: 'State',
    field: 'state',
    width: 110,
    pinned: 'left',
  },
  {
    headerName: 'Total UPB',
    field: 'total_upb',
    width: 150,
    valueFormatter: currencyFormatter,
    comparator: (valueA: number, valueB: number) => valueA - valueB,
  },
  {
    headerName: 'Status',
    field: 'status',
    width: 140,
    cellRenderer: BadgeCell as any,
    cellRendererParams: {
      mode: 'enum',
      enumMap: {
        'DD': { label: 'DD', color: 'bg-info' },
        'AWARDED': { label: 'Awarded', color: 'bg-success' },
        'PASS': { label: 'Pass', color: 'bg-secondary' },
        'BOARD': { label: 'Board', color: 'bg-primary' },
      },
    },
  },
  {
    // NOTE: Backend field is purchase_date; header is renamed for UX
    headerName: 'Purchase Date',
    field: 'purchase_date',
    width: 130,
    valueFormatter: dateFormatter,
  },
  {
    headerName: 'Last Updated',
    field: 'last_updated',
    width: 140,
    valueFormatter: dateFormatter,
    hide: true, // WHAT: Hidden by default, user can show via column panel
  },
  {
    headerName: 'Servicer ID',
    field: 'servicer_id',
    width: 160,
    headerClass: 'ag-left-aligned-header text-start',
    cellClass: 'ag-left-aligned-cell text-start',
    hide: true,
  },
  // Servicing view specific columns
  {
    headerName: 'Servicer Balance',
    field: 'servicer_current_balance',
    width: 150,
    valueFormatter: currencyFormatter,
    hide: true,
  },
  {
    headerName: 'Servicer Total Debt',
    field: 'servicer_total_debt',
    width: 150,
    valueFormatter: currencyFormatter,
    hide: true,
  },
  {
    headerName: 'Servicer As Of',
    field: 'servicer_as_of_date',
    width: 130,
    valueFormatter: dateFormatter,
    hide: true,
  },
  {
    headerName: 'Next Due Date',
    field: 'servicer_next_due_date',
    width: 130,
    valueFormatter: dateFormatter,
    hide: true,
  },
  {
    headerName: 'Months DLQ',
    field: 'months_dlq',
    width: 120,
    valueFormatter: numberFormatter,
    hide: true,
  },
  // Initial underwriting (purchase) view columns
  {
    headerName: 'Purchase Price',
    field: 'purchase_price',
    width: 150,
    valueFormatter: currencyFormatter,
    hide: true,
  },
  // Performance view columns
  {
    headerName: 'Current Duration (Months)',
    field: 'current_duration_months',
    width: 190,
    valueFormatter: numberFormatter,
    hide: true,
  },
  {
    headerName: 'Current Gross Cost',
    field: 'current_gross_cost',
    width: 170,
    valueFormatter: currencyFormatter,
    hide: true,
  },
  // Re-underwriting (projections) view columns
  {
    headerName: 'Projected Exit',
    field: 'expected_exit_date',
    width: 140,
    valueFormatter: dateFormatter,
    hide: true,
  },
  {
    headerName: 'Projected Gross Cost',
    field: 'projected_gross_cost',
    width: 180,
    valueFormatter: currencyFormatter,
    hide: true,
  },
  {
    headerName: 'Projected Gross Proceeds',
    field: 'expected_gross_proceeds',
    width: 190,
    valueFormatter: currencyFormatter,
    hide: true,
  },
])

const visibleColumnDefs = computed<ColDef[]>(() => {
  const view = currentGridView.value
  return baseColumnDefs.value.map(col => {
    const field = col.field as string | undefined
    if (!field) return col

    const alwaysVisible = [
      'trade_name',
      'street_address',
      'city',
      'state',
      'total_upb',
      'status',
      'purchase_date',
      'last_updated',
    ]

    if (alwaysVisible.includes(field)) {
      return { ...col, hide: col.hide === true && false }
    }

    const servicingFields = [
      'servicer_id',
      'servicer_current_balance',
      'servicer_total_debt',
      'servicer_as_of_date',
      'servicer_next_due_date',
      'months_dlq',
    ]
    const initialUnderwritingFields = [
      'purchase_price',
    ]
    const performanceFields = [
      'current_duration_months',
      'current_gross_cost',
    ]
    const reUnderwritingFields = [
      'expected_exit_date',
      'projected_gross_cost',
      'expected_gross_proceeds',
    ]

    let hide = true
    if (view === 'servicing' && servicingFields.includes(field)) hide = false
    if (view === 'initial-underwriting' && initialUnderwritingFields.includes(field)) hide = false
    if (view === 'performance' && performanceFields.includes(field)) hide = false
    if (view === 're-underwriting' && reUnderwritingFields.includes(field)) hide = false

    return { ...col, hide }
  })
})

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
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
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
          display: chartType.value === 'pie'
        },
        tooltip: {
          callbacks: {
            label: (context) => {
              return `UPB: $${(context.parsed.y / 1_000_000).toFixed(2)}MM`
            }
          }
        }
      }
    }
  })
}

function handleChartClick(data: any): void {
  emit('drill-down', { type: 'trade', data })
}

/**
 * WHAT: Handle row click from AG Grid
 * WHY: Trigger drill-down modal when user clicks a row
 */
function handleRowClickFromGrid(row: any): void {
  console.log('[ByTradeReport] Row clicked:', row)
  emit('drill-down', { type: 'trade', data: row })
}

watch([() => props.chartData, chartType], async () => {
  await nextTick()
  renderChart()
})

onMounted(async () => {
  await nextTick()
  renderChart()
})
</script>

<style scoped>
.chart-container {
  position: relative;
}

.table th {
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.5px;
  color: #6c757d;
  border-bottom: 2px solid #dee2e6;
}

.table-hover tbody tr:hover {
  background-color: rgba(54, 162, 235, 0.05);
}
</style>
