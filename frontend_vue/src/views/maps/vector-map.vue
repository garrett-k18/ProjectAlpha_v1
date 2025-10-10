<template>
  <Layout>
    <Breadcrumb :title="title" :items="items"/>

    <b-row>
      <b-col cols="12">
        <div class="card">
          <div class="card-body">
            <h4 class="header-title mb-3">United States Map</h4>
            <p class="text-muted">Includes all 50 states including Alaska and Hawaii</p>
            <BaseVectorMap id="usa-vectormap" :map-height="500" :options="usaMapOption"/>
          </div> <!-- end card-body-->
        </div> <!-- end card-->
      </b-col> <!-- end col-->
    </b-row>
    <!-- end row-->

  </Layout>
</template>

<script lang="ts">
/**
 * US Vector Map Component
 * Displays a clean interactive map of the United States including Alaska and Hawaii
 * Uses jsVectorMap library with us_merc_en map projection
 */
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";
import BaseVectorMap from "@/components/base-vector-map.vue";

export default {
  components: { BaseVectorMap, Breadcrumb, Layout },
  data() {
    return {
      // Page title and breadcrumb navigation
      title: 'US Map',
      items: [
        {
          text: 'Hyper',
          href: '/',
        },
        {
          text: 'Maps',
          href: '/',
        },
        {
          text: 'US Map',
          active: true,
        },
      ],
      
      // US Map configuration using dedicated US map (us_mill_en)
      // Shows all 50 states including Alaska and Hawaii in insets
      usaMapOption: {
        map: 'us_mill_en', // US Miller projection with AK and HI insets
        backgroundColor: 'transparent',
        zoomOnScroll: true, // Allow zoom with scroll wheel
        zoomButtons: true, // Show zoom controls
        regionStyle: {
          initial: {
            fill: '#727cf5', // Primary purple color from Hyper UI theme
            stroke: '#ffffff',
            'stroke-width': 1,
            'fill-opacity': 0.85
          },
          hover: {
            fill: '#5a67d8', // Darker purple on hover
            'fill-opacity': 1
          },
          selected: {
            fill: '#4c51bf', // Even darker when selected
            'stroke-width': 2
          }
        }
      }
    }
  }
}
</script>
