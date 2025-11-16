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
// **FIELDS**: Matches backend serial_rep_filterOptions.TradeOptionSerializer
export interface TradeOption {
  id: number
  trade_name: string
  seller_name: string
  status: string
  asset_count: number
}

// **WHAT**: Track option interface for multi-select filter (AM outcome tracks)
// **WHY**: Allows filtering by multiple tracks (REO, FC, DIL, Short Sale, Modification, Note Sale)
export interface TrackOption {
  value: string
  label: string
  count?: number // Optional: show count of assets on this track
}

// **WHAT**: Task status option interface for multi-select filter
// **WHY**: Allows filtering by active task types within outcome tracks
export interface TaskStatusOption {
  value: string
  label: string
  track: string // Which track this task belongs to (reo, fc, dil, etc.)
  count?: number // Optional: show count of assets with this task
}

// **WHAT**: Partnership option interface (FundLegalEntity) for filter dropdown
// **WHY**: Users select partnerships (fund/SPV wrappers) rather than general entities
export interface PartnershipOption {
  id: number
  nickname?: string | null
  entity_role?: string | null
  entity_role_label?: string | null
  is_active: boolean
  fund_id?: number | null
  fund_name?: string | null
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
  // PRIMARY FILTERS (Trade, Status, Fund, Partnerships)
  // ---------------------------------------------------------------------------
  
  // **WHAT**: Selected trade ID(s) - supports single or multi-select
  // **WHY**: Filter reports by specific trades
  const selectedTradeIds = ref<number[]>([])
  
  // **WHAT**: Selected track values - multi-select
  // **WHY**: Filter by AM outcome tracks (REO, FC, DIL, Short Sale, Modification, Note Sale)
  const selectedTracks = ref<string[]>([])
  
  // **WHAT**: Selected task status values - multi-select
  // **WHY**: Filter by active task types (eviction, trashout, nod_noi, etc.)
  const selectedTaskStatuses = ref<string[]>([])
  
  // **WHAT**: Selected partnership IDs - multi-select
  // **WHY**: Filter by FundLegalEntity partnerships (fund wrappers, GP LLCs, SPVs)
  const selectedPartnershipIds = ref<number[]>([])
  
  // ---------------------------------------------------------------------------
  // SECONDARY FILTERS
  // ---------------------------------------------------------------------------
  
  // **WHAT**: Date range for time-based filtering
  // **WHY**: Filter data by bid date, settlement date, etc.
  const dateRangeStart = ref<string | null>(null) // ISO date string YYYY-MM-DD
  const dateRangeEnd = ref<string | null>(null)
  
  // **WHAT**: Selected report view (e.g., 'by-trade', 'by-status')
  // **WHY**: Track which report is currently displayed
  const currentView = ref<string>('by-trade') // default to by-trade (overview not implemented yet)
  
  // ---------------------------------------------------------------------------
  // DROPDOWN OPTIONS CACHES
  // ---------------------------------------------------------------------------
  
  const tradeOptions = ref<TradeOption[]>([])
  const trackOptions = ref<TrackOption[]>([])
  const taskStatusOptions = ref<TaskStatusOption[]>([])
  const partnershipOptions = ref<PartnershipOption[]>([])
  
  // Loading states for each filter
  const loadingTrades = ref<boolean>(false)
  const loadingTracks = ref<boolean>(false)
  const loadingTaskStatuses = ref<boolean>(false)
  const loadingPartnerships = ref<boolean>(false)
  
  // Error states
  const errorTrades = ref<string | null>(null)
  const errorTracks = ref<string | null>(null)
  const errorTaskStatuses = ref<string | null>(null)
  const errorPartnerships = ref<string | null>(null)
  
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
      selectedTracks.value.length > 0 ||
      selectedTaskStatuses.value.length > 0 ||
      selectedPartnershipIds.value.length > 0
    )
  })
  
  // **WHAT**: Build filter query string for backend API calls
  // **WHY**: Convert UI state to URL params
  const filterQueryParams = computed<string>(() => {
    const params = new URLSearchParams()
    
    if (selectedTradeIds.value.length > 0) {
      params.append('trade_ids', selectedTradeIds.value.join(','))
    }
    if (selectedTracks.value.length > 0) {
      params.append('tracks', selectedTracks.value.join(','))
    }
    if (selectedTaskStatuses.value.length > 0) {
      params.append('task_statuses', selectedTaskStatuses.value.join(','))
    }
    if (selectedPartnershipIds.value.length > 0) {
      params.append('entity_ids', selectedPartnershipIds.value.join(','))
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
   * **HOW**: GET /api/reporting/trades/ (Backend endpoint ready!)
   */
  async function fetchTradeOptions(force: boolean = false): Promise<void> {
    if (!force && tradeOptions.value.length > 0) return // Use cache
    
    loadingTrades.value = true
    errorTrades.value = null
    
    try {
      // WHAT: Call reporting trades endpoint
      // WHY: Get all trades from Trade model
      // ENDPOINT: GET /api/reporting/trades/
      const response = await http.get<TradeOption[]>('/reporting/trades/')
      tradeOptions.value = response.data
      console.log('[ReportingStore] Loaded trades:', response.data.length)
    } catch (error: any) {
      console.error('[ReportingStore] fetchTradeOptions error:', error)
      errorTrades.value = error.message || 'Failed to load trades'
      tradeOptions.value = []
    } finally {
      loadingTrades.value = false
    }
  }
  
  /**
   * **WHAT**: Fetch track options for filter dropdown (AM outcome tracks)
   * **WHY**: Populate track multi-select with all outcome tracks
   * **WHERE**: Called on dashboard mount
   * **HOW**: GET /api/reporting/statuses/ (Backend endpoint ready!)
   */
  async function fetchTrackOptions(force: boolean = false): Promise<void> {
    if (!force && trackOptions.value.length > 0) return
    
    loadingTracks.value = true
    errorTracks.value = null
    
    try {
      // WHAT: Call reporting tracks endpoint (statuses endpoint now returns tracks)
      // WHY: Get all AM outcome tracks (REO, FC, DIL, Short Sale, Modification, Note Sale)
      // ENDPOINT: GET /api/reporting/statuses/
      const response = await http.get<TrackOption[]>('/reporting/statuses/')
      trackOptions.value = response.data
      console.log('[ReportingStore] Loaded tracks:', response.data.length)
    } catch (error: any) {
      console.error('[ReportingStore] fetchTrackOptions error:', error)
      errorTracks.value = error.message || 'Failed to load tracks'
      trackOptions.value = []
    } finally {
      loadingTracks.value = false
    }
  }
  
  /**
   * **WHAT**: Fetch task status options for filter dropdown
   * **WHY**: Populate task status multi-select with active tasks
   * **WHERE**: Called on dashboard mount or when tracks change
   * **HOW**: GET /api/reporting/task-statuses/?track={track} (Backend endpoint ready!)
   */
  async function fetchTaskStatusOptions(trackFilter?: string, force: boolean = false): Promise<void> {
    if (!force && taskStatusOptions.value.length > 0 && !trackFilter) return
    
    loadingTaskStatuses.value = true
    errorTaskStatuses.value = null
    
    try {
      // WHAT: Call reporting task statuses endpoint
      // WHY: Get all active task types across all tracks (or filtered by specific track)
      // ENDPOINT: GET /api/reporting/task-statuses/?track={track}
      const url = trackFilter 
        ? `/reporting/task-statuses/?track=${trackFilter}`
        : '/reporting/task-statuses/'
      const response = await http.get<TaskStatusOption[]>(url)
      taskStatusOptions.value = response.data
      console.log('[ReportingStore] Loaded task statuses:', response.data.length)
    } catch (error: any) {
      console.error('[ReportingStore] fetchTaskStatusOptions error:', error)
      errorTaskStatuses.value = error.message || 'Failed to load task statuses'
      taskStatusOptions.value = []
    } finally {
      loadingTaskStatuses.value = false
    }
  }
  
  /**
   * **WHAT**: Fetch partnership options for filter dropdown
   * **WHY**: Populate partnership selector from FundLegalEntity records
   * **WHERE**: Called on dashboard mount
   * **HOW**: GET /api/reporting/partnerships/
   */
  async function fetchPartnershipOptions(force: boolean = false): Promise<void> {
    if (!force && partnershipOptions.value.length > 0) return
    
    loadingPartnerships.value = true
    errorPartnerships.value = null
    
    try {
      const response = await http.get<PartnershipOption[]>('/reporting/partnerships/')
      partnershipOptions.value = response.data
      console.log('[ReportingStore] Loaded partnerships:', response.data.length)
    } catch (error: any) {
      console.error('[ReportingStore] fetchPartnershipOptions error:', error)
      errorPartnerships.value = error.message || 'Failed to load partnerships'
      partnershipOptions.value = []
    } finally {
      loadingPartnerships.value = false
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
      // WHAT: Call reporting summary endpoint
      // ENDPOINT: GET /reporting/summary/
      const query = filterQueryParams.value
      const url = `/reporting/summary/${query ? '?' + query : ''}`
      const response = await http.get<ReportSummary>(url)
      reportSummary.value = response.data
      console.log('[ReportingStore] Loaded summary:', response.data)
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
      // WHAT: Call reporting chart endpoint
      // ENDPOINT: GET /reporting/{currentView}/
      const query = filterQueryParams.value
      const url = `/reporting/${currentView.value}/${query ? '?' + query : ''}`
      const response = await http.get<ChartDataPoint[]>(url)
      chartData.value = response.data
      console.log('[ReportingStore] Loaded chart data:', response.data.length)
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
      // WHAT: Call reporting grid endpoint
      // ENDPOINT: GET /reporting/{currentView}/grid/
      const query = filterQueryParams.value
      const url = `/reporting/${currentView.value}/grid/${query ? '?' + query : ''}`
      const response = await http.get<any[]>(url)
      gridData.value = response.data
      console.log('[ReportingStore] Loaded grid data:', response.data.length)
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
    selectedTracks.value = []
    selectedTaskStatuses.value = []
    selectedPartnershipIds.value = []
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
      fetchTrackOptions(true),
      fetchTaskStatusOptions(undefined, true),
      fetchPartnershipOptions(true),
    ])
  }
  
  // ---------------------------------------------------------------------------
  // RETURN PUBLIC API
  // ---------------------------------------------------------------------------
  
  return {
    // State
    selectedTradeIds,
    selectedTracks,
    selectedTaskStatuses,
    selectedPartnershipIds,
    dateRangeStart,
    dateRangeEnd,
    currentView,
    tradeOptions,
    trackOptions,
    taskStatusOptions,
    partnershipOptions,
    loadingTrades,
    loadingTracks,
    loadingTaskStatuses,
    loadingPartnerships,
    errorTrades,
    errorTracks,
    errorTaskStatuses,
    errorPartnerships,
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
    fetchTrackOptions,
    fetchTaskStatusOptions,
    fetchPartnershipOptions,
    fetchReportSummary,
    fetchChartData,
    fetchGridData,
    resetFilters,
    setView,
    refreshAllOptions,
  }
})
