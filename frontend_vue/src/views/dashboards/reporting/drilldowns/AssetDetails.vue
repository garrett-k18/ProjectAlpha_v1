<template>
  <div class="asset-details">
    <div v-if="!data" class="text-center py-4 text-muted">
      <p>No asset data selected</p>
    </div>

    <div v-else>
      <div class="card bg-light mb-3">
        <div class="card-body">
          <h5 class="card-title mb-3">Asset Information</h5>
          <div class="row g-3">
            <div class="col-md-6">
              <small class="text-muted d-block">Asset ID</small>
              <span class="fw-semibold">{{ data.id || data.asset_id || 'N/A' }}</span>
            </div>
            <div class="col-md-6">
              <small class="text-muted d-block">Address</small>
              <span class="fw-semibold">{{ data.address || 'N/A' }}</span>
            </div>
            <div class="col-md-6">
              <small class="text-muted d-block">Current Balance</small>
              <span class="fw-semibold">{{ formatCurrency(data.current_balance) }}</span>
            </div>
            <div class="col-md-6">
              <small class="text-muted d-block">LTV</small>
              <span :class="getLtvClass(data.ltv)">{{ formatPercent(data.ltv) }}</span>
            </div>
            <div class="col-md-6">
              <small class="text-muted d-block">Property Type</small>
              <span>{{ data.property_type || 'N/A' }}</span>
            </div>
            <div class="col-md-6">
              <small class="text-muted d-block">State</small>
              <span>{{ data.state || 'N/A' }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="alert alert-info">
        <i class="mdi mdi-information-outline me-2"></i>
        Click "View Full Details" to see complete asset information in the loan-level view.
      </div>

      <div class="d-flex justify-content-end">
        <button class="btn btn-primary">
          <i class="mdi mdi-eye me-1"></i>
          View Full Details
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  data: any
}>()

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
</script>
