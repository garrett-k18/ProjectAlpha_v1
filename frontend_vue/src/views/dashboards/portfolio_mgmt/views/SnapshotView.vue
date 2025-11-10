<template>
  <!--
    Snapshot View
    High-level summary of all portfolio management areas
    Default landing view showing key metrics across Fund, JV, Waterfall, Cap Table, and Leverage
  -->
  <div class="snapshot-view">
    <!-- Overview Cards - Key Metrics -->
    <b-row class="g-2 mb-3">
      <!-- Total AUM -->
      <b-col xl="2" lg="4" md="6">
        <div class="card widget-flat">
          <div class="card-body">
            <div class="float-end">
              <i class="mdi mdi-briefcase-outline widget-icon bg-primary-lighten text-primary"></i>
            </div>
            <h6 class="text-muted fw-normal mt-0 text-truncate" title="Assets Under Management">
              Total AUM
            </h6>
            <h3 class="mt-2 mb-2">{{ formatCurrency(snapshot.totalAum) }}</h3>
            <p class="mb-0 text-muted">
              <span class="text-success me-1">
                <i class="mdi mdi-arrow-up-bold"></i> {{ snapshot.aumGrowth }}%
              </span>
              <span class="text-nowrap small">YTD</span>
            </p>
          </div>
        </div>
      </b-col>

      <!-- Fund Count -->
      <b-col xl="2" lg="4" md="6">
        <div class="card widget-flat">
          <div class="card-body">
            <div class="float-end">
              <i class="mdi mdi-finance widget-icon bg-success-lighten text-success"></i>
            </div>
            <h6 class="text-muted fw-normal mt-0 text-truncate" title="Active Funds">
              Funds
            </h6>
            <h3 class="mt-2 mb-2">{{ snapshot.fundCount }}</h3>
            <p class="mb-0 text-muted">
              <span class="text-nowrap small">{{ snapshot.fundDeployed }}% deployed</span>
            </p>
          </div>
        </div>
      </b-col>

      <!-- Joint Ventures -->
      <b-col xl="2" lg="4" md="6">
        <div class="card widget-flat">
          <div class="card-body">
            <div class="float-end">
              <i class="mdi mdi-handshake widget-icon bg-warning-lighten text-warning"></i>
            </div>
            <h6 class="text-muted fw-normal mt-0 text-truncate" title="Active Joint Ventures">
              JVs
            </h6>
            <h3 class="mt-2 mb-2">{{ snapshot.jvCount }}</h3>
            <p class="mb-0 text-muted">
              <span class="text-nowrap small">{{ formatCurrency(snapshot.jvCapital) }}</span>
            </p>
          </div>
        </div>
      </b-col>

      <!-- Total Equity -->
      <b-col xl="2" lg="4" md="6">
        <div class="card widget-flat">
          <div class="card-body">
            <div class="float-end">
              <i class="mdi mdi-chart-pie widget-icon bg-info-lighten text-info"></i>
            </div>
            <h6 class="text-muted fw-normal mt-0 text-truncate" title="Total Equity Value">
              Equity
            </h6>
            <h3 class="mt-2 mb-2">{{ formatCurrency(snapshot.totalEquity) }}</h3>
            <p class="mb-0 text-muted">
              <span class="text-nowrap small">{{ snapshot.stakeholderCount }} stakeholders</span>
            </p>
          </div>
        </div>
      </b-col>

      <!-- Total Debt -->
      <b-col xl="2" lg="4" md="6">
        <div class="card widget-flat">
          <div class="card-body">
            <div class="float-end">
              <i class="mdi mdi-bank widget-icon bg-danger-lighten text-danger"></i>
            </div>
            <h6 class="text-muted fw-normal mt-0 text-truncate" title="Total Debt Outstanding">
              Debt
            </h6>
            <h3 class="mt-2 mb-2">{{ formatCurrency(snapshot.totalDebt) }}</h3>
            <p class="mb-0 text-muted">
              <span class="text-nowrap small">{{ snapshot.facilityCount }} facilities</span>
            </p>
          </div>
        </div>
      </b-col>

      <!-- Portfolio IRR -->
      <b-col xl="2" lg="4" md="6">
        <div class="card widget-flat">
          <div class="card-body">
            <div class="float-end">
              <i class="mdi mdi-trending-up widget-icon bg-purple-lighten text-purple"></i>
            </div>
            <h6 class="text-muted fw-normal mt-0 text-truncate" title="Portfolio IRR">
              IRR
            </h6>
            <h3 class="mt-2 mb-2">{{ snapshot.portfolioIrr }}%</h3>
            <p class="mb-0 text-muted">
              <span class="text-success me-1">
                <i class="mdi mdi-arrow-up-bold"></i>
              </span>
              <span class="text-nowrap small">Net to LPs</span>
            </p>
          </div>
        </div>
      </b-col>
    </b-row>

    <!-- Fund Performance & Leverage Summary -->
    <b-row class="g-2 mb-3">
      <!-- Fund Performance Summary -->
      <b-col xl="8" lg="12">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h4 class="header-title mb-0">Fund Performance Summary</h4>
            <button class="btn btn-sm btn-link p-0">View Details →</button>
          </div>
          <div class="card-body pt-0">
            <div class="table-responsive">
              <table class="table table-centered table-nowrap table-hover mb-0">
                <thead>
                  <tr>
                    <th>Fund</th>
                    <th>Vintage</th>
                    <th>Committed Capital</th>
                    <th>Deployed</th>
                    <th>Current NAV</th>
                    <th>IRR</th>
                    <th>MOIC</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="fund in funds" :key="fund.id">
                    <td>
                      <h5 class="my-0 fw-normal">{{ fund.name }}</h5>
                    </td>
                    <td>{{ fund.vintage }}</td>
                    <td>{{ formatCurrency(fund.committed) }}</td>
                    <td>
                      <div class="progress" style="height: 6px; min-width: 80px;">
                        <div
                          class="progress-bar bg-success"
                          :style="{ width: fund.deployedPercent + '%' }"
                        ></div>
                      </div>
                      <span class="small">{{ fund.deployedPercent }}%</span>
                    </td>
                    <td class="fw-semibold">{{ formatCurrency(fund.nav) }}</td>
                    <td>
                      <span :class="getIrrColor(fund.irr)">{{ fund.irr }}%</span>
                    </td>
                    <td>
                      <span class="text-success fw-semibold">{{ fund.moic }}x</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </b-col>

      <!-- Leverage Summary -->
      <b-col xl="4" lg="12">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h4 class="header-title mb-0">Leverage Summary</h4>
            <button class="btn btn-sm btn-link p-0">View Details →</button>
          </div>
          <div class="card-body pt-0">
            <div class="mb-3">
              <h5 class="text-muted fw-normal mb-1">Total Debt Outstanding</h5>
              <h3 class="mb-0">{{ formatCurrency(leverageSummary.totalDebt) }}</h3>
            </div>
            <div class="mb-3">
              <h5 class="text-muted fw-normal mb-1">LTV Ratio</h5>
              <div class="d-flex align-items-center">
                <div class="progress flex-grow-1 me-2" style="height: 10px;">
                  <div
                    class="progress-bar"
                    :class="getLtvColor(leverageSummary.ltvRatio)"
                    :style="{ width: leverageSummary.ltvRatio + '%' }"
                  ></div>
                </div>
                <span class="fw-semibold">{{ leverageSummary.ltvRatio }}%</span>
              </div>
            </div>
            <div class="mb-3">
              <h5 class="text-muted fw-normal mb-1">Debt Service Coverage</h5>
              <p class="mb-0 fw-semibold" :class="leverageSummary.dscr >= 1.25 ? 'text-success' : 'text-warning'">
                {{ leverageSummary.dscr }}x
              </p>
            </div>
            <div class="mb-3">
              <h5 class="text-muted fw-normal mb-1">Weighted Avg Rate</h5>
              <p class="mb-0 fw-semibold">{{ leverageSummary.weightedRate }}%</p>
            </div>
            <div>
              <h5 class="text-muted fw-normal mb-1">Facilities Expiring (12mo)</h5>
              <p class="mb-0">
                <span class="badge bg-warning">{{ leverageSummary.expiringCount }}</span>
                <span class="ms-2 small text-muted">{{ formatCurrency(leverageSummary.expiringAmount) }}</span>
              </p>
            </div>
          </div>
        </div>
      </b-col>
    </b-row>

    <!-- Joint Ventures & Distributions -->
    <b-row class="g-2 mb-3">
      <!-- Active Joint Ventures -->
      <b-col xl="6" lg="12">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h4 class="header-title mb-0">Active Joint Ventures</h4>
            <button class="btn btn-sm btn-link p-0">View All →</button>
          </div>
          <div class="card-body pt-0">
            <div class="table-responsive">
              <table class="table table-sm table-centered table-nowrap mb-0">
                <thead>
                  <tr>
                    <th>JV Name</th>
                    <th>Our Share</th>
                    <th>Total Capital</th>
                    <th>Current Value</th>
                    <th>Return</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="jv in jointVentures" :key="jv.id">
                    <td>{{ jv.name }}</td>
                    <td>{{ jv.ourShare }}%</td>
                    <td>{{ formatCurrency(jv.totalCapital) }}</td>
                    <td>{{ formatCurrency(jv.currentValue) }}</td>
                    <td>
                      <span :class="jv.return >= 0 ? 'text-success' : 'text-danger'">
                        {{ jv.return >= 0 ? '+' : '' }}{{ jv.return }}%
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </b-col>

      <!-- Recent Distributions -->
      <b-col xl="6" lg="12">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h4 class="header-title mb-0">Recent Distributions</h4>
            <button class="btn btn-sm btn-link p-0">View All →</button>
          </div>
          <div class="card-body pt-0">
            <div class="table-responsive">
              <table class="table table-sm table-centered table-nowrap mb-0">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Fund/Entity</th>
                    <th>Type</th>
                    <th>Amount</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="dist in distributions" :key="dist.id">
                    <td>{{ dist.date }}</td>
                    <td>{{ dist.entity }}</td>
                    <td>{{ dist.type }}</td>
                    <td class="fw-semibold">{{ formatCurrency(dist.amount) }}</td>
                    <td>
                      <span :class="['badge', getDistStatusBadge(dist.status)]">
                        {{ dist.status }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </b-col>
    </b-row>

    <!-- Cap Table Summary & Alerts -->
    <b-row class="g-2">
      <!-- Ownership Structure -->
      <b-col xl="5" lg="12">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h4 class="header-title mb-0">Ownership Structure</h4>
            <button class="btn btn-sm btn-link p-0">Cap Table →</button>
          </div>
          <div class="card-body pt-0">
            <div v-for="owner in ownershipStructure" :key="owner.type" class="mb-3">
              <div class="d-flex justify-content-between mb-1">
                <span class="fw-semibold">{{ owner.type }}</span>
                <span class="text-muted">{{ owner.percent }}%</span>
              </div>
              <div class="progress" style="height: 8px;">
                <div
                  class="progress-bar"
                  :class="owner.color"
                  :style="{ width: owner.percent + '%' }"
                ></div>
              </div>
              <div class="d-flex justify-content-between mt-1">
                <small class="text-muted">{{ formatCurrency(owner.value) }}</small>
                <small class="text-muted">{{ owner.count }} entities</small>
              </div>
            </div>
          </div>
        </div>
      </b-col>

      <!-- Portfolio Alerts & Action Items -->
      <b-col xl="7" lg="12">
        <div class="card">
          <div class="card-header">
            <h4 class="header-title mb-0">Alerts & Action Items</h4>
          </div>
          <div class="card-body pt-0">
            <div class="alert alert-warning mb-2" v-for="alert in alerts" :key="alert.id">
              <div class="d-flex align-items-start">
                <i :class="['mdi', alert.icon, 'me-2', 'mt-1']" style="font-size: 20px;"></i>
                <div>
                  <h5 class="alert-heading mb-1">{{ alert.title }}</h5>
                  <p class="mb-0 small">{{ alert.description }}</p>
                  <small class="text-muted">{{ alert.due }}</small>
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
 * Snapshot View Component
 * 
 * WHAT: High-level portfolio summary showing aggregated metrics across
 *       all portfolio management areas (Fund, JV, Leverage, Cap Table, Waterfall)
 * 
 * WHY: Provides executives with a one-page overview of portfolio health,
 *      performance, and key action items without drilling into each section
 * 
 * WHERE: Default landing view in Portfolio Management dashboard
 * 
 * HOW: Aggregates data from all other views into summary cards, tables,
 *      and alerts. Backend integration via Pinia store (to be implemented)
 */
import { defineComponent, ref } from 'vue'

// WHAT: Define component using defineComponent for proper TypeScript support
// WHY: Ensures proper type inference and prevents interface naming errors
export default defineComponent({
  name: 'SnapshotView',
  setup() {
    // WHAT: Overall portfolio snapshot metrics
    // WHY: High-level KPIs for executive dashboard
    const snapshot = ref({
      totalAum: 850000000,
      aumGrowth: 14.2,
      fundCount: 3,
      fundDeployed: 78.5,
      jvCount: 5,
      jvCapital: 285000000,
      totalEquity: 625000000,
      stakeholderCount: 24,
      totalDebt: 425000000,
      facilityCount: 8,
      portfolioIrr: 18.7,
    })

    // WHAT: Fund-level summary data
    // WHY: Quick overview of each fund's performance
    const funds = ref([
      {
        id: 1,
        name: 'Fund I - Core Real Estate',
        vintage: '2020',
        committed: 250000000,
        deployedPercent: 92,
        nav: 285000000,
        irr: 18.7,
        moic: 1.58,
      },
      {
        id: 2,
        name: 'Fund II - Opportunistic',
        vintage: '2022',
        committed: 350000000,
        deployedPercent: 78,
        nav: 380000000,
        irr: 22.3,
        moic: 1.39,
      },
      {
        id: 3,
        name: 'Fund III - Value-Add',
        vintage: '2024',
        committed: 500000000,
        deployedPercent: 42,
        nav: 215000000,
        irr: 15.8,
        moic: 1.02,
      },
    ])

    // WHAT: Leverage summary metrics
    // WHY: Quick debt profile overview
    const leverageSummary = ref({
      totalDebt: 425000000,
      ltvRatio: 62.5,
      dscr: 1.45,
      weightedRate: 5.8,
      expiringCount: 2,
      expiringAmount: 85000000,
    })

    // WHAT: Active joint ventures
    // WHY: JV performance at a glance
    const jointVentures = ref([
      {
        id: 1,
        name: 'Oakwood Residential JV',
        ourShare: 50,
        totalCapital: 85000000,
        currentValue: 98500000,
        return: 15.9,
      },
      {
        id: 2,
        name: 'Gateway Industrial Partners',
        ourShare: 40,
        totalCapital: 120000000,
        currentValue: 135000000,
        return: 12.5,
      },
      {
        id: 3,
        name: 'Metro Mixed-Use Development',
        ourShare: 60,
        totalCapital: 95000000,
        currentValue: 102000000,
        return: 7.4,
      },
    ])

    // WHAT: Recent distribution history
    // WHY: Cash flow tracking
    const distributions = ref([
      {
        id: 1,
        date: 'Dec 15, 2024',
        entity: 'Fund I',
        type: 'Operating CF',
        amount: 4200000,
        status: 'Scheduled',
      },
      {
        id: 2,
        date: 'Nov 30, 2024',
        entity: 'Oakwood JV',
        type: 'Operating CF',
        amount: 2800000,
        status: 'Paid',
      },
      {
        id: 3,
        date: 'Nov 15, 2024',
        entity: 'Fund II',
        type: 'Return of Capital',
        amount: 5500000,
        status: 'Paid',
      },
    ])

    // WHAT: Ownership structure breakdown
    // WHY: Cap table summary
    const ownershipStructure = ref([
      { type: 'General Partners', percent: 22, value: 137500000, count: 3, color: 'bg-primary' },
      { type: 'Institutional LPs', percent: 48, value: 300000000, count: 8, color: 'bg-success' },
      { type: 'Co-Investors', percent: 20, value: 125000000, count: 9, color: 'bg-info' },
      { type: 'Individual LPs', percent: 10, value: 62500000, count: 4, color: 'bg-secondary' },
    ])

    // WHAT: Portfolio alerts and action items
    // WHY: Proactive management and compliance tracking
    const alerts = ref([
      {
        id: 1,
        icon: 'mdi-alert-circle',
        title: 'Debt Facility Expiring',
        description: 'Senior Credit Facility ($45M) expires in 90 days - refinance in progress',
        due: 'Due: Mar 15, 2025',
      },
      {
        id: 2,
        icon: 'mdi-calendar-check',
        title: 'Quarterly Distribution Pending',
        description: 'Fund I Q4 distribution ($4.2M) scheduled for approval',
        due: 'Review by: Dec 10, 2024',
      },
      {
        id: 3,
        icon: 'mdi-file-document-edit',
        title: 'LP Reporting Due',
        description: 'Q4 2024 investor reports due to limited partners',
        due: 'Due: Jan 15, 2025',
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
     * WHAT: Get color class for IRR display
     * WHY: Visual performance indicators
     */
    function getIrrColor(irr: number): string {
      if (irr >= 20) return 'text-success fw-bold'
      if (irr >= 15) return 'text-success'
      if (irr >= 10) return 'text-primary'
      return 'text-muted'
    }

    /**
     * WHAT: Get color class for LTV ratio
     * WHY: Risk-based color coding
     */
    function getLtvColor(ltv: number): string {
      if (ltv >= 75) return 'bg-danger'
      if (ltv >= 65) return 'bg-warning'
      return 'bg-success'
    }

    /**
     * WHAT: Get badge class for distribution status
     * WHY: Visual status indicators
     */
    function getDistStatusBadge(status: string): string {
      const map: { [key: string]: string } = {
        Paid: 'bg-success',
        Scheduled: 'bg-info',
        Processing: 'bg-warning',
        Pending: 'bg-secondary',
      }
      return map[status] || 'bg-secondary'
    }

    return {
      snapshot,
      funds,
      leverageSummary,
      jointVentures,
      distributions,
      ownershipStructure,
      alerts,
      formatCurrency,
      getIrrColor,
      getLtvColor,
      getDistStatusBadge,
    }
  },
})
</script>

<style scoped>
/**
 * Snapshot View Styles
 * Follows Hyper UI design system
 */
.widget-icon {
  height: 40px;
  width: 40px;
  text-align: center;
  line-height: 40px;
  font-size: 20px;
  border-radius: 4px;
}

.bg-purple-lighten {
  background-color: rgba(114, 124, 245, 0.18);
}

.text-purple {
  color: #727cf5;
}
</style>
