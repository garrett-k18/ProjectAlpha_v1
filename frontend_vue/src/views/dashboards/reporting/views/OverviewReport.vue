<template>
  <div>
    <b-row class="g-2">
      <b-col lg="6">
        <div class="card">
          <div class="card-header">
            <h4 class="header-title">Portfolio Summary</h4>
          </div>
          <div class="card-body">
            <div v-if="loadingChart" class="text-center py-5">
              <div class="spinner-border text-primary" role="status"></div>
            </div>
            <div v-else class="chart-container" style="height: 300px;">
              <canvas ref="summaryChart"></canvas>
            </div>
          </div>
        </div>
      </b-col>

      <b-col lg="6">
        <div class="card">
          <div class="card-header">
            <h4 class="header-title">Status Distribution</h4>
          </div>
          <div class="card-body">
            <div v-if="loadingChart" class="text-center py-5">
              <div class="spinner-border text-primary" role="status"></div>
            </div>
            <div v-else class="chart-container" style="height: 300px;">
              <canvas ref="statusChart"></canvas>
            </div>
          </div>
        </div>
      </b-col>
    </b-row>

    <div class="card mt-3">
      <div class="card-header">
        <h4 class="header-title">Recent Activity</h4>
      </div>
      <div class="card-body">
        <div v-if="loadingGrid" class="text-center py-3">
          <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
        </div>
        <div v-else-if="!gridData || gridData.length === 0" class="text-center py-3 text-muted">
          <p>No recent activity</p>
        </div>
        <div v-else>
          <div class="list-group list-group-flush">
            <div v-for="(item, index) in gridData.slice(0, 10)" :key="index" 
              class="list-group-item d-flex justify-content-between align-items-center">
              <div>
                <h6 class="mb-1">{{ item.title || item.name || 'Activity' }}</h6>
                <small class="text-muted">{{ item.description || formatDate(item.date) }}</small>
              </div>
              <button class="btn btn-sm btn-outline-primary" @click="handleDrillDown(item)">
                View
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

const props = defineProps<{
  chartData: any[]
  gridData: any[]
  loadingChart: boolean
  loadingGrid: boolean
}>()

const emit = defineEmits<{
  (e: 'drill-down', payload: { type: string; data: any }): void
}>()

const summaryChart = ref<HTMLCanvasElement | null>(null)
const statusChart = ref<HTMLCanvasElement | null>(null)
const summaryChartInstance = ref<Chart | null>(null)
const statusChartInstance = ref<Chart | null>(null)

function renderCharts(): void {
  if (summaryChart.value) {
    if (summaryChartInstance.value) summaryChartInstance.value.destroy()
    const ctx = summaryChart.value.getContext('2d')
    if (ctx) {
      summaryChartInstance.value = new Chart(ctx, {
        type: 'line',
        data: {
          labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
          datasets: [{
            label: 'Total UPB',
            data: [65, 68, 70, 72, 75, 78],
            borderColor: 'rgba(54, 162, 235, 1)',
            backgroundColor: 'rgba(54, 162, 235, 0.1)',
            tension: 0.4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false
        }
      })
    }
  }

  if (statusChart.value) {
    if (statusChartInstance.value) statusChartInstance.value.destroy()
    const ctx = statusChart.value.getContext('2d')
    if (ctx) {
      statusChartInstance.value = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: ['DD', 'Awarded', 'Pass', 'Board'],
          datasets: [{
            data: [30, 45, 15, 10],
            backgroundColor: [
              'rgba(23, 162, 184, 0.8)',
              'rgba(40, 167, 69, 0.8)',
              'rgba(108, 117, 125, 0.8)',
              'rgba(0, 123, 255, 0.8)'
            ]
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false
        }
      })
    }
  }
}

function handleDrillDown(item: any): void {
  emit('drill-down', { type: 'asset', data: item })
}

function formatDate(date: any): string {
  if (!date) return ''
  return new Date(date).toLocaleDateString()
}

watch([() => props.chartData, () => props.loadingChart], async () => {
  await nextTick()
  if (!props.loadingChart) renderCharts()
})

onMounted(async () => {
  await nextTick()
  renderCharts()
})
</script>
