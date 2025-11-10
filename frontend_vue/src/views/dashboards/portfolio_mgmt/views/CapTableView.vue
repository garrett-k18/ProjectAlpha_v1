<template>
  <!--
    Capitalization Table View
    Displays ownership structure, equity stakes, dilution tracking
    Manages investor rights, share classes, and equity transactions
  -->
  <div class="cap-table-view">
    <!-- Entity Selector & Controls -->
    <b-row class="mb-3">
      <b-col cols="12">
        <div class="d-flex align-items-center gap-3 flex-wrap justify-content-between">
          <div class="d-flex align-items-center gap-3">
            <label class="fw-bold mb-0">Select Entity:</label>
            <select v-model="selectedEntity" class="form-select" style="max-width: 350px;">
              <option :value="null">-- Select an Entity --</option>
              <option v-for="entity in entities" :key="entity.id" :value="entity.id">
                {{ entity.name }}
              </option>
            </select>
          </div>
          <div class="d-flex gap-2">
            <button class="btn btn-sm btn-primary">
              <i class="mdi mdi-plus-circle me-1"></i> Add Stakeholder
            </button>
            <button class="btn btn-sm btn-success">
              <i class="mdi mdi-file-document-edit me-1"></i> Record Transaction
            </button>
            <button class="btn btn-sm btn-secondary">
              <i class="mdi mdi-download me-1"></i> Export Cap Table
            </button>
          </div>
        </div>
      </b-col>
    </b-row>

    <!-- Cap Table Summary Cards -->
    <b-row class="g-2 mb-3">
      <!-- Total Equity Value -->
      <b-col xl="3" lg="6" md="6">
        <div class="card widget-flat">
          <div class="card-body">
            <div class="float-end">
              <i class="mdi mdi-currency-usd widget-icon bg-success-lighten text-success"></i>
            </div>
            <h5 class="text-muted fw-normal mt-0" title="Total Equity Value">
              Equity Value
            </h5>
            <h3 class="mt-3 mb-3">{{ formatCurrency(capStats.totalEquityValue) }}</h3>
            <p class="mb-0 text-muted">
              <span class="text-nowrap">Post-Money Valuation</span>
            </p>
          </div>
        </div>
      </b-col>

      <!-- Total Shares Outstanding -->
      <b-col xl="3" lg="6" md="6">
        <div class="card widget-flat">
          <div class="card-body">
            <div class="float-end">
              <i class="mdi mdi-chart-pie widget-icon bg-primary-lighten text-primary"></i>
            </div>
            <h5 class="text-muted fw-normal mt-0" title="Total Shares Outstanding">
              Shares Outstanding
            </h5>
            <h3 class="mt-3 mb-3">{{ formatNumber(capStats.sharesOutstanding) }}</h3>
            <p class="mb-0 text-muted">
              <span class="text-nowrap">{{ capStats.shareClasses }} Share Classes</span>
            </p>
          </div>
        </div>
      </b-col>

      <!-- Price Per Share -->
      <b-col xl="3" lg="6" md="6">
        <div class="card widget-flat">
          <div class="card-body">
            <div class="float-end">
              <i class="mdi mdi-tag widget-icon bg-warning-lighten text-warning"></i>
            </div>
            <h5 class="text-muted fw-normal mt-0" title="Price Per Share">
              Price Per Share
            </h5>
            <h3 class="mt-3 mb-3">{{ formatCurrency(capStats.pricePerShare) }}</h3>
            <p class="mb-0 text-muted">
              <span class="text-success me-2">
                <i class="mdi mdi-arrow-up-bold"></i> {{ capStats.priceChange }}%
              </span>
              <span class="text-nowrap">Last Round</span>
            </p>
          </div>
        </div>
      </b-col>

      <!-- Total Stakeholders -->
      <b-col xl="3" lg="6" md="6">
        <div class="card widget-flat">
          <div class="card-body">
            <div class="float-end">
              <i class="mdi mdi-account-group widget-icon bg-info-lighten text-info"></i>
            </div>
            <h5 class="text-muted fw-normal mt-0" title="Total Stakeholders">
              Stakeholders
            </h5>
            <h3 class="mt-3 mb-3">{{ capStats.totalStakeholders }}</h3>
            <p class="mb-0 text-muted">
              <span class="text-nowrap">{{ capStats.activeStakeholders }} Active</span>
            </p>
          </div>
        </div>
      </b-col>
    </b-row>

    <!-- Cap Table & Ownership Breakdown -->
    <b-row class="g-2 mb-3">
      <!-- Main Cap Table -->
      <b-col cols="12">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h4 class="header-title mb-0">Capitalization Table</h4>
            <div class="d-flex gap-2">
              <button class="btn btn-sm btn-outline-primary">
                <i class="mdi mdi-filter me-1"></i> Filter
              </button>
              <button class="btn btn-sm btn-outline-secondary">
                <i class="mdi mdi-eye-off me-1"></i> Show Diluted
              </button>
            </div>
          </div>
          <div class="card-body pt-0">
            <div class="table-responsive">
              <table class="table table-centered table-nowrap table-hover mb-0">
                <thead>
                  <tr>
                    <th>Stakeholder</th>
                    <th>Type</th>
                    <th>Share Class</th>
                    <th>Shares</th>
                    <th>Ownership %</th>
                    <th>Investment</th>
                    <th>Current Value</th>
                    <th>Return</th>
                    <th>Rights</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="holder in stakeholders" :key="holder.id">
                    <td>
                      <div class="d-flex align-items-center">
                        <div class="flex-shrink-0">
                          <div class="avatar-sm">
                            <span :class="['avatar-title rounded-circle', holder.avatarColor]">
                              {{ holder.initials }}
                            </span>
                          </div>
                        </div>
                        <div class="flex-grow-1 ms-2">
                          <h5 class="my-0 fw-normal">{{ holder.name }}</h5>
                          <small class="text-muted">{{ holder.role }}</small>
                        </div>
                      </div>
                    </td>
                    <td>
                      <span :class="['badge', getStakeholderTypeBadge(holder.type)]">
                        {{ holder.type }}
                      </span>
                    </td>
                    <td>{{ holder.shareClass }}</td>
                    <td>{{ formatNumber(holder.shares) }}</td>
                    <td>
                      <div class="progress" style="height: 6px;">
                        <div
                          class="progress-bar bg-primary"
                          :style="{ width: holder.ownershipPercent + '%' }"
                        ></div>
                      </div>
                      <span class="small fw-semibold">{{ holder.ownershipPercent.toFixed(2) }}%</span>
                    </td>
                    <td>{{ formatCurrency(holder.investment) }}</td>
                    <td class="fw-semibold">{{ formatCurrency(holder.currentValue) }}</td>
                    <td>
                      <span :class="holder.returnMultiple >= 1 ? 'text-success' : 'text-danger'">
                        {{ holder.returnMultiple.toFixed(2) }}x
                      </span>
                    </td>
                    <td>
                      <div class="d-flex gap-1">
                        <span v-if="holder.hasVoting" class="badge bg-info-lighten text-info" title="Voting Rights">
                          V
                        </span>
                        <span v-if="holder.hasProRata" class="badge bg-success-lighten text-success" title="Pro-Rata Rights">
                          PR
                        </span>
                        <span v-if="holder.hasBoard" class="badge bg-warning-lighten text-warning" title="Board Seat">
                          B
                        </span>
                      </div>
                    </td>
                  </tr>
                </tbody>
                <tfoot class="table-light">
                  <tr class="fw-bold">
                    <td colspan="3">Total</td>
                    <td>{{ formatNumber(capStats.sharesOutstanding) }}</td>
                    <td>100.00%</td>
                    <td>{{ formatCurrency(totalInvestment) }}</td>
                    <td>{{ formatCurrency(capStats.totalEquityValue) }}</td>
                    <td></td>
                    <td></td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>
        </div>
      </b-col>
    </b-row>

    <!-- Ownership Visualization & Share Classes -->
    <b-row class="g-2 mb-3">
      <!-- Ownership Pie Chart Placeholder -->
      <b-col xl="5" lg="12">
        <div class="card">
          <div class="card-header">
            <h4 class="header-title mb-0">Ownership Breakdown</h4>
          </div>
          <div class="card-body">
            <!-- Placeholder for pie/donut chart -->
            <div class="text-center py-4">
              <i class="mdi mdi-chart-donut" style="font-size: 64px; color: #727cf5;"></i>
              <p class="text-muted mt-2">Ownership visualization chart will be integrated here</p>
            </div>
            <!-- Ownership Summary List -->
            <div class="mt-3">
              <div v-for="group in ownershipGroups" :key="group.type" class="mb-2">
                <div class="d-flex justify-content-between mb-1">
                  <span class="fw-semibold">{{ group.type }}</span>
                  <span class="text-muted">{{ group.percent }}%</span>
                </div>
                <div class="progress" style="height: 8px;">
                  <div
                    class="progress-bar"
                    :class="group.color"
                    :style="{ width: group.percent + '%' }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </b-col>

      <!-- Share Classes -->
      <b-col xl="7" lg="12">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h4 class="header-title mb-0">Share Classes</h4>
            <button class="btn btn-sm btn-primary">
              <i class="mdi mdi-plus-circle me-1"></i> Add Share Class
            </button>
          </div>
          <div class="card-body pt-0">
            <div class="table-responsive">
              <table class="table table-sm table-centered table-nowrap mb-0">
                <thead>
                  <tr>
                    <th>Class</th>
                    <th>Type</th>
                    <th>Shares Issued</th>
                    <th>Price</th>
                    <th>Voting Rights</th>
                    <th>Liquidation Preference</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="shareClass in shareClasses" :key="shareClass.id">
                    <td>
                      <span class="badge bg-primary">{{ shareClass.name }}</span>
                    </td>
                    <td>{{ shareClass.type }}</td>
                    <td>{{ formatNumber(shareClass.sharesIssued) }}</td>
                    <td>{{ formatCurrency(shareClass.price) }}</td>
                    <td>{{ shareClass.votingRights }}</td>
                    <td>{{ shareClass.liquidationPref }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </b-col>
    </b-row>

    <!-- Equity Transactions & Dilution History -->
    <b-row class="g-2">
      <!-- Recent Equity Transactions -->
      <b-col xl="6" lg="12">
        <div class="card">
          <div class="card-header">
            <h4 class="header-title mb-0">Recent Equity Transactions</h4>
          </div>
          <div class="card-body pt-0">
            <div class="table-responsive">
              <table class="table table-sm table-centered table-nowrap mb-0">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Type</th>
                    <th>Stakeholder</th>
                    <th>Shares</th>
                    <th>Value</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="txn in transactions" :key="txn.id">
                    <td>{{ txn.date }}</td>
                    <td>
                      <span :class="['badge', getTransactionTypeBadge(txn.type)]">
                        {{ txn.type }}
                      </span>
                    </td>
                    <td>{{ txn.stakeholder }}</td>
                    <td>{{ formatNumber(txn.shares) }}</td>
                    <td>{{ formatCurrency(txn.value) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </b-col>

      <!-- Dilution History -->
      <b-col xl="6" lg="12">
        <div class="card">
          <div class="card-header">
            <h4 class="header-title mb-0">Dilution History</h4>
          </div>
          <div class="card-body pt-0">
            <div class="table-responsive">
              <table class="table table-sm table-centered table-nowrap mb-0">
                <thead>
                  <tr>
                    <th>Round</th>
                    <th>Date</th>
                    <th>Pre-Money</th>
                    <th>Amount Raised</th>
                    <th>Post-Money</th>
                    <th>Dilution</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="round in dilutionHistory" :key="round.id">
                    <td>
                      <span class="badge bg-primary">{{ round.name }}</span>
                    </td>
                    <td>{{ round.date }}</td>
                    <td>{{ formatCurrency(round.preMoney) }}</td>
                    <td>{{ formatCurrency(round.raised) }}</td>
                    <td>{{ formatCurrency(round.postMoney) }}</td>
                    <td>
                      <span class="text-danger">-{{ round.dilution }}%</span>
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
 * Cap Table View Component
 * 
 * WHAT: Displays capitalization table with ownership stakes, share classes,
 *       equity transactions, and dilution tracking
 * 
 * WHY: Essential for managing equity structure in private equity, venture capital,
 *      and real estate funds. Tracks investor rights, share classes, and ownership changes
 * 
 * WHERE: Rendered within Portfolio Management dashboard's Cap Table tab
 * 
 * HOW: Uses Hyper UI tables and visualizations to display complex equity structures
 *      Backend integration via Pinia store (to be implemented)
 */
import { defineComponent, ref, computed } from 'vue'

// WHAT: Type definition for entity
// WHY: Defines structure for entity selection
interface Entity {
  id: number
  name: string
}

// WHAT: Type definition for stakeholder
// WHY: Defines structure for stakeholder equity holdings
interface Stakeholder {
  id: number
  name: string
  initials: string
  avatarColor: string
  role: string
  type: string
  shareClass: string
  shares: number
  ownershipPercent: number
  investment: number
  currentValue: number
  returnMultiple: number
  hasVoting: boolean
  hasProRata: boolean
  hasBoard: boolean
}

// WHAT: Type definition for share class
// WHY: Defines structure for share class definitions
interface ShareClass {
  id: number
  name: string
  type: string
  sharesIssued: number
  price: number
  votingRights: string
  liquidationPref: string
}

// WHAT: Type definition for equity transaction
// WHY: Defines structure for equity transaction history
interface Transaction {
  id: number
  date: string
  type: string
  stakeholder: string
  shares: number
  value: number
}

// WHAT: Type definition for dilution round
// WHY: Defines structure for dilution history tracking
interface DilutionRound {
  id: number
  name: string
  date: string
  preMoney: number
  raised: number
  postMoney: number
  dilution: number
}

// WHAT: Define component using defineComponent for proper TypeScript support
// WHY: Ensures proper type inference and prevents interface naming errors
export default defineComponent({
  name: 'CapTableView',
  setup() {
    // WHAT: Selected entity ID
    // WHY: Controls which entity's cap table is displayed
    const selectedEntity = ref<number | null>(null)

    // WHAT: List of available entities
    // TODO: Fetch from backend
    const entities = ref<Entity[]>([
      { id: 1, name: 'Fund I - Core Real Estate' },
      { id: 2, name: 'Oakwood Residential JV' },
      { id: 3, name: 'Gateway Industrial SPV' },
    ])

    // WHAT: Cap table summary statistics
    // WHY: High-level equity metrics
    const capStats = ref({
      totalEquityValue: 285000000,
      sharesOutstanding: 10000000,
      shareClasses: 3,
      pricePerShare: 28.50,
      priceChange: 14.2,
      totalStakeholders: 12,
      activeStakeholders: 12,
    })

    // WHAT: Stakeholder equity holdings
    // WHY: Main cap table data showing ownership breakdown
    const stakeholders = ref<Stakeholder[]>([
      {
        id: 1,
        name: 'General Partner',
        initials: 'GP',
        avatarColor: 'bg-primary',
        role: 'Fund Manager',
        type: 'GP',
        shareClass: 'Class A',
        shares: 2000000,
        ownershipPercent: 20.0,
        investment: 10000000,
        currentValue: 57000000,
        returnMultiple: 5.7,
        hasVoting: true,
        hasProRata: false,
        hasBoard: true,
      },
      {
        id: 2,
        name: 'Institutional LP #1',
        initials: 'IL',
        avatarColor: 'bg-success',
        role: 'Limited Partner',
        type: 'LP',
        shareClass: 'Class B',
        shares: 3000000,
        ownershipPercent: 30.0,
        investment: 50000000,
        currentValue: 85500000,
        returnMultiple: 1.71,
        hasVoting: true,
        hasProRata: true,
        hasBoard: true,
      },
      {
        id: 3,
        name: 'Family Office Partners',
        initials: 'FO',
        avatarColor: 'bg-warning',
        role: 'Limited Partner',
        type: 'LP',
        shareClass: 'Class B',
        shares: 2500000,
        ownershipPercent: 25.0,
        investment: 40000000,
        currentValue: 71250000,
        returnMultiple: 1.78,
        hasVoting: true,
        hasProRata: true,
        hasBoard: false,
      },
      {
        id: 4,
        name: 'Strategic Co-Investor',
        initials: 'SC',
        avatarColor: 'bg-info',
        role: 'Co-Investor',
        type: 'Co-Inv',
        shareClass: 'Class C',
        shares: 1500000,
        ownershipPercent: 15.0,
        investment: 25000000,
        currentValue: 42750000,
        returnMultiple: 1.71,
        hasVoting: false,
        hasProRata: true,
        hasBoard: false,
      },
      {
        id: 5,
        name: 'Individual Investors',
        initials: 'II',
        avatarColor: 'bg-secondary',
        role: 'Limited Partner',
        type: 'LP',
        shareClass: 'Class B',
        shares: 1000000,
        ownershipPercent: 10.0,
        investment: 15000000,
        currentValue: 28500000,
        returnMultiple: 1.9,
        hasVoting: false,
        hasProRata: false,
        hasBoard: false,
      },
    ])

    // WHAT: Ownership grouped by stakeholder type
    // WHY: Visual breakdown for pie chart
    const ownershipGroups = ref([
      { type: 'General Partner', percent: 20.0, color: 'bg-primary' },
      { type: 'Institutional LPs', percent: 55.0, color: 'bg-success' },
      { type: 'Co-Investors', percent: 15.0, color: 'bg-info' },
      { type: 'Individual LPs', percent: 10.0, color: 'bg-secondary' },
    ])

    // WHAT: Share class definitions
    // WHY: Shows different equity instruments and their terms
    const shareClasses = ref<ShareClass[]>([
      {
        id: 1,
        name: 'Class A',
        type: 'Common',
        sharesIssued: 2000000,
        price: 28.50,
        votingRights: '10 votes per share',
        liquidationPref: 'None',
      },
      {
        id: 2,
        name: 'Class B',
        type: 'Preferred',
        sharesIssued: 6500000,
        price: 28.50,
        votingRights: '1 vote per share',
        liquidationPref: '1x non-participating',
      },
      {
        id: 3,
        name: 'Class C',
        type: 'Common',
        sharesIssued: 1500000,
        price: 28.50,
        votingRights: 'Non-voting',
        liquidationPref: 'None',
      },
    ])

    // WHAT: Recent equity transactions
    // WHY: Audit trail of share transfers and issuances
    const transactions = ref<Transaction[]>([
      {
        id: 1,
        date: 'Nov 15, 2024',
        type: 'Issuance',
        stakeholder: 'Strategic Co-Investor',
        shares: 500000,
        value: 14250000,
      },
      {
        id: 2,
        date: 'Sep 1, 2024',
        type: 'Transfer',
        stakeholder: 'Family Office Partners',
        shares: 250000,
        value: 7125000,
      },
      {
        id: 3,
        date: 'Jun 30, 2024',
        type: 'Issuance',
        stakeholder: 'Institutional LP #1',
        shares: 1000000,
        value: 28500000,
      },
    ])

    // WHAT: Financing rounds and dilution history
    // WHY: Shows how ownership has changed over time
    const dilutionHistory = ref<DilutionRound[]>([
      {
        id: 1,
        name: 'Series C',
        date: 'Nov 2024',
        preMoney: 260000000,
        raised: 25000000,
        postMoney: 285000000,
        dilution: 8.8,
      },
      {
        id: 2,
        name: 'Series B',
        date: 'Mar 2023',
        preMoney: 180000000,
        raised: 40000000,
        postMoney: 220000000,
        dilution: 18.2,
      },
      {
        id: 3,
        name: 'Series A',
        date: 'Jan 2022',
        preMoney: 100000000,
        raised: 50000000,
        postMoney: 150000000,
        dilution: 33.3,
      },
    ])

    // WHAT: Computed total investment across all stakeholders
    // WHY: Used in cap table footer
    const totalInvestment = computed(() => {
      return stakeholders.value.reduce((sum, sh) => sum + sh.investment, 0)
    })

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
     * WHAT: Format number with commas
     * WHY: Readable large numbers (shares)
     */
    function formatNumber(value: number): string {
      return new Intl.NumberFormat('en-US').format(value)
    }

    /**
     * WHAT: Get badge class for stakeholder type
     * WHY: Visual categorization
     */
    function getStakeholderTypeBadge(type: string): string {
      const map: { [key: string]: string } = {
        GP: 'bg-primary',
        LP: 'bg-success',
        'Co-Inv': 'bg-info',
      }
      return map[type] || 'bg-secondary'
    }

    /**
     * WHAT: Get badge class for transaction type
     * WHY: Visual indicators for different transaction types
     */
    function getTransactionTypeBadge(type: string): string {
      const map: { [key: string]: string } = {
        Issuance: 'bg-success',
        Transfer: 'bg-info',
        Repurchase: 'bg-warning',
        Cancellation: 'bg-danger',
      }
      return map[type] || 'bg-secondary'
    }

    return {
      selectedEntity,
      entities,
      capStats,
      stakeholders,
      ownershipGroups,
      shareClasses,
      transactions,
      dilutionHistory,
      totalInvestment,
      formatCurrency,
      formatNumber,
      getStakeholderTypeBadge,
      getTransactionTypeBadge,
    }
  },
})
</script>

<style scoped>
/**
 * Cap Table View Styles
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
