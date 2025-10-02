<template>
  <!--
    MsaAssumptionsTable.vue
    - Placeholder table for MSA-level assumptions (per metro/CBSA)
    - Will mirror StateAssumptionsTable patterns once API/data model are defined

    Location: frontend_vue/src/1_global/assumptions/components/MsaAssumptionsTable.vue
  -->
  <div class="msa-assumptions-container">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <div>
        <h5 class="mb-1">MSA Assumptions</h5>
        <p class="text-muted small mb-0">Configure metro/CBSA-specific modeling assumptions</p>
      </div>
      <div class="d-flex gap-2">
        <input 
          type="text" 
          class="form-control form-control-sm" 
          placeholder="Search MSAs..."
          v-model="searchQuery"
          style="width: 200px;"
        />
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

    <div class="text-muted small">Coming soon: table for MSA assumptions</div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

// Emits change events to parent hub
const emit = defineEmits<{ (e: 'changed'): void }>()

const searchQuery = ref('')
const hasChanges = ref(false)
const isSaving = ref(false)

function markAsChanged() {
  hasChanges.value = true
  emit('changed')
}

async function saveChanges() {
  isSaving.value = true
  try {
    // TODO: Implement API save once endpoints exist
    await new Promise(r => setTimeout(r, 400))
    hasChanges.value = false
  } finally {
    isSaving.value = false
  }
}
</script>

<style scoped>
.msa-assumptions-container {
  min-height: 200px;
}
</style>
