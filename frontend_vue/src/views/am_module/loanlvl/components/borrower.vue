<template>
  <div class="card h-100 w-100">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Borrower</h4>
    </div>
    <div class="card-body pt-0">
      <div v-if="!rowActive" class="text-muted text-center py-3">No borrower data available.</div>
      <div v-else class="row g-3">
        <div class="col-md-6">
          <small class="text-muted d-block">Borrower Name</small>
          <span class="fw-semibold text-dark">{{ [rowActive.borrower_first_name, rowActive.borrower_last_name].filter(Boolean).join(' ') || 'N/A' }}</span>
        </div>
        <div class="col-md-6">
          <small class="text-muted d-block">Home Phone</small>
          <span class="fw-semibold text-dark">{{ rowActive.borrower_home_phone || 'N/A' }}</span>
        </div>
        <div class="col-md-6">
          <small class="text-muted d-block">Current FICO</small>
          <span class="fw-semibold text-dark">
            {{ formatNumber(rowActive.current_fico) }}
            <em class="text-muted"> ({{ formatDate(rowActive.current_fico_date) }})</em>
          </span>
        </div>
        <div class="col-md-6">
          <small class="text-muted d-block">Current FICO Date</small>
          <span class="fw-semibold text-dark">{{ formatDate(rowActive.current_fico_date) }}</span>
        </div>
        <div class="col-md-6">
          <small class="text-muted d-block">Borrower Count</small>
          <span class="fw-semibold text-dark">{{ formatNumber(rowActive.borrower_count) }}</span>
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

function formatDate(v:any): string { return v ? new Date(v).toLocaleDateString('en-US') : 'N/A' }
function formatNumber(v:any): string { const n = typeof v==='number'? v : parseFloat(String(v)); return Number.isNaN(n)? 'N/A' : new Intl.NumberFormat('en-US').format(n) }
</script>
