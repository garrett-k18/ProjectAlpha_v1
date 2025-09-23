<template>
  <div class="card h-100 w-100">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Origination</h4>
    </div>
    <div class="card-body pt-0">
      <div v-if="!rowActive" class="text-muted text-center py-3">No origination data available.</div>
      <div v-else class="row g-3">
        <div class="col-md-6">
          <small class="text-muted d-block">Origination Date</small>
          <span class="fw-semibold text-dark">{{ formatDate(rowActive.origination_date) }}</span>
        </div>
        <div class="col-md-6">
          <small class="text-muted d-block">Origination Balance</small>
          <span class="fw-semibold text-dark">{{ formatCurrency(rowActive.origination_balance) }}</span>
        </div>
        <div class="col-md-6">
          <small class="text-muted d-block">Origination Rate</small>
          <span class="fw-semibold text-dark">{{ formatPercent(rowActive.origination_interest_rate) }}</span>
        </div>
        <div class="col-md-6">
          <small class="text-muted d-block">Original Appraised Value</small>
          <span class="fw-semibold text-dark">{{ formatCurrency(rowActive.original_appraised_value) }}</span>
        </div>
        <div class="col-md-6">
          <small class="text-muted d-block">Original Appraised Date</small>
          <span class="fw-semibold text-dark">{{ formatDate(rowActive.original_appraised_date) }}</span>
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
function formatCurrency(v: any): string { const n = typeof v==='number'?v:parseFloat(String(v)); return Number.isNaN(n)?'N/A':new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:0}).format(n) }
function formatPercent(v: any): string { const n = typeof v==='number'?v:parseFloat(String(v)); return Number.isNaN(n)?'N/A':`${(n*100).toFixed(2)}%` }
function formatDate(v:any): string { return v? new Date(v).toLocaleDateString('en-US'):'N/A' }
</script>
