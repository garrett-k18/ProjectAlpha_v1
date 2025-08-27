<template>
  <div class="card card-h-100">
    <div class="card-body">
      <b-alert
          letiant="warning"
          class="mb-3"
          show
          dismissible
          v-model="show"
      >Property HY1xx is not receiving hits. Either your site is not receiving any sessions or it is not tagged
        correctly.
      </b-alert>

      
      <!-- Removed quick links time filters -->
      <h4 class="header-title mb-3">Sessions Overview</h4>

      <apexchart
          height="309"
          type="area"
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
    let now = new Date();
    let labels = this.getDaysInMonth(now.getMonth() + 1, now.getFullYear());
    return {
      show: true,
      series: [
        {
          name: 'Sessions',
          data: [10, 20, 5, 15, 10, 20, 15, 25, 20, 30, 25, 40, 30, 50, 35],
        },
      ],
      chartOptions: {
        chart: {
          toolbar: {
            show: false,
          },
        },
        dataLabels: {
          enabled: false,
        },
        stroke: {
          curve: 'smooth',
          width: 4,
        },
        zoom: {
          enabled: false,
        },
        legend: {
          show: false,
        },
        colors: ['#0acf97'],
        xaxis: {
          type: 'string',
          categories: labels,
          tooltip: {
            enabled: false,
          },
          axisBorder: {
            show: false,
          },
          labels: {},
        },
        yaxis: {
          labels: {
            formatter: function (val: number): string {
              return `${val}k`
            },
            offsetX: -15,
          },
        },
        fill: {
          type: 'gradient',
          gradient: {
            type: 'vertical',
            shadeIntensity: 1,
            inverseColors: false,
            opacityFrom: 0.45,
            opacityTo: 0.05,
            stops: [45, 100],
          },
        },
      },
    }
  },
  methods: {
    getDaysInMonth(month:number, year:number) {
      let date:any = new Date(year, month, 1);
      let days = [];
      let idx = 0;
      while (date.getMonth() === month && idx < 15) {
        let d = new Date(date);
        days.push(d.getDate() + " " + d.toLocaleString('en-us', {month: 'short'}));
        date.setDate(date.getDate() + 1);
        idx += 1;
      }
      return days;
    }
  }
}
</script>