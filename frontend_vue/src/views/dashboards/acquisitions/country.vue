<template>
  <div class="card">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">State Strats</h4>
      <div class="float-end">
        <b-dropdown toggle-class="arrow-none card-drop p-0" variant="dark" right>
          <template v-slot:button-content>
            <i class="mdi mdi-dots-vertical"></i>
          </template>
          <b-dropdown-item href="javascript:void(0);">Refresh Report</b-dropdown-item>
          <b-dropdown-item href="javascript:void(0);">Export Report</b-dropdown-item>
        </b-dropdown>
      </div>
    </div>

    <div class="card-body pt-0">
      <b-row>
        <b-col lg="8">
          <BaseVectorMap
            id="world-map-markers"
            class="mt-3 mb-3"
            :map-height="300"
            :options="mapOptions"
            :markers="vectorMarkers"
          />
        </b-col>
        <b-col lg="4" dir="ltr">
          <BaseApexChart :height="320" :series="countryChart.series" :options="countryChart.options"/>
        </b-col>
      </b-row>
    </div>
  </div>

</template>

<script lang="ts">
import BaseVectorMap from "@/components/base-vector-map.vue";
import BaseApexChart from "@/components/base-apex-chart.vue";
import { useAcqSelectionsStore } from "@/stores/acqSelections";

export default {
  components: {BaseApexChart, BaseVectorMap},
  // Use setup to access Pinia in Options API component
  // Docs reviewed:
  // - Pinia usage: https://pinia.vuejs.org/core-concepts/
  // - Vue Options API with setup: https://vuejs.org/api/options-state.html#setup
  setup() {
    const acqStore = useAcqSelectionsStore()
    // Expose vectorMarkers (computed Ref from the store). Vue unwraps Refs in templates.
    return { vectorMarkers: acqStore.vectorMarkers }
  },
  data() {
    return {
      mapOptions: {
        map: 'us_merc_en',
        normalizeFunction: 'polynomial',
        hoverOpacity: 0.7,
        hoverColor: false,
        regionStyle: {
          initial: {
            fill: '#91a6bd40'
          }
        },
        // Make markers large and high-contrast so they are clearly visible.
        // jVectorMap docs: https://jvectormap.com/documentation/javascript-api/
        markerStyle: {
          initial: {
            // radius of the marker circle (default is ~5). Increase to make it huge/visible
            r: 4,
            // bright fill color for visibility against muted map colors
            fill: '#e83e8c',
            // white stroke for contrast on any background
            stroke: '#ffffff',
            // stroke width to outline the marker clearly
            'stroke-width': 2,
            // ensure marker is fully opaque
            'fill-opacity': 1
          },
          hover: {
            // subtle hover change
            fill: '#ff6fa8',
            'stroke-width': 2
          },
          selected: {
            // selection color
            fill: '#d63384'
          }
        },
        series: {
          regions: [{
            values: {
              "KR": "#91a6bd40",
              "CA": "#b3c3ff",
              "GB": "#809bfe",
              "NL": "#4d73fe",
              "IT": "#1b4cfe",
              "FR": "#727cf5",
              "JP": "#e7fef7",
              "US": "#e7e9fd",
              "CN": "#8890f7",
              "IN": "#727cf5",
            }, attribute: 'fill'
          }]
        },
        backgroundColor: 'transparent',
        zoomOnScroll: false,
        // Allow selecting markers (visual feedback)
        markersSelectable: true
      },
      countryChart: {
        series: [{
          name: 'Sessions',
          data: [90, 75, 60, 50, 45, 36, 28, 20, 15, 12]
        }],
        options: {
          chart: {
            type: 'bar',
            height: 320,
            toolbar: {
              show: false,
            },
          },
          plotOptions: {
            bar: {
              horizontal: true,
            }
          },
          colors: ['#727cf5'],
          dataLabels: {
            enabled: false
          },
          xaxis: {
            categories: ["India", "China", "United States", "Japan", "France", "Italy", "Netherlands", "United Kingdom", "Canada", "South Korea"],
            axisBorder: {
              show: false,
            },
            labels: {
              formatter: function (val: number | string) {
                return String(val) + "%";
              }
            }
          },
          grid: {
            strokeDashArray: [5]
          }
        }
      }
    }
  }
}
</script>
