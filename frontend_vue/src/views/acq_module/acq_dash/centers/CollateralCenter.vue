<template>
  <Layout>
    <b-row>
      <b-col class="col-12">
        <div class="page-title-box">
          <div class="page-title-right">
            <router-link to="/acquisitions" class="btn btn-success btn-sm">
              <i class="ri-arrow-left-line me-1"></i>Back to Dashboard
            </router-link>
          </div>
          <h4 class="page-title">
            <i class="ri-home-4-line me-2"></i>
            Collateral Center
          </h4>
        </div>
      </b-col>
    </b-row>

    <!-- Trade Info Bar -->
    <b-row v-if="hasSelection" class="mb-2">
      <b-col>
        <div class="card bg-success text-white mb-0">
          <div class="card-body py-2">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <i class="uil uil-briefcase me-2"></i>
                <strong>{{ currentTradeName }}</strong>
                <span class="mx-2">•</span>
                <strong>{{ currentSellerName }}</strong>
                <span class="mx-2">•</span>
                <span>{{ totalAssets }} Assets</span>
              </div>
            </div>
          </div>
        </div>
      </b-col>
    </b-row>

    <!-- Inspection Summary Cards -->
    <b-row v-if="hasSelection" class="g-2 mb-2">
      <b-col xl="3" lg="6">
        <div class="card tilebox-one mb-0">
          <div class="card-body pt-3 pb-2 px-3">
            <i class="uil uil-eye float-end"></i>
            <h6 class="text-uppercase mt-0">Inspections Ordered</h6>
            <h2 class="my-2 fs-3">{{ metrics.ordered }} / {{ totalAssets }}</h2>
            <p class="mb-0 text-muted">
              <span class="badge bg-success">{{ metrics.ordered_pct }}%</span>
              <span class="ms-2">Complete</span>
            </p>
          </div>
        </div>
      </b-col>

      <b-col xl="3" lg="6">
        <div class="card tilebox-one mb-0">
          <div class="card-body pt-3 pb-2 px-3">
            <i class="uil uil-camera float-end"></i>
            <h6 class="text-uppercase mt-0">Photos Received</h6>
            <h2 class="my-2 fs-3">{{ metrics.photos }} / {{ totalAssets }}</h2>
            <p class="mb-0 text-muted">
              <span class="badge bg-info">{{ metrics.photos_pct }}%</span>
              <span class="ms-2">Complete</span>
            </p>
          </div>
        </div>
      </b-col>

      <b-col xl="3" lg="6">
        <div class="card tilebox-one mb-0">
          <div class="card-body pt-3 pb-2 px-3">
            <i class="uil uil-wrench float-end"></i>
            <h6 class="text-uppercase mt-0">Repairs Identified</h6>
            <h2 class="my-2 fs-3">{{ metrics.repairs }}</h2>
            <p class="mb-0 text-muted">
              <span class="text-warning">{{ formatCurrency(metrics.repair_cost) }}</span>
              <span class="ms-2">Est. Cost</span>
            </p>
          </div>
        </div>
      </b-col>

      <b-col xl="3" lg="6">
        <div class="card tilebox-one mb-0">
          <div class="card-body pt-3 pb-2 px-3">
            <i class="uil uil-check-circle float-end"></i>
            <h6 class="text-uppercase mt-0">Fully Reviewed</h6>
            <h2 class="my-2 fs-3">{{ metrics.reviewed }} / {{ totalAssets }}</h2>
            <p class="mb-0 text-muted">
              <span class="badge bg-primary">{{ metrics.reviewed_pct }}%</span>
              <span class="ms-2">Complete</span>
            </p>
          </div>
        </div>
      </b-col>
    </b-row>

    <!-- Main Content -->
    <b-row v-if="hasSelection">
      <b-col>
        <div class="card">
          <div class="card-body">
            <ul class="nav nav-tabs nav-bordered mb-3">
              <li class="nav-item">
                <a href="#inspections" data-bs-toggle="tab" class="nav-link active">
                  <i class="ri-eye-line me-1"></i>Inspections
                </a>
              </li>
              <li class="nav-item">
                <a href="#photos" data-bs-toggle="tab" class="nav-link">
                  <i class="ri-image-line me-1"></i>Photo Gallery
                </a>
              </li>
              <li class="nav-item">
                <a href="#repairs" data-bs-toggle="tab" class="nav-link">
                  <i class="ri-tools-line me-1"></i>Repairs & Issues
                </a>
              </li>
              <li class="nav-item">
                <a href="#vendors" data-bs-toggle="tab" class="nav-link">
                  <i class="ri-team-line me-1"></i>Vendor Management
                </a>
              </li>
            </ul>

            <div class="tab-content">
              <!-- Inspections Tab -->
              <div class="tab-pane show active" id="inspections">
                <div class="d-flex justify-content-between align-items-center mb-3">
                  <h5 class="mb-0">Inspection Status</h5>
                  <button class="btn btn-sm btn-success">
                    <i class="ri-add-line me-1"></i>Order Inspections
                  </button>
                </div>
                <div class="table-responsive">
                  <table class="table table-hover table-centered mb-0">
                    <thead class="table-light">
                      <tr>
                        <th>Property</th>
                        <th>Type</th>
                        <th>Inspector</th>
                        <th>Scheduled Date</th>
                        <th>Status</th>
                        <th>Report</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td colspan="7" class="text-center text-muted py-4">
                          <i class="ri-information-line me-1"></i>
                          Inspection tracking data will appear here
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <!-- Photos Tab -->
              <div class="tab-pane" id="photos">
                <div class="alert alert-info mb-3">
                  <i class="ri-gallery-line me-1"></i>
                  Manage property photos from inspections, brokers, and public sources
                </div>
                <div class="row g-2">
                  <div class="col-md-4 col-lg-3">
                    <div class="card border">
                      <div class="card-body text-center py-4">
                        <i class="ri-image-add-line display-4 text-muted mb-2"></i>
                        <p class="mb-2 text-muted small">No photos available</p>
                        <button class="btn btn-sm btn-outline-primary">
                          <i class="ri-upload-line me-1"></i>Upload
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Repairs Tab -->
              <div class="tab-pane" id="repairs">
                <h5 class="mb-3">Repair & Issue Tracker</h5>
                <div class="row">
                  <div class="col-lg-8">
                    <div class="table-responsive">
                      <table class="table table-sm table-striped">
                        <thead>
                          <tr>
                            <th>Property</th>
                            <th>Issue Type</th>
                            <th>Severity</th>
                            <th>Est. Cost</th>
                            <th>Status</th>
                            <th>Actions</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr>
                            <td colspan="6" class="text-center text-muted py-3">
                              No repair items tracked yet
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                  <div class="col-lg-4">
                    <div class="card border border-warning">
                      <div class="card-body">
                        <h6 class="text-warning">Issue Summary</h6>
                        <div class="mb-2">
                          <div class="d-flex justify-content-between">
                            <span>Critical:</span>
                            <strong class="text-danger">0</strong>
                          </div>
                          <div class="d-flex justify-content-between">
                            <span>High Priority:</span>
                            <strong class="text-warning">0</strong>
                          </div>
                          <div class="d-flex justify-content-between">
                            <span>Low Priority:</span>
                            <strong class="text-muted">0</strong>
                          </div>
                        </div>
                        <hr/>
                        <div class="d-flex justify-content-between">
                          <span>Total Est. Repairs:</span>
                          <strong>$0</strong>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Vendors Tab -->
              <div class="tab-pane" id="vendors">
                <h5 class="mb-3">Vendor & Inspector Management</h5>
                <div class="row g-3">
                  <div class="col-md-6">
                    <div class="card border">
                      <div class="card-body">
                        <h6><i class="ri-user-star-line me-1"></i>Active Inspectors</h6>
                        <p class="text-muted small mb-2">Manage inspector relationships and performance</p>
                        <div class="list-group list-group-flush">
                          <div class="list-group-item text-center text-muted py-3">
                            No vendors assigned
                          </div>
                        </div>
                        <button class="btn btn-sm btn-outline-primary mt-2">
                          <i class="ri-add-line me-1"></i>Add Vendor
                        </button>
                      </div>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="card border">
                      <div class="card-body">
                        <h6><i class="ri-bar-chart-line me-1"></i>Vendor Performance</h6>
                        <p class="text-muted small mb-2">Track quality, turnaround time, and costs</p>
                        <div class="text-center text-muted py-4">
                          Analytics coming soon
                        </div>
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
            <i class="ri-home-4-line display-1 text-muted mb-3"></i>
            <h4>No Trade Selected</h4>
            <p class="text-muted">Select a seller and trade from the Acquisitions Dashboard to manage collateral inspections.</p>
            <router-link to="/acquisitions" class="btn btn-success mt-2">
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
import http from '@/lib/http'

const acqStore = useAcqSelectionsStore()
const { selectedSellerId, selectedTradeId, sellerOptions, tradeOptions } = storeToRefs(acqStore)
const gridStore = useAgGridRowsStore()
const { rows } = storeToRefs(gridStore)

// WHAT: Pool summary data from backend API (single source of truth)
// WHY: All aggregations should come from backend, not frontend grid
// HOW: Fetch from /api/acq/summary/pool/{seller_id}/{trade_id}/
const poolSummary = ref<any>(null)
const poolLoading = ref(false)

const hasSelection = computed(() => !!selectedSellerId.value && !!selectedTradeId.value)
// WHAT: Total assets from backend pool summary (excludes dropped assets automatically)
// WHY: Backend uses sellertrade_qs() which filters acq_status != DROP by default
// HOW: Fetch from pool summary API, fallback to 0 if not loaded
const totalAssets = computed(() => poolSummary.value?.assets ?? 0)
const currentSellerName = computed(() => sellerOptions.value.find(s => s.id === selectedSellerId.value)?.name || 'Unknown')
const currentTradeName = computed(() => tradeOptions.value.find(t => t.id === selectedTradeId.value)?.trade_name || 'Unknown')

// WHAT: Collateral metrics from backend API
// WHY: All aggregations come from backend, not frontend grid
const collateralMetrics = ref<any>(null)

// WHAT: Computed metrics with percentages
// WHY: Display both count and percentage for each metric
const metrics = computed(() => {
  if (!collateralMetrics.value) {
    return {
      ordered: 0,
      ordered_pct: 0,
      photos: 0,
      photos_pct: 0,
      repairs: 0,
      repair_cost: 0,
      reviewed: 0,
      reviewed_pct: 0,
    }
  }
  
  const total = totalAssets.value || 1
  return {
    ordered: collateralMetrics.value.ordered || 0,
    ordered_pct: Math.round(((collateralMetrics.value.ordered || 0) / total) * 100),
    photos: collateralMetrics.value.photos || 0,
    photos_pct: Math.round(((collateralMetrics.value.photos || 0) / total) * 100),
    repairs: collateralMetrics.value.repairs || 0,
    repair_cost: collateralMetrics.value.repair_cost || 0,
    reviewed: collateralMetrics.value.reviewed || 0,
    reviewed_pct: Math.round(((collateralMetrics.value.reviewed || 0) / total) * 100),
  }
})

function formatCurrency(val: number): string {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val)
}

// WHAT: Fetch collateral metrics from backend API
// WHY: All aggregations come from backend, not frontend grid
// HOW: Call /api/acq/summary/collateral/{seller_id}/{trade_id}/
async function fetchCollateralMetrics() {
  if (!selectedSellerId.value || !selectedTradeId.value) {
    collateralMetrics.value = null
    return
  }
  
  try {
    const resp = await http.get(`/acq/summary/collateral/${selectedSellerId.value}/${selectedTradeId.value}/`)
    collateralMetrics.value = resp.data
    console.log('[CollateralCenter] Collateral metrics loaded:', collateralMetrics.value)
  } catch (err: any) {
    console.error('[CollateralCenter] Failed to fetch collateral metrics:', err)
    collateralMetrics.value = null
  }
}

// WHAT: Fetch pool summary from backend API
// WHY: Get total asset count from backend (single source of truth)
// HOW: Call /api/acq/summary/pool/{seller_id}/{trade_id}/
async function fetchPoolSummary() {
  if (!selectedSellerId.value || !selectedTradeId.value) {
    poolSummary.value = null
    return
  }
  
  poolLoading.value = true
  try {
    const resp = await http.get(`/acq/summary/pool/${selectedSellerId.value}/${selectedTradeId.value}/`)
    poolSummary.value = resp.data
    console.log('[CollateralCenter] Pool summary loaded:', poolSummary.value)
  } catch (err: any) {
    console.error('[CollateralCenter] Failed to fetch pool summary:', err)
    poolSummary.value = null
  } finally {
    poolLoading.value = false
  }
}

onMounted(async () => {
  // WHAT: Load pool summary first (contains total asset count)
  // WHY: Total assets needed for all N/Total displays
  // HOW: Fetch from /api/acq/summary/pool/{seller_id}/{trade_id}/
  await fetchPoolSummary()
  
  // WHAT: Load collateral metrics from backend
  // WHY: All aggregations come from backend APIs, not grid data
  await fetchCollateralMetrics()
  
  // WHAT: Load grid data if needed (for display table only, not aggregations)
  // WHY: Grid displays individual asset rows, but does NOT aggregate
  if (hasSelection.value && (!rows.value || rows.value.length === 0)) {
    await gridStore.fetchRows(selectedSellerId.value!, selectedTradeId.value!, 'all')
  }
})
</script>

<style scoped>
/* Additional styling if needed */
</style>
