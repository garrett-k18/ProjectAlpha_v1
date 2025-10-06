<template>
  <!--
    LoanTabs
    - Encapsulates the tabbed UI used by the acquisitions modal and the loan-level pages
    - Keeps the AG Grid view lean by outsourcing tab structure and async loading here
    - Uses BootstrapVue Next tabs per docs: https://bootstrap-vue-next.github.io/bootstrap-vue-next/docs/components/tabs
  -->
  <b-tabs
    nav-class="nav-bordered mb-3"      
    content-class="pt-0"               
  >
    <!-- Snapshot (default active) -->
    <b-tab title="Snapshot" active>
      <!-- SnapshotTab now fetches its own photos; module selects API base (acq|am) -->
      <SnapshotTab :row="row" :assetId="assetId" :module="module" />
    </b-tab>

    <!-- Loan Details -->
    <b-tab title="Loan Details">
      <LoanDetailsTab :row="row" :assetId="assetId" :module="module" />
    </b-tab>

    <!-- Property Details -->
    <b-tab title="Property Details">
      <PropertyDetailsTab :row="row" :assetId="assetId" :module="module" />
    </b-tab>

    <!-- Acquisition Analysis -->
    <b-tab title="Acquisition Analysis">
      <AcquisitionAnalysisTab :row="row" :assetId="assetId" :module="module" />
    </b-tab>

    <!-- Commercial Analysis (conditional) -->
    <b-tab v-if="isCommercial" title="Commercial Analysis">
      <CommercialAnalysisTab :row="row" :assetId="assetId" :module="module" />
    </b-tab>

    <!-- Documents -->
    <b-tab title="Documents">
      <DocumentsTab :row="row" :assetId="assetId" :module="module" />
    </b-tab>
  </b-tabs>
</template>

<script setup lang="ts">
// -----------------------------------------------------------------------------------
// LoanTabs.vue
// -----------------------------------------------------------------------------------
// Responsibility:
// - Centralizes the tab template/structure for loan-level details
// - Lazy-loads each tab component for performance (Vue 3 async components)
// - Provides a single, reusable component that can be rendered in a modal or page
// -----------------------------------------------------------------------------------

import { defineAsyncComponent } from 'vue'
import { computed } from 'vue'

// Define props for strong typing and reusability
// - row: the active row object (nullable)
// - assetId: Asset Hub ID for the current asset (nullable)
// - module: selects the API module ('acq' | 'am') for child tabs
// These props are forwarded to the tab components.
const props = defineProps<{
  row: Record<string, unknown> | null
  assetId: string | number | null
  module?: 'acq' | 'am'
}>()

console.log('[LoanTabs] received assetId=', props.assetId, 'row.id=', (props.row as any)?.id)

// -----------------------------------------------------------------------------------
// Lazy-load tab content components per Vue documentation:
// https://vuejs.org/guide/components/async.html
// Using relative paths since this file lives in the same folder as the tabs.
// -----------------------------------------------------------------------------------
const SnapshotTab = defineAsyncComponent(() => import('./SnapshotTab.vue'))
const LoanDetailsTab = defineAsyncComponent(() => import('./LoanDetailsTab.vue'))
const PropertyDetailsTab = defineAsyncComponent(() => import('./PropertyDetailsTab.vue'))
const AcquisitionAnalysisTab = defineAsyncComponent(() => import('./AcquisitionAnalysisTab.vue'))
const DocumentsTab = defineAsyncComponent(() => import('./DocumentsTab.vue'))
const CommercialAnalysisTab = defineAsyncComponent(() => import('./CommercialAnalysisTab.vue'))

// Determine if the asset should show the Commercial Analysis tab.
// Priority: use backend-provided boolean flags on the row to avoid extra requests.
// Supported keys:
// - row.is_commercial (preferred)
// - row.is_commercial_flag (fallback naming)
// - row.asset_hub_is_commercial (if serializer flattened under a different name)
const isCommercial = computed<boolean>(() => {
  const r = props.row as any
  if (!r) return false
  // 1) Prefer backend-provided booleans
  if (typeof r.is_commercial === 'boolean') return r.is_commercial
  if (typeof r.is_commercial_flag === 'boolean') return r.is_commercial_flag
  if (typeof r.asset_hub_is_commercial === 'boolean') return r.asset_hub_is_commercial
  // 2) Fallback: infer from SRD standardized tags on the row
  const pt = r.property_type as string | undefined
  const prod = r.product_type as string | undefined
  const commercialPT = new Set(['Multifamily 5+', 'Industrial', 'Mixed Use'])
  if (pt && commercialPT.has(pt)) return true
  if (prod === 'Commercial') return true
  return false
})
</script>

<style scoped>
/* Keep styles minimal; rely on global/Hyper UI styles and Bootstrap classes */
</style>
