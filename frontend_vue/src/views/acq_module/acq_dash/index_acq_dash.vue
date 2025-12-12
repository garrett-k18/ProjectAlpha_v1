<template>
  <Layout>
    <b-row>
      <b-col class="col-12">
        <div class="page-title-box">
          <div class="page-title-right">
            <!-- Removed refresh button/form -->
          </div>
          <h4 class="page-title">Acquisition Pipeline</h4>
        </div>
      </b-col>
    </b-row>

   

    <!-- Prominent, centered selectors: MUST choose before page functions -->
    <b-row class="m-0">
      <b-col class="col-12">
        <div class="card">
          <!-- Balanced vertical padding for centered appearance -->
          <div class="card-body p-2">
            <!-- Centered selectors with Trade Settings button -->
            <div class="d-flex flex-wrap align-items-center justify-content-center gap-2 w-100 mb-0">
              
              <!-- Combined Active Pipeline select -->
              <div class="d-flex align-items-center gap-2">
                <label class="form-label fw-bold fs-5 mb-0" for="activePipelineSelect">Active Pipeline</label>
                <select
                  id="activePipelineSelect"
                  class="form-select form-select-sm text-center"
                  style="width: 400px; min-width: 400px; max-width: 400px;"
                  v-model="activePipelineSelection"
                  :disabled="pipelineLoading"
                >
                  <option :value="null">Select a deal from pipeline</option>
                  <option 
                    v-for="item in pipelineOptions" 
                    :key="item.key" 
                    :value="item.key"
                  >
                    {{ item.label }}
                  </option>
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
              <span v-if="pipelineLoading">Loading pipeline…</span>
              <span v-else-if="!selectedTradeId">Select a deal from the active pipeline to begin.</span>
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
        <VectorMap @open-loan="onOpenLoan" />
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
          v-model:servicingTransferDate="servicingTransferDateModel"
          v-model:servicerId="servicerIdModel"
          :servicers="servicers"
          :servicersLoading="servicersLoading"
          v-model:bidMethod="bidMethodModel"
          v-model:pctUPB="pctUPBModel"
          v-model:targetIrr="targetIrrModel"
          v-model:discountRate="discountRateModel"
          v-model:perfRplHoldPeriod="perfRplHoldPeriodModel"
          v-model:modRate="modRateModel"
          v-model:modLegalTerm="modLegalTermModel"
          v-model:modAmortTerm="modAmortTermModel"
          v-model:maxModLtv="maxModLtvModel"
          v-model:modIoFlag="modIoFlagModel"
          v-model:modDownPmt="modDownPmtModel"
          v-model:modOrigCost="modOrigCostModel"
          v-model:modSetupDuration="modSetupDurationModel"
          v-model:modHoldDuration="modHoldDurationModel"
          v-model:acqLegalCost="acqLegalCostModel"
          v-model:acqDdCost="acqDdCostModel"
          v-model:acqTaxTitleCost="acqTaxTitleCostModel"
          v-model:acqBrokerFees="acqBrokerFeesModel"
          v-model:acqOtherCosts="acqOtherCostsModel"
          v-model:amFeePct="amFeePctModel"
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

    <!-- Broker Assignments Modal -->
    <!-- WHAT: Modal for assigning brokers to assets in the current trade -->
    <!-- WHY: Centralized broker assignment workflow accessible from Trade Action Dock -->
    <BModal
      v-model="showBrokerAssignmentsModal"
      title="Broker Assignments"
      size="xl"
      centered
    >
      <BrokerAssignmentModal
        v-if="selectedTradeId"
        :rows="gridRows"
        :selected-seller-id="selectedSellerId"
        :selected-trade-id="selectedTradeId"
        @open-loan-modal="onOpenLoan"
      />
      <div v-else class="text-center py-4">
        <p class="text-muted">Please select a trade to assign brokers.</p>
      </div>
      <template #footer>
        <div class="d-flex justify-content-end w-100 gap-2">
          <button class="btn btn-primary" @click="showBrokerAssignmentsModal = false">Close</button>
        </div>
      </template>
    </BModal>
  </Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import StratsCurrentBal from "@/views/acq_module/acq_dash/strats/strats-current-bal.vue";
import StratsTotalDebt from "@/views/acq_module/acq_dash/strats/strats-total-debt.vue";
import StratsSellerAsIs from "@/views/acq_module/acq_dash/strats/strats-seller-asis.vue";
import StratsWac from "@/views/acq_module/acq_dash/strats/strats-wac.vue";
import StratsDefaultRate from "@/views/acq_module/acq_dash/strats/strats-default-rate.vue";
import StratsPropertyType from "@/views/acq_module/acq_dash/strats/strats-property-type.vue";
import StratsOccupancy from "@/views/acq_module/acq_dash/strats/strats-occupancy.vue";
import StratsJudVsNon from "@/views/acq_module/acq_dash/strats/strats-judvsnon.vue";
import StratsDelinquency from "@/views/acq_module/acq_dash/strats/strats-delinquency.vue";
import VectorMap from "@/views/acq_module/acq_dash/vectorMap.vue";
import Widgets from "@/views/acq_module/acq_dash/widgets.vue";
import TradeTasking from '@/views/acq_module/acq_dash/components/TradeTasking.vue';
import http from '@/lib/http'
// Local type for document items used by TradeDocumentsModal
// Exported to fix TypeScript module inference when this component is imported elsewhere
export interface DocumentItem { id: string; name: string; type: string; sizeBytes: number; previewUrl: string; downloadUrl: string }
// AG Grid: simplified testing grid for acquisitions dashboard
import AcqGrid from "@/views/acq_module/acq_dash/acq-grid.vue";
// BootstrapVue Next modal component (Vue 3 compatible)
import { BModal } from 'bootstrap-vue-next';
// Centralized loan-level wrapper used for both full-page and modal
import LoanLevelIndex from '@/views/acq_module/loanlvl/loanlvl_index.vue'
// Trade modals
import TradeDetailsModal from '@/views/acq_module/acq_dash/modals/TradeDetailsModal.vue'
import TradeDocumentsModal from '@/views/acq_module/acq_dash/modals/TradeDocumentsModal.vue'
import ImportSellerTapeModal from '@/views/acq_module/acq_dash/modals/ImportSellerTapeModal.vue'
import BrokerAssignmentModal from '@/views/acq_module/acq_dash/components/BrokerAssignmentModal.vue'
// Trade control prototype Option 1 (Action Dock)
import TradeActionDock from '@/views/acq_module/acq_dash/components/TradeActionDock.vue';
// Trade control prototype Option 2 (Tabbed Control Center)
// Selections store + helpers
import { useAcqSelectionsStore } from '@/stores/acqSelections'
import { useAgGridRowsStore } from '@/stores/agGridRows'
import { useTradeAssumptionsStore } from '@/stores/tradeAssumptions'
import { storeToRefs } from 'pinia'
import { ref, watch, onMounted, computed } from 'vue'
import type { SellerOption, TradeOption } from '@/stores/acqSelections'

// WHAT: Local servicer type to avoid circular type dependencies
// WHY: Prevents Vue type inference issues with TradeDetailsModal
interface ServicerOption {
  id: number
  servicerName: string
  defaultForTradeAssumptions?: boolean
}

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
    BrokerAssignmentModal,
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

    // WHAT: Trade assumptions form state - all fields from TradeDetailsModal
    // WHY: Need reactive references for all form fields to enable two-way binding
    // Trade dates
    const bidDateModel = ref<string>('')
    const settlementDateModel = ref<string>('')
    const servicingTransferDateModel = ref<string>('')
    // Servicer selection
    const servicerIdModel = ref<number | null>(null)
    const servicers = ref<ServicerOption[]>([])
    const servicersLoading = ref<boolean>(false)
    // Financial assumptions
    const bidMethodModel = ref<string>('')
    const pctUPBModel = ref<number | string>('')
    const targetIrrModel = ref<number | string>('')
    const discountRateModel = ref<number | string>('')
    const perfRplHoldPeriodModel = ref<number | string>('')
    // Modification assumptions
    const modRateModel = ref<number | string>('')
    const modLegalTermModel = ref<number | string>('')
    const modAmortTermModel = ref<number | string>('')
    const maxModLtvModel = ref<number | string>('')
    const modIoFlagModel = ref<boolean>(false)
    const modDownPmtModel = ref<number | string>('')
    const modOrigCostModel = ref<number | string>('')
    const modSetupDurationModel = ref<number | string>('')
    const modHoldDurationModel = ref<number | string>('')
    // Acquisition costs
    const acqLegalCostModel = ref<number | string>('')
    const acqDdCostModel = ref<number | string>('')
    const acqTaxTitleCostModel = ref<number | string>('')
    const acqBrokerFeesModel = ref<number | string>('')
    const acqOtherCostsModel = ref<number | string>('')
    // Asset management fees
    const amFeePctModel = ref<number | string>('')
    
    const dateFieldsLoading = ref<boolean>(false)

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
    const showBrokerAssignmentsModal = ref<boolean>(false) // Controls visibility of the broker assignments modal

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

    // WHAT: Update local form models from store
    // WHY: Load saved assumptions when trade is selected
    function updateLocalDateModels() {
      const assumptions = tradeAssumptionsStore.assumptions
      if (assumptions) {
        // WHAT: Load all form fields from store assumptions
        // Trade dates
        bidDateModel.value = assumptions.bid_date ? assumptions.bid_date.substring(0, 10) : ''
        settlementDateModel.value = assumptions.settlement_date ? assumptions.settlement_date.substring(0, 10) : ''
        servicingTransferDateModel.value = assumptions.servicing_transfer_date ? assumptions.servicing_transfer_date.substring(0, 10) : ''
        // Servicer selection (use type assertion for optional property)
        // WHAT: Default UI selection to the configured default servicer when no servicer_id is set
        // WHY: Trade assumptions should respect the global default configured in Servicer Assumptions
        servicerIdModel.value = (assumptions as any).servicer_id ?? getDefaultServicerId()
        // Financial assumptions
        bidMethodModel.value = assumptions.bid_method ?? ''
        pctUPBModel.value = assumptions.pctUPB ?? ''
        targetIrrModel.value = assumptions.target_irr ?? ''
        discountRateModel.value = assumptions.discount_rate ?? ''
        perfRplHoldPeriodModel.value = assumptions.perf_rpl_hold_period ?? ''
        // Modification assumptions
        modRateModel.value = assumptions.mod_rate ?? ''
        modLegalTermModel.value = assumptions.mod_legal_term ?? ''
        modAmortTermModel.value = assumptions.mod_amort_term ?? ''
        maxModLtvModel.value = assumptions.max_mod_ltv ?? ''
        modIoFlagModel.value = assumptions.mod_io_flag ?? false
        modDownPmtModel.value = assumptions.mod_down_pmt ?? ''
        modOrigCostModel.value = assumptions.mod_orig_cost ?? ''
        modSetupDurationModel.value = assumptions.mod_setup_duration ?? ''
        modHoldDurationModel.value = assumptions.mod_hold_duration ?? ''
        // Acquisition costs
        acqLegalCostModel.value = assumptions.acq_legal_cost ?? ''
        acqDdCostModel.value = assumptions.acq_dd_cost ?? ''
        acqTaxTitleCostModel.value = assumptions.acq_tax_title_cost ?? ''
        acqBrokerFeesModel.value = assumptions.acq_broker_fees ?? ''
        acqOtherCostsModel.value = assumptions.acq_other_costs ?? ''
        // Asset management fees
        amFeePctModel.value = assumptions.am_fee_pct ?? ''
      } else {
        // WHAT: No existing assumptions record for this trade
        // WHY: Show sensible defaults, using the globally configured default servicer in the UI
        resetLocalDateModels()
        servicerIdModel.value = getDefaultServicerId()
      }
    }
    
    // WHAT: Reset local form models
    // WHY: Clear all fields when switching trades or sellers
    function resetLocalDateModels() {
      // Trade dates
      bidDateModel.value = ''
      settlementDateModel.value = ''
      servicingTransferDateModel.value = ''
      // Servicer selection
      servicerIdModel.value = null
      // Financial assumptions
      bidMethodModel.value = ''
      pctUPBModel.value = ''
      targetIrrModel.value = ''
      discountRateModel.value = ''
      perfRplHoldPeriodModel.value = ''
      // Modification assumptions
      modRateModel.value = ''
      modLegalTermModel.value = ''
      modAmortTermModel.value = ''
      maxModLtvModel.value = ''
      modIoFlagModel.value = false
      modDownPmtModel.value = ''
      modOrigCostModel.value = ''
      modSetupDurationModel.value = ''
      modHoldDurationModel.value = ''
      // Acquisition costs
      acqLegalCostModel.value = ''
      acqDdCostModel.value = ''
      acqTaxTitleCostModel.value = ''
      acqBrokerFeesModel.value = ''
      acqOtherCostsModel.value = ''
      // Asset management fees
      amFeePctModel.value = ''
    }
    
    // Handlers for date input changes
    function handleBidDateChange() {
      // Optional validation could be added here
    }
    
    function handleSettlementDateChange() {
      // Optional validation could be added here
    }
    
    // WHAT: Save all trade assumption changes to the backend
    // WHY: Persist user-entered values for all form fields
    async function saveDateChanges() {
      if (!selectedTradeId.value) return
      
      dateFieldsLoading.value = true
      
      // WHAT: Build payload with all form fields
      // WHY: Convert all numeric values to strings as expected by the API
      const data = {
        // Trade dates
        bid_date: bidDateModel.value || null,
        settlement_date: settlementDateModel.value || null,
        servicing_transfer_date: servicingTransferDateModel.value || null,
        // Servicer selection
        servicer_id: servicerIdModel.value || null,
        // Financial assumptions (convert to string)
        bid_method: bidMethodModel.value || null,
        pctUPB: pctUPBModel.value ? String(pctUPBModel.value) : null,
        target_irr: targetIrrModel.value ? String(targetIrrModel.value) : null,
        discount_rate: discountRateModel.value ? String(discountRateModel.value) : null,
        perf_rpl_hold_period: perfRplHoldPeriodModel.value ? String(perfRplHoldPeriodModel.value) : null,
        // Modification assumptions (convert to string)
        mod_rate: modRateModel.value ? String(modRateModel.value) : null,
        mod_legal_term: modLegalTermModel.value ? String(modLegalTermModel.value) : null,
        mod_amort_term: modAmortTermModel.value ? String(modAmortTermModel.value) : null,
        max_mod_ltv: maxModLtvModel.value ? String(maxModLtvModel.value) : null,
        mod_io_flag: modIoFlagModel.value,
        mod_down_pmt: modDownPmtModel.value ? String(modDownPmtModel.value) : null,
        mod_orig_cost: modOrigCostModel.value ? String(modOrigCostModel.value) : null,
        mod_setup_duration: modSetupDurationModel.value ? String(modSetupDurationModel.value) : null,
        mod_hold_duration: modHoldDurationModel.value ? String(modHoldDurationModel.value) : null,
        // Acquisition costs (convert to string)
        acq_legal_cost: acqLegalCostModel.value ? String(acqLegalCostModel.value) : null,
        acq_dd_cost: acqDdCostModel.value ? String(acqDdCostModel.value) : null,
        acq_tax_title_cost: acqTaxTitleCostModel.value ? String(acqTaxTitleCostModel.value) : null,
        acq_broker_fees: acqBrokerFeesModel.value ? String(acqBrokerFeesModel.value) : null,
        acq_other_costs: acqOtherCostsModel.value ? String(acqOtherCostsModel.value) : null,
        // Asset management fees (convert to string)
        am_fee_pct: amFeePctModel.value ? String(amFeePctModel.value) : null,
      } as any
      
      const success = await tradeAssumptionsStore.updateAssumptions(selectedTradeId.value, data)
      
      dateFieldsLoading.value = false
      return success
    }
    
    // WHAT: Fetch servicers list for the dropdown
    // WHY: Load available servicers when component mounts
    // HOW: Call the /api/core/servicers/ endpoint
    async function fetchServicers() {
      servicersLoading.value = true
      try {
        const resp = await fetch('/api/core/servicers/', {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include'
        })
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
        const payload = await resp.json()
        // WHAT: Normalize response to handle both array and paginated formats
        // WHY: DRF can return either {results: [...]} or just [...]
        servicers.value = Array.isArray(payload)
          ? payload
          : Array.isArray(payload?.results)
            ? payload.results
            : []
      } catch (err) {
        console.error('[fetchServicers] Error loading servicers:', err)
        servicers.value = []
      } finally {
        servicersLoading.value = false
      }
    }

    // WHAT: Determine the default servicer id for trade assumptions
    // WHY: Use the Servicer flagged as defaultForTradeAssumptions, fall back to StateBridge or first in list
    function getDefaultServicerId(): number | null {
      const list = servicers.value as any[]
      if (!list || list.length === 0) return null

      const explicitDefault = list.find(s => s.defaultForTradeAssumptions)
      if (explicitDefault && typeof explicitDefault.id === 'number') {
        return explicitDefault.id
      }

      const stateBridge = list.find(
        s => typeof s.servicerName === 'string' && s.servicerName.toLowerCase().includes('statebridge')
      )
      if (stateBridge && typeof stateBridge.id === 'number') {
        return stateBridge.id
      }

      return typeof list[0].id === 'number' ? list[0].id : null
    }
    
    // Auto-save function triggered on input change
    async function autosaveDateChanges() {
      await saveDateChanges()
    }

    // WHAT: Active deals backing the combined pipeline dropdown
    // WHY: Single call to backend instead of per-seller loops
    const activeDeals = ref<Array<{ seller_id: number; seller_name: string; trade_id: number; trade_name: string; status?: string }>>([])
    const activeDealsLoading = ref<boolean>(false)

    // WHAT: Combined pipeline options that flatten all seller-trade combinations
    // WHY: Single dropdown showing "SELLER - Trade" for easier selection
    const pipelineOptions = computed(() => {
      return activeDeals.value.map((deal) => ({
        key: `${deal.seller_id}:${deal.trade_id}`,
        label: `${String(deal.seller_name).toUpperCase()} - ${deal.trade_name}`,
        sellerId: deal.seller_id,
        tradeId: deal.trade_id,
      }))
    })

    // WHAT: Load all active deals (seller+trade) for the pipeline dropdown
    // WHY: Users need to see all available deals in one place without N calls
    async function loadActiveDeals(): Promise<void> {
      activeDealsLoading.value = true
      try {
        const resp = await http.get<Array<{ seller_id: number; seller_name: string; trade_id: number; trade_name: string; status?: string }>>('/acq/trades/active-deals/', { timeout: 15000 })
        activeDeals.value = Array.isArray(resp.data) ? resp.data : []
      } catch (e) {
        console.warn('[Acq Index] Failed to load active deals for pipeline', e)
        activeDeals.value = []
      } finally {
        activeDealsLoading.value = false
      }
    }
    
    // WHAT: Two-way binding for the combined Active Pipeline dropdown
    // WHY: Parse "sellerId:tradeId" key and update both selections atomically
    const activePipelineSelection = computed<string | null>({
      get: () => {
        if (selectedSellerId.value && selectedTradeId.value) {
          return `${selectedSellerId.value}:${selectedTradeId.value}`
        }
        return null
      },
      set: (val) => {
        if (!val) {
          acqStore.setSeller(null)
          acqStore.setTrade(null)
          return
        }
        // Parse the "sellerId:tradeId" format
        const parts = val.split(':')
        if (parts.length === 2) {
          const sellerId = parseInt(parts[0], 10)
          const tradeId = parseInt(parts[1], 10)
          if (!isNaN(sellerId) && !isNaN(tradeId)) {
            // Set seller first, then trade
            acqStore.setSeller(sellerId)
            acqStore.setTrade(tradeId)
          }
        }
      },
    })
    
    // WHAT: Combined loading state for pipeline dropdown
    // WHY: Show loading indicator while fetching sellers or active deals
    const pipelineLoading = computed<boolean>(() => {
      return sellerOptionsLoading.value || tradeOptionsLoading.value || activeDealsLoading.value
    })

    // Watch seller selection -> reset local models and trade status when cleared
    watch(selectedSellerId, async (newSellerId) => {
      resetLocalDateModels();
      if (!newSellerId) {
        acqStore.resetTradeStatus();
      }
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

    // WHAT: Watch for modal opening to ensure data is loaded and displayed
    // WHY: When modal opens, we need to refresh data from backend and update local models
    // HOW: Fetch assumptions with forceRefresh and update local models when modal becomes visible
    watch(showTradeDetailsModal, async (isOpen) => {
      if (isOpen && selectedTradeId.value) {
        // WHAT: Fetch fresh data from backend when modal opens
        // WHY: Ensure we're showing the latest data, not stale cached data
        dateFieldsLoading.value = true
        try {
          // WHAT: Force refresh to bypass cache and get latest data from backend
          // WHY: The store caches data, but we want fresh data when modal opens to show current backend values
          await tradeAssumptionsStore.fetchAssumptions(selectedTradeId.value, true)
          // WHAT: Update local form models with fresh data from backend
          // WHY: Ensure form fields display the current backend values in the modal
          updateLocalDateModels()
        } catch (error) {
          console.error('[Acq Index] Failed to load trade assumptions for modal:', error)
          // WHAT: Even if fetch fails, try to update models with cached data if available
          // WHY: Better UX to show cached data than empty fields
          updateLocalDateModels()
        } finally {
          dateFieldsLoading.value = false
        }
      }
    })

    onMounted(async () => {
      // WHAT: Load sellers first
      await acqStore.fetchSellerOptions(true);
      // WHAT: Fetch servicers list for trade assumptions modal
      await fetchServicers();
      // WHAT: Load all active deals to populate Active Pipeline dropdown
      // WHY: Users need to see all available deals in one combined dropdown
      await loadActiveDeals();
      // WHAT: If a trade already selected (persisted in store), fetch its status
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
      // WHAT: Reload all active deals for the Active Pipeline dropdown
      await loadActiveDeals();
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
      gridRows,
      gridRowsLoaded,
      // WHAT: Active Pipeline combined dropdown
      pipelineOptions,
      activePipelineSelection,
      pipelineLoading,
      // WHAT: All form field models for TradeDetailsModal
      // Trade dates
      bidDateModel,
      settlementDateModel,
      servicingTransferDateModel,
      // Servicer selection
      servicerIdModel,
      servicers,
      servicersLoading,
      // Financial assumptions
      bidMethodModel,
      pctUPBModel,
      targetIrrModel,
      discountRateModel,
      perfRplHoldPeriodModel,
      // Modification assumptions
      modRateModel,
      modLegalTermModel,
      modAmortTermModel,
      maxModLtvModel,
      modIoFlagModel,
      modDownPmtModel,
      modOrigCostModel,
      modSetupDurationModel,
      modHoldDurationModel,
      // Acquisition costs
      acqLegalCostModel,
      acqDdCostModel,
      acqTaxTitleCostModel,
      // Asset management fees
      amFeePctModel,
      // Loading state
      dateFieldsLoading,
      // Modal state
      showTradeDetailsModal,
      showTradeDocumentsModal,
      showImportModal,
      showBrokerAssignmentsModal,
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
    // First line: prefer Seller Tape ID / loan # for display, fall back to internal id
    modalIdText(): string {
      const r: any = this.selectedRow || {}
      // WHAT: Prefer seller tape identifier surfaced on the row
      // WHY: Users think in terms of seller's loan number, not internal asset hub id
      const loanId = String(
        r.sellertape_id ??
        r.asset_hub_display?.sellertape_id ??
        ''
      ).trim()

      const internalId = this.selectedId ? String(this.selectedId) : ''

      // Try multiple common keys for trade name
      const tradeName = String(r.trade_name ?? r.trade?.trade_name ?? r.tradeName ?? '').trim()

      const primaryId = loanId || internalId
      const line = [primaryId, tradeName].filter(Boolean).join(' / ')
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
      if (actionId === 'broker-assignments') {
        // WHAT: Open broker assignments modal when action is triggered
        // WHY: Allow users to assign brokers to assets in the current trade
        this.showBrokerAssignmentsModal = true
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
