<template>
  <Layout>
    <b-row>
      <b-col class="col-12">
        <div class="page-title-box">
          <div class="page-title-right">
            <!-- Removed refresh button/form -->
          </div>
          <h4 class="page-title">Acquisitions</h4>
        </div>
      </b-col>
    </b-row>

    <!-- Top metrics: four tiles across -->
    <b-row class="g-3">
      <b-col xl="3" lg="6">
        <div class="card tilebox-one">
          <div class="card-body">
            <i class="uil uil-users-alt float-end"></i>
            <h6 class="text-uppercase mt-0">Active Users</h6>
            <h2 class="my-2" id="active-users-count">121</h2>
            <p class="mb-0 text-muted">
              <span class="text-success me-2"><span class="mdi mdi-arrow-up-bold"></span> 5.27%</span>
              <span class="text-nowrap">Since last month</span>
            </p>
          </div>
        </div>
      </b-col>

      <b-col xl="3" lg="6">
        <div class="card tilebox-one">
          <div class="card-body">
            <i class="uil uil-window-restore float-end"></i>
            <h6 class="text-uppercase mt-0">Views per minute</h6>
            <h2 class="my-2" id="active-views-count">560</h2>
            <p class="mb-0 text-muted">
              <span class="text-danger me-2"><span class="mdi mdi-arrow-down-bold"></span> 1.08%</span>
              <span class="text-nowrap">Since previous week</span>
            </p>
          </div>
        </div>
      </b-col>

      <b-col xl="3" lg="6">
        <div class="card tilebox-one">
          <div class="card-body">
            <i class="uil uil-chart-line float-end"></i>
            <h6 class="text-uppercase mt-0">New Sessions</h6>
            <h2 class="my-2" id="new-sessions-count">2,430</h2>
            <p class="mb-0 text-muted">
              <span class="text-success me-2"><span class="mdi mdi-arrow-up-bold"></span> 3.12%</span>
              <span class="text-nowrap">Since last week</span>
            </p>
          </div>
        </div>
      </b-col>

      <b-col xl="3" lg="6">
        <div class="card tilebox-one">
          <div class="card-body">
            <i class="uil uil-chart-down float-end"></i>
            <h6 class="text-uppercase mt-0">Bounce Rate</h6>
            <h2 class="my-2" id="bounce-rate-count">32%</h2>
            <p class="mb-0 text-muted">
              <span class="text-danger me-2"><span class="mdi mdi-arrow-down-bold"></span> 0.84%</span>
              <span class="text-nowrap">Since last month</span>
            </p>
          </div>
        </div>
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
        <Views />
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

    <!-- Full-width AG Grid data table row -->
    <b-row>
      <b-col class="col-12">
        <!-- Pass behavior control to the grid: modal-first with onOpenLoan callback -->
        <DataGrid :open-mode="'modal'" :open-loan="onOpenLoan" />
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
import Views from "@/views/dashboards/acquisitions/views.vue";
import Browser from "@/views/dashboards/acquisitions/browser.vue";
import System from "@/views/dashboards/acquisitions/system.vue";
import Channel from "@/views/dashboards/acquisitions/channel.vue";
import Media from "@/views/dashboards/acquisitions/media.vue";
import EngagementOverview from "@/views/dashboards/acquisitions/engagement-overview.vue";
import VectorMap from "@/views/dashboards/acquisitions/vectorMap.vue";
// AG Grid: modular data grid component for acquisitions dashboard
import DataGrid from "@/views/dashboards/acquisitions/data-grid.vue";
// BootstrapVue Next modal component (Vue 3 compatible)
import { BModal } from 'bootstrap-vue-next';
// Centralized loan-level wrapper used for both full-page and modal
import LoanLevelIndex from '@/views/acq_module/loanlvl/loanlvl_index.vue'

export default {
  components: {
    VectorMap,
    EngagementOverview,
    Media,
    Channel,
    System,
    Browser,
    Views,
    Overview,
    // Register AG Grid data grid component
    DataGrid,
    Layout,
    // Register modal + loan-level wrapper
    BModal,
    LoanLevelIndex,
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
