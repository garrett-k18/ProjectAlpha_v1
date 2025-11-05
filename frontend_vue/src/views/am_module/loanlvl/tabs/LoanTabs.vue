<template>
  <!-- AM LoanTabs: mirrors acquisitions tab structure, but can diverge safely -->
  <b-tabs nav-class="nav-bordered mb-3" content-class="pt-0">
    <b-tab title="Snapshot" active>
      <SnapshotTab :row="row" :assetHubId="assetHubId" />
    </b-tab>

    <b-tab title="Asset Management">
      <AssetManagementTab :row="row" :assetHubId="assetHubId" />
    </b-tab>

    <b-tab title="Servicing">
      <ServicingTab :row="row" :assetHubId="assetHubId" />
    </b-tab>

    <b-tab title="Property Details">
      <PropertyDetailsTab :row="row" :assetHubId="assetHubId" />
    </b-tab>

    <b-tab title="Documents">
      <DocumentsTab :row="row" :assetHubId="assetHubId" />
    </b-tab>
    
    <b-tab title="Performance">
      <PerformanceTab :row="row" :assetHubId="assetHubId" />
    </b-tab>

    <b-tab title="Narrative">
      <NarrativeTab :row="row" :assetHubId="assetHubId" />
    </b-tab>
  </b-tabs>
</template>

<script setup lang="ts">
import { defineAsyncComponent, withDefaults, defineProps } from 'vue'

withDefaults(defineProps<{ row?: Record<string, any> | null; assetHubId?: string | number | null }>(), {
  row: null,
  assetHubId: null,
})

const SnapshotTab = defineAsyncComponent(() => import('./SnapshotTab.vue'))
const ServicingTab = defineAsyncComponent(() => import('./ServicingTab.vue'))
const PropertyDetailsTab = defineAsyncComponent(() => import('./PropertyDetailsTab.vue'))
const AssetManagementTab = defineAsyncComponent(() => import('./AssetManagement.vue'))
const DocumentsTab = defineAsyncComponent(() => import('./DocumentsTab.vue'))
const PerformanceTab = defineAsyncComponent(() => import('./PerformanceTab.vue'))
const NarrativeTab = defineAsyncComponent(() => import('./NarrativeTab.vue'))
</script>
