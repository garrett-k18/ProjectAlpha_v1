<template>
  <!-- AM Property Details Tab -->
  <b-row class="g-3 g-lg-4 px-3 px-lg-4">
    <b-col lg="12" class="d-flex">
      <PropertyDetails class="w-100" :row="row" :assetHubId="assetHubId" />
    </b-col>
  </b-row>
</template>

<script setup lang="ts">
import { withDefaults, defineProps } from 'vue'
// Reuse existing propertydetails component which renders from provided row
import PropertyDetails from '@/views/acq_module/loanlvl/components/propertydetails.vue'

withDefaults(defineProps<{ row?: Record<string, any> | null; assetHubId?: string | number | null }>(), {
  row: null,
  assetHubId: null,
})
</script>
