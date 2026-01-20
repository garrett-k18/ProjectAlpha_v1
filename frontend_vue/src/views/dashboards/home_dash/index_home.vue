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
      :tasksCount="tasksCount"
      :listsCount="listsCount"
      :tradesCount="tradesCount"
      @open-pipeline="showPipelineModal = true"
      @open-tasks="openTasksModal"
      @open-lists="openListsModal"
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
    <PipelineWidget @open-asset="onOpenAssetFromPipeline" />
  </b-modal>

  <b-modal
    v-model="showTasksModal"
    title="My Tasks"
    size="xl"
    dialog-class="modal-dialog-centered tasks-modal"
    hide-footer
    body-class="p-0 tasks-modal-body"
  >
    <div v-if="tasksLoading" class="text-center py-3">
      <div class="spinner-border spinner-border-sm text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
    <div v-else class="tasks-container">
      <div v-if="tasksError" class="alert alert-danger mb-3">
        <i class="mdi mdi-alert-circle-outline me-2"></i>{{ tasksError }}
      </div>
      
      <!-- Summary Stats Bar -->
      <div v-if="taskAssets.length" class="tasks-summary mb-4">
        <div class="row g-3">
          <div class="col-3 text-center">
            <div class="summary-stat overdue">
              <div class="stat-number">{{ filteredTasks.filter(f => f.days_until < 0).length }}</div>
              <div class="stat-label">Overdue</div>
            </div>
          </div>
          <div class="col-3 text-center">
            <div class="summary-stat week">
              <div class="stat-number">{{ filteredTasks.filter(f => f.days_until >= 0 && f.days_until <= 7).length }}</div>
              <div class="stat-label">This Week</div>
            </div>
          </div>
          <div class="col-3 text-center">
            <div class="summary-stat month">
              <div class="stat-number">{{ filteredTasks.filter(f => f.days_until > 7 && f.days_until <= 30).length }}</div>
              <div class="stat-label">This Month</div>
            </div>
          </div>
          <div class="col-3 text-center">
            <div class="summary-stat future">
              <div class="stat-number">{{ filteredTasks.filter(f => f.days_until > 30).length }}</div>
              <div class="stat-label">Future</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Filters & Controls -->
      <div v-if="taskAssets.length" class="tasks-controls mb-4">
        <div class="row g-3 align-items-end">
          <div class="col-md-3">
            <label class="form-label small fw-semibold text-muted">FILTER BY STATUS</label>
            <select v-model="selectedStatusFilter" class="form-select form-select-sm">
              <option value="all">All Tasks</option>
              <option value="overdue">Overdue</option>
              <option value="urgent">Urgent (≤7 days)</option>
              <option value="active">Active (≤30 days)</option>
              <option value="upcoming">Upcoming (31-60 days)</option>
              <option value="future">Future (61+ days)</option>
            </select>
          </div>
          <div class="col-md-2">
            <label class="form-label small fw-semibold text-muted">PRIORITY</label>
            <select v-model="selectedPriorityFilter" class="form-select form-select-sm">
              <option value="all">All</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
          <div class="col-md-2">
            <label class="form-label small fw-semibold text-muted">CATEGORY</label>
            <select v-model="selectedCategoryFilter" class="form-select form-select-sm">
              <option value="all">All</option>
              <option value="follow_up">Follow-up</option>
              <option value="document_review">Document Review</option>
              <option value="contact_borrower">Contact Borrower</option>
              <option value="legal">Legal</option>
              <option value="inspection">Inspection</option>
              <option value="other">Other</option>
            </select>
          </div>
          <div class="col-md-3">
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

      <!-- Tasks List -->
      <div v-if="filteredTasks.length" class="tasks-list">
        <div 
          v-for="asset in filteredTasks" 
          :key="`task-${asset.asset_hub_id}`"
          class="task-card"
          :class="getUrgencyClass(asset.days_until)"
        >
          <div class="task-header">
            <div class="task-priority">
              <div class="priority-indicator" :class="getTaskPriorityClass(asset.next_priority)">
                <i class="mdi" :class="getTaskPriorityIcon(asset.next_priority)"></i>
              </div>
              <div class="task-meta">
                <div class="task-header-line d-flex align-items-center mb-1">
                  <div class="task-id">{{ asset.servicer_id }}</div>
                  <span v-if="asset.servicer_id && getFullAddress(asset)" class="mx-1">-</span>
                  <div class="task-address-header">
                    <i class="mdi mdi-map-marker-outline me-1"></i>
                    {{ getFullAddress(asset) }}
                  </div>
                </div>
                <div class="task-trade-header">
                  <i class="mdi mdi-briefcase-outline me-1"></i>
                  <span class="trade-name">{{ asset.trade_name || 'No Trade Assigned' }}</span>
                </div>
              </div>
            </div>
            <div class="task-actions">
              <span v-if="asset.count > 1" class="badge bg-warning text-dark me-1">
                {{ asset.count }} tasks
              </span>
              <div class="btn-group">
                <button 
                  class="btn btn-sm btn-outline-success d-flex align-items-center justify-content-center"
                  @click="markComplete(asset.asset_hub_id)"
                  :disabled="!asset.task_id || markingAssetId === asset.asset_hub_id"
                  title="Mark Complete"
                >
                  <span v-if="markingAssetId === asset.asset_hub_id" class="spinner-border spinner-border-sm text-success"></span>
                  <i v-else class="mdi mdi-check"></i>
                </button>
                <button 
                  class="btn btn-sm btn-outline-primary"
                  @click="openAssetFromTasks(asset.asset_hub_id, asset.address)"
                  :disabled="asset.asset_hub_id < 0"
                  :title="asset.asset_hub_id > 0 ? 'View Asset Details' : 'Standalone task (no asset)'"
                >
                  <i class="mdi mdi-eye"></i>
                </button>
              </div>
            </div>
          </div>
          
          <div class="task-content">
            <div v-if="asset.next_category" class="task-category mb-1">
              <i class="mdi mdi-tag-outline me-1"></i>
              <span class="category-badge" :class="getCategoryClass(asset.next_category)">
                {{ getCategoryLabel(asset.next_category) }}
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
        <p class="empty-message">You have no pending tasks at this time.</p>
      </div>
    </div>
  </b-modal>

  <b-modal
    v-model="showListsModal"
    title="My Lists"
    size="lg"
    dialog-class="modal-dialog-centered"
    hide-footer
  >
    <div v-if="listsLoading" class="text-center py-4">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="text-muted mt-2 mb-0">Loading lists...</p>
    </div>
    <div v-else>
      <div v-if="listsError" class="alert alert-danger mb-3">
        <i class="mdi mdi-alert-circle-outline me-2"></i>{{ listsError }}
      </div>
      <div v-if="customLists.length" class="list-group">
        <div
          v-for="list in customLists"
          :key="`list-${list.id}`"
          class="list-group-item list-group-item-action d-flex justify-content-between align-items-start"
          @click="openListAssets(list)"
        >
          <div class="me-3">
            <div class="fw-semibold">{{ list.name }}</div>
            <div v-if="list.description" class="text-muted small">{{ list.description }}</div>
          </div>
          <div class="d-flex align-items-center gap-2">
            <span class="badge bg-primary rounded-pill">
              {{ Array.isArray(list.assets) ? list.assets.length : 0 }}
            </span>
            <button
              type="button"
              class="btn btn-sm btn-outline-danger"
              :disabled="deletingListId === list.id"
              @click.stop="deleteCustomList(list)"
              title="Delete list"
            >
              <span v-if="deletingListId === list.id" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
              <span v-else>Delete</span>
            </button>
          </div>
        </div>
      </div>
      <div v-else class="text-center py-5">
        <i class="mdi mdi-format-list-bulleted text-muted" style="font-size: 3rem;"></i>
        <p class="text-muted mt-2 mb-0">No custom lists yet</p>
      </div>
    </div>
  </b-modal>

  <b-modal
    v-model="showListAssetsModal"
    :title="selectedList ? selectedList.name : 'List Assets'"
    size="xl"
    dialog-class="modal-dialog-centered"
    hide-footer
  >
    <div class="d-flex flex-wrap align-items-center justify-content-between gap-2 mb-3">
      <div class="d-flex flex-wrap gap-2">
        <button
          type="button"
          class="btn btn-sm"
          :class="listAssetsView === 'showtape' ? 'btn-primary' : 'btn-outline-primary'"
          @click="setListAssetsView('showtape')"
        >
          Showtape
        </button>
        <button
          type="button"
          class="btn btn-sm"
          :class="listAssetsView === 'bid_analysis' ? 'btn-primary' : 'btn-outline-primary'"
          @click="setListAssetsView('bid_analysis')"
        >
          Bid Analysis
        </button>
      </div>
      <div v-if="selectedList" class="text-muted small">
        {{ Array.isArray(selectedList.assets) ? selectedList.assets.length : 0 }} assets
      </div>
    </div>

    <div v-if="listAssetsLoading" class="text-center py-4">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="text-muted mt-2 mb-0">Loading assets...</p>
    </div>
    <div v-else>
      <div v-if="listAssetsError" class="alert alert-danger mb-3">
        <i class="mdi mdi-alert-circle-outline me-2"></i>{{ listAssetsError }}
      </div>
      <div v-else>
        <ag-grid-vue
          v-if="listAssetRows.length"
          class="acq-grid"
          :style="{ width: '100%', height: '60vh' }"
          :theme="themeQuartz"
          :columnDefs="listAssetColumnDefs"
          :rowData="listAssetRows"
          :defaultColDef="listAssetDefaultColDef"
          :animateRows="true"
          :pagination="true"
          :paginationPageSize="50"
          :enableCellTextSelection="true"
        />
        <div v-else class="text-center py-5">
          <i class="mdi mdi-format-list-bulleted text-muted" style="font-size: 3rem;"></i>
          <p class="text-muted mt-2 mb-0">No assets found for this list</p>
        </div>
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
import { AgGridVue } from 'ag-grid-vue3'
import { themeQuartz } from 'ag-grid-community'

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

type TaskRow = {
  id: number
  title: string
  description: string
  due_date: string
  priority: 'low' | 'medium' | 'high'
  category: string
  assigned_to: number | null
  assigned_to_username: string | null
  notified_users: string[] | null
  completed: boolean
  asset_hub: number
}

type TaskAssetRow = {
  asset_hub_id: number
  address: string
  servicer_id: string
  trade_name: string | null
  task_id: number | null
  city: string | null
  state: string | null
  count: number
  next_date: string
  next_title: string
  next_priority: 'low' | 'medium' | 'high'
  next_category: string | null
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
    AgGridVue,
  },
  // Options API state for simplicity and broad compatibility across the app
  data() {
    return {
      recentActivity: [] as RecentActivityItem[],
      isLoadingRecentActivity: false,
      showPipelineModal: false,
      showTasksModal: false,
      showListsModal: false,
      tasksCount: 0,
      listsCount: 0,
      tasksLoading: false,
      tasksError: '',
      taskAssets: [] as TaskAssetRow[],
      selectedStatusFilter: 'all',
      selectedPriorityFilter: 'all',
      selectedCategoryFilter: 'all',
      searchQuery: '',
      selectedSort: 'date',
      markingAssetId: null as number | null,
      showTradesModal: false,
      tradesCount: 0,
      tradesLoading: false,
      tradesError: '',
      trades: [] as TradeRow[],
      listsLoading: false,
      listsError: '',
      deletingListId: null as number | null,
      customLists: [] as Array<{ id: number; name: string; description?: string | null; assets?: any[] }>,
      showListAssetsModal: false,
      selectedList: null as ({ id: number; name: string; description?: string | null; assets?: any[] } | null),
      listAssetsView: 'showtape' as 'showtape' | 'bid_analysis',
      listAssetsLoading: false,
      listAssetsError: '',
      listAssetRows: [] as any[],
      listAssetColumnDefs: [
        { field: 'trade_name', headerName: 'Trade', width: 180 },
        { field: 'lifecycle_status', headerName: 'Lifecycle Status', width: 160 },
        { field: 'active_tracks', headerName: 'Active Track(s)', width: 180 },
        { field: 'servicer_id', headerName: 'Servicer ID', width: 140 },
        { field: 'street_address', headerName: 'Address', flex: 1, minWidth: 240 },
        { field: 'city', headerName: 'City', width: 160 },
        { field: 'state', headerName: 'State', width: 110 },
      ] as any[],
      listAssetDefaultColDef: {
        resizable: true,
        filter: true,
        wrapHeaderText: true,
        autoHeaderHeight: true,
        headerClass: 'text-center',
        cellClass: 'text-center',
        floatingFilter: false,
        menuTabs: ['filterMenuTab'],
      } as any,
      themeQuartz,
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
    this.loadActiveTasks()
    this.loadActiveTrades()
    this.loadCustomListsCount()
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

    // Filtered and sorted tasks
    filteredTasks(): TaskAssetRow[] {
      let filtered = [...this.taskAssets]
      
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
      
      // Priority filter
      if (this.selectedPriorityFilter !== 'all') {
        filtered = filtered.filter(asset => 
          asset.next_priority === this.selectedPriorityFilter
        )
      }
      
      // Category filter
      if (this.selectedCategoryFilter !== 'all') {
        filtered = filtered.filter(asset => 
          asset.next_category === this.selectedCategoryFilter
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
    tasks30Days(): TaskAssetRow[] {
      return this.taskAssets.filter((a: TaskAssetRow) => a.days_until <= 30)
    },
    tasks60Days(): TaskAssetRow[] {
      return this.taskAssets.filter((a: TaskAssetRow) => a.days_until > 30 && a.days_until <= 60)
    },
    tasks90Days(): TaskAssetRow[] {
      return this.taskAssets.filter((a: TaskAssetRow) => a.days_until > 60)
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

    getFullAddress(asset: TaskAssetRow): string {
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

    getTaskPriorityClass(priority: 'low' | 'medium' | 'high'): string {
      const priorityMap: Record<string, string> = {
        'high': 'priority-high',
        'medium': 'priority-medium',
        'low': 'priority-low'
      }
      return priorityMap[priority] || 'priority-medium'
    },

    getTaskPriorityIcon(priority: 'low' | 'medium' | 'high'): string {
      const iconMap: Record<string, string> = {
        'high': 'mdi-alert-circle',
        'medium': 'mdi-clock-alert-outline',
        'low': 'mdi-calendar-outline'
      }
      return iconMap[priority] || 'mdi-clock-alert-outline'
    },

    getCategoryClass(category: string): string {
      const categoryMap: Record<string, string> = {
        'follow_up': 'category-followup',
        'document_review': 'category-document',
        'contact_borrower': 'category-contact',
        'legal': 'category-legal',
        'inspection': 'category-inspection',
        'other': 'category-other'
      }
      return categoryMap[category?.toLowerCase()] || 'category-other'
    },

    getCategoryLabel(category: string): string {
      const labelMap: Record<string, string> = {
        'follow_up': 'Follow-up',
        'document_review': 'Document Review',
        'contact_borrower': 'Contact Borrower',
        'legal': 'Legal',
        'inspection': 'Inspection',
        'other': 'Other'
      }
      return labelMap[category] || category
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
      const asset = this.taskAssets.find((a: TaskAssetRow) => a.asset_hub_id === assetHubId)
      if (!asset?.task_id) {
        console.warn('[Home Dashboard] No task found for asset', assetHubId)
        return
      }

      if (this.markingAssetId != null) {
        return
      }

      this.markingAssetId = assetHubId
      this.tasksError = ''

      try {
        await http.patch(`/core/calendar/events/custom/${asset.task_id}/`, {
          completed: true,
          is_reminder: false,
        })
        await this.loadActiveTasks()
      } catch (err: any) {
        console.error('[Home Dashboard] markComplete failed', err)
        this.tasksError = 'Failed to mark task complete.'
      } finally {
        this.markingAssetId = null
      }
    },
    goToActivity() {
      this.$router.push('/pages/activity')
    },

    async loadActiveTasks() {
      // WHAT: Fetch active tasks for the logged-in user
      // WHY: Consolidated workflow - tasks replace follow-ups
      this.tasksLoading = true
      this.tasksError = ''
      try {
        // WHAT: Fetch all incomplete tasks (no user filter in dev mode)
        // WHY: In dev mode with bypassed auth, we want to see all tasks
        // HOW: Backend will filter by user if authenticated, otherwise show all public tasks
        const resp = await http.get('/core/calendar/events/custom/', {
          params: {
            completed: false,
            // Note: Backend handles user filtering based on authentication
          }
        })
        
        // WHAT: DRF ModelViewSet returns paginated results by default
        // WHY: Need to check if data is in results array or directly in data
        let taskEvents = []
        if (Array.isArray((resp as any)?.data)) {
          taskEvents = (resp as any).data
        } else if ((resp as any)?.data?.results && Array.isArray((resp as any).data.results)) {
          taskEvents = (resp as any).data.results
        } else if ((resp as any)?.data) {
          // If data exists but isn't an array, wrap it
          taskEvents = [(resp as any).data]
        }
        
        // WHAT: Group tasks by asset_hub_id (or use negative IDs for standalone tasks)
        // WHY: Support both asset-linked tasks and standalone tasks without asset_hub
        // HOW: Use actual asset_hub_id if present, otherwise use negative index for standalone
        const grouped = new Map<number, any[]>()
        const assetInfo = new Map<number, { address: string; servicer_id: string; city: string; state: string; trade_name: string }>()
        let standaloneIndex = -1

        for (const r of taskEvents) {
          const rawId = (r as any).asset_hub ?? (r as any).asset_hub_id
          const idNum = rawId != null ? Number(rawId) : NaN
          
          // WHAT: Assign unique negative ID for standalone tasks (no asset_hub)
          // WHY: Allow tasks without asset_hub to display in the modal
          const groupId = Number.isFinite(idNum) ? idNum : standaloneIndex--
          
          const bucket = grouped.get(groupId) ?? []
          bucket.push(r)
          grouped.set(groupId, bucket)
          
          if (!assetInfo.has(groupId)) {
            assetInfo.set(groupId, { 
              address: r.address || r.title || 'Standalone Task',
              servicer_id: r.servicer_id || 'N/A',
              city: r.city || '',
              state: r.state || '',
              trade_name: r.trade_name || ''
            })
          }
        }

        const today = new Date()
        today.setHours(0, 0, 0, 0)

        const assetIds = Array.from(grouped.keys())
        const assets = assetIds.map(id => {
          const info = assetInfo.get(id)
          const tasks = (grouped.get(id) ?? []).slice().sort((a, b) => String(a.date).localeCompare(String(b.date)))
          const next = tasks[0]
          const nextTaskId = next?.id ? Number(next.id) : null
          
          const nextDate = new Date(next.date)
          nextDate.setHours(0, 0, 0, 0)
          const diffTime = nextDate.getTime() - today.getTime()
          const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

          return {
            asset_hub_id: id,
            address: info?.address || 'No address',
            servicer_id: info?.servicer_id || 'No ID',
            trade_name: info?.trade_name || null,
            city: info?.city || null,
            state: info?.state || null,
            count: tasks.length,
            next_date: String(next?.date ?? ''),
            next_title: String(next?.title ?? ''),
            next_priority: (next?.priority as 'low' | 'medium' | 'high') || 'medium',
            next_category: next?.reason || next?.category || null,
            days_until: diffDays,
            task_id: nextTaskId,
          } as TaskAssetRow
        })

        const sorted = assets.sort((a, b) => 
          String(a.next_date).localeCompare(String(b.next_date)) || a.asset_hub_id - b.asset_hub_id
        )

        this.taskAssets = sorted
        this.tasksCount = sorted.length
      } catch (e: any) {
        console.error('[Home Dashboard] loadActiveTasks failed', e)
        this.tasksError = 'Failed to load tasks.'
        this.taskAssets = []
        this.tasksCount = 0
      } finally {
        this.tasksLoading = false
      }
    },

    openTasksModal() {
      this.showTasksModal = true
      if (!this.tasksLoading && this.taskAssets.length === 0) {
        this.loadActiveTasks()
      }
    },

    openAssetFromTasks(assetHubId: number, address: string) {
      // WHAT: Open asset modal only for tasks with valid asset_hub
      // WHY: Standalone tasks (negative IDs) don't have an asset to display
      // HOW: Check if ID is positive before opening modal
      if (assetHubId > 0) {
        this.selectedId = assetHubId
        this.selectedRow = null
        this.selectedAddr = address || null
        this.showTasksModal = false
        this.showAssetModal = true
      } else {
        // Standalone task - just close the modal (no asset to view)
        this.showTasksModal = false
      }
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

    async loadCustomListsCount() {
      // WHAT: Load count of custom asset lists for "My Lists" tile
      // WHY: Users expect the tile to reflect their saved lists
      // HOW: Call AM custom lists endpoint and derive count from results
      try {
        const resp = await http.get('/am/custom-lists/')
        if (Array.isArray((resp as any)?.data)) {
          this.listsCount = (resp as any).data.length
        } else if (Array.isArray((resp as any)?.data?.results)) {
          this.listsCount = (resp as any).data.results.length
        } else {
          this.listsCount = 0
        }
      } catch (e) {
        console.error('[Home Dashboard] loadCustomListsCount failed', e)
        this.listsCount = 0
      }
    },

    async loadCustomLists() {
      // WHAT: Load full custom list data for the "My Lists" modal
      // WHY: Users need to see list names and asset counts
      // HOW: Call AM custom lists endpoint and map to local state
      this.listsLoading = true
      this.listsError = ''
      try {
        const resp = await http.get('/am/custom-lists/')
        if (Array.isArray((resp as any)?.data)) {
          this.customLists = (resp as any).data
        } else if (Array.isArray((resp as any)?.data?.results)) {
          this.customLists = (resp as any).data.results
        } else {
          this.customLists = []
        }
      } catch (e) {
        console.error('[Home Dashboard] loadCustomLists failed', e)
        this.customLists = []
        this.listsError = 'Failed to load custom lists.'
      } finally {
        this.listsLoading = false
      }
    },

    openTradesModal() {
      this.showTradesModal = true
      if (!this.tradesLoading && this.trades.length === 0) {
        this.loadActiveTrades()
      }
    },

    openListsModal() {
      // WHAT: Open "My Lists" modal and load list data
      // WHY: Users expect the tile to open a list details modal
      // HOW: Fetch lists only when needed to reduce API calls
      this.showListsModal = true
      if (!this.listsLoading && this.customLists.length === 0) {
        this.loadCustomLists()
      }
    },

    async deleteCustomList(list: { id: number; name: string }) {
      if (!list?.id) return
      const ok = window.confirm(`Delete list "${list.name}"?`)
      if (!ok) return

      this.deletingListId = list.id
      this.listsError = ''
      try {
        await http.delete(`/am/custom-lists/${list.id}/`)
        await this.loadCustomLists()
      } catch (e) {
        console.error('[Home Dashboard] deleteCustomList failed', e)
        this.listsError = 'Failed to delete list.'
      } finally {
        this.deletingListId = null
      }
    },

    async openListAssets(list: { id: number; name: string; description?: string | null; assets?: any[] }) {
      this.selectedList = list
      this.showListsModal = false
      this.showListAssetsModal = true
      this.setListAssetsView('showtape')
      await this.loadListAssets(list)
    },

    setListAssetsView(view: 'showtape' | 'bid_analysis') {
      this.listAssetsView = view
      if (view === 'showtape') {
        this.listAssetColumnDefs = [
          { field: 'trade_name', headerName: 'Trade', width: 180 },
          { field: 'lifecycle_status', headerName: 'Lifecycle Status', width: 160 },
          { field: 'active_tracks', headerName: 'Active Track(s)', width: 180 },
          { field: 'servicer_id', headerName: 'Servicer ID', width: 140 },
          { field: 'street_address', headerName: 'Address', flex: 1, minWidth: 240 },
          { field: 'city', headerName: 'City', width: 160 },
          { field: 'state', headerName: 'State', width: 110 },
        ]
      } else {
        this.listAssetColumnDefs = [
          { field: 'servicer_id', headerName: 'Servicer ID', width: 140 },
          { field: 'street_address', headerName: 'Address', flex: 1, minWidth: 240 },
          { field: 'city', headerName: 'City', width: 160 },
          { field: 'state', headerName: 'State', width: 110 },
        ]
      }
    },

    async loadListAssets(list: { id: number; name: string; description?: string | null; assets?: any[] }) {
      this.listAssetsLoading = true
      this.listAssetsError = ''
      this.listAssetRows = []

      try {
        const rawIds = Array.isArray(list.assets) ? list.assets : []
        const ids = Array.from(new Set(rawIds.map((x: any) => Number(x)).filter((n: number) => Number.isFinite(n))))
        if (ids.length === 0) {
          this.listAssetRows = []
          return
        }

        const rows: any[] = []
        const chunkSize = 10
        for (let i = 0; i < ids.length; i += chunkSize) {
          const chunk = ids.slice(i, i + chunkSize)
          const chunkRows = await Promise.all(
            chunk.map(async (id) => {
              try {
                const res = await http.get(`/am/assets/${id}/`)
                return res.data
              } catch {
                return null
              }
            }),
          )
          rows.push(...chunkRows.filter(Boolean))
        }

        this.listAssetRows = rows
      } catch (e) {
        console.error('[Home Dashboard] loadListAssets failed', e)
        this.listAssetsError = 'Failed to load list assets.'
        this.listAssetRows = []
      } finally {
        this.listAssetsLoading = false
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
      this.selectedId = payload.id
      // Set row to null so LoanLevelIndex fetches the complete asset data by ID
      // Calendar event object doesn't have trade_name, street_address, city, state, etc.
      this.selectedRow = null
      this.selectedAddr = payload.addr || null
      this.showAssetModal = true
    },

    onOpenAssetFromPipeline(payload: { id: string | number; row: any; addr?: string }): void {
      this.selectedId = payload.id
      this.selectedRow = payload.row || null
      this.selectedAddr = payload.addr || null
      this.showPipelineModal = false
      this.showAssetModal = true
    },

    // Handle row-loaded event from LoanLevelIndex
    onRowLoaded(row: any): void {
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

/* Tasks modal - Professional Navy & Gold Design */
.tasks-modal {
  max-height: 80vh;
}

.tasks-modal .modal-content {
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  background: #FDFBF7; /* Warm White from color palette */
}

.tasks-modal-body {
  overflow-y: auto;
  flex: 1;
  max-height: calc(80vh - 120px);
  padding: 0;
}

/* Tasks container */
.tasks-container {
  padding: 1.5rem;
  background: #FDFBF7; /* Warm White */
}

/* Controls section */
.tasks-controls {
  background: linear-gradient(135deg, #F5F3EE 0%, #E9ECEF 100%); /* Cream to Light Gray */
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid #dee2e6;
}

.tasks-controls .form-label {
  color: #1B3B5F; /* Primary Navy */
  font-size: 0.75rem;
  letter-spacing: 0.5px;
}

.tasks-controls .form-select,
.tasks-controls .form-control {
  border: 1px solid #4A6FA5; /* Steel Blue */
  background: #FDFBF7; /* Warm White */
}

.tasks-controls .form-select:focus,
.tasks-controls .form-control:focus {
  border-color: #D4AF37; /* Accent Gold */
  box-shadow: 0 0 0 0.2rem rgba(212, 175, 55, 0.25);
}

/* Summary stats */
.tasks-summary {
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

/* Task cards */
.tasks-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.task-card {
  background: #FDFBF7; /* Warm White */
  border-radius: 12px;
  border: 1px solid #E9ECEF; /* Light Gray */
  padding: 0.65rem;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(27, 59, 95, 0.08); /* Navy shadow */
  margin-bottom: 0.2rem;
}

.task-card:hover {
  box-shadow: 0 4px 12px rgba(27, 59, 95, 0.15); /* Navy shadow */
  transform: translateY(-1px);
  border-color: #D4AF37; /* Accent Gold */
}

.task-card.urgent-high {
  border-left: 4px solid #B85A3A; /* Burnt Sienna */
  background: linear-gradient(135deg, rgba(184, 90, 58, 0.08) 0%, #FDFBF7 100%);
}

.task-card.urgent-medium {
  border-left: 4px solid #DAA520; /* Goldenrod */
  background: linear-gradient(135deg, rgba(218, 165, 32, 0.08) 0%, #FDFBF7 100%);
}

.task-card.upcoming {
  border-left: 4px solid #6B5A7A; /* Muted Plum */
  background: linear-gradient(135deg, rgba(107, 90, 122, 0.08) 0%, #FDFBF7 100%);
}

.task-card.future {
  border-left: 4px solid #1B5E20; /* Forest Green */
  background: linear-gradient(135deg, rgba(27, 94, 32, 0.08) 0%, #FDFBF7 100%);
}

/* Task header */
.task-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
}

.task-priority {
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

.task-meta {
  display: flex;
  flex-direction: column;
}

.task-header-line {
  margin-bottom: 0.25rem;
}

.task-id {
  font-size: 0.95rem;
  font-weight: 600;
  color: #1B3B5F; /* Primary Navy */
  letter-spacing: 0.5px;
}

.task-trade-header {
  font-size: 0.9rem;
  color: #4A6FA5; /* Steel Blue */
  display: flex;
  align-items: center;
  margin-bottom: 0.25rem;
}

.task-trade-header .trade-name {
  font-weight: 600;
}

.task-address-header {
  font-size: 0.9rem;
  color: #2C3E50; /* Charcoal */
  display: flex;
  align-items: center;
}


.task-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* Task content */
.task-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.task-trade {
  font-size: 0.9rem;
  color: #1B3B5F; /* Primary Navy */
  display: flex;
  align-items: center;
}

.trade-name {
  font-weight: 600;
  color: #4A6FA5; /* Steel Blue */
}

.task-address {
  font-size: 0.9rem;
  color: #2C3E50; /* Charcoal */
  display: flex;
  align-items: center;
}

.task-category {
  display: flex;
  align-items: center;
}

.category-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.category-badge.category-followup {
  background: rgba(74, 111, 165, 0.1); /* Steel Blue tint */
  color: #4A6FA5; /* Steel Blue */
}

.category-badge.category-document {
  background: rgba(205, 122, 50, 0.1); /* Bronze tint */
  color: #CD7F32; /* Bronze */
}

.category-badge.category-legal {
  background: rgba(107, 90, 122, 0.1); /* Muted Plum tint */
  color: #6B5A7A; /* Muted Plum */
}

.category-badge.category-inspection {
  background: rgba(46, 125, 50, 0.1); /* Success Green tint */
  color: #2E7D32; /* Success Green */
}

.category-badge.category-contact {
  background: rgba(218, 165, 32, 0.1); /* Goldenrod tint */
  color: #DAA520; /* Goldenrod */
}

.category-badge.category-other {
  background: rgba(149, 165, 166, 0.1); /* Medium Gray tint */
  color: #95A5A6; /* Medium Gray */
}

.task-title {
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


