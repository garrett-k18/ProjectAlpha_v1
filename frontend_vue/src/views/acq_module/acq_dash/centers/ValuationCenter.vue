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
                        <th class="text-center">Quick Links</th>
                        <th class="text-center">Seller AIV - ARV</th>
                        <th class="text-center">BPO AIV - ARV</th>
                        <th class="text-center">Broker AIV - ARV</th>
                        <th class="text-center">Internal AIV - ARV</th>
                        <th class="text-center">Variance</th>
                        <th class="text-center">Status</th>
                        <th class="text-center">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-if="!rows || rows.length === 0">
                        <td colspan="9" class="text-center text-muted py-3">
                          No assets to display
                        </td>
                      </tr>
                      <tr v-for="asset in (rows as any[])" :key="asset.asset_hub_id">
                        <td>
                          <div class="fw-semibold address-link" @click="openLoanModal(asset)">
                            {{ formatAddress(asset) }}
                          </div>
                          <div class="small address-link address-link-secondary" @click="openLoanModal(asset)">
                            {{ formatCityState(asset) }}
                          </div>
                        </td>
                        <td class="text-center py-1">
                          <!-- WHAT: 3rd Party Site Links - stacked vertically with minimal spacing -->
                          <div class="d-flex flex-column align-items-center" style="gap: 1px; line-height: 1.3;">
                            <a 
                              :href="getZillowUrl(asset)" 
                              target="_blank" 
                              class="third-party-link small"
                              @click.stop
                            >
                              Zillow <i class="ri-external-link-line"></i>
                            </a>
                            <a 
                              :href="getRedfinUrl(asset)" 
                              target="_blank" 
                              class="third-party-link small"
                              @click.stop
                            >
                              Redfin <i class="ri-external-link-line"></i>
                            </a>
                            <a 
                              :href="getRealtorUrl(asset)" 
                              target="_blank" 
                              class="third-party-link small"
                              @click.stop
                            >
                              Realtor <i class="ri-external-link-line"></i>
                            </a>
                          </div>
                        </td>
                        <td class="text-center">
                          <span>{{ formatCurrency(asset.seller_asis_value as number) }}</span>
                          <span class="mx-2"> - </span>
                          <span>{{ formatCurrency(asset.seller_arv_value as number) }}</span>
                        </td>
                        <td class="text-center">
                          <span>{{ formatCurrency(asset.additional_asis_value as number) }}</span>
                          <span class="mx-2"> - </span>
                          <span>{{ formatCurrency(asset.additional_arv_value as number) }}</span>
                        </td>
                        <td class="text-center">
                          <span>{{ formatCurrency(asset.broker_asis_value as number) }}</span>
                          <span class="mx-2"> - </span>
                          <span>{{ formatCurrency(asset.broker_arv_value as number) }}</span>
                        </td>
                        <td class="text-center">
                          <!-- WHAT: Editable Internal UW Initial As-Is Value - styled to blend in -->
                          <input
                            type="text"
                            class="editable-value-inline"
                            :value="formatCurrencyForInput(asset.internal_initial_uw_asis_value)"
                            @blur="(e) => saveInternalUW(asset, 'asis', e)"
                            @keyup.enter="(e) => saveInternalUW(asset, 'asis', e)"
                            placeholder="-"
                          />
                          <span style="margin: 0 0px;"> - </span>
                          <!-- WHAT: Editable Internal UW Initial ARV Value - styled to blend in -->
                          <input
                            type="text"
                            class="editable-value-inline"
                            :value="formatCurrencyForInput(asset.internal_initial_uw_arv_value)"
                            @blur="(e) => saveInternalUW(asset, 'arv', e)"
                            @keyup.enter="(e) => saveInternalUW(asset, 'arv', e)"
                            placeholder="-"
                          />
                        </td>
                        <td class="text-center">
                          <span :class="varianceClass(calculateVariance(asset))">
                            {{ formatPercent(calculateVariance(asset)) }}
                          </span>
                        </td>
                        <td class="text-center">
                          <span class="badge" :class="statusBadgeClass(getValuationStatus(asset))">
                            {{ getValuationStatus(asset) }}
                          </span>
                        </td>
                        <td class="text-center">
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

    <!-- Loan-Level Modal - Match exact structure from main acquisitions dashboard -->
    <BModal
      v-model="showLoanModal"
      size="xl"
      body-class="p-0 bg-body text-body"
      dialog-class="product-details-dialog"
      content-class="product-details-content bg-body text-body"
      hide-footer
    >
      <!-- Custom header with asset ID and address -->
      <template #header>
        <div class="d-flex align-items-center w-100">
          <h5 class="modal-title mb-0">
            <div class="lh-sm"><span class="fw-bold">{{ modalIdText }}</span></div>
            <div class="text-muted lh-sm"><span class="fw-bold text-dark fs-4">{{ modalAddrText }}</span></div>
          </h5>
          <div class="ms-auto">
            <button
              type="button"
              class="btn-close"
              @click="showLoanModal = false"
              aria-label="Close"
            ></button>
          </div>
        </div>
      </template>
      <!-- Render loan-level component with v-if and :key for proper re-mounting -->
      <LoanLevelIndex
        v-if="selectedId"
        :key="`loan-${selectedId}`"
        :assetId="selectedId"
        :row="selectedRow"
        :address="selectedAddr"
        :standalone="false"
      />
    </BModal>
  </Layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useAcqSelectionsStore } from '@/stores/acqSelections'
import { useAgGridRowsStore } from '@/stores/agGridRows'
import Layout from '@/components/layouts/layout.vue'
import { BModal } from 'bootstrap-vue-next'
import LoanLevelIndex from '@/views/acq_module/loanlvl/loanlvl_index.vue'
import http from '@/lib/http'

// Stores
const acqStore = useAcqSelectionsStore()
const { selectedSellerId, selectedTradeId, sellerOptions, tradeOptions } = storeToRefs(acqStore)
const gridStore = useAgGridRowsStore()
const { rows } = storeToRefs(gridStore)

// WHAT: Modal state for loan-level details
const showLoanModal = ref<boolean>(false)
const selectedId = ref<string | null>(null)
const selectedRow = ref<any>(null)
const selectedAddr = ref<string | null>(null)

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

// WHAT: Computed modal ID text (first line of modal header)
// WHY: Show asset ID and trade name in header
const modalIdText = computed<string>(() => {
  const id = selectedId.value ? String(selectedId.value) : ''
  const r: any = selectedRow.value || {}
  const tradeName = String(r.trade_name ?? r.trade?.trade_name ?? r.tradeName ?? '').trim()
  const line = [id, tradeName].filter(Boolean).join(' / ')
  return line || 'Asset'
})

// WHAT: Computed modal address text (second line of modal header)
// WHY: Show full address without ZIP in header
const modalAddrText = computed<string>(() => {
  const r: any = selectedRow.value || {}
  const street = String(r.street_address ?? r.property_address ?? r.address ?? '').trim()
  const city = String(r.property_city ?? r.city ?? '').trim()
  const state = String(r.property_state ?? r.state ?? '').trim()
  const locality = [city, state].filter(Boolean).join(', ')
  const built = [street, locality].filter(Boolean).join(', ')
  if (built) return built
  const rawAddr = selectedAddr.value ? String(selectedAddr.value) : ''
  // Strip trailing ZIP if present
  return rawAddr.replace(/,?\s*\d{5}(?:-\d{4})?$/, '')
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

// WHAT: Determine valuation status based on available data
// WHY: Show appropriate status tag for each asset's valuation completion
function getValuationStatus(asset: any): string {
  const hasSeller = asset.seller_asis_value != null
  const hasBPO = asset.additional_asis_value != null
  const hasBroker = asset.broker_asis_value != null
  const hasInternal = asset.internal_initial_uw_asis_value != null
  
  // WHAT: If all valuations complete, check for variance issues
  if (hasSeller && hasBPO && hasBroker && hasInternal) {
    const variance = calculateVariance(asset)
    if (variance && Math.abs(variance) > 0.1) return 'Review'
    return 'Approved'
  }
  
  // WHAT: Check what's missing and show appropriate pending status
  if (!hasBPO) return 'Pending BPO'
  if (!hasBroker) return 'Pending Broker'
  if (!hasInternal) return 'Pending UW'
  
  return 'In Progress'
}

function formatCurrency(val: number | null): string {
  if (val == null) return '-'
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val)
}

// WHAT: Format currency for input field (with $ symbol and commas)
// WHY: Display values in familiar currency format
function formatCurrencyForInput(val: number | null): string {
  if (val == null) return ''
  return '$' + new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 }).format(val)
}

// WHAT: Save Internal UW Initial valuation to backend
// WHY: Persist user-entered values to the Valuation model
// HOW: Parse input, send to API endpoint, refresh data
async function saveInternalUW(asset: any, field: 'asis' | 'arv', event: Event) {
  const input = event.target as HTMLInputElement
  // WHAT: Remove dollar signs and commas from input
  const valueStr = input.value.replace(/[$,]/g, '')
  
  // WHAT: If empty, skip save
  if (!valueStr || valueStr.trim() === '') {
    return
  }
  
  // WHAT: Parse to number
  const numValue = parseFloat(valueStr)
  if (isNaN(numValue)) {
    console.error('[ValuationCenter] Invalid number:', valueStr)
    return
  }
  
  // WHAT: Get asset hub ID
  const assetHubId = asset.asset_hub_id || asset.id
  if (!assetHubId) {
    console.error('[ValuationCenter] No asset hub ID found')
    return
  }
  
  try {
    // WHAT: Build payload for Internal Initial UW valuation
    const payload: any = {
      source: 'internalInitialUW',
      value_date: new Date().toISOString().split('T')[0], // Today's date
    }
    
    // WHAT: Set the appropriate field (asis_value or arv_value)
    if (field === 'asis') {
      payload.asis_value = numValue
    } else {
      payload.arv_value = numValue
    }
    
    // WHAT: Send to backend API
    const response = await http.post(`/core/valuations/${assetHubId}/`, payload)
    
    // WHAT: Update local data with response
    if (response.data) {
      if (field === 'asis') {
        asset.internal_initial_uw_asis_value = response.data.asis_value
      } else {
        asset.internal_initial_uw_arv_value = response.data.arv_value
      }
    }
    
    console.log('[ValuationCenter] Saved Internal UW value:', response.data)
  } catch (error) {
    console.error('[ValuationCenter] Failed to save Internal UW value:', error)
    // TODO: Show user-friendly error message
  }
}

// Format address from asset data
function formatAddress(asset: any): string {
  // Try different possible address field names
  return asset.property_address || asset.address || asset.street_address || '-'
}

// Format city and state
function formatCityState(asset: any): string {
  const city = asset.property_city || asset.city || ''
  const state = asset.property_state || asset.state || ''
  if (!city && !state) return ''
  return `${city}${city && state ? ', ' : ''}${state}`
}

// WHAT: Generate Zillow URL for the property
// WHY: Allow users to quickly view property on Zillow
// HOW: Build search URL using address, city, state
function getZillowUrl(asset: any): string {
  const street = formatAddress(asset)
  const cityState = formatCityState(asset)
  const fullAddress = `${street}, ${cityState}`.replace(/\s+/g, '-').replace(/,/g, '')
  return `https://www.zillow.com/homes/${encodeURIComponent(fullAddress)}_rb/`
}

// WHAT: Generate Redfin URL for the property
// WHY: Allow users to quickly view property on Redfin
// HOW: Build URL in format: /STATE/City/Street-Address
function getRedfinUrl(asset: any): string {
  const street = formatAddress(asset).replace(/\s+/g, '-')
  const city = (asset.property_city || asset.city || '').replace(/\s+/g, '-')
  const state = (asset.property_state || asset.state || '').toUpperCase()
  
  if (!street || !city || !state) {
    return 'https://www.redfin.com'
  }
  
  return `https://www.redfin.com/${state}/${city}/${street}`
}

// WHAT: Generate Realtor.com URL for the property
// WHY: Allow users to quickly view property on Realtor.com
// HOW: Build URL in format: /realestateandhomes-detail/Street_City_State_ZIP
function getRealtorUrl(asset: any): string {
  const street = formatAddress(asset).replace(/\s+/g, '-')
  const city = (asset.property_city || asset.city || '').replace(/\s+/g, '-')
  const state = (asset.property_state || asset.state || '').toUpperCase()
  const zip = asset.property_zip || asset.zip || asset.zipcode || ''
  
  if (!street || !city || !state || !zip) {
    return 'https://www.realtor.com'
  }
  
  return `https://www.realtor.com/realestateandhomes-detail/${street}_${city}_${state}_${zip}`
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

// WHAT: Open loan-level modal for a specific asset
// WHY: Allow users to view detailed loan information by clicking on address
function openLoanModal(asset: any) {
  // WHAT: Set selected asset details
  selectedId.value = asset.seller_loan_id || asset.id || String(asset.asset_hub_id)
  selectedRow.value = asset
  selectedAddr.value = formatAddress(asset)
  
  // WHAT: Open the modal
  showLoanModal.value = true
  console.log('[ValuationCenter] Opening loan modal for:', selectedId.value, selectedAddr.value)
}

onMounted(() => {
  // Load data if needed
  if (hasSelection.value && (!rows.value || rows.value.length === 0)) {
    gridStore.fetchRows(selectedSellerId.value!, selectedTradeId.value!, 'all')
  }
})
</script>

<style scoped>
/* WHAT: Clickable address link styling */
/* WHY: Make addresses look clickable and navigate to loan details */
.address-link {
  color: #0d6efd;
  transition: all 0.2s ease;
  cursor: pointer;
}

.address-link:hover {
  color: #0b5ed7;
  text-decoration: underline;
}

/* WHAT: Secondary address link styling (city/state) - blue like main address */
/* WHY: Make both address lines clearly clickable and consistent */
.address-link-secondary {
  color: #0d6efd !important;
  font-weight: 400;
}

.address-link-secondary:hover {
  color: #0b5ed7 !important;
  text-decoration: underline;
}

/* WHAT: 3rd party site link styling - compact */
/* WHY: Make external links visually consistent and appealing with minimal spacing */
.third-party-link {
  color: #0d6efd;
  text-decoration: none;
  transition: all 0.2s ease;
  font-size: 0.8rem;
  white-space: nowrap;
  line-height: 1.1;
  padding: 0;
  margin: 0;
  display: inline-block;
}

.third-party-link:hover {
  color: #0b5ed7;
  text-decoration: underline;
}

.third-party-link i {
  font-size: 0.7rem;
  opacity: 0.7;
  margin-left: 2px;
}

/* WHAT: Editable inline value styling - blend with table text */
/* WHY: Make editable fields look seamless, only showing they're editable via color and underline */
.editable-value-inline {
  /* WHAT: Remove all borders and background to blend in */
  border: none;
  background: transparent;
  padding: 0;
  
  /* WHAT: Match table text styling */
  font-family: inherit;
  font-size: inherit;
  text-align: center;
  
  /* WHAT: Blue color with underline to indicate editability */
  color: #0d6efd;
  text-decoration: underline;
  text-decoration-style: solid;
  text-underline-offset: 2px;
  
  /* WHAT: Set width to accommodate currency values */
  width: 90px;
  display: inline-block;
  
  /* WHAT: Smooth cursor transition */
  cursor: text;
  transition: all 0.2s ease;
}

/* WHAT: Hover state - slightly darker blue */
.editable-value-inline:hover {
  color: #0b5ed7;
  text-decoration-thickness: 2px;
}

/* WHAT: Focus state - remove outline, keep underline, slightly bolder */
.editable-value-inline:focus {
  outline: none;
  color: #0a58ca;
  text-decoration-thickness: 2px;
  font-weight: 500;
}

/* WHAT: Placeholder styling to match empty cells */
.editable-value-inline::placeholder {
  color: #6c757d;
  opacity: 0.5;
}
</style>
