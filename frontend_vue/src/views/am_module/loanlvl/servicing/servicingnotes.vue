<template>
  <div class="card h-100 w-100">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Servicing Notes</h4>
    </div>
    <div class="card-body pt-0">
      <div v-if="!rowActive" class="text-muted text-center py-3">No notes available.</div>
      <div v-else class="row g-3">
        <div class="col-12">
          <small class="text-muted d-block">Last Note</small>
          <div class="fw-semibold text-dark">{{ rowActive.last_note || '' }}</div>
        </div>
        <div class="col-md-6">
          <small class="text-muted d-block">Last Note Date</small>
          <span class="fw-semibold text-dark">{{ formatDate(rowActive.last_note_date) }}</span>
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
/* Always show labels; fallback to blank strings so servicing tab omits placeholder text */
function formatDate(v:any): string { return v ? new Date(v).toLocaleDateString('en-US') : '' }
</script>
