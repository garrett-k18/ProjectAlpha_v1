<template>
  <!-- AM Acquisition Analysis tab: placeholder for charts/metrics specific to Asset Mgmt -->
  <div class="text-muted px-3 px-lg-4">
    Acquisition Analysis (AM) content coming soon.
  </div>
</template>

<script setup lang="ts">
import { withDefaults, defineProps } from 'vue'
withDefaults(defineProps<{ row?: Record<string, any> | null; productId?: string | number | null }>(), {
  row: null,
  productId: null,
})
</script>
