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
    <b-row class="mb-3">
      <b-col class="col-12">
        <div class="card">
          <div class="card-body py-3">
            <div class="d-flex flex-column align-items-center">
              <div class="fw-bold text-center mb-2 fs-5">Select Seller and Trade</div>
              <div class="row g-2 justify-content-center w-100">
                <div class="col-12 col-md-4 col-lg-3">
                  <label class="form-label fw-bold text-center w-100" for="topSellerSelect">Seller</label>
                  <select
                    id="topSellerSelect"
                    class="form-select text-center"
                    v-model="selectedSellerId"
                    :disabled="sellersLoading"
                  >
                    <option :value="null">Select a seller</option>
                    <option v-for="s in sellers" :key="s.id" :value="s.id">{{ s.name }}</option>
                  </select>
                </div>
                <div class="col-12 col-md-4 col-lg-3">
                  <label class="form-label fw-bold text-center w-100" for="topTradeSelect">Trade</label>
                  <select
                    id="topTradeSelect"
                    class="form-select text-center"
                    v-model="selectedTradeId"
                    :disabled="!selectedSellerId || tradesLoading"
                  >
                    <option :value="null">Select a trade</option>
                    <option v-for="t in trades" :key="t.id" :value="t.id">{{ t.trade_name }}</option>
                  </select>
                </div>
              </div>
              <div class="form-text text-center mt-2">
                <span v-if="sellersLoading">Loading sellers…</span>
                <span v-else-if="selectedSellerId && tradesLoading">Loading trades…</span>
                <span v-else-if="selectedSellerId && !selectedTradeId">Select a trade to view data.</span>
                <span v-else-if="!selectedSellerId">Select a seller to begin.</span>
              </div>
            </div>
          </div>
        </div>
      </b-col>
    </b-row>

    <!-- Top metrics widgets rendered by a dedicated component -->
    <Widgets />

    <!-- Seller Data Tape card (AG Grid) moved directly under top metrics -->
    <b-row class="mt-2">
      <b-col class="col-12">
        <!-- Pass behavior control to the grid: modal-first with onOpenLoan callback -->
        <DataGrid :open-mode="'modal'" :open-loan="onOpenLoan" :show-filters="false" />
      </b-col>
    </b-row>

    <!-- Overview moved to its own row -->
    <b-row class="mt-2">
      <b-col class="col-12">
        <Overview />
      </b-col>
    </b-row>

    <b-row>
      <b-col class="col-12">
        <VectorMap />
      </b-col>
    </b-row>

    <b-row>
      <b-col xl="4" lg="12">
        <Strats />
      </b-col>

      <b-col xl="4" lg="6">
        <Browser />
      </b-col>

      <b-col xl="4" lg="6">
        <System />
      </b-col>
    </b-row>

    <b-row>
      <b-col xl="4" lg="6">
        <Channel />
      </b-col>

      <b-col xl="4" lg="6">
        <Media />
      </b-col>

      <b-col xl="4" lg="12">
        <EngagementOverview />
      </b-col>
    </b-row>

    
    <!-- Loan-Level Modal wrapper using BootstrapVue Next -->
    <!-- Docs: https://bootstrap-vue-next.github.io/bootstrap-vue-next/docs/components/modal -->
    <BModal
      v-model="showLoanModal"
      size="xl"
      body-class="p-0"
      dialog-class="product-details-dialog"
      content-class="product-details-content"
      hide-footer
      @shown="onModalShown"
      @hidden="onModalHidden"
    >
      <!-- Custom header with action button (far right) -->
      <template #header>
        <div class="d-flex align-items-center w-100">
          <h5 class="modal-title mb-0">{{ modalTitle }}</h5>
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
      <LoanLevelIndex
        :productId="selectedId"
        :row="selectedRow"
        :address="selectedAddr"
        :standalone="false"
      />
    </BModal>
  </Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Overview from "@/views/dashboards/acquisitions/overview.vue";
import Strats from "@/views/dashboards/acquisitions/strats.vue";
import Browser from "@/views/dashboards/acquisitions/browser.vue";
import System from "@/views/dashboards/acquisitions/system.vue";
import Channel from "@/views/dashboards/acquisitions/channel.vue";
import Media from "@/views/dashboards/acquisitions/media.vue";
import EngagementOverview from "@/views/dashboards/acquisitions/engagement-overview.vue";
import VectorMap from "@/views/dashboards/acquisitions/vectorMap.vue";
import Widgets from "@/views/dashboards/acquisitions/widgets.vue";
// AG Grid: modular data grid component for acquisitions dashboard
import DataGrid from "@/views/dashboards/acquisitions/data-grid.vue";
// BootstrapVue Next modal component (Vue 3 compatible)
import { BModal } from 'bootstrap-vue-next';
// Centralized loan-level wrapper used for both full-page and modal
import LoanLevelIndex from '@/views/acq_module/loanlvl/loanlvl_index.vue'
// Selections store + helpers
import { useAcqSelectionsStore } from '@/stores/acqSelections'
import { storeToRefs } from 'pinia'
import { ref, watch, onMounted } from 'vue'
// Centralized Axios instance (baseURL='/api')
import http from '@/lib/http'

// Types for dropdown options (module-scope to satisfy TS export typing)
export interface SellerOption { id: number; name: string }
export interface TradeOption { id: number; trade_name: string }

export default {
  components: {
    VectorMap,
    EngagementOverview,
    Media,
    Channel,
    System,
    Browser,
    Strats,
    Overview,
    Widgets,
    // Register AG Grid data grid component
    DataGrid,
    Layout,
    // Register modal + loan-level wrapper
    BModal,
    LoanLevelIndex,
  },
  setup() {
    // Local lists for options
    const sellers = ref<SellerOption[]>([])
    const trades = ref<TradeOption[]>([])
    const sellersLoading = ref<boolean>(false)
    const tradesLoading = ref<boolean>(false)

    // Shared selection state via Pinia store
    const acqStore = useAcqSelectionsStore()
    const { selectedSellerId, selectedTradeId } = storeToRefs(acqStore)

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

    // Fetch trades for a specific seller
    async function fetchTrades(sellerId: number): Promise<void> {
      if (!sellerId) { trades.value = []; return }
      tradesLoading.value = true
      try {
        const resp = await http.get<TradeOption[]>(`/acq/trades/${sellerId}/`)
        trades.value = Array.isArray(resp.data) ? resp.data : []
      } catch (e) {
        console.error('[Acq Index] Failed to load trades', e)
        trades.value = []
      } finally {
        tradesLoading.value = false
      }
    }

    // Watch seller selection -> clear trade and load trades list
    watch(selectedSellerId, async (newSellerId) => {
      // Clear current trade list and selection
      trades.value = []
      selectedTradeId.value = null
      if (newSellerId) await fetchTrades(newSellerId)
    })

    onMounted(async () => {
      await fetchSellers()
      // If a seller already selected (e.g., persisted), load trades
      if (selectedSellerId.value) {
        await fetchTrades(selectedSellerId.value)
      }
    })

    return {
      sellers,
      trades,
      sellersLoading,
      tradesLoading,
      selectedSellerId,
      selectedTradeId,
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
  },
  methods: {
    /**
     * onModalShown
     * Attach a keydown listener while modal is open to support Ctrl+Enter shortcut.
     */
    onModalShown(): void {
      document.addEventListener('keydown', this.onKeydown as any)
    },
    /**
     * onOpenLoan
     * Called by IdLinkCell via data-grid when user clicks the ID and
     * openMode==='modal'. Opens the BootstrapVue Next modal and stores payload.
     */
    onOpenLoan(payload: { id: string; row: any; addr?: string }): void {
      this.selectedId = payload?.id ?? null
      this.selectedRow = payload?.row ?? null
      this.selectedAddr = payload?.addr ?? null
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
  },
  mounted() {
    // this.useMeta({
    //   title: "Acquisitions Dashboard",
    // });
  }
};
</script>
