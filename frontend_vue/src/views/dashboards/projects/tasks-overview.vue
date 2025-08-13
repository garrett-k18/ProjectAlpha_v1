<template>
  <div class="card">
    <div class="card-header d-flex justify-content-between align-items-center">
      <h4 class="header-title">Tasks Overview</h4>
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

    <div class="card-body">
      <div dir="ltr">
        <div class="chartjs-chart" style="height: 320px;">
          <Bar id="task-area-chart" :options="chartOptions" :data="chartData"></Bar>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import {Bar} from 'vue-chartjs'
import {Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

export default {
  components: { Bar},
  data() {
    return {
      chartData: {
        labels: ["Sprint 1", "Sprint 2", "Sprint 3", "Sprint 4", "Sprint 5", "Sprint 6", "Sprint 7", "Sprint 8", "Sprint 9", "Sprint 10", "Sprint 11", "Sprint 12", "Sprint 13", "Sprint 14", "Sprint 15", "Sprint 16", "Sprint 17", "Sprint 18", "Sprint 19", "Sprint 20", "Sprint 21", "Sprint 22", "Sprint 23", "Sprint 24"],
        datasets: [{
          label: "This year",
          backgroundColor: ['#727cf5'],
          borderColor: ['#727cf5'],
          data: [16, 44, 32, 48, 72, 60, 84, 64, 78, 50, 68, 34, 26, 44, 32, 48, 72, 60, 74, 52, 62, 50, 32, 22]
        }]
      },
      chartOptions: {
        maintainAspectRatio: false, barPercentage: 0.7, categoryPercentage: 0.5, // barSpacing: 10,
        plugins: {
          filler: {
            propagate: false
          }, legend: {
            display: false
          }, tooltips: {
            intersect: false
          }, hover: {
            intersect: true
          },

        }, scales: {
          x: {
            grid: {
              color: "rgba(0,0,0,0.05)"
            }
          }, y: {
            ticks: {
              stepSize: 10, display: false
            }, min: 10, max: 100, display: true, borderDash: [5, 5], grid: {
              color: "rgba(0,0,0,0)", fontColor: '#fff',
            }
          }
        }
      }
    }
  }
}
</script>