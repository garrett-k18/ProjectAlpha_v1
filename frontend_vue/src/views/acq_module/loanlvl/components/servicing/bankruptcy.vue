<template>
  <!--
    bankruptcy.vue
    - Reusable card that displays bankruptcy-related fields from SellerRawData.
    - Accepts either a full `row` object or, if absent, fetches data by `productId`.
    - Uses Hyper UI/Bootstrap card styling with acquisitions-consistent header.
  -->
  <div class="card h-100">
    <!-- Header follows acquisitions dashboard pattern: card-header + h4.header-title -->
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Bankruptcy</h4>
    </div>

    <!-- Body uses pt-0 to align spacing with other cards -->
    <div class="card-body pt-0">
      <!-- Empty state when nothing is available to display -->
      <div v-if="!hasAnyData" class="text-muted text-center py-3">
        No bankruptcy data available.
      </div>

      <!-- Details grid; each field shown only if present -->
      <div v-else class="row g-3">
        <div class="col-md-6">
          <!-- Bankruptcy Flag -->
          <div class="mb-2">
            <small class="text-muted d-block">Bankruptcy Flag</small>
            <span v-if="rowActive?.bk_flag" class="badge bg-warning-subtle text-warning">Yes</span>
            <span v-else class="badge bg-secondary-subtle text-secondary">No</span>
          </div>
        </div>

        <div class="col-md-6" v-if="rowActive?.bk_chapter">
          <!-- Chapter -->
          <div class="mb-2">
            <small class="text-muted d-block">Chapter</small>
            <span class="fw-semibold text-dark">{{ rowActive?.bk_chapter }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
/**
 * bankruptcy.vue
 * - Displays bankruptcy fields for a loan from SellerRawData:
 *   bk_flag, bk_chapter.
 * - Props allow passing a `row` directly or fetching by `productId`.
 * - Uses Hyper UI header pattern (h4.header-title) and consistent spacing (pt-0 body).
 */
import { defineComponent, computed, ref, watch } from 'vue'
import type { PropType } from 'vue'
import http from '@/lib/http'

export default defineComponent({
  name: 'Bankruptcy',
  props: {
    row: {
      type: Object as PropType<Record<string, any> | null>,
      default: null,
    },
    productId: {
      type: [String, Number] as PropType<string | number | null>,
      default: null,
    },
  },
  setup(props) {
    // Local state to store a fetched row as a fallback
    const fetchedRow = ref<Record<string, any> | null>(null)

    // Active row: prefer the `row` prop; otherwise use `fetchedRow`
    const rowActive = computed(() => props.row ?? fetchedRow.value)

    // Derived flag indicating whether there is any bankruptcy data to display
    const hasAnyData = computed<boolean>(() => {
      const r = rowActive.value
      return !!(r && (r.bk_flag != null || r.bk_chapter))
    })

    // Fetch helper that gets the row by id from the backend API
    async function loadRowById(id: number) {
      try {
        const res = await http.get(`/acq/raw-data/by-id/${id}/`)
        fetchedRow.value = res.data && Object.keys(res.data).length ? res.data : null
        // eslint-disable-next-line no-console
        console.debug('[Bankruptcy] loaded row for', id)
      } catch (err) {
        // eslint-disable-next-line no-console
        console.warn('[Bankruptcy] failed to load row for', id, err)
        fetchedRow.value = null
      }
    }

    // Watch for productId changes; fetch when appropriate
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

    return {
      rowActive,
      hasAnyData,
    }
  },
})
</script>

<style scoped>
/* Rely on Hyper UI/Bootstrap utility classes for styling; no custom CSS needed */
</style>
