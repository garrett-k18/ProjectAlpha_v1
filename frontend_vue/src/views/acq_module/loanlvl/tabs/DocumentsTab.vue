<template>
  <!-- Placeholder for Documents tab content. Replace with file list/viewer. -->
  <div class="text-muted">
    Documents content coming soon.
  </div>
</template>

<script setup lang="ts">
// Placeholder component for Documents.
import { withDefaults, defineProps } from 'vue'

withDefaults(defineProps<{
  row?: Record<string, any> | null
  productId?: string | number | null
}>(), {
  row: null,
  productId: null,
})
</script>
