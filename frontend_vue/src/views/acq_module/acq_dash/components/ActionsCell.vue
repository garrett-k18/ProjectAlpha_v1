<template>
  <!--
    Actions cell: provides a row-select checkbox and action buttons.
    - View: Opens loan-level details modal
    - Edit: Opens edit modal (future implementation)
    - Notes: Opens notes modal (future implementation)
    - Drop: Moves asset to "Drops" view (removed from active bidding list)
    - Restore: Restores dropped asset back to active bidding (only in Drops view)
    
    Buttons emit an action back to the parent via the onAction callback passed
    through cellRendererParams. Styling uses Bootstrap 5 utility classes for
    consistency with the template.
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

    <!-- Compact action buttons. Show different buttons based on drop status. -->
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
      <!-- Show Add to Population button if asset is dropped, otherwise show Drop button -->
      <button 
        v-if="isDropped" 
        type="button" 
        class="btn btn-outline-success" 
        @click="emitAction('restore')" 
        title="Add to Population"
      >
        <i class="mdi mdi-plus-circle"></i>
      </button>
      <button 
        v-else
        type="button" 
        class="btn btn-outline-warning" 
        @click="emitAction('drop')" 
        title="Drop from List"
      >
        <i class="mdi mdi-arrow-down-circle"></i>
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
const acqStatus = computed<string>(() => {
  // Surface the acquisition lifecycle status string from backend row data
  const status = props.params.data?.acq_status
  return typeof status === 'string' ? status : ''
})

const isDropped = computed<boolean>(() => {
  // Treat rows with acquisition status DROP as removed from active bidding
  return acqStatus.value === 'DROP'
})

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
