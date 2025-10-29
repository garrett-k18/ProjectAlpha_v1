// src/stores/reporting.ts
// Pinia store for reporting dashboard filters, data, and views
// Docs reviewed:
// - Pinia: https://pinia.vuejs.org/core-concepts/
// - Axios instances: https://axios-http.com/docs/instance

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import http from '@/lib/http'

// **WHAT**: Trade option interface for primary filter dropdown
// **WHY**: Standardized shape for trade selection across reporting views
export interface TradeOption {
  id: number
  trade_name: string
  seller_name?: string
}

// **WHAT**: Status option interface for multi-select filter
// **WHY**: Allows filtering by multiple statuses (DD, AWARDED, etc.)
export interface StatusOption {
  value: string
  label: string
  count?: number // Optional: show count of assets in this status
}

// **WHAT**: Fund option interface for fund-level reporting
// **WHY**: Group reports by investment fund/vehicle
export interface FundOption {
  id: number
  name: string
  code?: string // Optional: short code like "FUND-I", "FUND-II"
}

// **WHAT**: Entity option interface for legal entity filtering
// **WHY**: Report by legal entity (LLC, LP, etc.) for compliance/accounting
export interface EntityOption {
  id: number
  name: string
  entity_type?: string // Optional: LLC, LP, Corporation, etc.
}

// **WHAT**: Report summary data interface
// **WHY**: Standardized response from backend summary endpoints
export interface ReportSummary {
  total_upb: number | string
  asset_count: number
  avg_ltv: number
  delinquency_rate: number
  // Add more as needed per report type
}

// **WHAT**: Chart data point interface for visualizations
// **WHY**: Consistent data shape for ApexCharts/Chart.js
export interface ChartDataPoint {
  x: string | number // Label or timestamp
  y: number          // Value
  meta?: any         // Optional: extra data for drill-downs
}

// **WHAT**: Reporting Pinia store
// **WHY**: Centralized state management for all reporting dashboard filters and data
export const useReportingStore = defineStore('reporting', () => {
  // ---------------------------------------------------------------------------
  // PRIMARY FILTERS (Trade, Status, Fund, Entity)
  // ---------------------------------------------------------------------------
  
  // **WHAT**: Selected trade ID(s) - supports single or multi-select
  // **WHY**: Filter reports by specific trades
  const selectedTradeIds = ref<number[]>([])
  
  // **WHAT**: Selected status values - multi-select
  // **WHY**: Filter by DD, AWARDED, PASS, BOARD, etc.
  const selectedStatuses = ref<string[]>([])
  
  // **WHAT**: Selected fund ID - single select
  // **WHY**: Show data for a specific investment fund
  const selectedFundId = ref<number | null>(null)
  
  // **WHAT**: Selected entity ID - single select
  // **WHY**: Filter by legal entity for accounting purposes
  const selectedEntityId = ref<number | null>(null)
  
  // ---------------------------------------------------------------------------
  // SECONDARY FILTERS
  // ---------------------------------------------------------------------------
  
  // **WHAT**: Date range for time-based filtering
  // **WHY**: Filter data by bid date, settlement date, etc.
  const dateRangeStart = ref<string | null>(null) // ISO date string YYYY-MM-DD
  const dateRangeEnd = ref<string | null>(null)
  
  // **WHAT**: Selected report view (e.g., 'by-trade', 'by-status')
  // **WHY**: Track which report is currently displayed
  const currentView = ref<string>('overview') // default to overview
  
  // ---------------------------------------------------------------------------
  // DROPDOWN OPTIONS CACHES
  // ---------------------------------------------------------------------------
  
  const tradeOptions = ref<TradeOption[]>([])
  const statusOptions = ref<StatusOption[]>([])
  const fundOptions = ref<FundOption[]>([])
  const entityOptions = ref<EntityOption[]>([])
  
  // Loading states for each filter
  const loadingTrades = ref<boolean>(false)
  const loadingStatuses = ref<boolean>(false)
  const loadingFunds = ref<boolean>(false)
  const loadingEntities = ref<boolean>(false)
  
  // Error states
  const errorTrades = ref<string | null>(null)
  const errorStatuses = ref<string | null>(null)
  const errorFunds = ref<string | null>(null)
  const errorEntities = ref<string | null>(null)
  
  // ---------------------------------------------------------------------------
  // REPORT DATA STATE
  // ---------------------------------------------------------------------------
  
  // **WHAT**: Current report summary metrics (top bar KPIs)
  // **WHY**: Show high-level metrics for selected filters
  const reportSummary = ref<ReportSummary | null>(null)
  const loadingSummary = ref<boolean>(false)
  const errorSummary = ref<string | null>(null)
  
  // **WHAT**: Chart data for current view
  // **WHY**: Populated based on selected report type
  const chartData = ref<ChartDataPoint[]>([])
  const loadingChart = ref<boolean>(false)
  const errorChart = ref<string | null>(null)
  
  // **WHAT**: Grid data for detailed table view
  // **WHY**: AG Grid or Bootstrap table showing row-level details
  const gridData = ref<any[]>([])
  const loadingGrid = ref<boolean>(false)
  const errorGrid = ref<string | null>(null)
  
  // ---------------------------------------------------------------------------
  // SAVED REPORTS (Future enhancement)
  // ---------------------------------------------------------------------------
  
  const savedReports = ref<any[]>([])
  
  // ---------------------------------------------------------------------------
  // COMPUTED PROPERTIES
  // ---------------------------------------------------------------------------
  
  // **WHAT**: Check if any primary filters are active
  // **WHY**: Show/hide reset button, determine if data should load
  const hasActiveFilters = computed<boolean>(() => {
    return (
      selectedTradeIds.value.length > 0 ||
      selectedStatuses.value.length > 0 ||
      selectedFundId.value !== null ||
      selectedEntityId.value !== null
    )
  })
  
  // **WHAT**: Build filter query string for backend API calls
  // **WHY**: Convert UI state to URL params
  const filterQueryParams = computed<string>(() => {
    const params = new URLSearchParams()
    
    if (selectedTradeIds.value.length > 0) {
      params.append('trade_ids', selectedTradeIds.value.join(','))
    }
    if (selectedStatuses.value.length > 0) {
      params.append('statuses', selectedStatuses.value.join(','))
    }
    if (selectedFundId.value !== null) {
      params.append('fund_id', String(selectedFundId.value))
    }
    if (selectedEntityId.value !== null) {
      params.append('entity_id', String(selectedEntityId.value))
    }
    if (dateRangeStart.value) {
      params.append('start_date', dateRangeStart.value)
    }
    if (dateRangeEnd.value) {
      params.append('end_date', dateRangeEnd.value)
    }
    
    return params.toString()
  })
  
  // ---------------------------------------------------------------------------
  // ACTIONS: Fetch dropdown options
  // ---------------------------------------------------------------------------
  
  /**
   * **WHAT**: Fetch trade options for filter dropdown
   * **WHY**: Populate trade selector with all available trades
   * **WHERE**: Called on dashboard mount
   * **HOW**: GET /api/reporting/trades/ (TODO: implement backend endpoint)
   */
  async function fetchTradeOptions(force: boolean = false): Promise<void> {
    if (!force && tradeOptions.value.length > 0) return // Use cache
    
    loadingTrades.value = true
    errorTrades.value = null
    
    try {
      // TODO: Update endpoint when backend is ready
      const response = await http.get<TradeOption[]>('/api/acq/trades/')
      tradeOptions.value = response.data
    } catch (error: any) {
      console.error('[ReportingStore] fetchTradeOptions error:', error)
      errorTrades.value = error.message || 'Failed to load trades'
      tradeOptions.value = []
    } finally {
      loadingTrades.value = false
    }
  }
  
  /**
   * **WHAT**: Fetch status options for filter dropdown
   * **WHY**: Populate status multi-select with all possible statuses
   * **WHERE**: Called on dashboard mount
   * **HOW**: GET /api/reporting/statuses/ (TODO: implement backend endpoint)
   */
  async function fetchStatusOptions(force: boolean = false): Promise<void> {
    if (!force && statusOptions.value.length > 0) return
    
    loadingStatuses.value = true
    errorStatuses.value = null
    
    try {
      // TODO: Update endpoint when backend is ready
      // For now, use hardcoded values matching your trade status model
      statusOptions.value = [
        { value: 'DD', label: 'Due Diligence' },
        { value: 'AWARDED', label: 'Awarded' },
        { value: 'PASS', label: 'Passed' },
        { value: 'BOARD', label: 'Boarded' },
      ]
    } catch (error: any) {
      console.error('[ReportingStore] fetchStatusOptions error:', error)
      errorStatuses.value = error.message || 'Failed to load statuses'
      statusOptions.value = []
    } finally {
      loadingStatuses.value = false
    }
  }
  
  /**
   * **WHAT**: Fetch fund options for filter dropdown
   * **WHY**: Populate fund selector
   * **WHERE**: Called on dashboard mount
   * **HOW**: GET /api/reporting/funds/ (TODO: implement backend endpoint)
   */
  async function fetchFundOptions(force: boolean = false): Promise<void> {
    if (!force && fundOptions.value.length > 0) return
    
    loadingFunds.value = true
    errorFunds.value = null
    
    try {
      // TODO: Update endpoint when backend is ready
      // Placeholder - replace with real API call
      fundOptions.value = [
        { id: 1, name: 'Fund I', code: 'FUND-I' },
        { id: 2, name: 'Fund II', code: 'FUND-II' },
      ]
    } catch (error: any) {
      console.error('[ReportingStore] fetchFundOptions error:', error)
      errorFunds.value = error.message || 'Failed to load funds'
      fundOptions.value = []
    } finally {
      loadingFunds.value = false
    }
  }
  
  /**
   * **WHAT**: Fetch entity options for filter dropdown
   * **WHY**: Populate entity selector
   * **WHERE**: Called on dashboard mount
   * **HOW**: GET /api/reporting/entities/ (TODO: implement backend endpoint)
   */
  async function fetchEntityOptions(force: boolean = false): Promise<void> {
    if (!force && entityOptions.value.length > 0) return
    
    loadingEntities.value = true
    errorEntities.value = null
    
    try {
      // TODO: Update endpoint when backend is ready
      // Placeholder - replace with real API call
      entityOptions.value = [
        { id: 1, name: 'Alpha Capital LLC', entity_type: 'LLC' },
        { id: 2, name: 'Beta Properties LP', entity_type: 'LP' },
      ]
    } catch (error: any) {
      console.error('[ReportingStore] fetchEntityOptions error:', error)
      errorEntities.value = error.message || 'Failed to load entities'
      entityOptions.value = []
    } finally {
      loadingEntities.value = false
    }
  }
  
  // ---------------------------------------------------------------------------
  // ACTIONS: Fetch report data
  // ---------------------------------------------------------------------------
  
  /**
   * **WHAT**: Fetch report summary metrics (KPIs for top bar)
   * **WHY**: Show high-level metrics based on current filters
   * **WHERE**: Called when filters change or view loads
   * **HOW**: GET /api/reporting/summary/?{filterQueryParams}
   */
  async function fetchReportSummary(): Promise<void> {
    loadingSummary.value = true
    errorSummary.value = null
    
    try {
      // TODO: Update endpoint when backend is ready
      const query = filterQueryParams.value
      const url = `/api/reporting/summary/${query ? '?' + query : ''}`
      const response = await http.get<ReportSummary>(url)
      reportSummary.value = response.data
    } catch (error: any) {
      console.error('[ReportingStore] fetchReportSummary error:', error)
      errorSummary.value = error.message || 'Failed to load summary'
      reportSummary.value = null
    } finally {
      loadingSummary.value = false
    }
  }
  
  /**
   * **WHAT**: Fetch chart data for current view
   * **WHY**: Populate main visualization based on selected report type
   * **WHERE**: Called when view or filters change
   * **HOW**: GET /api/reporting/{currentView}/?{filterQueryParams}
   */
  async function fetchChartData(): Promise<void> {
    loadingChart.value = true
    errorChart.value = null
    
    try {
      // TODO: Update endpoint when backend is ready
      const query = filterQueryParams.value
      const url = `/api/reporting/${currentView.value}/${query ? '?' + query : ''}`
      const response = await http.get<ChartDataPoint[]>(url)
      chartData.value = response.data
    } catch (error: any) {
      console.error('[ReportingStore] fetchChartData error:', error)
      errorChart.value = error.message || 'Failed to load chart data'
      chartData.value = []
    } finally {
      loadingChart.value = false
    }
  }
  
  /**
   * **WHAT**: Fetch grid/table data for current view
   * **WHY**: Show detailed row-level data below charts
   * **WHERE**: Called when view or filters change
   * **HOW**: GET /api/reporting/{currentView}/grid/?{filterQueryParams}
   */
  async function fetchGridData(): Promise<void> {
    loadingGrid.value = true
    errorGrid.value = null
    
    try {
      // TODO: Update endpoint when backend is ready
      const query = filterQueryParams.value
      const url = `/api/reporting/${currentView.value}/grid/${query ? '?' + query : ''}`
      const response = await http.get<any[]>(url)
      gridData.value = response.data
    } catch (error: any) {
      console.error('[ReportingStore] fetchGridData error:', error)
      errorGrid.value = error.message || 'Failed to load grid data'
      gridData.value = []
    } finally {
      loadingGrid.value = false
    }
  }
  
  // ---------------------------------------------------------------------------
  // ACTIONS: Filter mutations
  // ---------------------------------------------------------------------------
  
  /**
   * **WHAT**: Reset all filters to default state
   * **WHY**: Clear button to start fresh
   */
  function resetFilters(): void {
    selectedTradeIds.value = []
    selectedStatuses.value = []
    selectedFundId.value = null
    selectedEntityId.value = null
    dateRangeStart.value = null
    dateRangeEnd.value = null
  }
  
  /**
   * **WHAT**: Change current report view
   * **WHY**: Switch between By Trade, By Status, etc.
   */
  function setView(viewName: string): void {
    currentView.value = viewName
  }
  
  /**
   * **WHAT**: Refresh all dropdown options
   * **WHY**: Force cache invalidation after imports or edits
   */
  async function refreshAllOptions(): Promise<void> {
    await Promise.all([
      fetchTradeOptions(true),
      fetchStatusOptions(true),
      fetchFundOptions(true),
      fetchEntityOptions(true),
    ])
  }
  
  // ---------------------------------------------------------------------------
  // RETURN PUBLIC API
  // ---------------------------------------------------------------------------
  
  return {
    // State
    selectedTradeIds,
    selectedStatuses,
    selectedFundId,
    selectedEntityId,
    dateRangeStart,
    dateRangeEnd,
    currentView,
    tradeOptions,
    statusOptions,
    fundOptions,
    entityOptions,
    loadingTrades,
    loadingStatuses,
    loadingFunds,
    loadingEntities,
    errorTrades,
    errorStatuses,
    errorFunds,
    errorEntities,
    reportSummary,
    loadingSummary,
    errorSummary,
    chartData,
    loadingChart,
    errorChart,
    gridData,
    loadingGrid,
    errorGrid,
    savedReports,
    
    // Computed
    hasActiveFilters,
    filterQueryParams,
    
    // Actions
    fetchTradeOptions,
    fetchStatusOptions,
    fetchFundOptions,
    fetchEntityOptions,
    fetchReportSummary,
    fetchChartData,
    fetchGridData,
    resetFilters,
    setView,
    refreshAllOptions,
  }
})
