<template>
  <!--
    Actions cell: provides action buttons for each row.
    - View: Opens loan-level details modal
    - Edit: Opens edit modal (future implementation)
    - Notes: Opens notes modal (future implementation)
    - Drop: Moves asset to "Drops" view (removed from active bidding list)
    - Restore: Restores dropped asset back to active bidding (only in Drops view)
    
    Buttons emit an action back to the parent via the onAction callback passed
    through cellRendererParams. Styling uses Bootstrap 5 utility classes for
    consistency with the template.
    
    Note: Row selection checkbox is now handled by AG Grid's built-in selection column.
  -->
  <div class="actions-cell d-flex align-items-center gap-2 h-100">
    <!-- Compact action buttons. Show different buttons based on drop status or custom config. -->
    <div class="btn-group btn-group-sm" role="group" aria-label="Row actions">
      <!-- Custom action buttons (used by AM grid to replace free slots) -->
      <template v-if="hasCustomActions">
        <button
          v-for="action in customActions"
          :key="action.key"
          type="button"
          class="btn"
          :class="action.variantClass"
          :title="action.title"
          @click="emitAction(action.key)"
        >
          <i class="mdi" :class="action.iconClass"></i>
        </button>
      </template>
      <!-- Default action buttons (ACQ grid behavior) -->
      <template v-else>
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
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
// Types for AG Grid cell renderers
import type { ICellRendererParams } from 'ag-grid-community'
import { computed } from 'vue'

// Props provided by AG Grid to Vue cell renderers
// Action button configuration for custom use-cases (e.g., AM grid "Add to List")
type ActionButtonConfig = {
  // Unique action key emitted back to parent (e.g., 'view', 'add_to_list')
  key: string
  // Tooltip text for the button
  title: string
  // mdi icon class name (e.g., 'mdi-eye', 'mdi-playlist-plus')
  iconClass: string
  // Bootstrap variant class for the button (e.g., 'btn-outline-primary')
  variantClass: string
}

const props = defineProps<{ params: ICellRendererParams & {
  // Optional callback provided from parent via cellRendererParams
  onAction?: (action: string, row: any) => void
  // Optional custom action list to override the default button set
  actions?: ActionButtonConfig[]
} }>()

// Access helpers
const acqStatus = computed<string>(() => {
  // Surface the acquisition lifecycle status string from backend row data
  const status = props.params.data?.acq_status
  return typeof status === 'string' ? status : ''
})

const isDropped = computed<boolean>(() => {
  // Treat rows with acquisition status DROP as removed from active bidding
  return acqStatus.value === 'DROP'
})

// Determine if custom actions were provided by the parent
const hasCustomActions = computed<boolean>(() => {
  return Array.isArray(props.params?.actions) && props.params.actions.length > 0
})

// Normalize custom actions list for rendering
const customActions = computed<ActionButtonConfig[]>(() => {
  return (props.params?.actions || []).filter((action) => !!action?.key)
})

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
