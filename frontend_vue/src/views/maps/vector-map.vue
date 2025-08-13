<template>
  <Layout>
    <Breadcrumb :title="title" :items="items"/>

    <b-row>
      <b-col cols="12">
        <div class="card">
          <div class="card-body">
            <h4 class="header-title mb-3">World Vector Map</h4>
            <BaseVectorMap id="world-map-markers" :map-height="360" :options="worldMapOption"/>
          </div> <!-- end card-body-->
        </div> <!-- end card-->
      </b-col> <!-- end col-->
    </b-row>
    <!-- end row-->

    <b-row>
      <b-col xl="6">
        <div class="card">
          <div class="card-body">
            <h4 class="header-title mb-3">USA Vector Map</h4>
            <BaseVectorMap id="usa-vectormap" :map-height="300" :options="usaMapOption"/>
          </div> <!-- end card-body-->
        </div> <!-- end card-->
      </b-col> <!-- end col-->
      <b-col xl="6">
        <div class="card">
          <div class="card-body">
            <h4 class="header-title mb-3">India Vector Map</h4>
            <BaseVectorMap id="india-vectormap" :map-height="300" :options="indiaMapOption"/>
          </div> <!-- end card-body-->
        </div> <!-- end card-->
      </b-col> <!-- end col-->
    </b-row>
    <!-- end row-->

    <b-row>
      <b-col xl="6">
        <div class="card">
          <div class="card-body">
            <h4 class="header-title mb-3">Australia Vector Map</h4>
            <BaseVectorMap id="australia-vectormap" :map-height="300" :options="ausMapOption"/>
          </div> <!-- end card-body-->
        </div> <!-- end card-->
      </b-col> <!-- end col-->
      <b-col xl="6">
        <div class="card">
          <div class="card-body">
            <h4 class="header-title mb-3">Chicago Vector Map</h4>
            <BaseVectorMap id="chicago-vectormap" :map-height="300" :options="chicagoMapOption"/>
          </div> <!-- end card-body-->
        </div> <!-- end card-->
      </b-col> <!-- end col-->
    </b-row>
    <!-- end row-->

    <b-row>
      <b-col xl="6">
        <div class="card">
          <div class="card-body">
            <h4 class="header-title mb-3">UK Vector Map</h4>
            <BaseVectorMap id="uk-vectormap" :map-height="300" :options="ukMapOption"/>
          </div> <!-- end card-body-->
        </div> <!-- end card-->
      </b-col> <!-- end col-->
      <b-col xl="6">
        <div class="card">
          <div class="card-body">
            <h4 class="header-title mb-3">Canada Vector Map</h4>
            <BaseVectorMap id="canada-vectormap" :map-height="300" :options="canadaMapOption"/>
          </div> <!-- end card-body-->
        </div> <!-- end card-->
      </b-col> <!-- end col-->
    </b-row>
    <!-- end row-->

    <b-row>
      <b-col xl="6">
        <div class="card">
          <div class="card-body">
            <h4 class="header-title mb-3">Europe Vector Map</h4>
            <BaseVectorMap id="europe-vectormap" :map-height="300" :options="europeMapOption"/>
          </div> <!-- end card-body-->
        </div> <!-- end card-->
      </b-col> <!-- end col-->
      <b-col xl="6">
        <div class="card">
          <div class="card-body">
            <h4 class="header-title mb-3">France Vector Map</h4>
            <BaseVectorMap id="france-vectormap" :map-height="300" :options="franceMapOption"/>
          </div> <!-- end card-body-->
        </div> <!-- end card-->
      </b-col> <!-- end col-->
    </b-row>
    <!-- end row-->

    <b-row>
      <b-col xl="6">
        <div class="card">
          <div class="card-body">
            <h4 class="header-title mb-3">Spain Vector Map</h4>
            <BaseVectorMap id="spain-vectormap" :map-height="300" :options="spainMapOption"/>
          </div> <!-- end card-body-->
        </div> <!-- end card-->
      </b-col> <!-- end col-->
      <b-col xl="6">
        <div class="card">
          <div class="card-body">
            <h4 class="header-title mb-3">Spain Vector Map</h4>
            <BaseVectorMap id="spain2-vectormap" :map-height="300" :options="spain2MapOption"/>
          </div> <!-- end card-body-->
        </div> <!-- end card-->
      </b-col> <!-- end col-->
    </b-row>
    <!-- end row-->

  </Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";
import BaseVectorMap from "@/components/base-vector-map.vue";

export default {
  components: {BaseVectorMap, Breadcrumb, Layout},
  data() {
    return {
      title: 'Vector Maps',
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
          text: 'Vector Maps',
          active: true,
        },
      ],

      worldMapOption: {
        map: 'world_mill_en',
        normalizeFunction: 'polynomial',
        hoverOpacity: 0.7,
        hoverColor: false,
        regionStyle: {
          initial: {
            fill: '#91a6bd40'
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
          latLng: [41.90, 12.45],
          name: 'Vatican City'
        }, {
          latLng: [43.73, 7.41],
          name: 'Monaco'
        }, {
          latLng: [-0.52, 166.93],
          name: 'Nauru'
        }, {
          latLng: [-8.51, 179.21],
          name: 'Tuvalu'
        }, {
          latLng: [43.93, 12.46],
          name: 'San Marino'
        }, {
          latLng: [47.14, 9.52],
          name: 'Liechtenstein'
        }, {
          latLng: [7.11, 171.06],
          name: 'Marshall Islands'
        }, {
          latLng: [17.3, -62.73],
          name: 'Saint Kitts and Nevis'
        }, {
          latLng: [3.2, 73.22],
          name: 'Maldives'
        }, {
          latLng: [35.88, 14.5],
          name: 'Malta'
        }, {
          latLng: [12.05, -61.75],
          name: 'Grenada'
        }, {
          latLng: [13.16, -61.23],
          name: 'Saint Vincent and the Grenadines'
        }, {
          latLng: [13.16, -59.55],
          name: 'Barbados'
        }, {
          latLng: [17.11, -61.85],
          name: 'Antigua and Barbuda'
        }, {
          latLng: [-4.61, 55.45],
          name: 'Seychelles'
        }, {
          latLng: [7.35, 134.46],
          name: 'Palau'
        }, {
          latLng: [42.5, 1.51],
          name: 'Andorra'
        }, {
          latLng: [14.01, -60.98],
          name: 'Saint Lucia'
        }, {
          latLng: [6.91, 158.18],
          name: 'Federated States of Micronesia'
        }, {
          latLng: [1.3, 103.8],
          name: 'Singapore'
        }, {
          latLng: [0.33, 6.73],
          name: 'SÃ£o TomÃ© and PrÃ­ncipe'
        }]
      },
      usaMapOption:{
        map: 'us_merc_en',
        backgroundColor: 'transparent',
        regionStyle: {
          initial: {
            fill: '#727cf5'
          }
        }
      },
      indiaMapOption:{
        map: 'in_mill_en',
        backgroundColor: 'transparent',
        regionStyle: {
          initial: {
            fill: '#6c757d'
          }
        }
      },
      ausMapOption:{
        map: 'au_mill_en',
        backgroundColor: 'transparent',
        regionStyle: {
          initial: {
            fill: '#0acf97'
          }
        }
      },
      chicagoMapOption:{
        map: 'us-il-chicago_mill_en',
        backgroundColor: 'transparent',
        regionStyle: {
          initial: {
            fill: '#39afd1'
          }
        }
      },
      ukMapOption:{
        map: 'uk_mill_en',
        backgroundColor: 'transparent',
        regionStyle: {
          initial: {
            fill: '#fa5c7c'
          }
        }
      },
      canadaMapOption:{
        map: 'ca_lcc_en',
        backgroundColor: 'transparent',
        regionStyle: {
          initial: {
            fill: '#ffbc00'
          }
        }
      },
      europeMapOption:{
        map: 'europe_mill_en',
        backgroundColor: 'transparent',
        regionStyle: {
          initial: {
            fill: '#727cf5'
          }
        }
      },
      franceMapOption:{
        map: 'fr_merc_en',
        backgroundColor: 'transparent',
        regionStyle: {
          initial: {
            fill: '#0acf97'
          }
        }
      },
      spainMapOption:{
        map: 'es_merc',
        backgroundColor: 'transparent',
        regionStyle: {
          initial: {
            fill: '#39afd1'
          }
        }
      },
      spain2MapOption:{
        map: 'es_mill',
        backgroundColor: 'transparent',
        regionStyle: {
          initial: {
            fill: '#6c757d'
          }
        }
      }
    }
  }

}
</script>
