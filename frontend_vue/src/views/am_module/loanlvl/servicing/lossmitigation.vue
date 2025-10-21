<template>
  <div class="card h-100 w-100">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Loss Mitigation</h4>
    </div>
    <div class="card-body pt-0">
      <div v-if="!rowActive" class="text-muted text-center py-3">No loss mit data available.</div>
      <div v-else class="row g-3">
        <div class="col-md-6">
          <small class="text-muted d-block">Loss Mit Flag</small>
          <span v-if="!!rowActive.loss_mitigation_status" class="badge bg-warning-subtle text-warning">Yes</span>
          <span v-else class="badge bg-secondary-subtle text-secondary">No</span>
        </div>
        <div class="col-md-6" v-if="rowActive.loss_mitigation_status">
          <small class="text-muted d-block">Status</small>
          <span class="fw-semibold text-dark">{{ rowActive.loss_mitigation_status }}</span>
        </div>
        <div class="col-md-6" v-if="rowActive.loss_mitigation_status && rowActive.loss_mitigation_start_date">
          <small class="text-muted d-block">Start Date</small>
          <span class="fw-semibold text-dark">{{ formatDate(rowActive.loss_mitigation_start_date) }}</span>
        </div>
        <div class="col-md-6" v-if="rowActive.loss_mitigation_status && rowActive.repayment_plan_status">
          <small class="text-muted d-block">Repayment Plan</small>
          <span class="fw-semibold text-dark">{{ rowActive.repayment_plan_status }}</span>
        </div>
        <div class="col-md-6" v-if="rowActive.loss_mitigation_status && rowActive.loan_modification_date">
          <small class="text-muted d-block">Loan Mod Date</small>
          <span class="fw-semibold text-dark">{{ formatDate(rowActive.loan_modification_date) }}</span>
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
function formatDate(v:any): string { return v? new Date(v).toLocaleDateString('en-US'):'N/A' }
</script>
