<template>
  <div>
    <div class="card">
      <div class="d-flex card-header justify-content-between align-items-center">
        <h4 class="header-title">Performance by Entity</h4>
      </div>

      <div class="card-body pt-2">
        <div v-if="loadingChart" class="text-center py-5">
          <div class="spinner-border text-primary" role="status"></div>
          <p class="text-muted mt-2">Loading entity performance...</p>
        </div>

        <div v-else-if="!chartData || chartData.length === 0" class="text-center py-5 text-muted">
          <i class="mdi mdi-domain fs-1 mb-3 d-block"></i>
          <p>No entity data available</p>
        </div>

        <div v-else>
          <div class="chart-container" style="min-height: 400px;">
            <canvas ref="chartCanvas"></canvas>
          </div>
          <div class="text-center mt-3">
            <small class="text-muted">Click any bar for entity breakdown</small>
          </div>
        </div>
      </div>
    </div>

    <div class="card mt-3">
      <div class="d-flex card-header justify-content-between align-items-center">
        <h4 class="header-title">Entity Details</h4>
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
          <p>No entity details available</p>
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover table-striped align-middle mb-0">
            <thead>
              <tr>
                <th>Entity</th>
                <th>Type</th>
                <th class="text-end">Assets</th>
                <th class="text-end">Total UPB</th>
                <th class="text-end">Avg LTV</th>
                <th class="text-center">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in gridData" :key="row.id">
                <td class="fw-semibold">
                  <i class="mdi mdi-domain text-info me-1"></i>
                  {{ row.name }}
                </td>
                <td>
                  <span class="badge bg-light text-dark">{{ row.entity_type }}</span>
                </td>
                <td class="text-end">{{ formatNumber(row.asset_count) }}</td>
                <td class="text-end fw-semibold">{{ formatCurrency(row.total_upb) }}</td>
                <td class="text-end" :class="getLtvClass(row.avg_ltv)">
                  {{ formatPercent(row.avg_ltv) }}
                </td>
                <td class="text-center">
                  <button class="btn btn-sm btn-outline-primary" @click="handleDrillDown(row)">
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

function renderChart(): void {
  if (!chartCanvas.value || !props.chartData || props.chartData.length === 0) return

  if (chartInstance.value) {
    chartInstance.value.destroy()
  }

  const ctx = chartCanvas.value.getContext('2d')
  if (!ctx) return

  chartInstance.value = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: props.chartData.map(d => d.x),
      datasets: [{
        label: 'Total UPB ($MM)',
        data: props.chartData.map(d => d.y),
        backgroundColor: 'rgba(23, 162, 184, 0.6)',
        borderColor: 'rgba(23, 162, 184, 1)',
        borderWidth: 1,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: 'y',
      onClick: (event, elements) => {
        if (elements.length > 0) {
          const index = elements[0].index
          handleChartClick(props.chartData[index])
        }
      },
      scales: {
        x: {
          beginAtZero: true,
          ticks: {
            callback: (value) => `$${(Number(value) / 1_000_000).toFixed(1)}MM`
          }
        }
      },
      plugins: {
        tooltip: {
          callbacks: {
            label: (context) => `UPB: $${(context.parsed.x / 1_000_000).toFixed(2)}MM`
          }
        }
      }
    }
  })
}

function handleChartClick(data: any): void {
  emit('drill-down', { type: 'entity', data })
}

function handleDrillDown(row: any): void {
  emit('drill-down', { type: 'entity', data: row })
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

function getLtvClass(ltv: number): string {
  if (ltv > 100) return 'text-danger fw-bold'
  if (ltv >= 90) return 'text-warning fw-semibold'
  return 'text-success'
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
.table th {
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.75rem;
  color: #6c757d;
  border-bottom: 2px solid #dee2e6;
}
</style>
