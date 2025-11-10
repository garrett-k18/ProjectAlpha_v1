<template>
  <!--
    Waterfall View
    Displays waterfall distribution calculations for investments
    Shows tier-by-tier cash flow allocation and promote calculations
  -->
  <div class="waterfall-view">
    <!-- Investment Selector & Controls -->
    <b-row class="mb-3">
      <b-col cols="12">
        <div class="d-flex align-items-center gap-3 flex-wrap justify-content-between">
          <div class="d-flex align-items-center gap-3">
            <label class="fw-bold mb-0">Select Investment:</label>
            <select v-model="selectedInvestment" class="form-select" style="max-width: 350px;">
              <option :value="null">-- Select an Investment --</option>
              <option v-for="inv in investments" :key="inv.id" :value="inv.id">
                {{ inv.name }}
              </option>
            </select>
          </div>
          <div class="d-flex gap-2">
            <button class="btn btn-sm btn-primary">
              <i class="mdi mdi-calculator me-1"></i> Run Waterfall
            </button>
            <button class="btn btn-sm btn-secondary">
              <i class="mdi mdi-download me-1"></i> Export
            </button>
          </div>
        </div>
      </b-col>
    </b-row>

    <!-- Waterfall Summary Cards -->
    <b-row class="g-2 mb-3">
      <!-- Total Proceeds -->
      <b-col xl="3" lg="6" md="6">
        <div class="card widget-flat">
          <div class="card-body">
            <div class="float-end">
              <i class="mdi mdi-cash-100 widget-icon bg-success-lighten text-success"></i>
            </div>
            <h5 class="text-muted fw-normal mt-0" title="Total Proceeds">
              Total Proceeds
            </h5>
            <h3 class="mt-3 mb-3">{{ formatCurrency(waterfallStats.totalProceeds) }}</h3>
            <p class="mb-0 text-muted">
              <span class="text-nowrap">Available for Distribution</span>
            </p>
          </div>
        </div>
      </b-col>

      <!-- LP Share -->
      <b-col xl="3" lg="6" md="6">
        <div class="card widget-flat">
          <div class="card-body">
            <div class="float-end">
              <i class="mdi mdi-account-group widget-icon bg-primary-lighten text-primary"></i>
            </div>
            <h5 class="text-muted fw-normal mt-0" title="Limited Partner Share">
              LP Share
            </h5>
            <h3 class="mt-3 mb-3">{{ formatCurrency(waterfallStats.lpShare) }}</h3>
            <p class="mb-0 text-muted">
              <span class="text-primary me-2">{{ waterfallStats.lpPercent }}%</span>
              <span class="text-nowrap">of Proceeds</span>
            </p>
          </div>
        </div>
      </b-col>

      <!-- GP Share -->
      <b-col xl="3" lg="6" md="6">
        <div class="card widget-flat">
          <div class="card-body">
            <div class="float-end">
              <i class="mdi mdi-shield-account widget-icon bg-warning-lighten text-warning"></i>
            </div>
            <h5 class="text-muted fw-normal mt-0" title="General Partner Share">
              GP Share
            </h5>
            <h3 class="mt-3 mb-3">{{ formatCurrency(waterfallStats.gpShare) }}</h3>
            <p class="mb-0 text-muted">
              <span class="text-warning me-2">{{ waterfallStats.gpPercent }}%</span>
              <span class="text-nowrap">of Proceeds</span>
            </p>
          </div>
        </div>
      </b-col>

      <!-- Promote -->
      <b-col xl="3" lg="6" md="6">
        <div class="card widget-flat">
          <div class="card-body">
            <div class="float-end">
              <i class="mdi mdi-trophy widget-icon bg-info-lighten text-info"></i>
            </div>
            <h5 class="text-muted fw-normal mt-0" title="GP Promote">GP Promote</h5>
            <h3 class="mt-3 mb-3">{{ formatCurrency(waterfallStats.promote) }}</h3>
            <p class="mb-0 text-muted">
              <span class="text-nowrap">Performance-Based</span>
            </p>
          </div>
        </div>
      </b-col>
    </b-row>

    <!-- Waterfall Tiers & Visual Flow -->
    <b-row class="g-2 mb-3">
      <!-- Waterfall Tiers Table -->
      <b-col xl="8" lg="12">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h4 class="header-title mb-0">Waterfall Distribution Tiers</h4>
            <button class="btn btn-sm btn-link p-0">
              <i class="mdi mdi-information-outline"></i> About Waterfall Structure
            </button>
          </div>
          <div class="card-body pt-0">
            <div class="table-responsive">
              <table class="table table-centered table-nowrap mb-0">
                <thead>
                  <tr>
                    <th>Tier</th>
                    <th>Description</th>
                    <th>Split</th>
                    <th>Amount</th>
                    <th>LP</th>
                    <th>GP</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="tier in waterfallTiers" :key="tier.id">
                    <td>
                      <span class="badge bg-primary">{{ tier.tier }}</span>
                    </td>
                    <td>
                      <h5 class="my-0 fw-normal">{{ tier.name }}</h5>
                      <small class="text-muted">{{ tier.description }}</small>
                    </td>
                    <td>{{ tier.split }}</td>
                    <td class="fw-semibold">{{ formatCurrency(tier.amount) }}</td>
                    <td class="text-primary">{{ formatCurrency(tier.lpAmount) }}</td>
                    <td class="text-warning">{{ formatCurrency(tier.gpAmount) }}</td>
                    <td>
                      <span :class="['badge', getTierStatusBadge(tier.status)]">
                        {{ tier.status }}
                      </span>
                    </td>
                  </tr>
                </tbody>
                <tfoot>
                  <tr class="table-light fw-bold">
                    <td colspan="3">Total Distribution</td>
                    <td>{{ formatCurrency(waterfallStats.totalProceeds) }}</td>
                    <td class="text-primary">{{ formatCurrency(waterfallStats.lpShare) }}</td>
                    <td class="text-warning">{{ formatCurrency(waterfallStats.gpShare) }}</td>
                    <td></td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>
        </div>
      </b-col>

      <!-- Waterfall Parameters -->
      <b-col xl="4" lg="12">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h4 class="header-title mb-0">Waterfall Parameters</h4>
            <button class="btn btn-sm btn-link p-0">
              <i class="mdi mdi-pencil"></i> Edit
            </button>
          </div>
          <div class="card-body pt-0">
            <div class="mb-3">
              <h5 class="text-muted fw-normal mb-1">Waterfall Type</h5>
              <p class="mb-0 fw-semibold">{{ parameters.type }}</p>
            </div>
            <div class="mb-3">
              <h5 class="text-muted fw-normal mb-1">Preferred Return</h5>
              <p class="mb-0 text-success fw-semibold">{{ parameters.preferredReturn }}%</p>
            </div>
            <div class="mb-3">
              <h5 class="text-muted fw-normal mb-1">LP Capital</h5>
              <p class="mb-0">{{ formatCurrency(parameters.lpCapital) }}</p>
            </div>
            <div class="mb-3">
              <h5 class="text-muted fw-normal mb-1">GP Capital</h5>
              <p class="mb-0">{{ formatCurrency(parameters.gpCapital) }}</p>
            </div>
            <div class="mb-3">
              <h5 class="text-muted fw-normal mb-1">Promote Hurdles</h5>
              <ul class="list-unstyled mb-0">
                <li v-for="(hurdle, idx) in parameters.hurdles" :key="idx">
                  <small>{{ hurdle.rate }}% IRR → {{ hurdle.split }} split</small>
                </li>
              </ul>
            </div>
            <div class="mb-3">
              <h5 class="text-muted fw-normal mb-1">Catch-Up</h5>
              <p class="mb-0">{{ parameters.catchUp }}</p>
            </div>
          </div>
        </div>
      </b-col>
    </b-row>

    <!-- Scenario Analysis & Historical Distributions -->
    <b-row class="g-2">
      <!-- Scenario Analysis -->
      <b-col xl="6" lg="12">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h4 class="header-title mb-0">Scenario Analysis</h4>
            <button class="btn btn-sm btn-primary">
              <i class="mdi mdi-table-plus me-1"></i> Add Scenario
            </button>
          </div>
          <div class="card-body pt-0">
            <div class="table-responsive">
              <table class="table table-sm table-centered table-nowrap mb-0">
                <thead>
                  <tr>
                    <th>Scenario</th>
                    <th>Exit Value</th>
                    <th>LP Return</th>
                    <th>GP Promote</th>
                    <th>IRR</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="scenario in scenarios" :key="scenario.id" :class="{ 'table-success': scenario.isBase }">
                    <td>
                      <span v-if="scenario.isBase" class="badge bg-success me-1">Base</span>
                      {{ scenario.name }}
                    </td>
                    <td>{{ formatCurrency(scenario.exitValue) }}</td>
                    <td>{{ formatCurrency(scenario.lpReturn) }}</td>
                    <td>{{ formatCurrency(scenario.gpPromote) }}</td>
                    <td>
                      <span :class="getIrrColor(scenario.irr)">{{ scenario.irr }}%</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </b-col>

      <!-- Historical Distributions -->
      <b-col xl="6" lg="12">
        <div class="card">
          <div class="card-header">
            <h4 class="header-title mb-0">Historical Distributions</h4>
          </div>
          <div class="card-body pt-0">
            <div class="table-responsive">
              <table class="table table-sm table-centered table-nowrap mb-0">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Type</th>
                    <th>Amount</th>
                    <th>LP</th>
                    <th>GP</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="dist in historicalDistributions" :key="dist.id">
                    <td>{{ dist.date }}</td>
                    <td>{{ dist.type }}</td>
                    <td>{{ formatCurrency(dist.amount) }}</td>
                    <td class="text-primary">{{ formatCurrency(dist.lpAmount) }}</td>
                    <td class="text-warning">{{ formatCurrency(dist.gpAmount) }}</td>
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
 * Waterfall View Component
 * 
 * WHAT: Displays waterfall distribution calculations showing how proceeds
 *       flow through different tiers to LPs and GP based on returns
 * 
 * WHY: Critical for private equity/real estate fund management to calculate
 *      and visualize complex profit-sharing arrangements with promote structures
 * 
 * WHERE: Rendered within Portfolio Management dashboard's Waterfalls tab
 * 
 * HOW: Shows tier-by-tier distribution logic, scenario analysis, and historical
 *      distributions. Backend calculations via Pinia store (to be implemented)
 */
import { defineComponent, ref } from 'vue'

// WHAT: Type definition for investment
// WHY: Defines structure for investment selection
interface Investment {
  id: number
  name: string
}

// WHAT: Type definition for waterfall tier
// WHY: Defines structure for waterfall tier calculations
interface WaterfallTier {
  id: number
  tier: number
  name: string
  description: string
  split: string
  amount: number
  lpAmount: number
  gpAmount: number
  status: string
}

// WHAT: Type definition for scenario
// WHY: Defines structure for waterfall scenario analysis
interface Scenario {
  id: number
  name: string
  exitValue: number
  lpReturn: number
  gpPromote: number
  irr: number
  isBase: boolean
}

// WHAT: Type definition for historical distribution
// WHY: Defines structure for historical distribution records
interface HistoricalDistribution {
  id: number
  date: string
  type: string
  amount: number
  lpAmount: number
  gpAmount: number
}

// WHAT: Define component using defineComponent for proper TypeScript support
// WHY: Ensures proper type inference and prevents interface naming errors
export default defineComponent({
  name: 'WaterfallView',
  setup() {
    // WHAT: Selected investment ID
    // WHY: Controls which investment's waterfall is displayed
    const selectedInvestment = ref<number | null>(null)

    // WHAT: List of available investments
    // TODO: Fetch from backend
    const investments = ref<Investment[]>([
      { id: 1, name: 'Multifamily Portfolio - Austin' },
      { id: 2, name: 'Office Complex - Dallas' },
      { id: 3, name: 'Industrial Park - Houston' },
      { id: 4, name: 'Mixed-Use Development' },
    ])

    // WHAT: Waterfall summary statistics
    // WHY: High-level distribution breakdown
    const waterfallStats = ref({
      totalProceeds: 65000000,
      lpShare: 52000000,
      lpPercent: 80.0,
      gpShare: 13000000,
      gpPercent: 20.0,
      promote: 8500000,
    })

    // WHAT: Waterfall tier definitions
    // WHY: Shows step-by-step cash flow allocation
    const waterfallTiers = ref<WaterfallTier[]>([
      {
        id: 1,
        tier: 1,
        name: 'Return of Capital',
        description: 'Return LP capital contributions',
        split: '100/0',
        amount: 32000000,
        lpAmount: 32000000,
        gpAmount: 0,
        status: 'Funded',
      },
      {
        id: 2,
        tier: 2,
        name: 'Preferred Return',
        description: '8% preferred return to LP',
        split: '100/0',
        amount: 8960000,
        lpAmount: 8960000,
        gpAmount: 0,
        status: 'Funded',
      },
      {
        id: 3,
        tier: 3,
        name: 'GP Catch-Up',
        description: 'GP catches up to 20% of Tiers 1-2',
        split: '0/100',
        amount: 10240000,
        lpAmount: 0,
        gpAmount: 10240000,
        status: 'Funded',
      },
      {
        id: 4,
        tier: 4,
        name: 'Remaining Split',
        description: 'Remaining proceeds split 80/20',
        split: '80/20',
        amount: 13800000,
        lpAmount: 11040000,
        gpAmount: 2760000,
        status: 'Projected',
      },
    ])

    // WHAT: Waterfall parameters
    // WHY: Defines the rules and structure of the waterfall
    const parameters = ref({
      type: 'European (Whole Fund)',
      preferredReturn: 8.0,
      lpCapital: 32000000,
      gpCapital: 8000000,
      hurdles: [
        { rate: 8, split: '100/0' },
        { rate: 12, split: '80/20' },
        { rate: 15, split: '70/30' },
      ],
      catchUp: '100% to GP until 20% of total',
    })

    // WHAT: Scenario analysis for different exit values
    // WHY: Shows how waterfall changes under different outcomes
    const scenarios = ref<Scenario[]>([
      {
        id: 1,
        name: 'Downside',
        exitValue: 50000000,
        lpReturn: 42000000,
        gpPromote: 3500000,
        irr: 12.5,
        isBase: false,
      },
      {
        id: 2,
        name: 'Base Case',
        exitValue: 65000000,
        lpReturn: 52000000,
        gpPromote: 8500000,
        irr: 18.2,
        isBase: true,
      },
      {
        id: 3,
        name: 'Upside',
        exitValue: 80000000,
        lpReturn: 62000000,
        gpPromote: 13500000,
        irr: 24.8,
        isBase: false,
      },
    ])

    // WHAT: Historical distribution records
    // WHY: Shows actual past distributions from this investment
    const historicalDistributions = ref<HistoricalDistribution[]>([
      {
        id: 1,
        date: 'Sep 30, 2024',
        type: 'Operating Cash Flow',
        amount: 2400000,
        lpAmount: 1920000,
        gpAmount: 480000,
      },
      {
        id: 2,
        date: 'Jun 30, 2024',
        type: 'Operating Cash Flow',
        amount: 2200000,
        lpAmount: 1760000,
        gpAmount: 440000,
      },
      {
        id: 3,
        date: 'Mar 31, 2024',
        type: 'Refinancing Proceeds',
        amount: 8500000,
        lpAmount: 8500000,
        gpAmount: 0,
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
     * WHAT: Get badge class for tier status
     * WHY: Visual indicators for tier completion
     */
    function getTierStatusBadge(status: string): string {
      const map: { [key: string]: string } = {
        Funded: 'bg-success',
        Projected: 'bg-info',
        Partial: 'bg-warning',
      }
      return map[status] || 'bg-secondary'
    }

    /**
     * WHAT: Get color class for IRR display
     * WHY: Color-code performance metrics
     */
    function getIrrColor(irr: number): string {
      if (irr >= 20) return 'text-success fw-bold'
      if (irr >= 15) return 'text-success'
      if (irr >= 10) return 'text-primary'
      return 'text-muted'
    }

    return {
      selectedInvestment,
      investments,
      waterfallStats,
      waterfallTiers,
      parameters,
      scenarios,
      historicalDistributions,
      formatCurrency,
      getTierStatusBadge,
      getIrrColor,
    }
  },
})
</script>

<style scoped>
/**
 * Waterfall View Styles
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

.table-success {
  background-color: rgba(10, 207, 151, 0.1);
}
</style>
