<template>
  <DocumentManagerPanel
    :tradeId="tradeId ?? undefined"
    :assetId="assetId ?? undefined"
    :row="row ?? null"
    module="acq"
    :viewModesInput="viewModesTradeOnly"
    initialViewId="by-type"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import DocumentManagerPanel from '@/components/document_components/DocumentManagerPanel.vue'
import type { ViewMode } from '@/components/document_components/types'

const props = withDefaults(defineProps<{
  assetId?: string | number | null
  row?: Record<string, any> | null
  tradeId?: string | number | null
}>(), {
  assetId: null,
  row: null,
  tradeId: null,
})

// Constrain view modes to trade-focused variants for modal usage
const viewModesTradeOnly = computed<ViewMode[]>(() => [
  { id: 'by-type', label: 'By Document Type', icon: 'mdi mdi-file-document', description: 'Group by document category' },
  { id: 'recent', label: 'Recent', icon: 'mdi mdi-clock-outline', description: 'Recently uploaded' },
])
</script>

<style scoped>
/* Modal now reuses the global DocumentManagerPanel styling */
</style>
