<template>
  <div class="card">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Views Per Minute</h4>

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
      <apexchart
          height="150"
          type="bar"
          class="apex-charts mt-2"
          :series="series"
          :options="chartOptions"
      ></apexchart>

      <div class="table-responsive mt-2 mb-0">
        <table class="table table-sm mb-0 font-13">
          <thead>
          <tr>
            <th>Page</th>
            <th>Views</th>
            <th>Bounce Rate</th>
          </tr>
          </thead>
          <tbody>
          <tr>
            <td>
              <a href="javascript:void(0);" class="text-muted">/hyper/dashboard-analytics</a>
            </td>
            <td>25</td>
            <td>87.5%</td>
          </tr>
          <tr>
            <td>
              <a href="javascript:void(0);" class="text-muted">/hyper/dashboard-crm</a>
            </td>
            <td>15</td>
            <td>21.48%</td>
          </tr>
          <tr>
            <td>
              <a href="javascript:void(0);" class="text-muted">/ubold/dashboard</a>
            </td>
            <td>10</td>
            <td>63.59%</td>
          </tr>
          <tr>
            <td>
              <a href="javascript:void(0);" class="text-muted">/minton/home</a>
            </td>
            <td>7</td>
            <td>56.12%</td>
          </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
export default {
  mounted() {
    for (let i = 10; i >= 1; i--) {
      this.categories.push(i + ' min ago');
    }
  },
  data() {
    // Initialize categories array to store time references for the chart
    let categories: string[] = [];
    return {
      categories, // Array of time references (e.g. "1 min ago", "2 min ago")
      series: [
        {
          name: 'Views',
          data: this.getRandomData(10),
        },
      ],
      chartOptions: {
        chart: {
          stacked: true,
          toolbar: {
            show: false,
          },
        },
        plotOptions: {
          bar: {
            horizontal: false,
            endingShape: 'rounded',
            columnWidth: '22%',
            dataLabels: {
              position: 'top', // top, center, bottom
            },
          },
        },
        dataLabels: {
          enabled: true,
          offsetY: -24,
          style: {
            fontSize: '12px',
            colors: ['#98a6ad'],
          },
        },
        zoom: {
          enabled: false,
        },
        legend: {
          show: false,
        },
        colors: ['#0acf97'],
        xaxis: {
          categories: categories,
          labels: {
            show: false,
          },
          axisTicks: {
            show: false,
          },
          axisBorder: {
            show: false,
          },
        },
        yaxis: {
          labels: {
            show: false,
          },
        },
        fill: {
          type: 'gradient',
          gradient: {
            inverseColors: !0,
            shade: 'light',
            type: 'horizontal',
            shadeIntensity: 0.25,
            gradientToColors: void 0,
            opacityFrom: 1,
            opacityTo: 1,
            stops: [0, 100, 100, 100],
          },
        },
        tooltip: {
          y: {
            formatter: function (val: number): number {
              return val
            },
          },
        },
      },
    }
  },
  methods: {
    getRandomData(number: number) {
      var graphData = []
      for (var idx = 0; idx < number; idx++) {
        graphData.push(Math.floor(Math.random() * Math.floor(90)) + 30)
      }
      return graphData
    }
  }
}
</script>