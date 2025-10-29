<template>
  <!--
    Simple link-style cell that renders the cell value (record ID) as a clickable link.
    Clicking will navigate to the new loan-level route so the details open as a full page
    in the master wrapper (`loanlvl_index.vue`).
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
// Import router utilities to perform navigation on click
import { useRouter } from 'vue-router'

// Define the props expected from AG Grid's Vue cell renderer integration.
// Single-file toggle support:
// - openMode: 'modal' | 'page' -> determines preferred behavior
// - onOpen: function(payload) -> when provided (and not explicitly overridden by openMode==='page'), invoke to open parent-controlled modal
const props = defineProps<{ params: ICellRendererParams & { onOpen?: (payload: { id: string; row: any; addr?: string }) => void; openMode?: 'modal' | 'page' } }>()

// Initialize router once at setup scope
const router = useRouter()

// Compute a display value for the cell (fallback to empty string if nullish)
const displayValue = computed<string>(() => {
  const v = (props?.params?.value ?? '') as any
  return String(v)
})

/**
 * onClick
 * Handles click on the ID link. Navigates to the new route `/loanlvl/products-details`
 * with query params for `id` and a best-effort `addr` built from row data.
 *
 * Notes:
 * - We intentionally avoid opening a modal here to keep the grid free of UI logic.
 * - If an `onOpen` callback exists from older code, we ignore it and route instead.
 */
function onClick() {
  // Extract the row (record) associated with this cell; AG Grid provides it in params.data
  const row: any = props?.params?.data ?? {}

  // Compute the product/record id from the cell value (what this cell renders)
  const id = String(props?.params?.value ?? '')

  // Build a best-effort single-line address string from common fields if present
  const street = String(row['street_address'] ?? '').trim()
  const city = String(row['city'] ?? '').trim()
  const state = String(row['state'] ?? '').trim()
  const zip = String(row['zip'] ?? '').trim()
  const locality = [city, state].filter(Boolean).join(', ')
  const tail = [locality, zip].filter(Boolean).join(' ')
  const addr = [street, tail].filter(Boolean).join(', ')

  // Behavior toggle: if a parent provided an onOpen callback, prefer modal
  // unless the explicit openMode is 'page'. This matches legacy behavior
  // where presence of onOpen meant modal-first.
  const openMode = props?.params?.openMode
  if (typeof props?.params?.onOpen === 'function' && openMode !== 'page') {
    // Parent handles showing a BModal and can pass { id, row, addr }
    // Debug: log branch decision
    // eslint-disable-next-line no-console
    console.debug('[IdLinkCell] opening modal via onOpen()', { id, addr, hasRow: !!row })
    props.params.onOpen({ id, row, addr })
    return
  }

  // Navigate to the loan-level product details page (full-page wrapper)
  // Debug: log branch decision
  // eslint-disable-next-line no-console
  console.debug('[IdLinkCell] routing to full page', { id, addr })
  router.push({
    path: '/loanlvl/products-details',
    query: {
      id,           // record id used to fetch details in the page
      addr: addr || undefined, // optional address string for breadcrumb/title convenience
    },
  })
}
</script>

<style scoped>
/* Keep the link inline and subtle to fit dense grid UIs */
a {
  cursor: pointer;
}
</style>
