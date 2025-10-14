<template>
  <!--
    Valuation Matrix Option 2: Comparison Grid
    Side-by-side comparison with visual indicators for differences
    Clean, modern grid layout with color-coded sources
    Component path: frontend_vue/src/views/acq_module/loanlvl/components/valuationMatrix_Option2.vue
  -->
  <div class="valuation-option-2">
    <div class="card">
      <div class="card-body p-0">
        <!-- Grid Header -->
        <div class="comparison-header">
          <div class="source-col header-cell">Source</div>
          <div class="value-col header-cell">As-Is Value</div>
          <div class="value-col header-cell">After Repair Value</div>
          <div class="value-col header-cell">Rehab Estimate</div>
        </div>

        <!-- Internal Reconciled Row (Editable) -->
        <div class="comparison-row reconciled-row">
          <div class="source-col">
            <div class="d-flex align-items-center">
              <i class="mdi mdi-pencil text-primary me-2"></i>
              <strong>Internal Reconciled</strong>
            </div>
          </div>
          <div class="value-col">
            <b-form-input
              v-model="internalAsIs"
              v-currency
              @update:modelValue="onCurrencyModel('asIs', $event)"
              type="text"
              inputmode="numeric"
              pattern="[0-9,]*"
              size="sm"
              class="text-start"
              :disabled="!sellerId || saving"
              @blur="onAsIsBlur"
              placeholder="Enter"
            />
            <small v-if="asIsTouched && internalAsIs !== '' && !isWholeNumberDisplay(internalAsIs)" class="text-danger d-block mt-1">Whole number only</small>
          </div>
          <div class="value-col">
            <b-form-input
              v-model="internalArv"
              v-currency
              @update:modelValue="onCurrencyModel('arv', $event)"
              type="text"
              inputmode="numeric"
              pattern="[0-9,]*"
              size="sm"
              class="text-start"
              :disabled="!sellerId || saving"
              @blur="onArvBlur"
              placeholder="Enter"
            />
            <small v-if="arvTouched && internalArv !== '' && !isWholeNumberDisplay(internalArv)" class="text-danger d-block mt-1">Whole number only</small>
          </div>
          <div class="value-col">
            <b-form-input
              v-model="internalRehab"
              v-currency
              @update:modelValue="onCurrencyModel('rehab', $event)"
              type="text"
              inputmode="numeric"
              pattern="[0-9,]*"
              size="sm"
              class="text-start"
              :disabled="!sellerId || saving"
              @blur="onRehabBlur"
              placeholder="Enter"
            />
            <small v-if="rehabTouched && internalRehab !== '' && !isWholeNumberDisplay(internalRehab)" class="text-danger d-block mt-1">Whole number only</small>
          </div>
        </div>

        <!-- Divider -->
        <div class="divider"></div>

        <!-- Reference Rows (Read-only) -->
        <div v-for="(r, idx) in otherRows" :key="idx" class="comparison-row reference-row">
          <div class="source-col">
            <span class="source-badge" :class="getSourceBadgeClass(r.source)">
              {{ r.source }}
            </span>
          </div>
          <div class="value-col">
            <span class="value-display">{{ r.asIs || '—' }}</span>
          </div>
          <div class="value-col">
            <span class="value-display">{{ r.arv || '—' }}</span>
          </div>
          <div class="value-col">
            <span class="value-display">{{ r.rehab || '—' }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Valuation Matrix Option 2: Comparison Grid
 * Clean grid layout with side-by-side comparison of all sources
 * Color-coded badges for easy source identification
 */
import { withDefaults } from 'vue'
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

// Helper to assign color classes to source badges
function getSourceBadgeClass(source: string): string {
  if (source.includes('Seller')) return 'badge-seller'
  if (source.includes('Agent')) return 'badge-agent'
  if (source.includes('BPO')) return 'badge-bpo'
  return 'badge-default'
}
</script>

<style scoped>
.valuation-option-2 {
  font-size: 0.95rem;
}

.comparison-header {
  display: grid;
  grid-template-columns: 2fr 1.5fr 1.5fr 1.5fr;
  gap: 1rem;
  padding: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: 600;
  border-radius: 0.25rem 0.25rem 0 0;
}

.comparison-row {
  display: grid;
  grid-template-columns: 2fr 1.5fr 1.5fr 1.5fr;
  gap: 1rem;
  padding: 1rem;
  align-items: center;
  border-bottom: 1px solid #e9ecef;
}

.comparison-row:last-child {
  border-bottom: none;
}

.reconciled-row {
  background: #fafbfc;
  border-left: 4px solid #667eea;
}

.reference-row:hover {
  background: #f8f9fa;
}

.header-cell {
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.source-col {
  display: flex;
  align-items: center;
}

.value-col {
  display: flex;
  flex-direction: column;
}

.value-display {
  font-size: 1.1rem;
  font-weight: 500;
  color: #495057;
}

.source-badge {
  padding: 0.35rem 0.75rem;
  border-radius: 0.25rem;
  font-size: 0.85rem;
  font-weight: 500;
}

.badge-seller {
  background: #e8eaf6;
  color: #3f51b5;
}

.badge-agent {
  background: #f3e5f5;
  color: #8e24aa;
}

.badge-bpo {
  background: #e0f2f1;
  color: #00897b;
}

.badge-default {
  background: #eceff1;
  color: #546e7a;
}

.divider {
  height: 2px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  margin: 0;
}

@media (max-width: 768px) {
  .comparison-header,
  .comparison-row {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }
  
  .header-cell {
    display: none;
  }
  
  .value-col::before {
    content: attr(data-label);
    font-weight: 600;
    margin-bottom: 0.25rem;
  }
}
</style>
