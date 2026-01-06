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
    <StatsWidget
      :followupCount="followupAssetCount"
      :tradesCount="tradesCount"
      @open-pipeline="showPipelineModal = true"
      @open-followups="openFollowupsModal"
      @open-trades="openTradesModal"
      class="mb-3"
    />

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
    dialog-class="modal-dialog-centered"
    hide-footer
  >
    <PipelineWidget />
  </b-modal>

  <b-modal
    v-model="showFollowupsModal"
    title="My Follow-ups"
    size="xl"
    dialog-class="modal-dialog-centered"
    hide-footer
  >
    <div v-if="followupsLoading" class="text-center py-3">
      <div class="spinner-border spinner-border-sm text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
    <div v-else>
      <div v-if="followupsError" class="text-danger small mb-2">{{ followupsError }}</div>
      <ul v-if="followupAssets.length" class="list-group">
        <li
          v-for="asset in followupAssets"
          :key="`followup-asset-${asset.asset_hub_id}`"
          class="list-group-item d-flex align-items-start"
        >
          <div class="flex-grow-1">
            <div class="fw-semibold">
              <span class="me-2">{{ asset.asset_hub_id }}</span>
              <span>{{ asset.address }}</span>
            </div>
            <div v-if="asset.next_date" class="text-muted small">
              Next: {{ asset.next_date }}<span v-if="asset.next_title"> — {{ asset.next_title }}</span>
            </div>
          </div>
          <span class="badge bg-primary ms-2 align-self-center">{{ asset.count }}</span>
          <button
            type="button"
            class="btn btn-sm btn-outline-primary ms-2 align-self-center"
            @click="openAssetFromFollowups(asset.asset_hub_id, asset.address)"
          >
            Open
          </button>
        </li>
      </ul>
      <div v-else class="text-muted small">No active follow-ups.</div>
    </div>
  </b-modal>

  <b-modal
    v-model="showTradesModal"
    title="Active Trades"
    size="lg"
    dialog-class="modal-dialog-centered"
    hide-footer
  >
    <div v-if="tradesLoading" class="text-center py-4">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="text-muted mt-2 mb-0">Loading trades...</p>
    </div>
    <div v-else>
      <div v-if="tradesError" class="alert alert-danger mb-3">
        <i class="mdi mdi-alert-circle-outline me-2"></i>{{ tradesError }}
      </div>
      <div v-if="trades.length" class="trades-list">
        <div
          v-for="trade in trades"
          :key="`trade-${trade.trade_id}`"
          class="trade-card"
          @click="openTradeAssets(trade)"
        >
          <div class="trade-card-header">
            <div class="trade-info">
              <div class="d-flex align-items-center justify-content-between w-100">
                <div>
                  <h6 class="trade-name mb-1">
                    <i class="mdi mdi-swap-horizontal me-2 text-primary"></i>
                    {{ trade.trade_name }}
                  </h6>
                  <div class="seller-name text-muted">
                    <i class="mdi mdi-domain me-1"></i>
                    {{ trade.seller_name }}
                  </div>
                </div>
                <div class="d-flex align-items-center gap-3">
                  <div class="asset-count-badge">
                    <span class="count">{{ trade.active_asset_count || 0 }}</span>
                    <span class="label">Active Assets</span>
                  </div>
                  <span class="view-assets-link">
                    View Assets
                    <i class="mdi mdi-arrow-right ms-1"></i>
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="text-center py-5">
        <i class="mdi mdi-folder-open-outline text-muted" style="font-size: 3rem;"></i>
        <p class="text-muted mt-2 mb-0">No active trades found</p>
      </div>
    </div>
  </b-modal>

  <!-- Trade Assets Grid Modal - Reuses full AssetGrid component -->
  <b-modal
    v-model="showTradeGridModal"
    :title="selectedTrade ? `${selectedTrade.trade_name} - Assets` : 'Trade Assets'"
    size="xl"
    dialog-class="modal-dialog-centered"
    hide-footer
    body-class="p-0"
  >
    <div v-if="selectedTrade" class="p-3">
      <div class="mb-2 text-muted small">
        <i class="mdi mdi-domain me-1"></i>{{ selectedTrade.seller_name }}
        <span class="mx-2">•</span>
        <i class="mdi mdi-package-variant me-1"></i>{{ selectedTrade.active_asset_count || 0 }} Active Assets
      </div>
      <AssetGrid 
        :key="`trade-grid-${selectedTrade.trade_id}`"
        :filterTradeName="selectedTrade.trade_name"
        :filterSellerName="selectedTrade.seller_name"
        :filterActiveOnly="true"
      />
    </div>
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
      @row-loaded="onRowLoaded"
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
import LoanLevelIndex from '@/views/am_module/loanlvl_index.vue'
import AssetGrid from '@/views/dashboards/asset_mgmt/asset-grid.vue'
import { useDjangoAuthStore } from '@/stores/djangoAuth'
import http from '@/lib/http'

type ActivityRow = {
  id: string
  source: string
  created_at: string
  title: string
  message: string
}

function todayIso(): string {
  const d = new Date()
  const yyyy = d.getFullYear()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${yyyy}-${mm}-${dd}`
}

type FollowupRow = {
  id: number
  title: string
  date: string
  time: string
  description: string
  category: string
  asset_hub: number | null
  asset_hub_id?: number | null
  reason?: string | null
}

type FollowupAssetRow = {
  asset_hub_id: number
  address: string
  count: number
  next_date: string
  next_title: string
}

type TradeRow = {
  seller_id: number
  seller_name: string
  trade_id: number
  trade_name: string
  status: string
  active_asset_count?: number
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
    AssetGrid,
  },
  // Options API state for simplicity and broad compatibility across the app
  data() {
    return {
      recentActivity: [] as RecentActivityItem[],
      isLoadingRecentActivity: false,
      showPipelineModal: false,
      showFollowupsModal: false,
      followupAssetCount: 0,
      followupsLoading: false,
      followupsError: '',
      followupAssets: [] as FollowupAssetRow[],
      showTradesModal: false,
      tradesCount: 0,
      tradesLoading: false,
      tradesError: '',
      trades: [] as TradeRow[],
      showTradeGridModal: false,
      selectedTrade: null as TradeRow | null,
      // EXACT copy from asset-grid.vue modal state
      showAssetModal: false,
      selectedId: null as string | number | null,
      selectedRow: null as any,
      selectedAddr: null as string | null,
    };
  },
  async mounted() {
    await this.loadRecentActivity()
    this.loadActiveFollowups()
    this.loadActiveTrades()
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

    async loadActiveFollowups() {
      this.followupsLoading = true
      this.followupsError = ''
      try {
        const resp = await http.get('/core/calendar/events/custom/', {
          params: {
            is_reminder: true,
            start_date: todayIso(),
          },
        })

        const rows: FollowupRow[] = Array.isArray((resp as any)?.data) ? (resp as any).data : []
        const grouped = new Map<number, FollowupRow[]>()

        for (const r of rows) {
          const rawId = (r as any).asset_hub_id ?? (r as any).asset_hub
          const idNum = rawId != null ? Number(rawId) : NaN
          if (!Number.isFinite(idNum)) continue
          const bucket = grouped.get(idNum) ?? []
          bucket.push(r)
          grouped.set(idNum, bucket)
        }

        const assetIds = Array.from(grouped.keys()).sort((a, b) => a - b)

        const assets = await Promise.all(
          assetIds.map(async (id) => {
            try {
              const res = await http.get(`/am/assets/${id}/`)
              const row = (res as any)?.data ?? {}
              const street = String(row.street_address ?? '').trim()
              const city = String(row.city ?? '').trim()
              const state = String(row.state ?? '').trim()
              const zip = String(row.zip ?? '').trim()
              const locality = [city, state].filter(Boolean).join(', ')
              const address = [street, locality, zip].filter(Boolean).join(' ')

              const fups = (grouped.get(id) ?? []).slice().sort((a, b) => String(a.date).localeCompare(String(b.date)))
              const next = fups[0]

              return {
                asset_hub_id: id,
                address: address || 'No address',
                count: fups.length,
                next_date: String((next as any)?.date ?? ''),
                next_title: String((next as any)?.title ?? ''),
              } as FollowupAssetRow
            } catch {
              const fups = (grouped.get(id) ?? []).slice().sort((a, b) => String(a.date).localeCompare(String(b.date)))
              const next = fups[0]
              return {
                asset_hub_id: id,
                address: 'No address',
                count: fups.length,
                next_date: String((next as any)?.date ?? ''),
                next_title: String((next as any)?.title ?? ''),
              } as FollowupAssetRow
            }
          })
        )

        const sorted = assets
          .slice()
          .sort((a, b) => String(a.next_date).localeCompare(String(b.next_date)) || a.asset_hub_id - b.asset_hub_id)

        this.followupAssets = sorted
        this.followupAssetCount = sorted.length
      } catch (e) {
        console.error('[Home Dashboard] loadActiveFollowups failed', e)
        this.followupAssets = []
        this.followupAssetCount = 0
        this.followupsError = 'Failed to load follow-ups.'
      } finally {
        this.followupsLoading = false
      }
    },

    openFollowupsModal() {
      this.showFollowupsModal = true
      if (!this.followupsLoading && this.followupAssets.length === 0) {
        this.loadActiveFollowups()
      }
    },

    openAssetFromFollowups(assetHubId: number, address: string) {
      this.selectedId = assetHubId
      this.selectedRow = null
      this.selectedAddr = address || null
      this.showFollowupsModal = false
      this.showAssetModal = true
    },

    async loadActiveTrades() {
      this.tradesLoading = true
      this.tradesError = ''
      try {
        const resp = await http.get('/acq/trades/with-active-assets/')
        const rows: TradeRow[] = Array.isArray((resp as any)?.data) ? (resp as any).data : []
        
        // Endpoint returns trades with ACTIVE assets (based on AssetDetails.asset_status)
        this.trades = rows.sort((a, b) => 
          a.seller_name.localeCompare(b.seller_name) || a.trade_name.localeCompare(b.trade_name)
        )
        this.tradesCount = rows.length
      } catch (e) {
        console.error('[Home Dashboard] loadActiveTrades failed', e)
        this.trades = []
        this.tradesCount = 0
        this.tradesError = 'Failed to load trades.'
      } finally {
        this.tradesLoading = false
      }
    },

    openTradesModal() {
      this.showTradesModal = true
      if (!this.tradesLoading && this.trades.length === 0) {
        this.loadActiveTrades()
      }
    },

    openTradeAssets(trade: TradeRow) {
      this.showTradesModal = false
      this.selectedTrade = trade
      this.showTradeGridModal = true
    },

    closeTradeGridModal() {
      this.showTradeGridModal = false
      this.selectedTrade = null
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
      // Set row to null so LoanLevelIndex fetches the complete asset data by ID
      // Calendar event object doesn't have trade_name, street_address, city, state, etc.
      this.selectedRow = null
      this.selectedAddr = payload.addr || null
      console.log('[Home Dashboard] Opening modal with:', {
        selectedId: this.selectedId,
        selectedRow: this.selectedRow,
        selectedAddr: this.selectedAddr
      });
      this.showAssetModal = true
    },

    // Handle row-loaded event from LoanLevelIndex
    onRowLoaded(row: any): void {
      console.log('[Home Dashboard] onRowLoaded called', row);
      // Update selectedRow with the fetched asset data so modal header displays correctly
      this.selectedRow = row
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

/* Quick links hover effect */
.btn-light:hover {
  background-color: var(--bs-light);
  transform: translateX(2px);
  transition: transform 0.15s ease;
}

/* Trade cards styling */
.trades-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.trade-card {
  background: #FDFBF7;
  border: 1px solid #e3e6e8;
  border-radius: 8px;
  padding: 0.625rem 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.trade-card:hover {
  border-color: #D4AF37;
  box-shadow: 0 2px 8px rgba(212, 175, 55, 0.15);
  transform: translateY(-1px);
}

.trade-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0;
}

.trade-info {
  flex: 1;
}

.trade-name {
  font-size: 1rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
}

.seller-name {
  font-size: 0.875rem;
  display: flex;
  align-items: center;
}

.trade-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.asset-count-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: #5A8A95;
  color: white;
  padding: 0.35rem 0.6rem;
  border-radius: 4px;
  min-width: 70px;
}

.asset-count-badge .count {
  font-size: 1rem;
  font-weight: 600;
  line-height: 1;
}

.asset-count-badge .label {
  font-size: 0.625rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  opacity: 0.9;
  margin-top: 2px;
}

.view-assets-link {
  color: #D4AF37;
  font-size: 0.875rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.trade-card:hover .view-assets-link {
  color: #b8941f;
  transform: translateX(3px);
}
</style>

