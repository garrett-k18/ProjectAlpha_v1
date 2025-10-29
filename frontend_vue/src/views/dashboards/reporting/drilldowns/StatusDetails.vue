<template>
  <div class="status-details">
    <div v-if="!data" class="text-center py-4 text-muted">
      <p>No status data selected</p>
    </div>

    <div v-else>
      <div class="card bg-light mb-3">
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <h5 class="mb-0">
              Status: <span :class="['badge', getStatusClass(data.status)]">{{ data.status }}</span>
            </h5>
          </div>
          <b-row>
            <b-col md="4">
              <div class="text-center">
                <div class="text-muted small">Asset Count</div>
                <div class="h4 mb-0">{{ formatNumber(data.count) }}</div>
              </div>
            </b-col>
            <b-col md="4">
              <div class="text-center">
                <div class="text-muted small">Total UPB</div>
                <div class="h4 mb-0">{{ formatCurrency(data.total_upb) }}</div>
              </div>
            </b-col>
            <b-col md="4">
              <div class="text-center">
                <div class="text-muted small">Percentage</div>
                <div class="h4 mb-0">{{ formatPercent(data.percentage) }}</div>
              </div>
            </b-col>
          </b-row>
        </div>
      </div>

      <h6 class="mb-3">Status Breakdown</h6>
      <div class="table-responsive">
        <table class="table table-sm table-hover">
          <thead>
            <tr>
              <th>Metric</th>
              <th class="text-end">Value</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Average UPB</td>
              <td class="text-end fw-semibold">{{ formatCurrency(data.avg_upb) }}</td>
            </tr>
            <tr>
              <td>Average LTV</td>
              <td class="text-end" :class="getLtvClass(data.avg_ltv)">{{ formatPercent(data.avg_ltv) }}</td>
            </tr>
            <tr>
              <td>Total Debt</td>
              <td class="text-end">{{ formatCurrency(data.total_debt) }}</td>
            </tr>
            <tr>
              <td>Delinquency Rate</td>
              <td class="text-end">{{ formatPercent(data.delinquency_rate) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  data: any
}>()

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
  const map: Record<string, string> = {
    'DD': 'bg-info',
    'AWARDED': 'bg-success',
    'PASS': 'bg-secondary',
    'BOARD': 'bg-primary'
  }
  return map[status] || 'bg-secondary'
}
</script>
