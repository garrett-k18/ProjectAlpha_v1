<template>
  <div class="card h-100 w-100">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">T12 Cash Flow</h4>
    </div>
    <div class="card-body pt-0">
      <div v-if="!rowActive" class="text-muted text-center py-3">No cash flow data available.</div>
      <div v-else class="row g-3">
        <div class="col-md-6" v-if="rowActive.t12_gross_cash_flow != null">
          <small class="text-muted d-block">T12 Gross Cash Flow</small>
          <span class="fw-semibold text-dark">{{ formatCurrency(rowActive.t12_gross_cash_flow) }}</span>
        </div>
        <div class="col-md-6" v-if="rowActive.t12_net_cash_flow != null">
          <small class="text-muted d-block">T12 Net Cash Flow</small>
          <span class="fw-semibold text-dark">{{ formatCurrency(rowActive.t12_net_cash_flow) }}</span>
        </div>
        <div class="col-md-6" v-if="rowActive.t12_total_receipts != null">
          <small class="text-muted d-block">T12 Total Receipts</small>
          <span class="fw-semibold text-dark">{{ formatCurrency(rowActive.t12_total_receipts) }}</span>
        </div>
        <div class="col-md-6" v-if="rowActive.t12_total_disbursements != null">
          <small class="text-muted d-block">T12 Total Disbursements</small>
          <span class="fw-semibold text-dark">{{ formatCurrency(rowActive.t12_total_disbursements) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import type { PropType } from 'vue'
const props = defineProps({ row: { type: Object as PropType<Record<string, any> | null>, default: null } })
const rowActive = computed(() => props.row)
function formatCurrency(v: any): string {
  const n = typeof v === 'number' ? v : parseFloat(String(v))
  if (Number.isNaN(n)) return '' // WHAT: Show blank when cash flow figures are missing instead of rendering "N/A" placeholders
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(n)
}
</script>
