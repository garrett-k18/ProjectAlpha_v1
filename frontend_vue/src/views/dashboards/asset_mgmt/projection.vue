<template>
  <div class="card card-h-100">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Projections Vs Actuals</h4>
      <div class="float-end">
        <b-dropdown toggle-class="arrow-none card-drop p-0" variant="black" right>
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
      <div dir="ltr">
        <apexchart height="256" type="bar" class="apex-charts" :series="series" :options="chartOptions"></apexchart>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
export default {
  data() {
    return {
      series: [
        {
          name: 'Actual',
          data: [65, 59, 80, 81, 56, 89, 40, 32, 65, 59, 80, 81],
        },
        {
          name: 'Projection',
          data: [89, 40, 32, 65, 59, 80, 81, 56, 89, 40, 65, 59],
        },
      ],
      chartOptions: {
        chart: {
          parentHeightOffset: 0,
          stacked: true,
          toolbar: {
            show: false,
          },
        },
        plotOptions: {
          bar: {
            horizontal: false,
            columnWidth: '25%',
          },
        },
        grid: {
          padding: {
            left: 0,
            right: 0,
          },
        },
        dataLabels: {
          enabled: false,
        },
        stroke: {
          show: true,
          width: 2,
          colors: ['transparent'],
        },
        zoom: {
          enabled: false,
        },
        legend: {
          show: false,
        },
        colors: ['#727cf5', '#e3eaef'],
        xaxis: {
          categories: [
            'Jan',
            'Feb',
            'Mar',
            'Apr',
            'May',
            'Jun',
            'Jul',
            'Aug',
            'Sep',
            'Oct',
            'Nov',
            'Dec',
          ],
          axisBorder: {
            show: false,
          },
        },
        yaxis: {
          labels: {
            formatter: function (val) {
              return val + 'k'
            },
            offsetX: -15,
          },
        },
        fill: {
          opacity: 1,
        },
        tooltip: {
          y: {
            formatter: function (val) {
              return '$' + val + 'k'
            },
          },
        },
      },
    }
  },
}
</script>