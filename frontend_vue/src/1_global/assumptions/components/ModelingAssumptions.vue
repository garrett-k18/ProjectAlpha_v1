<template>
  <!--
    ModelingAssumptions.vue
    - Placeholder for global modeling assumptions (e.g., discount rates, scenario toggles)

    Location: frontend_vue/src/1_global/assumptions/components/ModelingAssumptions.vue
  -->
  <div class="modeling-assumptions-container">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <div>
        <h5 class="mb-1">Modeling Assumptions</h5>
        <p class="text-muted small mb-0">Global parameters used across models</p>
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

    <div class="text-muted small">Coming soon: controls for global modeling parameters</div>
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
.modeling-assumptions-container {
  min-height: 200px;
}
</style>
