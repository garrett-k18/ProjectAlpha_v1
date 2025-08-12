<template>
  <div class="card">
    <div class="card-header d-flex justify-content-between align-items-center">
      <h4 class="header-title">Project Statistics</h4>
      <div>
        <button type="button" class="btn btn-soft-primary btn-sm">
          All
        </button>
        <button type="button" class="btn btn-soft-secondary btn-sm">
          6M
        </button>
        <button type="button" class="btn btn-soft-secondary btn-sm">
          1Y
        </button>
      </div>
    </div>

    <div class="card-body pt-0">
      <div dir="ltr" class="mt-2">
        <BaseApexChart class="apex-charts" :height="326" :series="statisticsData.series" :options="statisticsData.options"/>
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
      statisticsData: {
        series: [{
          name: 'Projects',
          data: [56, 38, 85, 72, 28, 69, 55, 52, 69]
        }, {
          name: 'Working Hours',
          data: [176, 185, 256, 240, 187, 205, 191, 114, 194]
        }],
        options: {
          chart: {
            height: 326,
            type: 'bar',
            toolbar: {
              show: false
            }
          },
          plotOptions: {
            bar: {
              horizontal: false,
              endingShape: 'rounded',
              columnWidth: '25%',
            },
          },
          dataLabels: {
            enabled: false
          },
          stroke: {
            show: true,
            width: 0,
            colors: ['transparent']
          },
          colors: ['#ced1ff', '#727cf5'],

          xaxis: {
            categories: ['Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct'],
          },
          legend: {
            offsetY: 7,
          },
          fill: {
            opacity: 1

          },
          // legend: {
          //     floating: true
          // },
          grid: {
            row: {
              colors: ['transparent', 'transparent'], // takes an array which will be repeated on columns
              opacity: 0.2
            },
            borderColor: '#f1f3fa',
            padding: {
              bottom: 5
            }
          }
        }
      }
    }
  }

}
</script>
