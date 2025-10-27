<template>
  <!--
    Joint Venture (JV) Level View
    Displays JV partnership metrics, capital contributions, performance tracking
    Manages JV agreements, partner allocations, and distribution schedules
  -->
  <div class="jv-level-view">
    <!-- JV Selector -->
    <b-row class="mb-3">
      <b-col cols="12">
        <div class="d-flex align-items-center gap-3 flex-wrap">
          <label class="fw-bold mb-0">Select Joint Venture:</label>
          <select v-model="selectedJv" class="form-select" style="max-width: 350px;">
            <option :value="null">-- Select a JV --</option>
            <option v-for="jv in jointVentures" :key="jv.id" :value="jv.id">
              {{ jv.name }}
            </option>
          </select>
          <button class="btn btn-sm btn-success">
            <i class="mdi mdi-plus-circle me-1"></i> New JV
          </button>
        </div>
      </b-col>
    </b-row>

    <!-- JV Summary Cards -->
    <b-row class="g-2 mb-3">
      <!-- Total JV Capital -->
      <b-col xl="3" lg="6" md="6">
        <div class="card widget-flat">
          <div class="card-body">
            <div class="float-end">
              <i class="mdi mdi-handshake widget-icon bg-primary-lighten text-primary"></i>
            </div>
            <h5 class="text-muted fw-normal mt-0" title="Total JV Capital">JV Capital</h5>
            <h3 class="mt-3 mb-3">{{ formatCurrency(jvStats.totalCapital) }}</h3>
            <p class="mb-0 text-muted">
              <span class="text-nowrap">{{ jvStats.partnerCount }} Partners</span>
            </p>
          </div>
        </div>
      </b-col>

      <!-- Our Contribution -->
      <b-col xl="3" lg="6" md="6">
        <div class="card widget-flat">
          <div class="card-body">
            <div class="float-end">
              <i class="mdi mdi-account-cash widget-icon bg-success-lighten text-success"></i>
            </div>
            <h5 class="text-muted fw-normal mt-0" title="Our Contribution">
              Our Contribution
            </h5>
            <h3 class="mt-3 mb-3">{{ formatCurrency(jvStats.ourContribution) }}</h3>
            <p class="mb-0 text-muted">
              <span class="text-success me-2">{{ jvStats.ourOwnership }}%</span>
              <span class="text-nowrap">Ownership</span>
            </p>
          </div>
        </div>
      </b-col>

      <!-- Current Value -->
      <b-col xl="3" lg="6" md="6">
        <div class="card widget-flat">
          <div class="card-body">
            <div class="float-end">
              <i class="mdi mdi-chart-line-variant widget-icon bg-warning-lighten text-warning"></i>
            </div>
            <h5 class="text-muted fw-normal mt-0" title="Current JV Value">
              Current Value
            </h5>
            <h3 class="mt-3 mb-3">{{ formatCurrency(jvStats.currentValue) }}</h3>
            <p class="mb-0 text-muted">
              <span class="text-success me-2">
                <i class="mdi mdi-arrow-up-bold"></i> {{ jvStats.valueGrowth }}%
              </span>
              <span class="text-nowrap">Growth</span>
            </p>
          </div>
        </div>
      </b-col>

      <!-- Distributions -->
      <b-col xl="3" lg="6" md="6">
        <div class="card widget-flat">
          <div class="card-body">
            <div class="float-end">
              <i class="mdi mdi-cash-multiple widget-icon bg-info-lighten text-info"></i>
            </div>
            <h5 class="text-muted fw-normal mt-0" title="Total Distributions">
              Distributions
            </h5>
            <h3 class="mt-3 mb-3">{{ formatCurrency(jvStats.distributions) }}</h3>
            <p class="mb-0 text-muted">
              <span class="text-nowrap">{{ jvStats.distributionCount }} Payments</span>
            </p>
          </div>
        </div>
      </b-col>
    </b-row>

    <!-- Partner Contributions & JV Agreement -->
    <b-row class="g-2 mb-3">
      <!-- Partner Contributions Table -->
      <b-col xl="7" lg="12">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h4 class="header-title mb-0">Partner Contributions</h4>
            <button class="btn btn-sm btn-primary">
              <i class="mdi mdi-pencil me-1"></i> Edit Partners
            </button>
          </div>
          <div class="card-body pt-0">
            <div class="table-responsive">
              <table class="table table-centered table-nowrap table-hover mb-0">
                <thead>
                  <tr>
                    <th>Partner</th>
                    <th>Type</th>
                    <th>Contribution</th>
                    <th>Ownership %</th>
                    <th>Distributions</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="partner in partners" :key="partner.id">
                    <td>
                      <div class="d-flex align-items-center">
                        <div class="flex-shrink-0">
                          <div class="avatar-sm">
                            <span :class="['avatar-title rounded-circle', partner.avatarColor]">
                              {{ partner.initials }}
                            </span>
                          </div>
                        </div>
                        <div class="flex-grow-1 ms-2">
                          <h5 class="my-0 fw-normal">{{ partner.name }}</h5>
                        </div>
                      </div>
                    </td>
                    <td>{{ partner.type }}</td>
                    <td>{{ formatCurrency(partner.contribution) }}</td>
                    <td>
                      <div class="progress" style="height: 6px;">
                        <div
                          class="progress-bar bg-primary"
                          :style="{ width: partner.ownership + '%' }"
                        ></div>
                      </div>
                      <span class="small">{{ partner.ownership }}%</span>
                    </td>
                    <td>{{ formatCurrency(partner.distributions) }}</td>
                    <td>
                      <span :class="['badge', getPartnerStatusBadge(partner.status)]">
                        {{ partner.status }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </b-col>

      <!-- JV Agreement Details -->
      <b-col xl="5" lg="12">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h4 class="header-title mb-0">JV Agreement</h4>
            <button class="btn btn-sm btn-link p-0">
              <i class="mdi mdi-file-document-outline"></i> View Agreement
            </button>
          </div>
          <div class="card-body pt-0">
            <div class="mb-3">
              <h5 class="text-muted fw-normal mb-1">Structure</h5>
              <p class="mb-0 fw-semibold">{{ agreement.structure }}</p>
            </div>
            <div class="mb-3">
              <h5 class="text-muted fw-normal mb-1">Term</h5>
              <p class="mb-0">{{ agreement.term }}</p>
            </div>
            <div class="mb-3">
              <h5 class="text-muted fw-normal mb-1">Waterfall Type</h5>
              <p class="mb-0">{{ agreement.waterfallType }}</p>
            </div>
            <div class="mb-3">
              <h5 class="text-muted fw-normal mb-1">Preferred Return</h5>
              <p class="mb-0 text-success fw-semibold">{{ agreement.preferredReturn }}%</p>
            </div>
            <div class="mb-3">
              <h5 class="text-muted fw-normal mb-1">Promote Split</h5>
              <p class="mb-0">{{ agreement.promoteSplit }}</p>
            </div>
            <div class="mb-3">
              <h5 class="text-muted fw-normal mb-1">Key Dates</h5>
              <ul class="list-unstyled mb-0">
                <li>
                  <small class="text-muted">Formation:</small> {{ agreement.formationDate }}
                </li>
                <li>
                  <small class="text-muted">Maturity:</small> {{ agreement.maturityDate }}
                </li>
              </ul>
            </div>
          </div>
        </div>
      </b-col>
    </b-row>

    <!-- Capital Calls & Distribution Schedule -->
    <b-row class="g-2">
      <!-- Capital Calls History -->
      <b-col xl="6" lg="12">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h4 class="header-title mb-0">Capital Calls</h4>
            <button class="btn btn-sm btn-primary">
              <i class="mdi mdi-plus-circle me-1"></i> New Capital Call
            </button>
          </div>
          <div class="card-body pt-0">
            <div class="table-responsive">
              <table class="table table-sm table-centered table-nowrap mb-0">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Amount</th>
                    <th>Purpose</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="call in capitalCalls" :key="call.id">
                    <td>{{ call.date }}</td>
                    <td>{{ formatCurrency(call.amount) }}</td>
                    <td>{{ call.purpose }}</td>
                    <td>
                      <span :class="['badge', getCallStatusBadge(call.status)]">
                        {{ call.status }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </b-col>

      <!-- Distribution Schedule -->
      <b-col xl="6" lg="12">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h4 class="header-title mb-0">Distribution Schedule</h4>
            <button class="btn btn-sm btn-success">
              <i class="mdi mdi-calendar-plus me-1"></i> Schedule Distribution
            </button>
          </div>
          <div class="card-body pt-0">
            <div class="table-responsive">
              <table class="table table-sm table-centered table-nowrap mb-0">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Amount</th>
                    <th>Type</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="dist in distributions" :key="dist.id">
                    <td>{{ dist.date }}</td>
                    <td>{{ formatCurrency(dist.amount) }}</td>
                    <td>{{ dist.type }}</td>
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
  </div>
</template>

<script lang="ts">
/**
 * JV Level View Component
 * 
 * WHAT: Displays joint venture partnership details, partner contributions,
 *       capital calls, distribution schedules, and JV agreement terms
 * 
 * WHY: Manages complex multi-partner investment structures with detailed
 *      tracking of contributions, ownership splits, and waterfall distributions
 * 
 * WHERE: Rendered within Portfolio Management dashboard's JV Level tab
 * 
 * HOW: Uses Hyper UI tables, cards, and widgets to display JV data
 *      Backend integration via Pinia store (to be implemented)
 */
import { ref } from 'vue'

// WHAT: Type definition for joint venture entity
interface JointVenture {
  id: number
  name: string
}

// WHAT: Type definition for JV partner
interface Partner {
  id: number
  name: string
  initials: string
  avatarColor: string
  type: string
  contribution: number
  ownership: number
  distributions: number
  status: string
}

// WHAT: Type definition for capital call
interface CapitalCall {
  id: number
  date: string
  amount: number
  purpose: string
  status: string
}

// WHAT: Type definition for distribution
interface Distribution {
  id: number
  date: string
  amount: number
  type: string
  status: string
}

export default {
  name: 'JvLevelView',
  setup() {
    // WHAT: Selected JV ID
    // WHY: Controls which JV's data is displayed
    const selectedJv = ref<number | null>(null)

    // WHAT: List of available joint ventures
    // TODO: Fetch from backend via Pinia store
    const jointVentures = ref<JointVenture[]>([
      { id: 1, name: 'Oakwood Residential JV' },
      { id: 2, name: 'Gateway Industrial Partners' },
      { id: 3, name: 'Metro Mixed-Use Development' },
    ])

    // WHAT: JV-level statistics
    // WHY: Summary metrics for selected JV
    const jvStats = ref({
      totalCapital: 85000000,
      partnerCount: 4,
      ourContribution: 42500000,
      ourOwnership: 50,
      currentValue: 98500000,
      valueGrowth: 15.9,
      distributions: 8500000,
      distributionCount: 6,
    })

    // WHAT: Partner contribution details
    // WHY: Shows capital structure and ownership breakdown
    const partners = ref<Partner[]>([
      {
        id: 1,
        name: 'Our Fund (GP)',
        initials: 'GP',
        avatarColor: 'bg-primary',
        type: 'General Partner',
        contribution: 42500000,
        ownership: 50.0,
        distributions: 4250000,
        status: 'Active',
      },
      {
        id: 2,
        name: 'Institutional Investor LP',
        initials: 'II',
        avatarColor: 'bg-success',
        type: 'Limited Partner',
        contribution: 25500000,
        ownership: 30.0,
        distributions: 2550000,
        status: 'Active',
      },
      {
        id: 3,
        name: 'Family Office Partners',
        initials: 'FO',
        avatarColor: 'bg-warning',
        type: 'Limited Partner',
        contribution: 12750000,
        ownership: 15.0,
        distributions: 1275000,
        status: 'Active',
      },
      {
        id: 4,
        name: 'Strategic Co-Investor',
        initials: 'SC',
        avatarColor: 'bg-info',
        type: 'Co-Investor',
        contribution: 4250000,
        ownership: 5.0,
        distributions: 425000,
        status: 'Active',
      },
    ])

    // WHAT: JV agreement terms
    // WHY: Displays legal and financial structure of the JV
    const agreement = ref({
      structure: 'Limited Partnership',
      term: '7 years + 2 year extensions',
      waterfallType: 'European (Whole Fund)',
      preferredReturn: 8.0,
      promoteSplit: '80/20 after 8% pref',
      formationDate: 'Jan 15, 2022',
      maturityDate: 'Jan 14, 2029',
    })

    // WHAT: Capital call history
    // WHY: Tracks when partners need to contribute additional capital
    const capitalCalls = ref<CapitalCall[]>([
      {
        id: 1,
        date: 'Oct 1, 2024',
        amount: 15000000,
        purpose: 'Property Acquisition',
        status: 'Funded',
      },
      {
        id: 2,
        date: 'Jul 15, 2024',
        amount: 8500000,
        purpose: 'Construction Costs',
        status: 'Funded',
      },
      {
        id: 3,
        date: 'Apr 1, 2024',
        amount: 12000000,
        purpose: 'Initial Capital',
        status: 'Funded',
      },
      {
        id: 4,
        date: 'Dec 15, 2024',
        amount: 6000000,
        purpose: 'Operating Reserve',
        status: 'Pending',
      },
    ])

    // WHAT: Distribution schedule
    // WHY: Shows past and planned distributions to partners
    const distributions = ref<Distribution[]>([
      {
        id: 1,
        date: 'Dec 31, 2024',
        amount: 3200000,
        type: 'Operating Cash Flow',
        status: 'Scheduled',
      },
      {
        id: 2,
        date: 'Sep 30, 2024',
        amount: 2800000,
        type: 'Operating Cash Flow',
        status: 'Paid',
      },
      {
        id: 3,
        date: 'Jun 30, 2024',
        amount: 2500000,
        type: 'Operating Cash Flow',
        status: 'Paid',
      },
      {
        id: 4,
        date: 'Mar 31, 2024',
        amount: 1800000,
        type: 'Return of Capital',
        status: 'Paid',
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
     * WHAT: Get badge class for partner status
     * WHY: Visual status indicators
     */
    function getPartnerStatusBadge(status: string): string {
      const map: { [key: string]: string } = {
        Active: 'bg-success',
        Pending: 'bg-warning',
        Inactive: 'bg-secondary',
      }
      return map[status] || 'bg-secondary'
    }

    /**
     * WHAT: Get badge class for capital call status
     * WHY: Visual status indicators
     */
    function getCallStatusBadge(status: string): string {
      const map: { [key: string]: string } = {
        Funded: 'bg-success',
        Pending: 'bg-warning',
        Overdue: 'bg-danger',
      }
      return map[status] || 'bg-secondary'
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
      }
      return map[status] || 'bg-secondary'
    }

    return {
      selectedJv,
      jointVentures,
      jvStats,
      partners,
      agreement,
      capitalCalls,
      distributions,
      formatCurrency,
      getPartnerStatusBadge,
      getCallStatusBadge,
      getDistStatusBadge,
    }
  },
}
</script>

<style scoped>
/**
 * JV Level View Styles
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

.avatar-sm {
  height: 2.5rem;
  width: 2.5rem;
}

.avatar-title {
  align-items: center;
  background-color: #727cf5;
  color: #fff;
  display: flex;
  font-weight: 500;
  height: 100%;
  justify-content: center;
  width: 100%;
}
</style>
