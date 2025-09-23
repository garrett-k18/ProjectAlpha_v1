<template>
  <div class="card h-100 w-100">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Rehab Holdbacks</h4>
    </div>
    <div class="card-body pt-0">
      <div v-if="!rowActive" class="text-muted text-center py-3">No rehab holdback data available.</div>
      <div v-else class="row g-3">
        <div class="col-md-6">
          <small class="text-muted d-block">Total Holdback</small>
          <span class="fw-semibold text-dark">{{ formatCurrency(rowActive.rehab_holdback_total) }}</span>
        </div>
        <div class="col-md-6">
          <small class="text-muted d-block">Remaining Holdback</small>
          <span class="fw-semibold text-dark">{{ formatCurrency(rowActive.rehab_holdback_remaining) }}</span>
        </div>
        <div class="col-md-6">
          <small class="text-muted d-block">Disbursed To Date</small>
          <span class="fw-semibold text-dark">{{ formatCurrency(rowActive.rehab_holdback_disbursed_to_date) }}</span>
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
</script>
