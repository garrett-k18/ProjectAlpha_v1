<template>
  <!--
    Simple link-style cell that renders the cell value (record ID) as a clickable link.
    Clicking will call the provided onOpen callback with the current row's data.
  -->
  <a
    href="javascript:void(0);"
    class="text-primary text-decoration-underline"
    @click.stop.prevent="onClick"
    :aria-label="`Open details for record ${displayValue}`"
  >
    {{ displayValue }}
  </a>
</template>

<script setup lang="ts">
// Import Vue APIs for computed values
import { computed } from 'vue'
// Import AG Grid types to strongly type the params
import type { ICellRendererParams } from 'ag-grid-community'

// Define the props expected from AG Grid's Vue cell renderer integration.
// We also accept an optional onOpen callback from the parent via cellRendererParams
// which will be used to open the modal from the parent component with full control.
const props = defineProps<{ params: ICellRendererParams & { onOpen?: (row: any) => void } }>()

// Compute a display value for the cell (fallback to empty string if nullish)
const displayValue = computed<string>(() => {
  const v = (props?.params?.value ?? '') as any
  return String(v)
})

/**
 * onClick
 * Handles click on the ID link. Uses the provided onOpen callback so the parent
 * component (grid host) can control modal state and pass the current row data.
 */
function onClick() {
  // Prefer explicit callback (best practice to avoid coupling renderer to parent)
  if (typeof props.params.onOpen === 'function') {
    props.params.onOpen(props.params.data)
    return
  }
  // Fallback: emit a console message for debugging if no callback provided
  // eslint-disable-next-line no-console
  console.log('[IdLinkCell] onOpen callback not provided. Row =', props.params.data)
}
</script>

<style scoped>
/* Keep the link inline and subtle to fit dense grid UIs */
a {
  cursor: pointer;
}
</style>
