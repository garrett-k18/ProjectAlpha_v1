<template>
  <b-row class="g-2 mb-2">
    <!-- Total Debits Card -->
    <b-col xl="2" lg="4" sm="6">
      <div class="card tilebox-one mb-0">
        <div class="card-body pt-3 pb-2 px-3">
          <i class="uil uil-plus-circle float-end text-success" aria-hidden="true"></i>
          <h6 class="text-uppercase mt-0">Total Debits</h6>
          <h2 class="my-2">
            <span v-if="loading">...</span>
            <span v-else class="fs-4 fs-lg-2 text-success">{{ formatCurrency(totalDebits) }}</span>
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
            <span v-if="loading">...</span>
            <span v-else class="fs-4 fs-lg-2 text-danger">{{ formatCurrency(totalCredits) }}</span>
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
            <span v-if="loading">...</span>
            <span v-else :class="['fs-4 fs-lg-2', netColorClass]">{{ formatCurrency(netTotal) }}</span>
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
            <span v-if="loading">...</span>
            <span v-else class="fs-4 fs-lg-2">{{ formatNumber(totalEntries) }}</span>
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
            <span v-if="loading">...</span>
            <span v-else class="fs-4 fs-lg-2 text-warning">{{ formatNumber(entriesRequiringReview) }}</span>
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
            <span v-if="loading">...</span>
            <span v-else class="fs-6">
              {{ dateRangeDisplay }}
            </span>
          </div>
        </div>
      </div>
    </b-col>
  </b-row>
</template>

<script setup lang="ts">
/**
 * WHAT: Summary cards component for GL dashboard
 * WHY: Display key GL metrics at a glance
 * HOW: Format and display summary statistics from store
 */
import { computed } from 'vue'
import type { GLEntrySummary } from '@/stores/generalLedger'

const props = defineProps<{
  summary: GLEntrySummary | null
  loading: boolean
}>()

// WHAT: Parse and compute metric values
// WHY: Convert string decimals to numbers for formatting
// HOW: Safe parsing with fallback to 0
const totalDebits = computed<number>(() => {
  if (!props.summary) return 0
  return typeof props.summary.total_debits === 'string'
    ? parseFloat(props.summary.total_debits)
    : props.summary.total_debits
})

const totalCredits = computed<number>(() => {
  if (!props.summary) return 0
  return typeof props.summary.total_credits === 'string'
    ? parseFloat(props.summary.total_credits)
    : props.summary.total_credits
})

const netTotal = computed<number>(() => {
  if (!props.summary) return 0
  return typeof props.summary.net_total === 'string'
    ? parseFloat(props.summary.net_total)
    : props.summary.net_total
})

const totalEntries = computed<number>(() => {
  return props.summary?.total_entries || 0
})

const entriesRequiringReview = computed<number>(() => {
  return props.summary?.entries_requiring_review || 0
})

// WHAT: Compute color class for net total
// WHY: Visual indication of positive/negative balance
// HOW: Green for positive, red for negative
const netColorClass = computed<string>(() => {
  const net = netTotal.value
  if (net > 0) return 'text-success'
  if (net < 0) return 'text-danger'
  return 'text-secondary'
})

// WHAT: Format date range for display
// WHY: Show date range of filtered entries
// HOW: Format dates or show "All Time"
const dateRangeDisplay = computed<string>(() => {
  if (!props.summary) return 'N/A'
  
  const start = props.summary.date_range_start
  const end = props.summary.date_range_end
  
  if (!start || !end) return 'All Time'
  
  const formatDate = (dateStr: string): string => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: '2-digit' })
  }
  
  return `${formatDate(start)} - ${formatDate(end)}`
})

// -----------------------------
// Formatting Utilities
// -----------------------------

/**
 * WHAT: Format currency values with appropriate units
 * WHY: Display large numbers in readable format (MM, B)
 * HOW: Check magnitude and apply appropriate suffix
 */
function formatCurrency(value: number): string {
  const abs = Math.abs(value || 0)
  const sign = value < 0 ? '-' : ''
  
  if (abs >= 1_000_000_000) {
    return `${sign}$${(abs / 1_000_000_000).toFixed(2)}B`
  }
  if (abs >= 1_000_000) {
    return `${sign}$${(abs / 1_000_000).toFixed(2)}MM`
  }
  if (abs >= 1_000) {
    return `${sign}$${(abs / 1_000).toFixed(1)}K`
  }
  return `${sign}$${abs.toFixed(0)}`
}

/**
 * WHAT: Format numbers with thousand separators
 * WHY: Improve readability of large counts
 * HOW: Use toLocaleString
 */
function formatNumber(value: number): string {
  return (value || 0).toLocaleString()
}
</script>

<style scoped>
.tilebox-one {
  transition: transform 0.2s ease;
}

.tilebox-one:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
</style>

