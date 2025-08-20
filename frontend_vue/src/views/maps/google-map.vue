<template>
  <Layout>
    <Breadcrumb :title="title" :items="items"/>
    <b-row>
      <b-col lg="12">
        <div class="card">
          <div class="card-body">
            <h4 class="header-title mb-3">Basic Google Map</h4>
            <!-- basic map -->
            <GoogleMap :api-key="api" :center="{ lat: 2, lng: 2 }" :zoom="5" style="height: 300px"></GoogleMap>
          </div>
        </div>
      </b-col>
    </b-row>
    <!-- end row -->
  </Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";

import {GoogleMap} from "vue3-google-map";

export default {

  components: {Layout, Breadcrumb, GoogleMap},
  data() {
    return {
      title: 'Google Maps',
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
          text: 'Google Maps',
          active: true,
        },
      ],
      // Read key from Vite env per vue3-google-map docs
      api: import.meta.env.VITE_GOOGLE_MAPS_API_KEY || '',
    }
  },
  methods: {},
}
</script>