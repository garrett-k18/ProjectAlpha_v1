/**
 * Asset Grid Data Composable
 * Manages data fetching, loading state, and sorting
 */

import { ref, watch } from 'vue'
import type { GridApi } from 'ag-grid-community'
import http from '@/lib/http'

export function useAssetGridData() {
  const rowData = ref<any[]>([])
  const loading = ref<boolean>(false)
  const sortExpr = ref<string>('')
  const gridApi = ref<GridApi | null>(null)

  // Fetch rows from backend with filters, sort, and pagination
  async function fetchRows(params: {
    page: number
    pageSize: number
    quickFilter?: string
    sortExpr?: string
    filterParams?: Record<string, any>
    props?: {
      filterTradeName?: string
      filterSellerName?: string
      filterActiveOnly?: boolean
    }
    routeQuery?: Record<string, any>
  }): Promise<{ success: boolean; data?: any }> {
    loading.value = true
    try {
      const requestParams: Record<string, any> = {
        page: params.page,
        page_size: params.pageSize,
      }

      if (params.quickFilter) requestParams.q = params.quickFilter
      if (params.sortExpr) requestParams.sort = params.sortExpr

      // Apply filters: props take precedence over URL query params
      const tradeName =
        params.props?.filterTradeName ||
        params.filterParams?.trade_name ||
        params.routeQuery?.trade_name
      const sellerName =
        params.props?.filterSellerName ||
        params.filterParams?.seller_name ||
        params.routeQuery?.seller_name
      const fundName =
        params.filterParams?.fund_name || params.routeQuery?.fund_name
      const trackTypes =
        params.filterParams?.active_tracks || params.routeQuery?.active_tracks

      if (tradeName) requestParams.trade_name = tradeName
      if (sellerName) requestParams.seller_name = sellerName
      if (fundName) requestParams.fund_name = fundName
      if (trackTypes) requestParams.active_tracks = trackTypes
      if (params.props?.filterActiveOnly) requestParams.lifecycle_status = 'ACTIVE'

      const { data } = await http.get('/am/assets/', { params: requestParams })

      rowData.value = Array.isArray(data?.results) ? data.results : []

      return { success: true, data }
    } catch (e) {
      console.error('[AssetGrid] fetch failed', e)
      rowData.value = []
      return { success: false }
    } finally {
      loading.value = false
    }
  }

  // Fetch all rows (uses server max_page_size=500)
  async function fetchAllRows(params: {
    quickFilter?: string
    sortExpr?: string
    props?: {
      filterTradeName?: string
      filterSellerName?: string
      filterActiveOnly?: boolean
    }
    routeQuery?: Record<string, any>
  }): Promise<{ success: boolean; totalCount: number }> {
    loading.value = true
    try {
      const baseParams: Record<string, any> = { page: 1, page_size: 500 }

      if (params.quickFilter) baseParams.q = params.quickFilter
      if (params.sortExpr) baseParams.sort = params.sortExpr

      // Apply filters: props take precedence over URL query params
      const tradeName =
        params.props?.filterTradeName || params.routeQuery?.trade_name
      const sellerName =
        params.props?.filterSellerName || params.routeQuery?.seller_name

      if (tradeName) baseParams.trade_name = tradeName
      if (sellerName) baseParams.seller_name = sellerName
      if (params.props?.filterActiveOnly) baseParams.lifecycle_status = 'ACTIVE'

      const all: any[] = []
      let currentPage = 1
      let count: number | null = null

      while (true) {
        const requestParams = { ...baseParams, page: currentPage }
        const { data } = await http.get('/am/assets/', { params: requestParams })
        const results = Array.isArray(data?.results) ? data.results : []

        if (count === null && typeof data?.count === 'number') count = data.count
        all.push(...results)

        if (!data?.next || results.length === 0) break

        currentPage += 1
        // Safety cap to avoid runaway loops
        if (currentPage > 100) break
      }

      rowData.value = all
      console.debug('[AssetGrid] loaded ALL rows:', rowData.value.length)

      return { success: true, totalCount: count ?? all.length }
    } catch (e) {
      console.error('[AssetGrid] fetchAll failed', e)
      rowData.value = []
      return { success: false, totalCount: 0 }
    } finally {
      loading.value = false
    }
  }

  // Fetch filter options from backend
  async function fetchFilterOptions(): Promise<{
    trades?: string[]
    sellers?: string[]
    funds?: string[]
    tracks?: string[]
  }> {
    try {
      const { data } = await http.get('/am/assets/filter_options/')
      return {
        trades: data.trades || [],
        sellers: data.sellers || [],
        funds: data.funds || [],
        tracks: data.tracks || [],
      }
    } catch (err) {
      console.error('Failed to fetch filter options:', err)
      return {}
    }
  }

  // Update asset master status via API
  async function updateAssetMasterStatus(params: {
    assetId: string | number
    newValue: string
    oldValue: string
  }): Promise<{ success: boolean; data?: any }> {
    try {
      const { data } = await http.patch(`/am/assets/${params.assetId}/`, {
        asset_master_status: params.newValue,
      })

      console.debug(
        `[AssetGrid] Updated asset_master_status: ${params.assetId} → ${params.newValue}`
      )

      return { success: true, data }
    } catch (err) {
      console.error('[AssetGrid] Failed to update asset_master_status:', err)
      return { success: false }
    }
  }

  // Handle sort changes from AG Grid
  function onSortChanged(): void {
    const api = gridApi.value as any
    if (!api) return

    const sortModel =
      api.getColumnState?.()?.filter((c: any) => c.sort != null) || []

    if (sortModel.length === 0) {
      sortExpr.value = ''
      return
    }

    const parts = sortModel.map((c: any) => {
      const field = c.colId
      const dir = c.sort === 'desc' ? '-' : ''
      return `${dir}${field}`
    })

    sortExpr.value = parts.join(',')
  }

  // Manage grid overlay state
  function syncGridOverlay(): void {
    const api = gridApi.value
    if (!api) return

    if (rowData.value.length === 0 && !loading.value) {
      api.showNoRowsOverlay()
      return
    }

    api.hideOverlay()
  }

  // Watch rowData changes to update overlay
  watch(rowData, () => {
    syncGridOverlay()
  })

  return {
    // State
    rowData,
    loading,
    sortExpr,
    gridApi,

    // Methods
    fetchRows,
    fetchAllRows,
    fetchFilterOptions,
    updateAssetMasterStatus,
    onSortChanged,
    syncGridOverlay,
  }
}
