<template>
  <Layout>
    <div class="container-fluid">
      <!-- Page Title -->
    <div class="row">
      <div class="col-12">
        <div class="page-title-box">
          <div class="page-title-right">
            <ol class="breadcrumb m-0">
              <li class="breadcrumb-item"><a href="#">Dashboards</a></li>
              <li class="breadcrumb-item active">Servicing</li>
            </ol>
          </div>
          <h4 class="page-title">Servicing Dashboard</h4>
        </div>
      </div>
    </div>

    <!-- Servicer Selection -->
    <div class="row">
      <div class="col-12">
        <div class="card">
          <div class="card-body">
            <div class="row align-items-center">
              <div class="col-md-4">
                <h5 class="mb-0">Select Servicer</h5>
              </div>
              <div class="col-md-8">
                <div class="d-flex flex-wrap gap-2 align-items-center">
                  <select v-model="selectedServicer" class="form-select" style="min-width: 240px; flex: 1 1 240px;" @change="loadServicingData" :disabled="isLoadingServicers">
                    <option value="">-- Select a Servicer --</option>
                    <option v-if="isLoadingServicers" disabled value="">Loading servicers...</option>
                    <option v-for="servicer in servicers" :key="servicer.id" :value="String(servicer.id)">
                      {{ servicer.name }}
                    </option>
                  </select>

                  <button
                    class="btn btn-sm btn-outline-secondary"
                    type="button"
                    @click="openRawViewer('monthly_remit')"
                    :disabled="!selectedServicer"
                    title="View Monthly Remit raw file data"
                  >
                    <i class="mdi mdi-file-document-outline"></i>
                    Monthly Remit
                  </button>

                  <button
                    class="btn btn-sm btn-outline-secondary"
                    type="button"
                    @click="openRawViewer('daily_loan_data')"
                    title="View Daily Loan Data raw feed"
                  >
                    <i class="mdi mdi-table"></i>
                    Daily Loan Data
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Key Metrics Cards -->
    <div v-if="selectedServicer" class="row">
      <div class="col-xl-3 col-md-6">
        <div class="card">
          <div class="card-body">
            <div class="row align-items-center">
              <div class="col-6">
                <h5 class="text-muted fw-normal mt-0 text-truncate">Total Collections</h5>
                <h3 class="my-2 py-1">{{ formatCurrency(metrics.totalCollections) }}</h3>
                <p class="mb-0 text-muted">
                  <span class="text-success me-2"><i class="mdi mdi-arrow-up-bold"></i> {{ metrics.collectionsGrowth }}%</span>
                </p>
              </div>
              <div class="col-6">
                <div class="text-end">
                  <div id="collections-chart" style="min-height: 45px;"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-xl-3 col-md-6">
        <div class="card">
          <div class="card-body">
            <div class="row align-items-center">
              <div class="col-6">
                <h5 class="text-muted fw-normal mt-0 text-truncate">Outstanding Balance</h5>
                <h3 class="my-2 py-1">{{ formatCurrency(metrics.outstandingBalance) }}</h3>
                <p class="mb-0 text-muted">
                  <span class="text-danger me-2"><i class="mdi mdi-arrow-down-bold"></i> {{ metrics.balanceChange }}%</span>
                </p>
              </div>
              <div class="col-6">
                <div class="text-end">
                  <div id="balance-chart" style="min-height: 45px;"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-xl-3 col-md-6">
        <div class="card">
          <div class="card-body">
            <div class="row align-items-center">
              <div class="col-6">
                <h5 class="text-muted fw-normal mt-0 text-truncate">Payoffs (MTD)</h5>
                <h3 class="my-2 py-1">{{ formatCurrency(metrics.payoffsMTD) }}</h3>
                <p class="mb-0 text-muted">
                  <span class="text-success me-2">{{ metrics.payoffsCount }} loans</span>
                </p>
              </div>
              <div class="col-6">
                <div class="text-end">
                  <div id="payoffs-chart" style="min-height: 45px;"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-xl-3 col-md-6">
        <div class="card">
          <div class="card-body">
            <div class="row align-items-center">
              <div class="col-6">
                <h5 class="text-muted fw-normal mt-0 text-truncate">Servicing Fees</h5>
                <h3 class="my-2 py-1">{{ formatCurrency(metrics.servicingFees) }}</h3>
                <p class="mb-0 text-muted">
                  <span class="text-info me-2">Current Month</span>
                </p>
              </div>
              <div class="col-6">
                <div class="text-end">
                  <div id="fees-chart" style="min-height: 45px;"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Monthly Remittance & Trial Balance -->
    <div v-if="selectedServicer" class="row">
      <div class="col-xl-6">
        <div class="card">
          <div class="card-body">
            <h4 class="header-title mb-3">Monthly Remittance Summary</h4>
            <div class="table-responsive">
              <table class="table table-sm table-centered mb-0">
                <thead class="table-light">
                  <tr>
                    <th>Category</th>
                    <th class="text-end">Amount</th>
                    <th class="text-end">% of Collections</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in remittanceData" :key="item.category">
                    <td>{{ item.category }}</td>
                    <td class="text-end">{{ formatCurrency(item.amount) }}</td>
                    <td class="text-end">
                      <span :class="getBadgeClass(item.percentage)">{{ item.percentage }}%</span>
                    </td>
                  </tr>
                  <tr class="table-active fw-bold">
                    <td>Net to Investor</td>
                    <td class="text-end">{{ formatCurrency(netToInvestor) }}</td>
                    <td class="text-end">{{ netPercentage }}%</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <div class="col-xl-6">
        <div class="card">
          <div class="card-body">
            <h4 class="header-title mb-3">Trial Balance Overview</h4>
            <div class="table-responsive">
              <table class="table table-sm table-centered mb-0">
                <thead class="table-light">
                  <tr>
                    <th>Account</th>
                    <th class="text-end">Debit</th>
                    <th class="text-end">Credit</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in trialBalance" :key="item.account">
                    <td>{{ item.account }}</td>
                    <td class="text-end">{{ item.debit ? formatCurrency(item.debit) : '-' }}</td>
                    <td class="text-end">{{ item.credit ? formatCurrency(item.credit) : '-' }}</td>
                  </tr>
                  <tr class="table-active fw-bold">
                    <td>Total</td>
                    <td class="text-end">{{ formatCurrency(totalDebit) }}</td>
                    <td class="text-end">{{ formatCurrency(totalCredit) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Collections & Expenses -->
    <div v-if="selectedServicer" class="row">
      <div class="col-xl-8">
        <div class="card">
          <div class="card-body">
            <h4 class="header-title mb-3">Collections Trend (Last 12 Months)</h4>
            <div id="collections-trend-chart"></div>
          </div>
        </div>
      </div>

      <div class="col-xl-4">
        <div class="card">
          <div class="card-body">
            <h4 class="header-title mb-3">Servicing Expenses</h4>
            <div class="table-responsive">
              <table class="table table-sm table-centered mb-0">
                <thead class="table-light">
                  <tr>
                    <th>Expense Type</th>
                    <th class="text-end">MTD</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="expense in expenses" :key="expense.type">
                    <td>{{ expense.type }}</td>
                    <td class="text-end">{{ formatCurrency(expense.amount) }}</td>
                  </tr>
                  <tr class="table-active fw-bold">
                    <td>Total Expenses</td>
                    <td class="text-end">{{ formatCurrency(totalExpenses) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Advances & Tax/Insurance -->
    <div v-if="selectedServicer" class="row">
      <div class="col-xl-6">
        <div class="card">
          <div class="card-body">
            <h4 class="header-title mb-3">Outstanding Advances</h4>
            <div class="table-responsive">
              <table class="table table-sm table-centered table-striped mb-0">
                <thead class="table-light">
                  <tr>
                    <th>Advance Type</th>
                    <th class="text-end">Count</th>
                    <th class="text-end">Amount</th>
                    <th class="text-end">Avg Age (Days)</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="advance in advances" :key="advance.type">
                    <td>{{ advance.type }}</td>
                    <td class="text-end">{{ advance.count }}</td>
                    <td class="text-end">{{ formatCurrency(advance.amount) }}</td>
                    <td class="text-end">{{ advance.avgAge }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <div class="col-xl-6">
        <div class="card">
          <div class="card-body">
            <h4 class="header-title mb-3">Tax & Insurance Tracking</h4>
            <div class="row">
              <div class="col-6">
                <div class="text-center">
                  <h5 class="fw-normal text-muted">Property Taxes</h5>
                  <h3 class="mt-3 mb-3">{{ formatCurrency(taxInsurance.propertyTaxes) }}</h3>
                  <p class="mb-0 text-muted">
                    <span class="badge badge-soft-success">{{ taxInsurance.taxPaidCount }} Paid</span>
                    <span class="badge badge-soft-warning ms-1">{{ taxInsurance.taxPendingCount }} Pending</span>
                  </p>
                </div>
              </div>
              <div class="col-6">
                <div class="text-center">
                  <h5 class="fw-normal text-muted">Insurance</h5>
                  <h3 class="mt-3 mb-3">{{ formatCurrency(taxInsurance.insurance) }}</h3>
                  <p class="mb-0 text-muted">
                    <span class="badge badge-soft-success">{{ taxInsurance.insuredCount }} Active</span>
                    <span class="badge badge-soft-danger ms-1">{{ taxInsurance.uninsuredCount }} Lapsed</span>
                  </p>
                </div>
              </div>
            </div>
            <div class="mt-3">
              <div class="progress progress-sm">
                <div class="progress-bar bg-success" role="progressbar" 
                     :style="{ width: taxInsurance.complianceRate + '%' }"
                     :aria-valuenow="taxInsurance.complianceRate" aria-valuemin="0" aria-valuemax="100">
                </div>
              </div>
              <p class="mb-0 text-muted mt-1">
                <small>Compliance Rate: {{ taxInsurance.complianceRate }}%</small>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- P&I and Recent Activity -->
    <div v-if="selectedServicer" class="row">
      <div class="col-xl-4">
        <div class="card">
          <div class="card-body">
            <h4 class="header-title mb-3">P&I Collections (NPL)</h4>
            <div class="text-center">
              <div id="pi-chart" style="height: 250px;"></div>
            </div>
            <div class="row text-center mt-3">
              <div class="col-6">
                <h5 class="fw-normal text-muted">Principal</h5>
                <h4>{{ formatCurrency(piCollections.principal) }}</h4>
              </div>
              <div class="col-6">
                <h5 class="fw-normal text-muted">Interest</h5>
                <h4>{{ formatCurrency(piCollections.interest) }}</h4>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-xl-8">
        <div class="card">
          <div class="card-body">
            <h4 class="header-title mb-3">Recent Servicing Activity</h4>
            <div class="table-responsive">
              <table class="table table-sm table-centered table-hover mb-0">
                <thead class="table-light">
                  <tr>
                    <th>Date</th>
                    <th>Loan ID</th>
                    <th>Activity</th>
                    <th class="text-end">Amount</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="activity in recentActivity" :key="activity.id">
                    <td>{{ formatDate(activity.date) }}</td>
                    <td>{{ activity.loanId }}</td>
                    <td>{{ activity.type }}</td>
                    <td class="text-end">{{ formatCurrency(activity.amount) }}</td>
                    <td>
                      <span :class="getStatusBadge(activity.status)">
                        {{ activity.status }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="!selectedServicer" class="row">
      <div class="col-12">
        <div class="card">
          <div class="card-body text-center" style="min-height: 400px; display: flex; align-items: center; justify-content: center;">
            <div>
              <i class="ri-line-chart-line" style="font-size: 72px; color: #98a6ad;"></i>
              <h4 class="mt-3 text-muted">Please select a servicer to view dashboard</h4>
              <p class="text-muted">Choose a servicer from the dropdown above to see detailed servicing metrics</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <BModal
      v-model="showRawModal"
      size="xl"
      body-class="p-3 bg-body text-body"
      hide-footer
    >
      <template #header>
        <div class="d-flex align-items-center w-100">
          <h5 class="modal-title mb-0">{{ rawViewerTitle }}</h5>
          <div class="ms-auto d-flex align-items-center gap-2">
            <input
              v-if="rawViewerType === 'daily_loan_data'"
              v-model="rawDateFilter"
              type="date"
              class="form-control form-control-sm"
              style="max-width: 160px;"
              :disabled="rawLoading"
              @change="fetchRawViewerData"
            />
            <button
              type="button"
              class="btn btn-sm btn-outline-secondary"
              @click="toggleRawFullWindow"
              :title="rawIsFullWindow ? 'Exit Full Window' : 'Full Window'"
            >
              <i class="mdi" :class="rawIsFullWindow ? 'mdi-fullscreen-exit' : 'mdi-fullscreen'"></i>
            </button>
            <button type="button" class="btn-close" @click="showRawModal = false" aria-label="Close" />
          </div>
        </div>
      </template>

      <div v-if="rawLoading" class="d-flex align-items-center justify-content-center text-muted small py-5">
        <div class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></div>
        <span>Loading raw data...</span>
      </div>

      <div v-else-if="rawError" class="alert alert-warning mb-0">
        {{ rawError }}
      </div>

      <div v-else>
        <ag-grid-vue
          class="acq-grid"
          :style="{ width: '100%', height: rawGridHeight }"
          :theme="themeQuartz"
          :columnDefs="rawColumnDefs"
          :rowData="rawRows"
          :defaultColDef="rawDefaultColDef"
          :animateRows="true"
          :pagination="true"
          :paginationPageSize="100"
          :enableCellTextSelection="true"
        />
      </div>
    </BModal>

    </div>
  </Layout>
</template>

<script>
import ApexCharts from 'apexcharts';
import Layout from "@/components/layouts/layout.vue";
import http from "@/lib/http";
import { BModal } from 'bootstrap-vue-next';
import { AgGridVue } from 'ag-grid-vue3';
import { themeQuartz } from 'ag-grid-community';

export default {
  name: 'ServicingDashboard',
  components: {
    Layout,
    BModal,
    AgGridVue,
  },
  
  data() {
    return {
      selectedServicer: '',
      servicers: [],
      isLoadingServicers: false,

      showRawModal: false,
      rawViewerType: 'daily_loan_data',
      rawLoading: false,
      rawError: null,
      rawRows: [],
      rawColumnDefs: [],
      rawDateFilter: '',
      rawIsFullWindow: false,
      rawDefaultColDef: {
        resizable: true,
        filter: true,
        wrapHeaderText: true,
        autoHeaderHeight: true,
        headerClass: 'text-center',
        cellClass: 'text-center',
        floatingFilter: false,
        menuTabs: ['filterMenuTab'],
      },

      themeQuartz,
      
      metrics: {
        totalCollections: 0,
        collectionsGrowth: 0,
        outstandingBalance: 0,
        balanceChange: 0,
        payoffsMTD: 0,
        payoffsCount: 0,
        servicingFees: 0,
      },
      
      remittanceData: [],
      trialBalance: [],
      expenses: [],
      advances: [],
      
      taxInsurance: {
        propertyTaxes: 0,
        insurance: 0,
        taxPaidCount: 0,
        taxPendingCount: 0,
        insuredCount: 0,
        uninsuredCount: 0,
        complianceRate: 0,
      },
      
      piCollections: {
        principal: 0,
        interest: 0,
      },
      
      recentActivity: [],
      
      charts: {
        collections: null,
        balance: null,
        payoffs: null,
        fees: null,
        collectionsTrend: null,
        pi: null,
      }
    };
  },

  mounted() {
    this.loadServicers();
  },
  
  computed: {
    rawGridHeight() {
      return this.rawIsFullWindow ? '85vh' : '70vh'
    },

    rawViewerTitle() {
      if (this.rawViewerType === 'daily_loan_data') return 'Daily Loan Data (Raw)'
      return 'Monthly Remit (Raw)'
    },

    netToInvestor() {
      return this.remittanceData.reduce((sum, item) => {
        if (item.category === 'Total Collections') return sum + item.amount;
        if (item.category !== 'Net to Investor') return sum - item.amount;
        return sum;
      }, 0);
    },
    
    netPercentage() {
      const total = this.remittanceData.find(item => item.category === 'Total Collections')?.amount || 0;
      if (total === 0) return 0;
      return ((this.netToInvestor / total) * 100).toFixed(2);
    },
    
    totalDebit() {
      return this.trialBalance.reduce((sum, item) => sum + (item.debit || 0), 0);
    },
    
    totalCredit() {
      return this.trialBalance.reduce((sum, item) => sum + (item.credit || 0), 0);
    },
    
    totalExpenses() {
      return this.expenses.reduce((sum, expense) => sum + expense.amount, 0);
    }
  },
  
  methods: {
    toggleRawFullWindow() {
      this.rawIsFullWindow = !this.rawIsFullWindow
    },

    openRawViewer(type) {
      this.rawViewerType = type
      this.rawError = null
      this.rawRows = []
      this.rawColumnDefs = []
      this.rawIsFullWindow = false
      this.showRawModal = true
      this.fetchRawViewerData()
    },

    buildRawColumnDefs(rows) {
      const first = Array.isArray(rows) && rows.length > 0 ? rows[0] : null
      if (!first) return []
      return Object.keys(first).map((k) => ({
        headerName: String(k).replace(/_/g, ' '),
        field: k,
        minWidth: 120,
        flex: 1,
      }))
    },

    async fetchRawViewerData() {
      this.rawLoading = true
      this.rawError = null
      this.rawRows = []
      this.rawColumnDefs = []
      try {
        if (this.rawViewerType === 'daily_loan_data') {
          const params = { limit: 500 }
          if (this.rawDateFilter) params.date = this.rawDateFilter
          const resp = await http.get('/am/raw/statebridge/daily-loan-data/', { params })
          const payload = resp?.data
          if (!this.rawDateFilter && payload?.applied_date_iso) {
            this.rawDateFilter = payload.applied_date_iso
          }
          const rowsOut = Array.isArray(payload?.results) ? payload.results : []
          this.rawRows = rowsOut
          this.rawColumnDefs = this.buildRawColumnDefs(rowsOut)

          if (!rowsOut || rowsOut.length === 0) {
            this.rawError = this.rawDateFilter
              ? `No Daily Loan Data found for ${this.rawDateFilter}.`
              : 'No Daily Loan Data found.'
          }
          return
        }

        this.rawError = 'Monthly Remit raw data source is not configured yet. Tell me where this data lives (DB table/model or file location) and I will wire it up.'
      } catch (err) {
        console.error('Error loading raw data:', err)
        this.rawError = 'Failed to load raw data.'
      } finally {
        this.rawLoading = false
      }
    },

    async loadServicers() {
      this.isLoadingServicers = true;
      try {
        const resp = await http.get('/core/servicers/');
        const payload = resp?.data;
        const rows = Array.isArray(payload)
          ? payload
          : Array.isArray(payload?.results)
            ? payload.results
            : [];

        this.servicers = rows
          .map((s) => ({
            id: s.id,
            name: s.servicerName ?? s.servicer_name ?? s.name,
          }))
          .filter((s) => s.id != null && s.name);
      } catch (err) {
        console.error('Error loading servicers:', err);
        this.servicers = [];
      } finally {
        this.isLoadingServicers = false;
      }
    },

    async loadServicingData() {
      if (!this.selectedServicer) return;
      
      // Simulate API call - replace with actual API endpoint
      this.loadMockData();
      
      // Initialize charts after data is loaded
      this.$nextTick(() => {
        this.initializeCharts();
      });
    },
    
    loadMockData() {
      // Mock data - replace with actual API calls
      this.metrics = {
        totalCollections: 1245000,
        collectionsGrowth: 8.3,
        outstandingBalance: 45600000,
        balanceChange: 3.2,
        payoffsMTD: 385000,
        payoffsCount: 12,
        servicingFees: 42000,
      };
      
      this.remittanceData = [
        { category: 'Total Collections', amount: 1245000, percentage: 100 },
        { category: 'Servicing Fees', amount: 42000, percentage: 3.37 },
        { category: 'P&I to Investor', amount: 125000, percentage: 10.04 },
        { category: 'Tax Advances', amount: 85000, percentage: 6.83 },
        { category: 'Insurance Premiums', amount: 32000, percentage: 2.57 },
        { category: 'Property Expenses', amount: 18000, percentage: 1.45 },
        { category: 'Legal Fees', amount: 15000, percentage: 1.20 },
      ];
      
      this.trialBalance = [
        { account: 'Principal Balance', debit: 45600000, credit: null },
        { account: 'Interest Receivable', debit: 2340000, credit: null },
        { account: 'Advances - Taxes', debit: 385000, credit: null },
        { account: 'Advances - Insurance', debit: 142000, credit: null },
        { account: 'Servicing Income', debit: null, credit: 126000 },
        { account: 'Collections Suspense', debit: null, credit: 842000 },
        { account: 'Investor Payable', debit: null, credit: 47499000 },
      ];
      
      this.expenses = [
        { type: 'Property Inspection', amount: 8500 },
        { type: 'Legal & Foreclosure', amount: 15000 },
        { type: 'Property Taxes', amount: 12000 },
        { type: 'Insurance Premiums', amount: 32000 },
        { type: 'REO Maintenance', amount: 5200 },
        { type: 'Other', amount: 3800 },
      ];
      
      this.advances = [
        { type: 'Property Tax Advances', count: 45, amount: 385000, avgAge: 87 },
        { type: 'Insurance Advances', count: 28, amount: 142000, avgAge: 42 },
        { type: 'Legal Fee Advances', count: 12, amount: 68000, avgAge: 156 },
        { type: 'Property Preservation', count: 8, amount: 24000, avgAge: 23 },
      ];
      
      this.taxInsurance = {
        propertyTaxes: 385000,
        insurance: 142000,
        taxPaidCount: 124,
        taxPendingCount: 45,
        insuredCount: 156,
        uninsuredCount: 13,
        complianceRate: 92.3,
      };
      
      this.piCollections = {
        principal: 98500,
        interest: 26500,
      };
      
      this.recentActivity = [
        { id: 1, date: '2024-01-15', loanId: 'L-00123', type: 'Payment Received', amount: 2500, status: 'Posted' },
        { id: 2, date: '2024-01-15', loanId: 'L-00456', type: 'Tax Advance', amount: 8500, status: 'Pending' },
        { id: 3, date: '2024-01-14', loanId: 'L-00789', type: 'Payoff', amount: 125000, status: 'Cleared' },
        { id: 4, date: '2024-01-14', loanId: 'L-00234', type: 'Insurance Payment', amount: 1200, status: 'Posted' },
        { id: 5, date: '2024-01-13', loanId: 'L-00567', type: 'Partial Payment', amount: 500, status: 'Posted' },
        { id: 6, date: '2024-01-13', loanId: 'L-00890', type: 'Legal Fee Advance', amount: 3500, status: 'Pending' },
        { id: 7, date: '2024-01-12', loanId: 'L-00345', type: 'Payment Received', amount: 1800, status: 'Posted' },
      ];
    },
    
    initializeCharts() {
      this.destroyCharts();
      this.createSparklineChart('collections-chart', [45, 52, 48, 58, 65, 62, 70, 68, 75, 82, 88, 95]);
      this.createSparklineChart('balance-chart', [95, 92, 90, 87, 85, 83, 80, 78, 76, 74, 71, 68], '#f1556c');
      this.createSparklineChart('payoffs-chart', [12, 15, 8, 22, 18, 25, 30, 28, 35, 32, 38, 42], '#10c469');
      this.createSparklineChart('fees-chart', [38, 40, 39, 41, 42, 40, 43, 42, 44, 43, 45, 42], '#ffbd4a');
      this.createCollectionsTrendChart();
      this.createPIChart();
    },
    
    createSparklineChart(elementId, data, color = '#4a81d4') {
      const options = {
        chart: {
          type: 'line',
          width: 80,
          height: 45,
          sparkline: { enabled: true }
        },
        series: [{
          data: data
        }],
        stroke: {
          width: 2,
          curve: 'smooth'
        },
        colors: [color],
        tooltip: {
          fixed: { enabled: false },
          x: { show: false },
          y: {
            title: {
              formatter: function() {
                return '';
              }
            }
          },
          marker: { show: false }
        }
      };
      
      this.charts[elementId.replace('-chart', '')] = new ApexCharts(document.querySelector('#' + elementId), options);
      this.charts[elementId.replace('-chart', '')].render();
    },
    
    createCollectionsTrendChart() {
      const options = {
        chart: {
          type: 'area',
          height: 300,
          toolbar: { show: false }
        },
        dataLabels: { enabled: false },
        stroke: {
          curve: 'smooth',
          width: 2
        },
        series: [{
          name: 'Collections',
          data: [985000, 1020000, 1080000, 1150000, 1125000, 1180000, 1215000, 1190000, 1235000, 1220000, 1268000, 1245000]
        }],
        fill: {
          type: 'gradient',
          gradient: {
            shadeIntensity: 1,
            opacityFrom: 0.7,
            opacityTo: 0.3,
          }
        },
        xaxis: {
          categories: ['Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan']
        },
        yaxis: {
          labels: {
            formatter: (value) => this.formatCurrency(value, true)
          }
        },
        colors: ['#4a81d4'],
        tooltip: {
          y: {
            formatter: (value) => this.formatCurrency(value)
          }
        }
      };
      
      this.charts.collectionsTrend = new ApexCharts(document.querySelector('#collections-trend-chart'), options);
      this.charts.collectionsTrend.render();
    },
    
    createPIChart() {
      const options = {
        chart: {
          type: 'donut',
          height: 250
        },
        series: [this.piCollections.principal, this.piCollections.interest],
        labels: ['Principal', 'Interest'],
        colors: ['#4a81d4', '#10c469'],
        legend: {
          show: true,
          position: 'bottom'
        },
        dataLabels: {
          enabled: true,
          formatter: (val) => val.toFixed(1) + '%'
        },
        tooltip: {
          y: {
            formatter: (value) => this.formatCurrency(value)
          }
        }
      };
      
      this.charts.pi = new ApexCharts(document.querySelector('#pi-chart'), options);
      this.charts.pi.render();
    },
    
    destroyCharts() {
      Object.values(this.charts).forEach(chart => {
        if (chart) chart.destroy();
      });
    },
    
    formatCurrency(amount, short = false) {
      if (short) {
        if (amount >= 1000000) {
          return '$' + (amount / 1000000).toFixed(1) + 'M';
        }
        if (amount >= 1000) {
          return '$' + (amount / 1000).toFixed(0) + 'K';
        }
      }
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }).format(amount);
    },
    
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      });
    },
    
    getBadgeClass(percentage) {
      if (percentage < 5) return 'badge badge-soft-success';
      if (percentage < 10) return 'badge badge-soft-info';
      if (percentage < 15) return 'badge badge-soft-warning';
      return 'badge badge-soft-danger';
    },
    
    getStatusBadge(status) {
      const badges = {
        'Posted': 'badge badge-soft-success',
        'Pending': 'badge badge-soft-warning',
        'Cleared': 'badge badge-soft-info',
        'Failed': 'badge badge-soft-danger'
      };
      return badges[status] || 'badge badge-soft-secondary';
    }
  },
  
  beforeUnmount() {
    this.destroyCharts();
  }
};
</script>

<style scoped>
.badge {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
}

.card {
  box-shadow: 0 0 35px 0 rgba(154, 161, 171, 0.15);
  border-radius: 0.25rem;
  margin-bottom: 24px;
}

.table-responsive {
  overflow-x: auto;
}

.progress-sm {
  height: 8px;
}
</style>

