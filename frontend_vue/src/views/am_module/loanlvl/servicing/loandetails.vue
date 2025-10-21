<template>
  <div class="card h-100 w-100">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Loan Details</h4>
    </div>
    <div class="card-body pt-0">
      <div v-if="!rowActive" class="text-muted text-center py-3">No loan details available.</div>
      <div v-else class="row g-3">
        
        <div class="col-md-6">
          <small class="text-muted d-block">Interest Rate</small>
          <span class="fw-semibold text-dark">{{ formatPercent(rowActive.interest_rate) }}</span>
        </div>
        <div class="col-md-6">
          <small class="text-muted d-block">Current Balance</small>
          <span class="fw-semibold text-dark">{{ formatCurrency(rowActive.current_balance) }}</span>
        </div>
        <div class="col-md-6">
          <small class="text-muted d-block">Deferred Balance</small>
          <span class="fw-semibold text-dark">{{ formatCurrency(rowActive.deferred_balance) }}</span>
        </div>
        <div class="col-md-6">
          <small class="text-muted d-block">Next Due Date</small>
          <span class="fw-semibold text-dark">{{ formatDate(rowActive.next_due_date) }}</span>
        </div>
        <div class="col-md-6">
          <small class="text-muted d-block">Last Paid Date</small>
          <span class="fw-semibold text-dark">{{ formatDate(rowActive.next_due_date) }}</span>
        </div>
        <div class="col-md-6">
          <small class="text-muted d-block">Current P&I</small>
          <span class="fw-semibold text-dark">{{ formatCurrency(rowActive.current_pi) }}</span>
        </div>
        <div class="col-md-6">
          <small class="text-muted d-block">Current T&I</small>
          <span class="fw-semibold text-dark">{{ formatCurrency(rowActive.current_ti) }}</span>
        </div>
        <div class="col-md-6">
          <small class="text-muted d-block">Current PITI</small>
          <span class="fw-semibold text-dark">{{ formatCurrency((Number(rowActive.current_pi) || 0) + (Number(rowActive.current_ti) || 0)) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { PropType } from 'vue'

const props = defineProps({
  row: { type: Object as PropType<Record<string, any> | null>, default: null },
  productId: { type: [String, Number] as PropType<string | number | null>, default: null },
})

const rowActive = computed(() => props.row)

function formatCurrency(v: any): string {
  const num = typeof v === 'number' ? v : parseFloat(String(v))
  if (Number.isNaN(num)) return 'N/A'
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(num)
}
function formatPercent(v: any): string {
  const num = typeof v === 'number' ? v : parseFloat(String(v))
  if (Number.isNaN(num)) return 'N/A'
  return `${(num * 100).toFixed(2)}%`
}
function formatDate(v: any): string { return v ? new Date(v).toLocaleDateString('en-US') : 'N/A' }
</script>
