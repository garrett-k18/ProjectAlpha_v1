<template>
  <Layout>
    <b-row>
      <b-col class="col-12">
        <div class="page-title-box">
          <div class="page-title-right">
            <router-link to="/acquisitions" class="btn btn-info btn-sm">
              <i class="ri-arrow-left-line me-1"></i>Back to Dashboard
            </router-link>
          </div>
          <h4 class="page-title">
            <i class="ri-file-shield-line me-2"></i>
            Title Center
          </h4>
        </div>
      </b-col>
    </b-row>

    <!-- Trade Info Bar -->
    <b-row v-if="hasSelection" class="mb-2">
      <b-col>
        <div class="card bg-info text-white mb-0">
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

    <!-- Title Summary Cards -->
    <b-row v-if="hasSelection" class="g-2 mb-2">
      <b-col xl="3" lg="6">
        <div class="card tilebox-one mb-0">
          <div class="card-body pt-3 pb-2 px-3">
            <i class="uil uil-file-alt float-end"></i>
            <h6 class="text-uppercase mt-0">Title Reports Ordered</h6>
            <h2 class="my-2 fs-3">{{ metrics.ordered }} / {{ totalAssets }}</h2>
            <p class="mb-0 text-muted">
              <span class="badge bg-info">{{ metrics.ordered_pct }}%</span>
              <span class="ms-2">Complete</span>
            </p>
          </div>
        </div>
      </b-col>

      <b-col xl="3" lg="6">
        <div class="card tilebox-one mb-0">
          <div class="card-body pt-3 pb-2 px-3">
            <i class="uil uil-check-circle float-end"></i>
            <h6 class="text-uppercase mt-0">Clear Titles</h6>
            <h2 class="my-2 fs-3">{{ metrics.clear }} / {{ totalAssets }}</h2>
            <p class="mb-0 text-muted">
              <span class="badge bg-success">{{ metrics.clear_pct }}%</span>
              <span class="ms-2">No Issues</span>
            </p>
          </div>
        </div>
      </b-col>

      <b-col xl="3" lg="6">
        <div class="card tilebox-one mb-0">
          <div class="card-body pt-3 pb-2 px-3">
            <i class="uil uil-exclamation-triangle float-end"></i>
            <h6 class="text-uppercase mt-0">Issues Found</h6>
            <h2 class="my-2 fs-3">{{ metrics.issues }}</h2>
            <p class="mb-0 text-muted">
              <span class="text-warning">{{ metrics.critical }} Critical</span>
            </p>
          </div>
        </div>
      </b-col>

      <b-col xl="3" lg="6">
        <div class="card tilebox-one mb-0">
          <div class="card-body pt-3 pb-2 px-3">
            <i class="uil uil-check-square float-end"></i>
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
                <a href="#title-status" data-bs-toggle="tab" class="nav-link active">
                  <i class="ri-file-list-line me-1"></i>Title Status
                </a>
              </li>
              <li class="nav-item">
                <a href="#exceptions" data-bs-toggle="tab" class="nav-link">
                  <i class="ri-alert-line me-1"></i>Exceptions & Issues
                </a>
              </li>
              <li class="nav-item">
                <a href="#liens" data-bs-toggle="tab" class="nav-link">
                  <i class="ri-file-warning-line me-1"></i>Liens & Encumbrances
                </a>
              </li>
              <li class="nav-item">
                <a href="#companies" data-bs-toggle="tab" class="nav-link">
                  <i class="ri-building-line me-1"></i>Title Companies
                </a>
              </li>
            </ul>

            <div class="tab-content">
              <!-- Title Status Tab -->
              <div class="tab-pane show active" id="title-status">
                <div class="d-flex justify-content-between align-items-center mb-3">
                  <h5 class="mb-0">Title Report Status</h5>
                  <button class="btn btn-sm btn-info">
                    <i class="ri-add-line me-1"></i>Order Title Reports
                  </button>
                </div>
                <div class="table-responsive">
                  <table class="table table-hover table-centered mb-0">
                    <thead class="table-light">
                      <tr>
                        <th>Property</th>
                        <th>Title Company</th>
                        <th>Order Date</th>
                        <th>Received Date</th>
                        <th>Status</th>
                        <th>Issues</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td colspan="7" class="text-center text-muted py-4">
                          <i class="ri-information-line me-1"></i>
                          Title report tracking data will appear here
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <!-- Exceptions Tab -->
              <div class="tab-pane" id="exceptions">
                <h5 class="mb-3">Title Exceptions & Issues</h5>
                <div class="alert alert-warning">
                  <i class="ri-alert-line me-1"></i>
                  Track and resolve title issues, exceptions, and defects across the portfolio
                </div>
                <div class="row">
                  <div class="col-lg-8">
                    <div class="table-responsive">
                      <table class="table table-sm table-striped">
                        <thead>
                          <tr>
                            <th>Property</th>
                            <th>Exception Type</th>
                            <th>Severity</th>
                            <th>Description</th>
                            <th>Status</th>
                            <th>Actions</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr>
                            <td colspan="6" class="text-center text-muted py-3">
                              No exceptions tracked
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                  <div class="col-lg-4">
                    <div class="card border border-danger">
                      <div class="card-body">
                        <h6 class="text-danger">Critical Issues</h6>
                        <p class="text-muted small">Immediate attention required</p>
                        <div class="list-group list-group-flush">
                          <div class="list-group-item text-center text-muted py-3">
                            No critical issues
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Liens Tab -->
              <div class="tab-pane" id="liens">
                <h5 class="mb-3">Liens & Encumbrances Tracker</h5>
                <div class="row">
                  <div class="col-12">
                    <div class="table-responsive">
                      <table class="table table-hover">
                        <thead class="table-light">
                          <tr>
                            <th>Property</th>
                            <th>Lien Type</th>
                            <th>Lienholder</th>
                            <th>Amount</th>
                            <th>Priority</th>
                            <th>Status</th>
                            <th>Actions</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr>
                            <td colspan="7" class="text-center text-muted py-4">
                              Lien tracking data coming soon
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
                <div class="row mt-3">
                  <div class="col-md-4">
                    <div class="card border">
                      <div class="card-body">
                        <h6>Summary</h6>
                        <div class="d-flex justify-content-between mb-1">
                          <span class="text-muted">Total Liens:</span>
                          <strong>0</strong>
                        </div>
                        <div class="d-flex justify-content-between mb-1">
                          <span class="text-muted">Avg Lien Amount:</span>
                          <strong>$0</strong>
                        </div>
                        <div class="d-flex justify-content-between">
                          <span class="text-muted">Resolved:</span>
                          <strong class="text-success">0</strong>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Title Companies Tab -->
              <div class="tab-pane" id="companies">
                <h5 class="mb-3">Title Company Management</h5>
                <div class="row g-3">
                  <div class="col-md-6">
                    <div class="card border">
                      <div class="card-body">
                        <h6><i class="ri-building-line me-1"></i>Active Title Companies</h6>
                        <p class="text-muted small mb-2">Manage relationships and track performance</p>
                        <div class="list-group list-group-flush">
                          <div class="list-group-item text-center text-muted py-3">
                            No companies assigned
                          </div>
                        </div>
                        <button class="btn btn-sm btn-outline-info mt-2">
                          <i class="ri-add-line me-1"></i>Add Title Company
                        </button>
                      </div>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="card border">
                      <div class="card-body">
                        <h6><i class="ri-bar-chart-line me-1"></i>Performance Metrics</h6>
                        <p class="text-muted small mb-2">Track turnaround time, accuracy, and costs</p>
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
            <i class="ri-file-shield-line display-1 text-muted mb-3"></i>
            <h4>No Trade Selected</h4>
            <p class="text-muted">Select a seller and trade from the Acquisitions Dashboard to manage title reports and issues.</p>
            <router-link to="/acquisitions" class="btn btn-info mt-2">
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

// WHAT: Title metrics from backend API
// WHY: All aggregations come from backend, not frontend grid
const titleMetrics = ref<any>(null)

// WHAT: Computed metrics with percentages
// WHY: Display both count and percentage for each metric
const metrics = computed(() => {
  if (!titleMetrics.value) {
    return {
      ordered: 0,
      ordered_pct: 0,
      clear: 0,
      clear_pct: 0,
      issues: 0,
      critical: 0,
      reviewed: 0,
      reviewed_pct: 0,
    }
  }
  
  const total = totalAssets.value || 1
  return {
    ordered: titleMetrics.value.ordered || 0,
    ordered_pct: Math.round(((titleMetrics.value.ordered || 0) / total) * 100),
    clear: titleMetrics.value.clear || 0,
    clear_pct: Math.round(((titleMetrics.value.clear || 0) / total) * 100),
    issues: titleMetrics.value.issues || 0,
    critical: titleMetrics.value.critical || 0,
    reviewed: titleMetrics.value.reviewed || 0,
    reviewed_pct: Math.round(((titleMetrics.value.reviewed || 0) / total) * 100),
  }
})

// WHAT: Fetch title metrics from backend API
// WHY: All aggregations come from backend, not frontend grid
// HOW: Call /api/acq/summary/title/{seller_id}/{trade_id}/
async function fetchTitleMetrics() {
  if (!selectedSellerId.value || !selectedTradeId.value) {
    titleMetrics.value = null
    return
  }
  
  try {
    const resp = await http.get(`/acq/summary/title/${selectedSellerId.value}/${selectedTradeId.value}/`)
    titleMetrics.value = resp.data
    console.log('[TitleCenter] Title metrics loaded:', titleMetrics.value)
  } catch (err: any) {
    console.error('[TitleCenter] Failed to fetch title metrics:', err)
    titleMetrics.value = null
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
    console.log('[TitleCenter] Pool summary loaded:', poolSummary.value)
  } catch (err: any) {
    console.error('[TitleCenter] Failed to fetch pool summary:', err)
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
  
  // WHAT: Load title metrics from backend
  // WHY: All aggregations come from backend APIs, not grid data
  await fetchTitleMetrics()
  
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
