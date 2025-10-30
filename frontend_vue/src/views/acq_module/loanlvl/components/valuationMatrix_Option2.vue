<template>
  <!-- Valuation Matrix Option 2: Comparison Grid -->
  <div class="card">
    <!-- Card Header -->
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Valuation Summary</h4>
      <div v-if="saving" class="text-muted small">
        <i class="mdi mdi-reload mdi-spin me-1"></i>Saving…
      </div>
    </div>

    <!-- Card Body -->
    <div class="card-body pt-0">
      <div class="table-responsive">
        <table class="table table-centered table-hover mb-0">
          <thead class="table-light">
            <tr>
              <th>Source</th>
              <th>As-Is Value</th>
              <th>After Repair Value</th>
              <th>Rehab Estimate</th>
            </tr>
          </thead>
          <tbody>
            <!-- Internal Reconciled Row (Editable) -->
            <tr class="table-active">
              <td>
                <span class="badge bg-primary-subtle text-primary">
                  <i class="mdi mdi-pencil me-1"></i>Internal Reconciled
                </span>
              </td>
              <td>
                <b-form-input
                  v-model="internalAsIs"
                  v-currency
                  @update:modelValue="onCurrencyModel('asIs', $event)"
                  type="text"
                  inputmode="numeric"
                  pattern="[0-9,]*"
                  size="sm"
                  :disabled="!sellerId || saving"
                  @blur="onAsIsBlur"
                  placeholder="Enter value"
                  style="max-width: 180px;"
                />
                <small v-if="asIsTouched && internalAsIs !== '' && !isWholeNumberDisplay(internalAsIs)" class="text-danger d-block mt-1">
                  Whole number only
                </small>
              </td>
              <td>
                <b-form-input
                  v-model="internalArv"
                  v-currency
                  @update:modelValue="onCurrencyModel('arv', $event)"
                  type="text"
                  inputmode="numeric"
                  pattern="[0-9,]*"
                  size="sm"
                  :disabled="!sellerId || saving"
                  @blur="onArvBlur"
                  placeholder="Enter value"
                  style="max-width: 180px;"
                />
                <small v-if="arvTouched && internalArv !== '' && !isWholeNumberDisplay(internalArv)" class="text-danger d-block mt-1">
                  Whole number only
                </small>
              </td>
              <td>
                <b-form-input
                  v-model="internalRehab"
                  v-currency
                  @update:modelValue="onCurrencyModel('rehab', $event)"
                  type="text"
                  inputmode="numeric"
                  pattern="[0-9,]*"
                  size="sm"
                  :disabled="!sellerId || saving"
                  @blur="onRehabBlur"
                  placeholder="Enter value"
                  style="max-width: 180px;"
                />
                <small v-if="rehabTouched && internalRehab !== '' && !isWholeNumberDisplay(internalRehab)" class="text-danger d-block mt-1">
                  Whole number only
                </small>
              </td>
            </tr>

            <!-- Supporting Reference Rows (Read-only) -->
            <tr v-for="(r, idx) in otherRows" :key="idx">
              <td>
                <span class="badge" :class="getSourceBadgeClass(r.source)">
                  {{ r.source }}
                </span>
              </td>
              <td class="fw-semibold">{{ formatDisplay(r.asIs) }}</td>
              <td class="fw-semibold">{{ formatDisplay(r.arv) }}</td>
              <td>{{ formatDisplay(r.rehab) }}</td>
            </tr>

            <!-- Empty State -->
            <tr v-if="otherRows.length === 0">
              <td colspan="4" class="text-center text-muted py-3">
                No supporting valuations available for this asset.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Valuation Matrix Option 2: Comparison Grid
 * 
 * Displays a clean grid layout with side-by-side comparison of all valuation sources.
 * Internal reconciled values are editable inputs, supporting values are read-only.
 * Uses color-coded badges for easy source identification.
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

// Use shared valuation logic composable
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

/**
 * Returns Bootstrap badge class based on valuation source type
 */
function getSourceBadgeClass(source: string): string {
  if (source.includes('Seller')) return 'bg-info-subtle text-info'
  if (source.includes('Agent')) return 'bg-purple-subtle text-purple'
  if (source.includes('BPO')) return 'bg-success-subtle text-success'
  return 'bg-secondary-subtle text-secondary'
}

/**
 * Formats display value, showing em dash for empty/null values
 */
function formatDisplay(value?: string): string {
  return value && value.trim() !== '' ? value : '—'
}
</script>

<style scoped>
/* Minimal scoped styles - rely on Hyper UI Bootstrap utilities */

/* Purple badge variant (not in Bootstrap by default) */
.bg-purple-subtle {
  background-color: #f3e5f5 !important;
}

.text-purple {
  color: #6a1b9a !important;
}
</style>
