<template>
  <!--
    am_aggrid.vue
    Purpose: Reusable AG Grid card for the Asset Management module.
    Visuals: Matches acquisitions grid (card header, Quartz theme, spacing).

    ✨ REFACTORED & ORGANIZED:
    - All column config in config/assetGridColumns.ts
    - Filter logic in composables/useAssetFilters.ts
    - Pagination logic in composables/useAssetPagination.ts
    - Data fetching in composables/useAssetGridData.ts
    - Modal management in composables/useAssetModals.ts
  -->
  <div class="card" ref="cardRef" :class="{ 'fullwindow-card': isFullWindow }">
    <!-- Card Header -->
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title mb-0">Asset Inventory</h4>
      <div class="d-flex align-items-center gap-2">
        <button
          class="btn btn-sm btn-light"
          type="button"
          :title="isFullWindow ? 'Exit Full Window' : 'Full Window'"
          :aria-pressed="isFullWindow ? 'true' : 'false'"
          aria-label="Toggle full window view"
          @click="toggleFullWindow"
        >
          <i class="mdi" :class="isFullWindow ? 'mdi-fullscreen-exit' : 'mdi-fullscreen'"></i>
        </button>
      </div>
    </div>

    <div class="card-body pt-0">
      <!-- Toolbar: Filters + View Selector -->
      <AssetGridToolbar
        v-model:quickFilter="filters.quickFilter.value"
        v-model:selectedTrades="filters.selectedTrades.value"
        v-model:selectedSellers="filters.selectedSellers.value"
        v-model:selectedFunds="filters.selectedFunds.value"
        v-model:selectedTracks="filters.selectedTracks.value"
        v-model:showTradeDropdown="filters.showTradeDropdown.value"
        v-model:showSellerDropdown="filters.showSellerDropdown.value"
        v-model:showFundDropdown="filters.showFundDropdown.value"
        v-model:showTracksDropdown="filters.showTracksDropdown.value"
        v-model:activeView="activeView"
        :uniqueTrades="filters.uniqueTrades.value"
        :uniqueSellers="filters.uniqueSellers.value"
        :uniqueFunds="filters.uniqueFunds.value"
        :uniqueTracks="filters.uniqueTracks.value"
        :hasActiveFilters="filters.hasActiveFilters.value"
        @filterChange="handleFilterChange"
        @clearFilters="handleClearFilters"
        @viewChange="handleViewChange"
      />

      <!-- AG Grid -->
      <ag-grid-vue
        ref="gridRef"
        class="asset-grid"
        :style="gridStyle"
        :theme="themeQuartz"
        :rowData="gridData.rowData.value"
        :columnDefs="columnDefs"
        :defaultColDef="defaultColDef"
        :isExternalFilterPresent="filters.isExternalFilterPresent"
        :doesExternalFilterPass="filters.doesExternalFilterPass"
        :selectionColumnDef="{ pinned: 'left', width: 50 }"
        :rowSelection="{ mode: 'multiRow', checkboxes: true, headerCheckbox: true, enableClickSelection: true }"
        :animateRows="true"
        :loading="gridData.loading.value"
        :rowHeight="40"
        overlayNoRowsTemplate="No assets found"
        overlayLoadingTemplate="Loading assets…"
        @grid-ready="onGridReady"
        @sort-changed="handleSortChanged"
        @cell-value-changed="handleCellValueChanged"
      />

      <!-- Pagination Controls -->
      <AssetGridPagination
        :page="pagination.page.value"
        :pageSize="pagination.pageSize.value"
        v-model:pageSizeSelection="pagination.pageSizeSelection.value"
        :viewAll="pagination.viewAll.value"
        :totalCount="pagination.totalCount.value"
        :totalPages="pagination.totalPages.value"
        :loading="gridData.loading.value"
        :canGoToPrev="pagination.canGoToPrevPage.value"
        :canGoToNext="pagination.canGoToNextPage.value"
        @pageSizeChange="handlePageSizeChange"
        @prevPage="handlePrevPage"
        @nextPage="handleNextPage"
      />

      <!-- Asset Detail Modal -->
      <BModal
        v-model="modals.showAssetModal.value"
        size="xl"
        body-class="p-0 bg-body text-body"
        dialog-class="product-details-dialog"
        content-class="product-details-content bg-body text-body"
        hide-footer
        @shown="onModalShown"
        @hidden="onModalHidden"
      >
        <template #header>
          <div class="d-flex align-items-center w-100">
            <h5 class="modal-title mb-0" v-if="modals.headerReady.value">
              <div class="lh-sm d-flex align-items-center">
                <span class="fw-bold text-dark">{{ modals.modalIdText.value }}</span>
                <template v-if="modals.modalTradeText.value">
                  <span class="text-dark mx-2">|</span>
                  <span class="fw-bold text-dark">{{ modals.modalTradeText.value }}</span>
                </template>
              </div>
              <div class="text-muted lh-sm">
                <span class="fw-bold text-dark">{{ modals.modalAddrText.value }}</span>
              </div>
            </h5>
            <h5 class="modal-title mb-0" v-else>
              <div class="lh-sm">&nbsp;</div>
              <div class="text-muted lh-sm">&nbsp;</div>
            </h5>
            <div class="ms-auto">
              <button
                type="button"
                class="btn btn-sm btn-primary"
                @click="modals.openFullPage"
                title="Open full page (Ctrl + Enter)"
              >
                ⤢ Full Page
              </button>
            </div>
          </div>
        </template>
        <LoanLevelIndex
          :assetHubId="modals.selectedId.value"
          :row="modals.selectedRow.value"
          :address="modals.selectedAddr.value"
          :standalone="false"
          @row-loaded="modals.onLoanRowLoaded"
        />
      </BModal>

      <!-- Add to Custom List Modal -->
      <BModal
        v-model="modals.showAddToListModal.value"
        title="Add Assets to Custom List"
        size="lg"
        dialog-class="modal-dialog-centered"
        @hidden="modals.resetAddToListModal"
      >
        <div class="d-flex flex-column gap-3">
          <div class="alert alert-light border mb-0">
            <strong>{{ modals.selectedListAssetIds.value.length }}</strong> asset(s) selected
          </div>
          <div>
            <label class="form-label">List Name</label>
            <input
              v-model="modals.newListName.value"
              type="text"
              class="form-control"
              placeholder="e.g., Q1 DIL Review"
            />
          </div>
          <div>
            <label class="form-label">Description (optional)</label>
            <textarea
              v-model="modals.newListDescription.value"
              class="form-control"
              rows="3"
              placeholder="Add a short description..."
            ></textarea>
          </div>
        </div>
        <template #footer>
          <div class="d-flex align-items-center gap-2 ms-auto">
            <button type="button" class="btn btn-light" @click="modals.showAddToListModal.value = false">
              Cancel
            </button>
            <button
              type="button"
              class="btn btn-primary"
              :disabled="!modals.canSaveCustomList.value || modals.isSavingCustomList.value"
              @click="handleSaveCustomList"
            >
              <span v-if="modals.isSavingCustomList.value" class="spinner-border spinner-border-sm me-1"></span>
              {{ modals.isSavingCustomList.value ? 'Saving...' : 'Create List' }}
            </button>
          </div>
        </template>
      </BModal>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { AgGridVue } from 'ag-grid-vue3'
import { themeQuartz } from 'ag-grid-community'
import type { GridReadyEvent, ColDef } from 'ag-grid-community'
import { BModal } from 'bootstrap-vue-next'
import LoanLevelIndex from '@/views/am_module/loanlvl_index.vue'
import ActionsCell from '@/views/acq_module/acq_dash/components/ActionsCell.vue'

// Components
import AssetGridToolbar from './components/AssetGridToolbar.vue'
import AssetGridPagination from './components/AssetGridPagination.vue'

// Composables
import { useAssetFilters } from './composables/useAssetFilters'
import { useAssetPagination } from './composables/useAssetPagination'
import { useAssetGridData } from './composables/useAssetGridData'
import { useFullWindowMode } from './composables/useFullWindowMode'
import { useAssetModals } from './composables/useAssetModals'

// Column configuration
import { buildColumnDefs, getFixedWidthColumns } from './config/assetGridColumns'

// Props
const props = defineProps<{
  filterTradeName?: string
  filterSellerName?: string
  filterActiveOnly?: boolean
}>()

// Router
const router = useRouter()
const route = router.currentRoute

// Composables
const filters = useAssetFilters()
const pagination = useAssetPagination()
const gridData = useAssetGridData()
const { isFullWindow, toggleFullWindow } = useFullWindowMode()
const modals = useAssetModals()

// Grid refs
const gridRef = ref<any>(null)
const cardRef = ref<HTMLElement | null>(null)

// Active view
const activeView = ref<'snapshot' | 'performance' | 'valuation' | 'servicing' | 'all'>('snapshot')

// Actions column configuration
const actionsColumn: ColDef = {
  headerName: 'Actions',
  colId: 'actions',
  pinned: 'left',
  width: 140,
  minWidth: 130,
  lockPosition: true,
  suppressMovable: true,
  sortable: false,
  filter: false,
  suppressHeaderContextMenu: true,
  cellRenderer: ActionsCell as any,
  cellRendererParams: {
    onAction: handleRowAction,
    actions: [
      {
        key: 'view',
        title: 'View Asset',
        iconClass: 'mdi-eye',
        variantClass: 'btn-outline-primary',
      },
      {
        key: 'add_to_list',
        title: 'Add to Custom List',
        iconClass: 'mdi-playlist-plus',
        variantClass: 'btn-outline-secondary',
      },
    ],
  },
}

// Column definitions (built from centralized config)
const columnDefs = ref<ColDef[]>(buildColumnDefs(activeView.value, actionsColumn))

// Default column settings
const defaultColDef: ColDef = {
  resizable: true,
  filter: true,
  wrapHeaderText: true,
  autoHeaderHeight: true,
  minWidth: 90, // WHAT: Reduce minimum width to fit more columns
  maxWidth: 200, // WHAT: Cap default width so auto-size doesn't over-expand
  headerClass: 'text-center',
  cellClass: 'text-center',
  floatingFilter: false,
  menuTabs: ['filterMenuTab'],
}

// Grid style (responsive to full window mode)
const gridStyle = computed(() =>
  isFullWindow.value
    ? { width: '100%', height: '100%' }
    : { width: '100%', height: '700px' }
)

// Debounced quick filter watcher
let qTimer: any = null
watch(filters.quickFilter, () => {
  if (qTimer) clearTimeout(qTimer)
  qTimer = setTimeout(() => fetchData(), 300)
})

// Watch active smart filter changes
watch(filters.activeSmartFilter, () => {
  filters.applySmartFilter(gridData.gridApi.value)
})

// Grid event handlers
function onGridReady(e: GridReadyEvent): void {
  gridData.gridApi.value = e.api

  // Sync page size on mount
  pagination.syncPageSize()

  // Refresh header
  gridData.gridApi.value?.refreshHeader?.()

  // Load filter options
  loadFilterOptions()

  // Initial data fetch
  fetchData()
}

function handleSortChanged(): void {
  gridData.onSortChanged()
  nextTick(() => fetchData())
}

function handleCellValueChanged(params: any): void {
  handleAssetMasterStatusChange(params)
}

// Handle inline editing of asset master status
async function handleAssetMasterStatusChange(params: any): Promise<void> {
  const row = params.data
  const newValue = params.newValue
  const oldValue = params.oldValue

  if (newValue === oldValue) return

  const assetId = modals.getAssetHubIdFromRow(row)
  if (!assetId) {
    console.error('[AssetGrid] Cannot update: missing asset ID')
    return
  }

  const result = await gridData.updateAssetMasterStatus({
    assetId,
    newValue,
    oldValue,
  })

  if (result.success && result.data) {
    // Update row with fresh data
    const api = gridData.gridApi.value
    if (api) {
      const rowNode = api.getRowNode(String(assetId))
      if (rowNode) {
        rowNode.setData(result.data)
      }
    }
  } else {
    // Revert on error
    const api = gridData.gridApi.value
    if (api) {
      const rowNode = api.getRowNode(String(assetId))
      if (rowNode) {
        rowNode.setDataValue('asset_master_status', oldValue)
      }
    }
  }
}

// Actions handler
function handleRowAction(action: string, row: any): void {
  if (action === 'view') {
    modals.openAssetModal(row)
    return
  }

  if (action === 'add_to_list') {
    const selectedRows = getSelectedAssetRows()
    modals.openAddToListModal({ clickedRow: row, selectedRows })
    return
  }

  console.log(`[AssetGrid] action="${action}"`, row)
}

function getSelectedAssetRows(): any[] {
  const api = gridData.gridApi.value
  if (!api || typeof api.getSelectedRows !== 'function') return []
  return api.getSelectedRows() || []
}

// Filter handlers
function handleFilterChange(): void {
  pagination.resetToFirstPage()
  fetchData()
}

function handleClearFilters(): void {
  filters.clearAllFilters()
  pagination.resetToFirstPage()
  fetchData()
}

// View change handler
function handleViewChange(): void {
  columnDefs.value = buildColumnDefs(activeView.value, actionsColumn)

  nextTick(() => {
    const api = gridData.gridApi.value as any
    api?.resetColumnState?.()
    api?.refreshHeader?.()
    gridData.onSortChanged()
    updateGridSize()
  })
}

// Pagination handlers
function handlePageSizeChange(): void {
  const result = pagination.handlePageSizeChange()
  if (result.shouldFetchAll) {
    fetchAllData()
  } else {
    fetchData()
  }
}

function handlePrevPage(): void {
  if (pagination.prevPage()) {
    fetchData()
  }
}

function handleNextPage(): void {
  if (pagination.nextPage()) {
    fetchData()
  }
}

// Data fetching
async function fetchData(): Promise<void> {
  const result = await gridData.fetchRows({
    page: pagination.page.value,
    pageSize: pagination.pageSize.value,
    quickFilter: filters.quickFilter.value,
    sortExpr: gridData.sortExpr.value,
    filterParams: filters.buildFilterParams(),
    props: {
      filterTradeName: props.filterTradeName,
      filterSellerName: props.filterSellerName,
      filterActiveOnly: props.filterActiveOnly,
    },
    routeQuery: route.value.query,
  })

  if (result.success && result.data) {
    pagination.updateFromResponse(result.data)
  } else {
    pagination.resetPagination()
  }

  nextTick(() => updateGridSize())
}

async function fetchAllData(): Promise<void> {
  const result = await gridData.fetchAllRows({
    quickFilter: filters.quickFilter.value,
    sortExpr: gridData.sortExpr.value,
    props: {
      filterTradeName: props.filterTradeName,
      filterSellerName: props.filterSellerName,
      filterActiveOnly: props.filterActiveOnly,
    },
    routeQuery: route.value.query,
  })

  pagination.totalCount.value = result.totalCount
  pagination.totalPages.value = 1

  nextTick(() => updateGridSize())
}

async function loadFilterOptions(): Promise<void> {
  const options = await gridData.fetchFilterOptions()
  filters.setFilterOptions(options)
}

// Grid sizing
function updateGridSize(): void {
  nextTick(() => {
    setTimeout(() => {
      try {
        const api = gridData.gridApi.value as any
        if (!api) return

        const fixedWidthColumns = getFixedWidthColumns()
        const allColumns = api.getColumns?.() || []
        const columnsToAutosize = allColumns
          .filter((col: any) => !fixedWidthColumns.includes(col.getColId()))
          .map((col: any) => col.getColId())

        if (columnsToAutosize.length > 0) {
          api.autoSizeColumns?.(columnsToAutosize) ||
            api.columnApi?.autoSizeColumns?.(columnsToAutosize)
        }
      } catch {}
    }, 50)
  })
}

// Modal handlers
function onModalShown(): void {
  document.addEventListener('keydown', onKeydown as any)
}

function onModalHidden(): void {
  document.removeEventListener('keydown', onKeydown as any)
  const { shouldRefresh } = modals.closeAssetModal()
  if (shouldRefresh) {
    fetchData()
  }
}

function onKeydown(e: KeyboardEvent): void {
  if (e.ctrlKey && (e.key === 'Enter' || e.code === 'Enter')) {
    e.preventDefault()
    modals.openFullPage()
  }
}

async function handleSaveCustomList(): Promise<void> {
  await modals.saveCustomList()
}

// Close dropdowns on outside click
onMounted(() => {
  const handleClickOutside = (event: MouseEvent) => {
    const target = event.target as HTMLElement
    if (!target.closest('.dropdown')) {
      filters.closeAllDropdowns()
    }
  }
  document.addEventListener('click', handleClickOutside)
  onUnmounted(() => {
    document.removeEventListener('click', handleClickOutside)
  })
})

// Expose modal opener for parent components
defineExpose({
  openAssetModalFromMarker: modals.openAssetModalFromMarker,
})
</script>

<style scoped>
.fullwindow-card {
  position: fixed;
  inset: 0;
  z-index: 1050;
  border-radius: 0 !important;
  display: flex;
  flex-direction: column;
}

.fullwindow-card > .card-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.fullwindow-card :deep(.asset-grid) {
  flex: 1;
  height: 100% !important;
}

:deep(.asset-grid .ag-header-cell-label) {
  justify-content: center;
  font-size: 12px; /* WHAT: Smaller header text to fit more columns */
}

:deep(.asset-grid .ag-cell) {
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  font-size: 12px; /* WHAT: Smaller cell text to fit more rows/columns */
}

:deep(.asset-grid .ag-header-select-all),
:deep(.asset-grid .ag-selection-checkbox) {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  padding: 0;
}

:deep(.asset-grid .ag-header-select-all .ag-checkbox-input-wrapper) {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  padding: 0;
  transform: translateX(-4px);
}

:deep(.asset-grid .ag-selection-checkbox .ag-checkbox-input-wrapper) {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  padding: 0;
}

/* WHAT: Reduce action button size for tighter rows */
/* WHY: Smaller buttons fit better with reduced row height */
/* HOW: Override button padding and icon size inside action cells */
:deep(.asset-grid .actions-cell .btn-group .btn) {
  padding: 0.15rem 0.35rem; /* WHAT: Slightly larger than tightest size for usability */
  font-size: 0.7rem;
}

:deep(.asset-grid .actions-cell .btn-group .btn .mdi) {
  font-size: 0.9rem;
  line-height: 1;
}

</style>
