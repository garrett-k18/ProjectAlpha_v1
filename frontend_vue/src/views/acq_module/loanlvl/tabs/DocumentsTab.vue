<template>
  <!-- Full documents list using the reusable quick view widget -->
  <b-row class="g-3 g-lg-4 px-3 px-lg-4">
    <b-col lg="12" class="d-flex">
      <div class="w-100 h-100">
        <DocumentsQuickView
          title="All Documents"
          :docs="docItems"
          :maxItems="0"
          :showViewAll="false"
        />
      </div>
    </b-col>
  </b-row>
  
  <!-- Slot for future document viewer/details area if needed -->
  <slot />
</template>

<script setup lang="ts">
// Documents tab: renders the full document list using the reusable widget
// Uses BootstrapVue Next grid for layout and Hyper UI card styles from the component
import { withDefaults, defineProps, computed } from 'vue'
import DocumentsQuickView from '@/components/DocumentsQuickView.vue'
import type { DocumentItem } from '@/components/DocumentsQuickView.vue'

withDefaults(defineProps<{
  row?: Record<string, any> | null
  productId?: string | number | null
}>(), {
  row: null,
  productId: null,
})

// Demo dataset renamed per request
// Replace with API-backed mapping once available
const docItems = computed<DocumentItem[]>(() => [
  {
    id: 'pdf-bpo',
    name: 'BPO.pdf',
    type: 'application/pdf',
    sizeBytes: Math.round(2.3 * 1024 * 1024),
    previewUrl: '#',
    downloadUrl: '#',
  },
  {
    id: 'pdf-appraisal',
    name: 'Appraisal.pdf',
    type: 'application/pdf',
    sizeBytes: Math.round(3.25 * 1024 * 1024),
    previewUrl: '#',
    downloadUrl: '#',
  },
  {
    id: 'doc-memo',
    name: 'Memo.docx',
    type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    sizeBytes: Math.round(7.05 * 1024 * 1024),
    previewUrl: '#',
    downloadUrl: '#',
  },
])
</script>
