<template>
  <!--
    ForeclosureModelCard.vue
    What: Comprehensive foreclosure sale model card with all FC-related inputs and assumptions
    Why: Consolidate scattered foreclosure information into one clear, concise card
    Where: frontend_vue/src/views/acq_module/loanlvl/components/model/ForeclosureModelCard.vue
    How: Combines existing FC data with detailed model assumptions and calculations
  -->
  <div class="card border-primary">
    <div class="card-header bg-primary-subtle">
      <div class="d-flex align-items-center justify-content-between">
          <h5 class="mb-0 d-flex align-items-center">
            <i class="fas fa-gavel me-2 text-primary"></i>
            Foreclosure Model
            <span class="badge bg-primary ms-2">{{ fcProbability }}Probability</span>
          </h5>
        <div class="d-flex gap-2 align-items-center">
          <!-- FC Sale Probability Input -->
          <div class="d-flex align-items-center gap-2">
            <label class="form-label fw-semibold mb-0 text-body">
              Probability:
            </label>
            <div class="input-group" style="max-width: 100px;">
              <input
                v-model.number="fcProbability"
                type="number"
                class="form-control form-control-sm text-end fw-bold"
                min="0"
                max="100"
                step="1"
                placeholder="0"
                @input="handleProbabilityChange"
              />
              <span class="input-group-text">%</span>
            </div>
          </div>
          
          <!-- Collapse/Expand button -->
          <button
            type="button"
            class="btn btn-sm btn-outline-secondary"
            @click="collapsed = !collapsed"
            :aria-expanded="!collapsed"
          >
            <i :class="collapsed ? 'mdi mdi-chevron-down' : 'mdi mdi-chevron-up'"></i>
          </button>
        </div>
      </div>
    </div>

    <div v-show="!collapsed" class="card-body">
      <!-- Financial Summary KPIs -->
      <div class="mb-4">
        <div class="row g-3">
          <div class="col-md-2">
            <div class="text-center p-2 bg-light rounded h-100">
              <small class="text-muted d-block">Total Costs</small>
              <span class="fw-bold text-danger">{{ formatCurrency(calculatedTotalCosts) }}</span>
            </div>
          </div>
          <div class="col-md-2">
            <div class="text-center p-2 bg-light rounded h-100">
              <small class="text-muted d-block">Expected Proceeds</small>
              <span class="fw-bold text-success">{{ formatCurrency(timelineData.expected_recovery || 0) }}</span>
            </div>
          </div>
          <div class="col-md-2">
            <div class="text-center p-2 bg-light rounded h-100">
              <small class="text-muted d-block">Net PL</small>
              <span class="fw-bold" :class="calculatedNetRecovery >= 0 ? 'text-success' : 'text-danger'">
                {{ formatCurrency(calculatedNetRecovery) }}
              </span>
            </div>
          </div>
          <div class="col-md-2">
            <div class="text-center p-2 bg-light rounded h-100">
              <small class="text-muted d-block">Total Duration</small>
              <span class="fw-bold text-primary">
                {{ timelineData.total_timeline_months != null ? timelineData.total_timeline_months : '—' }} months
              </span>
            </div>
          </div>
          <div class="col-md-2">
            <div class="text-center p-2 bg-light rounded h-100">
              <small class="text-muted d-block">MOIC</small>
              <span class="fw-bold" :class="liveMOIC >= 1 ? 'text-success' : 'text-danger'">
                {{ liveMOIC.toFixed(2) }}x
              </span>
            </div>
          </div>
          <div class="col-md-2">
            <div class="text-center p-2 bg-light rounded h-100">
              <small class="text-muted d-block">Annualized ROI</small>
              <span class="fw-bold" :class="liveAnnualizedROI >= 0 ? 'text-success' : 'text-danger'">
                {{ (liveAnnualizedROI * 100).toFixed(1) }}%
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Key Inputs Section -->
      <div class="mb-4 p-3 bg-light rounded border text-center acquisition-price-card">
        <h6 class="text-uppercase text-muted small fw-semibold mb-3">
          Key Assumption
        </h6>
        <div class="d-inline-flex align-items-center gap-2 mb-3">
          <label class="form-label fw-semibold mb-0 fs-5 text-muted">
            Acquisition Price
          </label>
          <div class="input-group editable-input-highlight" style="max-width: 220px;">
            <span class="input-group-text fs-5 bg-transparent border-0 text-muted pe-1">$</span>
            <input
              type="text"
              class="form-control form-control-lg text-center fw-bold fs-4 bg-transparent border-0 editable-price-value"
              style="box-shadow: none; cursor: text;"
              :value="formattedAcquisitionPrice"
              @input="handleAcquisitionPriceInput"
              @blur="saveAcquisitionPrice"
              @keyup.enter="saveAcquisitionPrice"
              placeholder="Click to edit"
            />
          </div>
        </div>

        <!-- Purchase Price Metrics -->
        <div class="d-flex flex-wrap justify-content-center gap-2">
          <span 
            v-if="liveMetrics.currentBalance != null" 
            class="badge bg-info-subtle text-info border border-info"
            style="font-weight: 500; font-size: 0.8rem; padding: 0.5em 0.8em;"
          >
            {{ liveMetrics.currentBalance }}% of Current Balance
          </span>
          <span 
            v-if="liveMetrics.totalDebt != null" 
            class="badge bg-warning-subtle text-warning border border-warning"
            style="font-weight: 500; font-size: 0.8rem; padding: 0.5em 0.8em;"
          >
            {{ liveMetrics.totalDebt }}% of Total Debt
          </span>
          <span 
            v-if="liveMetrics.sellerAsIs != null" 
            class="badge bg-success-subtle text-success border border-success"
            style="font-weight: 500; font-size: 0.8rem; padding: 0.5em 0.8em;"
          >
            {{ liveMetrics.sellerAsIs }}% of Seller As-Is
          </span>
          <span 
            v-if="liveMetrics.internalUWAsIs != null" 
            class="badge bg-primary-subtle text-primary border border-primary"
            style="font-weight: 500; font-size: 0.8rem; padding: 0.5em 0.8em;"
          >
            {{ liveMetrics.internalUWAsIs }}% of UW As-Is
          </span>
        </div>
      </div>

      <!-- Timelines, Acquisition Costs, Carry Costs, and Liquidation Expenses Section -->
      <div class="mb-4">
        <div class="row g-3">
          <!-- Timelines Column -->
          <div class="col-md-3">
            <div class="p-3 bg-light rounded border h-100">
              <h6 class="fw-semibold text-body mb-2">
                <i class="mdi mdi-clock-outline me-2 text-warning"></i>
                Timelines
              </h6>
              <div class="d-flex flex-column gap-2">
                <div class="d-flex align-items-baseline gap-2">
                  <small class="text-muted d-block" style="min-width: 140px;">Servicing Transfer:</small>
                  <span class="fw-semibold text-dark">
                    {{ timelineData.servicing_transfer_months != null ? timelineData.servicing_transfer_months : '—' }} months
                  </span>
                </div>
                
                <!-- UI OPTION A: Inline +/- Controls -->
                <div v-if="!uiOptionB" class="d-flex align-items-baseline gap-2">
                  <small class="text-muted d-block" style="min-width: 140px;">Foreclosure:</small>
                  <div class="d-flex align-items-center gap-2">
                    <span class="fw-semibold text-dark">
                      {{ timelineData.foreclosure_months != null ? timelineData.foreclosure_months : '—' }} months
                    </span>
                    <div class="btn-group btn-group-sm fc-duration-controls" role="group">
                      <button
                        type="button"
                        class="btn btn-outline-secondary"
                        @click="adjustFcDuration(-1)"
                        :disabled="loadingTimelines || timelineData.foreclosure_months_base == null"
                        title="Subtract 1 month"
                      >
                        <i v-if="loadingTimelines" class="mdi mdi-refresh mdi-spin"></i>
                        <i v-else class="mdi mdi-minus"></i>
                      </button>
                      <button
                        type="button"
                        class="btn btn-outline-secondary"
                        @click="adjustFcDuration(1)"
                        :disabled="loadingTimelines || timelineData.foreclosure_months_base == null"
                        title="Add 1 month"
                      >
                        <i v-if="loadingTimelines" class="mdi mdi-refresh mdi-spin"></i>
                        <i v-else class="mdi mdi-plus"></i>
                      </button>
                    </div>
                    <span v-if="timelineData.fc_duration_override_months != null && timelineData.fc_duration_override_months !== 0" 
                          class="badge" 
                          :class="timelineData.fc_duration_override_months > 0 ? 'bg-success' : 'bg-danger'"
                          style="font-size: 0.7rem;">
                      {{ timelineData.fc_duration_override_months > 0 ? '+' : '' }}{{ timelineData.fc_duration_override_months }}
                    </span>
                  </div>
                </div>
                
                <!-- UI OPTION B: Display Format -->
                <div v-if="uiOptionB" class="d-flex align-items-baseline gap-2">
                  <small class="text-muted d-block" style="min-width: 140px;">Foreclosure:</small>
                  <div class="d-flex align-items-center gap-2">
                    <span class="fw-semibold text-dark">
                      {{ timelineData.foreclosure_months_base != null ? timelineData.foreclosure_months_base : '—' }} months
                    </span>
                    <span v-if="timelineData.fc_duration_override_months != null && timelineData.fc_duration_override_months !== 0" 
                          class="text-muted small">
                      [Override: 
                      <span :class="timelineData.fc_duration_override_months > 0 ? 'text-success' : 'text-danger'">
                        {{ timelineData.fc_duration_override_months > 0 ? '+' : '' }}{{ timelineData.fc_duration_override_months }}
                      </span>]
                    </span>
                    <span v-if="timelineData.foreclosure_months_base != null" class="fw-bold text-primary">
                      → {{ timelineData.foreclosure_months != null ? timelineData.foreclosure_months : '—' }} months
                    </span>
                    <div class="btn-group btn-group-sm fc-duration-controls ms-2" role="group">
                      <button
                        type="button"
                        class="btn btn-outline-secondary"
                        @click="adjustFcDuration(-1)"
                        :disabled="loadingTimelines || timelineData.foreclosure_months_base == null"
                        title="Subtract 1 month"
                      >
                        <i v-if="loadingTimelines" class="mdi mdi-refresh mdi-spin"></i>
                        <i v-else class="mdi mdi-minus"></i>
                      </button>
                      <button
                        type="button"
                        class="btn btn-outline-secondary"
                        @click="adjustFcDuration(1)"
                        :disabled="loadingTimelines || timelineData.foreclosure_months_base == null"
                        title="Add 1 month"
                      >
                        <i v-if="loadingTimelines" class="mdi mdi-refresh mdi-spin"></i>
                        <i v-else class="mdi mdi-plus"></i>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Acquisition Costs Column -->
          <div class="col-md-3">
            <div class="p-3 bg-light rounded border h-100">
              <h6 class="fw-semibold text-body mb-2">
                <i class="mdi mdi-briefcase-outline me-2 text-info"></i>
                Acquisition Costs
              </h6>
              <div class="d-flex flex-column gap-2">
              <div class="d-flex align-items-baseline gap-2">
                <small class="text-muted d-block" style="min-width: 140px;">Broker Fee:</small>
                <span class="fw-bold text-dark">{{ formatCurrency(liveBrokerFee) }}</span>
              </div>
              <div class="d-flex align-items-baseline gap-2">
                <small class="text-muted d-block" style="min-width: 140px;">Other Fees:</small>
                <span class="fw-bold text-dark">{{ formatCurrency(liveOtherFee) }}</span>
              </div>
              <div class="d-flex align-items-baseline gap-2">
                <small class="text-muted d-block" style="min-width: 140px;">Legal Cost:</small>
                <span class="fw-bold text-dark">{{ formatCurrency(timelineData.acq_legal || 0) }}</span>
              </div>
              <div class="d-flex align-items-baseline gap-2">
                <small class="text-muted d-block" style="min-width: 140px;">Due Diligence:</small>
                <span class="fw-bold text-dark">{{ formatCurrency(timelineData.acq_dd || 0) }}</span>
              </div>
              <div class="d-flex align-items-baseline gap-2">
                <small class="text-muted d-block" style="min-width: 140px;">Tax/Title:</small>
                <span class="fw-bold text-dark">{{ formatCurrency(timelineData.acq_tax_title || 0) }}</span>
              </div>
            </div>
            </div>
          </div>
          
          <!-- Carry Costs Column -->
          <div class="col-md-3">
            <div class="p-3 bg-light rounded border h-100">
              <h6 class="fw-semibold text-body mb-2">
                <i class="mdi mdi-cash-multiple me-2 text-warning"></i>
                Carry Costs
              </h6>
              <div class="d-flex flex-column gap-2">
              <div class="d-flex align-items-baseline gap-2">
                <small class="text-muted d-block" style="min-width: 140px;">Servicing Fees:</small>
                <span class="fw-bold text-dark">{{ formatCurrency(expenses.servicingFees) }}</span>
              </div>
              <div class="d-flex align-items-baseline gap-2">
                <small class="text-muted d-block" style="min-width: 140px;">Taxes:</small>
                <span class="fw-bold text-dark">{{ formatCurrency(expenses.taxes) }}</span>
              </div>
              <div class="d-flex align-items-baseline gap-2">
                <small class="text-muted d-block" style="min-width: 140px;">Insurance:</small>
                <span class="fw-bold text-dark">{{ formatCurrency(expenses.insurance) }}</span>
              </div>
              <div class="d-flex align-items-baseline gap-2">
                <small class="text-muted d-block" style="min-width: 140px;">Legal Cost:</small>
                <span class="fw-bold text-dark">{{ formatCurrency(expenses.legalCost) }}</span>
              </div>
            </div>
            </div>
          </div>
          
          <!-- Liquidation Expenses Column -->
          <div class="col-md-3">
            <div class="p-3 bg-light rounded border h-100">
              <h6 class="fw-semibold text-body mb-2">
                <i class="mdi mdi-gavel me-2 text-warning"></i>
                Liquidation Expenses
              </h6>
              <div class="d-flex flex-column gap-2">
              <div class="d-flex align-items-baseline gap-2">
                <small class="text-muted d-block" style="min-width: 160px;">Servicer Liquidation Fee:</small>
                <span class="fw-bold text-dark">{{ formatCurrency(timelineData.servicer_liquidation_fee || 0) }}</span>
              </div>
              <div class="d-flex align-items-baseline gap-2">
                <small class="text-muted d-block" style="min-width: 160px;">AM Liquidation Fee:</small>
                <span class="fw-bold text-dark">{{ formatCurrency(timelineData.am_liquidation_fee || 0) }}</span>
              </div>
            </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Validation Messages -->
      <div v-if="validationMessages.length > 0" class="alert alert-warning mt-3 py-2 px-3 small">
        <i class="fas fa-exclamation-triangle me-1"></i>
        <ul class="mb-0 ps-3">
          <li v-for="message in validationMessages" :key="message">{{ message }}</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch, onMounted } from 'vue'
import http from '@/lib/http'

// WHAT: Props for the ForeclosureModelCard component
const props = defineProps<{
  // WHAT: Row data containing existing foreclosure information from SellerRawData
  row?: Record<string, any> | null
  // WHAT: Asset ID for fetching additional FC data if needed
  assetId?: string | number | null
  // WHAT: Whether this is the only selected model (auto-sets to 100% if true)
  isOnlySelectedModel?: boolean
  // WHAT: Shared acquisition price value from parent to sync across all models
  sharedAcquisitionPrice?: number
}>()

// WHAT: Emits for parent component communication
const emit = defineEmits<{
  assumptionsChanged: [assumptions: FcAssumptions]
  probabilityChanged: [probability: number]
  acquisitionPriceChanged: [price: number]
}>()

// WHAT: Interface for foreclosure model assumptions (simplified - keeping for compatibility)
interface FcAssumptions {
  // Minimal assumptions kept for compatibility
  expectedBidPrice: number
  // WHAT: Expense fields
  servicingFees: number
  taxes: number
  insurance: number
  legalCost: number
}

// WHAT: Reactive state for component
const collapsed = ref(false)

// WHAT: UI option toggle - false = Option A (inline +/-), true = Option B (display format)
// WHY: Allow user to see and compare both UI designs
const uiOptionB = ref(false)

// WHAT: FC Sale probability (auto-sets to 100% if only model selected)
const fcProbability = ref<number>(0)

// WHAT: Timeline data from backend API
const timelineData = reactive<{
  servicing_transfer_months: number | null
  foreclosure_days: number | null
  foreclosure_months: number | null
  foreclosure_months_base: number | null
  fc_duration_override_months: number | null
  total_timeline_months: number | null
  expected_recovery: number | null
  acquisition_price: number | null
  // WHAT: Acquisition Cost values from backend models
  acq_broker_fees: number | null
  acq_other_fees: number | null
  acq_legal: number | null
  acq_dd: number | null
  acq_tax_title: number | null
  // WHAT: Acquisition fee percentages for live calculation
  acq_broker_fee_pct: number | null
  acq_other_fee_pct: number | null
  // WHAT: Carry Cost values from backend models
  servicing_fees: number | null
  taxes: number | null
  insurance: number | null
  legal_cost: number | null
  // WHAT: Liquidation Expense values from backend models
  servicer_liquidation_fee: number | null
  am_liquidation_fee: number | null
  // WHAT: Calculated financial metrics from backend
  total_costs: number | null
  net_pl: number | null
  moic: number | null
  annualized_roi: number | null
  // WHAT: Purchase price metrics (as percentages)
  purchase_of_currentBalance: number | null
  purchase_of_totalDebt: number | null
  purchase_of_sellerAsIs: number | null
  purchase_of_internalUWAsIs: number | null
  // WHAT: Base values for real-time metric calculation
  base_currentBalance: number | null
  base_totalDebt: number | null
  base_sellerAsIs: number | null
  base_internalUWAsIs: number | null
}>({
  servicing_transfer_months: null,
  foreclosure_days: null,
  foreclosure_months: null,
  foreclosure_months_base: null,
  fc_duration_override_months: null,
  total_timeline_months: null,
  expected_recovery: null,
  acquisition_price: null,
  acq_broker_fees: null,
  acq_other_fees: null,
  acq_legal: null,
  acq_dd: null,
  acq_tax_title: null,
  acq_broker_fee_pct: null,
  acq_other_fee_pct: null,
  servicing_fees: null,
  taxes: null,
  insurance: null,
  legal_cost: null,
  servicer_liquidation_fee: null,
  am_liquidation_fee: null,
  total_costs: null,
  net_pl: null,
  moic: null,
  annualized_roi: null,
  purchase_of_currentBalance: null,
  purchase_of_totalDebt: null,
  purchase_of_sellerAsIs: null,
  purchase_of_internalUWAsIs: null,
  base_currentBalance: null,
  base_totalDebt: null,
  base_sellerAsIs: null,
  base_internalUWAsIs: null
})

// WHAT: Loading state for timeline data
const loadingTimelines = ref(false)

// WHAT: Editable acquisition price - computed to directly use shared parent value
// WHY: Ensure both models use literally the same value, not separate synced copies
// HOW: Computed getter/setter that reads and writes through parent
const acquisitionPrice = computed({
  get: () => props.sharedAcquisitionPrice ?? 0,
  set: (value) => {
    // Emit to parent to update shared value immediately (for real-time sync)
    emit('acquisitionPriceChanged', value)
  }
})

// WHAT: Computed property for formatted acquisition price display
// WHY: Format number with commas for better readability
const formattedAcquisitionPrice = computed(() => {
  if (!acquisitionPrice.value || acquisitionPrice.value === 0) {
    return ''
  }
  return acquisitionPrice.value.toLocaleString('en-US')
})

// WHAT: Handler for acquisition price input
// WHY: Parse formatted input and update raw numeric value
function handleAcquisitionPriceInput(event: Event) {
  const target = event.target as HTMLInputElement
  const value = target.value
  
  // WHAT: Remove all non-digit characters
  const numericValue = value.replace(/[^0-9]/g, '')
  
  // WHAT: Convert to number (or 0 if empty)
  acquisitionPrice.value = numericValue ? parseInt(numericValue, 10) : 0
}

// WHAT: Minimal assumptions (kept for compatibility with Financial Summary)
const assumptions = reactive<FcAssumptions>({
  expectedBidPrice: 0,
  servicingFees: 0,
  taxes: 0,
  insurance: 0,
  legalCost: 0
})

// WHAT: Expense fields for the Expenses section
// WHY: Separate reactive object for easier management, synced from backend API
const expenses = reactive({
  servicingFees: 0,
  taxes: 0,
  insurance: 0,
  legalCost: 0
})

// WHAT: Watch timelineData expense fields and sync to expenses object
// WHY: Update expenses when API data is fetched
watch(() => [
  timelineData.servicing_fees,
  timelineData.taxes,
  timelineData.insurance,
  timelineData.legal_cost
], () => {
  expenses.servicingFees = timelineData.servicing_fees ?? 0
  expenses.taxes = timelineData.taxes ?? 0
  expenses.insurance = timelineData.insurance ?? 0
  expenses.legalCost = timelineData.legal_cost ?? 0
  // WHAT: Sync to assumptions for emits
  // WHY: Keep assumptions in sync for parent component
  assumptions.servicingFees = expenses.servicingFees
  assumptions.taxes = expenses.taxes
  assumptions.insurance = expenses.insurance
  assumptions.legalCost = expenses.legalCost
  emitChanges()
}, { deep: true })

// WHAT: Computed property to extract foreclosure data from row
const fcData = computed(() => {
  return props.row ? {
    fc_flag: props.row.fc_flag,
    fc_first_legal_date: props.row.fc_first_legal_date,
    fc_referred_date: props.row.fc_referred_date,
    fc_judgement_date: props.row.fc_judgement_date,
    fc_scheduled_sale_date: props.row.fc_scheduled_sale_date,
    fc_sale_date: props.row.fc_sale_date,
    fc_starting: props.row.fc_starting
  } : null
})

// WHAT: Computed property to display total costs with live acquisition price updates
// WHY: Total costs includes broker/other fees which depend on acquisition price, so needs to update in real-time
// HOW: Start with backend total_costs, then subtract old broker/other fees and add live ones
const calculatedTotalCosts = computed(() => {
  // WHAT: Get base total costs from backend
  const baseTotalCosts = timelineData.total_costs || 0
  
  // WHAT: Subtract the backend-calculated broker and other fees (which used old acquisition price)
  const oldBrokerFee = timelineData.acq_broker_fees || 0
  const oldOtherFee = timelineData.acq_other_fees || 0
  
  // WHAT: Add the live-calculated broker and other fees (using current acquisition price)
  const newBrokerFee = liveBrokerFee.value || 0
  const newOtherFee = liveOtherFee.value || 0
  
  // WHAT: Calculate adjusted total costs
  // WHY: Replace old fees with new fees to reflect current acquisition price
  return baseTotalCosts - oldBrokerFee - oldOtherFee + newBrokerFee + newOtherFee
})

// WHAT: Computed property to display net PL with real-time updates
// WHY: Net PL = Expected Recovery - Total Costs - Acquisition Price
// HOW: Use local acquisitionPrice for real-time updates as user types
const calculatedNetRecovery = computed(() => {
  const expectedRecovery = timelineData.expected_recovery || 0
  const totalCosts = timelineData.total_costs || 0
  const acqPrice = acquisitionPrice.value || 0
  
  return expectedRecovery - totalCosts - acqPrice
})

// WHAT: Computed properties for live-updating purchase price metrics
// WHY: Update metrics in real-time as user types acquisition price
// HOW: Calculate percentage based on base values and current acquisitionPrice
const liveMetrics = computed(() => {
  const price = acquisitionPrice.value || 0
  
  if (price <= 0) {
    return {
      currentBalance: null,
      totalDebt: null,
      sellerAsIs: null,
      internalUWAsIs: null
    }
  }
  
  return {
    currentBalance: timelineData.base_currentBalance && timelineData.base_currentBalance > 0
      ? ((price / timelineData.base_currentBalance) * 100).toFixed(1)
      : null,
    totalDebt: timelineData.base_totalDebt && timelineData.base_totalDebt > 0
      ? ((price / timelineData.base_totalDebt) * 100).toFixed(1)
      : null,
    sellerAsIs: timelineData.base_sellerAsIs && timelineData.base_sellerAsIs > 0
      ? ((price / timelineData.base_sellerAsIs) * 100).toFixed(1)
      : null,
    internalUWAsIs: timelineData.base_internalUWAsIs && timelineData.base_internalUWAsIs > 0
      ? ((price / timelineData.base_internalUWAsIs) * 100).toFixed(1)
      : null
  }
})

// WHAT: Computed properties for live acquisition fee calculations
// WHY: Update broker and other fees in real-time as acquisition price changes
const liveBrokerFee = computed(() => {
  const price = acquisitionPrice.value || 0
  const pct = timelineData.acq_broker_fee_pct || 0
  return price * pct
})

const liveOtherFee = computed(() => {
  const price = acquisitionPrice.value || 0
  const pct = timelineData.acq_other_fee_pct || 0
  return price * pct
})

// WHAT: Computed property for live-updating MOIC (Multiple on Invested Capital)
// WHY: Update MOIC in real-time as acquisition price changes
// HOW: MOIC = (Expected Recovery) / (Total Costs + Acquisition Price)
const liveMOIC = computed(() => {
  const expectedRecovery = timelineData.expected_recovery || 0
  const totalCosts = timelineData.total_costs || 0
  const acqPrice = acquisitionPrice.value || 0
  const totalOutflows = totalCosts + acqPrice
  
  if (totalOutflows <= 0 || expectedRecovery <= 0) {
    return 0
  }
  
  return expectedRecovery / totalOutflows
})

// WHAT: Computed property for live-updating Annualized ROI
// WHY: Update Annualized ROI in real-time as acquisition price changes
// HOW: Annualized ROI = ((Net PL / Gross Cost) + 1) ^ (12 / total_duration) - 1
const liveAnnualizedROI = computed(() => {
  const expectedRecovery = timelineData.expected_recovery || 0
  const totalCosts = timelineData.total_costs || 0
  const acqPrice = acquisitionPrice.value || 0
  const grossCost = acqPrice + totalCosts
  const netPL = expectedRecovery - totalCosts - acqPrice
  const totalDuration = timelineData.total_timeline_months || 1 // Avoid division by zero
  
  if (grossCost <= 0 || totalDuration <= 0) {
    return 0
  }
  
  const returnRatio = (netPL / grossCost) + 1
  const annualizedROI = Math.pow(returnRatio, 12 / totalDuration) - 1
  
  return annualizedROI
})

// WHAT: Computed property for validation messages
const validationMessages = computed(() => {
  const messages: string[] = []
  
  if (fcProbability.value < 0 || fcProbability.value > 100) {
    messages.push('FC Sale probability must be between 0% and 100%')
  }
  
  return messages
})

// WHAT: Function to adjust FC duration by increment/decrement
// WHY: Allow users to adjust FC duration with +/- buttons
async function adjustFcDuration(change: number) {
  if (!props.assetId) {
    console.warn('[ForeclosureModelCard] No assetId provided, cannot adjust FC duration')
    return
  }

  // WHAT: Calculate new override value
  // WHY: Apply the change to the current override (or start from 0 if no override)
  const currentOverride = timelineData.fc_duration_override_months || 0
  const newOverride = currentOverride + change

  // WHAT: Save the new override value to backend
  // WHY: Persist user adjustments
  try {
    loadingTimelines.value = true
    await http.post(`/acq/assets/${props.assetId}/fc-duration-override/`, {
      fc_duration_override_months: newOverride
    })

    // WHAT: Refresh timeline data to get updated values
    // WHY: Ensure UI reflects backend-calculated totals
    await fetchTimelineData()
  } catch (error) {
    console.error('[ForeclosureModelCard] Failed to update FC duration override:', error)
    // TODO: Show user-friendly error message
  } finally {
    loadingTimelines.value = false
  }
}

// WHAT: Function to fetch timeline data from backend API
async function fetchTimelineData() {
  if (!props.assetId) {
    console.warn('[ForeclosureModelCard] No assetId provided, cannot fetch timeline data')
    return
  }

  loadingTimelines.value = true
  try {
    const response = await http.get(`/acq/assets/${props.assetId}/fc-model-sums/`)
    Object.assign(timelineData, response.data)
    
    // WHAT: Sync acquisition price to local state
    // WHY: Allow editing in the input field
    if (response.data.acquisition_price != null) {
      acquisitionPrice.value = response.data.acquisition_price
    }
  } catch (error) {
    console.error('[ForeclosureModelCard] Failed to fetch timeline data:', error)
    // Keep null values on error
  } finally {
    loadingTimelines.value = false
  }
}

// WHAT: Function to save acquisition price to backend
// WHY: Persist user-entered acquisition price
async function saveAcquisitionPrice() {
  if (!props.assetId) {
    console.warn('[ForeclosureModelCard] No assetId provided, cannot save acquisition price')
    return
  }

  try {
    await http.post(`/acq/assets/${props.assetId}/acquisition-price/`, {
      acquisition_price: acquisitionPrice.value || 0
    })
    
    console.log('[ForeclosureModelCard] Acquisition price saved:', acquisitionPrice.value)
    
    // Note: No need to emit here, already emitting on every value change via computed setter
    
    // WHAT: Refresh timeline data to get updated calculations
    // WHY: Acquisition price affects other calculations (broker fees, etc.)
    await fetchTimelineData()
  } catch (error) {
    console.error('[ForeclosureModelCard] Failed to save acquisition price:', error)
  }
}

// WHAT: Formatting helper functions
const formatCurrency = (value: number | null | undefined): string => {
  if (value == null || isNaN(value)) return '$0'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value)
}

const formatDate = (value: any): string => {
  if (!value) return 'N/A'
  try {
    return new Date(value).toLocaleDateString('en-US')
  } catch {
    return 'N/A'
  }
}

// WHAT: Function to emit changes to parent component
function emitChanges() {
  emit('assumptionsChanged', { ...assumptions })
}

// WHAT: Function to handle probability change
function handleProbabilityChange() {
  emit('probabilityChanged', fcProbability.value)
}

// WHAT: Watch for changes in assumptions and emit to parent
watch(assumptions, () => {
  emitChanges()
}, { deep: true })

// WHAT: Watch for isOnlySelectedModel prop - auto-set to 100% if only model selected
watch(() => props.isOnlySelectedModel, (isOnly) => {
  if (isOnly && fcProbability.value !== 100) {
    fcProbability.value = 100
    emit('probabilityChanged', fcProbability.value)
  }
}, { immediate: true })

// WHAT: Watch for assetId changes and fetch timeline data
watch(() => props.assetId, (newAssetId) => {
  if (newAssetId) {
    fetchTimelineData()
  }
}, { immediate: true })

// WHAT: Fetch timeline data on component mount
onMounted(() => {
  if (props.assetId) {
    fetchTimelineData()
  }
})

// WHAT: Initialize with existing FC data if available
if (fcData.value?.fc_starting) {
  assumptions.expectedBidPrice = Number(fcData.value.fc_starting) || assumptions.expectedBidPrice
}
</script>

<style scoped>
/* WHAT: Component-specific styles for ForeclosureModelCard */
.card-header {
  border-bottom: 1px solid rgba(13, 110, 253, 0.2);
}

.bg-primary-subtle {
  background-color: rgba(13, 110, 253, 0.1) !important;
}

.border-primary {
  border-color: rgba(13, 110, 253, 0.3) !important;
}

.form-control:focus {
  border-color: rgba(13, 110, 253, 0.5);
  box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25);
}

.bg-light {
  background-color: #f8f9fa !important;
}

/* WHAT: Smaller FC duration control buttons */
.fc-duration-controls {
  /* WHAT: Make the button group itself smaller */
  font-size: 0.7rem;
}

.fc-duration-controls .btn {
  /* WHAT: Smaller padding for compact buttons */
  padding: 0.15rem 0.35rem !important;
  /* WHAT: Smaller line height */
  line-height: 1.2;
  /* WHAT: Smaller font size */
  font-size: 0.7rem;
  /* WHAT: Minimal width */
  min-width: auto;
}

.fc-duration-controls .btn i {
  /* WHAT: Smaller icon size */
  font-size: 0.85rem;
}

/* WHAT: Hide number input spinner arrows */
/* Chrome, Safari, Edge, Opera */
input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

/* Firefox */
input[type="number"] {
  -moz-appearance: textfield;
  appearance: textfield;
}

/* WHAT: Visual hint that acquisition price is editable */
.acquisition-price-card {
  position: relative;
  transition: all 0.2s ease;
}

.acquisition-price-card:hover {
  background-color: #e9ecef !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

/* WHAT: Style the acquisition price value to show it's editable */
.editable-price-value {
  color: #0d6efd !important;
  text-decoration: underline;
  text-underline-offset: 4px;
  text-decoration-thickness: 2px;
}

.editable-price-value:hover {
  background-color: rgba(13, 110, 253, 0.03) !important;
  color: #0b5ed7 !important;
}

.editable-price-value:focus {
  background-color: rgba(13, 110, 253, 0.05) !important;
  color: #0b5ed7 !important;
  text-decoration: none;
}
</style>
