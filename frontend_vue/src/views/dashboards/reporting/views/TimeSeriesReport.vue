<template>
  <div class="card">
    <div class="card-header">
      <h4 class="header-title">Time Series Analysis</h4>
    </div>
    <div class="card-body">
      <div v-if="loadingChart" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
      </div>
      <div v-else>
        <div class="chart-container" style="height: 400px;">
          <canvas ref="timeseriesChart"></canvas>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

const props = defineProps<{
  chartData: any[]
  gridData: any[]
  loadingChart: boolean
  loadingGrid: boolean
}>()

const timeseriesChart = ref<HTMLCanvasElement | null>(null)

function renderChart(): void {
  if (!timeseriesChart.value) return

  const ctx = timeseriesChart.value.getContext('2d')
  if (!ctx) return

  new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024'],
      datasets: [
        {
          label: 'Total UPB',
          data: [65, 70, 68, 75],
          borderColor: '#007bff',
          backgroundColor: 'rgba(0, 123, 255, 0.1)',
          tension: 0.4
        },
        {
          label: 'Asset Count',
          data: [120, 135, 130, 145],
          borderColor: '#28a745',
          backgroundColor: 'rgba(40, 167, 69, 0.1)',
          tension: 0.4,
          yAxisID: 'y1'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          type: 'linear',
          position: 'left',
          title: { display: true, text: 'UPB ($MM)' }
        },
        y1: {
          type: 'linear',
          position: 'right',
          title: { display: true, text: 'Asset Count' },
          grid: { drawOnChartArea: false }
        }
      }
    }
  })
}

onMounted(async () => {
  await nextTick()
  renderChart()
})
</script>
