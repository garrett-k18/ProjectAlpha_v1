<template>
  <!-- Documents tab now composes the full Document Manager panel for reuse -->
  <b-row class="g-3 g-lg-4 px-3 px-lg-4">
    <b-col lg="12" class="d-flex">
      <div class="w-100 h-100">
        <DocumentManagerPanel
          :row="row"
          :assetId="assetId ?? undefined"
          :module="module"
          :viewModesInput="viewModesNoTrade"
          initialViewId="by-type"
        />
      </div>
    </b-col>
  </b-row>

  <!-- Slot for future document viewer/details area if needed -->
  <slot />
</template>

<script setup lang="ts">
// Documents tab: now composes the reusable DocumentManagerPanel
import { withDefaults, defineProps } from 'vue'
import DocumentManagerPanel from '@/components/document_components/DocumentManagerPanel.vue'
import type { ViewMode } from '@/components/document_components/types'

withDefaults(defineProps<{
  row?: Record<string, any> | null
  assetId?: string | number
  module?: 'acq' | 'am'
}>(), {
  row: null,
  module: 'acq',
})

// View modes for Documents tab (no 'by-trade')
const viewModesNoTrade: ViewMode[] = [
  { id: 'by-type', label: 'By Document Type', icon: 'mdi mdi-file-document', description: 'Group by document category' },
  { id: 'by-status', label: 'By Status', icon: 'mdi mdi-check-circle', description: 'Active, Archived, etc.' },
  { id: 'recent', label: 'Recent', icon: 'mdi mdi-clock-outline', description: 'Recently uploaded' },
]
</script>
