<template>
  <div class="card h-100 w-100">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Foreclosure</h4>
    </div>
    <div class="card-body pt-0">
      <div v-if="!rowActive" class="text-muted text-center py-3">No foreclosure data available.</div>
      <div v-else class="row g-3">
        <div class="col-md-6">
          <small class="text-muted d-block">FC Flag</small>
          <span v-if="rowActive.fc_flag" class="badge bg-danger-subtle text-danger">Yes</span>
          <span v-else class="badge bg-secondary-subtle text-secondary">No</span>
        </div>
        <div class="col-md-6" v-if="rowActive.fc_flag && rowActive.fc_status">
          <small class="text-muted d-block">FC Status</small>
          <span class="fw-semibold text-dark">{{ rowActive.fc_status }}</span>
        </div>
        <div class="col-md-6" v-if="rowActive.fc_flag && rowActive.date_referred_to_fc_atty">
          <small class="text-muted d-block">Referred to Atty</small>
          <span class="fw-semibold text-dark">{{ formatDate(rowActive.date_referred_to_fc_atty) }}</span>
        </div>
        <div class="col-md-6" v-if="rowActive.fc_flag && rowActive.foreclosure_business_area_status">
          <small class="text-muted d-block">FC BA Status</small>
          <span class="fw-semibold text-dark">{{ rowActive.foreclosure_business_area_status }}</span>
        </div>
        <div class="col-md-6" v-if="rowActive.fc_flag && rowActive.foreclosure_business_area_status_date">
          <small class="text-muted d-block">FC BA Status Date</small>
          <span class="fw-semibold text-dark">{{ formatDate(rowActive.foreclosure_business_area_status_date) }}</span>
        </div>
        <div class="col-md-6" v-if="rowActive.fc_flag && rowActive.scheduled_fc_sale_date">
          <small class="text-muted d-block">Scheduled Sale</small>
          <span class="fw-semibold text-dark">{{ formatDate(rowActive.scheduled_fc_sale_date) }}</span>
        </div>
        <div class="col-md-6" v-if="rowActive.fc_flag && rowActive.actual_fc_sale_date">
          <small class="text-muted d-block">Actual Sale</small>
          <span class="fw-semibold text-dark">{{ formatDate(rowActive.actual_fc_sale_date) }}</span>
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
