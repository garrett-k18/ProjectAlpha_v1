<template>
  <div class="card card-h-100">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Projected Liquidations</h4>
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
      <div dir="ltr">
        <apexchart height="256" type="line" class="apex-charts" :series="series" :options="chartOptions"></apexchart>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
export default {
  data() {
    return {
      // DEV NOTE: Placeholder dataset until liquidation projections model is exposed via API.
      // WHEN: Backend service ready, swap static arrays for axios call returning quantity + dollar projections.
      series: [
        {
          name: 'Projected Assets',
          type: 'column',
          // TODO: Replace static values with quantity projections from upcoming liquidation model service.
          // ORDER: Values aligned to x-axis categories starting with current month (October) and wrapping through September.
          data: [59, 80, 81, 65, 59, 80, 81, 56, 89, 40, 32, 65],
        },
        {
          name: 'Projected Proceeds',
          type: 'line',
          // TODO: Replace static values with dollar projections once backend endpoint is wired.
          // ORDER: Mirrors quantity series so month-to-month comparisons remain consistent for the combined visualization.
          data: [40, 65, 59, 89, 40, 32, 65, 59, 80, 81, 56, 89],
        },
      ],
      chartOptions: {
        chart: {
          parentHeightOffset: 0,
          stacked: false,
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
          width: [0, 3],
          colors: ['transparent', '#ffab00'],
        },
        zoom: {
          enabled: false,
        },
        legend: {
          show: true,
        },
        colors: ['#727cf5', '#ffab00'],
        xaxis: {
          // NOTE: First entry reflects the current calendar month (October); remaining months wrap chronologically.
          categories: [
            'Oct',
            'Nov',
            'Dec',
            'Jan',
            'Feb',
            'Mar',
            'Apr',
            'May',
            'Jun',
            'Jul',
            'Aug',
            'Sep',
          ],
          axisBorder: {
            show: false,
          },
        },
        yaxis: [
          {
            title: {
              text: 'Assets (units)',
            },
            labels: {
              formatter: function (val: number) {
                return `${Math.round(val)}`
              },
              offsetX: -15,
            },
          },
          {
            opposite: true,
            title: {
              text: 'Liquidation Value (thousands USD)',
            },
            labels: {
              formatter: function (val: number) {
                return `$${val}k`
              },
            },
          },
        ],
        fill: {
          opacity: 1,
        },
        tooltip: {
          shared: true,
          intersect: false,
          y: [
            {
              formatter: function (val: number) {
                return `${Math.round(val)} assets`
              },
            },
            {
              formatter: function (val: number) {
                return `$${val}k`
              },
            },
          ],
        },
      },
    }
  },
}
</script>