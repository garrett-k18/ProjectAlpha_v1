<template>
  <div>
    <!-- Trade Wrap-Up Summary Table -->
    <div class="card">
      <div class="d-flex card-header justify-content-between align-items-center">
        <h4 class="header-title">
          <i class="mdi mdi-table-large me-2"></i>
          Trade Wrap-Up Summary
        </h4>
      </div>

      <div class="card-body pt-2 pb-3">
        <div v-if="loadingGrid" class="text-center py-4">
          <div class="spinner-border spinner-border-sm text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="text-muted small mt-2 mb-0">Calculating summary...</p>
        </div>

        <div v-else-if="!gridData || gridData.length === 0" class="text-center py-4 text-muted">
          <i class="mdi mdi-information-outline fs-3 d-block mb-2"></i>
          <p class="mb-0">No trade data available.</p>
        </div>

        <div v-else class="table-responsive">
          <table class="table table-sm table-bordered mb-0 wrap-up-table">
            <thead>
              <tr class="table-light">
                <th class="text-start" style="width: 180px;">Category</th>
                <th class="text-center">Count</th>
                <th class="text-end">Purchase Price</th>
                <th class="text-end">Total Expenses</th>
                <th class="text-end">Gross Proceeds</th>
                <th class="text-end">Net P/L</th>
                <th class="text-end">Avg MOIC</th>
              </tr>
            </thead>
            <tbody>
              <!-- Closed/Liquidated Row -->
              <tr class="closed-row expandable-row" @click="toggleExpand('closed')">
                <td class="text-start">
                  <i class="mdi me-1" :class="expanded.closed ? 'mdi-chevron-down' : 'mdi-chevron-right'"></i>
                  <strong>Liquidated</strong>
                </td>
                <td class="text-center">{{ summaryStats.closed.count }}</td>
                <td class="text-end text-danger">{{ formatCurrency(summaryStats.closed.purchasePrice) }}</td>
                <td class="text-end text-danger">{{ formatCurrency(summaryStats.closed.totalExpenses) }}</td>
                <td class="text-end text-success">{{ formatCurrency(summaryStats.closed.grossProceeds) }}</td>
                <td class="text-end" :class="summaryStats.closed.netPL >= 0 ? 'text-success' : 'text-danger'">
                  {{ formatCurrency(summaryStats.closed.netPL) }}
                </td>
                <td class="text-end">{{ formatMoic(summaryStats.closed.avgMoic) }}</td>
              </tr>
              <!-- Closed Trade Breakdown Rows -->
              <template v-if="expanded.closed">
                <tr v-for="trade in tradeBreakdown.closed" :key="'closed-' + trade.tradeName" class="nested-row closed-nested">
                  <td class="text-start ps-4">
                    <small class="text-muted">{{ trade.tradeName }}</small>
                  </td>
                  <td class="text-center"><small>{{ trade.count }}</small></td>
                  <td class="text-end"><small class="text-danger">{{ formatCurrency(trade.purchasePrice) }}</small></td>
                  <td class="text-end"><small class="text-danger">{{ formatCurrency(trade.totalExpenses) }}</small></td>
                  <td class="text-end"><small class="text-success">{{ formatCurrency(trade.grossProceeds) }}</small></td>
                  <td class="text-end"><small :class="trade.netPL >= 0 ? 'text-success' : 'text-danger'">{{ formatCurrency(trade.netPL) }}</small></td>
                  <td class="text-end"><small>{{ formatMoic(trade.avgMoic) }}</small></td>
                </tr>
              </template>

              <!-- Open/Active Row -->
              <tr class="open-row expandable-row" @click="toggleExpand('open')">
                <td class="text-start">
                  <i class="mdi me-1" :class="expanded.open ? 'mdi-chevron-down' : 'mdi-chevron-right'"></i>
                  <strong>Active</strong>
                </td>
                <td class="text-center">{{ summaryStats.open.count }}</td>
                <td class="text-end text-danger">{{ formatCurrency(summaryStats.open.purchasePrice) }}</td>
                <td class="text-end text-danger">{{ formatCurrency(summaryStats.open.totalExpenses) }}</td>
                <td class="text-end text-muted">{{ formatCurrency(summaryStats.open.projGrossProceeds ?? 0) }}</td>
                <td class="text-end text-muted">{{ formatCurrency(summaryStats.open.projNetPL ?? 0) }}</td>
                <td class="text-end text-muted">{{ formatMoic(summaryStats.open.projMoic ?? 0) }}</td>
              </tr>
              <!-- Open Trade Breakdown Rows -->
              <template v-if="expanded.open">
                <tr v-for="trade in tradeBreakdown.open" :key="'open-' + trade.tradeName" class="nested-row open-nested">
                  <td class="text-start ps-4">
                    <small class="text-muted">{{ trade.tradeName }}</small>
                  </td>
                  <td class="text-center"><small>{{ trade.count }}</small></td>
                  <td class="text-end"><small class="text-danger">{{ formatCurrency(trade.purchasePrice) }}</small></td>
                  <td class="text-end"><small class="text-danger">{{ formatCurrency(trade.totalExpenses) }}</small></td>
                  <td class="text-end"><small class="text-muted">{{ formatCurrency(trade.projGrossProceeds) }}</small></td>
                  <td class="text-end"><small class="text-muted">{{ formatCurrency(trade.projNetPL) }}</small></td>
                  <td class="text-end"><small class="text-muted">{{ formatMoic(trade.projMoic) }}</small></td>
                </tr>
              </template>

              <!-- Blended/Proforma Row -->
              <tr class="blended-row table-active fw-semibold expandable-row" @click="toggleExpand('blended')">
                <td class="text-start">
                  <i class="mdi me-1" :class="expanded.blended ? 'mdi-chevron-down' : 'mdi-chevron-right'"></i>
                  <strong>Total Portfolio (Blended)</strong>
                </td>
                <td class="text-center">{{ summaryStats.blended.count }}</td>
                <td class="text-end text-danger">{{ formatCurrency(summaryStats.blended.purchasePrice) }}</td>
                <td class="text-end text-danger">{{ formatCurrency(summaryStats.blended.totalExpenses) }}</td>
                <td class="text-end">{{ formatCurrency(summaryStats.blended.grossProceeds) }}</td>
                <td class="text-end" :class="summaryStats.blended.netPL >= 0 ? 'text-success' : 'text-danger'">
                  {{ formatCurrency(summaryStats.blended.netPL) }}
                </td>
                <td class="text-end">{{ formatMoic(summaryStats.blended.avgMoic) }}</td>
              </tr>
              <!-- Blended Trade Breakdown Rows -->
              <template v-if="expanded.blended">
                <tr v-for="trade in tradeBreakdown.blended" :key="'blended-' + trade.tradeName" class="nested-row blended-nested">
                  <td class="text-start ps-4">
                    <small class="text-muted">{{ trade.tradeName }}</small>
                  </td>
                  <td class="text-center"><small>{{ trade.count }}</small></td>
                  <td class="text-end"><small class="text-danger">{{ formatCurrency(trade.purchasePrice) }}</small></td>
                  <td class="text-end"><small class="text-danger">{{ formatCurrency(trade.totalExpenses) }}</small></td>
                  <td class="text-end"><small>{{ formatCurrency(trade.grossProceeds) }}</small></td>
                  <td class="text-end"><small :class="trade.netPL >= 0 ? 'text-success' : 'text-danger'">{{ formatCurrency(trade.netPL) }}</small></td>
                  <td class="text-end"><small>{{ formatMoic(trade.avgMoic) }}</small></td>
                </tr>
              </template>
            </tbody>
          </table>

          <div class="row mt-3 g-2">
            <div class="col-md-4">
              <div class="border rounded p-2 text-center bg-light">
                <small class="text-muted d-block">Realized Return (Closed)</small>
                <span class="fs-5 fw-bold" :class="summaryStats.closed.netPL >= 0 ? 'text-success' : 'text-danger'">
                  {{ formatCurrency(summaryStats.closed.netPL) }}
                </span>
              </div>
            </div>
            <div class="col-md-4">
              <div class="border rounded p-2 text-center bg-light">
                <small class="text-muted d-block">Projected Return (Open)</small>
                <span class="fs-5 fw-bold text-muted">
                  {{ formatCurrency(summaryStats.open.projNetPL ?? 0) }}
                </span>
              </div>
            </div>
            <div class="col-md-4">
              <div class="border rounded p-2 text-center bg-light">
                <small class="text-muted d-block">Total Blended P/L</small>
                <span class="fs-5 fw-bold" :class="summaryStats.blended.netPL >= 0 ? 'text-success' : 'text-danger'">
                  {{ formatCurrency(summaryStats.blended.netPL) }}
                </span>
              </div>
            </div>
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
        </div>
      </div>

      <div class="card-body">
        <ReportingAgGrid
          ref="agGridRef"
          :column-defs="visibleColumnDefs"
          :row-data="gridData"
          :loading="loadingGrid"
          grid-height="1200px"
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
import { ref, computed } from 'vue'
import type { ColDef, ColGroupDef, ValueFormatterParams, ValueGetterParams } from 'ag-grid-community'
import ReportingAgGrid from '../components/ReportingAgGrid.vue'
import BadgeCell from '@/views/acq_module/acq_dash/components/BadgeCell.vue'
import { activeTracksEnumMap, activeTasksColorMap } from '@/config/badgeTokens'

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

// WHAT: Interface for summary statistics
interface CategoryStats {
  count: number
  purchasePrice: number
  totalExpenses: number
  grossProceeds: number
  netPL: number
  avgMoic: number
  projGrossProceeds?: number
  projNetPL?: number
  projMoic?: number
}

// WHAT: Interface for per-trade breakdown stats
interface TradeStats {
  tradeName: string
  count: number
  purchasePrice: number
  totalExpenses: number
  grossProceeds: number
  netPL: number
  avgMoic: number
  projGrossProceeds: number
  projNetPL: number
  projMoic: number
}

// WHAT: Expand/collapse state for each category row
const expanded = ref<{ closed: boolean; open: boolean; blended: boolean }>({
  closed: false,
  open: false,
  blended: false,
})

// WHAT: Toggle expand/collapse for a category
function toggleExpand(category: 'closed' | 'open' | 'blended'): void {
  expanded.value[category] = !expanded.value[category]
}

// WHAT: Compute summary stats for closed, open, and blended categories
// WHY: Provides high-level trade wrap-up view replacing the chart
const summaryStats = computed(() => {
  const data = props.gridData || []
  
  // Partition assets by status
  const closed = data.filter((d: any) => 
    d.asset_master_status?.toUpperCase() === 'LIQUIDATED' || 
    d.asset_master_status?.toUpperCase() === 'CLOSED'
  )
  const open = data.filter((d: any) => 
    d.asset_master_status?.toUpperCase() !== 'LIQUIDATED' && 
    d.asset_master_status?.toUpperCase() !== 'CLOSED'
  )
  
  // Helper to safely sum numeric fields
  const sum = (arr: any[], field: string): number => {
    return arr.reduce((acc, item) => {
      const val = item[field]
      return acc + (typeof val === 'number' ? val : (Number(val) || 0))
    }, 0)
  }
  
  // Helper to calculate average (non-null values only)
  const avg = (arr: any[], field: string): number => {
    const validItems = arr.filter(item => item[field] != null && !isNaN(Number(item[field])))
    if (validItems.length === 0) return 0
    return sum(validItems, field) / validItems.length
  }
  
  // Closed/Liquidated stats (realized values)
  const closedStats: CategoryStats = {
    count: closed.length,
    purchasePrice: sum(closed, 'realized_gross_purchase_price') || sum(closed, 'purchase_price'),
    totalExpenses: sum(closed, 'realized_total_expenses'),
    grossProceeds: sum(closed, 'realized_gross_liquidation_proceeds'),
    netPL: sum(closed, 'realized_net_liquidation_proceeds') - Math.abs(sum(closed, 'realized_gross_cost')),
    avgMoic: avg(closed, 'realized_moic') || avg(closed, 'expected_moic'),
  }
  
  // Open/Active stats (projected/underwritten values)
  const openStats: CategoryStats = {
    count: open.length,
    purchasePrice: sum(open, 'purchase_price') || sum(open, 'gross_purchase_price'),
    totalExpenses: sum(open, 'realized_total_expenses') || sum(open, 'uw_total_expenses'),
    grossProceeds: 0, // No realized proceeds yet
    netPL: 0, // No realized P/L yet
    avgMoic: 0,
    projGrossProceeds: sum(open, 'expected_gross_proceeds'),
    projNetPL: sum(open, 'expected_pl'),
    projMoic: avg(open, 'expected_moic'),
  }
  
  // Blended stats (combined proforma)
  const blendedStats: CategoryStats = {
    count: data.length,
    purchasePrice: closedStats.purchasePrice + openStats.purchasePrice,
    totalExpenses: closedStats.totalExpenses + openStats.totalExpenses,
    grossProceeds: closedStats.grossProceeds + (openStats.projGrossProceeds || 0),
    netPL: closedStats.netPL + (openStats.projNetPL || 0),
    avgMoic: data.length > 0 
      ? (closedStats.avgMoic * closed.length + (openStats.projMoic || 0) * open.length) / data.length
      : 0,
  }
  
  return {
    closed: closedStats,
    open: openStats,
    blended: blendedStats,
  }
})

// WHAT: Compute per-trade breakdown for each category
// WHY: Show detailed trade-level stats when user expands a category row
const tradeBreakdown = computed(() => {
  const data = props.gridData || []
  
  // Helper to safely sum numeric fields
  const sum = (arr: any[], field: string): number => {
    return arr.reduce((acc, item) => {
      const val = item[field]
      return acc + (typeof val === 'number' ? val : (Number(val) || 0))
    }, 0)
  }
  
  // Helper to calculate average (non-null values only)
  const avg = (arr: any[], field: string): number => {
    const validItems = arr.filter(item => item[field] != null && !isNaN(Number(item[field])))
    if (validItems.length === 0) return 0
    return sum(validItems, field) / validItems.length
  }
  
  // Group data by trade_name
  const tradeGroups = new Map<string, any[]>()
  for (const item of data) {
    const tradeName = item.trade_name || 'Unknown'
    if (!tradeGroups.has(tradeName)) {
      tradeGroups.set(tradeName, [])
    }
    tradeGroups.get(tradeName)!.push(item)
  }
  
  // Calculate stats for each trade in each category
  const closedByTrade: TradeStats[] = []
  const openByTrade: TradeStats[] = []
  const blendedByTrade: TradeStats[] = []
  
  for (const [tradeName, assets] of tradeGroups) {
    const closedAssets = assets.filter((d: any) => 
      d.asset_master_status?.toUpperCase() === 'LIQUIDATED' || 
      d.asset_master_status?.toUpperCase() === 'CLOSED'
    )
    const openAssets = assets.filter((d: any) => 
      d.asset_master_status?.toUpperCase() !== 'LIQUIDATED' && 
      d.asset_master_status?.toUpperCase() !== 'CLOSED'
    )
    
    // Closed stats per trade
    if (closedAssets.length > 0) {
      closedByTrade.push({
        tradeName,
        count: closedAssets.length,
        purchasePrice: sum(closedAssets, 'realized_gross_purchase_price') || sum(closedAssets, 'purchase_price'),
        totalExpenses: sum(closedAssets, 'realized_total_expenses'),
        grossProceeds: sum(closedAssets, 'realized_gross_liquidation_proceeds'),
        netPL: sum(closedAssets, 'realized_net_liquidation_proceeds') - Math.abs(sum(closedAssets, 'realized_gross_cost')),
        avgMoic: avg(closedAssets, 'realized_moic') || avg(closedAssets, 'expected_moic'),
        projGrossProceeds: 0,
        projNetPL: 0,
        projMoic: 0,
      })
    }
    
    // Open stats per trade
    if (openAssets.length > 0) {
      openByTrade.push({
        tradeName,
        count: openAssets.length,
        purchasePrice: sum(openAssets, 'purchase_price') || sum(openAssets, 'gross_purchase_price'),
        totalExpenses: sum(openAssets, 'realized_total_expenses') || sum(openAssets, 'uw_total_expenses'),
        grossProceeds: 0,
        netPL: 0,
        avgMoic: 0,
        projGrossProceeds: sum(openAssets, 'expected_gross_proceeds'),
        projNetPL: sum(openAssets, 'expected_pl'),
        projMoic: avg(openAssets, 'expected_moic'),
      })
    }
    
    // Blended stats per trade (all assets)
    if (assets.length > 0) {
      const closedPP = sum(closedAssets, 'realized_gross_purchase_price') || sum(closedAssets, 'purchase_price')
      const openPP = sum(openAssets, 'purchase_price') || sum(openAssets, 'gross_purchase_price')
      const closedGP = sum(closedAssets, 'realized_gross_liquidation_proceeds')
      const openProjGP = sum(openAssets, 'expected_gross_proceeds')
      const closedPL = sum(closedAssets, 'realized_net_liquidation_proceeds') - Math.abs(sum(closedAssets, 'realized_gross_cost'))
      const openProjPL = sum(openAssets, 'expected_pl')
      const closedMoic = avg(closedAssets, 'realized_moic') || avg(closedAssets, 'expected_moic')
      const openMoic = avg(openAssets, 'expected_moic')
      
      blendedByTrade.push({
        tradeName,
        count: assets.length,
        purchasePrice: closedPP + openPP,
        totalExpenses: sum(closedAssets, 'realized_total_expenses') + (sum(openAssets, 'realized_total_expenses') || sum(openAssets, 'uw_total_expenses')),
        grossProceeds: closedGP + openProjGP,
        netPL: closedPL + openProjPL,
        avgMoic: assets.length > 0
          ? (closedMoic * closedAssets.length + openMoic * openAssets.length) / assets.length
          : 0,
        projGrossProceeds: openProjGP,
        projNetPL: openProjPL,
        projMoic: openMoic,
      })
    }
  }
  
  // Sort by count descending
  closedByTrade.sort((a, b) => b.count - a.count)
  openByTrade.sort((a, b) => b.count - a.count)
  blendedByTrade.sort((a, b) => b.count - a.count)
  
  return {
    closed: closedByTrade,
    open: openByTrade,
    blended: blendedByTrade,
  }
})

// WHAT: Format number as currency for display in template
function formatCurrency(value: number): string {
  if (value === null || value === undefined || isNaN(value)) return '$0'
  const absValue = Math.abs(value)
  if (absValue >= 1_000_000) {
    return `${value < 0 ? '-' : ''}$${(absValue / 1_000_000).toFixed(1)}MM`
  }
  if (absValue >= 1_000) {
    return `${value < 0 ? '-' : ''}$${(absValue / 1_000).toFixed(0)}K`
  }
  return new Intl.NumberFormat('en-US', { 
    style: 'currency', 
    currency: 'USD', 
    maximumFractionDigits: 0 
  }).format(value)
}

// WHAT: Format MOIC multiplier for display
function formatMoic(value: number): string {
  if (value === null || value === undefined || isNaN(value) || value === 0) return '—'
  return `${value.toFixed(2)}x`
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
    aggFunc: 'skip',
  },
  {
    headerName: 'Servicer ID',
    field: 'servicer_id',
    width: 120,
    minWidth: 120,
    headerClass: 'ag-left-aligned-header text-start',
    cellClass: 'ag-left-aligned-cell text-start',
    hide: true,
    aggFunc: 'count',
  },
  {
    headerName: 'Address',
    field: 'street_address',
    width: 260,
    minWidth: 260,
    headerClass: 'ag-left-aligned-header text-start',
    cellClass: 'ag-left-aligned-cell text-start',
    aggFunc: 'skip',
  },
  {
    headerName: 'City',
    field: 'city',
    width: 180,
    minWidth: 180,
    headerClass: 'ag-left-aligned-header text-start',
    cellClass: 'ag-left-aligned-cell text-start',
    aggFunc: 'skip',
  },
  {
    headerName: 'State',
    field: 'state',
    width: 90,
    minWidth: 90,
    hide: false,
    aggFunc: 'skip',
  },
  {
    headerName: 'Lifecycle Status',
    field: 'asset_master_status',
    width: 120,
    minWidth: 120,
    valueFormatter: (params: ValueFormatterParams) => params.value || '—',
    hide: true,
    aggFunc: 'skip',
  },
  {
    headerName: 'Bid Price',
    field: 'purchase_price',
    width: 150,
    valueFormatter: currencyFormatter,
    hide: true,
    aggFunc: 'sum',
  },
  {
    headerName: 'Purchase Date',
    field: 'purchase_date',
    width: 130,
    valueFormatter: dateFormatter,
    aggFunc: 'skip',
  },
  {
    headerName: 'Balance at Purchase',
    field: 'current_balance',
    width: 150,
    valueFormatter: currencyFormatter,
    hide: true,
    aggFunc: 'sum',
  },
  {
    headerName: 'Total Debt at Purchase',
    field: 'total_debt',
    width: 150,
    valueFormatter: currencyFormatter,
    hide: true,
    aggFunc: 'sum',
  },
  {
    headerName: 'Seller As-Is at Purchase',
    field: 'seller_asis_value',
    width: 170,
    valueFormatter: currencyFormatter,
    hide: true,
    aggFunc: 'sum',
  },
  // Servicing view specific columns
  {
    headerName: 'Current Balance',
    field: 'servicer_current_balance',
    width: 150,
    valueFormatter: currencyFormatter,
    hide: true,
    aggFunc: 'sum',
  },
  {
    headerName: 'Total Debt',
    field: 'servicer_total_debt',
    width: 150,
    valueFormatter: currencyFormatter,
    hide: true,
    aggFunc: 'sum',
  },
  {
    headerName: 'Next Due Date',
    field: 'servicer_next_due_date',
    width: 130,
    valueFormatter: dateFormatter,
    hide: true,
    aggFunc: 'skip',
  },
  {
    headerName: 'Months DLQ',
    field: 'months_dlq',
    width: 120,
    valueFormatter: numberFormatter,
    hide: true,
    aggFunc: { type: 'weightedAvg', weightField: 'purchase_price' } as any,
  },
  {
    headerName: 'Current FICO',
    field: 'servicer_current_fico',
    width: 120,
    valueFormatter: numberFormatter,
    hide: true,
    aggFunc: 'avg',
  },
  {
    headerName: 'Interest Rate',
    field: 'servicer_interest_rate',
    width: 130,
    valueFormatter: percentFormatter,
    hide: true,
    aggFunc: 'avg',
  },
  {
    headerName: 'Maturity Date',
    field: 'servicer_maturity_date',
    width: 130,
    valueFormatter: dateFormatter,
    hide: true,
    aggFunc: 'skip',
  },
  // Purchase view columns
  {
    headerName: 'Exit Strategy',
    field: 'exit_strategy',
    width: 160,
    hide: true,
    aggFunc: 'skip',
  },
  {
    headerName: 'Bid % UPB',
    field: 'bid_pct_upb',
    width: 130,
    valueFormatter: percentFormatter,
    hide: true,
    aggFunc: { type: 'ratioOfSums', numeratorField: 'purchase_price', denominatorField: 'current_balance' } as any,
  },
  {
    headerName: 'Bid % TD',
    field: 'bid_pct_td',
    width: 120,
    valueFormatter: percentFormatter,
    hide: true,
    aggFunc: { type: 'ratioOfSums', numeratorField: 'purchase_price', denominatorField: 'total_debt' } as any,
  },
  {
    headerName: 'Bid % Seller As-Is',
    field: 'bid_pct_sellerasis',
    width: 170,
    valueFormatter: percentFormatter,
    hide: true,
    aggFunc: { type: 'ratioOfSums', numeratorField: 'purchase_price', denominatorField: 'seller_asis_value' } as any,
  },
  {
    headerName: 'Bid % PV',
    field: 'bid_pct_pv',
    width: 120,
    valueFormatter: percentFormatter,
    hide: true,
    aggFunc: { type: 'weightedAvg', weightField: 'purchase_price' } as any,
  },
  // Initial underwriting view columns
  {
    headerName: 'Pre-REO Hold',
    field: 'pre_reo_hold_duration',
    width: 190,
    valueFormatter: numberFormatter,
    hide: true,
    aggFunc: { type: 'weightedAvg', weightField: 'purchase_price' } as any,
  },
  {
    headerName: 'REO Hold',
    field: 'reo_hold_duration',
    width: 170,
    valueFormatter: numberFormatter,
    hide: true,
    aggFunc: { type: 'weightedAvg', weightField: 'purchase_price' } as any,
  },
  {
    headerName: 'Total Hold',
    field: 'uw_exit_duration_months',
    width: 210,
    valueFormatter: numberFormatter,
    hide: true,
    aggFunc: { type: 'weightedAvg', weightField: 'purchase_price' } as any,
  },
  {
    headerName: 'Exit Date',
    field: 'expected_exit_date',
    width: 140,
    valueFormatter: dateFormatter,
    hide: true,
    aggFunc: 'skip',
  },
  {
    headerName: 'Gross Purchase Price',
    field: 'gross_purchase_price',
    width: 170,
    valueFormatter: negativeCurrencyFormatter,
    cellClass: 'text-danger',
    hide: true,
    aggFunc: 'sum',
  },
  {
    headerName: 'Legal Expenses',
    field: 'legal_expenses',
    width: 150,
    valueFormatter: negativeCurrencyFormatter,
    cellClass: 'text-danger',
    hide: true,
    aggFunc: 'sum',
  },
  {
    headerName: 'Servicing Fees',
    field: 'servicing_expenses',
    width: 170,
    valueFormatter: negativeCurrencyFormatter,
    cellClass: 'text-danger',
    hide: true,
    aggFunc: 'sum',
  },
  {
    headerName: 'REO Expenses',
    field: 'reo_expenses',
    width: 150,
    valueFormatter: negativeCurrencyFormatter,
    cellClass: 'text-danger',
    hide: true,
    aggFunc: 'sum',
  },
  {
    headerName: 'Rehab / Trashout',
    field: 'rehab_trashout_cost',
    width: 160,
    valueFormatter: negativeCurrencyFormatter,
    cellClass: 'text-danger',
    hide: true,
    aggFunc: 'sum',
  },
  {
    headerName: 'Carry Cost',
    field: 'carry_cost',
    width: 170,
    valueFormatter: negativeCurrencyFormatter,
    cellClass: 'text-danger',
    hide: true,
    aggFunc: 'sum',
  },
  {
    headerName: 'Liquidation Fees',
    field: 'liq_fees',
    width: 170,
    valueFormatter: negativeCurrencyFormatter,
    cellClass: 'text-danger',
    hide: true,
    aggFunc: 'sum',
  },
  {
    headerName: 'REO Closing Cost',
    field: 'reo_closing_cost',
    width: 170,
    valueFormatter: negativeCurrencyFormatter,
    cellClass: 'text-danger',
    hide: true,
    aggFunc: 'sum',
  },
  {
    headerName: 'Total Expenses',
    field: 'uw_total_expenses',
    width: 190,
    valueFormatter: negativeCurrencyFormatter,
    cellClass: 'text-danger',
    hide: true,
    aggFunc: 'sum',
  },
  {
    headerName: 'Proj. Gross Cost',
    field: 'projected_gross_cost',
    width: 180,
    valueFormatter: negativeCurrencyFormatter,
    cellClass: 'text-danger',
    hide: true,
    aggFunc: 'sum',
  },
  {
    headerName: 'Proj. Gross Proceeds',
    field: 'expected_gross_proceeds',
    width: 190,
    valueFormatter: currencyFormatter,
    hide: true,
    aggFunc: 'sum',
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
    aggFunc: 'sum',
  },
  {
    headerName: 'UW P/L',
    field: 'expected_pl',
    width: 170,
    valueFormatter: currencyFormatter,
    hide: true,
    aggFunc: 'sum',
  },
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
    aggFunc: { type: 'weightedAvg', weightField: 'purchase_price' } as any,
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
    aggFunc: { type: 'weightedAvg', weightField: 'purchase_price' } as any,
  },
  // Performance view columns
  {
    headerName: 'Current Hold',
    field: 'current_duration_months',
    width: 190,
    valueFormatter: numberFormatter,
    hide: true,
    aggFunc: { type: 'weightedAvg', weightField: 'purchase_price' } as any,
  },
  {
    headerName: 'Gross Purchase Price',
    field: 'realized_gross_purchase_price',
    width: 190,
    valueFormatter: negativeCurrencyFormatter,
    cellClass: 'text-danger',
    hide: true,
    aggFunc: 'sum',
  },
  {
    headerName: 'Servicing Fees',
    field: 'expense_servicing_realized',
    width: 190,
    valueFormatter: negativeCurrencyFormatter,
    cellClass: 'text-danger',
    hide: true,
    aggFunc: 'sum',
  },
  {
    headerName: 'Legal Expenses',
    field: 'realized_legal_expenses',
    width: 190,
    valueFormatter: negativeCurrencyFormatter,
    cellClass: 'text-danger',
    hide: true,
    aggFunc: 'sum',
  },
  {
    headerName: 'Carry Cost',
    field: 'realized_operating_expenses',
    width: 210,
    valueFormatter: negativeCurrencyFormatter,
    cellClass: 'text-danger',
    hide: true,
    aggFunc: 'sum',
  },
  {
    headerName: 'REO Expenses',
    field: 'realized_reo_expenses',
    width: 190,
    valueFormatter: negativeCurrencyFormatter,
    cellClass: 'text-danger',
    hide: true,
    aggFunc: 'sum',
  },
  {
    headerName: 'Rehab / Trashout',
    field: 'realized_rehab_trashout',
    width: 200,
    valueFormatter: negativeCurrencyFormatter,
    cellClass: 'text-danger',
    hide: true,
    aggFunc: 'sum',
  },
  {
    headerName: 'REO Closing Cost',
    field: 'realized_reo_closing_cost',
    width: 210,
    valueFormatter: negativeCurrencyFormatter,
    cellClass: 'text-danger',
    hide: true,
    aggFunc: 'sum',
  },
  {
    headerName: 'Total Expenses',
    field: 'realized_total_expenses',
    width: 190,
    valueFormatter: negativeCurrencyFormatter,
    cellClass: 'text-danger',
    hide: true,
    aggFunc: 'sum',
  },
  {
    headerName: 'Gross Cost',
    field: 'realized_gross_cost',
    width: 190,
    valueFormatter: negativeCurrencyFormatter,
    cellClass: 'text-danger',
    hide: true,
    aggFunc: 'sum',
  },
  {
    headerName: 'Gross Liquidation Proceeds',
    field: 'realized_gross_liquidation_proceeds',
    width: 220,
    valueFormatter: currencyFormatter,
    hide: true,
    aggFunc: 'sum',
  },
  {
    headerName: 'Net Liquidation Proceeds',
    field: 'realized_net_liquidation_proceeds',
    width: 210,
    valueFormatter: currencyFormatter,
    hide: true,
    aggFunc: 'sum',
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
      { headerName: 'Purchase', children: pick([
        'purchase_price','purchase_date',
        'bid_pct_upb','bid_pct_td','bid_pct_sellerasis',
      ]) },
      { headerName: 'Asset Management', children: pick(['active_tracks','active_tasks']) },
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
        'realized_reo_closing_cost',
        'realized_total_expenses',
        'realized_gross_cost',
        'realized_gross_liquidation_proceeds',
        'realized_net_liquidation_proceeds',
      ]) },
      { headerName: 'Re-underwriting', children: pick([
        'expected_exit_date',
        'expected_gross_proceeds',
      ]) },
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
      'servicer_current_fico',
      'servicer_interest_rate',
      'servicer_maturity_date',
      'asset_master_status',
    ]
    const initialUnderwritingFields = [
      'purchase_price','purchase_date',
      'current_balance','total_debt','seller_asis_value',
      'exit_strategy',
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
      'realized_reo_closing_cost',
      'realized_total_expenses',
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

/**
 * WHAT: Handle row click from AG Grid
 * WHY: Trigger drill-down modal when user clicks a row
 */
function handleRowClickFromGrid(row: any): void {
  console.log('[ByTradeReport] Row clicked:', row)
  emit('drill-down', { type: 'trade', data: row })
}
</script>

<style scoped>
.wrap-up-table th {
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  padding: 0.5rem 0.75rem;
}

.wrap-up-table td {
  padding: 0.6rem 0.75rem;
  vertical-align: middle;
}

.wrap-up-table .closed-row {
  background-color: rgba(25, 135, 84, 0.03);
}

.wrap-up-table .open-row {
  background-color: rgba(13, 110, 253, 0.03);
}

.wrap-up-table .blended-row {
  background-color: rgba(33, 37, 41, 0.05);
  border-top: 2px solid #dee2e6;
}

.wrap-up-table .expandable-row {
  cursor: pointer;
  transition: background-color 0.15s ease;
}

.wrap-up-table .expandable-row:hover {
  filter: brightness(0.97);
}

.wrap-up-table .expandable-row i.mdi {
  font-size: 1rem;
  color: #6c757d;
  transition: transform 0.2s ease;
}

.wrap-up-table .nested-row {
  background-color: rgba(0, 0, 0, 0.02);
  border-left: 3px solid transparent;
}

.wrap-up-table .nested-row.closed-nested {
  border-left-color: rgba(25, 135, 84, 0.3);
  background-color: rgba(25, 135, 84, 0.02);
}

.wrap-up-table .nested-row.open-nested {
  border-left-color: rgba(13, 110, 253, 0.3);
  background-color: rgba(13, 110, 253, 0.02);
}

.wrap-up-table .nested-row.blended-nested {
  border-left-color: rgba(33, 37, 41, 0.3);
  background-color: rgba(33, 37, 41, 0.02);
}

.wrap-up-table .nested-row td {
  padding-top: 0.35rem;
  padding-bottom: 0.35rem;
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
