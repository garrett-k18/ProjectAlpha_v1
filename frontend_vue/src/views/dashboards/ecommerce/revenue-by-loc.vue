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
        <BaseVectorMap id="world-map-markers" :map-height="217" :options="mapOptions"/>
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
import BaseVectorMap from "@/components/base-vector-map.vue";

export default {
  components: {BaseVectorMap},
  data() {
    return {
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
          location: 'Sydney',
          progress: 25
        },
        {
          location: 'Singapore',
          progress: 61
        },
      ],
      mapOptions: {
        map: 'world_mill_en',
        normalizeFunction: 'polynomial',
        hoverOpacity: 0.7,
        hoverColor: false,
        regionStyle: {
          initial: {
            fill: 'rgba(145, 166, 189, 0.25)'
          }
        },
        markerStyle: {
          initial: {
            r: 9,
            'fill': '#727cf5',
            'fill-opacity': 0.9,
            'stroke': '#fff',
            'stroke-width': 7,
            'stroke-opacity': 0.4
          },

          hover: {
            'stroke': '#fff',
            'fill-opacity': 1,
            'stroke-width': 1.5
          }
        },
        backgroundColor: 'transparent',
        markers: [{
          latLng: [40.71, -74.00],
          name: 'New York'
        }, {
          latLng: [37.77, -122.41],
          name: 'San Francisco'
        }, {
          latLng: [-33.86, 151.20],
          name: 'Sydney'
        }, {
          latLng: [1.3, 103.8],
          name: 'Singapore'
        }],
        zoomOnScroll: false
      }
    }
  },
  mounted() {

  }
}
</script>
