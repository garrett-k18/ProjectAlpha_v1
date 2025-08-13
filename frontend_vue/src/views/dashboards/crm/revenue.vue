<template>
  <div class="card">
    <div class="card-header d-flex justify-content-between align-items-center">
      <h4 class="header-title">Revenue</h4>
      <div>
        <button type="button" class="btn btn-soft-secondary btn-sm">
          ALL
        </button>
        <button type="button" class="btn btn-soft-primary btn-sm">
          1M
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
      <div class="chart-content-bg">
        <b-row class="text-center">
          <b-col md="6">
            <p class="text-muted mb-0 mt-3">Current Month</p>
            <h2 class="fw-normal mb-3">
              <span>$42,025</span>
            </h2>
          </b-col>
          <b-col md="6">
            <p class="text-muted mb-0 mt-3">Previous Month</p>
            <h2 class="fw-normal mb-3">
              <span>$74,651</span>
            </h2>
          </b-col>
        </b-row>
      </div>
      <div dir="ltr">
        <apexchart
            height="338"
            type="line"
            class="apex-charts"
            :series="series"
            :options="chartOptions"
        ></apexchart>
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
          name: 'Total Revenue',
          type: 'area',
          data: [44, 55, 31, 47, 31, 43, 26, 41, 31, 47, 33, 43],
        },
        {
          name: 'Total Pipeline',
          type: 'line',
          data: [55, 69, 45, 61, 43, 54, 37, 52, 44, 61, 43, 56],
        },
      ],
      chartOptions: {
        chart: {
          toolbar: {
            show: false,
          },
        },
        stroke: {
          curve: 'smooth',
          width: 2,
        },
        fill: {
          type: 'solid',
          opacity: [0.35, 1],
        },
        labels: [
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
        markers: {
          size: 0,
        },
        colors: ['#0acf97', '#fa5c7c'],
        yaxis: [
          {
            title: {
              text: 'Revenue (USD)',
            },
            min: 0,
          },
        ],
        tooltip: {
          shared: true,
          intersect: false,
          y: {
            formatter: function (y) {
              if (typeof y !== 'undefined') {
                return y.toFixed(0) + 'k'
              }
              return y
            },
          },
        },
        grid: {
          borderColor: '#f1f3fa',
          padding: {
            bottom: 5
          }
        },
        legend: {
          fontSize: '14px',
          fontFamily: '14px',
          offsetY: 5,
        },
        responsive: [
          {
            breakpoint: 600,
            options: {
              yaxis: {
                show: false,
              },
              legend: {
                show: false,
              },
            },
          },
        ],
      },
    }
  },
}
</script>

