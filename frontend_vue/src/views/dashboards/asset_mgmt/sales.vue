<template>
  <div class="card">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Asset Allocation</h4>
      <div class="float-end">
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

    <div class="card-body pt-0">
      <apexchart
          height="224"
          type="donut"
          class="apex-charts mb-4 mt-2"
          :series="series"
          :options="chartOptions"
      ></apexchart>

    </div>
    <!-- end card-body-->
  </div>
  <!-- end card-->
</template>

<script lang="ts">
export default {
  data() {
    return {
      series: [44, 55, 41, 17],
      chartOptions: {
        chart: {
          type: 'radialBar',
          events: {},
        },
        legend: {
          show: false,
        },
        stroke: {
          width: 0
        },
        labels: ['Direct', 'Affiliate', 'Sponsored', 'E-mail'],
        responsive: [
          {
            breakpoint: 480,
            options: {
              chart: {
                width: 200
              },
              legend: {
                position: 'bottom'
              }
            }
          },
        ],
        colors: ['#727cf5', '#0acf97', '#fa5c7c', '#ffbc00'],
      },
    }
  },
}
</script>