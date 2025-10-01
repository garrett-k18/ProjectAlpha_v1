<template>
  <!-- AM Documents Tab: uses reusable quick view widget -->
  <b-row class="g-3 g-lg-4 px-3 px-lg-4">
    <b-col lg="12" class="d-flex">
      <div class="w-100 h-100">
        <DocumentsQuickView title="All Documents" :docs="docItems" :maxItems="0" :showViewAll="false" />
      </div>
    </b-col>
  </b-row>
  <slot />
</template>

<script setup lang="ts">
import { withDefaults, defineProps, computed } from 'vue'
import DocumentsQuickView from '@/components/DocumentsQuickView.vue'
import type { DocumentItem } from '@/components/DocumentsQuickView.vue'

withDefaults(defineProps<{ row?: Record<string, any> | null; assetHubId?: string | number | null }>(), {
  row: null,
  assetHubId: null,
})

const docItems = computed<DocumentItem[]>(() => [
  { id: 'pdf-bpo', name: 'BPO.pdf', type: 'application/pdf', sizeBytes: Math.round(2.3 * 1024 * 1024), previewUrl: '#', downloadUrl: '#' },
  { id: 'pdf-appraisal', name: 'Appraisal.pdf', type: 'application/pdf', sizeBytes: Math.round(3.25 * 1024 * 1024), previewUrl: '#', downloadUrl: '#' },
  { id: 'doc-memo', name: 'Memo.docx', type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', sizeBytes: Math.round(7.05 * 1024 * 1024), previewUrl: '#', downloadUrl: '#' },
])
</script>
