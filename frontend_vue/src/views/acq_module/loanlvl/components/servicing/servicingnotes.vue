<template>
  <!--
    servicingnotes.vue
    - Reusable card to display long-form Servicing Notes for a loan.
    - Accepts either a full `row` object or, if absent, fetches data by `productId`.
    - Uses Hyper UI/Bootstrap card styling with acquisitions-consistent header.

    NOTE: Backend field name not confirmed in seller.py. This component will look
    for the following likely keys on the row and pick the first non-empty value:
      - servicing_notes
      - notes
      - servicer_notes
    When backend exposes a definitive field, pass it through the API response
    using one of the above keys or update the mapping here.
  -->
  <div class="card h-100">
    <!-- Header -->
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Servicing Notes</h4>
    </div>

    <div class="card-body pt-0">
      <!-- Empty state -->
      <div v-if="!hasNotes" class="text-muted text-center py-3">
        No servicing notes available.
      </div>

      <!-- Notes content -->
      <div v-else>
        <pre class="mb-0 text-wrap" style="white-space: pre-wrap; word-break: break-word;">{{ notesText }}</pre>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
/**
 * servicingnotes.vue
 * - Displays long-form text notes for a loan from SellerRawData (or related model).
 * - Props allow passing a `row` directly or fetching by `productId`.
 * - Highly commented for clarity and future maintainability.
 */
import { defineComponent, computed, ref, watch } from 'vue'
import type { PropType } from 'vue'
import http from '@/lib/http'

export default defineComponent({
  name: 'ServicingNotes',
  props: {
    // Upstream-provided full row (preferred if already available)
    row: {
      type: Object as PropType<Record<string, any> | null>,
      default: null,
    },
    // Product ID to fetch row if not provided
    productId: {
      type: [String, Number] as PropType<string | number | null>,
      default: null,
    },
  },
  setup(props) {
    // Local store for fetched row when `row` prop is not provided
    const fetchedRow = ref<Record<string, any> | null>(null)

    // Active row selects prop first, otherwise fetched
    const rowActive = computed(() => props.row ?? fetchedRow.value)

    // Choose first available notes-like field
    const notesText = computed<string>(() => {
      const r = rowActive.value as any
      if (!r) return ''
      return (
        r.servicing_notes ||
        r.notes ||
        r.servicer_notes ||
        ''
      )
    })

    // Whether there is any content to display
    const hasNotes = computed<boolean>(() => !!(notesText.value && String(notesText.value).trim().length))

    // Fetch by product ID when needed
    async function loadRowById(id: number) {
      try {
        const res = await http.get(`/acq/raw-data/by-id/${id}/`)
        fetchedRow.value = res.data && Object.keys(res.data).length ? res.data : null
        // eslint-disable-next-line no-console
        console.debug('[ServicingNotes] loaded row for', id)
      } catch (err) {
        // eslint-disable-next-line no-console
        console.warn('[ServicingNotes] failed to load row for', id, err)
        fetchedRow.value = null
      }
    }

    // React to productId changes
    watch(
      () => props.productId,
      (raw) => {
        const id = raw != null ? Number(raw) : NaN
        if (!props.row && Number.isFinite(id)) {
          loadRowById(id)
        } else if (!Number.isFinite(id)) {
          fetchedRow.value = null
        }
      },
      { immediate: true }
    )

    return { rowActive, notesText, hasNotes }
  },
})
</script>

<style scoped>
/* No custom styles needed beyond Bootstrap/Hyper utilities */
</style>
