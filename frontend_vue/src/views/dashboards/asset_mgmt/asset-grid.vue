<template>
  <!--
    AssetGrid.vue
    Purpose: Reusable AG Grid card for the Asset Management module.
    Visuals: Matches acquisitions grid (card header, Quartz theme, spacing).
  -->
  <div class="card" ref="cardRef" :class="{ 'fullscreen-card': isFullscreen }">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Asset Inventory</h4>
      <div class="d-flex align-items-center gap-2">
        <!-- Fullscreen toggle to mirror acquisitions experience -->
        <button
          class="btn btn-sm btn-light"
          type="button"
          :title="isFullscreen ? 'Exit Full Page' : 'Full Page'"
          :aria-pressed="isFullscreen ? 'true' : 'false'"
          aria-label="Toggle full page view"
          @click="toggleFullscreen"
        >
          <i class="mdi" :class="isFullscreen ? 'mdi-fullscreen-exit' : 'mdi-fullscreen'"></i>
        </button>
      </div>
    </div>

    <div class="card-body pt-0">
      <!-- Controls row placed directly under header, aligned left -->
      <div class="d-flex justify-content-between flex-wrap gap-2 mb-2">
        <!-- Quick Filter on the left -->
        <div class="input-group input-group-sm" style="width: 260px; max-width: 100%;">
          <span class="input-group-text"><i class="mdi mdi-magnify"></i></span>
          <input
            v-model="quickFilter"
            type="text"
            class="form-control"
            placeholder="Quick filter..."
            aria-label="Quick filter"
          />
          <button
            v-if="quickFilter"
            class="btn btn-light"
            type="button"
            title="Clear"
            @click="quickFilter = ''"
          >
            <i class="mdi mdi-close"></i>
          </button>
        </div>

        <!-- View dropdown on the right -->
        <div class="d-flex align-items-center gap-2">
          <label for="viewSelect" class="small mb-0">View</label>
          <select id="viewSelect" class="form-select form-select-sm" v-model="activeView" @change="applyView">
            <option value="overview">Overview</option>
            <option value="financials">Financials</option>
            <option value="timeline">Timeline</option>
            <option value="all">All</option>
          </select>
        </div>
      </div>
      <!-- AG Grid with Quartz theme and consistent height -->
      <ag-grid-vue
        ref="gridRef"
        class="asset-grid"
        :style="gridStyle"
        :theme="themeQuartz"
        :rowData="rowData"
        :columnDefs="columnDefs"
        :defaultColDef="defaultColDef"
        :quickFilterText="quickFilter"
        :rowSelection="{ mode: 'multiRow', checkboxes: false, headerCheckbox: false, enableClickSelection: true }"
        :animateRows="true"
        overlayNoRowsTemplate="No assets found"
        @grid-ready="onGridReady"
        @sort-changed="onSortChanged"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
// AG Grid Vue 3 wrapper and Quartz theme (matches acquisitions)
import { AgGridVue } from 'ag-grid-vue3'
import { themeQuartz } from 'ag-grid-community'
import type { GridApi, GridReadyEvent, ColDef, ValueFormatterParams } from 'ag-grid-community'
import { ref, computed, nextTick, watch } from 'vue'
import http from '@/lib/http'

// Constant columns (always shown, pinned left first)
const constantColumns: ColDef[] = [
  {
    headerName: 'Actions',
    colId: 'actions',
    pinned: 'left',
    width: 160,
    lockPosition: true,
    suppressMovable: true,
    sortable: false,
    filter: false,
    cellRenderer: (p: any) => {
      const root = document.createElement('div')
      root.className = 'd-flex align-items-center gap-1'
      root.innerHTML = `
        <input type="checkbox" class="form-check-input" aria-label="Select row" />
        <button type="button" class="btn btn-xs btn-outline-primary">View</button>
        <button type="button" class="btn btn-xs btn-outline-secondary">Edit</button>
      `
      const [checkbox, viewBtn, editBtn] = [
        root.querySelector('input.form-check-input'),
        root.querySelector('button.btn-outline-primary'),
        root.querySelector('button.btn-outline-secondary'),
      ] as any
      viewBtn?.addEventListener('click', (e: Event) => {
        e.stopPropagation()
        console.debug('[Actions] View clicked', p.data)
      })
      editBtn?.addEventListener('click', (e: Event) => {
        e.stopPropagation()
        console.debug('[Actions] Edit clicked', p.data)
      })
      checkbox?.addEventListener('click', (e: Event) => e.stopPropagation())
      return root
    },
  },
  { headerName: 'Asset ID', field: 'asset_id', minWidth: 120, pinned: 'left' },
  { headerName: 'Status', field: 'asset_status', minWidth: 120, pinned: 'left' },
  {
    headerName: 'Property Address',
    colId: 'address',
    minWidth: 260,
    wrapHeaderText: true,
    autoHeaderHeight: true,
    cellClass: 'text-start',
    pinned: 'left',
    valueGetter: (p: any) => {
      const s = (p.data?.street_address || '').toString().trim()
      const c = (p.data?.city || '').toString().trim()
      const st = (p.data?.state || '').toString().trim()
      return [s, c, st].filter(Boolean).join(', ')
    },
  },
]

// Additional columns (vary by view)
const allExtraColumns: ColDef[] = [
  // ZIP intentionally omitted per latest serializer change
  { headerName: 'Type', field: 'property_type', minWidth: 140 },
  { headerName: 'Occupancy', field: 'occupancy', minWidth: 130 },
  { headerName: 'Trade', field: 'trade_name', minWidth: 160, cellClass: 'text-start' },
  { headerName: 'ARV (Seller)', field: 'seller_arv_value', valueFormatter: currencyFormatter, minWidth: 140 },
  { headerName: 'As-Is (Seller)', field: 'seller_asis_value', valueFormatter: currencyFormatter, minWidth: 140 },
  { headerName: 'Acq Cost', field: 'acq_cost', valueFormatter: currencyFormatter, minWidth: 130 },
  { headerName: 'Total Expenses', field: 'total_expenses', valueFormatter: currencyFormatter, minWidth: 150 },
  { headerName: 'Total Hold (days)', field: 'total_hold', minWidth: 150 },
  { headerName: 'Exit Date', field: 'exit_date', valueFormatter: dateFormatter, minWidth: 140 },
  { headerName: 'Gross Proceeds', field: 'expected_gross_proceeds', valueFormatter: currencyFormatter, minWidth: 150 },
  { headerName: 'Net Proceeds', field: 'expected_net_proceeds', valueFormatter: currencyFormatter, minWidth: 150 },
  { headerName: 'Expected P/L', field: 'expected_pl', valueFormatter: currencyFormatter, minWidth: 140 },
  { headerName: 'Expected CF', field: 'expected_cf', valueFormatter: currencyFormatter, minWidth: 140 },
  { headerName: 'IRR %', field: 'expected_irr', valueFormatter: percentFormatter, minWidth: 110 },
  { headerName: 'MOIC', field: 'expected_moic', valueFormatter: moicFormatter, minWidth: 110 },
  { headerName: 'NPV', field: 'expected_npv', valueFormatter: currencyFormatter, minWidth: 140 },
]

const presets: Record<string, ColDef[]> = {
  overview: [
    allExtraColumns[0], // Type
    allExtraColumns[1], // Occupancy
    allExtraColumns[2], // Trade
  ],
  financials: [
    allExtraColumns[3], // ARV
    allExtraColumns[4], // As-Is
    allExtraColumns[5], // Acq Cost
    allExtraColumns[6], // Total Expenses
    allExtraColumns[10], // Expected P/L
    allExtraColumns[11], // Expected CF
    allExtraColumns[12], // IRR
    allExtraColumns[13], // MOIC
    allExtraColumns[14], // NPV
  ],
  timeline: [
    allExtraColumns[7], // Total Hold
    allExtraColumns[8], // Exit Date
  ],
  all: allExtraColumns,
}

const activeView = ref<'overview' | 'financials' | 'timeline' | 'all'>('overview')
const columnDefs = ref<ColDef[]>([...constantColumns, ...presets[activeView.value]])

function applyView() {
  columnDefs.value = [...constantColumns, ...presets[activeView.value]]

  // Re-apply sort because visible columns changed
  nextTick(() => onSortChanged())
}

// Default column behavior
const defaultColDef: ColDef = {
  resizable: true,
  filter: true,
  wrapHeaderText: true,
  autoHeaderHeight: true,
  // Center-align headers and cell content for consistent presentation
  headerClass: 'text-center',
  cellClass: 'text-center',
  floatingFilter: false,
  menuTabs: ['filterMenuTab'],
  minWidth: 120,
}

// Live data from API
const rowData = ref<any[]>([])
const loading = ref<boolean>(false)
const page = ref<number>(1)
const pageSize = ref<number>(50)
const sortExpr = ref<string>('')

// Quick filter state bound to the grid's quickFilterText option
const quickFilter = ref<string>('')

// Number formatting helpers (consistent with acquisitions)
function currencyFormatter(params: ValueFormatterParams): string {
  const v = params.value
  const num = typeof v === 'number' ? v : parseFloat(String(v))
  if (Number.isNaN(num)) return v == null ? '' : String(v)
  return new Intl.NumberFormat(undefined, { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(num)
}

function dateFormatter(params: ValueFormatterParams): string {
  const v = params.value
  if (!v) return ''
  const d = new Date(String(v))
  if (isNaN(d.getTime())) return String(v)
  return new Intl.DateTimeFormat('en-US', { year: 'numeric', month: '2-digit', day: '2-digit' }).format(d)
}

function percentFormatter(params: ValueFormatterParams): string {
  const v = params.value
  if (v == null || v === '') return ''
  const num = typeof v === 'number' ? v : parseFloat(String(v))
  if (Number.isNaN(num)) return String(v)
  return `${num.toFixed(2)}%`
}

function moicFormatter(params: ValueFormatterParams): string {
  const v = params.value
  if (v == null || v === '') return ''
  const num = typeof v === 'number' ? v : parseFloat(String(v))
  if (Number.isNaN(num)) return String(v)
  return num.toFixed(2)
}

// Grid instance refs
const gridRef = ref<any>(null)
const gridApi = ref<GridApi | null>(null)

// Fullscreen state for the card
const cardRef = ref<HTMLElement | null>(null)
const isFullscreen = ref<boolean>(false)

// Grid area size
const gridStyle = computed(() => (
  isFullscreen.value
    ? { width: '100%', height: '100%' }
    : { width: '100%', height: '420px' }
))

function updateGridSize(): void {
  nextTick(() => {
    try {
      const api = gridApi.value as any
      if (!api) return
      // In fullscreen, autosize to content; allow horizontal scroll otherwise
      if (isFullscreen.value || document.fullscreenElement) {
        api.autoSizeAllColumns?.() || api.columnApi?.autoSizeAllColumns?.()
      } else {
        // Do not call sizeColumnsToFit so columns can exceed width and enable horizontal scroll
      }
    } catch {}
  })
}

function onGridReady(e: GridReadyEvent) {
  gridApi.value = e.api
  updateGridSize()
  fetchRows()
}

async function enterFullscreen(): Promise<void> {
  const el = cardRef.value as any
  try {
    if (el?.requestFullscreen) await el.requestFullscreen()
    else isFullscreen.value = true
  } finally {
    updateGridSize()
  }
}

async function exitFullscreen(): Promise<void> {
  try {
    if (document.fullscreenElement) await document.exitFullscreen()
    else isFullscreen.value = false
  } finally {
    isFullscreen.value = false
    updateGridSize()
  }
}

function toggleFullscreen(): void {
  if (isFullscreen.value || document.fullscreenElement) exitFullscreen()
  else enterFullscreen()
}

// Fetch rows from backend with q and sort
async function fetchRows(): Promise<void> {
  loading.value = true
  try {
    const params: Record<string, any> = {
      page: page.value,
      page_size: pageSize.value,
    }
    if (quickFilter.value) params.q = quickFilter.value
    if (sortExpr.value) params.sort = sortExpr.value
    const { data } = await http.get('/am/assets/', { params })
    rowData.value = Array.isArray(data?.results) ? data.results : []
    console.debug('[AssetGrid] loaded rows:', rowData.value.length)
  } catch (e) {
    console.debug('[AssetGrid] fetch failed', e)
    rowData.value = []
  } finally {
    loading.value = false
    nextTick(() => updateGridSize())
  }
}

// Debounce quick filter API calls
let qTimer: any = null
watch(quickFilter, () => {
  if (qTimer) clearTimeout(qTimer)
  qTimer = setTimeout(() => fetchRows(), 300)
})

// Capture sort changes and build sort expression (supports multi-col)
function onSortChanged(): void {
  const api: any = gridApi.value
  if (!api) return
  const sortModels = api.getColumnState?.().filter((c: any) => c.sort)
  if (!sortModels || sortModels.length === 0) {
    sortExpr.value = ''
    fetchRows()
    return
  }
  // Exclude derived 'address' from server-side sorting; let grid sort client-side for it
  const serverSorts = sortModels
    .filter((c: any) => c.colId !== 'address')
    .map((c: any) => (c.sort === 'desc' ? `-${c.colId}` : c.colId))
  sortExpr.value = serverSorts.join(',')
  if (serverSorts.length > 0) {
    fetchRows()
  }
}
</script>

<style scoped>
.fullscreen-card {
  position: fixed;
  inset: 0;
  z-index: 1050; /* above app chrome */
  border-radius: 0 !important;
}

/* Center AG Grid header text and cell contents (Quartz theme uses flex wrappers) */
:deep(.asset-grid .ag-header-cell-label) {
  justify-content: center;
}

:deep(.asset-grid .ag-cell) {
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
}
</style>
