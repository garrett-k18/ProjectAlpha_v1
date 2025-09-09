<template>
  <!--
    Actions cell: provides a row-select checkbox and four action buttons.
    Buttons emit an action back to the parent via the onAction callback passed
    through cellRendererParams. Styling uses Bootstrap 5 utility classes for
    consistency with the template. Replace classes with Hyper UI classes if desired.
  -->
  <div class="actions-cell d-flex align-items-center gap-2 h-100">
    <!-- Row selection checkbox tied to AG Grid selection state -->
    <input
      class="form-check-input m-0"
      type="checkbox"
      :checked="isSelected"
      @change="onToggleSelection($event)"
      :aria-label="`Select row ${rowId}`"
    />

    <!-- Compact action buttons. Replace icons/labels per your needs. -->
    <div class="btn-group btn-group-sm" role="group" aria-label="Row actions">
      <button type="button" class="btn btn-outline-primary" @click="emitAction('view')" title="View">
        <i class="mdi mdi-eye"></i>
      </button>
      <button type="button" class="btn btn-outline-secondary" @click="emitAction('edit')" title="Edit">
        <i class="mdi mdi-pencil"></i>
      </button>
      <button type="button" class="btn btn-outline-info" @click="emitAction('notes')" title="Notes">
        <i class="mdi mdi-note-text"></i>
      </button>
      <button type="button" class="btn btn-outline-danger" @click="emitAction('delete')" title="Delete">
        <i class="mdi mdi-delete"></i>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
// Types for AG Grid cell renderers
import type { ICellRendererParams } from 'ag-grid-community'
import { computed } from 'vue'

// Props provided by AG Grid to Vue cell renderers
const props = defineProps<{ params: ICellRendererParams & {
  // Optional callback provided from parent via cellRendererParams
  onAction?: (action: string, row: any) => void
} }>()

// Access helpers
const isSelected = computed<boolean>(() => {
  const node = (props?.params as any)?.node
  if (!node || typeof node.isSelected !== 'function') return false
  return node.isSelected() === true
})
const rowId = computed(() => props.params.node.id)

/**
 * Toggle selection using AG Grid API so the grid stays in sync.
 */
function onToggleSelection(event: Event) {
  const target = event.target as HTMLInputElement
  const checked = !!target?.checked
  // Select this node only (do not clear others); source = UI event
  props.params.node.setSelected(checked)
}

/**
 * Emit an action back to the parent via the provided callback.
 * Consumers can open modals or perform any side-effect.
 */
function emitAction(action: string) {
  if (typeof props.params.onAction === 'function') {
    props.params.onAction(action, props.params.data)
  } else {
    // Fallback: log for debugging if no callback was provided
    // eslint-disable-next-line no-console
    console.log(`[ActionsCell] action=\"${action}\"`, props.params.data)
  }
}
</script>

<style scoped>
/* Keep the cell contents compact and horizontally aligned */
.btn-group .btn {
  padding: 0.15rem 0.35rem; /* smaller hit area for dense grids */
}
/* Make the root fill the full cell height so align-items-center truly centers vertically */
.actions-cell {
  height: 100%;
}
</style>
