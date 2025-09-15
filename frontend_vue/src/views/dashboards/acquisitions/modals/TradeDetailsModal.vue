<template>
  <!--
    TradeDetailsModal
    - Presents editable fields for trade-level details (e.g., dates)
    - Designed to be placed inside a parent BModal
    - Uses v-model bindings for two-way sync with parent state
  -->
  <div class="container-fluid">
    <!-- Dates section -->
    <div class="row">
      <div class="col-12">
        <h5 class="mb-3">Trade Dates</h5>
      </div>

      <!-- Bid Date -->
      <div class="col-12 col-md-6 mb-3">
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
      <div class="col-12 col-md-6 mb-3">
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
    </div>
  </div>
</template>

<script setup lang="ts">
// ----------------------------------------------------------------------------------
// TradeDetailsModal.vue
// ----------------------------------------------------------------------------------
// Props and emits are strongly typed. We expose two v-models:
//   - v-model:bidDate (string)
//   - v-model:settlementDate (string)
// The parent controls persistence. We just emit updates and a generic
// "changed" signal on field change so the parent can auto-save.
// ----------------------------------------------------------------------------------
import { computed } from 'vue'

// Props definition with v-model aliases
const props = defineProps<{
  /** ISO date string: YYYY-MM-DD */
  bidDate?: string
  /** ISO date string: YYYY-MM-DD */
  settlementDate?: string
  /** Disable inputs while saving */
  disabled?: boolean
}>()

// Emits: two-way model updates and a generic changed event
const emit = defineEmits<{
  /** v-model:bidDate */
  (e: 'update:bidDate', value: string): void
  /** v-model:settlementDate */
  (e: 'update:settlementDate', value: string): void
  /** Generic change signal so parent can auto-save */
  (e: 'changed'): void
}>()

// Local computed wrappers so we can handle empty strings safely
const bidDateLocal = computed(() => props.bidDate ?? '')
const settlementDateLocal = computed(() => props.settlementDate ?? '')

// Handlers for inputs. We keep handlers small and explicit for clarity.
function onBidInput(ev: Event) {
  // Get HTML input value (string in YYYY-MM-DD or '')
  const v = (ev.target as HTMLInputElement)?.value ?? ''
  emit('update:bidDate', v)
}

function onSettlementInput(ev: Event) {
  // Get HTML input value (string in YYYY-MM-DD or '')
  const v = (ev.target as HTMLInputElement)?.value ?? ''
  emit('update:settlementDate', v)
}

function emitChanged() {
  // Parent may auto-save on this signal
  emit('changed')
}
</script>

<style scoped>
/* Keep styling minimal; rely on Bootstrap/Hyper UI utilities */
</style>
