<template>
  <!--
    Root dashboard wrapper uses the shared Hyper UI Layout so we inherit the
    topbar, sidebar, and global styles. All content below is the internal
    dashboard page content specific to the homepage.
  -->
  <Layout>
    <!-- 
      Compact Header Section 
      - Greeting + AI Assistant in unified hero area
      - Tight vertical rhythm for professional feel
    -->
    <div class="dashboard-hero mb-3 pt-2">
      <!-- Greeting - compact and elegant -->
      <h2 class="greeting-title mb-2 text-center">{{ greeting }}!</h2>
      
      <!-- AI Chat Widget - centered for better visual balance -->
      <div class="ai-widget-wrapper mx-auto">
        <AIChatWidget />
      </div>
    </div>

    <!-- Stats Row - Key metrics tiles (minimal top margin as hero provides context) -->
    <StatsWidget @open-pipeline="showPipelineModal = true" class="mb-3" />

    <!-- Calendar Section - Full width calendar with event list -->
    <HomeCalendarWidget @open-asset-modal="onOpenAssetModal" class="mb-3" />

    <!-- Secondary Content Row - Recent Activity and Quick Links -->
    <b-row class="g-3">
      <!-- Recent Activity - Full width on smaller screens -->
      <b-col cols="12" lg="8">
        <div class="card h-100">
          <div class="card-header d-flex justify-content-between align-items-center py-2">
            <h6 class="mb-0 fw-semibold text-uppercase letter-spacing-1">Recent Activity</h6>
            <button type="button" class="btn btn-sm btn-outline-primary" @click="goToActivity">View All</button>
          </div>
          <div class="card-body py-2" style="max-height: 280px; overflow-y: auto;">
            <div v-if="isLoadingRecentActivity" class="text-center py-3">
              <div class="spinner-border spinner-border-sm text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            <div v-else>
              <ul v-if="recentActivity.length" class="list-unstyled mb-0">
                <li v-for="(evt, idx) in recentActivity" :key="`evt-${idx}`" class="d-flex align-items-start py-2 border-bottom">
                  <i class="mdi mdi-checkbox-blank-circle-outline text-primary me-2 mt-1 small"></i>
                  <div class="flex-grow-1">
                    <div class="fw-semibold small">{{ evt.title }}</div>
                    <div v-if="evt.message" class="text-muted small">{{ evt.message }}</div>
                  </div>
                  <small class="text-muted ms-2 flex-shrink-0">{{ evt.when }}</small>
                </li>
              </ul>
              <div v-else class="text-muted small py-3 text-center">No recent activity</div>
            </div>
          </div>
        </div>
      </b-col>

      <!-- Quick Links / Getting Started - Condensed sidebar -->
      <b-col cols="12" lg="4">
        <div class="card h-100">
          <div class="card-header py-2">
            <h6 class="mb-0 fw-semibold text-uppercase letter-spacing-1">Quick Links</h6>
          </div>
          <div class="card-body py-2">
            <div class="d-grid gap-2">
              <button type="button" class="btn btn-light btn-sm text-start d-flex align-items-center" @click="$router.push('/am/asset-grid')">
                <i class="mdi mdi-home-city-outline me-2 text-primary"></i>
                <span>Asset Inventory</span>
                <i class="mdi mdi-chevron-right ms-auto text-muted"></i>
              </button>
              <button type="button" class="btn btn-light btn-sm text-start d-flex align-items-center" @click="$router.push('/acq/trades')">
                <i class="mdi mdi-swap-horizontal-bold me-2 text-primary"></i>
                <span>Active Trades</span>
                <i class="mdi mdi-chevron-right ms-auto text-muted"></i>
              </button>
              <button type="button" class="btn btn-light btn-sm text-start d-flex align-items-center" @click="$router.push('/reports')">
                <i class="mdi mdi-chart-bar me-2 text-primary"></i>
                <span>Reports</span>
                <i class="mdi mdi-chevron-right ms-auto text-muted"></i>
              </button>
              <button type="button" class="btn btn-light btn-sm text-start d-flex align-items-center" @click="$router.push('/crm/partners')">
                <i class="mdi mdi-account-group-outline me-2 text-primary"></i>
                <span>Trading Partners</span>
                <i class="mdi mdi-chevron-right ms-auto text-muted"></i>
              </button>
            </div>
          </div>
        </div>
      </b-col>
    </b-row>
  </Layout>
  <!-- End Layout wrapper -->
  
  <!-- Financial Ticker - Only shown on home page -->
  <FinancialTicker />

  <b-modal
    v-model="showPipelineModal"
    title="My Pipeline"
    size="xl"
    hide-footer
  >
    <PipelineWidget />
  </b-modal>

  <!-- EXACT copy from asset-grid.vue: Loan-Level Modal -->
  <b-modal
    v-model="showAssetModal"
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
        <h5 class="modal-title mb-0">
          <div class="lh-sm">
            <span class="fw-bold text-dark">{{ modalIdText }}</span>
            <span v-if="modalTradeText" class="fw-bold text-dark ms-1">/ {{ modalTradeText }}</span>
          </div>
          <div class="text-muted lh-sm"><span class="fw-bold text-dark">{{ modalAddrText }}</span></div>
        </h5>
        <div class="ms-auto">
          <button
            type="button"
            class="btn btn-sm btn-primary"
            @click="openFullPage"
            title="Open full page (Ctrl + Enter)"
            aria-label="Open full page"
          >
            ⤢ Full Page
          </button>
        </div>
      </div>
    </template>
    <LoanLevelIndex
      :assetHubId="selectedId"
      :row="selectedRow"
      :address="selectedAddr"
      :standalone="false"
    />
  </b-modal>
</template>

<script lang="ts">
// Import the shared Layout at the top-level per code standards
import Layout from "@/components/layouts/layout.vue";
// Financial ticker tape - auto-scrolling market indicators (home page only)
import FinancialTicker from '@/components/FinancialTicker.vue'
// Condensed calendar widget for homepage (modular, reusable)
import HomeCalendarWidget from '@/components/widgets/HomeCalendarWidget.vue'
// Stats widget - key metrics tiles (Assets, Tasks, Brokers, Docs)
import StatsWidget from './components/StatsWidget.vue'
// Pipeline widget - asset pipeline stages by outcome track (FC, REO, etc.)
import PipelineWidget from './components/PipelineWidget.vue'
// AI Chat widget - conversational interface for company data queries
import AIChatWidget from './components/AIChatWidget.vue'
// Asset Management loan-level modal (copied from asset-grid.vue)
import LoanLevelIndex from '@/views/am_module/loanlvl_index.vue'
// Django auth store for user data
import { useDjangoAuthStore } from '@/stores/djangoAuth'
import http from '@/lib/http'

type ActivityRow = {
  id: string
  source: string
  created_at: string
  title: string
  message: string
}

type RecentActivityItem = {
  title: string
  message?: string
  when: string
}

function formatRelativeTime(dateStr: string): string {
  if (!dateStr) return ''
  try {
    const date = new Date(dateStr)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffSec = Math.floor(diffMs / 1000)
    const diffMin = Math.floor(diffSec / 60)
    const diffHr = Math.floor(diffMin / 60)
    const diffDay = Math.floor(diffHr / 24)

    if (diffSec < 60) return 'Just now'
    if (diffMin < 60) return `${diffMin} min ago`
    if (diffHr < 24) return `${diffHr} hr ago`
    if (diffDay < 7) return `${diffDay} day${diffDay > 1 ? 's' : ''} ago`

    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
    })
  } catch {
    return dateStr
  }
}

export default {
  // Explicit component name for devtools and tracing
  name: "HomePage",
  // Register child components locally
  components: {
    Layout,
    FinancialTicker,
    HomeCalendarWidget,
    StatsWidget,
    PipelineWidget,
    AIChatWidget,
    LoanLevelIndex,
  },
  // Options API state for simplicity and broad compatibility across the app
  data() {
    return {
      recentActivity: [] as RecentActivityItem[],
      isLoadingRecentActivity: false,
      showPipelineModal: false,
      // EXACT copy from asset-grid.vue modal state
      showAssetModal: false,
      selectedId: null as string | number | null,
      selectedRow: null as any,
      selectedAddr: null as string | null,
    };
  },
  async mounted() {
    await this.loadRecentActivity()
  },
  computed: {
    /**
     * greeting: Personalized time-based greeting with user's first name
     * Returns "Good Morning/Afternoon/Evening [FirstName]"
     * Morning: 5am-11:59am, Afternoon: 12pm-4:59pm, Evening: 5pm-4:59am
     */
    greeting(): string {
      const authStore = useDjangoAuthStore();
      const firstName = authStore.user?.first_name || 'User';
      
      // Get current hour (0-23)
      const hour = new Date().getHours();
      
      // Determine time of day
      let timeOfDay = 'Evening';
      if (hour >= 5 && hour < 12) {
        timeOfDay = 'Morning';
      } else if (hour >= 12 && hour < 17) {
        timeOfDay = 'Afternoon';
      }
      
      return `Good ${timeOfDay}, ${firstName}`;
    },
    
    // EXACT copy from asset-grid.vue modal computed properties
    modalIdText(): string {
      const servicerId = this.selectedRow?.servicer_id ?? this.selectedRow?.asset_hub?.servicer_id
      if (servicerId != null && servicerId !== '') return String(servicerId)
      const hubId = this.selectedRow?.asset_hub_id ?? this.selectedRow?.asset_hub?.id
      if (hubId != null && hubId !== '') return String(hubId)
      return this.selectedId != null ? String(this.selectedId) : 'Asset'
    },
    modalTradeText(): string {
      const rawTrade = this.selectedRow?.trade_name ?? this.selectedRow?.tradeName ?? ''
      return rawTrade ? String(rawTrade).trim() : ''
    },
    modalAddrText(): string {
      const r: any = this.selectedRow || {}
      const street = String(r.street_address ?? '').trim()
      const city = String(r.city ?? '').trim()
      const state = String(r.state ?? '').trim()
      const locality = [city, state].filter(Boolean).join(', ')
      const built = [street, locality].filter(Boolean).join(', ')
      if (built) return built
      const rawAddr = this.selectedAddr ? String(this.selectedAddr) : ''
      return rawAddr.replace(/,?\s*\d{5}(?:-\d{4})?$/, '')
    }
  },
  methods: {
    async loadRecentActivity() {
      this.isLoadingRecentActivity = true
      try {
        const res = await http.get('/core/activity/?limit=8')
        const rows: ActivityRow[] = (res as any)?.data || []

        this.recentActivity = (rows || []).map((row: ActivityRow) => {
          const msg = (row.message || '').trim()
          return {
            title: row.title || 'Activity',
            message: msg ? msg : undefined,
            when: formatRelativeTime(row.created_at),
          }
        })
      } catch (e) {
        console.error('Failed to load recent activity:', e)
        this.recentActivity = []
      } finally {
        this.isLoadingRecentActivity = false
      }
    },
    goToActivity() {
      this.$router.push('/pages/activity')
    },
    
    // EXACT copy from asset-grid.vue modal methods
    onModalShown(): void {
      document.addEventListener('keydown', this.onKeydown as any)
    },
    onModalHidden(): void {
      document.removeEventListener('keydown', this.onKeydown as any)
      this.selectedId = null
      this.selectedRow = null
      this.selectedAddr = null
    },
    onKeydown(e: KeyboardEvent): void {
      if (e.ctrlKey && (e.key === 'Enter' || e.code === 'Enter')) {
        e.preventDefault()
        this.openFullPage()
      }
    },
    openFullPage(): void {
      if (!this.selectedId) return
      const query: any = { id: this.selectedId }
      if (this.selectedAddr) query.addr = this.selectedAddr
      query.module = 'am'
      this.showAssetModal = false
      this.$router.push({ path: '/loanlvl/products-details', query })
    },
    
    // Handle calendar event click to open asset modal
    onOpenAssetModal(payload: { id: string | number; row: any; addr?: string }): void {
      console.log('[Home Dashboard] onOpenAssetModal called', payload);
      this.selectedId = payload.id
      // CRITICAL: Set selectedRow to null so LoanLevelIndex fetches the asset data by ID
      // The calendar event object (payload.row) has calendar fields (title, date, category),
      // NOT asset fields (street_address, current_balance, etc.) that LoanLevelIndex needs.
      // When row is null, LoanLevelIndex uses assetHubId to fetch the full asset data.
      this.selectedRow = null
      this.selectedAddr = payload.addr || null
      console.log('[Home Dashboard] Opening modal with:', {
        selectedId: this.selectedId,
        selectedRow: this.selectedRow,
        selectedAddr: this.selectedAddr
      });
      this.showAssetModal = true
    },
  },
};
</script>

<style scoped>
/**
 * WHAT: Dashboard Hero Section Styles
 * WHY: Create a compact, elegant header area with greeting + AI assistant
 * HOW: Minimal padding, unified background treatment
 */

/* Hero wrapper - unified visual section with minimal top padding */
.dashboard-hero {
  padding-top: 0.5rem;
}

/* Greeting - compact and elegant, centered */
.greeting-title {
  font-size: 1.75rem;
  font-weight: 600;
  color: var(--bs-body-color);
  margin: 0;
  line-height: 1.2;
  text-align: center;
}

/* AI Widget wrapper - constrained width, centered */
.ai-widget-wrapper {
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}

/* Center the input text inside AI widget */
.ai-widget-wrapper :deep(.form-control) {
  text-align: center;
}

/* Reset text alignment when user starts typing */
.ai-widget-wrapper :deep(.form-control:focus) {
  text-align: left;
}

/* Letter spacing utility */
.letter-spacing-1 {
  letter-spacing: 0.5px;
  font-size: 0.7rem;
}

/* Tighter card headers */
:deep(.card-header) {
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
}

/* Quick links hover effect */
.btn-light:hover {
  background-color: var(--bs-light);
  transform: translateX(2px);
  transition: transform 0.15s ease;
}
</style>

