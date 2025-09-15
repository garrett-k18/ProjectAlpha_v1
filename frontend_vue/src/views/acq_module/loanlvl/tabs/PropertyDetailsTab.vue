<template>
  <div class="px-3 px-lg-4">
    <div class="row g-3">
      <!-- Property Details Card -->
      <div class="col-12 col-lg-6 col-xl-4">
        <PropertyDetails :row="row" :productId="productId" />
      </div>

      <!-- Demographics Grid Card -->
      <div class="col-12 col-lg-6 col-xl-4">
        <DemographicsGrid :row="row" :productId="productId" />
      </div>

      <!-- Empty Card 3: 1:1 square -->
      <div class="col-12 col-lg-6 col-xl-4">
        <div class="card h-100 d-flex flex-column">
          <div class="card-body d-flex flex-column p-0" style="height: 500px;">
            <!-- Embedded Google Map (same data source as Snapshot) -->
            <PropertyMap class="h-100 d-flex flex-column" bare :row="row" :productId="productId" height="100%" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { withDefaults, defineProps } from 'vue'
// Import components
import PropertyMap from '@/1_global/components/PropertyMap.vue'
import PropertyDetails from '@/views/acq_module/loanlvl/components/propertydetails.vue'
import DemographicsGrid from '@/views/acq_module/loanlvl/components/DemographicsGrid.vue'

// Keep props consistent with other tabs so parent can pass row/productId
withDefaults(defineProps<{
  row?: Record<string, any> | null
  productId?: string | number | null
}>(), {
  row: null,
  productId: null,
})
</script>