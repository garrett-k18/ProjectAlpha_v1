<template>
  <Layout>
    <b-row>
      <b-col class="col-12">
        <div class="page-title-box">
          <div class="page-title-right">
            <router-link to="/acquisitions" class="btn btn-primary btn-sm">
              <i class="ri-arrow-left-line me-1"></i>Back to Dashboard
            </router-link>
          </div>
          <h4 class="page-title">
            <i class="ri-line-chart-line me-2"></i>
            Valuation Center
            <span v-if="hasSelection" class="text-muted fs-5 ms-3 fw-normal">
              {{ currentTradeName }} • {{ totalAssets }} Assets
            </span>
          </h4>
        </div>
      </b-col>
    </b-row>

    <!-- Valuation Summary Cards -->
    <b-row v-if="hasSelection" class="g-2 mb-2">
      <b-col xl="" lg="4" md="6">
        <div class="card tilebox-one mb-0">
          <div class="card-body pt-3 pb-2 px-3">
            <i class="uil uil-building float-end"></i>
            <h6 class="text-uppercase mt-0">Seller Values</h6>
            <h2 class="my-2 fs-3">{{ valuationMetrics.seller_count }} / {{ totalAssets }}</h2>
            <p class="mb-0 text-muted">
              <span class="badge" :class="progressBadgeClass(valuationMetrics.seller_count, totalAssets)">
                {{ valuationMetrics.seller_pct }}%
              </span>
              <span class="ms-2">Complete</span>
            </p>
          </div>
        </div>
      </b-col>

      <b-col xl="" lg="4" md="6">
        <div class="card tilebox-one mb-0">
          <div class="card-body pt-3 pb-2 px-3">
            <i class="uil uil-file-alt float-end"></i>
            <h6 class="text-uppercase mt-0">BPO Values</h6>
            <h2 class="my-2 fs-3">{{ valuationMetrics.bpo_count }} / {{ totalAssets }}</h2>
            <p class="mb-0 text-muted">
              <span class="badge" :class="progressBadgeClass(valuationMetrics.bpo_count, totalAssets)">
                {{ valuationMetrics.bpo_pct }}%
              </span>
              <span class="ms-2">Complete</span>
            </p>
          </div>
        </div>
      </b-col>

      <b-col xl="" lg="4" md="6">
        <div class="card tilebox-one mb-0">
          <div class="card-body pt-3 pb-2 px-3">
            <i class="uil uil-user-check float-end"></i>
            <h6 class="text-uppercase mt-0">Broker Values</h6>
            <h2 class="my-2 fs-3">{{ valuationMetrics.broker_count }} / {{ totalAssets }}</h2>
            <p class="mb-0 text-muted">
              <span class="badge" :class="progressBadgeClass(valuationMetrics.broker_count, totalAssets)">
                {{ valuationMetrics.broker_pct }}%
              </span>
              <span class="ms-2">Complete</span>
            </p>
          </div>
        </div>
      </b-col>

      <b-col xl="" lg="4" md="6">
        <div class="card tilebox-one mb-0">
          <div class="card-body pt-3 pb-2 px-3">
            <i class="uil uil-shield-check float-end"></i>
            <h6 class="text-uppercase mt-0">Reconciled</h6>
            <h2 class="my-2 fs-3">{{ valuationMetrics.reconciled_count }} / {{ totalAssets }}</h2>
            <p class="mb-0 text-muted">
              <span class="badge" :class="progressBadgeClass(valuationMetrics.reconciled_count, totalAssets)">
                {{ valuationMetrics.reconciled_pct }}%
              </span>
              <span class="ms-2">Complete</span>
            </p>
          </div>
        </div>
      </b-col>

      <b-col xl="" lg="4" md="6">
        <div class="card tilebox-one mb-0">
          <div class="card-body pt-3 pb-2 px-3">
            <i class="uil uil-exclamation-triangle float-end text-warning"></i>
            <h6 class="text-uppercase mt-0">Variances</h6>
            <h2 class="my-2 fs-3">{{ valuationMetrics.variance_count }}</h2>
            <p class="mb-0 text-muted">
              <span class="text-warning">{{ valuationMetrics.variance_pct }}%</span>
              <span class="ms-2">&gt;10% Diff</span>
            </p>
          </div>
        </div>
      </b-col>
    </b-row>

    <!-- Main Content Tabs -->
    <b-row v-if="hasSelection">
      <b-col>
        <div class="card">
          <div class="card-body">
            <ul class="nav nav-tabs nav-bordered mb-3">
              <li class="nav-item">
                <a href="#overview" data-bs-toggle="tab" class="nav-link active">
                  <i class="ri-dashboard-line me-1"></i>Overview
                </a>
              </li>
              <li class="nav-item">
                <a href="#bpo-tracker" data-bs-toggle="tab" class="nav-link">
                  <i class="ri-file-list-line me-1"></i>BPO Tracker
                </a>
              </li>
              <li class="nav-item">
                <a href="#reconciliation" data-bs-toggle="tab" class="nav-link">
                  <i class="ri-scales-line me-1"></i>Reconciliation
                </a>
              </li>
              <li class="nav-item">
                <a href="#bulk-actions" data-bs-toggle="tab" class="nav-link">
                  <i class="ri-tools-line me-1"></i>Bulk Actions
                </a>
              </li>
            </ul>

            <div class="tab-content">
              <!-- Overview Tab -->
              <div class="tab-pane show active" id="overview">
                <h5 class="mb-3">Valuation Summary Table</h5>
                <div class="table-responsive">
                  <table class="table table-centered table-hover mb-0">
                    <thead class="table-light">
                      <tr>
                        <th>Address</th>
                        <th>Seller AIV</th>
                        <th>Broker AIV</th>
                        <th>Internal AIV</th>
                        <th>Variance</th>
                        <th>Status</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-if="!rows || rows.length === 0">
                        <td colspan="7" class="text-center text-muted py-3">
                          No assets to display
                        </td>
                      </tr>
                      <tr v-for="asset in (rows as any[])" :key="asset.asset_hub_id">
                        <td>
                          <div class="fw-semibold">{{ asset.property_address || '-' }}</div>
                          <div class="text-muted small">{{ asset.property_city }}, {{ asset.property_state }}</div>
                        </td>
                        <td>{{ formatCurrency(asset.seller_asis_value as number) }}</td>
                        <td>{{ formatCurrency(asset.broker_asis_value as number) }}</td>
                        <td>{{ formatCurrency(asset.internal_initial_uw_asis_value as number) }}</td>
                        <td>
                          <span :class="varianceClass(calculateVariance(asset))">
                            {{ formatPercent(calculateVariance(asset)) }}
                          </span>
                        </td>
                        <td>
                          <span class="badge" :class="statusBadgeClass(getValuationStatus(asset))">
                            {{ getValuationStatus(asset) }}
                          </span>
                        </td>
                        <td>
                          <button class="btn btn-sm btn-light me-1" title="View Details">
                            <i class="ri-eye-line"></i>
                          </button>
                          <button class="btn btn-sm btn-light" title="Edit">
                            <i class="ri-edit-line"></i>
                          </button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <!-- BPO Tracker Tab -->
              <div class="tab-pane" id="bpo-tracker">
                <div class="row">
                  <div class="col-lg-8">
                    <h5 class="mb-3">BPO Assignment & Status</h5>
                    <div class="alert alert-info">
                      <i class="ri-information-line me-1"></i>
                      Manage BPO orders, assignments, and review statuses for the entire trade
                    </div>
                    <div class="table-responsive">
                      <table class="table table-sm table-striped">
                        <thead>
                          <tr>
                            <th>Property</th>
                            <th>BPO Company</th>
                            <th>Order Date</th>
                            <th>Received Date</th>
                            <th>Status</th>
                            <th>Actions</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr>
                            <td colspan="6" class="text-center text-muted py-4">
                              BPO tracking integration coming soon
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                  <div class="col-lg-4">
                    <div class="card border">
                      <div class="card-body">
                        <h5 class="card-title">Quick Stats</h5>
                        <div class="mb-3">
                          <div class="d-flex justify-content-between mb-2">
                            <span>BPOs Ordered:</span>
                            <strong>0</strong>
                          </div>
                          <div class="d-flex justify-content-between mb-2">
                            <span>BPOs Received:</span>
                            <strong>0</strong>
                          </div>
                          <div class="d-flex justify-content-between">
                            <span>Avg Turnaround:</span>
                            <strong>-- days</strong>
                          </div>
                        </div>
                        <button class="btn btn-primary btn-sm w-100">
                          <i class="ri-add-line me-1"></i>Order BPO Batch
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Reconciliation Tab -->
              <div class="tab-pane" id="reconciliation">
                <h5 class="mb-3">Value Reconciliation</h5>
                <div class="alert alert-warning">
                  <i class="ri-alert-line me-1"></i>
                  Review and reconcile valuation discrepancies across all sources
                </div>
                <div class="row">
                  <div class="col-12">
                    <div class="card border border-warning">
                      <div class="card-body">
                        <h6 class="text-warning"><i class="ri-error-warning-line me-1"></i>High Variance Assets</h6>
                        <p class="text-muted small">Assets with >10% variance between valuation sources</p>
                        <div class="table-responsive">
                          <table class="table table-sm mb-0">
                            <thead>
                              <tr>
                                <th>Address</th>
                                <th>Source 1</th>
                                <th>Source 2</th>
                                <th>Variance</th>
                                <th>Action</th>
                              </tr>
                            </thead>
                            <tbody>
                              <tr>
                                <td colspan="5" class="text-center text-muted py-3">
                                  No high-variance assets found
                                </td>
                              </tr>
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Bulk Actions Tab -->
              <div class="tab-pane" id="bulk-actions">
                <h5 class="mb-3">Bulk Operations</h5>
                <div class="row g-3">
                  <div class="col-md-6">
                    <div class="card border">
                      <div class="card-body">
                        <h6><i class="ri-upload-cloud-line me-1"></i>Import Valuations</h6>
                        <p class="text-muted small">Bulk import values from CSV or Excel</p>
                        <button class="btn btn-outline-primary btn-sm">
                          <i class="ri-file-excel-line me-1"></i>Upload File
                        </button>
                      </div>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="card border">
                      <div class="card-body">
                        <h6><i class="ri-download-cloud-line me-1"></i>Export Report</h6>
                        <p class="text-muted small">Download valuation summary report</p>
                        <button class="btn btn-outline-success btn-sm">
                          <i class="ri-file-download-line me-1"></i>Export CSV
                        </button>
                      </div>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="card border">
                      <div class="card-body">
                        <h6><i class="ri-refresh-line me-1"></i>Refresh Zillow Data</h6>
                        <p class="text-muted small">Pull latest Zillow estimates</p>
                        <button class="btn btn-outline-info btn-sm">
                          <i class="ri-refresh-line me-1"></i>Refresh All
                        </button>
                      </div>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="card border">
                      <div class="card-body">
                        <h6><i class="ri-check-double-line me-1"></i>Auto-Reconcile</h6>
                        <p class="text-muted small">Auto-approve values within threshold</p>
                        <button class="btn btn-outline-warning btn-sm">
                          <i class="ri-magic-line me-1"></i>Run Auto-Reconcile
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </b-col>
    </b-row>

    <!-- Empty State -->
    <b-row v-if="!hasSelection">
      <b-col>
        <div class="card">
          <div class="card-body text-center py-5">
            <i class="ri-line-chart-line display-1 text-muted mb-3"></i>
            <h4>No Trade Selected</h4>
            <p class="text-muted">Please select a seller and trade from the Acquisitions Dashboard to view valuation data.</p>
            <router-link to="/acquisitions" class="btn btn-primary mt-2">
              <i class="ri-arrow-left-line me-1"></i>Go to Acquisitions Dashboard
            </router-link>
          </div>
        </div>
      </b-col>
    </b-row>
  </Layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useAcqSelectionsStore } from '@/stores/acqSelections'
import { useAgGridRowsStore } from '@/stores/agGridRows'
import Layout from '@/components/layouts/layout.vue'

// Stores
const acqStore = useAcqSelectionsStore()
const { selectedSellerId, selectedTradeId, sellerOptions, tradeOptions } = storeToRefs(acqStore)
const gridStore = useAgGridRowsStore()
const { rows } = storeToRefs(gridStore)

// Computed
const hasSelection = computed(() => !!selectedSellerId.value && !!selectedTradeId.value)
const totalAssets = computed(() => Array.isArray(rows.value) ? rows.value.length : 0)
const currentSellerName = computed(() => {
  const seller = sellerOptions.value.find(s => s.id === selectedSellerId.value)
  return seller?.name || 'Unknown'
})
const currentTradeName = computed(() => {
  const trade = tradeOptions.value.find(t => t.id === selectedTradeId.value)
  return trade?.trade_name || 'Unknown'
})

// Valuation metrics (calculated from grid rows)
const valuationMetrics = computed(() => {
  const assets = rows.value || []
  const total = assets.length
  
  if (!total) return {
    seller_count: 0,
    seller_pct: 0,
    bpo_count: 0,
    bpo_pct: 0,
    broker_count: 0,
    broker_pct: 0,
    internal_count: 0,
    internal_pct: 0,
    reconciled_count: 0,
    reconciled_pct: 0,
    variance_count: 0,
    variance_pct: 0,
  }
  
  const seller_count = assets.filter((a: any) => a.seller_asis_value != null).length
  // BPO is stored in additional_asis_value field
  const bpo_count = assets.filter((a: any) => a.additional_asis_value != null).length
  // Broker values come from broker_asis_value field
  const broker_count = assets.filter((a: any) => a.broker_asis_value != null).length
  const internal_count = assets.filter((a: any) => a.internal_initial_uw_asis_value != null).length
  const reconciled_count = assets.filter((a: any) => 
    a.seller_asis_value != null && (a.broker_asis_value != null || a.additional_asis_value != null) && a.internal_initial_uw_asis_value != null
  ).length
  
  // Count assets with >10% variance between any two valuation sources
  const variance_count = assets.filter((a: any) => {
    const variance = calculateVariance(a)
    return variance != null && Math.abs(variance) > 0.1
  }).length
  
  return {
    seller_count,
    seller_pct: Math.round((seller_count / total) * 100),
    bpo_count,
    bpo_pct: Math.round((bpo_count / total) * 100),
    broker_count,
    broker_pct: Math.round((broker_count / total) * 100),
    internal_count,
    internal_pct: Math.round((internal_count / total) * 100),
    reconciled_count,
    reconciled_pct: Math.round((reconciled_count / total) * 100),
    variance_count,
    variance_pct: Math.round((variance_count / total) * 100),
  }
})

// Helper functions
// Calculate variance between seller and broker values
function calculateVariance(asset: any): number | null {
  const seller = asset.seller_asis_value
  const broker = asset.broker_asis_value
  if (!seller || !broker) return null
  return (broker - seller) / seller
}

// Determine valuation status based on available data
function getValuationStatus(asset: any): string {
  const hasSeller = asset.seller_asis_value != null
  const hasBroker = asset.broker_asis_value != null
  const hasInternal = asset.internal_initial_uw_asis_value != null
  
  if (hasSeller && hasBroker && hasInternal) {
    const variance = calculateVariance(asset)
    if (variance && Math.abs(variance) > 0.1) return 'Review'
    return 'Approved'
  }
  if (!hasBroker) return 'Pending BPO'
  if (!hasInternal) return 'Pending UW'
  return 'In Progress'
}

function formatCurrency(val: number | null): string {
  if (val == null) return '-'
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val)
}

function formatPercent(val: number | null): string {
  if (val == null) return '-'
  return `${(val * 100).toFixed(1)}%`
}

function progressBadgeClass(completed: number, total: number): string {
  if (!total) return 'bg-secondary'
  const pct = (completed / total) * 100
  if (pct === 100) return 'bg-success'
  if (pct >= 50) return 'bg-warning'
  return 'bg-secondary'
}

function varianceClass(variance: number | null): string {
  if (variance == null) return 'text-muted'
  if (variance > 0.1) return 'text-danger fw-bold'
  if (variance < -0.1) return 'text-success fw-bold'
  return 'text-muted'
}

function statusBadgeClass(status: string): string {
  const map: Record<string, string> = {
    'Approved': 'bg-success',
    'Review': 'bg-warning',
    'Pending BPO': 'bg-secondary',
    'Rejected': 'bg-danger',
  }
  return map[status] || 'bg-secondary'
}

onMounted(() => {
  // Load data if needed
  if (hasSelection.value && (!rows.value || rows.value.length === 0)) {
    gridStore.fetchRows(selectedSellerId.value!, selectedTradeId.value!, 'all')
  }
})
</script>

<style scoped>
/* Additional styling if needed */
</style>
