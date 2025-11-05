<template>
  <!--
    NeighborhoodInsights.vue
    - Displays neighborhood quality metrics and nearby amenities
    - Shows School Rating, Walk Score, Transit Score, and Bike Score
    - Lists nearby amenities with distances
    - Uses Bootstrap/Hyper UI card pattern
  -->
  <div class="card">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title mb-0">Neighborhood Insights</h4>
      <span class="badge bg-info-subtle text-info">Local Data</span>
    </div>
    <div class="card-body">
      <div class="row g-3">
        <div class="col-6">
          <div class="text-center p-2 bg-light rounded">
            <i class="mdi mdi-school fs-2 text-primary"></i>
            <h6 class="mb-0 mt-2 small text-muted">School Rating</h6>
            <h4 class="mb-0 text-primary">8.5/10</h4>
          </div>
        </div>
        <div class="col-6">
          <div class="text-center p-2 bg-light rounded">
            <i class="mdi mdi-walk fs-2 text-success"></i>
            <h6 class="mb-0 mt-2 small text-muted">Walk Score</h6>
            <h4 class="mb-0 text-success">72</h4>
          </div>
        </div>
        <div class="col-6">
          <div class="text-center p-2 bg-light rounded">
            <i class="mdi mdi-car fs-2 text-warning"></i>
            <h6 class="mb-0 mt-2 small text-muted">Transit Score</h6>
            <h4 class="mb-0 text-warning">45</h4>
          </div>
        </div>
        <div class="col-6">
          <div class="text-center p-2 bg-light rounded">
            <i class="mdi mdi-bike fs-2 text-info"></i>
            <h6 class="mb-0 mt-2 small text-muted">Bike Score</h6>
            <h4 class="mb-0 text-info">58</h4>
          </div>
        </div>
      </div>
      <div class="mt-3">
        <h6 class="text-muted mb-2">Nearby Amenities</h6>
        <div class="d-flex flex-wrap gap-1">
          <span class="badge bg-light text-dark" v-for="amenity in nearbyAmenities" :key="amenity">
            <i class="mdi mdi-map-marker"></i> {{ amenity }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * NeighborhoodInsights.vue
 * 
 * Displays neighborhood quality scores and nearby amenities.
 * Includes walkability, transit, school ratings, and local points of interest.
 * TODO: Wire to backend neighborhood data API when available.
 */
import { computed, withDefaults } from 'vue'

// Props definition
const props = withDefaults(defineProps<{
  row?: Record<string, any> | null
  assetId?: string | number | null
}>(), {
  row: null,
  assetId: null,
})

// Neighborhood Insights - Nearby amenities
const nearbyAmenities = computed(() => [
  'Grocery Store (0.5 mi)',
  'Elementary School (0.8 mi)',
  'Park (0.3 mi)',
  'Hospital (2.1 mi)',
  'Shopping Center (1.2 mi)'
])
</script>
