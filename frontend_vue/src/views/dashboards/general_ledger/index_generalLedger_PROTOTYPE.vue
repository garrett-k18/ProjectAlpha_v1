<template>
  <Layout>
    <!-- Page Title -->
    <b-row>
      <b-col class="col-12">
        <div class="page-title-box">
          <div class="page-title-right">
            <div class="d-flex gap-2">
              <button class="btn btn-sm btn-success">
                <i class="mdi mdi-download me-1"></i>
                Export
              </button>
              <button class="btn btn-sm btn-primary">
                <i class="mdi mdi-plus me-1"></i>
                New Entry
              </button>
              <button class="btn btn-sm btn-secondary">
                <i class="mdi mdi-filter me-1"></i>
                Filters
                <span class="badge bg-danger ms-1">2</span>
              </button>
            </div>
          </div>
          <h4 class="page-title">General Ledger Dashboard <span class="badge bg-info ms-2">PROTOTYPE</span></h4>
        </div>
      </b-col>
    </b-row>

    <!-- Summary Stats Cards -->
    <b-row class="g-2 mb-2">
      <!-- Total Debits Card -->
      <b-col xl="2" lg="4" sm="6">
        <div class="card tilebox-one mb-0">
          <div class="card-body pt-3 pb-2 px-3">
            <i class="uil uil-plus-circle float-end text-success" aria-hidden="true"></i>
            <h6 class="text-uppercase mt-0">Total Debits</h6>
            <h2 class="my-2">
              <span class="fs-4 fs-lg-2 text-success">$45.8MM</span>
            </h2>
          </div>
        </div>
      </b-col>

      <!-- Total Credits Card -->
      <b-col xl="2" lg="4" sm="6">
        <div class="card tilebox-one mb-0">
          <div class="card-body pt-3 pb-2 px-3">
            <i class="uil uil-minus-circle float-end text-danger" aria-hidden="true"></i>
            <h6 class="text-uppercase mt-0">Total Credits</h6>
            <h2 class="my-2">
              <span class="fs-4 fs-lg-2 text-danger">$43.2MM</span>
            </h2>
          </div>
        </div>
      </b-col>

      <!-- Net Total Card -->
      <b-col xl="2" lg="4" sm="6">
        <div class="card tilebox-one mb-0">
          <div class="card-body pt-3 pb-2 px-3">
            <i class="uil uil-balance-scale float-end text-primary" aria-hidden="true"></i>
            <h6 class="text-uppercase mt-0">Net Total</h6>
            <h2 class="my-2">
              <span class="fs-4 fs-lg-2 text-success">$2.6MM</span>
            </h2>
          </div>
        </div>
      </b-col>

      <!-- Total Entries Card -->
      <b-col xl="2" lg="4" sm="6">
        <div class="card tilebox-one mb-0">
          <div class="card-body pt-3 pb-2 px-3">
            <i class="uil uil-file-alt float-end text-info" aria-hidden="true"></i>
            <h6 class="text-uppercase mt-0">Total Entries</h6>
            <h2 class="my-2">
              <span class="fs-4 fs-lg-2">1,247</span>
            </h2>
          </div>
        </div>
      </b-col>

      <!-- Entries Requiring Review Card -->
      <b-col xl="2" lg="4" sm="6">
        <div class="card tilebox-one mb-0">
          <div class="card-body pt-3 pb-2 px-3">
            <i class="uil uil-exclamation-triangle float-end text-warning" aria-hidden="true"></i>
            <h6 class="text-uppercase mt-0">Needs Review</h6>
            <h2 class="my-2">
              <span class="fs-4 fs-lg-2 text-warning">23</span>
            </h2>
          </div>
        </div>
      </b-col>

      <!-- Date Range Card -->
      <b-col xl="2" lg="4" sm="6">
        <div class="card tilebox-one mb-0">
          <div class="card-body pt-3 pb-2 px-3">
            <i class="uil uil-calendar-alt float-end text-secondary" aria-hidden="true"></i>
            <h6 class="text-uppercase mt-0">Date Range</h6>
            <div class="my-2">
              <span class="fs-6">Jan 1 - Nov 24, 2025</span>
            </div>
          </div>
        </div>
      </b-col>
    </b-row>

    <!-- Main Content -->
    <b-row class="g-2 mt-2">
      <!-- Charts Section -->
      <b-col xl="12" lg="12">
        <b-row class="g-2">
          <!-- Tag Distribution Chart -->
          <b-col xl="6" lg="12">
            <div class="card">
              <div class="card-body">
                <h4 class="header-title mb-3">
                  <i class="mdi mdi-tag-multiple text-primary me-1"></i>
                  By Category (Tag)
                </h4>
                <div class="text-center py-5">
                  <base-apex-chart
                    type="donut"
                    :series="tagSeries"
                    :options="tagChartOptions"
                    height="300"
                  />
                  <div class="mt-4 row">
                    <div class="col-4 mb-2" v-for="(tag, i) in tagData" :key="i">
                      <span class="badge" :style="{ backgroundColor: colors[i] }">{{ tag.label }}</span>
                      <div class="fw-bold mt-1">{{ tag.value }}</div>
                      <small class="text-muted">{{ tag.count }} entries</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </b-col>

          <!-- Bucket Distribution Chart -->
          <b-col xl="6" lg="12">
            <div class="card">
              <div class="card-body">
                <h4 class="header-title mb-3">
                  <i class="mdi mdi-briefcase text-success me-1"></i>
                  By Strategic Bucket
                </h4>
                <div class="py-3">
                  <base-apex-chart
                    type="bar"
                    :series="bucketSeries"
                    :options="bucketChartOptions"
                    height="300"
                  />
                </div>
              </div>
            </div>
          </b-col>

          <!-- Monthly Trend Chart -->
          <b-col xl="8" lg="12">
            <div class="card">
              <div class="card-body">
                <h4 class="header-title mb-3">
                  <i class="mdi mdi-chart-line text-info me-1"></i>
                  Monthly Trend (12 Months)
                </h4>
                <base-apex-chart
                  type="area"
                  :series="trendSeries"
                  :options="trendChartOptions"
                  height="300"
                />
              </div>
            </div>
          </b-col>

          <!-- Top Accounts -->
          <b-col xl="4" lg="12">
            <div class="card">
              <div class="card-body">
                <h4 class="header-title mb-3">
                  <i class="mdi mdi-currency-usd text-warning me-1"></i>
                  Top 10 Accounts
                </h4>
                <div class="account-list">
                  <div v-for="(account, index) in topAccounts" :key="index" class="account-item mb-3 p-2 rounded">
                    <div class="d-flex justify-content-between align-items-start">
                      <div class="flex-grow-1">
                        <div class="fw-bold text-dark">{{ account.number }}</div>
                        <small class="text-muted">{{ account.name }}</small>
                      </div>
                      <div class="text-end ms-2">
                        <div class="fw-bold text-success">{{ account.amount }}</div>
                        <small class="text-muted">{{ account.count }} entries</small>
                      </div>
                    </div>
                    <div class="mt-2">
                      <div class="progress" style="height: 4px;">
                        <div
                          class="progress-bar bg-success"
                          :style="{ width: account.width + '%' }"
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </b-col>
        </b-row>
      </b-col>

      <!-- Entries Grid -->
      <b-col xl="12" lg="12" class="mt-2">
        <div class="card">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h4 class="header-title">
                <i class="mdi mdi-format-list-bulleted text-secondary me-1"></i>
                General Ledger Entries
              </h4>
              <div class="d-flex gap-2 align-items-center">
                <!-- Search Input -->
                <div class="input-group" style="width: 300px;">
                  <span class="input-group-text">
                    <i class="mdi mdi-magnify"></i>
                  </span>
                  <input
                    type="text"
                    class="form-control"
                    placeholder="Search entries..."
                  />
                </div>
                <!-- Review Filter Toggle -->
                <button class="btn btn-sm btn-outline-secondary">
                  <i class="mdi mdi-flag"></i>
                  Review Only
                  <span class="badge bg-danger ms-1">23</span>
                </button>
              </div>
            </div>
            
            <!-- Mock Grid -->
            <div class="table-responsive">
              <table class="table table-hover table-sm">
                <thead>
                  <tr>
                    <th>Entry #</th>
                    <th>Posting Date</th>
                    <th>Company</th>
                    <th>Loan #</th>
                    <th>Account</th>
                    <th class="text-end">Debit</th>
                    <th class="text-end">Credit</th>
                    <th class="text-end">Net</th>
                    <th>Tag</th>
                    <th>Bucket</th>
                    <th>Status</th>
                    <th class="text-center">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="entry in mockEntries" :key="entry.id" :class="{ 'table-warning': entry.review }">
                    <td><span class="fw-bold">{{ entry.entryNum }}</span></td>
                    <td>{{ entry.date }}</td>
                    <td>
                      <div class="text-truncate" style="max-width: 120px;" :title="entry.company">
                        {{ entry.company }}
                      </div>
                    </td>
                    <td>{{ entry.loan }}</td>
                    <td>
                      <div class="text-truncate" style="max-width: 100px;" :title="entry.account">
                        {{ entry.account }}
                      </div>
                    </td>
                    <td class="text-end text-success">{{ entry.debit }}</td>
                    <td class="text-end text-danger">{{ entry.credit }}</td>
                    <td class="text-end fw-bold" :class="entry.netClass">{{ entry.net }}</td>
                    <td>
                      <span class="badge" :class="entry.tagClass">{{ entry.tag }}</span>
                    </td>
                    <td>
                      <span class="badge bg-secondary">{{ entry.bucket }}</span>
                    </td>
                    <td>
                      <span v-if="entry.review" class="badge bg-warning">
                        <i class="mdi mdi-flag"></i> Review
                      </span>
                      <span v-else class="badge bg-success">
                        <i class="mdi mdi-check"></i> OK
                      </span>
                    </td>
                    <td class="text-center">
                      <div class="btn-group btn-group-sm">
                        <button class="btn btn-light" title="Edit">
                          <i class="mdi mdi-pencil"></i>
                        </button>
                        <button class="btn btn-light" title="Flag">
                          <i class="mdi mdi-flag text-warning"></i>
                        </button>
                        <button class="btn btn-light text-danger" title="Delete">
                          <i class="mdi mdi-delete"></i>
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Pagination -->
            <div class="d-flex justify-content-between align-items-center mt-3">
              <div class="text-muted">
                Showing 1 to 15 of 1,247 entries
              </div>
              <nav>
                <ul class="pagination pagination-sm mb-0">
                  <li class="page-item disabled">
                    <a class="page-link" href="#"><i class="mdi mdi-chevron-left"></i></a>
                  </li>
                  <li class="page-item active"><a class="page-link" href="#">1</a></li>
                  <li class="page-item"><a class="page-link" href="#">2</a></li>
                  <li class="page-item"><a class="page-link" href="#">3</a></li>
                  <li class="page-item"><a class="page-link" href="#">4</a></li>
                  <li class="page-item"><a class="page-link" href="#">5</a></li>
                  <li class="page-item">
                    <a class="page-link" href="#"><i class="mdi mdi-chevron-right"></i></a>
                  </li>
                </ul>
              </nav>
            </div>
          </div>
        </div>
      </b-col>
    </b-row>
  </Layout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Layout from '@/components/layouts/layout.vue'
import BaseApexChart from '@/components/base-apex-chart.vue'

// Mock data for charts
const colors = ['#727cf5', '#0acf97', '#fa5c7c', '#ffbc00', '#39afd1', '#6c757d', '#f672a7', '#5b69bc']

const tagData = ref([
  { label: 'Loan Origination', value: '$12.5MM', count: 324 },
  { label: 'Property Acquisition', value: '$8.2MM', count: 156 },
  { label: 'Loan Payment', value: '$6.8MM', count: 289 },
  { label: 'Operating Expense', value: '$4.3MM', count: 198 },
  { label: 'Interest Income', value: '$3.9MM', count: 145 },
  { label: 'Other', value: '$2.1MM', count: 135 },
])

const tagSeries = ref([12.5, 8.2, 6.8, 4.3, 3.9, 2.1])

const tagChartOptions = ref({
  labels: tagData.value.map(t => t.label),
  colors: colors,
  legend: { show: false },
  plotOptions: {
    pie: {
      donut: {
        size: '70%'
      }
    }
  },
  dataLabels: { enabled: false }
})

const bucketSeries = ref([{
  name: 'Net Amount',
  data: [15.2, 12.8, 8.5, 5.3, 3.2, 2.1, 1.8, 0.9]
}])

const bucketChartOptions = ref({
  chart: {
    type: 'bar',
    toolbar: { show: false }
  },
  plotOptions: {
    bar: {
      horizontal: true,
      distributed: true
    }
  },
  colors: colors,
  dataLabels: { enabled: false },
  xaxis: {
    categories: ['Acquisition', 'Servicing', 'Asset Mgmt', 'Disposition', 'Capital Markets', 'Fund Ops', 'Overhead', 'Special'],
    labels: {
      formatter: (val: number) => '$' + val.toFixed(1) + 'MM'
    }
  },
  legend: { show: false }
})

const trendSeries = ref([
  {
    name: 'Debits',
    data: [3.2, 3.8, 4.1, 3.5, 4.2, 4.8, 3.9, 4.5, 5.1, 4.3, 4.7, 5.2]
  },
  {
    name: 'Credits',
    data: [2.9, 3.5, 3.8, 3.2, 3.9, 4.5, 3.6, 4.2, 4.8, 4.0, 4.4, 4.9]
  }
])

const trendChartOptions = ref({
  chart: {
    type: 'area',
    toolbar: { show: false }
  },
  colors: ['#0acf97', '#fa5c7c'],
  stroke: {
    width: 2,
    curve: 'smooth'
  },
  fill: {
    type: 'gradient',
    gradient: {
      shadeIntensity: 1,
      opacityFrom: 0.4,
      opacityTo: 0.1
    }
  },
  xaxis: {
    categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  },
  yaxis: {
    labels: {
      formatter: (val: number) => '$' + val.toFixed(1) + 'MM'
    }
  },
  dataLabels: { enabled: false },
  legend: {
    position: 'top',
    horizontalAlign: 'right'
  }
})

const topAccounts = ref([
  { number: '1100', name: 'Loan Receivables', amount: '$15.2MM', count: 324, width: 100 },
  { number: '1200', name: 'Property Assets', amount: '$12.8MM', count: 156, width: 84 },
  { number: '4100', name: 'Interest Income', amount: '$8.5MM', count: 289, width: 56 },
  { number: '5100', name: 'Operating Expenses', amount: '$6.3MM', count: 198, width: 41 },
  { number: '2100', name: 'Notes Payable', amount: '$5.1MM', count: 145, width: 34 },
  { number: '1500', name: 'Cash', amount: '$4.2MM', count: 87, width: 28 },
  { number: '3100', name: 'Equity', amount: '$3.8MM', count: 56, width: 25 },
  { number: '5200', name: 'Admin Expenses', amount: '$2.9MM', count: 134, width: 19 },
  { number: '4200', name: 'Fee Income', amount: '$2.3MM', count: 67, width: 15 },
  { number: '5300', name: 'Legal Fees', amount: '$1.8MM', count: 89, width: 12 },
])

const mockEntries = ref([
  { id: 1, entryNum: 'GL-2025-1247', date: 'Nov 24, 2025', company: 'Alpha Fund I, LLC', loan: 'LN-45678', account: '1100 - Loans', debit: '$250,000', credit: '-', net: '$250,000', netClass: 'text-success', tag: 'Loan Origination', tagClass: 'bg-primary', bucket: 'Acquisition', review: false },
  { id: 2, entryNum: 'GL-2025-1246', date: 'Nov 23, 2025', company: 'Beta Properties', loan: 'LN-45677', account: '1200 - Property', debit: '$180,000', credit: '-', net: '$180,000', netClass: 'text-success', tag: 'Property Acquisition', tagClass: 'bg-info', bucket: 'Acquisition', review: true },
  { id: 3, entryNum: 'GL-2025-1245', date: 'Nov 23, 2025', company: 'Alpha Fund I, LLC', loan: 'LN-45676', account: '4100 - Interest', debit: '-', credit: '$12,500', net: '-$12,500', netClass: 'text-danger', tag: 'Interest Income', tagClass: 'bg-success', bucket: 'Servicing', review: false },
  { id: 4, entryNum: 'GL-2025-1244', date: 'Nov 22, 2025', company: 'Gamma Investments', loan: 'LN-45675', account: '1100 - Loans', debit: '$95,000', credit: '-', net: '$95,000', netClass: 'text-success', tag: 'Loan Payment', tagClass: 'bg-success', bucket: 'Servicing', review: false },
  { id: 5, entryNum: 'GL-2025-1243', date: 'Nov 22, 2025', company: 'Delta Holdings', loan: 'LN-45674', account: '5100 - OpEx', debit: '$8,500', credit: '-', net: '$8,500', netClass: 'text-success', tag: 'Operating Expense', tagClass: 'bg-warning', bucket: 'Asset Mgmt', review: false },
  { id: 6, entryNum: 'GL-2025-1242', date: 'Nov 21, 2025', company: 'Epsilon RE', loan: 'LN-45673', account: '1200 - Property', debit: '$425,000', credit: '-', net: '$425,000', netClass: 'text-success', tag: 'Property Acquisition', tagClass: 'bg-info', bucket: 'Acquisition', review: true },
  { id: 7, entryNum: 'GL-2025-1241', date: 'Nov 21, 2025', company: 'Alpha Fund I, LLC', loan: 'LN-45672', account: '5200 - Admin', debit: '$3,200', credit: '-', net: '$3,200', netClass: 'text-success', tag: 'Operating Expense', tagClass: 'bg-warning', bucket: 'Overhead', review: false },
  { id: 8, entryNum: 'GL-2025-1240', date: 'Nov 20, 2025', company: 'Zeta Capital', loan: 'LN-45671', account: '1100 - Loans', debit: '$150,000', credit: '-', net: '$150,000', netClass: 'text-success', tag: 'Loan Origination', tagClass: 'bg-primary', bucket: 'Acquisition', review: false },
  { id: 9, entryNum: 'GL-2025-1239', date: 'Nov 20, 2025', company: 'Theta Properties', loan: 'LN-45670', account: '4200 - Fees', debit: '-', credit: '$5,500', net: '-$5,500', netClass: 'text-danger', tag: 'Fee Income', tagClass: 'bg-success', bucket: 'Servicing', review: false },
  { id: 10, entryNum: 'GL-2025-1238', date: 'Nov 19, 2025', company: 'Iota Ventures', loan: 'LN-45669', account: '1200 - Property', debit: '$385,000', credit: '-', net: '$385,000', netClass: 'text-success', tag: 'Property Disposition', tagClass: 'bg-danger', bucket: 'Disposition', review: true },
  { id: 11, entryNum: 'GL-2025-1237', date: 'Nov 19, 2025', company: 'Alpha Fund I, LLC', loan: 'LN-45668', account: '5300 - Legal', debit: '$12,000', credit: '-', net: '$12,000', netClass: 'text-success', tag: 'Operating Expense', tagClass: 'bg-warning', bucket: 'Overhead', review: false },
  { id: 12, entryNum: 'GL-2025-1236', date: 'Nov 18, 2025', company: 'Kappa Mortgage', loan: 'LN-45667', account: '1100 - Loans', debit: '$275,000', credit: '-', net: '$275,000', netClass: 'text-success', tag: 'Loan Origination', tagClass: 'bg-primary', bucket: 'Acquisition', review: false },
  { id: 13, entryNum: 'GL-2025-1235', date: 'Nov 18, 2025', company: 'Lambda Real Estate', loan: 'LN-45666', account: '4100 - Interest', debit: '-', credit: '$18,750', net: '-$18,750', netClass: 'text-danger', tag: 'Interest Income', tagClass: 'bg-success', bucket: 'Servicing', review: false },
  { id: 14, entryNum: 'GL-2025-1234', date: 'Nov 17, 2025', company: 'Mu Capital', loan: 'LN-45665', account: '2100 - Payable', debit: '-', credit: '$100,000', net: '-$100,000', netClass: 'text-danger', tag: 'Capital Expense', tagClass: 'bg-warning', bucket: 'Capital Markets', review: true },
  { id: 15, entryNum: 'GL-2025-1233', date: 'Nov 17, 2025', company: 'Nu Properties', loan: 'LN-45664', account: '1200 - Property', debit: '$520,000', credit: '-', net: '$520,000', netClass: 'text-success', tag: 'Property Acquisition', tagClass: 'bg-info', bucket: 'Acquisition', review: false },
])
</script>

<style scoped>
.tilebox-one {
  transition: transform 0.2s ease;
}

.tilebox-one:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.page-title-box {
  margin-bottom: 1rem;
}

.input-group-text {
  background-color: #f1f3fa;
  border-color: #dee2e6;
}

.table th {
  font-weight: 600;
  font-size: 0.85rem;
  text-transform: uppercase;
  background-color: #f8f9fa;
}

.table-hover tbody tr:hover {
  background-color: #f1f3fa;
}

.table-warning {
  background-color: #fff3cd !important;
}

.btn-group-sm .btn {
  padding: 0.25rem 0.5rem;
}

.account-item {
  background-color: #f8f9fa;
  transition: all 0.2s ease;
}

.account-item:hover {
  background-color: #e9ecef;
  transform: translateX(4px);
}

@media (max-width: 768px) {
  .page-title-right .d-flex {
    flex-direction: column;
    width: 100%;
  }
  
  .page-title-right .btn {
    width: 100%;
  }
  
  .input-group {
    width: 100% !important;
  }
}
</style>

