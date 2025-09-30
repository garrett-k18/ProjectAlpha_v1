<template>
  <!-- AM Snapshot: Google Map card only (uses global PropertyMap component) -->
  <b-row class="g-3 px-3 px-lg-4 align-items-stretch">
    <!-- Left: Street-only View -->
    <b-col lg="6" class="d-flex">
      <div class="w-100 h-100">
        <PropertyMap
          class="w-100 h-100 d-flex flex-column"
          :row="row"
          :productId="productId"
          :height="380"
          :viewMode="'street'"
        />
      </div>
    </b-col>

    <!-- Right: Standard Map -->
    <b-col lg="6" class="d-flex">
      <div class="w-100 h-100">
        <!-- PropertyMap renders its own Hyper-style card by default (bare=false). -->
        <PropertyMap
          class="w-100 h-100 d-flex flex-column"
          :row="row"
          :productId="productId"
          :height="380"
        />
      </div>
    </b-col>
  </b-row>
</template>

<script setup lang="ts">
import { withDefaults, defineProps } from 'vue'
import PropertyMap from '@/components/PropertyMap.vue'

// Keep prop contract to avoid extraneous-prop warnings in parents that pass these.
withDefaults(defineProps<{
  row?: Record<string, any> | null
  productId?: string | number | null
  carouselWidth?: number | string
  carouselHeight?: number | string
  thumbWidth?: number | string
  thumbHeight?: number | string
}>(), {
  row: null,
  productId: null,
  carouselWidth: 500,
  carouselHeight: 280,
  thumbWidth: 120,
  thumbHeight: 90,
})
</script>
