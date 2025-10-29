<template>
  <div class="card">
    <div class="card-header">
      <h4 class="header-title">Collateral Analysis</h4>
    </div>
    <div class="card-body">
      <div v-if="loadingChart" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
      </div>
      <div v-else>
        <b-row class="g-3">
          <b-col lg="6">
            <div class="card bg-light">
              <div class="card-body">
                <h5 class="card-title">Property Type Distribution</h5>
                <div class="chart-container" style="height: 300px;">
                  <canvas ref="propertyTypeChart"></canvas>
                </div>
              </div>
            </div>
          </b-col>
          <b-col lg="6">
            <div class="card bg-light">
              <div class="card-body">
                <h5 class="card-title">Occupancy Status</h5>
                <div class="chart-container" style="height: 300px;">
                  <canvas ref="occupancyChart"></canvas>
                </div>
              </div>
            </div>
          </b-col>
        </b-row>
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

const propertyTypeChart = ref<HTMLCanvasElement | null>(null)
const occupancyChart = ref<HTMLCanvasElement | null>(null)

function renderCharts(): void {
  if (propertyTypeChart.value) {
    const ctx = propertyTypeChart.value.getContext('2d')
    if (ctx) {
      new Chart(ctx, {
        type: 'pie',
        data: {
          labels: ['SFR', 'Condo', 'Townhouse', 'Multi-Family'],
          datasets: [{
            data: [45, 25, 20, 10],
            backgroundColor: ['#007bff', '#28a745', '#ffc107', '#17a2b8']
          }]
        },
        options: { responsive: true, maintainAspectRatio: false }
      })
    }
  }

  if (occupancyChart.value) {
    const ctx = occupancyChart.value.getContext('2d')
    if (ctx) {
      new Chart(ctx, {
        type: 'bar',
        data: {
          labels: ['Owner Occupied', 'Vacant', 'Tenant Occupied'],
          datasets: [{
            label: 'Count',
            data: [120, 45, 80],
            backgroundColor: ['#28a745', '#dc3545', '#ffc107']
          }]
        },
        options: { responsive: true, maintainAspectRatio: false }
      })
    }
  }
}

onMounted(async () => {
  await nextTick()
  renderCharts()
})
</script>
