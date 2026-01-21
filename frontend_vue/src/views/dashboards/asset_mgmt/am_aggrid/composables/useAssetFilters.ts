/**
 * Asset Grid Filter Composable
 * Manages all filter state and logic for the asset grid
 */

import { ref, computed } from 'vue'
import type { GridApi } from 'ag-grid-community'

export function useAssetFilters() {
  // Quick text filter
  const quickFilter = ref<string>('')

  // Multi-select filter arrays
  const selectedTrades = ref<string[]>([])
  const selectedSellers = ref<string[]>([])
  const selectedFunds = ref<string[]>([])
  const selectedTracks = ref<string[]>([])

  // Smart filters (active tracks, delinquent, high value, etc.)
  // TODO: Move this logic to backend API (see backend-improvements.md)
  const activeSmartFilter = ref<string>('')

  // Available options for each filter
  const uniqueTrades = ref<string[]>([])
  const uniqueSellers = ref<string[]>([])
  const uniqueFunds = ref<string[]>([])
  const uniqueTracks = ref<string[]>([])

  // Dropdown visibility state
  const showTradeDropdown = ref<boolean>(false)
  const showSellerDropdown = ref<boolean>(false)
  const showFundDropdown = ref<boolean>(false)
  const showTracksDropdown = ref<boolean>(false)

  // Check if any filters are active
  const hasActiveFilters = computed(() => {
    return (
      selectedTrades.value.length > 0 ||
      selectedSellers.value.length > 0 ||
      selectedFunds.value.length > 0 ||
      selectedTracks.value.length > 0 ||
      activeSmartFilter.value !== ''
    )
  })

  // Clear all filters
  function clearAllFilters(): void {
    selectedTrades.value = []
    selectedSellers.value = []
    selectedFunds.value = []
    selectedTracks.value = []
    activeSmartFilter.value = ''
  }

  // Close all dropdowns
  function closeAllDropdowns(): void {
    showTradeDropdown.value = false
    showSellerDropdown.value = false
    showFundDropdown.value = false
    showTracksDropdown.value = false
  }

  // Build filter params for API request
  function buildFilterParams(): Record<string, any> {
    const params: Record<string, any> = {}

    if (selectedTrades.value.length > 0) {
      params.trade_name = selectedTrades.value.join(',')
    }
    if (selectedSellers.value.length > 0) {
      params.seller_name = selectedSellers.value.join(',')
    }
    if (selectedFunds.value.length > 0) {
      params.fund_name = selectedFunds.value.join(',')
    }
    if (selectedTracks.value.length > 0) {
      params.active_tracks = selectedTracks.value.join(',')
    }

    return params
  }

  // Toggle smart filter
  function toggleSmartFilter(filterType: string): void {
    if (activeSmartFilter.value === filterType) {
      activeSmartFilter.value = ''
    } else {
      activeSmartFilter.value = filterType
    }
  }

  // External filter functions for AG Grid
  // TODO: Move this logic to backend (see backend-improvements.md)
  function isExternalFilterPresent(): boolean {
    return activeSmartFilter.value !== ''
  }

  function doesExternalFilterPass(node: any): boolean {
    if (!activeSmartFilter.value) return true

    const row = node.data
    if (!row) return false

    switch (activeSmartFilter.value) {
      case 'active_tracks':
        return !!(row.active_tracks && row.active_tracks.trim())

      case 'delinquent':
        const hasDelinquentStatus =
          row.delinquency_status &&
          String(row.delinquency_status).toLowerCase() !== 'current' &&
          String(row.delinquency_status) !== '0'
        const hasDelinquentTrack =
          row.active_tracks &&
          String(row.active_tracks).toLowerCase().includes('delinquent')
        return hasDelinquentStatus || hasDelinquentTrack

      case 'high_value':
        const currentBalance = row.servicer_loan_data?.current_balance || 0
        const arv =
          row.internal_initial_uw_arv_value || row.seller_arv_value || 0
        return currentBalance > 100000 || arv > 100000

      default:
        return true
    }
  }

  // Apply smart filter to grid
  function applySmartFilter(gridApi: GridApi | null): void {
    if (!gridApi) return
    gridApi.onFilterChanged()
  }

  // Set available filter options
  function setFilterOptions(data: {
    trades?: string[]
    sellers?: string[]
    funds?: string[]
    tracks?: string[]
  }): void {
    uniqueTrades.value = data.trades || []
    uniqueSellers.value = data.sellers || []
    uniqueFunds.value = data.funds || []
    uniqueTracks.value = data.tracks || []
  }

  return {
    // State
    quickFilter,
    selectedTrades,
    selectedSellers,
    selectedFunds,
    selectedTracks,
    activeSmartFilter,
    uniqueTrades,
    uniqueSellers,
    uniqueFunds,
    uniqueTracks,
    showTradeDropdown,
    showSellerDropdown,
    showFundDropdown,
    showTracksDropdown,

    // Computed
    hasActiveFilters,

    // Methods
    clearAllFilters,
    closeAllDropdowns,
    buildFilterParams,
    toggleSmartFilter,
    isExternalFilterPresent,
    doesExternalFilterPass,
    applySmartFilter,
    setFilterOptions,
  }
}
