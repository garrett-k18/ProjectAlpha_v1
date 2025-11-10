<template>
  <!--
    Fund Level View
    High-level fund performance dashboard for management
    Displays fund stats, performance metrics, distributions, and portfolio health
  -->
  <div class="fund-level-view">
    <!-- Fund Selector -->
    <b-row class="mb-3">
      <b-col cols="12">
        <div class="d-flex align-items-center gap-3">
          <label class="fw-bold mb-0">Select Fund:</label>
          <select v-model="selectedFund" class="form-select" style="max-width: 300px;">
            <option :value="null">-- Select a Fund --</option>
            <option v-for="fund in funds" :key="fund.id" :value="fund.id">
              {{ fund.name }}
            </option>
          </select>
        </div>
      </b-col>
    </b-row>

    <!-- Fund Stats Cards - Top Row -->
    <b-row class="g-2 mb-3">
      <!-- Total Capital Committed -->
      <b-col xl="3" lg="6" md="6">
        <div class="card widget-flat">
          <div class="card-body">
            <div class="float-end">
              <i class="mdi mdi-cash-multiple widget-icon bg-success-lighten text-success"></i>
            </div>
            <h5 class="text-muted fw-normal mt-0" title="Total Capital Committed">
              Capital Committed
            </h5>
            <h3 class="mt-3 mb-3">{{ formatCurrency(stats.totalCapitalCommitted) }}</h3>
            <p class="mb-0 text-muted">
              <span class="text-success me-2">
                <i class="mdi mdi-arrow-up-bold"></i> {{ stats.capitalDeployedPercent }}%
              </span>
              <span class="text-nowrap">Deployed</span>
            </p>
          </div>
        </div>
      </b-col>

      <!-- Total NAV -->
      <b-col xl="3" lg="6" md="6">
        <div class="card widget-flat">
          <div class="card-body">
            <div class="float-end">
              <i class="mdi mdi-chart-line widget-icon bg-primary-lighten text-primary"></i>
            </div>
            <h5 class="text-muted fw-normal mt-0" title="Net Asset Value">NAV</h5>
            <h3 class="mt-3 mb-3">{{ formatCurrency(stats.nav) }}</h3>
            <p class="mb-0 text-muted">
              <span class="text-success me-2">
                <i class="mdi mdi-arrow-up-bold"></i> {{ stats.navGrowthPercent }}%
              </span>
              <span class="text-nowrap">Since Inception</span>
            </p>
          </div>
        </div>
      </b-col>

      <!-- Distributions -->
      <b-col xl="3" lg="6" md="6">
        <div class="card widget-flat">
          <div class="card-body">
            <div class="float-end">
              <i class="mdi mdi-cash-refund widget-icon bg-warning-lighten text-warning"></i>
            </div>
            <h5 class="text-muted fw-normal mt-0" title="Total Distributions">
              Distributions
            </h5>
            <h3 class="mt-3 mb-3">{{ formatCurrency(stats.totalDistributions) }}</h3>
            <p class="mb-0 text-muted">
              <span class="text-success me-2">
                <i class="mdi mdi-calendar"></i> {{ stats.lastDistributionDate }}
              </span>
              <span class="text-nowrap">Last Distribution</span>
            </p>
          </div>
        </div>
      </b-col>

      <!-- IRR -->
      <b-col xl="3" lg="6" md="6">
        <div class="card widget-flat">
          <div class="card-body">
            <div class="float-end">
              <i class="mdi mdi-percent widget-icon bg-info-lighten text-info"></i>
            </div>
            <h5 class="text-muted fw-normal mt-0" title="Internal Rate of Return">IRR</h5>
            <h3 class="mt-3 mb-3">{{ stats.irr }}%</h3>
            <p class="mb-0 text-muted">
              <span class="text-success me-2">
                <i class="mdi mdi-trending-up"></i> Net
              </span>
              <span class="text-nowrap">Since Inception</span>
            </p>
          </div>
        </div>
      </b-col>
    </b-row>

    <!-- Fund Performance Chart & Portfolio Composition -->
    <b-row class="g-2 mb-3">
      <!-- Performance Chart -->
      <b-col xl="8" lg="12">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h4 class="header-title mb-0">Fund Performance</h4>
            <div class="dropdown">
              <a href="#" class="dropdown-toggle arrow-none card-drop" data-bs-toggle="dropdown" aria-expanded="false">
                <i class="mdi mdi-dots-vertical"></i>
              </a>
              <div class="dropdown-menu dropdown-menu-end">
                <a href="javascript:void(0);" class="dropdown-item">Export Data</a>
                <a href="javascript:void(0);" class="dropdown-item">View Report</a>
              </div>
            </div>
          </div>
          <div class="card-body pt-0">
            <div class="chart-content-bg">
              <div class="row text-center">
                <div class="col-md-4">
                  <p class="text-muted mb-0 mt-3">Current Quarter</p>
                  <h2 class="fw-normal mb-3">
                    <small class="text-success me-1">
                      <i class="mdi mdi-arrow-up-bold"></i> {{ performance.currentQuarter }}%
                    </small>
                  </h2>
                </div>
                <div class="col-md-4">
                  <p class="text-muted mb-0 mt-3">Year to Date</p>
                  <h2 class="fw-normal mb-3">
                    <small class="text-success me-1">
                      <i class="mdi mdi-arrow-up-bold"></i> {{ performance.ytd }}%
                    </small>
                  </h2>
                </div>
                <div class="col-md-4">
                  <p class="text-muted mb-0 mt-3">Since Inception</p>
                  <h2 class="fw-normal mb-3">
                    <small class="text-success me-1">
                      <i class="mdi mdi-arrow-up-bold"></i> {{ performance.sinceInception }}%
                    </small>
                  </h2>
                </div>
              </div>
            </div>
            <!-- Placeholder for chart integration (Apex Charts, Chart.js, etc.) -->
            <div class="mt-3 text-center text-muted">
              <i class="mdi mdi-chart-areaspline" style="font-size: 48px;"></i>
              <p>Performance chart will be integrated here</p>
            </div>
          </div>
        </div>
      </b-col>

      <!-- Portfolio Composition -->
      <b-col xl="4" lg="12">
        <div class="card">
          <div class="card-header">
            <h4 class="header-title mb-0">Portfolio Composition</h4>
          </div>
          <div class="card-body pt-0">
            <div class="mb-3" v-for="asset in assetClasses" :key="asset.name">
              <div class="d-flex justify-content-between mb-1">
                <span class="fw-semibold">{{ asset.name }}</span>
                <span class="text-muted">{{ asset.percent }}%</span>
              </div>
              <div class="progress" style="height: 6px;">
                <div
                  class="progress-bar"
                  :class="asset.color"
                  :style="{ width: asset.percent + '%' }"
                ></div>
              </div>
              <div class="text-muted small mt-1">{{ formatCurrency(asset.value) }}</div>
            </div>
          </div>
        </div>
      </b-col>
    </b-row>

    <!-- Active Investments & Recent Activity -->
    <b-row class="g-2">
      <!-- Active Investments Table -->
      <b-col xl="7" lg="12">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h4 class="header-title mb-0">Active Investments</h4>
            <button class="btn btn-sm btn-primary">
              <i class="mdi mdi-plus-circle me-1"></i> New Investment
            </button>
          </div>
          <div class="card-body pt-0">
            <div class="table-responsive">
              <table class="table table-centered table-nowrap table-hover mb-0">
                <thead>
                  <tr>
                    <th>Investment</th>
                    <th>Type</th>
                    <th>Capital</th>
                    <th>Current Value</th>
                    <th>Return</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="inv in activeInvestments" :key="inv.id">
                    <td>
                      <h5 class="m-0 fw-normal">{{ inv.name }}</h5>
                      <p class="mb-0 text-muted small">{{ inv.date }}</p>
                    </td>
                    <td>{{ inv.type }}</td>
                    <td>{{ formatCurrency(inv.capital) }}</td>
                    <td>{{ formatCurrency(inv.currentValue) }}</td>
                    <td>
                      <span :class="['badge', inv.return >= 0 ? 'bg-success' : 'bg-danger']">
                        {{ inv.return >= 0 ? '+' : '' }}{{ inv.return }}%
                      </span>
                    </td>
                    <td>
                      <span :class="['badge', getStatusBadge(inv.status)]">{{ inv.status }}</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </b-col>

      <!-- Recent Activity -->
      <b-col xl="5" lg="12">
        <div class="card">
          <div class="card-header">
            <h4 class="header-title mb-0">Recent Activity</h4>
          </div>
          <div class="card-body pt-0">
            <div class="timeline-alt pb-0">
              <div class="timeline-item" v-for="(activity, idx) in recentActivity" :key="idx">
                <i :class="['mdi', activity.icon, 'bg-info-lighten', 'text-info', 'timeline-icon']"></i>
                <div class="timeline-item-info">
                  <h5 class="mt-0 mb-1">{{ activity.title }}</h5>
                  <p class="text-muted mb-0">{{ activity.description }}</p>
                  <p class="mb-0">
                    <small class="text-muted">{{ activity.time }}</small>
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </b-col>
    </b-row>
  </div>
</template>

<script lang="ts">
/**
 * Fund Level View Component
 * 
 * WHAT: Displays high-level fund performance metrics, portfolio composition,
 *       active investments, and recent activity for fund management
 * 
 * WHY: Provides executives and fund managers with a comprehensive view
 *      of fund health, performance trends, and key metrics
 * 
 * WHERE: Rendered within Portfolio Management dashboard's Fund Level tab
 * 
 * HOW: Uses Hyper UI card widgets, stat tiles, tables, and timeline components
 *      Data will be fetched from backend API via Pinia store (to be implemented)
 */
import { defineComponent, ref, computed } from 'vue'

// WHAT: Type definition for fund selector
// WHY: Defines structure for fund selection dropdown
interface Fund {
  id: number
  name: string
}

// WHAT: Type definition for asset class composition
// WHY: Defines structure for portfolio composition by asset type
interface AssetClass {
  name: string
  percent: number
  value: number
  color: string
}

// WHAT: Type definition for active investment
// WHY: Defines structure for investment row data in active investments table
interface Investment {
  id: number
  name: string
  date: string
  type: string
  capital: number
  currentValue: number
  return: number
  status: string
}

// WHAT: Type definition for activity timeline
// WHY: Defines structure for recent activity timeline items
interface Activity {
  title: string
  description: string
  time: string
  icon: string
}

// WHAT: Define component using defineComponent for proper TypeScript support
// WHY: Ensures proper type inference and prevents interface naming errors
export default defineComponent({
  name: 'FundLevelView',
  setup() {
    // WHAT: Selected fund ID (null = no fund selected)
    // WHY: Controls which fund's data is displayed
    const selectedFund = ref<number | null>(null)

    // WHAT: List of available funds
    // WHY: Populated from backend API - placeholder data for now
    // TODO: Replace with Pinia store fetch
    const funds = ref<Fund[]>([
      { id: 1, name: 'Fund I - Core Real Estate' },
      { id: 2, name: 'Fund II - Opportunistic' },
      { id: 3, name: 'Fund III - Value-Add' },
    ])

    // WHAT: Fund-level statistics
    // WHY: Key metrics for fund performance dashboard
    // TODO: Fetch from backend based on selectedFund
    const stats = ref({
      totalCapitalCommitted: 250000000,
      capitalDeployedPercent: 78.5,
      nav: 285000000,
      navGrowthPercent: 14.2,
      totalDistributions: 42500000,
      lastDistributionDate: 'Dec 15, 2024',
      irr: 18.7,
    })

    // WHAT: Performance metrics by period
    // WHY: Shows fund return performance across different time horizons
    const performance = ref({
      currentQuarter: 4.2,
      ytd: 12.8,
      sinceInception: 18.7,
    })

    // WHAT: Portfolio composition by asset class
    // WHY: Visual breakdown of how capital is allocated across asset types
    const assetClasses = ref<AssetClass[]>([
      { name: 'Residential', percent: 45, value: 128250000, color: 'bg-primary' },
      { name: 'Commercial', percent: 30, value: 85500000, color: 'bg-success' },
      { name: 'Industrial', percent: 15, value: 42750000, color: 'bg-warning' },
      { name: 'Land', percent: 10, value: 28500000, color: 'bg-info' },
    ])

    // WHAT: Active investments in the fund
    // WHY: Shows current portfolio holdings with performance metrics
    const activeInvestments = ref<Investment[]>([
      {
        id: 1,
        name: 'Multifamily Portfolio - Austin',
        date: 'Jan 2024',
        type: 'Residential',
        capital: 45000000,
        currentValue: 52000000,
        return: 15.6,
        status: 'Active',
      },
      {
        id: 2,
        name: 'Office Complex - Dallas',
        date: 'Mar 2024',
        type: 'Commercial',
        capital: 32000000,
        currentValue: 35500000,
        return: 10.9,
        status: 'Active',
      },
      {
        id: 3,
        name: 'Industrial Park - Houston',
        date: 'May 2024',
        type: 'Industrial',
        capital: 28000000,
        currentValue: 31200000,
        return: 11.4,
        status: 'Under Management',
      },
      {
        id: 4,
        name: 'Mixed-Use Development',
        date: 'Aug 2024',
        type: 'Commercial',
        capital: 52000000,
        currentValue: 53800000,
        return: 3.5,
        status: 'Active',
      },
    ])

    // WHAT: Recent fund activity timeline
    // WHY: Provides chronological view of key fund events and transactions
    const recentActivity = ref<Activity[]>([
      {
        title: 'Distribution Payment',
        description: '$4.2M distributed to LPs',
        time: '2 days ago',
        icon: 'mdi-cash-refund',
      },
      {
        title: 'New Investment',
        description: 'Closed on Industrial Park - Houston',
        time: '1 week ago',
        icon: 'mdi-home-plus',
      },
      {
        title: 'Asset Sale',
        description: 'Exited Retail Center - San Antonio',
        time: '2 weeks ago',
        icon: 'mdi-chart-line',
      },
      {
        title: 'Capital Call',
        description: '$12M capital call for Q4',
        time: '3 weeks ago',
        icon: 'mdi-cash-multiple',
      },
    ])

    /**
     * WHAT: Format number as currency
     * WHY: Consistent USD formatting across dashboard
     * @param value - Number to format
     * @returns Formatted currency string
     */
    function formatCurrency(value: number): string {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
      }).format(value)
    }

    /**
     * WHAT: Get Bootstrap badge class for investment status
     * WHY: Color-code status badges for quick visual scanning
     * @param status - Investment status string
     * @returns Bootstrap badge class
     */
    function getStatusBadge(status: string): string {
      const statusMap: { [key: string]: string } = {
        Active: 'bg-success',
        'Under Management': 'bg-info',
        'In Acquisition': 'bg-warning',
        Exited: 'bg-secondary',
      }
      return statusMap[status] || 'bg-secondary'
    }

    return {
      selectedFund,
      funds,
      stats,
      performance,
      assetClasses,
      activeInvestments,
      recentActivity,
      formatCurrency,
      getStatusBadge,
    }
  },
})
</script>

<style scoped>
/**
 * Fund Level View Styles
 * Follows Hyper UI design system
 */
.widget-icon {
  height: 48px;
  width: 48px;
  text-align: center;
  line-height: 48px;
  font-size: 24px;
  border-radius: 4px;
}

.chart-content-bg {
  background-color: #f9fafb;
  border-radius: 4px;
  padding: 1rem;
}

.timeline-alt {
  padding: 1.25rem 0;
}

.timeline-item {
  position: relative;
  padding-left: 44px;
  padding-bottom: 1.5rem;
}

.timeline-item:last-child {
  padding-bottom: 0;
}

.timeline-icon {
  position: absolute;
  left: 0;
  top: 0;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  text-align: center;
  line-height: 32px;
  font-size: 16px;
}

.timeline-item:not(:last-child):before {
  content: '';
  position: absolute;
  left: 15px;
  top: 32px;
  bottom: -12px;
  width: 2px;
  background-color: #e3eaef;
}

.timeline-item-info h5 {
  font-size: 0.9375rem;
}
</style>
