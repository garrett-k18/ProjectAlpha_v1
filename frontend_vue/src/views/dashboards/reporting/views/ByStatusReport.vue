<template>
  <div>
    <div class="card">
      <div class="d-flex card-header justify-content-between align-items-center">
        <h4 class="header-title">Portfolio by Status</h4>
      </div>

      <div class="card-body pt-2">
        <div v-if="loadingChart" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <div v-else-if="!chartData || chartData.length === 0" class="text-center py-5 text-muted">
          <i class="mdi mdi-tag-outline fs-1 mb-3 d-block"></i>
          <p>No status data available</p>
        </div>

        <div v-else>
          <b-row>
            <b-col lg="6">
              <div class="chart-container" style="min-height: 350px;">
                <canvas ref="chartCanvas"></canvas>
              </div>
            </b-col>
            <b-col lg="6">
              <div class="status-summary mt-3 mt-lg-0">
                <h5 class="mb-3">Status Breakdown</h5>
                <div v-for="(item, index) in statusBreakdown" :key="index" class="mb-3">
                  <div class="d-flex justify-content-between align-items-center mb-1">
                    <span class="fw-semibold">{{ item.label }}</span>
                    <span class="badge" :class="getStatusBadgeClass(item.status)">
                      {{ item.count }} assets
                    </span>
                  </div>
                  <div class="progress" style="height: 25px;">
                    <div
                      class="progress-bar"
                      :class="getStatusProgressClass(item.status)"
                      :style="{ width: item.percentage + '%' }"
                      role="progressbar"
                    >
                      {{ formatCurrency(item.upb) }}
                    </div>
                  </div>
                </div>
              </div>
            </b-col>
          </b-row>
        </div>
      </div>
    </div>

    <div class="card mt-3">
      <div class="d-flex card-header justify-content-between align-items-center">
        <h4 class="header-title">Status Details</h4>
        <button class="btn btn-sm btn-outline-secondary" @click="exportGrid">
          <i class="mdi mdi-download me-1"></i>
          Export
        </button>
      </div>

      <div class="card-body pt-2">
        <div v-if="loadingGrid" class="text-center py-3">
          <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
        </div>

        <div v-else-if="!gridData || gridData.length === 0" class="text-center py-3 text-muted">
          <p>No details available</p>
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover table-striped align-middle mb-0">
            <thead>
              <tr>
                <th>Status</th>
                <th class="text-end">Count</th>
                <th class="text-end">Total UPB</th>
                <th class="text-end">Avg UPB</th>
                <th class="text-end">% of Total</th>
                <th class="text-center">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in gridData" :key="row.status">
                <td>
                  <span class="badge" :class="getStatusBadgeClass(row.status)">
                    {{ row.status }}
                  </span>
                </td>
                <td class="text-end fw-semibold">{{ formatNumber(row.count) }}</td>
                <td class="text-end">{{ formatCurrency(row.total_upb) }}</td>
                <td class="text-end text-muted">{{ formatCurrency(row.avg_upb) }}</td>
                <td class="text-end">{{ formatPercent(row.percentage) }}</td>
                <td class="text-center">
                  <button
                    class="btn btn-sm btn-outline-primary"
                    @click="handleDrillDown(row)"
                  >
                    <i class="mdi mdi-eye"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
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

const chartCanvas = ref<HTMLCanvasElement | null>(null)
const chartInstance = ref<Chart | null>(null)

const statusBreakdown = computed(() => {
  if (!props.chartData || props.chartData.length === 0) return []
  
  const total = props.chartData.reduce((sum, item) => sum + item.y, 0)
  
  return props.chartData.map(item => ({
    status: item.x,
    label: item.x,
    count: item.meta?.count || 0,
    upb: item.y,
    percentage: total > 0 ? (item.y / total) * 100 : 0
  }))
})

function renderChart(): void {
  if (!chartCanvas.value || !props.chartData || props.chartData.length === 0) return

  if (chartInstance.value) {
    chartInstance.value.destroy()
  }

  const ctx = chartCanvas.value.getContext('2d')
  if (!ctx) return

  const colors = props.chartData.map(item => getStatusColor(item.x))

  chartInstance.value = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: props.chartData.map(d => d.x),
      datasets: [{
        data: props.chartData.map(d => d.y),
        backgroundColor: colors,
        borderWidth: 2,
        borderColor: '#fff'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      onClick: (event, elements) => {
        if (elements.length > 0) {
          const index = elements[0].index
          const clickedData = props.chartData[index]
          handleChartClick(clickedData)
        }
      },
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            padding: 15,
            font: {
              size: 12
            }
          }
        },
        tooltip: {
          callbacks: {
            label: (context) => {
              const value = context.parsed
              return `$${(value / 1_000_000).toFixed(2)}MM`
            }
          }
        }
      }
    }
  })
}

function getStatusColor(status: string): string {
  const colorMap: Record<string, string> = {
    'DD': '#17a2b8',
    'AWARDED': '#28a745',
    'PASS': '#6c757d',
    'BOARD': '#007bff',
  }
  return colorMap[status] || '#6c757d'
}

function getStatusBadgeClass(status: string): string {
  const classMap: Record<string, string> = {
    'DD': 'bg-info',
    'AWARDED': 'bg-success',
    'PASS': 'bg-secondary',
    'BOARD': 'bg-primary',
  }
  return classMap[status] || 'bg-secondary'
}

function getStatusProgressClass(status: string): string {
  const classMap: Record<string, string> = {
    'DD': 'bg-info',
    'AWARDED': 'bg-success',
    'PASS': 'bg-secondary',
    'BOARD': 'bg-primary',
  }
  return classMap[status] || 'bg-secondary'
}

function handleChartClick(data: any): void {
  emit('drill-down', { type: 'status', data })
}

function handleDrillDown(row: any): void {
  emit('drill-down', { type: 'status', data: row })
}

function exportGrid(): void {
  alert('Export coming soon!')
}

function formatNumber(value: number): string {
  return new Intl.NumberFormat().format(value || 0)
}

function formatCurrency(value: number): string {
  const abs = Math.abs(value || 0)
  if (abs >= 1_000_000) return `$${(abs / 1_000_000).toFixed(1)}MM`
  if (abs >= 1_000) return `$${(abs / 1_000).toFixed(1)}k`
  return `$${abs.toFixed(0)}`
}

function formatPercent(value: number): string {
  return `${(value || 0).toFixed(1)}%`
}

watch(() => props.chartData, async () => {
  await nextTick()
  renderChart()
})

onMounted(async () => {
  await nextTick()
  renderChart()
})
</script>

<style scoped>
.status-summary {
  padding: 0 1rem;
}

.progress {
  border-radius: 0.25rem;
  overflow: hidden;
}

.progress-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  font-weight: 600;
  color: white;
}

.table th {
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.75rem;
  color: #6c757d;
  border-bottom: 2px solid #dee2e6;
}
</style>
