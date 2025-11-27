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
            <option value="all">All</option>
            <option value="servicing">Servicing</option>
            <option value="initial-underwriting">Initial Underwriting</option>
            <option value="performance">Performance</option>
            <option value="re-underwriting">Re-Underwriting</option>
            <option value="asset-management">Asset Management</option>
          </select>
          <button
            class="btn btn-sm"
            :class="pinCoreColumns ? 'btn-outline-primary' : 'btn-outline-secondary'"
            type="button"
            @click="toggleCorePinning"
            title="Toggle pinning for core columns"
          >
            <i class="mdi" :class="pinCoreColumns ? 'mdi-pin' : 'mdi-pin-off'"></i>
            <span class="ms-1">{{ pinCoreColumns ? 'Pinned Core' : 'Scrolling Core' }}</span>
          </button>
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
import type { ColDef, ColGroupDef, ValueFormatterParams, ValueGetterParams } from 'ag-grid-community'
import ReportingAgGrid from '../components/ReportingAgGrid.vue'
import BadgeCell from '@/views/acq_module/acq_dash/components/BadgeCell.vue'
import { activeTracksEnumMap, activeTasksColorMap } from '@/config/badgeTokens'

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

const currentGridView = ref<'all' | 'servicing' | 'initial-underwriting' | 'performance' | 're-underwriting' | 'asset-management'>('all')
const pinCoreColumns = ref<boolean>(true)
const corePinnedFields = ['trade_name','servicer_id','street_address','city','state','asset_master_status'] as const

function toggleCorePinning(): void {
  pinCoreColumns.value = !pinCoreColumns.value
}

function shouldPinField(field?: string): 'left' | undefined {
  if (!field) return undefined
  return pinCoreColumns.value && corePinnedFields.includes(field as typeof corePinnedFields[number])
    ? 'left'
    : undefined
}

// WHAT: Value formatters (match existing grid patterns)
// WHY: Consistent formatting across all grids
function currencyFormatter(params: ValueFormatterParams): string {
  const v = params.value
  if (v === null || v === undefined || v === '') return ''
  const num = typeof v === 'number' ? v : Number(v)
  if (Number.isNaN(num)) return ''
  return new Intl.NumberFormat('en-US', { 
    style: 'currency', 
    currency: 'USD', 
    maximumFractionDigits: 0 
  }).format(num)
}

function negativeCurrencyFormatter(params: ValueFormatterParams): string {
  const v = params.value
  if (v === null || v === undefined || v === '') return ''
  const num = typeof v === 'number' ? v : Number(v)
  if (Number.isNaN(num)) return ''
  if (num === 0) {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0,
    }).format(0)
  }
  const display = -Math.abs(num)
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(display)
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
    width: 130,
    minWidth: 130,
    headerClass: 'ag-left-aligned-header text-start',
    cellClass: 'ag-left-aligned-cell text-start fw-semibold',
  },
  {
    headerName: 'Servicer ID',
    field: 'servicer_id',
    width: 120,
    minWidth: 120,
    headerClass: 'ag-left-aligned-header text-start',
    cellClass: 'ag-left-aligned-cell text-start',
    hide: true,
  },
  {
    headerName: 'Address',
    field: 'street_address',
    width: 260,
    minWidth: 260,
    headerClass: 'ag-left-aligned-header text-start',
    cellClass: 'ag-left-aligned-cell text-start',
  },
  {
    headerName: 'City',
    field: 'city',
    width: 180,
    minWidth: 180,
    headerClass: 'ag-left-aligned-header text-start',
    cellClass: 'ag-left-aligned-cell text-start',
  },
  {
    headerName: 'State',
    field: 'state',
    width: 90,
    minWidth: 90,
    hide: false,
  },
  {
    headerName: 'Lifecycle Status',
    field: 'asset_master_status',
    width: 120,
    minWidth: 120,
    valueFormatter: (params: ValueFormatterParams) => params.value || '—',
    hide: true,
  },
  {
    headerName: 'Bid Price',
    field: 'purchase_price',
    width: 150,
    valueFormatter: currencyFormatter,
    hide: true,
  },
  {
    headerName: 'Purchase Date',
    field: 'purchase_date',
    width: 130,
    valueFormatter: dateFormatter,
  },
  // Servicing view specific columns
  {
    headerName: 'Current Balance',
    field: 'servicer_current_balance',
    width: 150,
    valueFormatter: currencyFormatter,
    hide: true,
  },
  {
    headerName: 'Total Debt',
    field: 'servicer_total_debt',
    width: 150,
    valueFormatter: currencyFormatter,
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
  // Purchase view columns
  {
    headerName: 'Exit Strategy',
    field: 'exit_strategy',
    width: 160,
    hide: true,
  },
  {
    headerName: 'Bid % UPB',
    field: 'bid_pct_upb',
    width: 130,
    valueFormatter: percentFormatter,
    hide: true,
  },
  {
    headerName: 'Bid % TD',
    field: 'bid_pct_td',
    width: 120,
    valueFormatter: percentFormatter,
    hide: true,
  },
  {
    headerName: 'Bid % Seller As-Is',
    field: 'bid_pct_sellerasis',
    width: 170,
    valueFormatter: percentFormatter,
    hide: true,
  },
  {
    headerName: 'Bid % PV',
    field: 'bid_pct_pv',
    width: 120,
    valueFormatter: percentFormatter,
    hide: true,
  },
  // Initial underwriting view columns
  {
    headerName: 'Pre-REO Hold',
    field: 'pre_reo_hold_duration',
    width: 190,
    valueFormatter: numberFormatter,
    hide: true,
  },
  {
    headerName: 'REO Hold',
    field: 'reo_hold_duration',
    width: 170,
    valueFormatter: numberFormatter,
    hide: true,
  },
  {
    headerName: 'Total Hold',
    field: 'uw_exit_duration_months',
    width: 210,
    valueFormatter: numberFormatter,
    hide: true,
  },
  {
    headerName: 'Exit Date',
    field: 'expected_exit_date',
    width: 140,
    valueFormatter: dateFormatter,
    hide: true,
  },
  {
    headerName: 'Gross Purchase Price',
    field: 'gross_purchase_price',
    width: 170,
    valueFormatter: negativeCurrencyFormatter,
    cellClass: 'text-danger',
    hide: true,
  },
  {
    headerName: 'Legal Expenses',
    field: 'legal_expenses',
    width: 150,
    valueFormatter: negativeCurrencyFormatter,
    cellClass: 'text-danger',
    hide: true,
  },
  {
    headerName: 'Servicing Fees',
    field: 'servicing_expenses',
    width: 170,
    valueFormatter: negativeCurrencyFormatter,
    cellClass: 'text-danger',
    hide: true,
  },
  {
    headerName: 'REO Expenses',
    field: 'reo_expenses',
    width: 150,
    valueFormatter: negativeCurrencyFormatter,
    cellClass: 'text-danger',
    hide: true,
  },
  {
    headerName: 'Rehab / Trashout',
    field: 'rehab_trashout_cost',
    width: 160,
    valueFormatter: negativeCurrencyFormatter,
    cellClass: 'text-danger',
    hide: true,
  },
  {
    headerName: 'Carry Cost',
    field: 'carry_cost',
    width: 170,
    valueFormatter: negativeCurrencyFormatter,
    cellClass: 'text-danger',
    hide: true,
  },
  {
    headerName: 'Liquidation Fees',
    field: 'liq_fees',
    width: 170,
    valueFormatter: negativeCurrencyFormatter,
    cellClass: 'text-danger',
    hide: true,
  },
  {
    headerName: 'REO Closing Cost',
    field: 'reo_closing_cost',
    width: 170,
    valueFormatter: negativeCurrencyFormatter,
    cellClass: 'text-danger',
    hide: true,
  },
  {
    headerName: 'Total Expenses',
    field: 'uw_total_expenses',
    width: 190,
    valueFormatter: negativeCurrencyFormatter,
    cellClass: 'text-danger',
    hide: true,
  },
  {
    headerName: 'Proj. Gross Cost',
    field: 'projected_gross_cost',
    width: 180,
    valueFormatter: negativeCurrencyFormatter,
    cellClass: 'text-danger',
    hide: true,
  },
  {
    headerName: 'Proj. Gross Proceeds',
    field: 'expected_gross_proceeds',
    width: 190,
    valueFormatter: currencyFormatter,
    hide: true,
  },
  {
    headerName: 'Proj. Net Proceeds',
    field: 'uw_proj_net_proceeds_calc',
    colId: 'uw_proj_net_proceeds_calc',
    width: 190,
    valueGetter: (params: ValueGetterParams<any, any>) => {
      const gross = params.data?.expected_gross_proceeds
      if (gross === null || gross === undefined) return null
      const reoClosing = params.data?.reo_closing_cost ?? 0
      const grossNum = Number(gross)
      const closingNum = Number(reoClosing) || 0
      if (Number.isNaN(grossNum)) return null
      return grossNum - closingNum
    },
    valueFormatter: currencyFormatter,
    hide: true,
  },
  {
    headerName: 'UW P/L',
    field: 'expected_pl',
    width: 170,
    valueFormatter: currencyFormatter,
    hide: true,
  },
  {
    headerName: 'Proj. P/L',
    field: 'expected_pl',
    width: 170,
    valueFormatter: negativeCurrencyFormatter,
    cellClass: 'text-danger',
    hide: true,
  },
  // Performance view columns
  {
    headerName: 'Current Hold',
    field: 'current_duration_months',
    width: 190,
    valueFormatter: numberFormatter,
    hide: true,
  },
  {
    headerName: 'Realized Gross Purchase Price',
    field: 'realized_gross_purchase_price',
    width: 190,
    valueFormatter: negativeCurrencyFormatter,
    cellClass: 'text-danger',
    hide: true,
  },
  {
    headerName: 'Realized Servicing Fees',
    field: 'expense_servicing_realized',
    width: 190,
    valueFormatter: negativeCurrencyFormatter,
    cellClass: 'text-danger',
    hide: true,
  },
  {
    headerName: 'Realized Legal Expenses',
    field: 'realized_legal_expenses',
    width: 190,
    valueFormatter: negativeCurrencyFormatter,
    cellClass: 'text-danger',
    hide: true,
  },
  {
    headerName: 'Realized Carry Cost',
    field: 'realized_operating_expenses',
    width: 210,
    valueFormatter: negativeCurrencyFormatter,
    cellClass: 'text-danger',
    hide: true,
  },
  {
    headerName: 'Realized REO Expenses',
    field: 'realized_reo_expenses',
    width: 190,
    valueFormatter: negativeCurrencyFormatter,
    cellClass: 'text-danger',
    hide: true,
  },
  {
    headerName: 'Realized Rehab / Trashout',
    field: 'realized_rehab_trashout',
    width: 200,
    valueFormatter: negativeCurrencyFormatter,
    cellClass: 'text-danger',
    hide: true,
  },
  {
    headerName: 'Realized Total Expenses',
    field: 'realized_total_expenses',
    width: 190,
    valueFormatter: negativeCurrencyFormatter,
    cellClass: 'text-danger',
    hide: true,
  },
  {
    headerName: 'Current Gross Cost',
    field: 'current_gross_cost',
    width: 170,
    valueFormatter: negativeCurrencyFormatter,
    cellClass: 'text-danger',
    hide: true,
  },
  {
    headerName: 'Realized Gross Cost',
    field: 'realized_gross_cost',
    width: 190,
    valueFormatter: negativeCurrencyFormatter,
    cellClass: 'text-danger',
    hide: true,
  },
  {
    headerName: 'Realized Gross Liquidation Proceeds',
    field: 'realized_gross_liquidation_proceeds',
    width: 220,
    valueFormatter: currencyFormatter,
    hide: true,
  },
  {
    headerName: 'Realized Net Liquidation Proceeds',
    field: 'realized_net_liquidation_proceeds',
    width: 210,
    valueFormatter: currencyFormatter,
    hide: true,
  },
  // Re-underwriting (projections) view columns
  {
    headerName: 'UW IRR',
    field: 'expected_irr',
    width: 130,
    valueFormatter: (params: ValueFormatterParams) => {
      const v = params.value
      if (v == null || v === '') return ''
      const num = Number(v) * 100
      if (Number.isNaN(num)) return String(v)
      return `${num.toFixed(1)}%`
    },
    hide: true,
  },
  {
    headerName: 'UW MOIC',
    field: 'expected_moic',
    width: 130,
    valueFormatter: (params: ValueFormatterParams) => {
      const v = params.value
      if (v == null || v === '') return ''
      const num = Number(v)
      if (Number.isNaN(num)) return String(v)
      return `${num.toFixed(2)}x`
    },
    hide: true,
  },
  {
    headerName: 'Active Tracks',
    field: 'active_tracks',
    width: 160,
    wrapText: true,
    autoHeight: true,
    cellRenderer: BadgeCell as any,
    cellRendererParams: {
      mode: 'multi',
      enumMap: activeTracksEnumMap,
      size: 'sm',
    },
    hide: true,
  },
  {
    headerName: 'Active Tasks',
    field: 'active_tasks',
    width: 200,
    wrapText: true,
    autoHeight: true,
    cellRenderer: BadgeCell as any,
    cellRendererParams: {
      mode: 'multi-prefix',
      colorMap: activeTasksColorMap,
      size: 'sm',
    },
    hide: true,
  },
])

const visibleColumnDefs = computed<(ColDef | ColGroupDef)[]>(() => {
  const view = currentGridView.value
  if (view === 'all') {
    const byField = new Map<string, ColDef>()
    for (const c of baseColumnDefs.value) {
      const f = c.field as string | undefined
      if (f) byField.set(f, c)
    }
    const pick = (fields: string[]): ColDef[] => fields
      .map(f => byField.get(f))
      .filter((c): c is ColDef => !!c)
      .map(c => {
        const fieldName = c.field as string | undefined
        const pinned = shouldPinField(fieldName)
        return pinned ? { ...c, hide: false, pinned } : { ...c, hide: false }
      })

    return [
      { headerName: 'Core', marryChildren: true, children: pick(['trade_name','servicer_id','street_address','city','state','asset_master_status']) },
      { headerName: 'Servicing', children: pick(['servicer_current_balance','servicer_total_debt','servicer_next_due_date','months_dlq']) },
      { headerName: 'Purchase', children: pick([
        'purchase_price','purchase_date','exit_strategy',
        'bid_pct_upb','bid_pct_td','bid_pct_sellerasis','bid_pct_pv',
      ]) },
      { headerName: 'Initial Underwriting', children: pick([
        'pre_reo_hold_duration','reo_hold_duration',
        'uw_exit_duration_months','expected_exit_date',
        'gross_purchase_price','legal_expenses','servicing_expenses','reo_expenses','rehab_trashout_cost','carry_cost','liq_fees','reo_closing_cost','uw_total_expenses','projected_gross_cost',
        'expected_gross_proceeds','uw_proj_net_proceeds_calc','expected_pl','expected_cf','expected_irr','expected_moic',
      ]) },
      { headerName: 'Performance', children: pick([
        'current_duration_months',
        'realized_gross_purchase_price',
        'expense_servicing_realized',
        'realized_legal_expenses',
        'realized_operating_expenses',
        'realized_reo_expenses',
        'realized_rehab_trashout',
        'realized_total_expenses',
        'current_gross_cost',
        'realized_gross_cost',
        'realized_gross_liquidation_proceeds',
        'realized_net_liquidation_proceeds',
      ]) },
      { headerName: 'Asset Management', children: pick(['active_tracks','active_tasks']) },
    ]
  }

  return baseColumnDefs.value.map(col => {
    const field = col.field as string | undefined
    if (!field) return col
    const pinned = shouldPinField(field)

    const alwaysVisible = view === 'servicing'
      ? [
        'trade_name',
        'street_address',
        'city',
        'state',
        'asset_master_status',
        'servicer_id',
      ]
      : [
        'trade_name',
        'street_address',
        'city',
        'state',
        'asset_master_status',
      ]

    if (alwaysVisible.includes(field)) {
      const updatedBase = { ...col, hide: false }
      if (view === 'servicing' && field === 'servicer_id') {
        return { ...updatedBase, pinned: 'left' }
      }
      if (pinned) {
        return { ...updatedBase, pinned }
      }
      return updatedBase
    }

    const servicingFields = [
      'servicer_id',
      'servicer_current_balance',
      'servicer_total_debt',
      'servicer_next_due_date',
      'months_dlq',
      'asset_master_status',
    ]
    const initialUnderwritingFields = [
      'purchase_price','purchase_date','exit_strategy',
      'bid_pct_upb','bid_pct_td','bid_pct_sellerasis','bid_pct_pv',
      'pre_reo_hold_duration','reo_hold_duration',
      'uw_exit_duration_months','expected_exit_date',
      'gross_purchase_price','legal_expenses','servicing_expenses','reo_expenses','rehab_trashout_cost','carry_cost','liq_fees','reo_closing_cost','uw_total_expenses','projected_gross_cost',
      'expected_gross_proceeds','uw_proj_net_proceeds_calc','expected_pl','expected_irr','expected_moic',
    ]
    const performanceFields = [
      'current_duration_months',
      'realized_gross_purchase_price',
      'expense_servicing_realized',
      'realized_legal_expenses',
      'realized_operating_expenses',
      'realized_reo_expenses',
      'realized_rehab_trashout',
      'realized_total_expenses',
      'current_gross_cost',
      'realized_gross_cost',
      'realized_gross_liquidation_proceeds',
      'realized_net_liquidation_proceeds',
    ]
    const reUnderwritingFields = [
      'expected_exit_date',
      'expected_gross_proceeds',
    ]
    const assetManagementFields = [
      'active_tracks',
      'active_tasks',
    ]

    let hide = true
    if (view === 'servicing' && servicingFields.includes(field)) hide = false
    if (view === 'initial-underwriting' && initialUnderwritingFields.includes(field)) hide = false
    if (view === 'performance' && performanceFields.includes(field)) hide = false
    if (view === 're-underwriting' && reUnderwritingFields.includes(field)) hide = false
    if (view === 'asset-management' && assetManagementFields.includes(field)) hide = false

    const updated = { ...col, hide }
    return pinned ? { ...updated, pinned } : updated
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
