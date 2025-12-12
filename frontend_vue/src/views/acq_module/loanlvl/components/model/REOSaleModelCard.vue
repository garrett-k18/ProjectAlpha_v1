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
      <!-- REO Scenario Toggle -->
      <div class="mb-3">
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
              ARV
            </button>
          </div>
        </div>
      </div>

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
              <small class="text-muted d-block">IRR | MOIC</small>
              <span class="fw-bold">
                <span :class="(liveIRR ?? 0) >= 0 ? 'text-success' : 'text-danger'">
                  {{ liveIRR != null ? ((liveIRR * 100).toFixed(1) + '%') : '—' }}
                </span>
                <span class="text-muted mx-1">|</span>
                <span :class="liveMOIC >= 1 ? 'text-success' : 'text-danger'">
                  {{ liveMOIC.toFixed(2) }}x
                </span>
              </span>
            </div>
          </div>
          <div class="col-md-2">
            <div class="text-center p-2 bg-light rounded h-100">
              <small class="text-muted d-block">NPV</small>
              <span class="fw-bold" :class="(liveNPV ?? 0) >= 0 ? 'text-success' : 'text-danger'">
                {{ liveNPV != null ? formatCurrency(liveNPV) : '—' }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Key Inputs Section -->
      <div class="mb-4 p-3 bg-light rounded border text-center acquisition-price-card">
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
              <div class="d-flex align-items-center justify-content-between mb-2">
                <h6 class="fw-semibold text-body mb-0">
                  <i class="mdi mdi-clock-outline me-2 text-warning"></i>
                  Timelines
                </h6>
                <!-- Reset to Default Button -->
                <button
                  v-if="hasTimelineOverrides"
                  type="button"
                  class="btn btn-sm btn-outline-secondary"
                  @click="resetTimelineOverrides"
                  :disabled="loadingTimelines"
                  title="Reset all timeline overrides to default"
                >
                  <i v-if="loadingTimelines" class="mdi mdi-refresh mdi-spin"></i>
                  <i v-else class="mdi mdi-restore"></i>
                  <span class="ms-1 d-none d-sm-inline">Reset</span>
                </button>
              </div>
              <div class="d-flex flex-column gap-2">
                <div class="timeline-row">
                  <small class="timeline-label text-muted">Servicing Transfer:</small>
                  <div class="timeline-value-group">
                    <span class="timeline-override-badge is-empty"></span>
                    <span class="fw-semibold text-dark timeline-months-value">
                      {{ timelineData.servicing_transfer_months != null ? timelineData.servicing_transfer_months : '—' }} months
                    </span>
                  </div>
                  <div class="timeline-controls-placeholder"></div>
                </div>
                
                <!-- Foreclosure with +/- controls -->
                <div class="timeline-row">
                  <small class="timeline-label text-muted">Foreclosure:</small>
                  <div class="timeline-value-group">
                    <span 
                      class="timeline-override-badge"
                      :class="{
                        'is-empty': !timelineData.reo_fc_duration_override_months,
                        'bg-danger text-white': (timelineData.reo_fc_duration_override_months || 0) > 0,
                        'bg-success text-white': (timelineData.reo_fc_duration_override_months || 0) < 0
                      }"
                    >
                      <template v-if="timelineData.reo_fc_duration_override_months">
                        {{ timelineData.reo_fc_duration_override_months > 0 ? '+' : '' }}{{ timelineData.reo_fc_duration_override_months }}
                      </template>
                    </span>
                    <span class="fw-semibold text-dark timeline-months-value">
                      {{ timelineData.foreclosure_months != null ? timelineData.foreclosure_months : '—' }} months
                    </span>
                  </div>
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
                </div>
                
                <!-- REO Renovation with +/- controls (only shown in Rehab scenario) -->
                <div v-if="reoScenario === 'rehab'" class="timeline-row">
                  <small class="timeline-label text-muted">REO Renovation:</small>
                  <div class="timeline-value-group">
                    <span 
                      class="timeline-override-badge"
                      :class="{
                        'is-empty': !timelineData.reo_renovation_override_months,
                        'bg-danger text-white': (timelineData.reo_renovation_override_months || 0) > 0,
                        'bg-success text-white': (timelineData.reo_renovation_override_months || 0) < 0
                      }"
                    >
                      <template v-if="timelineData.reo_renovation_override_months">
                        {{ timelineData.reo_renovation_override_months > 0 ? '+' : '' }}{{ timelineData.reo_renovation_override_months }}
                      </template>
                    </span>
                    <span class="fw-semibold text-dark timeline-months-value">
                      {{ timelineData.reo_renovation_months != null ? timelineData.reo_renovation_months : '—' }} months
                    </span>
                  </div>
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
                </div>
                
                <!-- REO Marketing with +/- controls -->
                <div class="timeline-row">
                  <small class="timeline-label text-muted">REO Marketing:</small>
                  <div class="timeline-value-group">
                    <span 
                      class="timeline-override-badge"
                      :class="{
                        'is-empty': !timelineData.reo_marketing_override_months,
                        'bg-danger text-white': (timelineData.reo_marketing_override_months || 0) > 0,
                        'bg-success text-white': (timelineData.reo_marketing_override_months || 0) < 0
                      }"
                    >
                      <template v-if="timelineData.reo_marketing_override_months">
                        {{ timelineData.reo_marketing_override_months > 0 ? '+' : '' }}{{ timelineData.reo_marketing_override_months }}
                      </template>
                    </span>
                    <span class="fw-semibold text-dark timeline-months-value">
                      {{ timelineData.reo_marketing_months != null ? timelineData.reo_marketing_months : '—' }} months
                    </span>
                  </div>
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
                  <span class="fw-bold text-dark">{{ formatCurrency(timelineData.acq_broker_fees || 0) }}</span>
                </div>
                <div class="d-flex align-items-baseline gap-2">
                  <small class="text-muted d-block" style="min-width: 140px;">Other Fees:</small>
                  <span class="fw-bold text-dark">{{ formatCurrency(timelineData.acq_other_fees || 0) }}</span>
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

      <!-- WHAT: Cash Flow Series Component (horizontal expandable) -->
      <!-- WHY: Display period-by-period cash flow breakdown in horizontal format -->
      <REOCashFlowSeries
        v-if="assetId"
        :assetId="assetId"
        :initialScenario="reoScenario === 'as_is' ? 'as_is' : 'arv'"
        @irr-changed="handleIrrChanged"
        @npv-changed="handleNpvChanged"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch, onMounted } from 'vue'
import http from '@/lib/http'
import REOCashFlowSeries from '@/components/custom/REOCashFlowSeries.vue'
import { calculateXIRR, calculateNPV } from '@/lib/financial'

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
  // WHAT: Monthly rates for carry cost recalculation
  monthly_tax: number | null
  monthly_insurance: number | null
  monthly_reo_holding: number | null
  // WHAT: Individual REO holding cost components for detailed recalculation
  monthly_hoa: number | null
  monthly_utilities: number | null
  monthly_property_preservation: number | null
  // WHAT: Servicer fee components for servicing fee recalculation
  board_fee: number | null
  onetwentyday_fee: number | null
  fc_fee: number | null
  reo_fee: number | null
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
  monthly_tax: null,
  monthly_insurance: null,
  monthly_reo_holding: null,
  monthly_hoa: null,
  monthly_utilities: null,
  monthly_property_preservation: null,
  board_fee: null,
  onetwentyday_fee: null,
  fc_fee: null,
  reo_fee: null,
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

// WHAT: Build simplified cash flow array with dates from current inputs for instant XIRR/NPV calculation
// WHY: Calculate XIRR/NPV instantly from current data without waiting for backend API
// HOW: Create monthly cash flow with actual dates: period 0 = -acq, monthly = -carry, final = +proceeds
const simplifiedCashFlow = computed(() => {
  const acqPrice = acquisitionPrice.value || 0
  const totalCosts = calculatedTotalCosts.value
  const expectedProceeds = reoScenario.value === 'as_is' 
    ? (timelineData.expected_proceeds_asis || 0)
    : (timelineData.expected_proceeds_arv || 0)
  const totalDuration = calculatedTotalDuration.value || 0
  
  if (totalDuration <= 0) {
    return []
  }
  
  // WHAT: Get settlement date (default to today if not available)
  // WHY: XIRR requires actual dates for accurate calculation
  let settlementDate: Date
  try {
    // WHAT: Try to get settlement date from cash flow data if available
    // NOTE: For now, use today as start date - can be enhanced to get from API later
    settlementDate = new Date()
  } catch {
    settlementDate = new Date()
  }
  
  // WHAT: Acquisition costs (one-time at period 0)
  const acquisitionCosts = (
    (timelineData.acq_broker_fees || 0) +
    (timelineData.acq_other_fees || 0) +
    (timelineData.acq_legal || 0) +
    (timelineData.acq_dd || 0) +
    (timelineData.acq_tax_title || 0)
  )
  
  // WHAT: Build cash flow array with dates for XIRR
  const cashFlows: Array<{ amount: number; date: Date }> = []
  
  // WHAT: Period 0: Acquisition price + acquisition costs (negative = outflow) at settlement date
  cashFlows.push({
    amount: -(acqPrice + acquisitionCosts),
    date: new Date(settlementDate)
  })
  
  // WHAT: Monthly periods: spread remaining costs evenly (negative = outflow)
  const remainingCosts = totalCosts - acquisitionCosts
  const monthlyCarry = remainingCosts / totalDuration
  
  for (let i = 0; i < totalDuration; i++) {
    // WHAT: Calculate date for this period (add i+1 months to settlement date)
    const periodDate = new Date(settlementDate)
    periodDate.setMonth(periodDate.getMonth() + i + 1)
    
    cashFlows.push({
      amount: -monthlyCarry,
      date: periodDate
    })
  }
  
  // WHAT: Final period: add proceeds (positive = inflow)
  cashFlows[cashFlows.length - 1].amount += expectedProceeds
  
  return cashFlows
})

// WHAT: Calculate XIRR from simplified cash flow array with dates for instant updates
// WHY: Update XIRR instantly when acquisition price, costs, proceeds, or duration change
// HOW: Uses XIRR with actual dates for more accurate calculation (equivalent to Excel XIRR)
const liveIRR = computed(() => {
  const cashFlows = simplifiedCashFlow.value
  if (!cashFlows || cashFlows.length < 2) {
    return null
  }
  // WHAT: Convert to format expected by node-irr xirr function (date as string YYYY-MM-DD)
  const xirrInputs = cashFlows.map(cf => ({
    amount: cf.amount,
    date: cf.date.toISOString().split('T')[0] // Format as YYYY-MM-DD
  }))
  const calculatedIRR = calculateXIRR(xirrInputs)
  return calculatedIRR > 0 ? calculatedIRR : null
})

// WHAT: Calculate NPV from simplified cash flow array with dates for instant updates
// WHY: Update NPV instantly when acquisition price, costs, proceeds, or duration change
// NOTE: Uses 10% discount rate - can be made configurable later with total_discount from trade assumptions
const liveNPV = computed(() => {
  const cashFlows = simplifiedCashFlow.value
  if (!cashFlows || cashFlows.length === 0) {
    return null
  }
  // WHAT: Convert to format expected by calculateNPV (date as string YYYY-MM-DD)
  const npvInputs = cashFlows.map(cf => ({
    amount: cf.amount,
    date: cf.date.toISOString().split('T')[0] // Format as YYYY-MM-DD
  }))
  const discountRate = 0.10 // 10% annual discount rate (can use total_discount from trade assumptions later)
  return calculateNPV(npvInputs, discountRate)
})

// WHAT: Cash flow IRR and NPV values from backend (fallback if frontend calc fails)
// WHY: Store IRR and NPV calculated from detailed cash flow series as backup
const cashFlowIrr = ref<number | null>(null)
const cashFlowNpv = ref<number | null>(null)

// WHAT: Handle IRR changes from cash flow component (detailed backend calculation)
function handleIrrChanged(irr: number | null) {
  cashFlowIrr.value = irr
}

// WHAT: Handle NPV changes from cash flow component (detailed backend calculation)
function handleNpvChanged(npv: number | null) {
  cashFlowNpv.value = npv
}

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
  legalCost: 0,
  reoHoldingCosts: 0
})

// WHAT: Hybrid Calculation Architecture - Instant carry cost recalculation
// WHY: Industry best practice for financial applications (Bloomberg Terminal, Salesforce, Banking platforms)
// HOW: Backend provides authoritative calculations + monthly rates, frontend recalculates instantly on duration changes
// BENEFITS: 
//   - Instant UX: No 3-second waits for simple +/- button clicks
//   - Backend Authority: All permanent calculations remain server-side for audit/compliance
//   - Reduced Load: Avoid unnecessary API calls for UI interactions
//   - Data Consistency: Backend sends both final values AND calculation components
//   - Fallback Safety: If frontend calc fails, backend values remain unchanged
function recalculateCarryCosts(skipReoHolding = false) {
  const totalMonths = timelineData.total_timeline_months || 0
  const servicingMonths = timelineData.servicing_transfer_months || 0
  const foreclosureMonths = timelineData.foreclosure_months || 0
  const renovationMonths = timelineData.reo_renovation_months || 0
  const marketingMonths = timelineData.reo_marketing_months || 0
  const reoMonths = renovationMonths + marketingMonths
  
  // WHAT: Recalculate servicing fees (board_fee + onetwentyday_fee*servicing + fc_fee*foreclosure + reo_fee*reo)
  // WHY: Servicing fees change based on duration of each phase
  if (timelineData.board_fee !== null && timelineData.onetwentyday_fee !== null && 
      timelineData.fc_fee !== null && timelineData.reo_fee !== null) {
    let servicingFees = timelineData.board_fee || 0
    servicingFees += (timelineData.onetwentyday_fee || 0) * servicingMonths
    servicingFees += (timelineData.fc_fee || 0) * foreclosureMonths
    servicingFees += (timelineData.reo_fee || 0) * reoMonths
    
    // WHAT: Round to penny precision to avoid floating point errors
    servicingFees = Math.round(servicingFees * 100) / 100
    
    timelineData.servicing_fees = servicingFees
    expenses.servicingFees = servicingFees
    
    console.log(`[REO] Recalculated servicing fees: $${servicingFees.toFixed(2)} (Board: $${timelineData.board_fee}, 120-day: $${timelineData.onetwentyday_fee}*${servicingMonths}, FC: $${timelineData.fc_fee}*${foreclosureMonths}, REO: $${timelineData.reo_fee}*${reoMonths})`)
  }
  
  // WHAT: Recalculate taxes (monthly_tax * total_timeline_months)
  // WHY: Property taxes accrue monthly throughout entire timeline
  if (timelineData.monthly_tax && totalMonths > 0) {
    // WHAT: Round to penny precision to avoid floating point errors
    timelineData.taxes = Math.round(timelineData.monthly_tax * totalMonths * 100) / 100
    expenses.taxes = timelineData.taxes
    console.log(`[REO] Recalculated taxes: $${timelineData.taxes.toFixed(2)} (${timelineData.monthly_tax}/month * ${totalMonths} months)`)
  } else {
    expenses.taxes = timelineData.taxes ?? 0
  }
  
  // WHAT: Recalculate insurance (monthly_insurance * total_timeline_months)
  // WHY: Property insurance is required monthly throughout entire timeline
  if (timelineData.monthly_insurance && totalMonths > 0) {
    // WHAT: Round to penny precision to avoid floating point errors
    timelineData.insurance = Math.round(timelineData.monthly_insurance * totalMonths * 100) / 100
    expenses.insurance = timelineData.insurance
    console.log(`[REO] Recalculated insurance: $${timelineData.insurance.toFixed(2)} (${timelineData.monthly_insurance}/month * ${totalMonths} months)`)
  } else {
    expenses.insurance = timelineData.insurance ?? 0
  }
  
  // WHAT: Recalculate REO holding costs using individual components (renovation + marketing months)
  // WHY: REO holding costs accrue during BOTH renovation and marketing phases
  // HOW: Calculate each component separately: HOA + Utilities + Property Preservation
  // NOTE: Skip if skipReoHolding flag is set (e.g., when only foreclosure duration changes)
  const reoTotalMonths = renovationMonths + marketingMonths
  if (!skipReoHolding && reoTotalMonths > 0 && (timelineData.monthly_hoa !== null || timelineData.monthly_utilities !== null || timelineData.monthly_property_preservation !== null)) {
    let reoHoldingTotal = 0
    let breakdown = []
    
    // WHAT: Calculate HOA costs for renovation + marketing period
    if (timelineData.monthly_hoa !== null) {
      const hoaCosts = Math.round(timelineData.monthly_hoa * reoTotalMonths * 100) / 100
      reoHoldingTotal += hoaCosts
      breakdown.push(`HOA: $${timelineData.monthly_hoa}/month * ${reoTotalMonths} = $${hoaCosts.toFixed(2)}`)
    }
    
    // WHAT: Calculate utilities costs for renovation + marketing period
    if (timelineData.monthly_utilities !== null) {
      const utilityCosts = Math.round(timelineData.monthly_utilities * reoTotalMonths * 100) / 100
      reoHoldingTotal += utilityCosts
      breakdown.push(`Utilities: $${timelineData.monthly_utilities}/month * ${reoTotalMonths} = $${utilityCosts.toFixed(2)}`)
    }
    
    // WHAT: Calculate property preservation costs for renovation + marketing period
    if (timelineData.monthly_property_preservation !== null) {
      const propPresCosts = Math.round(timelineData.monthly_property_preservation * reoTotalMonths * 100) / 100
      reoHoldingTotal += propPresCosts
      breakdown.push(`Prop Pres: $${timelineData.monthly_property_preservation}/month * ${reoTotalMonths} = $${propPresCosts.toFixed(2)}`)
    }
    
    // WHAT: Round final total to penny precision
    reoHoldingTotal = Math.round(reoHoldingTotal * 100) / 100
    
    timelineData.reo_holding_costs = reoHoldingTotal
    expenses.reoHoldingCosts = reoHoldingTotal
    console.log(`[REO] Recalculated REO holding costs: $${reoHoldingTotal.toFixed(2)} (${breakdown.join(', ')}) - Renovation: ${renovationMonths} + Marketing: ${marketingMonths} = ${reoTotalMonths} months`)
  } else {
    expenses.reoHoldingCosts = timelineData.reo_holding_costs ?? 0
  }
  
  // WHAT: Other costs don't change with duration, keep backend values
  expenses.legalCost = timelineData.legal_cost ?? 0
}

// WHAT: Watch timelineData expense fields and sync to expenses object
// WHY: Update expenses when API data is fetched
watch(() => [
  timelineData.servicing_fees,
  timelineData.taxes,
  timelineData.insurance,
  timelineData.legal_cost,
  timelineData.reo_holding_costs
], () => {
  expenses.servicingFees = timelineData.servicing_fees ?? 0
  expenses.taxes = timelineData.taxes ?? 0
  expenses.insurance = timelineData.insurance ?? 0
  expenses.legalCost = timelineData.legal_cost ?? 0
  expenses.reoHoldingCosts = timelineData.reo_holding_costs ?? 0
  // WHAT: Sync to assumptions for emits
  // WHY: Keep assumptions in sync for parent component
  assumptions.servicingFees = expenses.servicingFees
  assumptions.taxes = expenses.taxes
  assumptions.insurance = expenses.insurance
  assumptions.legalCost = expenses.legalCost
  assumptions.reoHoldingCosts = expenses.reoHoldingCosts
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

// WHAT: Calculate total costs instantly using frontend expenses + backend static costs
// WHY: Instant UI feedback when carry costs change via duration adjustments
// HOW: Sum acquisition costs + carry costs (frontend) + liquidation costs (backend)
// NOTE: Maintains penny precision for calculations, display formatting is separate
const calculatedTotalCosts = computed(() => {
  // WHAT: Acquisition costs (static, from backend)
  const acquisitionCosts = (
    (timelineData.acq_broker_fees || 0) +
    (timelineData.acq_other_fees || 0) +
    (timelineData.acq_legal || 0) +
    (timelineData.acq_dd || 0) +
    (timelineData.acq_tax_title || 0)
  )
  
  // WHAT: Carry costs (dynamic, from frontend recalculation)
  const carryCosts = (
    expenses.servicingFees +
    expenses.taxes +
    expenses.insurance +
    expenses.legalCost +
    expenses.reoHoldingCosts +
    (timelineData.trashout_cost || 0) + // Static
    (reoScenario.value === 'rehab' ? (timelineData.renovation_cost || 0) : 0) // Static, rehab only
  )
  
  // WHAT: Liquidation costs (static, from backend, scenario-dependent)
  const liquidationCosts = reoScenario.value === 'as_is' 
    ? (
        (timelineData.broker_fees || 0) +
        (timelineData.servicer_liquidation_fee || 0) +
        (timelineData.am_liquidation_fee || 0)
      )
    : (
        (timelineData.broker_fees_arv || 0) +
        (timelineData.servicer_liquidation_fee_arv || 0) +
        (timelineData.am_liquidation_fee_arv || 0)
      )
  
  // WHAT: Round to penny precision to avoid floating point errors
  // WHY: JavaScript floating point can introduce tiny errors (e.g., 37800.999999999996)
  // HOW: Multiply by 100, round, divide by 100 to get exact penny amount
  const total = Math.round((acquisitionCosts + carryCosts + liquidationCosts) * 100) / 100
  
  // WHAT: Detailed logging for debugging Total Costs calculation
  console.log('=== TOTAL COSTS CALCULATION ===')
  console.log('ACQUISITION COSTS:')
  console.log(`  Broker Fee: $${(timelineData.acq_broker_fees || 0).toFixed(2)}`)
  console.log(`  Other Fees: $${(timelineData.acq_other_fees || 0).toFixed(2)}`)
  console.log(`  Legal Cost: $${(timelineData.acq_legal || 0).toFixed(2)}`)
  console.log(`  Due Diligence: $${(timelineData.acq_dd || 0).toFixed(2)}`)
  console.log(`  Tax/Title: $${(timelineData.acq_tax_title || 0).toFixed(2)}`)
  console.log(`  Subtotal: $${acquisitionCosts.toFixed(2)}`)
  console.log('CARRY COSTS (Frontend Recalculated):')
  console.log(`  Servicing Fees: $${expenses.servicingFees.toFixed(2)}`)
  console.log(`  Taxes: $${expenses.taxes.toFixed(2)}`)
  console.log(`  Insurance: $${expenses.insurance.toFixed(2)}`)
  console.log(`  Legal Cost: $${expenses.legalCost.toFixed(2)}`)
  console.log(`  REO Holding Costs: $${expenses.reoHoldingCosts.toFixed(2)}`)
  console.log(`  Trashout: $${(timelineData.trashout_cost || 0).toFixed(2)}`)
  if (reoScenario.value === 'rehab') {
    console.log(`  Renovation: $${(timelineData.renovation_cost || 0).toFixed(2)}`)
  }
  console.log(`  Subtotal: $${carryCosts.toFixed(2)}`)
  console.log('LIQUIDATION COSTS:')
  if (reoScenario.value === 'as_is') {
    console.log(`  Broker Fees: $${(timelineData.broker_fees || 0).toFixed(2)}`)
    console.log(`  Servicer Liq Fee: $${(timelineData.servicer_liquidation_fee || 0).toFixed(2)}`)
    console.log(`  AM Liq Fee: $${(timelineData.am_liquidation_fee || 0).toFixed(2)}`)
  } else {
    console.log(`  Broker Fees (ARV): $${(timelineData.broker_fees_arv || 0).toFixed(2)}`)
    console.log(`  Servicer Liq Fee (ARV): $${(timelineData.servicer_liquidation_fee_arv || 0).toFixed(2)}`)
    console.log(`  AM Liq Fee (ARV): $${(timelineData.am_liquidation_fee_arv || 0).toFixed(2)}`)
  }
  console.log(`  Subtotal: $${liquidationCosts.toFixed(2)}`)
  console.log('TOTAL COSTS:')
  console.log(`  Before rounding: $${(acquisitionCosts + carryCosts + liquidationCosts).toFixed(10)}`)
  console.log(`  After rounding: $${total.toFixed(2)}`)
  console.log('=== END TOTAL COSTS ===')
  
  return total
})

// WHAT: Computed property to display net PL with instant updates
// WHY: Net PL = Expected Proceeds - Total Costs - Acquisition Price (all components update instantly)
// HOW: Use instant calculatedTotalCosts for real-time feedback on duration changes
const calculatedNetRecovery = computed(() => {
  const expectedProceeds = reoScenario.value === 'as_is' 
    ? (timelineData.expected_proceeds_asis || 0)
    : (timelineData.expected_proceeds_arv || 0)
  const totalCosts = calculatedTotalCosts.value // Use instant total costs calculation
  const acqPrice = acquisitionPrice.value || 0
  
  const netPL = expectedProceeds - totalCosts - acqPrice
  console.log(`[REO] Net PL: $${netPL} (Proceeds: $${expectedProceeds} - Costs: $${totalCosts} - Acq: $${acqPrice})`)
  return netPL
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

// WHAT: Computed property for live-updating MOIC (Multiple on Invested Capital) with instant total costs
// WHY: Update MOIC instantly as duration/costs change (not waiting for backend)
// HOW: MOIC = (Expected Proceeds) / (Total Costs + Acquisition Price)
const liveMOIC = computed(() => {
  const expectedProceeds = reoScenario.value === 'as_is' 
    ? (timelineData.expected_proceeds_asis || 0)
    : (timelineData.expected_proceeds_arv || 0)
  const totalCosts = calculatedTotalCosts.value  // Use instant calculated costs, not backend values
  const acqPrice = acquisitionPrice.value || 0
  const totalOutflows = totalCosts + acqPrice
  
  if (totalOutflows <= 0 || expectedProceeds <= 0) {
    return 0
  }
  
  const moic = expectedProceeds / totalOutflows
  console.log(`[REO] MOIC: ${moic.toFixed(2)}x (Proceeds: $${expectedProceeds} / Outflows: $${totalOutflows})`)
  return moic
})

// WHAT: Computed property for live-updating Annualized ROI with instant total costs
// WHY: Update Annualized ROI instantly as duration/costs change (not waiting for backend)
// HOW: Annualized ROI = ((Net PL / Gross Cost) + 1) ^ (12 / total_duration) - 1
const liveAnnualizedROI = computed(() => {
  const expectedProceeds = reoScenario.value === 'as_is' 
    ? (timelineData.expected_proceeds_asis || 0)
    : (timelineData.expected_proceeds_arv || 0)
  const totalCosts = calculatedTotalCosts.value  // Use instant calculated costs, not backend values
  const acqPrice = acquisitionPrice.value || 0
  const grossCost = acqPrice + totalCosts
  const netPL = expectedProceeds - totalCosts - acqPrice
  const totalDuration = calculatedTotalDuration.value || 1 // Avoid division by zero
  
  if (grossCost <= 0 || totalDuration <= 0) {
    return 0
  }
  
  const returnRatio = (netPL / grossCost) + 1
  const annualizedROI = Math.pow(returnRatio, 12 / totalDuration) - 1
  
  console.log(`[REO] Annualized ROI Calculation:`)
  console.log(`  Expected Proceeds: $${expectedProceeds.toFixed(2)}`)
  console.log(`  Total Costs (instant): $${totalCosts.toFixed(2)}`)
  console.log(`  Acquisition Price: $${acqPrice.toFixed(2)}`)
  console.log(`  Gross Cost (Costs + Acq): $${grossCost.toFixed(2)}`)
  console.log(`  Net PL (Proceeds - Costs - Acq): $${netPL.toFixed(2)}`)
  console.log(`  Total Duration: ${totalDuration} months`)
  console.log(`  Return Ratio (NetPL/GrossCost + 1): ${returnRatio.toFixed(4)}`)
  console.log(`  Annualized ROI: ${(annualizedROI * 100).toFixed(2)}%`)
  return annualizedROI
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

  // WHAT: Update local state immediately for instant feedback
  const baseMonths = timelineData.foreclosure_months_base || 0
  timelineData.reo_fc_duration_override_months = newOverride
  timelineData.foreclosure_months = baseMonths + newOverride
  
  // WHAT: Update total timeline (servicing + foreclosure + renovation + marketing)
  const servicingMonths = timelineData.servicing_transfer_months || 0
  const renovationMonths = timelineData.reo_renovation_months || 0
  const marketingMonths = timelineData.reo_marketing_months || 0
  timelineData.total_timeline_months = servicingMonths + timelineData.foreclosure_months + renovationMonths + marketingMonths

  // WHAT: Recalculate carry costs with new foreclosure duration
  // WHY: Update taxes, insurance, and servicing fees instantly
  // NOTE: REO holding costs should NOT change when foreclosure changes (only when REO Marketing changes)
  recalculateCarryCosts(true)  // Skip REO holding cost recalculation

  // WHAT: Save to backend (fire and forget)
  http.post(`/acq/assets/${props.assetId}/reo-fc-duration-override/`, {
    reo_fc_duration_override_months: newOverride
  }).catch(error => {
    console.error('[REOSaleModelCard] Failed to update REO FC duration override:', error)
  })
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

  // WHAT: Update local state immediately for instant feedback
  const baseMonths = timelineData.reo_renovation_months_base || 0
  timelineData.reo_renovation_override_months = newOverride
  timelineData.reo_renovation_months = baseMonths + newOverride
  
  // WHAT: Update total timeline (servicing + foreclosure + renovation + marketing)
  const servicingMonths = timelineData.servicing_transfer_months || 0
  const foreclosureMonths = timelineData.foreclosure_months || 0
  const marketingMonths = timelineData.reo_marketing_months || 0
  timelineData.total_timeline_months = servicingMonths + foreclosureMonths + timelineData.reo_renovation_months + marketingMonths

  // WHAT: Recalculate carry costs with new renovation duration
  // WHY: Update taxes, insurance, servicing fees, and REO holding costs instantly
  // NOTE: REO holding costs ARE affected by renovation duration (renovation + marketing = total REO time)
  recalculateCarryCosts()  // Do NOT skip REO holding cost recalculation

  // WHAT: Save to backend (fire and forget)
  http.post(`/acq/assets/${props.assetId}/reo-renovation-override/`, {
    reo_renovation_override_months: newOverride
  }).catch(error => {
    console.error('[REOSaleModelCard] Failed to update REO renovation duration override:', error)
  })
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

  // WHAT: Update local state immediately for instant feedback
  const baseMonths = timelineData.reo_marketing_months_base || 0
  timelineData.reo_marketing_override_months = newOverride
  timelineData.reo_marketing_months = baseMonths + newOverride
  
  // WHAT: Update total timeline (servicing + foreclosure + renovation + marketing)
  const servicingMonths = timelineData.servicing_transfer_months || 0
  const foreclosureMonths = timelineData.foreclosure_months || 0
  const renovationMonths = timelineData.reo_renovation_months || 0
  timelineData.total_timeline_months = servicingMonths + foreclosureMonths + renovationMonths + timelineData.reo_marketing_months

  // WHAT: Recalculate carry costs with new marketing duration
  // WHY: Update taxes, insurance, servicing fees, and REO holding costs instantly
  // NOTE: REO holding costs ARE affected by marketing duration (renovation + marketing = total REO time)
  recalculateCarryCosts()  // Do NOT skip REO holding cost recalculation

  // WHAT: Save to backend (fire and forget)
  http.post(`/acq/assets/${props.assetId}/reo-marketing-override/`, {
    reo_marketing_override_months: newOverride
  }).catch(error => {
    console.error('[REOSaleModelCard] Failed to update REO marketing duration override:', error)
  })
}

// WHAT: Computed property to check if any timeline overrides exist
// WHY: Show reset button only when overrides are present
const hasTimelineOverrides = computed(() => {
  return (
    (timelineData.reo_fc_duration_override_months != null && timelineData.reo_fc_duration_override_months !== 0) ||
    (timelineData.reo_renovation_override_months != null && timelineData.reo_renovation_override_months !== 0) ||
    (timelineData.reo_marketing_override_months != null && timelineData.reo_marketing_override_months !== 0)
  )
})

// WHAT: Function to reset all timeline overrides to default (0)
// WHY: Allow users to quickly revert all manual timeline adjustments
async function resetTimelineOverrides() {
  if (!props.assetId) {
    console.warn('[REOSaleModelCard] No assetId provided, cannot reset timeline overrides')
    return
  }

  loadingTimelines.value = true

  try {
    // WHAT: Reset all override values to 0
    timelineData.reo_fc_duration_override_months = 0
    timelineData.reo_renovation_override_months = 0
    timelineData.reo_marketing_override_months = 0

    // WHAT: Recalculate actual months from base values
    const fcBaseMonths = timelineData.foreclosure_months_base || 0
    const renovationBaseMonths = timelineData.reo_renovation_months_base || 0
    const marketingBaseMonths = timelineData.reo_marketing_months_base || 0

    timelineData.foreclosure_months = fcBaseMonths
    timelineData.reo_renovation_months = renovationBaseMonths
    timelineData.reo_marketing_months = marketingBaseMonths

    // WHAT: Update total timeline (servicing + foreclosure + renovation + marketing)
    const servicingMonths = timelineData.servicing_transfer_months || 0
    timelineData.total_timeline_months = servicingMonths + fcBaseMonths + renovationBaseMonths + marketingBaseMonths

    // WHAT: Recalculate carry costs with reset durations
    recalculateCarryCosts()

    // WHAT: Save all resets to backend
    await Promise.all([
      http.post(`/acq/assets/${props.assetId}/reo-fc-duration-override/`, {
        reo_fc_duration_override_months: 0
      }),
      http.post(`/acq/assets/${props.assetId}/reo-renovation-override/`, {
        reo_renovation_override_months: 0
      }),
      http.post(`/acq/assets/${props.assetId}/reo-marketing-override/`, {
        reo_marketing_override_months: 0
      })
    ])
  } catch (error) {
    console.error('[REOSaleModelCard] Failed to reset timeline overrides:', error)
    // WHAT: Reload timeline data on error to restore correct state
    await fetchTimelineData()
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
// NOTE: Display formatting rounds to whole dollars for UI cleanliness
// WHY: Easier to read large numbers without cents (e.g., $37,800 vs $37,800.46)
// IMPORTANT: Underlying calculations maintain penny precision ($37,800.46 exactly)
// HOW: formatCurrency rounds for display only, all computed properties use exact values
const formatCurrency = (value: number | null | undefined): string => {
  if (value == null || isNaN(value)) return '$0'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,  // Display: no cents (rounds to nearest dollar)
    maximumFractionDigits: 0,  // Display: no cents
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
// WHY: immediate: true handles both initial load and subsequent changes, no need for onMounted
watch(() => props.assetId, (newAssetId) => {
  if (newAssetId) {
    fetchTimelineData()
  }
}, { immediate: true })
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

.timeline-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.timeline-label {
  min-width: 140px;
}

.timeline-value-group {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  min-width: 150px;
}

.timeline-override-badge {
  min-width: 34px;
  height: 22px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  font-size: 0.7rem;
  padding: 0;
  border-radius: 0.35rem;
  line-height: 1;
}

.timeline-override-badge.is-empty {
  visibility: hidden;
}

.timeline-controls-placeholder {
  width: 64px;
  height: 30px;
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

/* WHAT: Fixed width for timeline months values to keep +/- buttons aligned */
.timeline-months-value {
  min-width: 90px;
  display: inline-block;
  text-align: left;
}
</style>

