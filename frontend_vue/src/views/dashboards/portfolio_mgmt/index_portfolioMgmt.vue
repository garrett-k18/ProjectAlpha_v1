<template>
  <!--
    Portfolio Management Dashboard
    Main hub for fund-level, JV-level, waterfall, and cap table views
    Uses Hyper UI tab navigation pattern for clean UX
  -->
  <Layout>
    <!-- Page Title -->
    <b-row>
      <b-col class="col-12">
        <div class="page-title-box">
          <div class="page-title-right">
            <ol class="breadcrumb m-0">
              <li class="breadcrumb-item active">Portfolio Management</li>
            </ol>
          </div>
          <h4 class="page-title">Portfolio Management</h4>
        </div>
      </b-col>
    </b-row>

    <!-- Tab Navigation Card -->
    <b-row>
      <b-col class="col-12">
        <div class="card">
          <div class="card-body">
            <!-- Tabs: Snapshot | Fund Level | JV Level | Leverage | Waterfalls | Cap Table -->
            <ul class="nav nav-pills bg-nav-pills nav-justified mb-3">
              <li class="nav-item">
                <a 
                  href="#snapshot" 
                  :class="['nav-link rounded-0', { active: activeTab === 'snapshot' }]"
                  @click.prevent="activeTab = 'snapshot'"
                >
                  <i class="mdi mdi-view-dashboard d-md-none d-block"></i>
                  <span class="d-none d-md-block">Snapshot</span>
                </a>
              </li>
              <li class="nav-item">
                <a 
                  href="#fund-level" 
                  :class="['nav-link rounded-0', { active: activeTab === 'fund' }]"
                  @click.prevent="activeTab = 'fund'"
                >
                  <i class="mdi mdi-finance d-md-none d-block"></i>
                  <span class="d-none d-md-block">Fund Level</span>
                </a>
              </li>
              <li class="nav-item">
                <a 
                  href="#jv-level" 
                  :class="['nav-link rounded-0', { active: activeTab === 'jv' }]"
                  @click.prevent="activeTab = 'jv'"
                >
                  <i class="mdi mdi-handshake d-md-none d-block"></i>
                  <span class="d-none d-md-block">JV Level</span>
                </a>
              </li>
              <li class="nav-item">
                <a 
                  href="#leverage" 
                  :class="['nav-link rounded-0', { active: activeTab === 'leverage' }]"
                  @click.prevent="activeTab = 'leverage'"
                >
                  <i class="mdi mdi-bank d-md-none d-block"></i>
                  <span class="d-none d-md-block">Leverage</span>
                </a>
              </li>
              <li class="nav-item">
                <a 
                  href="#waterfalls" 
                  :class="['nav-link rounded-0', { active: activeTab === 'waterfalls' }]"
                  @click.prevent="activeTab = 'waterfalls'"
                >
                  <i class="mdi mdi-chart-waterfall d-md-none d-block"></i>
                  <span class="d-none d-md-block">Waterfalls</span>
                </a>
              </li>
              <li class="nav-item">
                <a 
                  href="#cap-table" 
                  :class="['nav-link rounded-0', { active: activeTab === 'cap' }]"
                  @click.prevent="activeTab = 'cap'"
                >
                  <i class="mdi mdi-table-large d-md-none d-block"></i>
                  <span class="d-none d-md-block">Cap Table</span>
                </a>
              </li>
            </ul>

            <!-- Tab Content Container -->
            <div class="tab-content">
              <!-- Snapshot Tab (Default) -->
              <div v-show="activeTab === 'snapshot'">
                <SnapshotView />
              </div>

              <!-- Fund Level Tab -->
              <div v-show="activeTab === 'fund'">
                <FundLevelView />
              </div>

              <!-- JV Level Tab -->
              <div v-show="activeTab === 'jv'">
                <JvLevelView />
              </div>

              <!-- Leverage Tab -->
              <div v-show="activeTab === 'leverage'">
                <LeverageView />
              </div>

              <!-- Waterfalls Tab -->
              <div v-show="activeTab === 'waterfalls'">
                <WaterfallView />
              </div>

              <!-- Cap Table Tab -->
              <div v-show="activeTab === 'cap'">
                <CapTableView />
              </div>
            </div>
          </div>
        </div>
      </b-col>
    </b-row>
  </Layout>
</template>

<script lang="ts">
/**
 * Portfolio Management Dashboard Index
 * 
 * Main entry point for portfolio management features including:
 * - Snapshot: High-level summary of all portfolio areas (default view)
 * - Fund-level performance and stats
 * - Joint Venture (JV) level metrics
 * - Leverage: Debt facilities, covenants, and leverage ratios
 * - Waterfall calculations and distributions
 * - Capitalization table management
 * 
 * WHAT: Tab-based navigation using Hyper UI nav-pills pattern
 * WHY: Clean separation of concerns, modular components, intuitive UX
 * WHERE: Each view is its own component file for maintainability
 */
import { ref } from 'vue'
import Layout from '@/components/layouts/layout.vue'
// Import all view components
import SnapshotView from './views/SnapshotView.vue'
import FundLevelView from './views/FundLevelView.vue'
import JvLevelView from './views/JvLevelView.vue'
import LeverageView from './views/LeverageView.vue'
import WaterfallView from './views/WaterfallView.vue'
import CapTableView from './views/CapTableView.vue'

export default {
  name: 'PortfolioManagementIndex',
  components: {
    Layout,
    SnapshotView,
    FundLevelView,
    JvLevelView,
    LeverageView,
    WaterfallView,
    CapTableView,
  },
  setup() {
    // WHAT: Active tab state - controls which view is displayed
    // WHY: Reactive state ensures smooth tab switching without route changes
    // NOTE: 'snapshot' is the default view showing portfolio summary
    const activeTab = ref<'snapshot' | 'fund' | 'jv' | 'leverage' | 'waterfalls' | 'cap'>('snapshot')

    return {
      activeTab,
    }
  },
}
</script>

<style scoped>
/**
 * Custom styles for portfolio management dashboard
 * Follows Hyper UI patterns and Bootstrap utilities
 */
.nav-pills .nav-link {
  font-weight: 500;
}

.nav-pills .nav-link.active {
  background-color: #0acf97;
}

.nav-pills .nav-link:hover:not(.active) {
  background-color: #f1f3fa;
  color: #6c757d;
}
</style>
