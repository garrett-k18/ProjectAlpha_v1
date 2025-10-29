<template>
  <div class="trade-details">
    <div v-if="!data" class="text-center py-4 text-muted">
      <p>No trade data selected</p>
    </div>

    <div v-else>
      <div class="card bg-light mb-3">
        <div class="card-body">
          <h5 class="card-title mb-3">{{ data.trade_name || 'Trade Details' }}</h5>
          <b-row>
            <b-col md="6">
              <div class="mb-2">
                <small class="text-muted d-block">Seller</small>
                <span class="fw-semibold">{{ data.seller_name || 'N/A' }}</span>
              </div>
              <div class="mb-2">
                <small class="text-muted d-block">Status</small>
                <span :class="['badge', getStatusClass(data.status)]">{{ data.status || 'N/A' }}</span>
              </div>
              <div class="mb-2">
                <small class="text-muted d-block">Asset Count</small>
                <span class="fw-semibold">{{ formatNumber(data.asset_count) }}</span>
              </div>
            </b-col>
            <b-col md="6">
              <div class="mb-2">
                <small class="text-muted d-block">Total UPB</small>
                <span class="fw-semibold">{{ formatCurrency(data.total_upb) }}</span>
              </div>
              <div class="mb-2">
                <small class="text-muted d-block">Avg LTV</small>
                <span :class="getLtvClass(data.avg_ltv)">{{ formatPercent(data.avg_ltv) }}</span>
              </div>
              <div class="mb-2">
                <small class="text-muted d-block">Bid Date</small>
                <span>{{ formatDate(data.bid_date) || 'N/A' }}</span>
              </div>
            </b-col>
          </b-row>
        </div>
      </div>

      <h6 class="mb-3">Trade Metrics</h6>
      <b-row class="g-2 mb-3">
        <b-col cols="6" md="3">
          <div class="card text-center">
            <div class="card-body py-2">
              <div class="text-muted small">Total Debt</div>
              <div class="fw-bold">{{ formatCurrency(data.total_debt) }}</div>
            </div>
          </div>
        </b-col>
        <b-col cols="6" md="3">
          <div class="card text-center">
            <div class="card-body py-2">
              <div class="text-muted small">As-Is Value</div>
              <div class="fw-bold">{{ formatCurrency(data.asis_value) }}</div>
            </div>
          </div>
        </b-col>
        <b-col cols="6" md="3">
          <div class="card text-center">
            <div class="card-body py-2">
              <div class="text-muted small">States</div>
              <div class="fw-bold">{{ data.state_count || 0 }}</div>
            </div>
          </div>
        </b-col>
        <b-col cols="6" md="3">
          <div class="card text-center">
            <div class="card-body py-2">
              <div class="text-muted small">Delinquency</div>
              <div class="fw-bold">{{ formatPercent(data.delinquency_rate) }}</div>
            </div>
          </div>
        </b-col>
      </b-row>

      <div class="d-flex justify-content-end gap-2 mt-3">
        <button class="btn btn-sm btn-outline-primary">
          <i class="mdi mdi-file-chart me-1"></i>
          View Full Report
        </button>
        <button class="btn btn-sm btn-primary">
          <i class="mdi mdi-eye me-1"></i>
          View Assets
        </button>
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

function formatDate(date: any): string {
  if (!date) return ''
  return new Date(date).toLocaleDateString()
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
