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
    <div class="dashboard-hero mb-3 pt-4">
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
    <div class="mb-3">
      <HomeCalendarWidget @open-asset-modal="onOpenAssetModal" />
    </div>

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
    dialog-class="modal-dialog-centered followups-modal"
    hide-footer
    body-class="p-0 followups-modal-body"
  >
    <div v-if="followupsLoading" class="text-center py-3">
      <div class="spinner-border spinner-border-sm text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
    <div v-else class="followups-container">
      <div v-if="followupsError" class="alert alert-danger mb-3">
        <i class="mdi mdi-alert-circle-outline me-2"></i>{{ followupsError }}
      </div>
      
      <!-- Summary Stats Bar -->
      <div v-if="followupAssets.length" class="followups-summary mb-4">
        <div class="row g-3">
          <div class="col-3 text-center">
            <div class="summary-stat overdue">
              <div class="stat-number">{{ filteredFollowups.filter(f => f.days_until < 0).length }}</div>
              <div class="stat-label">Overdue</div>
            </div>
          </div>
          <div class="col-3 text-center">
            <div class="summary-stat week">
              <div class="stat-number">{{ filteredFollowups.filter(f => f.days_until >= 0 && f.days_until <= 7).length }}</div>
              <div class="stat-label">This Week</div>
            </div>
          </div>
          <div class="col-3 text-center">
            <div class="summary-stat month">
              <div class="stat-number">{{ filteredFollowups.filter(f => f.days_until > 7 && f.days_until <= 30).length }}</div>
              <div class="stat-label">This Month</div>
            </div>
          </div>
          <div class="col-3 text-center">
            <div class="summary-stat future">
              <div class="stat-number">{{ filteredFollowups.filter(f => f.days_until > 30).length }}</div>
              <div class="stat-label">Future</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Filters & Controls -->
      <div v-if="followupAssets.length" class="followups-controls mb-4">
        <div class="row g-3 align-items-end">
          <div class="col-md-3">
            <label class="form-label small fw-semibold text-muted">FILTER BY STATUS</label>
            <select v-model="selectedStatusFilter" class="form-select form-select-sm">
              <option value="all">All Follow-ups</option>
              <option value="overdue">Overdue</option>
              <option value="urgent">Urgent (≤7 days)</option>
              <option value="active">Active (≤30 days)</option>
              <option value="upcoming">Upcoming (31-60 days)</option>
              <option value="future">Future (61+ days)</option>
            </select>
          </div>
          <div class="col-md-3">
            <label class="form-label small fw-semibold text-muted">FILTER BY REASON</label>
            <select v-model="selectedReasonFilter" class="form-select form-select-sm">
              <option value="all">All Reasons</option>
              <option value="escrow">Escrow</option>
              <option value="reo">REO</option>
              <option value="legal">Legal</option>
              <option value="inspection">Inspection</option>
            </select>
          </div>
          <div class="col-md-4">
            <label class="form-label small fw-semibold text-muted">SEARCH</label>
            <input 
              v-model="searchQuery" 
              type="text" 
              class="form-control form-control-sm" 
              placeholder="Search by ID, address, or trade..."
            >
          </div>
          <div class="col-md-2">
            <label class="form-label small fw-semibold text-muted">SORT BY</label>
            <select v-model="selectedSort" class="form-select form-select-sm">
              <option value="date">Due Date</option>
              <option value="priority">Priority</option>
              <option value="trade">Trade Name</option>
              <option value="servicer">Servicer ID</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Follow-ups List -->
      <div v-if="filteredFollowups.length" class="followups-list">
        <div 
          v-for="asset in filteredFollowups" 
          :key="`followup-${asset.asset_hub_id}`"
          class="followup-card"
          :class="getUrgencyClass(asset.days_until)"
        >
          <div class="followup-header">
            <div class="followup-priority">
              <div class="priority-indicator" :class="getPriorityClass(asset.days_until)">
                <i class="mdi" :class="getPriorityIcon(asset.days_until)"></i>
              </div>
              <div class="followup-meta">
                <div class="followup-header-line d-flex align-items-center justify-content-between mb-1">
                  <div class="followup-id">{{ asset.servicer_id }}</div>
                  <div class="followup-address-header">
                    <i class="mdi mdi-map-marker-outline me-1"></i>
                    {{ getFullAddress(asset) }}
                  </div>
                </div>
                <div class="followup-trade-header">
                  <i class="mdi mdi-briefcase-outline me-1"></i>
                  <span class="trade-name">{{ asset.trade_name || 'No Trade Assigned' }}</span>
                </div>
              </div>
            </div>
            <div class="followup-actions">
              <span v-if="asset.count > 1" class="badge bg-warning text-dark me-1">
                {{ asset.count }} tasks
              </span>
              <div class="btn-group">
                <button 
                  class="btn btn-sm btn-outline-success d-flex align-items-center justify-content-center"
                  @click="markComplete(asset.asset_hub_id)"
                  :disabled="!asset.followup_event_source_id || markingAssetId === asset.asset_hub_id"
                  title="Mark Complete"
                >
                  <span v-if="markingAssetId === asset.asset_hub_id" class="spinner-border spinner-border-sm text-success"></span>
                  <i v-else class="mdi mdi-check"></i>
                </button>
                <button 
                  class="btn btn-sm btn-outline-primary"
                  @click="openAssetFromFollowups(asset.asset_hub_id, asset.address)"
                  title="View Details"
                >
                  <i class="mdi mdi-eye"></i>
                </button>
              </div>
            </div>
          </div>
          
          <div class="followup-content">
            <div v-if="asset.next_reason" class="followup-reason mb-1">
              <i class="mdi mdi-tag-outline me-1"></i>
              <span class="reason-badge" :class="getReasonClass(asset.next_reason)">
                {{ asset.next_reason }}
              </span>
            </div>
            
            <!-- Status and Progress -->
            <div class="p-2 mt-1 bg-light border rounded">
              <div class="d-flex justify-content-between align-items-center mb-1">
                <span class="fw-semibold text-muted small text-uppercase">Status:</span>
                <span class="badge" :class="getStatusClass(asset.days_until)">
                  {{ getStatusText(asset.days_until) }}
                </span>
              </div>
              <div class="d-flex align-items-center">
                <span class="fw-semibold text-muted small text-uppercase">Due:</span>
                <span class="fw-bold text-primary ms-2">{{ formatDateMMDDYYYY(asset.next_date) }}</span>
                <span class="text-muted small ms-2">{{ getDaysText(asset.days_until) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div v-else class="empty-state">
        <div class="empty-icon">
          <i class="mdi mdi-calendar-check-outline"></i>
        </div>
        <h5 class="empty-title">All caught up!</h5>
        <p class="empty-message">You have no pending follow-ups at this time.</p>
      </div>
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
  servicer_id: string
  trade_name: string | null
  followup_event_source_id: number | null
  city: string | null
  state: string | null
  count: number
  next_date: string
  next_title: string
  next_reason: string | null
  days_until: number
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
      selectedStatusFilter: 'all',
      selectedReasonFilter: 'all',
      searchQuery: '',
      selectedSort: 'date',
      markingAssetId: null as number | null,
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
    },

    // Filtered and sorted follow-ups
    filteredFollowups(): FollowupAssetRow[] {
      let filtered = [...this.followupAssets]
      
      // Status filter
      if (this.selectedStatusFilter !== 'all') {
        filtered = filtered.filter(asset => {
          switch (this.selectedStatusFilter) {
            case 'overdue': return asset.days_until < 0
            case 'urgent': return asset.days_until >= 0 && asset.days_until <= 7
            case 'active': return asset.days_until >= 0 && asset.days_until <= 30
            case 'upcoming': return asset.days_until > 30 && asset.days_until <= 60
            case 'future': return asset.days_until > 60
            default: return true
          }
        })
      }
      
      // Reason filter
      if (this.selectedReasonFilter !== 'all') {
        filtered = filtered.filter(asset => 
          asset.next_reason?.toLowerCase() === this.selectedReasonFilter
        )
      }
      
      // Search filter
      if (this.searchQuery.trim()) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(asset => 
          asset.servicer_id.toLowerCase().includes(query) ||
          asset.address.toLowerCase().includes(query) ||
          (asset.trade_name && asset.trade_name.toLowerCase().includes(query)) ||
          (asset.next_title && asset.next_title.toLowerCase().includes(query))
        )
      }
      
      // Sort
      filtered.sort((a, b) => {
        switch (this.selectedSort) {
          case 'date':
            return a.next_date.localeCompare(b.next_date)
          case 'priority':
            return a.days_until - b.days_until
          case 'trade':
            return (a.trade_name || '').localeCompare(b.trade_name || '')
          case 'servicer':
            return a.servicer_id.localeCompare(b.servicer_id)
          default:
            return 0
        }
      })
      
      return filtered
    },

    // Legacy buckets for backward compatibility
    followups30Days(): FollowupAssetRow[] {
      return this.followupAssets.filter(a => a.days_until <= 30)
    },
    followups60Days(): FollowupAssetRow[] {
      return this.followupAssets.filter(a => a.days_until > 30 && a.days_until <= 60)
    },
    followups90Days(): FollowupAssetRow[] {
      return this.followupAssets.filter(a => a.days_until > 60)
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

    formatDateDMY(dateStr: string): string {
      if (!dateStr) return ''
      const parts = dateStr.split('-')
      if (parts.length !== 3) return dateStr
      return `${parts[1]}/${parts[2]}/${parts[0]}`
    },

    formatDateMMDDYYYY(dateStr: string): string {
      if (!dateStr) return ''
      const parts = dateStr.split('-')
      if (parts.length !== 3) return dateStr
      return `${parts[1]}/${parts[2]}/${parts[0]}` // MM/DD/YYYY
    },

    getFullAddress(asset: FollowupAssetRow): string {
      // WHAT: Combines address with city and state for full display
      // WHY: User requested city and state to be included in address
      // HOW: Concatenates address, city, and state with proper formatting
      let fullAddress = asset.address || ''
      
      // Add city and state if available
      const cityState = []
      if (asset.city) cityState.push(asset.city)
      if (asset.state) cityState.push(asset.state)
      
      if (cityState.length > 0) {
        fullAddress += `, ${cityState.join(', ')}`
      }
      
      return fullAddress
    },

    getUrgencyClass(daysUntil: number): string {
      if (daysUntil <= 7) return 'urgent-high'
      if (daysUntil <= 30) return 'urgent-medium'
      if (daysUntil <= 60) return 'upcoming'
      return 'future'
    },

    getPriorityClass(daysUntil: number): string {
      if (daysUntil <= 7) return 'priority-high'
      if (daysUntil <= 30) return 'priority-medium'
      return 'priority-low'
    },

    getPriorityIcon(daysUntil: number): string {
      if (daysUntil <= 7) return 'mdi-alert-circle'
      if (daysUntil <= 30) return 'mdi-clock-alert-outline'
      return 'mdi-calendar-outline'
    },

    getReasonClass(reason: string): string {
      const reasonMap: Record<string, string> = {
        'escrow': 'reason-escrow',
        'reo': 'reason-reo',
        'legal': 'reason-legal',
        'inspection': 'reason-inspection',
        'default': 'reason-default'
      }
      return reasonMap[reason?.toLowerCase()] || 'reason-default'
    },

    getStatusClass(daysUntil: number): string {
      if (daysUntil < 0) return 'status-overdue'
      if (daysUntil <= 7) return 'status-urgent'
      if (daysUntil <= 30) return 'status-active'
      return 'status-scheduled'
    },

    getStatusText(daysUntil: number): string {
      if (daysUntil < 0) return 'Overdue'
      if (daysUntil <= 7) return 'Urgent'
      if (daysUntil <= 30) return 'Active'
      return 'Scheduled'
    },

    getDaysText(daysUntil: number): string {
      if (daysUntil < 0) return `${Math.abs(daysUntil)} days overdue`
      if (daysUntil === 0) return 'Due today'
      if (daysUntil === 1) return 'Due tomorrow'
      return `${daysUntil} days remaining`
    },

    async markComplete(assetHubId: number): Promise<void> {
      const asset = this.followupAssets.find(a => a.asset_hub_id === assetHubId)
      if (!asset?.followup_event_source_id) {
        console.warn('[Home Dashboard] No follow-up event found for asset', assetHubId)
        return
      }

      if (this.markingAssetId != null) {
        return
      }

      this.markingAssetId = assetHubId
      this.followupsError = ''

      try {
        await http.delete(`/core/calendar/events/custom/${asset.followup_event_source_id}/`)
        await this.loadActiveFollowups()
      } catch (err: any) {
        console.error('[Home Dashboard] markComplete failed', err)
        this.followupsError = 'Failed to mark follow-up complete.'
      } finally {
        this.markingAssetId = null
      }
    },
    goToActivity() {
      this.$router.push('/pages/activity')
    },

    async loadActiveFollowups() {
      // WHAT: Use dedicated follow-ups endpoint with a 120-day window
      // WHY: Optimized specifically for follow-ups and prevents timeout
      this.followupsLoading = true
      this.followupsError = ''
      try {
        const now = new Date()
        const start = new Date(now)
        start.setDate(start.getDate() - 30) // Look back 1 month
        const end = new Date(now)
        end.setDate(end.getDate() + 90)    // Look ahead 3 months

        const startStr = start.toISOString().split('T')[0]
        const endStr = end.toISOString().split('T')[0]

        // WHAT: Use the NEW dedicated follow-ups endpoint
        const resp = await http.get('/core/calendar/followups/', {
          params: {
            start_date: startStr,
            end_date: endStr
          }
        })
        const followupEvents = Array.isArray((resp as any)?.data) ? (resp as any).data : []
        
        const grouped = new Map<number, any[]>()
        const assetInfo = new Map<number, { address: string; servicer_id: string; city: string; state: string }>()

        for (const r of followupEvents) {
          const rawId = (r as any).asset_hub_id ?? (r as any).asset_hub
          const idNum = rawId != null ? Number(rawId) : NaN
          if (!Number.isFinite(idNum)) continue
          
          const bucket = grouped.get(idNum) ?? []
          bucket.push(r)
          grouped.set(idNum, bucket)
          
          if (!assetInfo.has(idNum)) {
            assetInfo.set(idNum, { 
              address: r.address || 'No address',
              servicer_id: r.servicer_id || 'No ID',
              city: r.city || '',
              state: r.state || ''
            })
          }
        }

        const today = new Date()
        today.setHours(0, 0, 0, 0)

        const assetIds = Array.from(grouped.keys())
        const assets = assetIds.map(id => {
          const info = assetInfo.get(id)
          const fups = (grouped.get(id) ?? []).slice().sort((a, b) => String(a.date).localeCompare(String(b.date)))
          const next = fups[0]
          const nextSourceId = next?.source_model === 'CalendarEvent' && next?.source_id ? Number(next.source_id) : null
          
          const nextDate = new Date(next.date)
          nextDate.setHours(0, 0, 0, 0)
          const diffTime = nextDate.getTime() - today.getTime()
          const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

          return {
            asset_hub_id: id,
            address: info?.address || 'No address',
            servicer_id: info?.servicer_id || 'No ID',
            trade_name: next?.trade_name || null,
            city: info?.city || null,
            state: info?.state || null,
            count: fups.length,
            next_date: String(next?.date ?? ''),
            next_title: String(next?.title ?? ''),
            next_reason: next?.reason || null,
            days_until: diffDays,
            followup_event_source_id: nextSourceId,
          } as FollowupAssetRow
        })

        const sorted = assets.sort((a, b) => 
          String(a.next_date).localeCompare(String(b.next_date)) || a.asset_hub_id - b.asset_hub_id
        )

        this.followupAssets = sorted
        this.followupAssetCount = sorted.length
      } catch (e: any) {
        console.error('[Home Dashboard] loadActiveFollowups failed', e)
        this.followupsError = 'Failed to load follow-ups.'
        this.followupAssets = []
        this.followupAssetCount = 0
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
  /* Increased padding for more space between header and greeting */
  padding-top: 2rem;
}

.extra-small {
  font-size: 0.7rem;
}

.bg-soft-primary {
  background-color: rgba(64, 153, 255, 0.1) !important;
}

.bg-soft-info {
  background-color: rgba(57, 196, 255, 0.1) !important;
}

.bg-soft-secondary {
  background-color: rgba(108, 117, 125, 0.1) !important;
}

.list-group-item:hover {
  background-color: rgba(0, 0, 0, 0.01);
}

/* Follow-ups modal - Professional Navy & Gold Design */
.followups-modal {
  max-height: 80vh;
}

.followups-modal .modal-content {
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  background: #FDFBF7; /* Warm White from color palette */
}

.followups-modal-body {
  overflow-y: auto;
  flex: 1;
  max-height: calc(80vh - 120px);
  padding: 0;
}

/* Follow-ups container */
.followups-container {
  padding: 1.5rem;
  background: #FDFBF7; /* Warm White */
}

/* Controls section */
.followups-controls {
  background: linear-gradient(135deg, #F5F3EE 0%, #E9ECEF 100%); /* Cream to Light Gray */
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid #dee2e6;
}

.followups-controls .form-label {
  color: #1B3B5F; /* Primary Navy */
  font-size: 0.75rem;
  letter-spacing: 0.5px;
}

.followups-controls .form-select,
.followups-controls .form-control {
  border: 1px solid #4A6FA5; /* Steel Blue */
  background: #FDFBF7; /* Warm White */
}

.followups-controls .form-select:focus,
.followups-controls .form-control:focus {
  border-color: #D4AF37; /* Accent Gold */
  box-shadow: 0 0 0 0.2rem rgba(212, 175, 55, 0.25);
}

/* Summary stats */
.followups-summary {
  background: linear-gradient(135deg, #F5F3EE 0%, #E9ECEF 100%);
  border-radius: 10px;
  padding: 1rem 1.25rem;
  border: 1px solid #dee2e6;
}

.summary-stat {
  padding: 0.65rem 0.75rem;
  border-radius: 8px;
  background: #FDFBF7;
  box-shadow: 0 2px 4px rgba(27, 59, 95, 0.08);
  border-left: 4px solid transparent;
}

.summary-stat.overdue {
  border-left-color: #B85A3A; /* Burnt Sienna */
  background: linear-gradient(135deg, rgba(184, 90, 58, 0.08) 0%, #FDFBF7 100%);
}

.summary-stat.week {
  border-left-color: #DAA520; /* Goldenrod */
  background: linear-gradient(135deg, rgba(218, 165, 32, 0.08) 0%, #FDFBF7 100%);
}

.summary-stat.month {
  border-left-color: #6B5A7A; /* Muted Plum */
  background: linear-gradient(135deg, rgba(107, 90, 122, 0.08) 0%, #FDFBF7 100%);
}

.summary-stat.future {
  border-left-color: #1B5E20; /* Forest Green */
  background: linear-gradient(135deg, rgba(27, 94, 32, 0.08) 0%, #FDFBF7 100%);
}

.stat-number {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1B3B5F;
  line-height: 1;
}

.stat-label {
  font-size: 0.8rem;
  color: #2C3E50;
  margin-top: 0.1rem;
  font-weight: 500;
}

/* Follow-up cards */
.followups-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.followup-card {
  background: #FDFBF7; /* Warm White */
  border-radius: 12px;
  border: 1px solid #E9ECEF; /* Light Gray */
  padding: 0.65rem;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(27, 59, 95, 0.08); /* Navy shadow */
  margin-bottom: 0.2rem;
}

.followup-card:hover {
  box-shadow: 0 4px 12px rgba(27, 59, 95, 0.15); /* Navy shadow */
  transform: translateY(-1px);
  border-color: #D4AF37; /* Accent Gold */
}

.followup-card.urgent-high {
  border-left: 4px solid #B85A3A; /* Burnt Sienna */
  background: linear-gradient(135deg, rgba(184, 90, 58, 0.08) 0%, #FDFBF7 100%);
}

.followup-card.urgent-medium {
  border-left: 4px solid #DAA520; /* Goldenrod */
  background: linear-gradient(135deg, rgba(218, 165, 32, 0.08) 0%, #FDFBF7 100%);
}

.followup-card.upcoming {
  border-left: 4px solid #6B5A7A; /* Muted Plum */
  background: linear-gradient(135deg, rgba(107, 90, 122, 0.08) 0%, #FDFBF7 100%);
}

.followup-card.future {
  border-left: 4px solid #1B5E20; /* Forest Green */
  background: linear-gradient(135deg, rgba(27, 94, 32, 0.08) 0%, #FDFBF7 100%);
}

/* Follow-up header */
.followup-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
}

.followup-priority {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.priority-indicator {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}

.priority-indicator.priority-high {
  background: #B85A3A; /* Burnt Sienna */
  color: white;
}

.priority-indicator.priority-medium {
  background: #DAA520; /* Goldenrod */
  color: white;
}

.priority-indicator.priority-low {
  background: #6B5A7A; /* Muted Plum */
  color: white;
}

.followup-meta {
  display: flex;
  flex-direction: column;
}

.followup-header-line {
  margin-bottom: 0.25rem;
}

.followup-id {
  font-size: 0.95rem;
  font-weight: 600;
  color: #1B3B5F; /* Primary Navy */
  letter-spacing: 0.5px;
}

.followup-trade-header {
  font-size: 0.9rem;
  color: #4A6FA5; /* Steel Blue */
  display: flex;
  align-items: center;
  margin-bottom: 0.25rem;
}

.followup-trade-header .trade-name {
  font-weight: 600;
}

.followup-address-header {
  font-size: 0.9rem;
  color: #2C3E50; /* Charcoal */
  display: flex;
  align-items: center;
}


.followup-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* Follow-up content */
.followup-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.followup-trade {
  font-size: 0.9rem;
  color: #1B3B5F; /* Primary Navy */
  display: flex;
  align-items: center;
}

.trade-name {
  font-weight: 600;
  color: #4A6FA5; /* Steel Blue */
}

.followup-address {
  font-size: 0.9rem;
  color: #2C3E50; /* Charcoal */
  display: flex;
  align-items: center;
}

.followup-reason {
  display: flex;
  align-items: center;
}

.reason-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.reason-badge.reason-escrow {
  background: rgba(74, 111, 165, 0.1); /* Steel Blue tint */
  color: #4A6FA5; /* Steel Blue */
}

.reason-badge.reason-reo {
  background: rgba(205, 122, 50, 0.1); /* Bronze tint */
  color: #CD7F32; /* Bronze */
}

.reason-badge.reason-legal {
  background: rgba(107, 90, 122, 0.1); /* Muted Plum tint */
  color: #6B5A7A; /* Muted Plum */
}

.reason-badge.reason-inspection {
  background: rgba(46, 125, 50, 0.1); /* Success Green tint */
  color: #2E7D32; /* Success Green */
}

.reason-badge.reason-default {
  background: rgba(149, 165, 166, 0.1); /* Medium Gray tint */
  color: #95A5A6; /* Medium Gray */
}

.followup-title {
  font-size: 0.95rem;
  color: #1B3B5F; /* Primary Navy */
  font-weight: 500;
  line-height: 1.4;
}

/* Status badge colors - using Bootstrap badge with custom colors */
.badge.status-overdue {
  background: #C62828; /* Error Red */
}

.badge.status-urgent {
  background: #D4AF37; /* Accent Gold */
}

.badge.status-active {
  background: #4A6FA5; /* Steel Blue */
}

.badge.status-scheduled {
  background: #2E7D32; /* Success Green */
}

/* Empty state */
.empty-state {
  text-align: center;
  padding: 3rem 2rem;
}

.empty-icon {
  font-size: 4rem;
  color: #D4AF37; /* Accent Gold */
  margin-bottom: 1rem;
}

.empty-title {
  color: #1B3B5F; /* Primary Navy */
  margin-bottom: 0.5rem;
}

.empty-message {
  color: #2C3E50; /* Charcoal */
  margin-bottom: 0;
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


