<template>
  <div class="card">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Sessions by country</h4>
      <div class="float-end">
        <b-dropdown toggle-class="arrow-none card-drop p-0" variant="black" right>
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
          <BaseVectorMap id="world-map-markers" class="mt-3 mb-3" :map-height="300" :options="mapOptions"/>
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

export default {
  components: {BaseApexChart, BaseVectorMap},
  data() {
    return {
      mapOptions: {
        map: 'world_mill_en',
        normalizeFunction: 'polynomial',
        hoverOpacity: 0.7,
        hoverColor: false,
        regionStyle: {
          initial: {
            fill: '#91a6bd40'
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
        zoomOnScroll: false
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
              formatter: function (val) {
                return val + "%";
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
