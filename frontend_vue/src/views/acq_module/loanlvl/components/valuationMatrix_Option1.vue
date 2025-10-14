<template>
  <!--
    Valuation Matrix Option 1: Card-Based Layout
    Each valuation source gets its own card with visual hierarchy
    Reconciled values are prominently displayed at the top
    Component path: frontend_vue/src/views/acq_module/loanlvl/components/valuationMatrix_Option1.vue
  -->
  <div class="valuation-option-1">
    <!-- Header with title and description -->
    <div class="mb-3">
      <h5 class="mb-1">Option 1: Card-Based Layout</h5>
      <p class="text-muted small mb-0">Each source in its own card with clear visual separation</p>
    </div>

    <!-- Reconciled Values Section (Editable) - Prominent at top -->
    <div class="card border-primary mb-3">
      <div class="card-header bg-primary text-white d-flex align-items-center">
        <i class="mdi mdi-pencil me-2"></i>
        <strong>Internal Reconciled Values</strong>
        <span class="ms-auto badge bg-light text-primary">Editable</span>
      </div>
      <div class="card-body">
        <div class="row g-3">
          <!-- As-Is Value -->
          <div class="col-md-4">
            <label class="form-label small fw-bold mb-1">As-Is Value</label>
            <b-form-input
              v-model="internalAsIs"
              v-currency
              @update:modelValue="onCurrencyModel('asIs', $event)"
              type="text"
              inputmode="numeric"
              pattern="[0-9,]*"
              size="lg"
              class="text-start fw-bold"
              :disabled="!sellerId || saving"
              @blur="onAsIsBlur"
              placeholder="Enter value"
            />
            <small v-if="asIsTouched && internalAsIs !== '' && !isWholeNumberDisplay(internalAsIs)" class="text-danger">Enter a whole number</small>
          </div>
          <!-- ARV -->
          <div class="col-md-4">
            <label class="form-label small fw-bold mb-1">After Repair Value</label>
            <b-form-input
              v-model="internalArv"
              v-currency
              @update:modelValue="onCurrencyModel('arv', $event)"
              type="text"
              inputmode="numeric"
              pattern="[0-9,]*"
              size="lg"
              class="text-start fw-bold"
              :disabled="!sellerId || saving"
              @blur="onArvBlur"
              placeholder="Enter value"
            />
            <small v-if="arvTouched && internalArv !== '' && !isWholeNumberDisplay(internalArv)" class="text-danger">Enter a whole number</small>
          </div>
          <!-- Rehab -->
          <div class="col-md-4">
            <label class="form-label small fw-bold mb-1">Rehab Estimate</label>
            <b-form-input
              v-model="internalRehab"
              v-currency
              @update:modelValue="onCurrencyModel('rehab', $event)"
              type="text"
              inputmode="numeric"
              pattern="[0-9,]*"
              size="lg"
              class="text-start fw-bold"
              :disabled="!sellerId || saving"
              @blur="onRehabBlur"
              placeholder="Enter value"
            />
            <small v-if="rehabTouched && internalRehab !== '' && !isWholeNumberDisplay(internalRehab)" class="text-danger">Enter a whole number</small>
          </div>
        </div>
      </div>
    </div>

    <!-- Reference Values Section (Read-only) -->
    <div class="row g-3">
      <!-- Seller Values Card -->
      <div class="col-md-4" v-if="sellerRow">
        <div class="card h-100 border-secondary">
          <div class="card-header bg-light">
            <strong class="small">{{ sellerRow.source }}</strong>
          </div>
          <div class="card-body">
            <div class="mb-2">
              <div class="text-muted small">As-Is</div>
              <div class="fs-5">{{ sellerRow.asIs || '—' }}</div>
            </div>
            <div class="mb-2">
              <div class="text-muted small">ARV</div>
              <div class="fs-5">{{ sellerRow.arv || '—' }}</div>
            </div>
            <div>
              <div class="text-muted small">Rehab</div>
              <div class="fs-5">{{ sellerRow.rehab || '—' }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Local Agent Card -->
      <div class="col-md-4" v-if="agentRow">
        <div class="card h-100 border-secondary">
          <div class="card-header bg-light">
            <strong class="small">{{ agentRow.source }}</strong>
          </div>
          <div class="card-body">
            <div class="mb-2">
              <div class="text-muted small">As-Is</div>
              <div class="fs-5">{{ agentRow.asIs || '—' }}</div>
            </div>
            <div class="mb-2">
              <div class="text-muted small">ARV</div>
              <div class="fs-5">{{ agentRow.arv || '—' }}</div>
            </div>
            <div>
              <div class="text-muted small">Rehab</div>
              <div class="fs-5">{{ agentRow.rehab || '—' }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 3rd Party BPO Card -->
      <div class="col-md-4" v-if="bpoRow">
        <div class="card h-100 border-secondary">
          <div class="card-header bg-light">
            <strong class="small">{{ bpoRow.source }}</strong>
          </div>
          <div class="card-body">
            <div class="mb-2">
              <div class="text-muted small">As-Is</div>
              <div class="fs-5">{{ bpoRow.asIs || '—' }}</div>
            </div>
            <div class="mb-2">
              <div class="text-muted small">ARV</div>
              <div class="fs-5">{{ bpoRow.arv || '—' }}</div>
            </div>
            <div>
              <div class="text-muted small">Rehab</div>
              <div class="fs-5">{{ bpoRow.rehab || '—' }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Valuation Matrix Option 1: Card-Based Layout
 * Each valuation source displayed in its own card for clear visual separation
 * Reconciled values prominently displayed at top with editable inputs
 */
import { computed, withDefaults } from 'vue'
import { useValuationLogic } from './valuationLogic'

// Props definition
const props = withDefaults(defineProps<{
  rows?: any[]
  row?: Record<string, any> | null
  assetId?: string | number | null
}>(), {
  row: null,
  assetId: null,
})

// Use shared valuation logic
const {
  internalAsIs,
  internalArv,
  internalRehab,
  asIsTouched,
  arvTouched,
  rehabTouched,
  saving,
  sellerId,
  otherRows,
  onCurrencyModel,
  onAsIsBlur,
  onArvBlur,
  onRehabBlur,
  isWholeNumberDisplay,
} = useValuationLogic(props)

// Extract individual rows for card display
const sellerRow = computed(() => otherRows.value.find((r: any) => r.source === 'Seller Values'))
const agentRow = computed(() => otherRows.value.find((r: any) => r.source === 'Local Agent'))
const bpoRow = computed(() => otherRows.value.find((r: any) => r.source === '3rd Party BPO'))
</script>

<style scoped>
.valuation-option-1 .card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.valuation-option-1 .card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
</style>
