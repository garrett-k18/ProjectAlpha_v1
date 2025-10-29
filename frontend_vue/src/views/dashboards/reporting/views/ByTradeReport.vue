<template>
  <div>
    <div class="card">
      <div class="d-flex card-header justify-content-between align-items-center">
        <h4 class="header-title">Performance by Trade</h4>
        <div class="dropdown">
          <button
            class="btn btn-sm btn-outline-primary dropdown-toggle"
            type="button"
            data-bs-toggle="dropdown"
          >
            <i class="mdi mdi-chart-bar me-1"></i>
            Chart Type
          </button>
          <ul class="dropdown-menu">
            <li><a class="dropdown-item" href="#" @click.prevent="chartType = 'bar'">Bar Chart</a></li>
            <li><a class="dropdown-item" href="#" @click.prevent="chartType = 'line'">Line Chart</a></li>
            <li><a class="dropdown-item" href="#" @click.prevent="chartType = 'pie'">Pie Chart</a></li>
          </ul>
        </div>
      </div>

      <div class="card-body pt-2">
        <div v-if="loadingChart" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading chart...</span>
          </div>
          <p class="text-muted mt-2">Loading trade performance data...</p>
        </div>

        <div v-else-if="!chartData || chartData.length === 0" class="text-center py-5 text-muted">
          <i class="mdi mdi-chart-bar-stacked fs-1 mb-3 d-block"></i>
          <p>No trade data available. Adjust filters to see results.</p>
        </div>

        <div v-else>
          <div class="chart-container" style="min-height: 400px;">
            <canvas ref="chartCanvas"></canvas>
          </div>
          
          <div class="text-center mt-3">
            <small class="text-muted">Click any bar to view detailed trade analysis</small>
          </div>
        </div>
      </div>
    </div>

    <div class="card mt-3">
      <div class="d-flex card-header justify-content-between align-items-center">
        <h4 class="header-title">Trade Details</h4>
        <button class="btn btn-sm btn-outline-secondary" @click="exportGrid">
          <i class="mdi mdi-download me-1"></i>
          Export CSV
        </button>
      </div>

      <div class="card-body pt-2">
        <div v-if="loadingGrid" class="text-center py-3">
          <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
          <span class="ms-2 text-muted">Loading details...</span>
        </div>

        <div v-else-if="!gridData || gridData.length === 0" class="text-center py-3 text-muted">
          <p>No trade details available.</p>
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover table-striped align-middle mb-0">
            <thead>
              <tr>
                <th>Trade Name</th>
                <th class="text-end">Asset Count</th>
                <th class="text-end">Total UPB</th>
                <th class="text-end">Avg LTV</th>
                <th>Status</th>
                <th class="text-center">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in gridData" :key="row.id">
                <td class="fw-semibold">{{ row.trade_name }}</td>
                <td class="text-end">{{ formatNumber(row.asset_count) }}</td>
                <td class="text-end">{{ formatCurrency(row.total_upb) }}</td>
                <td class="text-end" :class="getLtvClass(row.avg_ltv)">
                  {{ formatPercent(row.avg_ltv) }}
                </td>
                <td>
                  <span :class="['badge', getStatusClass(row.status)]">
                    {{ row.status }}
                  </span>
                </td>
                <td class="text-center">
                  <button
                    class="btn btn-sm btn-outline-primary"
                    @click="handleDrillDown(row)"
                  >
                    <i class="mdi mdi-eye"></i>
                    View
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

const chartCanvas = ref<HTMLCanvasElement | null>(null)
const chartInstance = ref<Chart | null>(null)
const chartType = ref<'bar' | 'line' | 'pie'>('bar')

function renderChart(): void {
  if (!chartCanvas.value || !props.chartData || props.chartData.length === 0) return

  if (chartInstance.value) {
    chartInstance.value.destroy()
  }

  const ctx = chartCanvas.value.getContext('2d')
  if (!ctx) return

  chartInstance.value = new Chart(ctx, {
    type: chartType.value,
    data: {
      labels: props.chartData.map(d => d.x),
      datasets: [{
        label: 'Total UPB ($MM)',
        data: props.chartData.map(d => d.y),
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1,
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
      scales: chartType.value !== 'pie' ? {
        y: {
          beginAtZero: true,
          ticks: {
            callback: (value) => `$${(Number(value) / 1_000_000).toFixed(1)}MM`
          }
        }
      } : undefined,
      plugins: {
        legend: {
          display: chartType.value === 'pie'
        },
        tooltip: {
          callbacks: {
            label: (context) => {
              return `UPB: $${(context.parsed.y / 1_000_000).toFixed(2)}MM`
            }
          }
        }
      }
    }
  })
}

function handleChartClick(data: any): void {
  emit('drill-down', { type: 'trade', data })
}

function handleDrillDown(row: any): void {
  emit('drill-down', { type: 'trade', data: row })
}

function exportGrid(): void {
  console.log('[ByTradeReport] Export grid data')
  alert('CSV export coming soon!')
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

function getLtvClass(ltv: number): string {
  if (ltv > 100) return 'text-danger fw-bold'
  if (ltv >= 90) return 'text-warning fw-semibold'
  return 'text-success'
}

function getStatusClass(status: string): string {
  const statusMap: Record<string, string> = {
    'DD': 'bg-info',
    'AWARDED': 'bg-success',
    'PASS': 'bg-secondary',
    'BOARD': 'bg-primary',
  }
  return statusMap[status] || 'bg-secondary'
}

watch([() => props.chartData, chartType], async () => {
  await nextTick()
  renderChart()
})

onMounted(async () => {
  await nextTick()
  renderChart()
})
</script>

<style scoped>
.chart-container {
  position: relative;
}

.table th {
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.5px;
  color: #6c757d;
  border-bottom: 2px solid #dee2e6;
}

.table-hover tbody tr:hover {
  background-color: rgba(54, 162, 235, 0.05);
}
</style>
