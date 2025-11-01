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
            <span class="badge bg-primary ms-2">{{ fcProbability }}% Probability</span>
          </h5>
        <div class="d-flex gap-2">
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
      <!-- Timelines and Expenses Section -->
      <div class="mb-4">
        <div class="row g-3">
          <!-- Timelines Column -->
          <div class="col-md-6">
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
          
          <!-- Divider line -->
          <hr class="my-2" style="opacity: 0.4; border-width: 2px;" />
          
          <!-- Total Duration -->
          <div class="d-flex align-items-baseline gap-2">
            <small class="text-muted d-block fw-semibold" style="min-width: 140px;">Total Duration:</small>
            <span class="fw-bold text-dark">
              {{ timelineData.total_timeline_months != null ? timelineData.total_timeline_months : '—' }} months
            </span>
          </div>
            </div>
          </div>
          
          <!-- Expenses Column -->
          <div class="col-md-6">
            <h6 class="fw-semibold text-body mb-2">
              <i class="mdi mdi-cash-multiple me-2 text-warning"></i>
              Expenses
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
              
              <!-- Divider line -->
              <hr class="my-2" style="opacity: 0.4; border-width: 2px;" />
              
              <!-- FC Sale Probability -->
              <div class="d-flex align-items-baseline gap-2">
                <small class="text-muted d-block fw-semibold" style="min-width: 140px;">FC Sale Probability:</small>
                <div class="input-group input-group-sm" style="max-width: 120px;">
                  <input
                    v-model.number="fcProbability"
                    type="number"
                    class="form-control text-end"
                    min="0"
                    max="100"
                    step="1"
                    placeholder="0"
                    @input="handleProbabilityChange"
                  />
                  <span class="input-group-text">%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Financial Summary Section -->
      <div class="border-top pt-3">
        <h6 class="fw-semibold text-body mb-3">
          <i class="fas fa-calculator me-2 text-secondary"></i>
          Financial Summary
        </h6>
        <!-- Row 1: Acquisition Price Input -->
        <div class="row g-3 mb-2">
          <div class="col-md-12">
            <div class="text-center p-2 bg-light rounded">
              <small class="text-muted d-block mb-1">Acquisition Price</small>
              <div class="input-group input-group-sm" style="max-width: 180px; margin: 0 auto;">
                <span class="input-group-text">$</span>
                <input
                  type="number"
                  class="form-control text-end fw-bold"
                  v-model.number="acquisitionPrice"
                  @blur="saveAcquisitionPrice"
                  @keyup.enter="saveAcquisitionPrice"
                  step="1000"
                  min="0"
                  placeholder="0"
                />
              </div>
            </div>
          </div>
        </div>
        
        <!-- Row 2: Summary Metrics -->
        <div class="row g-3">
          <div class="col-md-4">
            <div class="text-center p-2 bg-light rounded">
              <small class="text-muted d-block">Total Costs</small>
              <span class="fw-bold text-danger">{{ formatCurrency(calculatedTotalCosts) }}</span>
            </div>
          </div>
          <div class="col-md-4">
            <div class="text-center p-2 bg-light rounded">
              <small class="text-muted d-block">Expected Recovery</small>
              <span class="fw-bold text-success">{{ formatCurrency(timelineData.expected_recovery || 0) }}</span>
            </div>
          </div>
          <div class="col-md-4">
            <div class="text-center p-2 bg-light rounded">
              <small class="text-muted d-block">Net Position</small>
              <span class="fw-bold" :class="calculatedNetRecovery >= 0 ? 'text-success' : 'text-danger'">
                {{ formatCurrency(calculatedNetRecovery) }}
              </span>
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
}>()

// WHAT: Emits for parent component communication
const emit = defineEmits<{
  assumptionsChanged: [assumptions: FcAssumptions]
  probabilityChanged: [probability: number]
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
  // WHAT: Expense values from backend models
  servicing_fees: number | null
  taxes: number | null
  insurance: number | null
  legal_cost: number | null
}>({
  servicing_transfer_months: null,
  foreclosure_days: null,
  foreclosure_months: null,
  foreclosure_months_base: null,
  fc_duration_override_months: null,
  total_timeline_months: null,
  expected_recovery: null,
  acquisition_price: null,
  servicing_fees: null,
  taxes: null,
  insurance: null,
  legal_cost: null
})

// WHAT: Loading state for timeline data
const loadingTimelines = ref(false)

// WHAT: Editable acquisition price
// WHY: Allow user to input/override acquisition price
const acquisitionPrice = ref<number>(0)

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

// WHAT: Computed property to calculate total costs (sum of all expenses)
const calculatedTotalCosts = computed(() => {
  return (expenses.servicingFees || 0) + 
         (expenses.taxes || 0) + 
         (expenses.insurance || 0) + 
         (expenses.legalCost || 0)
})

// WHAT: Computed property to calculate net recovery amount
const calculatedNetRecovery = computed(() => {
  return (timelineData.expected_recovery || 0) - calculatedTotalCosts.value
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
</style>
