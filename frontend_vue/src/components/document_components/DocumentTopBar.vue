<template>
  <!--
    DocumentTopBar: Right-pane header with title and view mode toggle
    What: Shows current view's label and grid/list toggle buttons
    Why: Reusable across different document manager views to keep UX consistent
    Where: Used inside `.page-aside-right` at the top
    How: Accepts `currentView` and `displayMode`; emits `update:displayMode`
  -->
  <div class="d-flex justify-content-between align-items-center mb-3">
    <h5 class="mb-0">{{ currentView?.label }}</h5>
    <div class="btn-group">
      <button
        class="btn btn-sm"
        :class="displayMode === 'grid' ? 'btn-primary' : 'btn-outline-secondary'"
        @click="$emit('update:displayMode', 'grid')"
      >
        <i class="mdi mdi-view-grid"></i>
      </button>
      <button
        class="btn btn-sm"
        :class="displayMode === 'list' ? 'btn-primary' : 'btn-outline-secondary'"
        @click="$emit('update:displayMode', 'list')"
      >
        <i class="mdi mdi-view-list"></i>
      </button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import type { PropType } from 'vue'
import type { ViewMode } from '@/components/document_components/types'

export default defineComponent({
  name: 'DocumentTopBar',
  props: {
    currentView: { type: Object as PropType<ViewMode | null>, required: false, default: null },
    displayMode: { type: String as PropType<'grid' | 'list'>, required: true },
  },
  emits: ['update:displayMode'],
})
</script>
