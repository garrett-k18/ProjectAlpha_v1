<template>
  <div class="card">
    <div class="card-body">
      <h4 class="header-title">Monthly Target</h4>

      <BaseApexChart class="apex-charts mb-4 mt-4" :height="256" :series="monthlyTargetData.series" :options="monthlyTargetData.options"/>

      <b-row>
        <b-col cols="6">
          <div class="text-center">
            <h5>Pending</h5>
            <p class="fw-semibold text-muted mb-0">
              <i class="mdi mdi-circle text-primary"></i> Projects

            </p>
          </div>
        </b-col>
        <b-col cols="6">
          <div class="text-center">
            <h5>Done</h5>
            <p class="fw-semibold text-muted mb-0">
              <i class="mdi mdi-circle text-success"></i> Projects
            </p>
          </div>
        </b-col>
      </b-row>
    </div>
  </div>
</template>

<script lang="ts">
import BaseApexChart from "@/components/base-apex-chart.vue";

export default {
  components: {BaseApexChart},
  data() {
    return {
      monthlyTargetData: {
        series: [82, 37],
        options: {
          chart: {
            height: 256,
            type: 'donut',
          },
          legend: {
            show: false
          },
          stroke: {
            width: 0,
            colors: ['transparent']
          },
          labels: ["Done Projects", "Pending Projects"],
          colors: ['#0acf97', '#727cf5'],
          responsive: [{
            breakpoint: 480,
            options: {
              chart: {
                width: 200
              },
              legend: {
                position: 'bottom'
              }
            }
          }]
        }
      }
    }
  }

}
</script>
