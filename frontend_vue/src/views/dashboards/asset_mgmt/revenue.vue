<template>
  <div class="card flex-grow-1 w-100">

    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Revenue</h4>

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

    <div class="card-body  pt-0">
      <div class="chart-content-bg">
        <b-row class="text-center">
          <b-col md="6">
            <p class="text-muted mb-0 mt-3">Current Week</p>
            <h2 class="fw-normal mb-3">
              <small class="mdi mdi-checkbox-blank-circle text-primary align-middle me-2"></small>
              <span>$58,254</span>
            </h2>
          </b-col>
          <b-col md="6">
            <p class="text-muted mb-0 mt-3">Previous Week</p>
            <h2 class="fw-normal mb-3">
              <small class="mdi mdi-checkbox-blank-circle text-success align-middle me-2"></small>
              <span>$69,524</span>
            </h2>
          </b-col>
        </b-row>
      </div>
      <div class="dash-item-overlay d-none d-md-block" dir="ltr">
        <h5>Today's Earning: $2,562.30</h5>
        <p class="text-muted font-13 mb-3 mt-2">
          Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. Nam eget dui.
          Etiam rhoncus...
        </p>
        <a href="javascript: void(0);" class="btn btn-outline-primary">
          View Statements
          <i class="mdi mdi-arrow-right ms-2"></i>
        </a>
      </div>
      <apexchart
          height="370"
          type="line"
          class="apex-charts mt-3"
          :series="series"
          :options="chartOptions"
      ></apexchart>
    </div>

  </div>
</template>

<script lang="ts">
export default {
  data() {
    return {
      series: [
        {
          name: 'Current Week',
          data: [10, 20, 15, 25, 20, 30, 20],
        },
        {
          name: 'Previous Week',
          data: [0, 15, 10, 30, 15, 35, 25],
        },
      ],
      chartOptions: {
        chart: {
          dropShadow: {
            enabled: true,
            opacity: 0.2,
            blur: 7,
            left: -7,
            top: 7,
          },
          toolbar: {
            show: false,
          },
          parentHeightOffset: 0,
        },
        grid: {
          strokeDashArray: 7,
        },
        dataLabels: {
          enabled: false,
        },
        stroke: {
          curve: 'smooth',
          width: 4,
        },
        colors: ['#727cf5', '#0acf97'],
        zoom: {
          enabled: false,
        },
        legend: {
          show: false,
        },
        xaxis: {
          type: 'string',
          categories: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
          tooltip: {
            enabled: false
          },
          axisBorder: {
            show: false
          }
        },
        yaxis: {
          labels: {
            formatter: function (val: number) {
              return val + "k"
            },
            offsetX: -15
          }
        },
      },
    }
  },
}
</script>