<template>
  <div class="card">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Sessions by Browser</h4>

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
          height="345 "
          type="radar"
          class="apex-charts mt-2"
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
          name: 'Usage',
          data: [80, 50, 30, 40, 60, 20],
        },
      ],
      chartOptions: {
        chart: {
          toolbar: {
            show: false,
          },
        },
        labels: ['Chrome', 'Firefox', 'Safari', 'Opera', 'Edge', 'Explorer'],
        plotOptions: {
          radar: {
            size: 130,
            polygons: {
              strokeColor: '#e9e9e9',
              fill: {
                colors: ['#f8f8f8', '#fff'],
              },
            },
          },
        },
        colors: ['#727cf5'],
        yaxis: {
          labels: {
            formatter: function (val: number): string {
              return val + '%'
            },
          },
        },
        dataLabels: {
          enabled: true,
        },
        markers: {
          size: 4,
          colors: ['#fff'],
          strokeColor: ['#727cf5'],
          strokeWidth: 2,
        },
      },
    }
  },
}
</script>