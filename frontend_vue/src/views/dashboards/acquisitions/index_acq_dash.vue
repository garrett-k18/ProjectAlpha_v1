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

    <!-- Value stratification cards: keep the three financial metrics together at the top -->
    <b-row class="g-2 mt-2" v-if="gridRowsLoaded">
      <b-col xl="4" lg="6" md="12">
        <StratsCurrentBal />
      </b-col>
      <b-col xl="4" lg="6" md="12">
        <StratsTotalDebt />
      </b-col>
      <b-col xl="4" lg="6" md="12">
        <StratsSellerAsIs />
      </b-col>
    </b-row>

    <!-- Property Type, Coupon, and Default Rate share a dedicated row for rate-focused insights -->
    <b-row class="g-2 mt-2 strat-row-equal-height" v-if="gridRowsLoaded">
      <b-col xl="4" lg="6" md="12" class="d-flex">
        <StratsPropertyType />
      </b-col>
      <b-col xl="4" lg="6" md="12" class="d-flex">
        <StratsWac />
      </b-col>
      <b-col xl="4" lg="6" md="12" class="d-flex">
        <StratsDefaultRate />
      </b-col>
    </b-row>

    <!-- Remaining categorical cards grouped below with Occupancy leading the row per user request -->
    <b-row class="g-2 mt-2 mb-3" v-if="gridRowsLoaded">
      <b-col xl="4" lg="6" md="12">
        <StratsOccupancy />
      </b-col>
      <b-col xl="4" lg="6" md="12">
        <StratsJudVsNon />
      </b-col>
      <b-col xl="4" lg="6" md="12">
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
        @refresh="handleImportRefresh"
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
import StratsDefaultRate from "@/views/dashboards/acquisitions/strats/strats-default-rate.vue";
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
import type { SellerOption, TradeOption } from '@/stores/acqSelections'

export default {
  components: {
    VectorMap,
    StratsJudVsNon,
    StratsCurrentBal,
    StratsTotalDebt,
    StratsSellerAsIs,
    StratsWac,
    StratsDefaultRate,
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
    // WHAT: Main acquisitions selections store consolidates seller/trade choices.
    // WHY: Avoid duplicate fetch logic across dashboard widgets and modals.
    const acqStore = useAcqSelectionsStore();
    const tradeAssumptionsStore = useTradeAssumptionsStore();
    const {
      tradeStatusValue,
      tradeStatusOptions,
      tradeStatusLoading,
      sellerOptions,
      tradeOptions,
      sellerOptionsLoading,
      tradeOptionsLoading,
      sellerOptionsError,
      tradeOptionsError,
    } = storeToRefs(acqStore);

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
      const match = sellerOptions.value.find((s) => s.id === (selectedSellerId.value ?? -1)) // Look up seller in current list
      return match ? match.name : 'No seller selected' // Return seller name or fallback placeholder
    })

    // selectedTradeLabel resolves the human-readable trade name for the trade control prototypes
    const selectedTradeLabel = computed<string>(() => {
      const match = tradeOptions.value.find((t) => t.id === (selectedTradeId.value ?? -1)) // Look up trade in current list
      return match ? match.trade_name : 'No trade selected' // Return trade name or fallback placeholder
    })

    // Context payload forwarded into TradeDocumentsModal for shared document components
    const tradeDocumentContext = computed(() => {
      const seller = sellerOptions.value.find((s) => s.id === (selectedSellerId.value ?? -1)) || null
      const trade = tradeOptions.value.find((t) => t.id === (selectedTradeId.value ?? -1)) || null
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

    // Watch seller selection -> load trades list
    watch(selectedSellerId, async (newSellerId) => {
      resetLocalDateModels();
      if (newSellerId) {
        await acqStore.fetchTradeOptions(newSellerId, true);
      } else {
        acqStore.resetTradeStatus();
      }
    });

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
      await acqStore.fetchSellerOptions(true);
      // WHAT: If a seller already selected (persisted in store), prime the trades list too.
      if (selectedSellerId.value) {
        await acqStore.fetchTradeOptions(selectedSellerId.value, true);
      }
      if (selectedTradeId.value) {
        await acqStore.fetchTradeStatus();
      }
    });

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
      // WHAT: persist status change via Pinia action so backend updates immediately
      const sellerIdBeforeChange = selectedSellerId.value // Capture seller id before any resets
      const tradeIdBeforeChange = selectedTradeId.value // Capture trade id before any resets
      const success = await acqStore.updateTradeStatus(value) // WHY: upstream handles API call and store synchronization
      if (!success) {
        return // Early exit when backend rejects the update so UI stays unchanged
      }

      // WHAT: When a trade is Passed or Boarded it should disappear from selectors
      const isTerminalStatus = value === 'PASS' || value === 'BOARD'
      if (!isTerminalStatus) {
        return // Non-terminal updates (e.g., DD/AWARDED) keep selectors as-is
      }

      // WHAT: Clear trade selection so dependent widgets reset immediately
      if (tradeIdBeforeChange !== null) {
        acqStore.setTrade(null) // WHY: ensures grid + status UI reset in tandem with dropdown state
      }

      // WHAT: Remove trade locally so dropdown updates without waiting on network
      if (tradeIdBeforeChange !== null) {
        tradeOptions.value = tradeOptions.value.filter((trade) => trade.id !== tradeIdBeforeChange);
      }

      // WHAT: Refresh trade list from backend to ensure alignment with server filters
      if (sellerIdBeforeChange !== null) {
        await acqStore.fetchTradeOptions(sellerIdBeforeChange, true); // WHY: backend now excludes PASS/BOARD so dropdown stays authoritative
      }

      // WHAT: If no trades remain for the seller, drop the seller entry and clear selection
      if (sellerIdBeforeChange !== null && tradeOptions.value.length === 0) {
        sellerOptions.value = sellerOptions.value.filter((seller) => seller.id !== sellerIdBeforeChange); // Remove seller from local options
        acqStore.setSeller(null); // Reset seller selection so watchers clear downstream state
      }

      // WHAT: Always refresh sellers list so new backend filtering (active trades only) is reflected globally
      await acqStore.fetchSellerOptions(true);
    }

    // WHAT: Refresh dropdown caches after import so new sellers/trades appear instantly.
    const handleImportRefresh = async (): Promise<void> => {
      await acqStore.refreshOptions();
      if (selectedSellerId.value) {
        await acqStore.fetchTradeOptions(selectedSellerId.value, true);
      }
    };

    // WHAT: Close modal on success, reload options, and auto-select imported seller/trade
    const handleImportSuccess = async (payload?: { sellerId: number; tradeId: number }): Promise<void> => {
      await handleImportRefresh();
      
      // Auto-select the imported seller and trade
      if (payload?.sellerId && payload?.tradeId) {
        acqStore.selectedSellerId = payload.sellerId;
        acqStore.selectedTradeId = payload.tradeId;
      }
      
      showImportModal.value = false;
    };

    return {
      sellers: sellerOptions,
      trades: tradeOptions,
      sellersLoading: sellerOptionsLoading,
      tradesLoading: tradeOptionsLoading,
      sellerOptionsError,
      tradeOptionsError,
      selectedSellerId,
      selectedTradeId,
      resetSelections,
      tradeStatusValue,
      tradeStatusOptions,
      tradeStatusLoading,
      handleTradeStatusUpdate,
      handleImportRefresh,
      handleImportSuccess,
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

<style>
/* Global style for all strat table headers - add subtle bottom border */
.bands-table thead th {
  border-bottom: 2px solid rgba(0, 0, 0, 0.1) !important;
  padding-bottom: 0.75rem !important;
}

/* Force equal height cards in strat row - nuclear option */
.strat-row-equal-height {
  display: flex;
  flex-wrap: wrap;
}

.strat-row-equal-height > [class*="col"] {
  display: flex !important;
}

.strat-row-equal-height .card {
  width: 100% !important;
  height: 100% !important;
  display: flex !important;
  flex-direction: column !important;
  min-height: 0 !important;
}

.strat-row-equal-height .card-body {
  flex: 1 1 auto !important;
  overflow: auto !important;
}
</style>
