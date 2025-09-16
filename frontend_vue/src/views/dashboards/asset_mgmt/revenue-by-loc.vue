<template>
  <div class="card">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Revenue By Location</h4>
      <div class="float-end">
        <!-- Using 'dark' variant instead of 'black' as per BootstrapVue valid variants -->
        <b-dropdown toggle-class="arrow-none card-drop p-0" variant="dark" right>
          <template v-slot:button-content>
            <i class="mdi mdi-dots-vertical"></i>
          </template>
          <b-dropdown-item href="javascript:void(0);">Sales Report</b-dropdown-item>
          <b-dropdown-item href="javascript:void(0);">Export Report</b-dropdown-item>
          <b-dropdown-item href="javascript:void(0);">Profit</b-dropdown-item>
          <b-dropdown-item href="javascript:void(0);">Action</b-dropdown-item>
        </b-dropdown>
      </div>
    </div>

    <div class="card-body py-0">
      <div class="mb-4 mt-3">
        <!-- US-focused map with markers for each location -->
        <VectorMap 
          id="us-revenue-map" 
          :map-height="217" 
          :location-data="locationData"
          :marker-color="'#727cf5'"
        />
      </div>

      <div v-for="(loc,index) in locationData" :key="index">
        <h5 class="mb-1 mt-0 fw-normal">{{ loc.location }}</h5>
        <div class="progress-w-percent ">
          <span class="progress-value fw-bold">{{ loc.progress }}k </span>
          <div class="progress progress-sm">
            <div class="progress-bar" role="progressbar" :style="`width: ${loc.progress}%;`"
                 :aria-valuenow="loc.progress" aria-valuemin="0"
                 aria-valuemax="100"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import VectorMap from "./vectorMap.vue";

export default defineComponent({
  name: 'RevenueByLocation',
  components: { VectorMap },
  data() {
    return {
      // Location data with US locations (to display on the US map)
      locationData: [
        {
          location: 'New York',
          progress: 72
        },
        {
          location: 'San Francisco',
          progress: 39
        },
        {
          location: 'Chicago',
          progress: 48
        },
        {
          location: 'Boston',
          progress: 61
        },
        {
          location: 'Los Angeles',
          progress: 54
        },
      ],
    }
  },
});
</script>
