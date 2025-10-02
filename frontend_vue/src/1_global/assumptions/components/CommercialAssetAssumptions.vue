<template>
  <!--
    CommercialAssetAssumptions.vue
    - Placeholder for commercial asset modeling assumptions (e.g., units, lease-up, capex)

    Location: frontend_vue/src/1_global/assumptions/components/CommercialAssetAssumptions.vue
  -->
  <div class="commercial-asset-assumptions-container">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <div>
        <h5 class="mb-1">Commercial Asset Assumptions</h5>
        <p class="text-muted small mb-0">Parameters for commercial unit modeling</p>
      </div>
      <div class="d-flex gap-2">
        <button 
          class="btn btn-sm btn-primary"
          @click="saveChanges"
          :disabled="!hasChanges || isSaving"
        >
          <i class="mdi mdi-content-save me-1"></i>
          {{ isSaving ? 'Saving...' : 'Save' }}
        </button>
      </div>
    </div>

    <div class="text-muted small">Coming soon: inputs for commercial asset assumptions</div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
const emit = defineEmits<{ (e: 'changed'): void }>()

const hasChanges = ref(false)
const isSaving = ref(false)

function markAsChanged() {
  hasChanges.value = true
  emit('changed')
}

async function saveChanges() {
  isSaving.value = true
  try {
    await new Promise(r => setTimeout(r, 400))
    hasChanges.value = false
  } finally {
    isSaving.value = false
  }
}
</script>

<style scoped>
.commercial-asset-assumptions-container {
  min-height: 200px;
}
</style>
