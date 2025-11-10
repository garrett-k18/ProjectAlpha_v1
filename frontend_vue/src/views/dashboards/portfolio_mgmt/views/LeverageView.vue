<template>
  <!--
    Leverage View
    Displays debt facilities, leverage ratios, covenants, and debt management
    Tracks all financing arrangements across the portfolio
  -->
  <div class="leverage-view">
    <!-- Entity Selector & Controls -->
    <b-row class="mb-3">
      <b-col cols="12">
        <div class="d-flex align-items-center gap-3 flex-wrap justify-content-between">
          <div class="d-flex align-items-center gap-3">
            <label class="fw-bold mb-0">Select Entity:</label>
            <select v-model="selectedEntity" class="form-select" style="max-width: 350px;">
              <option :value="null">-- All Entities --</option>
              <option v-for="entity in entities" :key="entity.id" :value="entity.id">
                {{ entity.name }}
              </option>
            </select>
          </div>
          <div class="d-flex gap-2">
            <button class="btn btn-sm btn-primary">
              <i class="mdi mdi-plus-circle me-1"></i> New Facility
            </button>
            <button class="btn btn-sm btn-secondary">
              <i class="mdi mdi-download me-1"></i> Export Report
            </button>
          </div>
        </div>
      </b-col>
    </b-row>

    <!-- Leverage Summary Cards -->
    <b-row class="g-2 mb-3">
      <!-- Total Debt Outstanding -->
      <b-col xl="3" lg="6" md="6">
        <div class="card widget-flat">
          <div class="card-body">
            <div class="float-end">
              <i class="mdi mdi-bank widget-icon bg-danger-lighten text-danger"></i>
            </div>
            <h5 class="text-muted fw-normal mt-0" title="Total Debt Outstanding">
              Total Debt
            </h5>
            <h3 class="mt-3 mb-3">{{ formatCurrency(leverageStats.totalDebt) }}</h3>
            <p class="mb-0 text-muted">
              <span class="text-nowrap">{{ leverageStats.facilityCount }} Facilities</span>
            </p>
          </div>
        </div>
      </b-col>

      <!-- LTV Ratio -->
      <b-col xl="3" lg="6" md="6">
        <div class="card widget-flat">
          <div class="card-body">
            <div class="float-end">
              <i class="mdi mdi-percent widget-icon bg-warning-lighten text-warning"></i>
            </div>
            <h5 class="text-muted fw-normal mt-0" title="Loan-to-Value Ratio">LTV Ratio</h5>
            <h3 class="mt-3 mb-3">{{ leverageStats.ltvRatio }}%</h3>
            <p class="mb-0 text-muted">
              <span :class="getLtvStatus(leverageStats.ltvRatio).class">
                <i :class="['mdi', getLtvStatus(leverageStats.ltvRatio).icon]"></i>
                {{ getLtvStatus(leverageStats.ltvRatio).text }}
              </span>
            </p>
          </div>
        </div>
      </b-col>

      <!-- Debt Service Coverage -->
      <b-col xl="3" lg="6" md="6">
        <div class="card widget-flat">
          <div class="card-body">
            <div class="float-end">
              <i class="mdi mdi-shield-check widget-icon bg-success-lighten text-success"></i>
            </div>
            <h5 class="text-muted fw-normal mt-0" title="Debt Service Coverage Ratio">
              DSCR
            </h5>
            <h3 class="mt-3 mb-3">{{ leverageStats.dscr }}x</h3>
            <p class="mb-0 text-muted">
              <span :class="leverageStats.dscr >= 1.25 ? 'text-success' : 'text-warning'">
                <i class="mdi mdi-check-circle"></i>
                {{ leverageStats.dscr >= 1.25 ? 'Healthy' : 'Monitor' }}
              </span>
            </p>
          </div>
        </div>
      </b-col>

      <!-- Weighted Avg Rate -->
      <b-col xl="3" lg="6" md="6">
        <div class="card widget-flat">
          <div class="card-body">
            <div class="float-end">
              <i class="mdi mdi-chart-line widget-icon bg-info-lighten text-info"></i>
            </div>
            <h5 class="text-muted fw-normal mt-0" title="Weighted Average Interest Rate">
              Avg Rate
            </h5>
            <h3 class="mt-3 mb-3">{{ leverageStats.weightedRate }}%</h3>
            <p class="mb-0 text-muted">
              <span class="text-nowrap">{{ leverageStats.fixedPercent }}% fixed</span>
            </p>
          </div>
        </div>
      </b-col>
    </b-row>

    <!-- Debt Facilities & Maturity Profile -->
    <b-row class="g-2 mb-3">
      <!-- Active Debt Facilities -->
      <b-col xl="8" lg="12">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h4 class="header-title mb-0">Active Debt Facilities</h4>
            <button class="btn btn-sm btn-link p-0">
              <i class="mdi mdi-refresh"></i> Refresh
            </button>
          </div>
          <div class="card-body pt-0">
            <div class="table-responsive">
              <table class="table table-centered table-nowrap table-hover mb-0">
                <thead>
                  <tr>
                    <th>Facility</th>
                    <th>Lender</th>
                    <th>Type</th>
                    <th>Amount</th>
                    <th>Outstanding</th>
                    <th>Rate</th>
                    <th>Maturity</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="facility in facilities" :key="facility.id">
                    <td>
                      <h5 class="my-0 fw-normal">{{ facility.name }}</h5>
                      <small class="text-muted">{{ facility.entity }}</small>
                    </td>
                    <td>{{ facility.lender }}</td>
                    <td>
                      <span class="badge bg-primary">{{ facility.type }}</span>
                    </td>
                    <td>{{ formatCurrency(facility.committed) }}</td>
                    <td class="fw-semibold">{{ formatCurrency(facility.outstanding) }}</td>
                    <td>
                      {{ facility.rate }}%
                      <span v-if="facility.isFixed" class="badge bg-success-lighten text-success ms-1">Fixed</span>
                      <span v-else class="badge bg-warning-lighten text-warning ms-1">Floating</span>
                    </td>
                    <td>{{ facility.maturity }}</td>
                    <td>
                      <span :class="['badge', getFacilityStatusBadge(facility.status)]">
                        {{ facility.status }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </b-col>

      <!-- Maturity Profile -->
      <b-col xl="4" lg="12">
        <div class="card">
          <div class="card-header">
            <h4 class="header-title mb-0">Maturity Profile</h4>
          </div>
          <div class="card-body pt-0">
            <!-- Placeholder for maturity chart -->
            <div class="text-center py-3 mb-3">
              <i class="mdi mdi-chart-bar" style="font-size: 48px; color: #727cf5;"></i>
              <p class="text-muted mt-2 mb-0 small">Maturity chart will be integrated here</p>
            </div>
            <!-- Maturity breakdown -->
            <div v-for="bucket in maturityBuckets" :key="bucket.period" class="mb-2">
              <div class="d-flex justify-content-between mb-1">
                <span class="fw-semibold">{{ bucket.period }}</span>
                <span class="text-muted">{{ formatCurrency(bucket.amount) }}</span>
              </div>
              <div class="progress" style="height: 6px;">
                <div
                  class="progress-bar"
                  :class="bucket.color"
                  :style="{ width: (bucket.amount / leverageStats.totalDebt * 100) + '%' }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </b-col>
    </b-row>

    <!-- Covenants & Debt Metrics -->
    <b-row class="g-2 mb-3">
      <!-- Financial Covenants -->
      <b-col xl="6" lg="12">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h4 class="header-title mb-0">Financial Covenants</h4>
            <button class="btn btn-sm btn-success">
              <i class="mdi mdi-file-document-edit me-1"></i> Test Covenants
            </button>
          </div>
          <div class="card-body pt-0">
            <div class="table-responsive">
              <table class="table table-sm table-centered table-nowrap mb-0">
                <thead>
                  <tr>
                    <th>Facility</th>
                    <th>Covenant</th>
                    <th>Required</th>
                    <th>Actual</th>
                    <th>Cushion</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="covenant in covenants" :key="covenant.id">
                    <td>{{ covenant.facility }}</td>
                    <td>{{ covenant.name }}</td>
                    <td>{{ covenant.required }}</td>
                    <td class="fw-semibold">{{ covenant.actual }}</td>
                    <td>
                      <span :class="getCovenantCushionColor(covenant.cushion)">
                        {{ covenant.cushion }}
                      </span>
                    </td>
                    <td>
                      <span :class="['badge', getCovenantStatusBadge(covenant.status)]">
                        {{ covenant.status }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </b-col>

      <!-- Key Debt Metrics -->
      <b-col xl="6" lg="12">
        <div class="card">
          <div class="card-header">
            <h4 class="header-title mb-0">Key Debt Metrics</h4>
          </div>
          <div class="card-body pt-0">
            <div class="row">
              <div class="col-md-6 mb-3">
                <h5 class="text-muted fw-normal mb-1">Total Commitments</h5>
                <h3 class="mb-0">{{ formatCurrency(debtMetrics.totalCommitments) }}</h3>
              </div>
              <div class="col-md-6 mb-3">
                <h5 class="text-muted fw-normal mb-1">Available to Draw</h5>
                <h3 class="mb-0 text-success">{{ formatCurrency(debtMetrics.availableToDraw) }}</h3>
              </div>
              <div class="col-md-6 mb-3">
                <h5 class="text-muted fw-normal mb-1">Annual Debt Service</h5>
                <h3 class="mb-0">{{ formatCurrency(debtMetrics.annualDebtService) }}</h3>
              </div>
              <div class="col-md-6 mb-3">
                <h5 class="text-muted fw-normal mb-1">Interest Expense (YTD)</h5>
                <h3 class="mb-0">{{ formatCurrency(debtMetrics.interestExpenseYtd) }}</h3>
              </div>
              <div class="col-md-6 mb-3">
                <h5 class="text-muted fw-normal mb-1">Debt/Equity Ratio</h5>
                <h3 class="mb-0">{{ debtMetrics.debtToEquity }}x</h3>
              </div>
              <div class="col-md-6 mb-3">
                <h5 class="text-muted fw-normal mb-1">Interest Coverage</h5>
                <h3 class="mb-0" :class="debtMetrics.interestCoverage >= 2.0 ? 'text-success' : 'text-warning'">
                  {{ debtMetrics.interestCoverage }}x
                </h3>
              </div>
            </div>
          </div>
        </div>
      </b-col>
    </b-row>

    <!-- Facility Activity & Upcoming Events -->
    <b-row class="g-2">
      <!-- Recent Facility Activity -->
      <b-col xl="6" lg="12">
        <div class="card">
          <div class="card-header">
            <h4 class="header-title mb-0">Recent Facility Activity</h4>
          </div>
          <div class="card-body pt-0">
            <div class="table-responsive">
              <table class="table table-sm table-centered table-nowrap mb-0">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Facility</th>
                    <th>Type</th>
                    <th>Amount</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="activity in recentActivity" :key="activity.id">
                    <td>{{ activity.date }}</td>
                    <td>{{ activity.facility }}</td>
                    <td>
                      <span :class="['badge', getActivityTypeBadge(activity.type)]">
                        {{ activity.type }}
                      </span>
                    </td>
                    <td>{{ formatCurrency(activity.amount) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </b-col>

      <!-- Upcoming Events -->
      <b-col xl="6" lg="12">
        <div class="card">
          <div class="card-header">
            <h4 class="header-title mb-0">Upcoming Events</h4>
          </div>
          <div class="card-body pt-0">
            <div class="timeline-alt pb-0">
              <div class="timeline-item" v-for="(event, idx) in upcomingEvents" :key="idx">
                <i :class="['mdi', event.icon, 'bg-warning-lighten', 'text-warning', 'timeline-icon']"></i>
                <div class="timeline-item-info">
                  <h5 class="mt-0 mb-1">{{ event.title }}</h5>
                  <p class="text-muted mb-0 small">{{ event.description }}</p>
                  <p class="mb-0">
                    <small class="text-muted">{{ event.date }}</small>
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
 * Leverage View Component
 * 
 * WHAT: Displays debt facilities, leverage ratios, financial covenants,
 *       and debt management metrics across the portfolio
 * 
 * WHY: Critical for monitoring debt obligations, covenant compliance,
 *      refinancing needs, and overall leverage management
 * 
 * WHERE: Rendered within Portfolio Management dashboard's Leverage tab
 * 
 * HOW: Tracks all debt facilities with maturity schedules, covenant tests,
 *      and key leverage metrics. Backend integration via Pinia store (to be implemented)
 */
import { defineComponent, ref } from 'vue'

// WHAT: Type definition for entity
// WHY: Defines structure for entity selection
interface Entity {
  id: number
  name: string
}

// WHAT: Type definition for debt facility
// WHY: Defines structure for debt facility tracking
interface Facility {
  id: number
  name: string
  entity: string
  lender: string
  type: string
  committed: number
  outstanding: number
  rate: number
  isFixed: boolean
  maturity: string
  status: string
}

// WHAT: Type definition for financial covenant
// WHY: Defines structure for covenant compliance tracking
interface Covenant {
  id: number
  facility: string
  name: string
  required: string
  actual: string
  cushion: string
  status: string
}

// WHAT: Define component using defineComponent for proper TypeScript support
// WHY: Ensures proper type inference and prevents interface naming errors
export default defineComponent({
  name: 'LeverageView',
  setup() {
    // WHAT: Selected entity ID
    // WHY: Filter facilities by entity
    const selectedEntity = ref<number | null>(null)

    // WHAT: List of entities with debt
    // TODO: Fetch from backend
    const entities = ref<Entity[]>([
      { id: 1, name: 'Fund I - Core Real Estate' },
      { id: 2, name: 'Fund II - Opportunistic' },
      { id: 3, name: 'Oakwood Residential JV' },
    ])

    // WHAT: Leverage summary statistics
    // WHY: High-level debt metrics
    const leverageStats = ref({
      totalDebt: 425000000,
      facilityCount: 8,
      ltvRatio: 62.5,
      dscr: 1.45,
      weightedRate: 5.8,
      fixedPercent: 65,
    })

    // WHAT: Active debt facilities
    // WHY: Complete debt facility inventory
    const facilities = ref<Facility[]>([
      {
        id: 1,
        name: 'Senior Credit Facility',
        entity: 'Fund I',
        lender: 'Wells Fargo',
        type: 'Revolving',
        committed: 150000000,
        outstanding: 125000000,
        rate: 5.25,
        isFixed: false,
        maturity: 'Mar 2025',
        status: 'Active',
      },
      {
        id: 2,
        name: 'Term Loan A',
        entity: 'Fund II',
        lender: 'JP Morgan',
        type: 'Term Loan',
        committed: 100000000,
        outstanding: 100000000,
        rate: 5.5,
        isFixed: true,
        maturity: 'Dec 2027',
        status: 'Active',
      },
      {
        id: 3,
        name: 'Construction Loan',
        entity: 'Oakwood JV',
        lender: 'Bank of America',
        type: 'Construction',
        committed: 75000000,
        outstanding: 58000000,
        rate: 6.2,
        isFixed: false,
        maturity: 'Jun 2026',
        status: 'Active',
      },
      {
        id: 4,
        name: 'Bridge Financing',
        entity: 'Fund II',
        lender: 'Starwood Capital',
        type: 'Bridge',
        committed: 50000000,
        outstanding: 45000000,
        rate: 7.5,
        isFixed: false,
        maturity: 'Sep 2025',
        status: 'Active',
      },
    ])

    // WHAT: Maturity profile buckets
    // WHY: Visualize refinancing needs
    const maturityBuckets = ref([
      { period: '< 12 months', amount: 85000000, color: 'bg-danger' },
      { period: '1-2 years', amount: 120000000, color: 'bg-warning' },
      { period: '2-3 years', amount: 95000000, color: 'bg-info' },
      { period: '3+ years', amount: 125000000, color: 'bg-success' },
    ])

    // WHAT: Financial covenants tracking
    // WHY: Compliance monitoring
    const covenants = ref<Covenant[]>([
      {
        id: 1,
        facility: 'Senior Credit',
        name: 'Min DSCR',
        required: '≥ 1.25x',
        actual: '1.45x',
        cushion: '+16%',
        status: 'Compliant',
      },
      {
        id: 2,
        facility: 'Senior Credit',
        name: 'Max LTV',
        required: '≤ 70%',
        actual: '62.5%',
        cushion: '+11%',
        status: 'Compliant',
      },
      {
        id: 3,
        facility: 'Term Loan A',
        name: 'Min Liquidity',
        required: '≥ $25M',
        actual: '$38M',
        cushion: '+52%',
        status: 'Compliant',
      },
      {
        id: 4,
        facility: 'Construction',
        name: 'Min NOI',
        required: '≥ $8M',
        actual: '$8.2M',
        cushion: '+2.5%',
        status: 'Monitor',
      },
    ])

    // WHAT: Key debt metrics
    // WHY: Comprehensive debt analysis
    const debtMetrics = ref({
      totalCommitments: 475000000,
      availableToDraw: 50000000,
      annualDebtService: 32500000,
      interestExpenseYtd: 21800000,
      debtToEquity: 0.68,
      interestCoverage: 2.35,
    })

    // WHAT: Recent facility activity
    // WHY: Track draws, repayments, amendments
    const recentActivity = ref([
      { id: 1, date: 'Nov 28, 2024', facility: 'Construction Loan', type: 'Draw', amount: 8000000 },
      { id: 2, date: 'Nov 15, 2024', facility: 'Senior Credit', type: 'Repayment', amount: 5000000 },
      { id: 3, date: 'Nov 1, 2024', facility: 'Bridge Financing', type: 'Draw', amount: 10000000 },
      { id: 4, date: 'Oct 20, 2024', facility: 'Term Loan A', type: 'Amendment', amount: 0 },
    ])

    // WHAT: Upcoming facility events
    // WHY: Proactive debt management
    const upcomingEvents = ref([
      {
        title: 'Covenant Test Period',
        description: 'Q4 2024 covenant testing for Senior Credit Facility',
        date: 'Dec 31, 2024',
        icon: 'mdi-clipboard-check',
      },
      {
        title: 'Rate Reset',
        description: 'SOFR rate reset on Construction Loan',
        date: 'Jan 5, 2025',
        icon: 'mdi-refresh',
      },
      {
        title: 'Facility Maturity',
        description: 'Senior Credit Facility expires - refinance in progress',
        date: 'Mar 15, 2025',
        icon: 'mdi-calendar-alert',
      },
    ])

    /**
     * WHAT: Format number as currency
     * WHY: Consistent USD formatting
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
     * WHAT: Get LTV status with color and icon
     * WHY: Visual risk assessment
     */
    function getLtvStatus(ltv: number): { class: string; icon: string; text: string } {
      if (ltv >= 75) return { class: 'text-danger', icon: 'mdi-alert-circle', text: 'High Risk' }
      if (ltv >= 65) return { class: 'text-warning', icon: 'mdi-alert', text: 'Monitor' }
      return { class: 'text-success', icon: 'mdi-check-circle', text: 'Healthy' }
    }

    /**
     * WHAT: Get badge class for facility status
     * WHY: Visual status indicators
     */
    function getFacilityStatusBadge(status: string): string {
      const map: { [key: string]: string } = {
        Active: 'bg-success',
        'In Amendment': 'bg-info',
        Maturing: 'bg-warning',
        Defaulted: 'bg-danger',
      }
      return map[status] || 'bg-secondary'
    }

    /**
     * WHAT: Get color class for covenant cushion
     * WHY: Risk-based color coding
     */
    function getCovenantCushionColor(cushion: string): string {
      const value = parseFloat(cushion.replace(/[^0-9.-]/g, ''))
      if (value < 5) return 'text-danger fw-bold'
      if (value < 10) return 'text-warning'
      return 'text-success'
    }

    /**
     * WHAT: Get badge class for covenant status
     * WHY: Compliance indicators
     */
    function getCovenantStatusBadge(status: string): string {
      const map: { [key: string]: string } = {
        Compliant: 'bg-success',
        Monitor: 'bg-warning',
        Breach: 'bg-danger',
        Waived: 'bg-info',
      }
      return map[status] || 'bg-secondary'
    }

    /**
     * WHAT: Get badge class for activity type
     * WHY: Visual activity categorization
     */
    function getActivityTypeBadge(type: string): string {
      const map: { [key: string]: string } = {
        Draw: 'bg-primary',
        Repayment: 'bg-success',
        Amendment: 'bg-info',
        Extension: 'bg-warning',
      }
      return map[type] || 'bg-secondary'
    }

    return {
      selectedEntity,
      entities,
      leverageStats,
      facilities,
      maturityBuckets,
      covenants,
      debtMetrics,
      recentActivity,
      upcomingEvents,
      formatCurrency,
      getLtvStatus,
      getFacilityStatusBadge,
      getCovenantCushionColor,
      getCovenantStatusBadge,
      getActivityTypeBadge,
    }
  },
})
</script>

<style scoped>
/**
 * Leverage View Styles
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
</style>
