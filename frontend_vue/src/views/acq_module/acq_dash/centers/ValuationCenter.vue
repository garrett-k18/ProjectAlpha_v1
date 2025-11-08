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
            <i class="uil uil-star float-end text-success"></i>
            <h6 class="text-uppercase mt-0">Graded Assets</h6>
            <h2 class="my-2 fs-3">{{ valuationMetrics.graded_count }} / {{ totalAssets }}</h2>
            <p class="mb-0 text-muted">
              <span class="badge" :class="progressBadgeClass(valuationMetrics.graded_count, totalAssets)">
                {{ valuationMetrics.graded_pct }}%
              </span>
              <span class="ms-2">Complete</span>
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
                <a href="#brokers" data-bs-toggle="tab" class="nav-link">
                  <i class="ri-user-line me-1"></i>Brokers
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
                <OverviewTab 
                  :rows="rows"
                  :selectedSellerId="selectedSellerId"
                  :selectedTradeId="selectedTradeId"
                  @openLoanModal="openLoanModal"
                  @saveGrade="saveGrade"
                  @saveInternalUW="saveInternalUW"
                />
              </div>

              <!-- Brokers Tab -->
              <div class="tab-pane" id="brokers">
                <BrokersTab 
                  :rows="rows"
                  @openLoanModal="openLoanModal"
                />
              </div>

              <!-- BPO Tracker Tab -->
              <div class="tab-pane" id="bpo-tracker">
                <h5 class="mb-3">BPO Tracker</h5>
                <div class="alert alert-info">
                  <i class="ri-information-line me-1"></i>
                  BPO tracking content coming soon
                </div>
              </div>

              <!-- Reconciliation Tab -->
              <div class="tab-pane" id="reconciliation">
                <h5 class="mb-3">Value Reconciliation</h5>
                      
                      <!-- Value Range Min -->
                      <div class="col-md-2">
                        <label class="form-label small mb-1">Min Value</label>
                        <input 
                          v-model="filters.minValue" 
                          type="number" 
                          class="form-control form-control-sm" 
                          placeholder="0"
                          @input="applyFilters"
                        />
                      </div>
                      
                      <!-- Value Range Max -->
                      <div class="col-md-2">
                        <label class="form-label small mb-1">Max Value</label>
                        <input 
                          v-model="filters.maxValue" 
                          type="number" 
                          class="form-control form-control-sm" 
                          placeholder="999999999"
                          @input="applyFilters"
                        />
                      </div>
                      
                      <!-- Grade Filter -->
                      <div class="col-md-1">
                        <label class="form-label small mb-1">Grade</label>
                        <select 
                          v-model="filters.grade" 
                          class="form-select form-select-sm"
                          @change="applyFilters"
                        >
                          <option value="">All Grades</option>
                          <option value="A+">A+</option>
                          <option value="A">A</option>
                          <option value="B">B</option>
                          <option value="C">C</option>
                          <option value="D">D</option>
                          <option value="F">F</option>
                        </select>
                      </div>
                      
                      <!-- Clear Filters Button -->
                      <div class="col-md-1">
                        <button 
                          class="btn btn-sm btn-light w-100" 
                          @click="clearFilters"
                          title="Clear all filters"
                        >
                          <i class="ri-filter-off-line"></i>
                        </button>
                      </div>
                    </div>
                    
                    <!-- Filter Results Count -->
                    <div class="mt-2 small text-muted">
                      Showing {{ paginatedRows.length }} of {{ filteredRows.length }} assets
                      <span v-if="filteredRows.length < (rows?.length || 0)">
                        (filtered from {{ rows?.length || 0 }} total)
                      </span>
                    </div>
                  </div>
                </div>
                
                <div class="table-responsive">
                  <table class="table table-centered table-hover mb-0">
                    <thead class="table-light">
                      <tr>
                        <th>Address</th>
                        <th class="text-center">Grade</th>
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
                      <tr v-if="!filteredRows || filteredRows.length === 0">
                        <td colspan="10" class="text-center text-muted py-3">
                          <span v-if="filters.search || filters.state || filters.minValue || filters.maxValue">
                            No assets match your filters
                          </span>
                          <span v-else>
                            No assets to display
                          </span>
                        </td>
                      </tr>
                      <tr v-for="(asset, index) in paginatedRows" :key="`asset-${asset?.asset_hub_id || asset?.id || index}`">
                        <td>
                          <div class="fw-semibold address-link" @click="openLoanModal(asset)">
                            {{ formatAddress(asset) }}
                          </div>
                          <div class="small address-link address-link-secondary" @click="openLoanModal(asset)">
                            {{ formatCityState(asset) }}
                          </div>
                        </td>
                        <td class="text-center">
                          <!-- WHAT: Grade dropdown for Internal Initial UW valuation -->
                          <!-- WHY: Allow users to assign grade to internal UW valuations -->
                          <select 
                            class="form-select form-select-sm grade-select"
                            :value="getInternalUWGrade(asset)"
                            @change="(e) => saveGrade(asset, (e.target as HTMLSelectElement).value)"
                          >
                            <option value="">-</option>
                            <option value="A+">A+</option>
                            <option value="A">A</option>
                            <option value="B">B</option>
                            <option value="C">C</option>
                            <option value="D">D</option>
                            <option value="F">F</option>
                          </select>
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
                            @input="(e) => formatInputOnType(e)"
                            @blur="(e) => saveInternalUW(asset, 'asis', e)"
                            @keyup.enter="(e) => saveInternalUW(asset, 'asis', e)"
                            placeholder="Click to edit"
                          />
                          <span style="margin: 0 0px;"> - </span>
                          <!-- WHAT: Editable Internal UW Initial ARV Value - styled to blend in -->
                          <input
                            type="text"
                            class="editable-value-inline"
                            :value="formatCurrencyForInput(asset.internal_initial_uw_arv_value)"
                            @input="(e) => formatInputOnType(e)"
                            @blur="(e) => saveInternalUW(asset, 'arv', e)"
                            @keyup.enter="(e) => saveInternalUW(asset, 'arv', e)"
                            placeholder="Click to edit"
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
                
                <!-- WHAT: Pagination Controls -->
                <!-- WHY: Navigate through pages of results -->
                <div v-if="filteredRows.length > pageSize" class="d-flex justify-content-between align-items-center mt-3">
                  <div class="text-muted small">
                    Showing {{ ((currentPage - 1) * pageSize) + 1 }} to {{ Math.min(currentPage * pageSize, filteredRows.length) }} of {{ filteredRows.length }} assets
                  </div>
                  
                  <nav>
                    <ul class="pagination pagination-sm mb-0">
                      <!-- Previous Button -->
                      <li class="page-item" :class="{ disabled: currentPage === 1 }">
                        <button class="page-link" @click="goToPage(currentPage - 1)" :disabled="currentPage === 1">
                          <i class="ri-arrow-left-s-line"></i>
                        </button>
                      </li>
                      
                      <!-- First Page -->
                      <li v-if="currentPage > 3" class="page-item">
                        <button class="page-link" @click="goToPage(1)">1</button>
                      </li>
                      <li v-if="currentPage > 4" class="page-item disabled">
                        <span class="page-link">...</span>
                      </li>
                      
                      <!-- Page Numbers (show 5 pages max) -->
                      <li 
                        v-for="page in visiblePages" 
                        :key="page" 
                        class="page-item" 
                        :class="{ active: page === currentPage }"
                      >
                        <button class="page-link" @click="goToPage(page)">
                          {{ page }}
                        </button>
                      </li>
                      
                      <!-- Last Page -->
                      <li v-if="currentPage < totalPages - 3" class="page-item disabled">
                        <span class="page-link">...</span>
                      </li>
                      <li v-if="currentPage < totalPages - 2" class="page-item">
                        <button class="page-link" @click="goToPage(totalPages)">{{ totalPages }}</button>
                      </li>
                      
                      <!-- Next Button -->
                      <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                        <button class="page-link" @click="goToPage(currentPage + 1)" :disabled="currentPage === totalPages">
                          <i class="ri-arrow-right-s-line"></i>
                        </button>
                      </li>
                    </ul>
                  </nav>
                  
                  <!-- Page Size Selector -->
                  <div class="d-flex align-items-center">
                    <label class="me-2 small mb-0">Per page:</label>
                    <select v-model="pageSize" class="form-select form-select-sm" style="width: auto;" @change="currentPage = 1">
                      <option :value="25">25</option>
                      <option :value="50">50</option>
                      <option :value="100">100</option>
                      <option :value="200">200</option>
                    </select>
                  </div>
                </div>
              </div>

              <!-- Brokers Tab -->
              <div class="tab-pane" id="brokers">
                <h5 class="mb-3">Broker Valuations</h5>
                
                <!-- WHAT: Advanced Filters Section -->
                <!-- WHY: Allow users to filter broker valuations by state, city, value ranges, grade -->
                <div class="card bg-light border mb-3">
                  <div class="card-body py-2">
                    <div class="row g-2 align-items-end">
                      <!-- Search Box (City Only) -->
                      <div class="col-md-3">
                        <label class="form-label small mb-1">Search City</label>
                        <input 
                          v-model="filters.search" 
                          type="text" 
                          class="form-control form-control-sm" 
                          placeholder="Search by city..."
                          @input="applyFilters"
                        />
                      </div>
                      
                      <!-- State Filter -->
                      <div class="col-md-2">
                        <label class="form-label small mb-1">State</label>
                        <select 
                          v-model="filters.state" 
                          class="form-select form-select-sm"
                          @change="applyFilters"
                        >
                          <option value="">All States</option>
                          <option v-for="state in availableStates" :key="state" :value="state">
                            {{ state }}
                          </option>
                        </select>
                      </div>
                      
                      <!-- Value Range Min -->
                      <div class="col-md-2">
                        <label class="form-label small mb-1">Min Value</label>
                        <input 
                          v-model="filters.minValue" 
                          type="number" 
                          class="form-control form-control-sm" 
                          placeholder="0"
                          @input="applyFilters"
                        />
                      </div>
                      
                      <!-- Value Range Max -->
                      <div class="col-md-2">
                        <label class="form-label small mb-1">Max Value</label>
                        <input 
                          v-model="filters.maxValue" 
                          type="number" 
                          class="form-control form-control-sm" 
                          placeholder="999999999"
                          @input="applyFilters"
                        />
                      </div>
                      
                      <!-- Grade Filter -->
                      <div class="col-md-1">
                        <label class="form-label small mb-1">Grade</label>
                        <select 
                          v-model="filters.grade" 
                          class="form-select form-select-sm"
                          @change="applyFilters"
                        >
                          <option value="">All Grades</option>
                          <option value="A+">A+</option>
                          <option value="A">A</option>
                          <option value="B">B</option>
                          <option value="C">C</option>
                          <option value="D">D</option>
                          <option value="F">F</option>
                        </select>
                      </div>
                      
                      <!-- Clear Filters Button -->
                      <div class="col-md-1">
                        <button 
                          class="btn btn-sm btn-light w-100" 
                          @click="clearFilters"
                          title="Clear all filters"
                        >
                          <i class="ri-filter-off-line"></i>
                        </button>
                      </div>
                    </div>
                    
                    <!-- Filter Results Count -->
                    <div class="mt-2 small text-muted">
                      Showing {{ paginatedRows.length }} of {{ filteredRows.length }} assets
                      <span v-if="filteredRows.length < (rows?.length || 0)">
                        (filtered from {{ rows?.length || 0 }} total)
                      </span>
                    </div>
                  </div>
                </div>
                
                <div class="table-responsive">
                  <table class="table table-centered table-hover mb-0">
                    <thead class="table-light">
                      <tr>
                        <th>Address</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-if="!filteredRows || filteredRows.length === 0">
                        <td class="text-center text-muted py-3">
                          <span v-if="filters.search || filters.state || filters.minValue || filters.maxValue || filters.grade">
                            No assets match your filters
                          </span>
                          <span v-else>
                            No assets to display
                          </span>
                        </td>
                      </tr>
                      <tr v-for="(asset, index) in paginatedRows" :key="`broker-asset-${asset?.asset_hub_id || asset?.id || index}`">
                        <td>
                          <div class="fw-semibold address-link" @click="openLoanModal(asset)">
                            {{ formatAddress(asset) }}
                          </div>
                          <div class="small address-link address-link-secondary" @click="openLoanModal(asset)">
                            {{ formatCityState(asset) }}
                          </div>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                
                <!-- Pagination Controls -->
                <div class="d-flex justify-content-between align-items-center mt-3">
                  <div class="text-muted small">
                    Page {{ currentPage }} of {{ totalPages }}
                  </div>
                  <nav>
                    <ul class="pagination pagination-sm mb-0">
                      <li class="page-item" :class="{ disabled: currentPage === 1 }">
                        <a class="page-link" href="#" @click.prevent="goToPage(currentPage - 1)">Previous</a>
                      </li>
                      <li 
                        class="page-item" 
                        v-for="page in visiblePages" 
                        :key="page"
                        :class="{ active: page === currentPage }"
                      >
                        <a class="page-link" href="#" @click.prevent="goToPage(page)">{{ page }}</a>
                      </li>
                      <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                        <a class="page-link" href="#" @click.prevent="goToPage(currentPage + 1)">Next</a>
                      </li>
                    </ul>
                  </nav>
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
import OverviewTab from './ValuationComponenets/OverviewTab.vue'
import BrokersTab from './ValuationComponenets/BrokersTab.vue'

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

// WHAT: Pagination state
// WHY: Control page display and navigation
const currentPage = ref(1)
const pageSize = ref(50)  // Default to 50 rows per page

// WHAT: Filter state
// WHY: Allow users to search and filter table data
const filters = ref({
  search: '',
  state: '',
  minValue: null as number | null,
  maxValue: null as number | null,
  grade: '',  // Filter by grade (A+, A, B, C, D, F) or empty for all
})

// WHAT: Pool summary data from backend API (single source of truth)
// WHY: All aggregations should come from backend, not frontend grid
// HOW: Fetch from /api/acq/summary/pool/{seller_id}/{trade_id}/
const poolSummary = ref<any>(null)
const poolLoading = ref(false)

// Computed
const hasSelection = computed(() => !!selectedSellerId.value && !!selectedTradeId.value)
// WHAT: Total assets from backend pool summary (excludes dropped assets automatically)
// WHY: Backend uses sellertrade_qs() which filters acq_status != DROP by default
// HOW: Fetch from pool summary API, fallback to 0 if not loaded
const totalAssets = computed(() => poolSummary.value?.assets ?? 0)

// WHAT: Extract unique states from rows for filter dropdown
// WHY: Populate state filter options
const availableStates = computed(() => {
  const states = new Set<string>()
  if (rows.value) {
    rows.value.forEach((row: any) => {
      if (row.state) states.add(row.state)
    })
  }
  return Array.from(states).sort()
})

// WHAT: Filtered rows based on user filters
// WHY: Apply search and filter criteria to rows
const filteredRows = computed(() => {
  if (!rows.value) return []
  
  let filtered = rows.value
  
  // WHAT: Apply search filter (city only)
  if (filters.value.search) {
    const searchLower = filters.value.search.toLowerCase()
    filtered = filtered.filter((row: any) => 
      (row.city || '').toLowerCase().includes(searchLower)
    )
  }
  
  // WHAT: Apply state filter
  if (filters.value.state) {
    filtered = filtered.filter((row: any) => row.state === filters.value.state)
  }
  
  // WHAT: Apply min value filter (seller_asis_value)
  if (filters.value.minValue != null && filters.value.minValue > 0) {
    filtered = filtered.filter((row: any) => 
      (row.seller_asis_value || 0) >= filters.value.minValue!
    )
  }
  
  // WHAT: Apply max value filter (seller_asis_value)
  if (filters.value.maxValue != null && filters.value.maxValue > 0) {
    filtered = filtered.filter((row: any) => 
      (row.seller_asis_value || 0) <= filters.value.maxValue!
    )
  }
  
  // WHAT: Apply grade filter
  // WHY: Allow users to view only assets with specific grades
  // HOW: Check internal_initial_uw_grade field
  if (filters.value.grade) {
    filtered = filtered.filter((row: any) => row.internal_initial_uw_grade === filters.value.grade)
  }
  
  return filtered
})

// WHAT: Total number of pages based on filtered results
const totalPages = computed(() => Math.ceil(filteredRows.value.length / pageSize.value) || 1)

// WHAT: Visible page numbers for pagination (show 5 pages max)
const visiblePages = computed(() => {
  const pages: number[] = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

// WHAT: Paginated rows for current page
// WHY: Show only rows for current page
const paginatedRows = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredRows.value.slice(start, end)
})
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

// WHAT: Valuation metrics from backend API aggregations
// WHY: Backend handles all counting/aggregation logic, frontend just displays
// HOW: Query backend API for valuation completion counts per source
const valuationMetrics = ref({
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
  graded_count: 0,
  graded_pct: 0,
})

// Helper functions
// WHAT: Apply filters and reset to page 1
// WHY: User changed filter criteria, show first page of results
function applyFilters() {
  currentPage.value = 1
}

// WHAT: Clear all filters and reset pagination
// WHY: User wants to see all data again
function clearFilters() {
  filters.value.search = ''
  filters.value.state = ''
  filters.value.minValue = null
  filters.value.maxValue = null
  filters.value.grade = ''
  currentPage.value = 1
}

// WHAT: Navigate to specific page
// WHY: User clicks pagination controls
function goToPage(page: number) {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

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
// HOW: Accept any type and safely convert to number or null
function formatCurrencyForInput(val: any): string {
  const num = typeof val === 'number' ? val : null
  if (num == null) return ''
  return '$' + new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 }).format(num)
}

// WHAT: Format input field as user types (add $ and commas)
// WHY: Provide real-time feedback as users enter currency values
// HOW: Extract numeric value, format with currency, update input while preserving cursor position
function formatInputOnType(event: Event) {
  const input = event.target as HTMLInputElement
  
  // WHAT: Store cursor position and old value before formatting
  const oldValue = input.value
  const oldCursorPosition = input.selectionStart || 0
  
  // WHAT: Get raw numeric value from input (remove all non-digits)
  const rawValue = oldValue.replace(/[^0-9]/g, '')
  
  // WHAT: If empty, keep it empty
  if (!rawValue) {
    input.value = ''
    return
  }
  
  // WHAT: Parse to number and format with $ and commas
  const numValue = parseInt(rawValue, 10)
  const formatted = '$' + new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 }).format(numValue)
  
  // WHAT: Only update if the formatted value is different
  if (oldValue === formatted) {
    return
  }
  
  // WHAT: Calculate cursor position adjustment
  // WHY: Account for added $ and comma characters
  const digitsBeforeCursor = oldValue.substring(0, oldCursorPosition).replace(/[^0-9]/g, '').length
  
  // WHAT: Find where those digits are in the new formatted string
  let newCursorPosition = 0
  let digitCount = 0
  for (let i = 0; i < formatted.length; i++) {
    if (/[0-9]/.test(formatted[i])) {
      digitCount++
      if (digitCount >= digitsBeforeCursor) {
        newCursorPosition = i + 1
        break
      }
    }
  }
  
  // WHAT: Update value and restore cursor
  input.value = formatted
  input.setSelectionRange(newCursorPosition, newCursorPosition)
}

// WHAT: Get current grade for Internal UW valuation
// WHY: Display current grade in dropdown
// HOW: Extract from asset data returned by serializer
function getInternalUWGrade(asset: any): string {
  const grade = asset.internal_initial_uw_grade || ''
  // Debug logging to see what grade data we have
  if (asset.asset_hub_id === 3691) {
    console.log('[ValuationCenter] getInternalUWGrade for asset 3691:', grade, 'full asset:', asset)
  }
  return grade
}

// WHAT: Save grade for Internal Initial UW valuation
// WHY: Allow users to assign quality grade (A+, A, B, C, D, F) to internal valuations
// HOW: Create/update Internal UW Valuation record with grade (values optional)
async function saveGrade(asset: any, gradeCode: string) {
  const assetHubId = asset.asset_hub_id || asset.id
  if (!assetHubId) {
    console.error('[ValuationCenter] No asset hub ID found')
    return
  }
  
  try {
    // WHAT: Create or update Internal Initial UW valuation with grade
    // WHY: Grade can be assigned even without asis/arv values
    // HOW: Send ONLY grade_code (no value_date) to use "latest or create" logic
    const payload = {
      grade_code: gradeCode || null,  // Empty string becomes null (removes grade)
      // WHAT: Do NOT send value_date
      // WHY: When value_date is null, backend uses "update latest or create new" logic
      // HOW: Backend finds latest Internal UW valuation or creates a new one
    }
    
    console.log('[ValuationCenter] Saving grade:', gradeCode, 'for asset:', assetHubId)
    
    // WHAT: Call valuation API with source=internalInitialUW
    // WHY: Backend endpoint handles grade lookup and valuation creation
    // HOW: PUT to /acq/valuations/internal/{id}/?source=internalInitialUW
    await http.put(`/acq/valuations/internal/${assetHubId}/`, payload, {
      params: { source: 'internalInitialUW' }
    })
    
    // WHAT: Wait a moment for database commit, then refresh
    // WHY: Ensure valuation is fully saved before fetching
    await new Promise(resolve => setTimeout(resolve, 200))
    
    // WHAT: Refresh grid data to show updated grade from backend
    // WHY: Ensure latest data is displayed with new grade
    // HOW: Clear cache and refetch all rows
    if (selectedSellerId.value && selectedTradeId.value) {
      gridStore.clearCache()
      await gridStore.fetchRows(selectedSellerId.value, selectedTradeId.value, 'all')
      console.log('[ValuationCenter] Grid refreshed with updated grade')
      
      // WHAT: Refresh graded assets count from backend
      // WHY: Update the Graded Assets card automatically
      // HOW: Call backend API for updated metrics
      await fetchValuationMetrics()
      console.log('[ValuationCenter] Graded assets count updated:', valuationMetrics.value.graded_count)
      
      // WHAT: Verify the grade is in the refreshed data
      const updatedAsset = rows.value?.find((r: any) => (r.asset_hub_id || r.id) === assetHubId)
      console.log('[ValuationCenter] Updated asset grade:', updatedAsset?.internal_initial_uw_grade)
      
      // WHAT: Check if any row has a grade to verify serializer is working
      const anyWithGrade = rows.value?.find((r: any) => r.internal_initial_uw_grade)
      console.log('[ValuationCenter] Any asset has grade?', anyWithGrade ? 'YES' : 'NO', anyWithGrade?.internal_initial_uw_grade)
    }
    
    console.log('[ValuationCenter] Grade saved successfully')
  } catch (err: any) {
    console.error('[ValuationCenter] Failed to save grade:', err)
    alert(`Failed to save grade: ${err?.response?.data?.error || err?.message || 'Unknown error'}`)
  }
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
      value_date: new Date().toISOString().split('T')[0], // Today's date
    }
    
    // WHAT: Set the appropriate field (asis_value or arv_value)
    if (field === 'asis') {
      payload.asis_value = numValue
    } else {
      payload.arv_value = numValue
    }
    
    // WHAT: Send to backend API with source parameter
    // WHY: Use same endpoint as saveGrade for consistency
    // HOW: PUT to /acq/valuations/internal/{id}/?source=internalInitialUW
    const response = await http.put(`/acq/valuations/internal/${assetHubId}/`, payload, {
      params: { source: 'internalInitialUW' }
    })
    
    // WHAT: Wait a moment for database commit
    // WHY: Ensure valuation is fully saved before refreshing
    await new Promise(resolve => setTimeout(resolve, 200))
    
    // WHAT: Refresh entire row from backend
    // WHY: Get both asis_value AND arv_value from the saved valuation
    // HOW: Clear cache and refetch all rows
    if (selectedSellerId.value && selectedTradeId.value) {
      gridStore.clearCache()
      await gridStore.fetchRows(selectedSellerId.value, selectedTradeId.value, 'all')
      
      // WHAT: Find the updated asset and refresh its values
      const updatedAsset = rows.value?.find((r: any) => (r.asset_hub_id || r.id) === assetHubId)
      if (updatedAsset) {
        asset.internal_initial_uw_asis_value = updatedAsset.internal_initial_uw_asis_value
        asset.internal_initial_uw_arv_value = updatedAsset.internal_initial_uw_arv_value
        console.log('[ValuationCenter] Updated asset values - asis:', asset.internal_initial_uw_asis_value, 'arv:', asset.internal_initial_uw_arv_value)
      }
    }
    
    // WHAT: Refresh valuation metrics from backend
    // WHY: Update the Internal UW count card automatically
    // HOW: Call backend API for updated metrics
    await fetchValuationMetrics()
    console.log('[ValuationCenter] Internal UW count updated:', valuationMetrics.value.internal_count)
    
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

// WHAT: Fetch pool summary from backend API
// WHY: Get total asset count and aggregations from backend (single source of truth)
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
    console.log('[ValuationCenter] Pool summary loaded:', poolSummary.value)
  } catch (err: any) {
    console.error('[ValuationCenter] Failed to fetch pool summary:', err)
    poolSummary.value = null
  } finally {
    poolLoading.value = false
  }
}

// WHAT: Fetch valuation metrics from backend API
// WHY: All aggregations should come from backend, not frontend grid
// HOW: Call /api/acq/summary/valuations/{seller_id}/{trade_id}/
async function fetchValuationMetrics() {
  if (!selectedSellerId.value || !selectedTradeId.value) {
    return
  }
  
  try {
    // WHAT: Fetch valuation counts from backend
    // WHY: Backend queries SellerRawData and Valuation models for accurate counts
    // HOW: GET request to valuation summary endpoint
    const resp = await http.get(`/acq/summary/valuations/${selectedSellerId.value}/${selectedTradeId.value}/`)
    const data = resp.data
    
    // WHAT: Calculate percentages using backend total assets count
    // WHY: Denominator (totalAssets) comes from pool summary API
    const total = totalAssets.value || 1  // Avoid division by zero
    
    // WHAT: Map backend response to frontend structure with percentages
    // WHY: Frontend displays both count and percentage for each source
    valuationMetrics.value = {
      seller_count: data.seller_count || 0,
      seller_pct: Math.round(((data.seller_count || 0) / total) * 100),
      bpo_count: data.bpo_count || 0,
      bpo_pct: Math.round(((data.bpo_count || 0) / total) * 100),
      broker_count: data.broker_count || 0,
      broker_pct: Math.round(((data.broker_count || 0) / total) * 100),
      internal_count: data.internal_uw_count || 0,
      internal_pct: Math.round(((data.internal_uw_count || 0) / total) * 100),
      reconciled_count: data.reconciled_count || 0,
      reconciled_pct: Math.round(((data.reconciled_count || 0) / total) * 100),
      graded_count: data.graded_count || 0,
      graded_pct: Math.round(((data.graded_count || 0) / total) * 100),
    }
    
    console.log('[ValuationCenter] Valuation metrics loaded from backend:', valuationMetrics.value)
  } catch (err: any) {
    console.error('[ValuationCenter] Failed to fetch valuation metrics:', err)
    // WHAT: Set zeros on error
    // WHY: Provide predictable fallback state
    valuationMetrics.value = {
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
      graded_count: 0,
      graded_pct: 0,
    }
  }
}

onMounted(async () => {
  // WHAT: Load pool summary first (contains total asset count)
  // WHY: Total assets needed for all percentage calculations
  // HOW: Fetch from /api/acq/summary/pool/{seller_id}/{trade_id}/
  await fetchPoolSummary()
  
  // WHAT: Load valuation metrics from backend
  // WHY: All aggregations come from backend APIs, not grid data
  // HOW: Fetch from /api/acq/summary/valuations/{seller_id}/{trade_id}/
  await fetchValuationMetrics()
  
  // WHAT: Load grid data if needed (for display table only, not aggregations)
  // WHY: Grid displays individual asset rows, but does NOT aggregate
  if (hasSelection.value && (!rows.value || rows.value.length === 0)) {
    await gridStore.fetchRows(selectedSellerId.value!, selectedTradeId.value!, 'all')
    
    // WHAT: Debug - check if grade fields are in the data
    // WHY: Verify serializer is returning grade fields
    if (rows.value && rows.value.length > 0) {
      const sample = rows.value[0]
      console.log('[ValuationCenter] Sample row keys:', Object.keys(sample))
      console.log('[ValuationCenter] Sample row grade field:', (sample as any).internal_initial_uw_grade)
      
      // Find asset 3691 specifically
      const asset3691 = rows.value.find((r: any) => (r.asset_hub_id || r.id) === 3691)
      if (asset3691) {
        console.log('[ValuationCenter] Asset 3691 grade:', (asset3691 as any).internal_initial_uw_grade)
      }
    }
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

/* WHAT: Grade dropdown select styling */
/* WHY: Compact dropdown that fits in table cell */
.grade-select {
  width: auto;
  min-width: 70px;
  max-width: 90px;
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
  border: 1px solid #dee2e6;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.grade-select:hover {
  border-color: #0d6efd;
  box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.1);
}

.grade-select:focus {
  border-color: #0d6efd;
  box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
  outline: 0;
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
