<template>
  <!--
    REOSaleModelCard.vue
    What: Comprehensive REO sale model card with all REO-related inputs and assumptions
    Why: Display REO sale scenario with timelines, costs, and financial metrics
    Where: frontend_vue/src/views/acq_module/loanlvl/components/model/REOSaleModelCard.vue
    How: Combines REO data with detailed model assumptions and calculations
  -->
  <div class="card border-primary">
    <div class="card-header bg-primary-subtle">
      <div class="d-flex align-items-center justify-content-between">
          <h5 class="mb-0 d-flex align-items-center">
            <i class="fas fa-home me-2 text-primary"></i>
            REO Sale Model
            <span class="badge bg-primary ms-2">{{ reoProbability }}% Probability</span>
          </h5>
        <div class="d-flex gap-2 align-items-center">
          <!-- REO Sale Probability Input -->
          <div class="d-flex align-items-center gap-2">
            <label class="form-label fw-semibold mb-0 text-body">
              Probability:
            </label>
            <div class="input-group" style="max-width: 100px;">
              <input
                v-model.number="reoProbability"
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
              <span class="fw-bold text-success">{{ formatCurrency(reoScenario === 'as_is' ? (timelineData.expected_proceeds_asis || 0) : (timelineData.expected_proceeds_arv || 0)) }}</span>
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
                {{ calculatedTotalDuration != null ? calculatedTotalDuration : '—' }} months
              </span>
            </div>
          </div>
          <div class="col-md-2">
            <div class="text-center p-2 bg-light rounded h-100">
              <small class="text-muted d-block">MOIC</small>
              <span class="fw-bold" :class="(reoScenario === 'as_is' ? timelineData.moic_asis : timelineData.moic_rehab) != null && (reoScenario === 'as_is' ? timelineData.moic_asis : timelineData.moic_rehab) >= 1 ? 'text-success' : 'text-danger'">
                {{ (reoScenario === 'as_is' ? timelineData.moic_asis : timelineData.moic_rehab) != null ? (reoScenario === 'as_is' ? timelineData.moic_asis : timelineData.moic_rehab).toFixed(2) + 'x' : '—' }}
              </span>
            </div>
          </div>
          <div class="col-md-2">
            <div class="text-center p-2 bg-light rounded h-100">
              <small class="text-muted d-block">Annualized ROI</small>
              <span class="fw-bold" :class="(reoScenario === 'as_is' ? timelineData.annualized_roi_asis : timelineData.annualized_roi_rehab) != null && (reoScenario === 'as_is' ? timelineData.annualized_roi_asis : timelineData.annualized_roi_rehab) >= 0 ? 'text-success' : 'text-danger'">
                {{ (reoScenario === 'as_is' ? timelineData.annualized_roi_asis : timelineData.annualized_roi_rehab) != null ? ((reoScenario === 'as_is' ? timelineData.annualized_roi_asis : timelineData.annualized_roi_rehab) * 100).toFixed(1) + '%' : '—' }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Key Inputs Section -->
      <div class="mb-4 p-3 bg-light rounded border">
        <div class="row g-3">
          <div class="col-md-6">
            <div class="d-flex align-items-center gap-2 mb-2">
              <label class="form-label fw-semibold mb-0">
                <i class="mdi mdi-currency-usd me-1 text-primary"></i>
                Acquisition Price:
              </label>
              <div class="input-group" style="max-width: 180px;">
                <span class="input-group-text">$</span>
                <input
                  type="text"
                  class="form-control form-control-sm text-end fw-bold"
                  :value="formattedAcquisitionPrice"
                  @input="handleAcquisitionPriceInput"
                  @blur="saveAcquisitionPrice"
                  @keyup.enter="saveAcquisitionPrice"
                  placeholder="0"
                />
              </div>
            </div>
            <!-- Purchase Price Metrics -->
            <div class="d-flex flex-wrap gap-2 ms-4 mt-2">
              <span 
                v-if="liveMetrics.currentBalance != null" 
                class="badge bg-info-subtle text-info border border-info"
                style="font-weight: 500; font-size: 0.75rem;"
              >
                {{ liveMetrics.currentBalance }}% of Current Balance
              </span>
              <span 
                v-if="liveMetrics.totalDebt != null" 
                class="badge bg-warning-subtle text-warning border border-warning"
                style="font-weight: 500; font-size: 0.75rem;"
              >
                {{ liveMetrics.totalDebt }}% of Total Debt
              </span>
              <span 
                v-if="liveMetrics.sellerAsIs != null" 
                class="badge bg-success-subtle text-success border border-success"
                style="font-weight: 500; font-size: 0.75rem;"
              >
                {{ liveMetrics.sellerAsIs }}% of Seller As-Is
              </span>
              <span 
                v-if="liveMetrics.internalUWAsIs != null" 
                class="badge bg-primary-subtle text-primary border border-primary"
                style="font-weight: 500; font-size: 0.75rem;"
              >
                {{ liveMetrics.internalUWAsIs }}% of UW As-Is
              </span>
            </div>
          </div>
          <!-- Second column removed - probability moved to header -->
        </div>
      </div>

      <!-- REO Scenario Toggle -->
      <div class="mb-4">
        <div class="d-flex align-items-center gap-2">
          <span class="fw-semibold text-body me-2">REO Scenario:</span>
          <div class="btn-group" role="group" aria-label="REO Scenario Toggle">
            <button
              type="button"
              class="btn btn-sm"
              :class="reoScenario === 'as_is' ? 'btn-primary' : 'btn-outline-primary'"
              @click="reoScenario = 'as_is'"
            >
              <i class="mdi mdi-home me-1"></i>
              As-Is
            </button>
            <button
              type="button"
              class="btn btn-sm"
              :class="reoScenario === 'rehab' ? 'btn-primary' : 'btn-outline-primary'"
              @click="reoScenario = 'rehab'"
            >
              <i class="mdi mdi-hammer-wrench me-1"></i>
              Rehab
            </button>
          </div>
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
                
                <!-- Foreclosure with +/- controls -->
                <div class="d-flex align-items-baseline gap-2">
                  <small class="text-muted d-block" style="min-width: 140px;">Foreclosure:</small>
                  <div class="d-flex align-items-center gap-2">
                    <span class="fw-semibold text-dark">
                      {{ timelineData.foreclosure_months != null ? timelineData.foreclosure_months : '—' }} months
                    </span>
                    <div class="btn-group btn-group-sm reo-duration-controls" role="group">
                      <button
                        type="button"
                        class="btn btn-outline-secondary"
                        @click="adjustReoFcDuration(-1)"
                        :disabled="loadingTimelines || timelineData.foreclosure_months_base == null"
                        title="Subtract 1 month"
                      >
                        <i v-if="loadingTimelines" class="mdi mdi-refresh mdi-spin"></i>
                        <i v-else class="mdi mdi-minus"></i>
                      </button>
                      <button
                        type="button"
                        class="btn btn-outline-secondary"
                        @click="adjustReoFcDuration(1)"
                        :disabled="loadingTimelines || timelineData.foreclosure_months_base == null"
                        title="Add 1 month"
                      >
                        <i v-if="loadingTimelines" class="mdi mdi-refresh mdi-spin"></i>
                        <i v-else class="mdi mdi-plus"></i>
                      </button>
                    </div>
                    <span v-if="timelineData.reo_fc_duration_override_months != null && timelineData.reo_fc_duration_override_months !== 0" 
                          class="badge" 
                          :class="timelineData.reo_fc_duration_override_months > 0 ? 'bg-success' : 'bg-danger'"
                          style="font-size: 0.7rem;">
                      {{ timelineData.reo_fc_duration_override_months > 0 ? '+' : '' }}{{ timelineData.reo_fc_duration_override_months }}
                    </span>
                  </div>
                </div>
                
                <!-- REO Renovation with +/- controls (only shown in Rehab scenario) -->
                <div v-if="reoScenario === 'rehab'" class="d-flex align-items-baseline gap-2">
                  <small class="text-muted d-block" style="min-width: 140px;">REO Renovation:</small>
                  <div class="d-flex align-items-center gap-2">
                    <span class="fw-semibold text-dark">
                      {{ timelineData.reo_renovation_months != null ? timelineData.reo_renovation_months : '—' }} months
                    </span>
                    <div class="btn-group btn-group-sm reo-duration-controls" role="group">
                      <button
                        type="button"
                        class="btn btn-outline-secondary"
                        @click="adjustReoRenovationDuration(-1)"
                        :disabled="loadingTimelines"
                        title="Subtract 1 month"
                      >
                        <i v-if="loadingTimelines" class="mdi mdi-refresh mdi-spin"></i>
                        <i v-else class="mdi mdi-minus"></i>
                      </button>
                      <button
                        type="button"
                        class="btn btn-outline-secondary"
                        @click="adjustReoRenovationDuration(1)"
                        :disabled="loadingTimelines"
                        title="Add 1 month"
                      >
                        <i v-if="loadingTimelines" class="mdi mdi-refresh mdi-spin"></i>
                        <i v-else class="mdi mdi-plus"></i>
                      </button>
                    </div>
                    <span v-if="timelineData.reo_renovation_override_months != null && timelineData.reo_renovation_override_months !== 0" 
                          class="badge" 
                          :class="timelineData.reo_renovation_override_months > 0 ? 'bg-success' : 'bg-danger'"
                          style="font-size: 0.7rem;">
                      {{ timelineData.reo_renovation_override_months > 0 ? '+' : '' }}{{ timelineData.reo_renovation_override_months }}
                    </span>
                  </div>
                </div>
                
                <!-- REO Marketing with +/- controls -->
                <div class="d-flex align-items-baseline gap-2">
                  <small class="text-muted d-block" style="min-width: 140px;">REO Marketing:</small>
                  <div class="d-flex align-items-center gap-2">
                    <span class="fw-semibold text-dark">
                      {{ timelineData.reo_marketing_months != null ? timelineData.reo_marketing_months : '—' }} months
                    </span>
                    <div class="btn-group btn-group-sm reo-duration-controls" role="group">
                      <button
                        type="button"
                        class="btn btn-outline-secondary"
                        @click="adjustReoMarketingDuration(-1)"
                        :disabled="loadingTimelines || timelineData.reo_marketing_months_base == null"
                        title="Subtract 1 month"
                      >
                        <i v-if="loadingTimelines" class="mdi mdi-refresh mdi-spin"></i>
                        <i v-else class="mdi mdi-minus"></i>
                      </button>
                      <button
                        type="button"
                        class="btn btn-outline-secondary"
                        @click="adjustReoMarketingDuration(1)"
                        :disabled="loadingTimelines || timelineData.reo_marketing_months_base == null"
                        title="Add 1 month"
                      >
                        <i v-if="loadingTimelines" class="mdi mdi-refresh mdi-spin"></i>
                        <i v-else class="mdi mdi-plus"></i>
                      </button>
                    </div>
                    <span v-if="timelineData.reo_marketing_override_months != null && timelineData.reo_marketing_override_months !== 0" 
                          class="badge" 
                          :class="timelineData.reo_marketing_override_months > 0 ? 'bg-success' : 'bg-danger'"
                          style="font-size: 0.7rem;">
                      {{ timelineData.reo_marketing_override_months > 0 ? '+' : '' }}{{ timelineData.reo_marketing_override_months }}
                    </span>
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
                <div class="d-flex align-items-baseline gap-2">
                  <small class="text-muted d-block" style="min-width: 140px;">REO Holding Costs:</small>
                  <span class="fw-bold text-dark">{{ formatCurrency(timelineData.reo_holding_costs || 0) }}</span>
                </div>
                <!-- Trashout (As-Is only) -->
                <div v-if="reoScenario === 'as_is'" class="d-flex align-items-baseline gap-2">
                  <small class="text-muted d-block" style="min-width: 140px;">Trashout:</small>
                  <span class="fw-bold text-dark">{{ formatCurrency(timelineData.trashout_cost || 0) }}</span>
                </div>
                <!-- Renovation Cost (Rehab only) -->
                <div v-if="reoScenario === 'rehab'" class="d-flex align-items-baseline gap-2">
                  <small class="text-muted d-block" style="min-width: 140px;">Renovation Cost:</small>
                  <span class="fw-bold text-dark">{{ formatCurrency(timelineData.renovation_cost || 0) }}</span>
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
                  <small class="text-muted d-block" style="min-width: 160px;">Broker Fees:</small>
                  <span class="fw-bold text-dark">{{ formatCurrency(reoScenario === 'as_is' ? (timelineData.broker_fees || 0) : (timelineData.broker_fees_arv || 0)) }}</span>
                </div>
                <div class="d-flex align-items-baseline gap-2">
                  <small class="text-muted d-block" style="min-width: 160px;">Servicer Liquidation Fee:</small>
                  <span class="fw-bold text-dark">{{ formatCurrency(reoScenario === 'as_is' ? (timelineData.servicer_liquidation_fee || 0) : (timelineData.servicer_liquidation_fee_arv || 0)) }}</span>
                </div>
                <div class="d-flex align-items-baseline gap-2">
                  <small class="text-muted d-block" style="min-width: 160px;">AM Liquidation Fee:</small>
                  <span class="fw-bold text-dark">{{ formatCurrency(reoScenario === 'as_is' ? (timelineData.am_liquidation_fee || 0) : (timelineData.am_liquidation_fee_arv || 0)) }}</span>
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

// WHAT: Props for the REOSaleModelCard component
const props = defineProps<{
  // WHAT: Row data containing existing REO information from SellerRawData
  row?: Record<string, any> | null
  // WHAT: Asset ID for fetching additional REO data if needed
  assetId?: string | number | null
  // WHAT: Whether this is the only selected model (auto-sets to 100% if true)
  isOnlySelectedModel?: boolean
  // WHAT: Shared acquisition price value from parent to sync across all models
  sharedAcquisitionPrice?: number
}>()

// WHAT: Emits for parent component communication
const emit = defineEmits<{
  assumptionsChanged: [assumptions: ReoAssumptions]
  probabilityChanged: [probability: number]
  acquisitionPriceChanged: [price: number]
}>()

// WHAT: Interface for REO model assumptions
interface ReoAssumptions {
  expectedSalePrice: number
  // WHAT: Expense fields
  servicingFees: number
  taxes: number
  insurance: number
  legalCost: number
  reoHoldingCosts: number
}

// WHAT: Reactive state for component
const collapsed = ref(false)

// WHAT: REO Sale probability (auto-sets to 100% if only model selected)
const reoProbability = ref<number>(0)

// WHAT: Timeline data from backend API
const timelineData = reactive<{
  servicing_transfer_months: number | null
  foreclosure_months: number | null
  foreclosure_months_base: number | null
  reo_fc_duration_override_months: number | null
  reo_renovation_months: number | null
  reo_renovation_months_base: number | null
  reo_renovation_override_months: number | null
  reo_marketing_months: number | null
  reo_marketing_months_base: number | null
  reo_marketing_override_months: number | null
  total_timeline_months: number | null
  expected_recovery: number | null
  expected_proceeds_asis: number | null
  expected_proceeds_arv: number | null
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
  reo_holding_costs: number | null
  trashout_cost: number | null
  renovation_cost: number | null
  // WHAT: Liquidation Expense values from backend models - As-Is
  broker_fees: number | null
  servicer_liquidation_fee: number | null
  am_liquidation_fee: number | null
  // WHAT: Liquidation Expense values - Rehab/ARV
  broker_fees_arv: number | null
  servicer_liquidation_fee_arv: number | null
  am_liquidation_fee_arv: number | null
  // WHAT: Calculated financial metrics from backend - As-Is
  total_costs: number | null
  total_costs_asis: number | null
  net_pl_asis: number | null
  moic_asis: number | null
  annualized_roi_asis: number | null
  // WHAT: Calculated financial metrics - Rehab
  total_costs_rehab: number | null
  net_pl_rehab: number | null
  moic_rehab: number | null
  annualized_roi_rehab: number | null
  // WHAT: Legacy fields
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
  foreclosure_months: null,
  foreclosure_months_base: null,
  reo_fc_duration_override_months: null,
  reo_renovation_months: null,
  reo_renovation_months_base: null,
  reo_renovation_override_months: null,
  reo_marketing_months: null,
  reo_marketing_months_base: null,
  reo_marketing_override_months: null,
  total_timeline_months: null,
  expected_recovery: null,
  expected_proceeds_asis: null,
  expected_proceeds_arv: null,
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
  reo_holding_costs: null,
  trashout_cost: null,
  renovation_cost: null,
  broker_fees: null,
  servicer_liquidation_fee: null,
  am_liquidation_fee: null,
  broker_fees_arv: null,
  servicer_liquidation_fee_arv: null,
  am_liquidation_fee_arv: null,
  total_costs: null,
  total_costs_asis: null,
  total_costs_rehab: null,
  net_pl: null,
  net_pl_asis: null,
  net_pl_rehab: null,
  moic: null,
  moic_asis: null,
  moic_rehab: null,
  annualized_roi: null,
  annualized_roi_asis: null,
  annualized_roi_rehab: null,
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

// WHAT: REO scenario toggle (As-Is vs Rehab)
// WHY: Allow user to switch between different REO scenarios
const reoScenario = ref<'as_is' | 'rehab'>('as_is')

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

// WHAT: Minimal assumptions (kept for compatibility)
const assumptions = reactive<ReoAssumptions>({
  expectedSalePrice: 0,
  servicingFees: 0,
  taxes: 0,
  insurance: 0,
  legalCost: 0,
  reoHoldingCosts: 0
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
  assumptions.reoHoldingCosts = timelineData.reo_holding_costs ?? 0
  emitChanges()
}, { deep: true })

// WHAT: Computed property for total duration based on REO scenario
// WHY: As-Is scenario excludes renovation, Rehab includes it
const calculatedTotalDuration = computed(() => {
  const servicing = timelineData.servicing_transfer_months || 0
  const foreclosure = timelineData.foreclosure_months || 0
  const renovation = timelineData.reo_renovation_months || 0
  const marketing = timelineData.reo_marketing_months || 0
  
  // WHAT: For As-Is scenario, exclude renovation duration
  if (reoScenario.value === 'as_is') {
    return servicing + foreclosure + marketing
  } else {
    // WHAT: For Rehab scenario, include renovation duration
    return servicing + foreclosure + renovation + marketing
  }
})

// WHAT: Computed property to display total costs based on scenario
// WHY: Use backend-calculated value for As-Is or Rehab
const calculatedTotalCosts = computed(() => {
  return reoScenario.value === 'as_is' 
    ? (timelineData.total_costs_asis || 0)
    : (timelineData.total_costs_rehab || 0)
})

// WHAT: Computed property to display net PL with real-time updates
// WHY: Net PL = Expected Proceeds - Total Costs - Acquisition Price
// HOW: Use correct proceeds and costs based on scenario (As-Is vs Rehab), update in real-time with acquisition price changes
const calculatedNetRecovery = computed(() => {
  const expectedProceeds = reoScenario.value === 'as_is' 
    ? (timelineData.expected_proceeds_asis || 0)
    : (timelineData.expected_proceeds_arv || 0)
  const totalCosts = reoScenario.value === 'as_is'
    ? (timelineData.total_costs_asis || 0)
    : (timelineData.total_costs_rehab || 0)
  const acqPrice = acquisitionPrice.value || 0
  
  return expectedProceeds - totalCosts - acqPrice
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

// WHAT: Computed property for validation messages
const validationMessages = computed(() => {
  const messages: string[] = []
  
  if (reoProbability.value < 0 || reoProbability.value > 100) {
    messages.push('REO Sale probability must be between 0% and 100%')
  }
  
  return messages
})

// WHAT: Function to adjust REO FC duration by increment/decrement
// WHY: Allow users to adjust REO FC duration independently from FC Sale model
async function adjustReoFcDuration(change: number) {
  if (!props.assetId) {
    console.warn('[REOSaleModelCard] No assetId provided, cannot adjust REO FC duration')
    return
  }

  const currentOverride = timelineData.reo_fc_duration_override_months || 0
  const newOverride = currentOverride + change

  try {
    loadingTimelines.value = true
    await http.post(`/acq/assets/${props.assetId}/reo-fc-duration-override/`, {
      reo_fc_duration_override_months: newOverride
    })
    await fetchTimelineData()
  } catch (error) {
    console.error('[REOSaleModelCard] Failed to update REO FC duration override:', error)
  } finally {
    loadingTimelines.value = false
  }
}

// WHAT: Function to adjust REO renovation duration by increment/decrement
// WHY: Allow users to adjust renovation timeline for REO properties
async function adjustReoRenovationDuration(change: number) {
  if (!props.assetId) {
    console.warn('[REOSaleModelCard] No assetId provided, cannot adjust REO renovation duration')
    return
  }

  const currentOverride = timelineData.reo_renovation_override_months || 0
  const newOverride = currentOverride + change

  try {
    loadingTimelines.value = true
    await http.post(`/acq/assets/${props.assetId}/reo-renovation-override/`, {
      reo_renovation_override_months: newOverride
    })
    await fetchTimelineData()
  } catch (error) {
    console.error('[REOSaleModelCard] Failed to update REO renovation duration override:', error)
  } finally {
    loadingTimelines.value = false
  }
}

// WHAT: Function to adjust REO marketing duration by increment/decrement
// WHY: Allow users to adjust marketing timeline based on market conditions
async function adjustReoMarketingDuration(change: number) {
  if (!props.assetId) {
    console.warn('[REOSaleModelCard] No assetId provided, cannot adjust REO marketing duration')
    return
  }

  const currentOverride = timelineData.reo_marketing_override_months || 0
  const newOverride = currentOverride + change

  try {
    loadingTimelines.value = true
    await http.post(`/acq/assets/${props.assetId}/reo-marketing-override/`, {
      reo_marketing_override_months: newOverride
    })
    await fetchTimelineData()
  } catch (error) {
    console.error('[REOSaleModelCard] Failed to update REO marketing duration override:', error)
  } finally {
    loadingTimelines.value = false
  }
}

// WHAT: Function to fetch timeline data from backend API
async function fetchTimelineData() {
  if (!props.assetId) {
    console.warn('[REOSaleModelCard] No assetId provided, cannot fetch timeline data')
    return
  }

  loadingTimelines.value = true
  try {
    const response = await http.get(`/acq/assets/${props.assetId}/reo-model-sums/`)
    Object.assign(timelineData, response.data)
    
    // WHAT: Sync acquisition price to local state
    // WHY: Allow editing in the input field
    if (response.data.acquisition_price != null) {
      acquisitionPrice.value = response.data.acquisition_price
    }
  } catch (error) {
    console.error('[REOSaleModelCard] Failed to fetch timeline data:', error)
    // Keep null values on error
  } finally {
    loadingTimelines.value = false
  }
}

// WHAT: Function to save acquisition price to backend
// WHY: Persist user-entered acquisition price
async function saveAcquisitionPrice() {
  if (!props.assetId) {
    console.warn('[REOSaleModelCard] No assetId provided, cannot save acquisition price')
    return
  }

  try {
    await http.post(`/acq/assets/${props.assetId}/acquisition-price/`, {
      acquisition_price: acquisitionPrice.value || 0
    })
    
    console.log('[REOSaleModelCard] Acquisition price saved:', acquisitionPrice.value)
    
    // Note: No need to emit here, already emitting on every value change via computed setter
    
    // WHAT: Refresh timeline data to get updated calculations
    // WHY: Acquisition price affects other calculations (broker fees, etc.)
    await fetchTimelineData()
  } catch (error) {
    console.error('[REOSaleModelCard] Failed to save acquisition price:', error)
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

// WHAT: Function to emit changes to parent component
function emitChanges() {
  emit('assumptionsChanged', { ...assumptions })
}

// WHAT: Function to handle probability change
function handleProbabilityChange() {
  emit('probabilityChanged', reoProbability.value)
}

// WHAT: Watch for changes in assumptions and emit to parent
watch(assumptions, () => {
  emitChanges()
}, { deep: true })

// WHAT: Watch for isOnlySelectedModel prop - auto-set to 100% if only model selected
watch(() => props.isOnlySelectedModel, (isOnly) => {
  if (isOnly && reoProbability.value !== 100) {
    reoProbability.value = 100
    emit('probabilityChanged', reoProbability.value)
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
</script>

<style scoped>
/* WHAT: Component-specific styles for REOSaleModelCard */
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

/* WHAT: Smaller REO duration control buttons */
.reo-duration-controls {
  /* WHAT: Make the button group itself smaller */
  font-size: 0.7rem;
}

.reo-duration-controls .btn {
  /* WHAT: Smaller padding for compact buttons */
  padding: 0.15rem 0.35rem !important;
  /* WHAT: Smaller line height */
  line-height: 1.2;
  /* WHAT: Smaller font size */
  font-size: 0.7rem;
  /* WHAT: Minimal width */
  min-width: auto;
}

.reo-duration-controls .btn i {
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
</style>

