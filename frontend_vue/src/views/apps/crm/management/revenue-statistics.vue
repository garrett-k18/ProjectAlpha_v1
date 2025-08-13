<template>
  <div class="card">
    <div class="card-header d-flex justify-content-between align-items-center">
      <h4 class="header-title">Revenue Statistics</h4>

      <b-dropdown class="float-end" variant="white" right toggle-tag="a" toggle-class="arrow-none p-0">
        <template v-slot:button-content>
          <i class="mdi mdi-dots-vertical"></i>
        </template>
        <b-dropdown-item href="javascript: void(0);">Today</b-dropdown-item>
        <b-dropdown-item href="javascript: void(0);">Yesterday</b-dropdown-item>
        <b-dropdown-item href="javascript: void(0);">Last Week</b-dropdown-item>
        <b-dropdown-item href="javascript: void(0);">Last Month</b-dropdown-item>
      </b-dropdown>

    </div>

    <div class="card-body pt-0">
      <div dir="ltr">
        <BaseApexChart class="apex-charts" :height="367" :series="statisticsChart.series" :options="statisticsChart.options"/>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import BaseApexChart from "@/components/base-apex-chart.vue";

export default {
  components: {BaseApexChart},
  data() {
    return {
      statisticsChart: {
        series: [{
          name: 'Budget',
          data: [10, 20, 15, 28, 22, 34]
        }, {
          name: 'Revenue',
          data: [2, 26, 10, 38, 30, 48]
        }],
        options: {
          chart: {
            height: 361,
            type: 'line',
            dropShadow: {
              enabled: true,
              opacity: 0.2,
              blur: 7,
              left: -7,
              top: 7
            }
          },
          dataLabels: {
            enabled: false
          },
          stroke: {
            curve: 'smooth',
            width: 4
          },

          colors: ['#727cf5', '#0acf97'],
          zoom: {
            enabled: false
          },
          xaxis: {
            type: 'string',
            categories: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
            tooltip: {
              enabled: false
            },
            axisBorder: {
              show: false
            }
          },
          yaxis: {
            labels: {
              formatter: function (val) {
                return val + "k"
              },
              offsetX: -15
            }
          }
        }
      }
    }
  }

}
</script>
