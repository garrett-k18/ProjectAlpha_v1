<template>
  <b-card>
    <h4 class="header-title mb-3">Orders & Revenue</h4>
    <div dir="ltr">
      <div style="height: 260px;" class="chartjs-chart">
        <Bar
            id="high-performing-product"
            :options="options"
            :data="data"
        />
      </div>
    </div>
  </b-card>
</template>

<script lang="ts">
import {Bar} from 'vue-chartjs'
import {Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

export default {
  components: {Bar},
  data() {

    return {
      data: {
        // labels: ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"],
        labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        datasets: [
          {
            label: "Orders",
            backgroundColor: '#727cf5',
            borderColor: '#727cf5',
            hoverBackgroundColor: '#727cf5',
            hoverBorderColor: '#727cf5',
            data: [65, 59, 80, 81, 56, 89, 40, 32, 65, 59, 80, 81]
          },
          {
            label: "Revenue",
            backgroundColor: "#91a6bd40",
            borderColor: "#91a6bd40",
            hoverBackgroundColor: "#91a6bd40",
            hoverBorderColor: "#91a6bd40",
            data: [89, 40, 32, 65, 59, 80, 81, 56, 89, 40, 65, 59]
          }
        ]
      },
      options: {
        maintainAspectRatio: false,
        datasets: {
          bar: {
            barPercentage: 0.7,
            categoryPercentage: 0.5,
          }
        },
        plugins: {
          legend: {
            display: false
          },
        },


        scales: {
          y: {
            grid: {
              display: false,
              color: "#91a6bd40"
            },
            stacked: false,
            ticks: {
              stepSize: 20
            }
          },
          x: {
            stacked: false,
            grid: {
              color: "rgba(0,0,0,0.01)"
            }
          }
        }
      },
    }
  },
}
</script>
