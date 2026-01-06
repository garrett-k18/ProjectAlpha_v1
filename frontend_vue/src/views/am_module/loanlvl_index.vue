<template>
  <!-- AM-specific Loan-Level wrapper -->
  <component :is="standalone ? Layout : 'div'">
    <Breadcrumb v-if="standalone" :title="displayTitle" :items="items" />
    <LoanTabs :row="effectiveRow" :assetHubId="assetHubId" />
  </component>
</template>

<script setup lang="ts">
// Layout + shared UI from Hyper UI template
import Layout from '@/components/layouts/layout.vue'
import Breadcrumb from '@/components/breadcrumb.vue'

// AM-specific tab structure component
import LoanTabs from '@/views/am_module/loanlvl/tabs/LoanTabs.vue'

import { ref, computed, toRef, watch } from 'vue'
import http from '@/lib/http'

const props = withDefaults(defineProps<{
  row?: Record<string, any> | null
  assetHubId?: string | number | null
  address?: string | null
  standalone?: boolean
}>(), {
  row: null,
  assetHubId: null,
  address: null,
  standalone: true,
})

const items = ref<Array<{ text: string; href?: string; to?: string; active?: boolean }>>([
  { text: 'Hyper', href: '/' },
  { text: 'Asset Management', to: '/asset-mgmt' },
  { text: 'Asset Details', active: true },
])

const assetHubId = toRef(props, 'assetHubId')
const row = toRef(props, 'row')
const addressProp = toRef(props, 'address')
const standalone = toRef(props, 'standalone')

const displayTitle = computed<string>(() => {
  const rawId = assetHubId.value
  const id = typeof rawId === 'string' || typeof rawId === 'number' ? String(rawId) : ''

  const r = row.value || {}
  const street = String((r as any)['street_address'] ?? '').trim()
  const city = String((r as any)['city'] ?? '').trim()
  const state = String((r as any)['state'] ?? '').trim()
  const zip = String((r as any)['zip'] ?? '').trim()
  const locality = [city, state].filter(Boolean).join(', ')
  const built = [street, locality].filter(Boolean).join(', ')
  const propAddr = String(addressProp?.value ?? '').trim()
  const address = built || propAddr

  if (id && address) return `<span class="fw-bold">${id}</span> — ${address}`
  if (id) return `<span class="fw-bold">${id}</span>`
  if (address) return address
  return ''
})

const fetchedRow = ref<Record<string, any> | null>(null)
const effectiveRow = computed(() => row.value ?? fetchedRow.value)

const emit = defineEmits<{
  'row-loaded': [row: Record<string, any>]
}>()

// AM fetch by SellerBoardedData id
async function loadRowById(id: number) {
  try {
    const res = await http.get(`/am/assets/${id}/`)
    fetchedRow.value = res.data && Object.keys(res.data).length ? res.data : null
    console.debug('[AM LoanLevelIndex] loaded row for', id)
    // Emit the fetched row to parent so modal header can use it
    if (fetchedRow.value) {
      emit('row-loaded', fetchedRow.value)
    }
  } catch (err) {
    console.warn('[AM LoanLevelIndex] failed to load row for', id, err)
    fetchedRow.value = null
  }
}

watch(assetHubId, (raw) => {
  const id = raw != null ? Number(raw) : NaN
  if (!row.value && Number.isFinite(id)) {
    loadRowById(id)
  }
}, { immediate: true })
</script>

<style>
.product-details-dialog {
  width: 90vw;
  max-width: 93.1vw !important;
  margin-left: 12%;
  margin-right: auto;
  position: relative;
  left: 0%;
}

@media (min-width: 1200px) {
  .product-details-dialog {
    width: 86vw;
    max-width: 90.7vw !important;
  }
}

html[data-sidenav-size='default'] .product-details-dialog { left: calc(var(--bs-leftbar-width) / 2); }
html[data-sidenav-size='compact'] .product-details-dialog { left: calc(var(--bs-leftbar-width-md) / 2); }
html[data-sidenav-size='condensed'] .product-details-dialog,
html[data-sidenav-size='sm-hover'] .product-details-dialog,
html[data-sidenav-size='sm-hover-active'] .product-details-dialog { left: calc(var(--bs-leftbar-width-sm) / 2); }
html[data-sidenav-size='full'] .product-details-dialog,
html[data-sidenav-size='fullscreen'] .product-details-dialog { left: 0; }

.product-details-content {
  height: 89.3vh;
  display: flex;
  flex-direction: column;
}
.product-details-content .modal-body {
  flex: 1 1 auto;
  overflow-y: auto;
  overflow-x: hidden;
}
</style>
