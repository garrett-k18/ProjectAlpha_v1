<template>
  <!-- AM LoanTabs: mirrors acquisitions tab structure, but can diverge safely -->
  <b-tabs nav-class="nav-bordered mb-3" content-class="pt-0">
    <b-tab title="Snapshot" active>
      <SnapshotTab :row="row" :productId="productId" />
    </b-tab>

    <b-tab title="Loan Details">
      <LoanDetailsTab :row="row" :productId="productId" />
    </b-tab>

    <b-tab title="Property Details">
      <PropertyDetailsTab :row="row" :productId="productId" />
    </b-tab>

    <b-tab title="Acquisition Analysis">
      <AcquisitionAnalysisTab :row="row" :productId="productId" />
    </b-tab>

    <b-tab title="Documents">
      <DocumentsTab :row="row" :productId="productId" />
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
const LoanDetailsTab = defineAsyncComponent(() => import('./LoanDetailsTab.vue'))
const PropertyDetailsTab = defineAsyncComponent(() => import('./PropertyDetailsTab.vue'))
const AcquisitionAnalysisTab = defineAsyncComponent(() => import('./AcquisitionAnalysisTab.vue'))
const DocumentsTab = defineAsyncComponent(() => import('./DocumentsTab.vue'))
</script>
