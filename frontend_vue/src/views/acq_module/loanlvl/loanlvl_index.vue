<template>
  <!--
    Master wrapper for Loan-Level UI.
    - Provides Hyper UI Layout/Breadcrumb shell for full-page usage
    - Hosts loan-level tabs (Snapshot, Property Details, Loan Details, Acquisition Analysis)
    - Central place for modal-related global styles (dialog/content sizing), so other
      components (e.g., data grid) remain clean and grid-only.
  -->
  <component :is="standalone ? Layout : 'div'">
    <Breadcrumb v-if="standalone" :title="displayTitle" :items="items" />

    <!--
      Delegated tab structure to `LoanTabs.vue` for modularity and reuse.
      Docs (BootstrapVue Next tabs used inside LoanTabs): https://bootstrap-vue-next.github.io/bootstrap-vue-next/docs/components/tabs
    -->
    <div v-if="!standalone" class="content">
      <b-container fluid>
        <LoanTabs :row="effectiveRow" :productId="productId" />
      </b-container>
    </div>
    <LoanTabs v-else :row="effectiveRow" :productId="productId" />
  </component>
</template>

<script setup lang="ts">
// Layout + shared UI from Hyper UI template
import Layout from '@/components/layouts/layout.vue'
import Breadcrumb from '@/components/breadcrumb.vue'

// Centralized tab structure component
import LoanTabs from '@/views/acq_module/loanlvl/tabs/LoanTabs.vue'
// (No demo images; SnapshotTab fetches real photos from backend)

// Vue reactivity utilities
import { ref, computed, toRef, withDefaults, defineProps, watch } from 'vue'
// Centralized Axios instance
import http from '@/lib/http'

// Strongly-typed props forwarded from router or parent (e.g., when used in a modal)
const props = withDefaults(defineProps<{
  row?: Record<string, any> | null
  productId?: string | number | null
  address?: string | null
  standalone?: boolean
}>(), {
  row: null,
  productId: null,
  address: null,
  standalone: true,
})

// Breadcrumb items beneath the main layout header
const items = ref<Array<{ text: string; href?: string; to?: string; active?: boolean }>>([
  { text: 'Hyper', href: '/' },
  { text: 'Acquisitions Dashboard', to: '/acquisitions' },
  { text: 'Asset Details', active: true },
])

// Create reactive references to incoming props
const productId = toRef(props, 'productId')
const row = toRef(props, 'row')
const addressProp = toRef(props, 'address')
const standalone = toRef(props, 'standalone')

// Page title matches the previous modal header format: `{id} — {address}`
const displayTitle = computed<string>(() => {
  const rawId = productId.value
  const id = typeof rawId === 'string' || typeof rawId === 'number' ? String(rawId) : ''

  const r = row.value || {}
  const street = String((r as any)['street_address'] ?? '').trim()
  const city = String((r as any)['city'] ?? '').trim()
  const state = String((r as any)['state'] ?? '').trim()
  const zip = String((r as any)['zip'] ?? '').trim()
  const locality = [city, state].filter(Boolean).join(', ')
  // Exclude ZIP from display title per request
  const built = [street, locality].filter(Boolean).join(', ')
  const propAddr = String(addressProp?.value ?? '').trim()
  const address = built || propAddr

  if (id && address) return `${id} — ${address}`
  if (id) return id
  if (address) return address
  return ''
})

// No demo images; SnapshotTab will render a loading placeholder until fetch

// Loaded row for full-page navigation when only an id is available
const fetchedRow = ref<Record<string, any> | null>(null)

// Prefer explicit row prop when provided (e.g., in modal), otherwise fallback to fetched
const effectiveRow = computed(() => row.value ?? fetchedRow.value)

// Fetch SellerRawData by id when navigating to full-page and row is not provided
async function loadRowById(id: number) {
  try {
    const res = await http.get(`/acq/raw-data/by-id/${id}/`)
    // Return {} when not found; normalize to null to simplify downstream checks
    fetchedRow.value = res.data && Object.keys(res.data).length ? res.data : null
    console.debug('[LoanLevelIndex] loaded row for', id)
  } catch (err) {
    console.warn('[LoanLevelIndex] failed to load row for', id, err)
    fetchedRow.value = null
  }
}

// Trigger fetch when productId changes and only if a row isn't already supplied
watch(productId, (raw) => {
  const id = raw != null ? Number(raw) : NaN
  if (!row.value && Number.isFinite(id)) {
    loadRowById(id)
  }
}, { immediate: true })
</script>

<style>
/*
  Global modal sizing & layout-aware centering for loan-level dialog.
  These classes are referenced by modal wrappers via dialog/content classes.
  Keeping them here ensures the grid stays clean and the styles are centralized.
*/
.product-details-dialog {
  width: 90vw; /* 5% smaller than 98vw */
  max-width: 93.1vw !important;
  margin-left: 12%;
  margin-right: auto;
  position: relative;
  left: 0%;
}

@media (min-width: 1200px) {
  .product-details-dialog {
    width: 86vw; /* 5% smaller than 86vw */
    max-width: 90.7vw !important;
  }
}

/* Layout-aware horizontal centering over content area (excluding sidebar) */
html[data-sidenav-size='default'] .product-details-dialog {
  left: calc(var(--bs-leftbar-width) / 2);
}
html[data-sidenav-size='compact'] .product-details-dialog {
  left: calc(var(--bs-leftbar-width-md) / 2);
}
html[data-sidenav-size='condensed'] .product-details-dialog,
html[data-sidenav-size='sm-hover'] .product-details-dialog,
html[data-sidenav-size='sm-hover-active'] .product-details-dialog {
  left: calc(var(--bs-leftbar-width-sm) / 2);
}
html[data-sidenav-size='full'] .product-details-dialog,
html[data-sidenav-size='fullscreen'] .product-details-dialog {
  left: 0;
}

.product-details-content {
  height: 89.3vh; /* 5% smaller than 94vh; body still scrolls */
  display: flex;
  flex-direction: column;
  /* Match dashboard page background (Bootstrap body bg) */
  /* Colors inherit from Bootstrap utilities */
}
.product-details-content .modal-body {
  flex: 1 1 auto;
  overflow-y: auto;   /* keep vertical scroll */
  overflow-x: hidden; /* disable horizontal scroll */
  /* Fallback in case utilities are overridden: ensure body bg */
  /* Background inherits from body-class="bg-body" */
}
</style>
