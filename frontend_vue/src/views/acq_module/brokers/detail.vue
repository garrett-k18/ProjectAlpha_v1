<template>
  <!--
    Broker Detail Page
    - Displays basic broker information (name, email, firm, location)
    - Shows quick stats (total invites, assigned loans, submissions)
    - Lists loans assigned to this broker via token invites

    UI guidelines:
    - Use existing framework styles (Hyper/BootstrapVue) without custom CSS
    - Keep markup semantic and accessible
  -->
  <div class="container-fluid">
    <!-- Header Section: Broker Identity + Quick Actions -->
    <div class="d-flex align-items-center justify-content-between mb-3">
      <div>
        <h3 class="mb-1">
          <!-- Broker name or fallback to email/id -->
          {{ brokerTitle }}
        </h3>
        <div class="text-muted">
          <!-- Firm and location line, rendered only if available -->
          <span v-if="broker?.broker_firm">{{ broker?.broker_firm }}</span>
          <span v-if="broker?.broker_city || broker?.broker_state"> • {{ broker?.broker_city }}<span v-if="broker?.broker_state">, {{ broker?.broker_state }}</span></span>
        </div>
        <div class="small text-muted" v-if="broker?.broker_email">{{ broker?.broker_email }}</div>
      </div>
      <!-- Refresh buttons for detail and assigned lists -->
      <div class="btn-group">
        <button class="btn btn-sm btn-outline-primary" :disabled="isLoadingDetail" @click="refreshDetail">Refresh Details</button>
        <button class="btn btn-sm btn-outline-primary" :disabled="isLoadingAssigned" @click="refreshAssigned">Refresh Loans</button>
      </div>
    </div>

    <!-- Alerts for errors -->
    <div v-if="detailError" class="alert alert-danger" role="alert">
      {{ detailError }}
    </div>
    <div v-if="assignedError" class="alert alert-danger" role="alert">
      {{ assignedError }}
    </div>

    <!-- Summary Cards: total invites / assigned loans / submissions -->
    <div class="row g-3 mb-3">
      <div class="col-md-4">
        <div class="card h-100">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <h6 class="text-uppercase text-muted mb-1">Total Invites</h6>
                <h3 class="mb-0">{{ broker?.stats.total_invites ?? 0 }}</h3>
              </div>
              <i class="uil-envelope text-primary fs-2"></i>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card h-100">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <h6 class="text-uppercase text-muted mb-1">Assigned Loans</h6>
                <h3 class="mb-0">{{ broker?.stats.assigned_loan_count ?? 0 }}</h3>
              </div>
              <i class="uil-link-alt text-success fs-2"></i>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card h-100">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <h6 class="text-uppercase text-muted mb-1">Submissions</h6>
                <h3 class="mb-0">{{ broker?.stats.submissions_count ?? 0 }}</h3>
              </div>
              <i class="uil-check-circle text-info fs-2"></i>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Assigned Loans Table -->
    <div class="card">
      <div class="card-header d-flex align-items-center justify-content-between">
        <h5 class="mb-0">Assigned Loans</h5>
        <span class="badge bg-secondary" v-if="assigned.length">{{ assigned.length }} total</span>
      </div>
      <div class="card-body p-0">
        <!-- Loading State -->
        <div v-if="isLoadingAssigned" class="p-4 text-center text-muted">Loading loans…</div>
        <!-- Empty State -->
        <div v-else-if="!assigned.length" class="p-4 text-center text-muted">No loans assigned.</div>
        <!-- Data Table -->
        <div v-else class="table-responsive">
          <table class="table table-hover table-sm mb-0">
            <thead class="table-light">
              <tr>
                <th scope="col">Loan ID</th>
                <th scope="col">Seller</th>
                <th scope="col">Trade</th>
                <th scope="col">Address</th>
                <th scope="col" class="text-end">Current Balance</th>
                <th scope="col">Token</th>
                <th scope="col">Status</th>
                <th scope="col" class="text-end">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in assigned" :key="row.seller_raw_data">
                <td>{{ row.seller_raw_data }}</td>
                <td>{{ row.seller?.name ?? row.seller?.id ?? '—' }}</td>
                <td>{{ row.trade?.name ?? row.trade?.id ?? '—' }}</td>
                <td>
                  <span>{{ row.address?.street_address }}</span>
                  <span v-if="row.address?.city || row.address?.state">, {{ row.address?.city }}<span v-if="row.address?.state">, {{ row.address?.state }}</span></span>
                  <span v-if="row.address?.zip"> {{ row.address?.zip }}</span>
                </td>
                <td class="text-end">{{ row.current_balance ?? '—' }}</td>
                <td>
                  <span class="text-monospace small">{{ row.token.value }}</span>
                </td>
                <td>
                  <span
                    class="badge me-1"
                    :class="{
                      'bg-success': !row.token.is_expired && !row.token.is_used,
                      'bg-warning': row.token.is_used && !row.token.is_expired,
                      'bg-danger': row.token.is_expired,
                    }"
                  >
                    <span v-if="row.token.is_expired">Expired</span>
                    <span v-else-if="row.token.is_used">Used</span>
                    <span v-else>Active</span>
                  </span>
                  <span class="badge bg-info" v-if="row.has_submission">Submission</span>
                </td>
                <td class="text-end">
                  <!-- Example action: copy public link -->
                  <button class="btn btn-xs btn-outline-secondary" @click="copyPublicLink(row.token.value)">
                    Copy Link
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// -----------------------------
// Script: Broker Detail Page
// -----------------------------
// - Accepts brokerId as a prop (from router)
// - Loads broker detail and assigned loans via Pinia store
// - Provides refresh actions and simple utilities

import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useBrokerLoansStore, type BrokerDetail, type AssignedLoanEntry } from '@/stores/brokerLoans'

// Props: brokerId provided by router (see routes.ts props mapping)
const props = defineProps<{ brokerId: number }>()

// Access current route if needed (e.g., for building links)
const route = useRoute()

// Initialize the Pinia store used for broker data
const store = useBrokerLoansStore()

// Local computed state extracted from store for reactivity and type-safety
const broker = computed<BrokerDetail | undefined>(() => store.getBroker(props.brokerId))
const assigned = computed<AssignedLoanEntry[]>(() => store.getAssignedLoans(props.brokerId))
const isLoadingDetail = computed<boolean>(() => !!store.loadingDetail[props.brokerId])
const isLoadingAssigned = computed<boolean>(() => !!store.loadingAssigned[props.brokerId])
const detailError = computed<string | null | undefined>(() => store.errorDetail[props.brokerId])
const assignedError = computed<string | null | undefined>(() => store.errorAssigned[props.brokerId])

// Friendly title that falls back to email or broker id if name is missing
const brokerTitle = computed<string>(() => {
  if (broker.value?.broker_name) return broker.value.broker_name
  if (broker.value?.broker_email) return broker.value.broker_email
  return `Broker #${props.brokerId}`
})

// Fetch functions with force refresh control
async function refreshDetail(): Promise<void> {
  await store.fetchBrokerDetail(props.brokerId, true)
}
async function refreshAssigned(): Promise<void> {
  await store.fetchAssignedLoans(props.brokerId, true)
}

// Utility: copy the public broker invite link to clipboard
async function copyPublicLink(token: string): Promise<void> {
  // Construct the absolute URL for the public brokerview route
  // Public route is defined at `/brokerview/:token` (no auth required)
  const origin = window.location.origin
  const url = `${origin}/brokerview/${token}`
  await navigator.clipboard.writeText(url)
}

// Lifecycle: initial load of both detail and assigned lists
onMounted(async () => {
  // In parallel is fine since endpoints are independent
  await Promise.all([
    store.fetchBrokerDetail(props.brokerId),
    store.fetchAssignedLoans(props.brokerId),
  ])
})
</script>
