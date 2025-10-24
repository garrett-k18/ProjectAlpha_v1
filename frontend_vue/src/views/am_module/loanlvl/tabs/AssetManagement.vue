<template>
  <!-- Asset Management: Tasking & Outcome Management -->
  <div class="px-3 px-lg-4">
    <!-- AM content is fully delegated to AmLlTasking -->
    <AmLlTasking :row="props.row" :assetHubId="props.assetHubId" />
  </div>
  
</template>

<script setup lang="ts">
import { withDefaults, defineProps } from 'vue'
import AmLlTasking from '@/views/am_module/loanlvl/am_tasking/index_amLLTasking.vue'

const props = withDefaults(defineProps<{ row?: Record<string, any> | null; assetHubId?: string | number | null }>(), {
  row: null,
  assetHubId: null,
})

</script>

