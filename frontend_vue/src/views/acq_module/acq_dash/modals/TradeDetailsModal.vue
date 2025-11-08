<template>
  <!--
    TradeDetailsModal (Trade Assumptions)
    - Presents editable fields for trade-level assumptions and settings
    - Designed to be placed inside a parent BModal
    - Uses v-model bindings for two-way sync with parent state
    - Organized into sections: Dates, Financial, Perf/RPL, Modifications, Acquisition Costs, AM Fees
  -->
  <div class="container-fluid">
    <!-- Trade Dates Section -->
    <div class="row mb-4">
      <div class="col-12">
        <h5 class="mb-3 text-primary border-bottom pb-2">
          <i class="mdi mdi-calendar-range me-2"></i>Trade Dates
        </h5>
      </div>

      <!-- Bid Date -->
      <div class="col-12 col-md-4 mb-3">
        <label for="tdm-bid-date" class="form-label fw-medium">Bid Date</label>
        <input
          id="tdm-bid-date"
          type="date"
          class="form-control"
          :disabled="disabled"
          :value="bidDateLocal"
          @input="onBidInput($event)"
          @change="emitChanged()"
        />
        <small class="form-text text-muted">Date when the bid will be submitted</small>
      </div>

      <!-- Settlement Date -->
      <div class="col-12 col-md-4 mb-3">
        <label for="tdm-settlement-date" class="form-label fw-medium">Settlement Date</label>
        <input
          id="tdm-settlement-date"
          type="date"
          class="form-control"
          :disabled="disabled"
          :value="settlementDateLocal"
          @input="onSettlementInput($event)"
          @change="emitChanged()"
        />
        <small class="form-text text-muted">Date when the transaction will settle</small>
      </div>

      <!-- Servicing Transfer Date -->
      <div class="col-12 col-md-4 mb-3">
        <label for="tdm-servicing-date" class="form-label fw-medium">Servicing Transfer Date</label>
        <input
          id="tdm-servicing-date"
          type="date"
          class="form-control"
          :disabled="disabled"
          :value="servicingTransferDateLocal"
          @input="onServicingTransferInput($event)"
          @change="emitChanged()"
        />
        <small class="form-text text-muted">Date servicing transfers to new servicer</small>
      </div>
    </div>

    <!-- Servicer Selection Section -->
    <div class="row mb-4">
      <div class="col-12">
        <h5 class="mb-3 text-primary border-bottom pb-2">
          <i class="mdi mdi-briefcase-account me-2"></i>Servicer
        </h5>
      </div>

      <!-- Servicer Dropdown -->
      <div class="col-12 col-md-6 mb-3">
        <label for="tdm-servicer" class="form-label fw-medium">Servicer</label>
        <select
          id="tdm-servicer"
          class="form-select"
          :disabled="disabled || servicersLoading"
          :value="servicerIdLocal"
          @change="onServicerInput($event)"
        >
          <option :value="null">Select a servicer...</option>
          <option v-for="servicer in servicers" :key="servicer.id" :value="servicer.id">
            {{ servicer.servicerName }}
          </option>
        </select>
        <small class="form-text text-muted">
          <span v-if="servicersLoading" class="text-info">
            <i class="mdi mdi-loading mdi-spin me-1"></i>Loading servicers...
          </span>
          <span v-else>Selected servicer for this trade</span>
        </small>
      </div>
    </div>

    <!-- Financial Assumptions Section -->
    <div class="row mb-4">
      <div class="col-12">
        <h5 class="mb-3 text-primary border-bottom pb-2">
          <i class="mdi mdi-finance me-2"></i>Financial Assumptions
        </h5>
      </div>

      <!-- Target IRR -->
      <div class="col-12 col-md-4 mb-3">
        <label for="tdm-target-irr" class="form-label fw-medium">Target IRR (%)</label>
        <input
          id="tdm-target-irr"
          type="number"
          step="0.01"
          class="form-control"
          :disabled="disabled"
          :value="targetIrrLocal"
          @input="onTargetIrrInput($event)"
          @change="emitChanged()"
        />
        <small class="form-text text-muted">Target internal rate of return</small>
      </div>

      <!-- Discount Rate -->
      <div class="col-12 col-md-4 mb-3">
        <label for="tdm-discount-rate" class="form-label fw-medium">Discount Rate (%)</label>
        <input
          id="tdm-discount-rate"
          type="number"
          step="0.01"
          class="form-control"
          :disabled="disabled"
          :value="discountRateLocal"
          @input="onDiscountRateInput($event)"
          @change="emitChanged()"
        />
        <small class="form-text text-muted">Discount rate for NPV calculations</small>
      </div>

      <!-- Perf/RPL Hold Period -->
      <div class="col-12 col-md-4 mb-3">
        <label for="tdm-perf-hold" class="form-label fw-medium">Perf/RPL Hold Period (months)</label>
        <input
          id="tdm-perf-hold"
          type="number"
          class="form-control"
          :disabled="disabled"
          :value="perfRplHoldPeriodLocal"
          @input="onPerfRplHoldPeriodInput($event)"
          @change="emitChanged()"
        />
        <small class="form-text text-muted">Hold period for performing/re-performing loans</small>
      </div>
    </div>

    <!-- Modification Assumptions Section -->
    <div class="row mb-4">
      <div class="col-12">
        <h5 class="mb-3 text-primary border-bottom pb-2">
          <i class="mdi mdi-file-edit-outline me-2"></i>Modification Assumptions
        </h5>
      </div>

      <!-- Mod Rate -->
      <div class="col-12 col-md-3 mb-3">
        <label for="tdm-mod-rate" class="form-label fw-medium">Mod Rate (%)</label>
        <input
          id="tdm-mod-rate"
          type="number"
          step="0.0001"
          class="form-control"
          :disabled="disabled"
          :value="modRateLocal"
          @input="onModRateInput($event)"
          @change="emitChanged()"
        />
        <small class="form-text text-muted">Modification interest rate</small>
      </div>

      <!-- Mod Legal Term -->
      <div class="col-12 col-md-3 mb-3">
        <label for="tdm-mod-legal-term" class="form-label fw-medium">Mod Legal Term (months)</label>
        <input
          id="tdm-mod-legal-term"
          type="number"
          class="form-control"
          :disabled="disabled"
          :value="modLegalTermLocal"
          @input="onModLegalTermInput($event)"
          @change="emitChanged()"
        />
        <small class="form-text text-muted">Modification legal term</small>
      </div>

      <!-- Mod Amort Term -->
      <div class="col-12 col-md-3 mb-3">
        <label for="tdm-mod-amort-term" class="form-label fw-medium">Mod Amort Term (months)</label>
        <input
          id="tdm-mod-amort-term"
          type="number"
          class="form-control"
          :disabled="disabled"
          :value="modAmortTermLocal"
          @input="onModAmortTermInput($event)"
          @change="emitChanged()"
        />
        <small class="form-text text-muted">Modification amortization term</small>
      </div>

      <!-- Max Mod LTV -->
      <div class="col-12 col-md-3 mb-3">
        <label for="tdm-max-mod-ltv" class="form-label fw-medium">Max Mod LTV (%)</label>
        <input
          id="tdm-max-mod-ltv"
          type="number"
          step="0.01"
          class="form-control"
          :disabled="disabled"
          :value="maxModLtvLocal"
          @input="onMaxModLtvInput($event)"
          @change="emitChanged()"
        />
        <small class="form-text text-muted">Maximum LTV for modifications</small>
      </div>

      <!-- Mod IO Flag -->
      <div class="col-12 col-md-3 mb-3">
        <label for="tdm-mod-io-flag" class="form-label fw-medium">Interest-Only Flag</label>
        <select
          id="tdm-mod-io-flag"
          class="form-select"
          :disabled="disabled"
          :value="modIoFlagLocal"
          @change="onModIoFlagInput($event)"
        >
          <option :value="false">No</option>
          <option :value="true">Yes</option>
        </select>
        <small class="form-text text-muted">IO flag for modifications</small>
      </div>

      <!-- Mod Down Payment -->
      <div class="col-12 col-md-3 mb-3">
        <label for="tdm-mod-down-pmt" class="form-label fw-medium">Mod Down Payment (%)</label>
        <input
          id="tdm-mod-down-pmt"
          type="number"
          step="0.01"
          class="form-control"
          :disabled="disabled"
          :value="modDownPmtLocal"
          @input="onModDownPmtInput($event)"
          @change="emitChanged()"
        />
        <small class="form-text text-muted">Modification down payment percentage</small>
      </div>

      <!-- Mod Origination Cost -->
      <div class="col-12 col-md-3 mb-3">
        <label for="tdm-mod-orig-cost" class="form-label fw-medium">Mod Orig Cost ($)</label>
        <input
          id="tdm-mod-orig-cost"
          type="number"
          step="0.01"
          min="0"
          class="form-control"
          :disabled="disabled"
          :value="modOrigCostLocal"
          @input="onModOrigCostInput($event)"
          @change="emitChanged()"
          placeholder="500.00"
        />
        <small class="form-text text-muted">Dollar amount per loan</small>
      </div>

      <!-- Mod Setup Duration -->
      <div class="col-12 col-md-3 mb-3">
        <label for="tdm-mod-setup-duration" class="form-label fw-medium">Mod Setup Duration (months)</label>
        <input
          id="tdm-mod-setup-duration"
          type="number"
          class="form-control"
          :disabled="disabled"
          :value="modSetupDurationLocal"
          @input="onModSetupDurationInput($event)"
          @change="emitChanged()"
        />
        <small class="form-text text-muted">Modification setup duration</small>
      </div>

      <!-- Mod Hold Duration -->
      <div class="col-12 col-md-3 mb-3">
        <label for="tdm-mod-hold-duration" class="form-label fw-medium">Mod Hold Duration (months)</label>
        <input
          id="tdm-mod-hold-duration"
          type="number"
          class="form-control"
          :disabled="disabled"
          :value="modHoldDurationLocal"
          @input="onModHoldDurationInput($event)"
          @change="emitChanged()"
        />
        <small class="form-text text-muted">Modification hold duration</small>
      </div>
    </div>

    <!-- Acquisition Costs Section -->
    <div class="row mb-4">
      <div class="col-12">
        <h5 class="mb-3 text-primary border-bottom pb-2">
          <i class="mdi mdi-cash-multiple me-2"></i>Acquisition Costs (per loan)
        </h5>
      </div>

      <!-- Acquisition Legal Cost -->
      <div class="col-12 col-md-4 mb-3">
        <label for="tdm-acq-legal-cost" class="form-label fw-medium">Legal Cost ($)</label>
        <input
          id="tdm-acq-legal-cost"
          type="number"
          step="0.01"
          min="0"
          class="form-control"
          :disabled="disabled"
          :value="acqLegalCostLocal"
          @input="onAcqLegalCostInput($event)"
          @change="emitChanged()"
          placeholder="300.00"
        />
        <small class="form-text text-muted">Dollar amount per loan</small>
      </div>

      <!-- Acquisition DD Cost -->
      <div class="col-12 col-md-4 mb-3">
        <label for="tdm-acq-dd-cost" class="form-label fw-medium">Due Diligence Cost ($)</label>
        <input
          id="tdm-acq-dd-cost"
          type="number"
          step="0.01"
          min="0"
          class="form-control"
          :disabled="disabled"
          :value="acqDdCostLocal"
          @input="onAcqDdCostInput($event)"
          @change="emitChanged()"
          placeholder="150.00"
        />
        <small class="form-text text-muted">Dollar amount per loan</small>
      </div>

      <!-- Acquisition Tax/Title Cost -->
      <div class="col-12 col-md-4 mb-3">
        <label for="tdm-acq-tax-title-cost" class="form-label fw-medium">Tax/Title Cost ($)</label>
        <input
          id="tdm-acq-tax-title-cost"
          type="number"
          step="0.01"
          min="0"
          class="form-control"
          :disabled="disabled"
          :value="acqTaxTitleCostLocal"
          @input="onAcqTaxTitleCostInput($event)"
          @change="emitChanged()"
          placeholder="100.00"
        />
        <small class="form-text text-muted">Dollar amount per loan</small>
      </div>
    </div>

    <!-- Asset Management Fees Section -->
    <div class="row mb-2">
      <div class="col-12">
        <h5 class="mb-3 text-primary border-bottom pb-2">
          <i class="mdi mdi-briefcase-outline me-2"></i>Asset Management Fees
        </h5>
      </div>

      <!-- AM Fee Percentage -->
      <div class="col-12 col-md-4 mb-3">
        <label for="tdm-am-fee-pct" class="form-label fw-medium">AM Fee</label>
        <div class="input-group">
          <input
            id="tdm-am-fee-pct"
            type="number"
            step="0.01"
            min="0"
            class="form-control"
            :disabled="disabled"
            :value="amFeePctLocal"
            @input="onAmFeePctInput($event)"
            @change="emitChanged()"
            placeholder="1.00"
          />
          <span class="input-group-text">%</span>
        </div>
        <small class="form-text text-muted">Enter as percentage (e.g., 1.00 for 1%)</small>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// ----------------------------------------------------------------------------------
// TradeDetailsModal.vue (Trade Assumptions)
// ----------------------------------------------------------------------------------
// Comprehensive trade-level assumptions form with v-model bindings for all fields.
// The parent controls persistence. We emit updates and a generic "changed" signal
// on field change so the parent can auto-save.
// ----------------------------------------------------------------------------------
import { computed } from 'vue'

// Servicer interface for dropdown options
// WHAT: Export this interface to prevent Vue type inference issues
// WHY: Vue Volar type checker needs explicit exports for component prop types
export interface Servicer {
  id: number
  servicerName: string
}

// Props definition with v-model aliases for all trade assumption fields
const props = defineProps<{
  // Trade Dates
  /** ISO date string: YYYY-MM-DD */
  bidDate?: string
  /** ISO date string: YYYY-MM-DD */
  settlementDate?: string
  /** ISO date string: YYYY-MM-DD */
  servicingTransferDate?: string
  
  // Servicer Selection
  /** Selected servicer ID */
  servicerId?: number | null
  /** List of available servicers for dropdown */
  servicers?: Servicer[]
  /** Loading state for servicers */
  servicersLoading?: boolean
  
  // Financial Assumptions
  /** Target IRR as decimal (e.g., 0.15 for 15%) */
  targetIrr?: number | string
  /** Discount rate as decimal (e.g., 0.12 for 12%) */
  discountRate?: number | string
  /** Perf/RPL hold period in months */
  perfRplHoldPeriod?: number | string
  
  // Modification Assumptions
  /** Modification rate as decimal (e.g., 0.04 for 4%) */
  modRate?: number | string
  /** Modification legal term in months */
  modLegalTerm?: number | string
  /** Modification amortization term in months */
  modAmortTerm?: number | string
  /** Maximum modification LTV as decimal (e.g., 0.95 for 95%) */
  maxModLtv?: number | string
  /** Interest-only flag for modifications */
  modIoFlag?: boolean
  /** Modification down payment as decimal (e.g., 0.05 for 5%) */
  modDownPmt?: number | string
  /** Modification origination cost in dollars per loan */
  modOrigCost?: number | string
  /** Modification setup duration in months */
  modSetupDuration?: number | string
  /** Modification hold duration in months */
  modHoldDuration?: number | string
  
  // Acquisition Costs (dollar amounts per loan)
  /** Acquisition legal cost in dollars per loan */
  acqLegalCost?: number | string
  /** Acquisition DD cost in dollars per loan */
  acqDdCost?: number | string
  /** Acquisition tax/title cost in dollars per loan */
  acqTaxTitleCost?: number | string
  
  // Asset Management Fees (stored as decimal but displayed as percentage)
  /** AM fee stored as decimal (e.g., 0.01) but displayed as percentage (e.g., 1) */
  amFeePct?: number | string
  
  /** Disable inputs while saving */
  disabled?: boolean
}>()

// Emits: two-way model updates for all fields and a generic changed event
const emit = defineEmits<{
  // Trade Dates
  (e: 'update:bidDate', value: string): void
  (e: 'update:settlementDate', value: string): void
  (e: 'update:servicingTransferDate', value: string): void
  
  // Servicer Selection
  (e: 'update:servicerId', value: number | null): void
  
  // Financial Assumptions
  (e: 'update:targetIrr', value: number | string): void
  (e: 'update:discountRate', value: number | string): void
  (e: 'update:perfRplHoldPeriod', value: number | string): void
  
  // Modification Assumptions
  (e: 'update:modRate', value: number | string): void
  (e: 'update:modLegalTerm', value: number | string): void
  (e: 'update:modAmortTerm', value: number | string): void
  (e: 'update:maxModLtv', value: number | string): void
  (e: 'update:modIoFlag', value: boolean): void
  (e: 'update:modDownPmt', value: number | string): void
  (e: 'update:modOrigCost', value: number | string): void
  (e: 'update:modSetupDuration', value: number | string): void
  (e: 'update:modHoldDuration', value: number | string): void
  
  // Acquisition Costs
  (e: 'update:acqLegalCost', value: number | string): void
  (e: 'update:acqDdCost', value: number | string): void
  (e: 'update:acqTaxTitleCost', value: number | string): void
  
  // Asset Management Fees
  (e: 'update:amFeePct', value: number | string): void
  
  /** Generic change signal so parent can auto-save */
  (e: 'changed'): void
}>()

// Local computed wrappers for all fields to handle empty/null values safely
const bidDateLocal = computed(() => props.bidDate ?? '')
const settlementDateLocal = computed(() => props.settlementDate ?? '')
const servicingTransferDateLocal = computed(() => props.servicingTransferDate ?? '')

// WHAT: Servicer selection local wrapper
// WHY: Handle null/undefined servicer ID safely
const servicerIdLocal = computed(() => props.servicerId ?? null)

const targetIrrLocal = computed(() => props.targetIrr ?? '')
const discountRateLocal = computed(() => props.discountRate ?? '')
const perfRplHoldPeriodLocal = computed(() => props.perfRplHoldPeriod ?? '')

const modRateLocal = computed(() => props.modRate ?? '')
const modLegalTermLocal = computed(() => props.modLegalTerm ?? '')
const modAmortTermLocal = computed(() => props.modAmortTerm ?? '')
const maxModLtvLocal = computed(() => props.maxModLtv ?? '')
const modIoFlagLocal = computed(() => props.modIoFlag ?? false)
const modDownPmtLocal = computed(() => props.modDownPmt ?? '')
const modOrigCostLocal = computed(() => props.modOrigCost ?? '')
const modSetupDurationLocal = computed(() => props.modSetupDuration ?? '')
const modHoldDurationLocal = computed(() => props.modHoldDuration ?? '')

const acqLegalCostLocal = computed(() => props.acqLegalCost ?? '')
const acqDdCostLocal = computed(() => props.acqDdCost ?? '')
const acqTaxTitleCostLocal = computed(() => props.acqTaxTitleCost ?? '')

// WHAT: Convert AM Fee from decimal to percentage for display
// WHY: User expects to see and enter percentages (e.g., 1%) not decimals (e.g., 0.01)
// HOW: Multiply decimal by 100 to get percentage; return empty string if no value
const amFeePctLocal = computed(() => {
  if (props.amFeePct === null || props.amFeePct === undefined || props.amFeePct === '') {
    return ''
  }
  // WHAT: Convert decimal to percentage (0.01 -> 1)
  const numValue = typeof props.amFeePct === 'string' ? parseFloat(props.amFeePct) : props.amFeePct
  if (isNaN(numValue)) {
    return ''
  }
  return numValue * 100
})

// Input handlers - Trade Dates
function onBidInput(ev: Event) {
  const v = (ev.target as HTMLInputElement)?.value ?? ''
  emit('update:bidDate', v)
}

function onSettlementInput(ev: Event) {
  const v = (ev.target as HTMLInputElement)?.value ?? ''
  emit('update:settlementDate', v)
}

function onServicingTransferInput(ev: Event) {
  const v = (ev.target as HTMLInputElement)?.value ?? ''
  emit('update:servicingTransferDate', v)
}

// Input handler - Servicer Selection
// WHAT: Handle servicer dropdown selection
// WHY: Update parent component with selected servicer ID
// HOW: Convert string value to number, emit null if empty
function onServicerInput(ev: Event) {
  const v = (ev.target as HTMLSelectElement)?.value ?? ''
  // WHAT: Convert to number or null
  // WHY: Backend expects number ID or null
  const servicerId = v === '' || v === 'null' ? null : parseInt(v, 10)
  emit('update:servicerId', servicerId)
  emitChanged()
}

// Input handlers - Financial Assumptions
function onTargetIrrInput(ev: Event) {
  const v = (ev.target as HTMLInputElement)?.value ?? ''
  emit('update:targetIrr', v)
}

function onDiscountRateInput(ev: Event) {
  const v = (ev.target as HTMLInputElement)?.value ?? ''
  emit('update:discountRate', v)
}

function onPerfRplHoldPeriodInput(ev: Event) {
  const v = (ev.target as HTMLInputElement)?.value ?? ''
  emit('update:perfRplHoldPeriod', v)
}

// Input handlers - Modification Assumptions
function onModRateInput(ev: Event) {
  const v = (ev.target as HTMLInputElement)?.value ?? ''
  emit('update:modRate', v)
}

function onModLegalTermInput(ev: Event) {
  const v = (ev.target as HTMLInputElement)?.value ?? ''
  emit('update:modLegalTerm', v)
}

function onModAmortTermInput(ev: Event) {
  const v = (ev.target as HTMLInputElement)?.value ?? ''
  emit('update:modAmortTerm', v)
}

function onMaxModLtvInput(ev: Event) {
  const v = (ev.target as HTMLInputElement)?.value ?? ''
  emit('update:maxModLtv', v)
}

function onModIoFlagInput(ev: Event) {
  const v = (ev.target as HTMLSelectElement)?.value ?? 'false'
  emit('update:modIoFlag', v === 'true')
  emitChanged()
}

function onModDownPmtInput(ev: Event) {
  const v = (ev.target as HTMLInputElement)?.value ?? ''
  emit('update:modDownPmt', v)
}

function onModOrigCostInput(ev: Event) {
  const v = (ev.target as HTMLInputElement)?.value ?? ''
  emit('update:modOrigCost', v)
}

function onModSetupDurationInput(ev: Event) {
  const v = (ev.target as HTMLInputElement)?.value ?? ''
  emit('update:modSetupDuration', v)
}

function onModHoldDurationInput(ev: Event) {
  const v = (ev.target as HTMLInputElement)?.value ?? ''
  emit('update:modHoldDuration', v)
}

// Input handlers - Acquisition Costs
function onAcqLegalCostInput(ev: Event) {
  const v = (ev.target as HTMLInputElement)?.value ?? ''
  emit('update:acqLegalCost', v)
}

function onAcqDdCostInput(ev: Event) {
  const v = (ev.target as HTMLInputElement)?.value ?? ''
  emit('update:acqDdCost', v)
}

function onAcqTaxTitleCostInput(ev: Event) {
  const v = (ev.target as HTMLInputElement)?.value ?? ''
  emit('update:acqTaxTitleCost', v)
}

// Input handlers - Asset Management Fees
// WHAT: Handle AM Fee input and convert from percentage to decimal
// WHY: User enters percentage (1) but backend expects decimal (0.01)
// HOW: Divide input by 100 to convert percentage to decimal
function onAmFeePctInput(ev: Event) {
  const v = (ev.target as HTMLInputElement)?.value ?? ''
  
  // WHAT: If empty, emit empty string
  if (v === '' || v === null || v === undefined) {
    emit('update:amFeePct', '')
    return
  }
  
  // WHAT: Convert percentage to decimal (1 -> 0.01)
  const percentageValue = parseFloat(v)
  if (isNaN(percentageValue)) {
    emit('update:amFeePct', '')
    return
  }
  
  // WHAT: Divide by 100 to convert percentage to decimal
  const decimalValue = percentageValue / 100
  emit('update:amFeePct', decimalValue)
}

// Generic change signal emitter
function emitChanged() {
  // Parent may auto-save on this signal
  emit('changed')
}
</script>

<style scoped>
/* Keep styling minimal; rely on Bootstrap/Hyper UI utilities */
</style>
