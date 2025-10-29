<template>
  <div>
    <div class="card">
      <div class="d-flex card-header justify-content-between align-items-center">
        <h4 class="header-title">Performance by Fund</h4>
      </div>

      <div class="card-body pt-2">
        <div v-if="loadingChart" class="text-center py-5">
          <div class="spinner-border text-primary" role="status"></div>
          <p class="text-muted mt-2">Loading fund performance...</p>
        </div>

        <div v-else-if="!chartData || chartData.length === 0" class="text-center py-5 text-muted">
          <i class="mdi mdi-wallet-outline fs-1 mb-3 d-block"></i>
          <p>No fund data available</p>
        </div>

        <div v-else>
          <b-row>
            <b-col lg="8">
              <div class="chart-container" style="min-height: 400px;">
                <canvas ref="chartCanvas"></canvas>
              </div>
            </b-col>
            <b-col lg="4">
              <div class="fund-metrics mt-3 mt-lg-0">
                <h5 class="mb-3">Fund Comparison</h5>
                <div v-for="(fund, index) in fundMetrics" :key="index" class="card bg-light mb-2">
                  <div class="card-body p-3">
                    <h6 class="mb-2 fw-bold">{{ fund.name }}</h6>
                    <div class="d-flex justify-content-between mb-1">
                      <span class="text-muted small">Assets:</span>
                      <span class="fw-semibold">{{ formatNumber(fund.count) }}</span>
                    </div>
                    <div class="d-flex justify-content-between mb-1">
                      <span class="text-muted small">UPB:</span>
                      <span class="fw-semibold">{{ formatCurrency(fund.upb) }}</span>
                    </div>
                    <div class="d-flex justify-content-between">
                      <span class="text-muted small">Avg LTV:</span>
                      <span :class="getLtvClass(fund.ltv)">{{ formatPercent(fund.ltv) }}</span>
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
        <h4 class="header-title">Fund Details</h4>
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
          <p>No fund details available</p>
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover table-striped align-middle mb-0">
            <thead>
              <tr>
                <th>Fund</th>
                <th class="text-end">Assets</th>
                <th class="text-end">Total UPB</th>
                <th class="text-end">Avg UPB</th>
                <th class="text-end">Avg LTV</th>
                <th class="text-center">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in gridData" :key="row.id">
                <td class="fw-semibold">
                  <i class="mdi mdi-wallet text-warning me-1"></i>
                  {{ row.name }}
                </td>
                <td class="text-end">{{ formatNumber(row.asset_count) }}</td>
                <td class="text-end fw-semibold">{{ formatCurrency(row.total_upb) }}</td>
                <td class="text-end text-muted">{{ formatCurrency(row.avg_upb) }}</td>
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

const fundMetrics = computed(() => {
  return props.chartData.map(item => ({
    name: item.x,
    count: item.meta?.count || 0,
    upb: item.y,
    ltv: item.meta?.ltv || 0
  }))
})

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
        backgroundColor: 'rgba(255, 193, 7, 0.6)',
        borderColor: 'rgba(255, 193, 7, 1)',
        borderWidth: 1,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      onClick: (event, elements) => {
        if (elements.length > 0) {
          const index = elements[0].index
          handleChartClick(props.chartData[index])
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: (value) => `$${(Number(value) / 1_000_000).toFixed(1)}MM`
          }
        }
      },
      plugins: {
        tooltip: {
          callbacks: {
            label: (context) => `UPB: $${(context.parsed.y / 1_000_000).toFixed(2)}MM`
          }
        }
      }
    }
  })
}

function handleChartClick(data: any): void {
  emit('drill-down', { type: 'fund', data })
}

function handleDrillDown(row: any): void {
  emit('drill-down', { type: 'fund', data: row })
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
.fund-metrics .card {
  border: none;
  transition: transform 0.2s;
}

.fund-metrics .card:hover {
  transform: translateX(5px);
}

.table th {
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.75rem;
  color: #6c757d;
  border-bottom: 2px solid #dee2e6;
}
</style>
