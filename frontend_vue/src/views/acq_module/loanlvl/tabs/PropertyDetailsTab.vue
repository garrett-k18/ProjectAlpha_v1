<template>
  <!-- Placeholder for Property Details tab content. Replace with real fields/layout. -->
  <div class="text-muted">
    Property Details content coming soon.
  </div>
</template>

<script setup lang="ts">
// Simple placeholder component for the Property Details tab.
// Accepts optional context props for future wiring.
import { withDefaults, defineProps } from 'vue'

withDefaults(defineProps<{
  row?: Record<string, any> | null
  productId?: string | number | null
}>(), {
  row: null,
  productId: null,
})
</script>
