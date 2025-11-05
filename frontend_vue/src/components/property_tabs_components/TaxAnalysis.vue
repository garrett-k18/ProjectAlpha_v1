<template>
  <!-- Root card container ensures consistent Hyper UI appearance -->
  <div class="card h-100">
    <!-- Card header communicates section purpose -->
    <div class="card-header d-flex align-items-center justify-content-between">
      <!-- Title follows dashboard typography pattern -->
      <h4 class="header-title mb-0">Tax Analysis</h4>
      <!-- Placeholder badge slot reserved for future status chips -->
      <slot name="status"></slot>
    </div>
    <!-- Card body holds tabular and detail content -->
    <div class="card-body">
      <!-- Taxing authority section lists line items subject to ad valorem tax -->
      <section class="mb-4">
        <!-- Section heading mirrors screenshot structure -->
        <h6 class="text-uppercase fw-semibold text-muted mb-2">Taxing Authority</h6>
        <!-- Responsive wrapper keeps table scrollable on narrow screens -->
        <div class="table-responsive">
          <!-- Compact table delivers rate and tax breakdown -->
          <table class="table table-sm align-middle mb-2">
            <thead class="table-light">
              <tr>
                <th scope="col">Authority</th>
                <th scope="col" class="text-end">Rate</th>
                <th scope="col" class="text-end">Assessed</th>
                <th scope="col" class="text-end">Exemption</th>
                <th scope="col" class="text-end">Taxable</th>
                <th scope="col" class="text-end">Tax</th>
              </tr>
            </thead>
            <tbody>
              <!-- Render each taxing authority line item or a helpful empty state -->
              <tr v-for="(item, index) in authorityRows" :key="`authority-${index}`">
                <td class="text-wrap">{{ formatDisplay(item.authority) }}</td>
                <td class="text-end">{{ formatDisplay(item.rate) }}</td>
                <td class="text-end">{{ formatCurrency(item.assessed) }}</td>
                <td class="text-end">{{ formatCurrency(item.exemption) }}</td>
                <td class="text-end">{{ formatCurrency(item.taxable) }}</td>
                <td class="text-end fw-semibold">{{ formatCurrency(item.tax) }}</td>
              </tr>
              <tr v-if="authorityRows.length === 0">
                <td colspan="6" class="text-center text-muted py-3">No taxing authorities supplied.</td>
              </tr>
            </tbody>
          </table>
        </div>
        <!-- Summary footer highlights total ad valorem tax burden -->
        <div class="d-flex justify-content-between align-items-center bg-light border rounded px-3 py-2">
          <span class="fw-semibold">Total Ad Valorem Taxes</span>
          <span class="fw-semibold">{{ formatCurrency(authorityTotal) }}</span>
        </div>
      </section>

      <!-- Special assessments section mirrors screenshot layout -->
      <section class="mb-4">
        <!-- Heading distinguishes special charges from ad valorem taxes -->
        <h6 class="text-uppercase fw-semibold text-muted mb-2">Direct Charges &amp; Special Assessments</h6>
        <!-- Responsive table for assessment line items -->
        <div class="table-responsive">
          <table class="table table-sm align-middle mb-2">
            <thead class="table-light">
              <tr>
                <th scope="col">Levying Authority</th>
                <th scope="col">Code</th>
                <th scope="col">Phone</th>
                <th scope="col" class="text-end">Amount</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in assessmentRows" :key="`assessment-${index}`">
                <td class="text-wrap">{{ formatDisplay(item.authority) }}</td>
                <td>{{ formatDisplay(item.code) }}</td>
                <td>{{ formatDisplay(item.phone) }}</td>
                <td class="text-end fw-semibold">{{ formatCurrency(item.amount) }}</td>
              </tr>
              <tr v-if="assessmentRows.length === 0">
                <td colspan="4" class="text-center text-muted py-3">No assessments supplied.</td>
              </tr>
            </tbody>
          </table>
        </div>
        <!-- Total row surfaces aggregate assessment burden -->
        <div class="d-flex justify-content-between align-items-center bg-light border rounded px-3 py-2">
          <span class="fw-semibold">Total Direct Charges &amp; Special Assessments</span>
          <span class="fw-semibold">{{ formatCurrency(assessmentTotal) }}</span>
        </div>
      </section>

      <!-- Totals grid communicates payment status -->
      <section class="mb-4">
        <!-- Section heading clarifies summary values below -->
        <h6 class="text-uppercase fw-semibold text-muted mb-2">Totals</h6>
        <!-- Use list group styling for clarity and responsive stacking -->
        <div class="list-group list-group-flush">
          <div class="list-group-item d-flex justify-content-between align-items-center">
            <span>Total Tax</span>
            <span class="fw-semibold">{{ formatCurrency(totals.totalTax) }}</span>
          </div>
          <div class="list-group-item d-flex justify-content-between align-items-center">
            <span>Total Payments Made</span>
            <span class="fw-semibold">{{ formatCurrency(totals.totalPayments) }}</span>
          </div>
          <div class="list-group-item d-flex justify-content-between align-items-center">
            <span>Balance Due</span>
            <span class="fw-semibold text-danger">{{ formatCurrency(totals.balanceDue) }}</span>
          </div>
        </div>
      </section>

      <!-- Parcel detail cards split into three columns as in screenshot -->
      <section>
        <!-- Heading guides reader to detailed parcel information -->
        <h6 class="text-uppercase fw-semibold text-muted mb-2">Parcel Details</h6>
        <!-- Responsive row to stack on mobile and align columns on desktop -->
        <div class="row g-3">
          <!-- General information column -->
          <div class="col-12 col-lg-4">
            <div class="border rounded p-3 h-100">
              <h6 class="fw-semibold text-muted text-uppercase small">General</h6>
              <dl class="row mb-0">
                <dt class="col-6">Account Number</dt>
                <dd class="col-6 text-end">{{ formatDisplay(parcel.general.accountNumber) }}</dd>
                <dt class="col-6">Tax Rate Area</dt>
                <dd class="col-6 text-end">{{ formatDisplay(parcel.general.taxRateArea) }}</dd>
                <dt class="col-6">Tax Rate</dt>
                <dd class="col-6 text-end">{{ formatDisplay(parcel.general.taxRate) }}</dd>
                <dt class="col-6">Tax Rate Year</dt>
                <dd class="col-6 text-end">{{ formatDisplay(parcel.general.taxRateYear) }}</dd>
              </dl>
            </div>
          </div>
          <!-- Assessed values column -->
          <div class="col-12 col-lg-4">
            <div class="border rounded p-3 h-100">
              <h6 class="fw-semibold text-muted text-uppercase small">Assessed Values</h6>
              <dl class="row mb-0">
                <dt class="col-6">Land</dt>
                <dd class="col-6 text-end">{{ formatCurrency(parcel.assessed.land) }}</dd>
                <dt class="col-6">Improvements</dt>
                <dd class="col-6 text-end">{{ formatCurrency(parcel.assessed.improvements) }}</dd>
                <dt class="col-6">Total Taxable Value</dt>
                <dd class="col-6 text-end">{{ formatCurrency(parcel.assessed.totalTaxable) }}</dd>
              </dl>
            </div>
          </div>
          <!-- Bill information column -->
          <div class="col-12 col-lg-4">
            <div class="border rounded p-3 h-100">
              <h6 class="fw-semibold text-muted text-uppercase small">Bill Information</h6>
              <dl class="row mb-0">
                <dt class="col-6">Bill #</dt>
                <dd class="col-6 text-end">{{ formatDisplay(parcel.bill.billNumber) }}</dd>
                <dt class="col-6">Assessment Year</dt>
                <dd class="col-6 text-end">{{ formatDisplay(parcel.bill.assessmentYear) }}</dd>
                <dt class="col-6">Escrow Company</dt>
                <dd class="col-6 text-end">{{ formatDisplay(parcel.bill.escrowCompany) }}</dd>
                <dt class="col-6">Total Tax</dt>
                <dd class="col-6 text-end">{{ formatCurrency(parcel.bill.totalTax) }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
// Import Vue helpers for defaults and computed logic
import { computed, withDefaults } from 'vue'

// Interface describing a single taxing authority entry
interface TaxAuthorityLine {
  authority?: string
  rate?: string | number
  assessed?: string | number
  exemption?: string | number
  taxable?: string | number
  tax?: string | number
}

// Interface describing a direct charge or special assessment row
interface SpecialAssessmentLine {
  authority?: string
  code?: string
  phone?: string
  amount?: string | number
}

// Interface summarizing high level totals
interface TaxTotalsSummary {
  totalTax?: string | number
  totalPayments?: string | number
  balanceDue?: string | number
}

// Interface describing parcel level detail sections
interface ParcelDetailsSummary {
  general: {
    accountNumber?: string
    taxRateArea?: string
    taxRate?: string | number
    taxRateYear?: string | number
  }
  assessed: {
    land?: string | number
    improvements?: string | number
    totalTaxable?: string | number
  }
  bill: {
    billNumber?: string
    assessmentYear?: string | number
    escrowCompany?: string
    totalTax?: string | number
  }
}

// Define component props with sensible defaults to ensure safe rendering
const props = withDefaults(defineProps<{
  taxAuthorities?: TaxAuthorityLine[]
  authorityTotal?: string | number | null
  specialAssessments?: SpecialAssessmentLine[]
  assessmentTotal?: string | number | null
  totals?: TaxTotalsSummary | null
  parcel?: ParcelDetailsSummary | null
}>(), {
  taxAuthorities: () => [],
  authorityTotal: null,
  specialAssessments: () => [],
  assessmentTotal: null,
  totals: () => ({ totalTax: null, totalPayments: null, balanceDue: null }),
  parcel: () => ({
    general: {},
    assessed: {},
    bill: {},
  }),
})

// Computed array normalises taxing authority rows for templating
const authorityRows = computed(() => props.taxAuthorities ?? [])

// Computed value ensures total string fallback for ad valorem taxes
const authorityTotal = computed(() => props.authorityTotal ?? null)

// Computed array normalises assessment rows for rendering
const assessmentRows = computed(() => props.specialAssessments ?? [])

// Computed value provides fallback for assessment totals
const assessmentTotal = computed(() => props.assessmentTotal ?? null)

// Computed object returns totals ensuring non-null object for template
const totals = computed(() => props.totals ?? { totalTax: null, totalPayments: null, balanceDue: null })

// Computed object guarantees parcel sections exist to avoid undefined access
const parcel = computed(() => props.parcel ?? { general: {}, assessed: {}, bill: {} })

// Helper formats currency values using US locale while handling blanks gracefully
function formatCurrency(value?: string | number | null): string {
  if (value === null || value === undefined || value === '') {
    return '—'
  }
  const numericValue = typeof value === 'string' ? Number(value) : value
  if (Number.isNaN(numericValue)) {
    return String(value)
  }
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 2 }).format(numericValue)
}

// Helper returns em dash when display value is missing or blank
function formatDisplay(value?: string | number | null): string {
  if (value === null || value === undefined || value === '') {
    return '—'
  }
  return String(value)
}
</script>

<style scoped>
/* Add subtle spacing between sections mirroring reference layout */
section + section {
  border-top: 1px solid var(--bs-border-color);
  padding-top: 1rem;
}
</style>
