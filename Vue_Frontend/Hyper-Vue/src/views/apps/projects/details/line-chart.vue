<template>
  <Line :options="chartOptions" :data="chartData"></Line>
</template>

<script lang="ts">
import {Line} from 'vue-chartjs'
import {Chart as ChartJS, Title, Tooltip, Legend, CategoryScale, LinearScale,PointElement,LineElement} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, CategoryScale, LinearScale,PointElement,LineElement)
export default {
  components: {Line},
  data() {
    return {
      chartData: {
        labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        datasets: [{
          label: "Completed Tasks",
          backgroundColor: 'rgba(10, 207, 151, 0.3)',
          borderColor: '#0acf97',
          data: [32, 42, 42, 62, 52, 75, 62]
        }, {
          label: "Plan Tasks",
          fill: true,
          backgroundColor: 'transparent',
          borderColor: "#727cf5",
          borderDash: [5, 5],
          data: [42, 58, 66, 93, 82, 105, 92]
        }]
      },
      chartOptions: {
        maintainAspectRatio: false,

        plugins: {
          filler: {
            propagate: false
          },
          legend: {
            display: false
          },
          tooltips: {
            intersect: false
          },
          hover: {
            intersect: true
          },
        },
        tension: 0.3,
        scales: {
          x: {

            grid: {
              color: "rgba(0,0,0,0.05)"
            }
          },
          y: {
            ticks: {
              stepSize: 20
            },
            display: true,
            borderDash: [5, 5],
            grid: {
              color: "rgba(0,0,0,0)",
              fontColor: '#fff'
            }
          }
        }
      }
    }
  }
}
</script>
