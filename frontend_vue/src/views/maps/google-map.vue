<template>
  <Layout>
    <Breadcrumb :title="title" :items="items"/>
    <b-row>
      <b-col lg="6">
        <div class="card">
          <div class="card-body">
            <h4 class="header-title mb-3">Basic Google Map</h4>
            <!-- basic map -->
            <GoogleMap :api-key="api" :center="{ lat: 2, lng: 2 }" :zoom="5" style="height: 300px"></GoogleMap>
          </div>
        </div>
      </b-col>
      <b-col lg="6">
        <div class="card">
          <div class="card-body">
            <h4 class="header-title mb-3">Markers Google Map</h4>
            <!-- Map with markers -->
            <GoogleMap :api-key="api" :center="{ lat: 11, lng: 12 }" :zoom="3" style="height: 300px">
              <Marker
                  v-for="(m, index) in markers"
                  :key="index"
                  :options="m.markerOptions"
                  :clickable="true"
                  :draggable="true"
              ></Marker>
            </GoogleMap>
          </div>
        </div>
      </b-col>
    </b-row>

    <b-row>
      <b-col lg="6">
        <div class="card">
          <div class="card-body">
            <h4 class="header-title mb-3">Polygon Editing</h4>
            <!-- Polygon editiong map -->
            <GoogleMap :api-key="api" :center="{ lat: 1.38, lng: 103.8 }" :zoom="12" style="height: 300px">
              <Polygon :paths="paths" :editable="true" @paths_changed="updateEdited($event)"></Polygon>
            </GoogleMap>
          </div>
          <!-- end card-body -->
        </div>
        <!-- end card -->
      </b-col>
      <!-- end col -->
      <b-col lg="6">
        <div class="card">
          <div class="card-body">
            <h4 class="header-title mb-3">Map type</h4>
            <!-- Set map type -->
            <GoogleMap :api-key="api"
                :center="{ lat: 4, lng: 4 }"
                :zoom="3"
                style="height: 300px"
                map-type-id="terrain"
            ></GoogleMap>
          </div>
          <!-- end card-body -->
        </div>
        <!-- end card -->
      </b-col>
      <!-- end col -->
    </b-row>
    <!-- end row -->
  </Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";

import {GoogleMap, Marker, Polygon} from "vue3-google-map";

export default {

  components: {Layout, Breadcrumb, GoogleMap, Marker, Polygon},
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
      api:'',
      markers: [
        {
          markerOptions: {position: {lat: 10.0, lng: 10.0}, label: "Hi", title: "Hello from marker"}
        },
      ],
      pov: null,
      pano: null,
      edited: [[{lat:0, lng: 0}]],
      paths: [
        [
          {lat: 1.38, lng: 103.8},
          {lat: 1.38, lng: 103.81},
          {lat: 1.39, lng: 103.81},
          {lat: 1.39, lng: 103.8},
        ],
        [
          {lat: 1.382, lng: 103.802},
          {lat: 1.382, lng: 103.808},
          {lat: 1.388, lng: 103.808},
          {lat: 1.388, lng: 103.802},
        ],
      ],
    }
  },
  methods: {
    /**
     * street view data update
     */
    updatePov(pov:any) {
      this.pov = pov
    },
    /**
     * street view data update
     */
    updatePano(pano:any) {
      this.pano = pano
    },
    /**
     * polygon editing
     */
    updateEdited(mvcArray:any) {
      let paths = []
      for (let i = 0; i < mvcArray.getLength(); i++) {
        let path = []
        for (let j = 0; j < mvcArray.getAt(i).getLength(); j++) {
          let point = mvcArray.getAt(i).getAt(j)
          path.push({lat: point.lat(), lng: point.lng()})
        }
        paths.push(path)
      }
      this.edited = paths
    },
  },
}
</script>