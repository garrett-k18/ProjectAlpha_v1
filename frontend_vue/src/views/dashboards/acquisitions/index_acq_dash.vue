<template>
  <Layout>
    <b-row>
      <b-col class="col-12">
        <div class="page-title-box">
          <div class="page-title-right">
            <!-- Removed refresh button/form -->
          </div>
          <h4 class="page-title">Acquisition Module</h4>
        </div>
      </b-col>
    </b-row>

   

    <!-- Prominent, centered selectors: MUST choose before page functions -->
    <b-row class="mb-0">
      <b-col class="col-12">
        <div class="card">
          <!-- Slightly increased bottom whitespace for breathing room (pb-2) -->
          <div class="card-body pt-1 pb-2 px-2">
            <!-- Centered selectors with Trade Settings button -->
            <div class="d-flex flex-wrap align-items-end justify-content-center gap-2 w-100 mb-2">
              <!-- Title inline on the left of the dropdowns -->
              <div class="fw-bold fs-6 me-2 fst-italic">Select Seller and Trade</div>

              <!-- Seller select -->
              <div class="d-flex flex-column align-items-center">
                <label class="form-label fw-bold text-center w-100 fs-5 mb-1" for="topSellerSelect">Seller</label>
                <select
                  id="topSellerSelect"
                  class="form-select form-select-sm text-center"
                  style="width: 250px; min-width: 250px; max-width: 250px;"
                  v-model="selectedSellerId"
                  :disabled="sellersLoading"
                >
                  <option :value="null">Select a seller</option>
                  <option v-for="s in sellers" :key="s.id" :value="s.id">{{ s.name }}</option>
                </select>
              </div>

              <!-- Trade select -->
              <div class="d-flex flex-column align-items-center">
                <label class="form-label fw-bold text-center w-100 fs-5 mb-1" for="topTradeSelect">Trade</label>
                <select
                  id="topTradeSelect"
                  class="form-select form-select-sm text-center"
                  style="width: 250px; min-width: 250px; max-width: 250px;"
                  :key="String(selectedSellerId ?? 'null')"
                  v-model="selectedTradeId"
                  :disabled="!selectedSellerId || tradesLoading"
                >
                  <option :value="null">Select a trade</option>
                  <option v-for="t in trades" :key="t.id" :value="t.id">{{ t.trade_name }}</option>
                </select>
              </div>

              <!-- Reset button -->
              <div class="d-flex align-items-end" v-if="selectedSellerId || selectedTradeId">
                <button class="btn btn-sm btn-secondary mb-0" @click="resetSelections">
                  <i class="mdi mdi-refresh me-1"></i> Reset
                </button>
              </div>
              <!-- Import Seller Tape - Always visible -->
              <div class="d-flex align-items-end">
                <button 
                  class="btn btn-sm btn-success mb-0" 
                  @click="showImportModal = true"
                  title="Import Seller Tape"
                  aria-label="Import Seller Tape"
                >
                  <i class="mdi mdi-upload"></i>
                </button>
              </div>
              
            </div>

            <!-- Helper text below toolbar -->
            <div class="form-text text-center mt-0">
              <span v-if="sellersLoading">Loading sellers…</span>
              <span v-else-if="selectedSellerId && tradesLoading">Loading trades…</span>
              <span v-else-if="selectedSellerId && !selectedTradeId">Select a trade to view data.</span>
              <span v-else-if="!selectedSellerId">Select a seller to begin.</span>
            </div>
          </div>
        </div>
      </b-col>
    </b-row>


    <!-- Top metrics widgets rendered directly to minimize vertical padding -->
    <div class="mb-0">
      <Widgets />
    </div>

    <!-- Trade control action dock paired with tasking tracker so stakeholders evaluate workflow coverage together -->
    <b-row class="g-2 mt-1 mb-2">
      <b-col xl="6" lg="12">
        <TradeActionDock
          :seller-name="selectedSellerLabel"
          :trade-name="selectedTradeLabel"
          :has-active-trade="Boolean(selectedTradeId)"
          :status-value="tradeStatusValue"
          :status-options="tradeStatusOptions"
          :saving-status="tradeStatusLoading"
          :on-update-status="handleTradeStatusUpdate"
          :on-refresh-status="handleTradeStatusRefresh"
          @trigger="handleOptionTrigger"
        />
      </b-col>
      <b-col xl="6" lg="12">
        <TradeTasking />
      </b-col>
    </b-row>
    
    
    <!-- Seller Data Tape card (AG Grid) moved directly under top metrics -->
    <b-row class="mt-3">
      <b-col class="col-12">
        <!-- Temporary: Use simplified AcqGrid for testing -->
        <!-- Wire AcqGrid's View action to open the loan modal in this page -->
        <AcqGrid @open-loan="onOpenLoan" />
      </b-col>
    </b-row>

    <b-row class="g-2 mt-2" v-if="gridRowsLoaded">
      <b-col class="col-12">
        <VectorMap />
      </b-col>
    </b-row>

    <!-- Stratification cards row: render all four in one row on xl screens -->
    <b-row class="g-2 mt-2" v-if="gridRowsLoaded">
      <b-col xl="3" lg="6" md="12">
        <StratsCurrentBal />
      </b-col>
      <b-col xl="3" lg="6" md="12">
        <StratsTotalDebt />
      </b-col>
      <b-col xl="3" lg="6" md="12">
        <StratsSellerAsIs />
      </b-col>
      <b-col xl="3" lg="6" md="12">
        <StratsWac />
      </b-col>
    </b-row>

    <!-- Other analytics cards (System removed) -->

    <!-- Property Type, Occupancy, Judicial, and Delinquency stratifications (categorical) -->
    <b-row class="g-2 mt-2" v-if="gridRowsLoaded">
      <b-col xl="3" lg="6" md="12">
        <StratsPropertyType />
      </b-col>
      <b-col xl="3" lg="6" md="12">
        <StratsOccupancy />
      </b-col>
      <!-- Moved Judicial vs Non-Judicial here to sit next to Occupancy -->
      <b-col xl="3" lg="6" md="12">
        <StratsJudVsNon />
      </b-col>
      <b-col xl="3" lg="6" md="12">
        <StratsDelinquency />
      </b-col>
    </b-row>

    

    

    
    <!-- Loan-Level Modal wrapper using BootstrapVue Next -->
    <!-- Docs: https://bootstrap-vue-next.github.io/bootstrap-vue-next/docs/components/modal -->
    <BModal
      v-model="showLoanModal"
      size="xl"
      body-class="p-0 bg-body text-body"
      dialog-class="product-details-dialog"
      content-class="product-details-content bg-body text-body"
      hide-footer
      @shown="onModalShown"
      @hidden="onModalHidden"
    >
      <!-- Custom header with action button (far right) -->
      <template #header>
        <div class="d-flex align-items-center w-100">
          <h5 class="modal-title mb-0">
            <div class="lh-sm"><span class="fw-bold">{{ modalIdText }}</span></div>
            <div class="text-muted lh-sm"><span class="fw-bold text-dark fs-4">{{ modalAddrText }}</span></div>
          </h5>
          <div class="ms-auto">
            <button
              type="button"
              class="btn btn-sm btn-primary"
              @click="openFullPage"
              title="Open full page (Ctrl + Enter)"
              aria-label="Open full page"
            >
              Full Page <span class="text-white-50">(Ctrl + Enter)</span>
            </button>
          </div>
        </div>
      </template>
      <!-- Render the centralized loan-level wrapper inside the modal -->
      <!-- 
        CRITICAL: v-if + :key force component re-creation when selectedId changes.
        Without this, Vue reuses the existing LoanLevelIndex instance (mounted with null props)
        instead of creating a fresh instance with the new assetId/row data.
        This was causing FC timeline and other features to fail in modals.
      -->
      <LoanLevelIndex
        v-if="selectedId"
        :key="`loan-${selectedId}`"
        :assetId="selectedId"
        :row="selectedRow"
        :address="selectedAddr"
        :standalone="false"
      />
    </BModal>
    
    <!-- Trade Assumptions Modal (centered) -->
    <BModal
      v-model="showTradeDetailsModal"
      title="Trade Assumptions"
      size="lg"
      centered
      hide-header-close
    >
      <div v-if="selectedTradeId">
        <TradeDetailsModal
          v-model:bidDate="bidDateModel"
          v-model:settlementDate="settlementDateModel"
          :disabled="dateFieldsLoading"
          @changed="autosaveDateChanges"
        />
      </div>
      <div v-else class="text-center py-4">Please select a trade to configure settings.</div>
      <template #footer>
        <div class="d-flex justify-content-end w-100 gap-2">
          <button class="btn btn-primary" @click="showTradeDetailsModal = false">Close</button>
        </div>
      </template>
    </BModal>

    <!-- Trade Documents Modal (large, with list + viewer) -->
    <BModal
      v-model="showTradeDocumentsModal"
      title="Trade Documents"
      size="xl"
      centered
    >
      <!-- Trade-specific document manager composed with shared components -->
      <TradeDocumentsModal
        :row="tradeDocumentContext"
        :tradeId="selectedTradeId ?? null"
      />
      <template #footer>
        <div class="d-flex justify-content-end w-100 gap-2">
          <button class="btn btn-primary" @click="showTradeDocumentsModal = false">Close</button>
        </div>
      </template>
    </BModal>

    <!-- Import Seller Tape Modal -->
    <BModal
      v-model="showImportModal"
      title="Import Seller Tape"
      size="lg"
      centered
      hide-footer
    >
      <ImportSellerTapeModal 
        @close="showImportModal = false" 
        @success="handleImportSuccess"
      />
    </BModal>
  </Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import StratsCurrentBal from "@/views/dashboards/acquisitions/strats/strats-current-bal.vue";
import StratsTotalDebt from "@/views/dashboards/acquisitions/strats/strats-total-debt.vue";
import StratsSellerAsIs from "@/views/dashboards/acquisitions/strats/strats-seller-asis.vue";
import StratsWac from "@/views/dashboards/acquisitions/strats/strats-wac.vue";
import StratsPropertyType from "@/views/dashboards/acquisitions/strats/strats-property-type.vue";
import StratsOccupancy from "@/views/dashboards/acquisitions/strats/strats-occupancy.vue";
import StratsJudVsNon from "@/views/dashboards/acquisitions/strats/strats-judvsnon.vue";
import StratsDelinquency from "@/views/dashboards/acquisitions/strats/strats-delinquency.vue";
import VectorMap from "@/views/dashboards/acquisitions/vectorMap.vue";
import Widgets from "@/views/dashboards/acquisitions/widgets.vue";
import TradeTasking from '@/views/dashboards/acquisitions/components/TradeTasking.vue';
// Local type for document items used by TradeDocumentsModal
// Exported to fix TypeScript module inference when this component is imported elsewhere
export interface DocumentItem { id: string; name: string; type: string; sizeBytes: number; previewUrl: string; downloadUrl: string }
// AG Grid: simplified testing grid for acquisitions dashboard
import AcqGrid from "@/views/dashboards/acquisitions/acq-grid.vue";
// BootstrapVue Next modal component (Vue 3 compatible)
import { BModal } from 'bootstrap-vue-next';
// Centralized loan-level wrapper used for both full-page and modal
import LoanLevelIndex from '@/views/acq_module/loanlvl/loanlvl_index.vue'
// Trade modals
import TradeDetailsModal from '@/views/dashboards/acquisitions/modals/TradeDetailsModal.vue'
import TradeDocumentsModal from '@/views/dashboards/acquisitions/modals/TradeDocumentsModal.vue'
import ImportSellerTapeModal from '@/views/dashboards/acquisitions/modals/ImportSellerTapeModal.vue'
// Trade control prototype Option 1 (Action Dock)
import TradeActionDock from '@/views/dashboards/acquisitions/components/TradeActionDock.vue';
// Trade control prototype Option 2 (Tabbed Control Center)
// Selections store + helpers
import { useAcqSelectionsStore } from '@/stores/acqSelections'
import { useAgGridRowsStore } from '@/stores/agGridRows'
import { useTradeAssumptionsStore } from '@/stores/tradeAssumptions'
import { storeToRefs } from 'pinia'
import { ref, watch, onMounted, computed } from 'vue'
// Centralized Axios instance (baseURL='/api')
import http from '@/lib/http'

// Types for dropdown options (module-scope to satisfy TS export typing)
export interface SellerOption { id: number; name: string }
export interface TradeOption { id: number; trade_name: string }

export default {
  components: {
    VectorMap,
    StratsJudVsNon,
    StratsCurrentBal,
    StratsTotalDebt,
    StratsSellerAsIs,
    StratsWac,
    StratsPropertyType,
    StratsOccupancy,
    StratsDelinquency,
    Widgets,
    TradeTasking,
    // Register simplified AG Grid component for testing
    AcqGrid,
    Layout,
    // Register modal + loan-level wrapper
    BModal,
    LoanLevelIndex,
    TradeDetailsModal,
    TradeDocumentsModal,
    ImportSellerTapeModal,
    TradeActionDock,
  },
  setup() {
    // Local lists for options
    const sellers = ref<SellerOption[]>([])
    const trades = ref<TradeOption[]>([])
    const sellersLoading = ref<boolean>(false)
    const tradesLoading = ref<boolean>(false)
    
    // Trade dates form state
    const bidDateModel = ref<string>('')
    const settlementDateModel = ref<string>('')
    const originalBidDate = ref<string>('')
    const originalSettlementDate = ref<string>('')
    const dateFieldsLoading = ref<boolean>(false)
    
    // Track if there are unsaved date changes
    const hasDateChanges = computed(() => {
      return bidDateModel.value !== originalBidDate.value || 
             settlementDateModel.value !== originalSettlementDate.value
    })

    // Shared selection state via Pinia stores
    const acqStore = useAcqSelectionsStore()
    const tradeAssumptionsStore = useTradeAssumptionsStore()
    const { tradeStatusValue, tradeStatusOptions, tradeStatusLoading } = storeToRefs(acqStore)
    // Use computed accessors that delegate to store actions to avoid
    // duplicating reset logic across components
    const selectedSellerId = computed<number | null>({
      // Unwrap Pinia ref if necessary so v-model gets a primitive value
      get: () => {
        const v: any = (acqStore as any).selectedSellerId
        return typeof v?.value !== 'undefined' ? (v.value as number | null) : (v as number | null)
      },
      set: (val) => acqStore.setSeller(val as number | null),
    })
    const selectedTradeId = computed<number | null>({
      get: () => {
        const v: any = (acqStore as any).selectedTradeId
        return typeof v?.value !== 'undefined' ? (v.value as number | null) : (v as number | null)
      },
      set: (val) => acqStore.setTrade(val as number | null),
    })

    // Grid rows store; used to know when primary dataset has loaded to gate heavy widgets
    const gridRowsStore = useAgGridRowsStore()
    const { rows: gridRows, loadingRows: gridLoadingRows, lastKey: gridLastKey } = storeToRefs(gridRowsStore)
    
    // Modal state
    const showTradeDetailsModal = ref<boolean>(false)
    const showTradeDocumentsModal = ref<boolean>(false)
    const showImportModal = ref<boolean>(false) // Controls visibility of the import seller tape modal

    // selectedSellerLabel resolves the human-readable seller name for the trade control prototypes
    const selectedSellerLabel = computed<string>(() => {
      const match = sellers.value.find((s) => s.id === (selectedSellerId.value ?? -1)) // Look up seller in current list
      return match ? match.name : 'No seller selected' // Return seller name or fallback placeholder
    })

    // selectedTradeLabel resolves the human-readable trade name for the trade control prototypes
    const selectedTradeLabel = computed<string>(() => {
      const match = trades.value.find((t) => t.id === (selectedTradeId.value ?? -1)) // Look up trade in current list
      return match ? match.trade_name : 'No trade selected' // Return trade name or fallback placeholder
    })

    // Context payload forwarded into TradeDocumentsModal for shared document components
    const tradeDocumentContext = computed(() => {
      const seller = sellers.value.find((s) => s.id === (selectedSellerId.value ?? -1)) || null
      const trade = trades.value.find((t) => t.id === (selectedTradeId.value ?? -1)) || null
      if (!seller && !trade) {
        return {
          seller: null,
          trade: null,
          sellerId: null,
          tradeId: null,
        }
      }
      return {
        seller,
        trade,
        sellerId: seller?.id ?? null,
        tradeId: trade?.id ?? null,
      }
    })

    // Update local date models from store
    function updateLocalDateModels() {
      const assumptions = tradeAssumptionsStore.assumptions
      if (assumptions) {
        // Format date strings to YYYY-MM-DD for input[type="date"]
        bidDateModel.value = assumptions.bid_date ? assumptions.bid_date.substring(0, 10) : ''
        settlementDateModel.value = assumptions.settlement_date ? assumptions.settlement_date.substring(0, 10) : ''
        
        // Store original values to detect changes
        originalBidDate.value = bidDateModel.value
        originalSettlementDate.value = settlementDateModel.value
      } else {
        resetLocalDateModels()
      }
    }
    
    // Reset local date models
    function resetLocalDateModels() {
      bidDateModel.value = ''
      settlementDateModel.value = ''
      originalBidDate.value = ''
      originalSettlementDate.value = ''
    }
    
    // Handlers for date input changes
    function handleBidDateChange() {
      // Optional validation could be added here
    }
    
    function handleSettlementDateChange() {
      // Optional validation could be added here
    }
    
    // Save date changes to the backend
    async function saveDateChanges() {
      if (!selectedTradeId.value) return
      
      dateFieldsLoading.value = true
      
      const data = {
        bid_date: bidDateModel.value || null,
        settlement_date: settlementDateModel.value || null,
      }
      
      const success = await tradeAssumptionsStore.updateAssumptions(selectedTradeId.value, data)
      
      if (success) {
        // Update our original values to match current values
        originalBidDate.value = bidDateModel.value
        originalSettlementDate.value = settlementDateModel.value
      }
      
      dateFieldsLoading.value = false
      return success
    }
    
    // Auto-save function triggered on input change
    async function autosaveDateChanges() {
      await saveDateChanges()
    }

    // Fetch sellers using centralized Axios instance
    async function fetchSellers(): Promise<void> {
      if (sellersLoading.value) return
      sellersLoading.value = true
      try {
        // Leading slash to correctly join with baseURL '/api' -> '/api/acq/sellers/'
        const resp = await http.get<SellerOption[]>(`/acq/sellers/`)
        sellers.value = Array.isArray(resp.data) ? resp.data : []
      } catch (e) {
        console.error('[Acq Index] Failed to load sellers', e)
        sellers.value = []
      } finally {
        sellersLoading.value = false
      }
    }

    // Fetch trades for a specific seller with cancellation and timeout
    let tradesController: AbortController | null = null
    async function fetchTrades(sellerId: number): Promise<void> {
      if (!sellerId) { trades.value = []; return }
      tradesLoading.value = true
      try {
        // Abort any previous in-flight request
        if (tradesController) { try { tradesController.abort() } catch {} }
        tradesController = new AbortController()
        const resp = await http.get<TradeOption[]>(`/acq/trades/${sellerId}/`, {
          signal: tradesController.signal as any,
          timeout: 10000,
        })
        trades.value = Array.isArray(resp.data) ? resp.data : []
      } catch (e) {
        // Non-fatal: log and clear list so the select becomes enabled
        console.error('[Acq Index] Failed to load trades', e)
        trades.value = []
      } finally {
        tradesLoading.value = false
        tradesController = null
      }
    }

    // Watch seller selection -> load trades list
    watch(selectedSellerId, async (newSellerId) => {
      trades.value = []
      resetLocalDateModels()
      if (newSellerId) await fetchTrades(newSellerId)
    })

    watch(selectedTradeId, async (newTradeId) => {
      if (newTradeId) {
        // Fetch trade assumptions when trade is selected
        dateFieldsLoading.value = true
        await tradeAssumptionsStore.fetchAssumptions(newTradeId)
        await acqStore.fetchTradeStatus()
        updateLocalDateModels()
        dateFieldsLoading.value = false
      } else {
        resetLocalDateModels()
        acqStore.resetTradeStatus()
      }
    })

    onMounted(async () => {
      await fetchSellers()
      // If a seller already selected (e.g., persisted), load trades
      if (selectedSellerId.value) {
        await fetchTrades(selectedSellerId.value)
      }
      if (selectedTradeId.value) {
        await acqStore.fetchTradeStatus()
      }
    })

    // Documents Quick View placeholder items (to be wired to real data)
    const docItems = computed<DocumentItem[]>(() => {
      return [
        {
          id: 'pdf-bpo',
          name: 'BPO.pdf',
          type: 'application/pdf',
          sizeBytes: Math.round(2.3 * 1024 * 1024),
          previewUrl: '#',
          downloadUrl: '#',
        },
        {
          id: 'pdf-appraisal',
          name: 'Appraisal.pdf',
          type: 'application/pdf',
          sizeBytes: Math.round(3.25 * 1024 * 1024),
          previewUrl: '#',
          downloadUrl: '#',
        },
        {
          id: 'doc-memo',
          name: 'Memo.docx',
          type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
          sizeBytes: Math.round(7.05 * 1024 * 1024),
          previewUrl: '#',
          downloadUrl: '#',
        },
      ]
    })

    // Function to reset all selections via store actions
    function resetSelections(): void {
      // Clear global selections
      acqStore.setSeller(null)
      acqStore.setTrade(null)
      // Also clear the AG Grid dataset immediately
      try {
        gridRowsStore.resetRows()
        gridRowsStore.clearCache()
      } catch (e) {
        console.warn('[Acq Index] resetSelections: failed to reset grid rows', e)
      }
    }
    
    // Consider grid rows "loaded" when we have both IDs, not currently fetching, and have >0 rows
    const gridRowsLoaded = computed<boolean>(() => {
      return !!(selectedSellerId.value && selectedTradeId.value) && !gridLoadingRows.value && Array.isArray(gridRows.value) && gridRows.value.length > 0
    })

    async function handleTradeStatusUpdate(value: string) {
      await acqStore.updateTradeStatus(value)
    }

    async function handleTradeStatusRefresh() {
      await acqStore.fetchTradeStatus()
    }

    return {
      sellers,
      trades,
      sellersLoading,
      tradesLoading,
      selectedSellerId,
      selectedTradeId,
      resetSelections,
      tradeStatusValue,
      tradeStatusOptions,
      tradeStatusLoading,
      handleTradeStatusUpdate,
      handleTradeStatusRefresh,
      docItems,
      gridRowsLoaded,
      // Date fields
      bidDateModel,
      settlementDateModel,
      dateFieldsLoading,
      hasDateChanges,
      // Modal state
      showTradeDetailsModal,
      showTradeDocumentsModal,
      showImportModal,
      selectedSellerLabel,
      selectedTradeLabel,
      tradeDocumentContext,
      // Date functions
      saveDateChanges,
      autosaveDateChanges,
    }
  },
  data() {
    return {
      // Whether the Loan-Level modal is visible
      showLoanModal: false as boolean,
      // Payload selected from the grid link
      selectedId: null as string | null,
      selectedRow: null as any,
      selectedAddr: null as string | null,
    }
  },
  computed: {
    // Builds a friendly modal title similar to the full-page breadcrumb title
    modalTitle(): string {
      const id = this.selectedId ? String(this.selectedId) : ''
      const addr = this.selectedAddr ? String(this.selectedAddr) : ''
      if (id && addr) return `${id} — ${addr}`
      if (id) return id
      if (addr) return addr
      return 'Asset Details'
    },
    // First line: just the ID (if available)
    modalIdText(): string {
      const id = this.selectedId ? String(this.selectedId) : ''
      const r: any = this.selectedRow || {}
      // Try multiple common keys for trade name
      const tradeName = String(r.trade_name ?? r.trade?.trade_name ?? r.tradeName ?? '').trim()
      const line = [id, tradeName].filter(Boolean).join(' / ')
      return line || 'Asset'
    },
    // Second line: Address without ZIP. Prefer selectedRow fields; fallback to selectedAddr string
    modalAddrText(): string {
      const r: any = this.selectedRow || {}
      const street = String(r.street_address ?? '').trim()
      const city = String(r.city ?? '').trim()
      const state = String(r.state ?? '').trim()
      const locality = [city, state].filter(Boolean).join(', ')
      const built = [street, locality].filter(Boolean).join(', ')
      if (built) return built
      const rawAddr = this.selectedAddr ? String(this.selectedAddr) : ''
      // Strip trailing ZIP if present
      return rawAddr.replace(/,?\s*\d{5}(?:-\d{4})?$/, '')
    },
  },
  methods: {
    /**
     * Handle successful import - refresh data
     */
    handleImportSuccess(): void {
      // Refresh sellers list after import
      (this as any).fetchSellers?.()
      this.showImportModal = false
    },
    /**
     * onModalShown
     * Attach a keydown listener while modal is open to support Ctrl+Enter shortcut.
     */
    onModalShown(): void {
      document.addEventListener('keydown', this.onKeydown as any)
    },
    /**
     * onOpenLoan
     * Called by the grid's ActionsCell "View" button. Opens the BootstrapVue
     * Next modal and stores the provided payload (id, row, addr).
     */
    onOpenLoan(payload: { id: string; row: any; addr?: string }): void {
      console.log('[Acquisitions] onOpenLoan payload=', payload)
      this.selectedId = payload?.id ?? null
      this.selectedRow = payload?.row ?? null
      this.selectedAddr = payload?.addr ?? null
      console.log('[Acquisitions] set selectedId=', this.selectedId, 'selectedRow.id=', this.selectedRow?.id)
      this.showLoanModal = true
    },
    /**
     * openFullPage
     * Navigate to the full page route with current selection, then hide modal.
     */
    openFullPage(): void {
      if (!this.selectedId) return
      const query: any = { id: this.selectedId }
      if (this.selectedAddr) query.addr = this.selectedAddr
      // Close modal first for cleanliness
      this.showLoanModal = false
      // Navigate to the loan-level details page
      this.$router.push({ path: '/loanlvl/products-details', query })
    },
    /**
     * onKeydown
     * Handles Ctrl+Enter shortcut to trigger openFullPage while modal is open.
     */
    onKeydown(e: KeyboardEvent): void {
      if (e.ctrlKey && (e.key === 'Enter' || e.code === 'Enter')) {
        e.preventDefault()
        this.openFullPage()
      }
    },
    /**
     * Clear state when modal fully hides
     */
    onModalHidden(): void {
      document.removeEventListener('keydown', this.onKeydown as any)
      this.selectedId = null
      this.selectedRow = null
      this.selectedAddr = null
    },
    /**
     * handleOptionTrigger
     * Responds to preview interactions from the Option prototypes and opens linked modals.
     */
    handleOptionTrigger(actionId: string): void {
      console.log('[Acquisitions] Prototype trigger ->', actionId)
      if (actionId === 'trade-assumptions' || actionId === 'settings-assumptions') {
        this.showTradeDetailsModal = true
      }
      if (actionId === 'trade-documents' || actionId === 'documents-room') {
        this.showTradeDocumentsModal = true
      }
      if (actionId === 'trade-approvals' || actionId === 'approvals-checklist') {
        console.log('[Acquisitions] Approvals prototype selected')
      }
    },
  },
  mounted() {
    // this.useMeta({
    //   title: "Acquisitions Dashboard",
    // });
  }
};
</script>
