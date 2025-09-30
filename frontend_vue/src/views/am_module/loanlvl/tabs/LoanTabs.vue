<template>
  <!-- AM LoanTabs: mirrors acquisitions tab structure, but can diverge safely -->
  <b-tabs nav-class="nav-bordered mb-3" content-class="pt-0">
    <b-tab title="Snapshot" active>
      <SnapshotTab :row="row" :productId="productId" />
    </b-tab>

    <b-tab title="Asset Management">
      <AssetManagementTab :row="row" :productId="productId" />
    </b-tab>

    <b-tab title="Servicing">
      <ServicingTab :row="row" :productId="productId" />
    </b-tab>

    <b-tab title="Property Details">
      <PropertyDetailsTab :row="row" :productId="productId" />
    </b-tab>

    <b-tab title="Documents">
      <DocumentsTab :row="row" :productId="productId" />
    </b-tab>
    
    <b-tab title="Performance">
      <PerformanceTab :row="row" :productId="productId" />
    </b-tab>
  </b-tabs>
</template>

<script setup lang="ts">
import { defineAsyncComponent, withDefaults, defineProps } from 'vue'

withDefaults(defineProps<{ row?: Record<string, any> | null; productId?: string | number | null }>(), {
  row: null,
  productId: null,
})

const SnapshotTab = defineAsyncComponent(() => import('./SnapshotTab.vue'))
const ServicingTab = defineAsyncComponent(() => import('./ServicingTab.vue'))
const PropertyDetailsTab = defineAsyncComponent(() => import('./PropertyDetailsTab.vue'))
const AssetManagementTab = defineAsyncComponent(() => import('./AssetManagement.vue'))
const DocumentsTab = defineAsyncComponent(() => import('./DocumentsTab.vue'))
const PerformanceTab = defineAsyncComponent(() => import('./PerformanceTab.vue'))
</script>
