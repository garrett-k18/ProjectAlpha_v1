<template>
  <div class="card h-100 w-100">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Bankruptcy</h4>
    </div>
    <div class="card-body pt-0">
      <div v-if="!rowActive" class="text-muted text-center py-3">No bankruptcy data available.</div>
      <div v-else class="row g-3">
        <div class="col-md-6">
          <small class="text-muted d-block">BK Flag</small>
          <span v-if="rowActive.bk_flag" class="badge bg-warning-subtle text-warning">Yes</span>
          <span v-else class="badge bg-secondary-subtle text-secondary">No</span>
        </div>
        <div class="col-md-6" v-if="rowActive.bk_flag && rowActive.bk_ch">
          <small class="text-muted d-block">Chapter</small>
          <span class="fw-semibold text-dark">{{ rowActive.bk_ch }}</span>
        </div>
        <div class="col-md-6" v-if="rowActive.bk_flag && rowActive.bk_current_status">
          <small class="text-muted d-block">Current Status</small>
          <span class="fw-semibold text-dark">{{ rowActive.bk_current_status }}</span>
        </div>
        <div class="col-md-6" v-if="rowActive.bk_flag && rowActive.bk_filed_date">
          <small class="text-muted d-block">Filed Date</small>
          <span class="fw-semibold text-dark">{{ formatDate(rowActive.bk_filed_date) }}</span>
        </div>
        <div class="col-md-6" v-if="rowActive.bk_flag && rowActive.bk_discharge_date">
          <small class="text-muted d-block">Discharge Date</small>
          <span class="fw-semibold text-dark">{{ formatDate(rowActive.bk_discharge_date) }}</span>
        </div>
        <div class="col-md-6" v-if="rowActive.bk_flag && rowActive.bk_dismissed_date">
          <small class="text-muted d-block">Dismissed Date</small>
          <span class="fw-semibold text-dark">{{ formatDate(rowActive.bk_dismissed_date) }}</span>
        </div>
        <div class="col-md-6" v-if="rowActive.bk_flag && rowActive.bk_case_closed_date">
          <small class="text-muted d-block">Case Closed</small>
          <span class="fw-semibold text-dark">{{ formatDate(rowActive.bk_case_closed_date) }}</span>
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
