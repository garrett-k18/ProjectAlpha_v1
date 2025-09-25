<template>
  <b-card class="w-100 h-100">
    <template #header>
      <div class="d-flex align-items-center justify-content-between">
        <h5 class="mb-0 d-flex align-items-center">
          <i class="fas fa-pen-alt me-2 text-secondary"></i>
          <span class="badge rounded-pill text-bg-secondary px-3 py-2">Modification</span>
        </h5>
        <div class="d-flex align-items-center gap-2">
          <div class="text-muted small">Hub {{ hubId }}</div>
          <button type="button" class="btn btn-sm btn-outline-danger" @click="emit('delete')">
            <i class="fas fa-trash me-1"></i>
            Delete
          </button>
        </div>
      </div>
    </template>

    <div class="text-muted">
      This Modification outcome has been initialized for hub <span class="fw-semibold">{{ hubId }}</span>.
      Detailed fields and tasking will be added next (mirroring the DIL card pattern).
    </div>
  </b-card>
</template>

<script setup lang="ts">
import { withDefaults, defineProps, defineEmits } from 'vue'

withDefaults(defineProps<{ hubId: number }>(), {})
const emit = defineEmits<{ (e: 'delete'): void }>()
</script>
