<template>
  <!-- DocumentEmptyState: shown when there are no folders or files -->
  <div class="text-center py-5">
    <i class="mdi mdi-folder-open-outline font-48 text-muted"></i>
    <p class="text-muted mt-3">No documents found</p>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
export default defineComponent({ name: 'DocumentEmptyState' })
</script>
