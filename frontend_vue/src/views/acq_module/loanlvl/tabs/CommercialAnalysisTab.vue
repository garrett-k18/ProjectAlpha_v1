<template>
  <!-- Commercial Analysis Tab
       - Subject summary: Unit Mix (if any)
       - Lease Comp Unit Mix (common)
       - Lease Comp Rent Roll (rare)
       Uses Hyper UI utilities + Bootstrap classes for clean layout.
  -->
  <div class="row g-3">
    <!-- Subject Unit Mix - using reusable component -->
    <div class="col-12">
      <UnitMixTable 
        :unit-mix-data="subjectUnitMix"
        :loading="loading.subjectUnitMix"
        title="Subject Unit Mix"
        :show-rent-per-sqft="true"
        :show-totals="true"
      />
    </div>

    <!-- Subject Rent Roll - using reusable component -->
    <div class="col-12">
      <RentRollTable
        :rent-roll-data="subjectRentRoll"
        :loading="loading.subjectRentRoll"
        title="Subject Rent Roll"
      />
    </div>

    <!-- Lease Comparable Unit Mix -->
    <div class="col-12">
      <div class="card h-100">
        <div class="card-header d-flex align-items-center justify-content-between">
          <h5 class="card-title mb-0">Lease Comp Unit Mix</h5>
        </div>
        <div class="card-body">
          <div v-if="loading.compMix" class="text-muted">Loading lease comp unit mix…</div>
          <div v-else-if="leaseCompUnitMix.length === 0" class="text-muted">No lease comp unit mix found.</div>
          <div v-else class="table-responsive">
            <table class="table table-sm align-middle mb-0">
              <thead>
                <tr>
                  <th>Property</th>
                  <th>Unit Type</th>
                  <th class="text-end">Count</th>
                  <th class="text-end">Avg Sqft</th>
                  <th class="text-end">Avg Rent</th>
                  <th class="text-end">Rent/Sqft</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(m, idx) in leaseCompUnitMix" :key="`mix-${idx}`">
                  <td>{{ m.property_label }}</td>
                  <td>{{ m.unit_type }}</td>
                  <td class="text-end">{{ formatInt(m.unit_count) }}</td>
                  <td class="text-end">{{ formatInt(m.unit_avg_sqft) }}</td>
                  <td class="text-end">{{ formatCurrency(m.unit_avg_rent) }}</td>
                  <td class="text-end">{{ formatCurrency(m.price_sqft) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Lease Comparable Rent Roll (rare) -->
    <div class="col-12">
      <div class="card h-100">
        <div class="card-header d-flex align-items-center justify-content-between">
          <h5 class="card-title mb-0">Lease Comp Rent Roll</h5>
        </div>
        <div class="card-body">
          <div v-if="loading.compRoll" class="text-muted">Loading lease comp rent roll…</div>
          <div v-else-if="leaseCompRentRoll.length === 0" class="text-muted">No lease comp rent roll records.</div>
          <div v-else class="table-responsive">
            <table class="table table-sm align-middle mb-0">
              <thead>
                <tr>
                  <th>Property</th>
                  <th>Unit</th>
                  <th class="text-end">Beds</th>
                  <th class="text-end">Baths</th>
                  <th class="text-end">Sqft</th>
                  <th class="text-end">Rent</th>
                  <th class="text-end">Start</th>
                  <th class="text-end">End</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(r, idx) in leaseCompRentRoll" :key="`roll-${idx}`">
                  <td>{{ r.property_label }}</td>
                  <td>{{ r.unit_number }}</td>
                  <td class="text-end">{{ r.beds ?? '-' }}</td>
                  <td class="text-end">{{ r.baths ?? '-' }}</td>
                  <td class="text-end">{{ formatInt(r.unit_sqft) }}</td>
                  <td class="text-end">{{ formatCurrency(r.monthly_rent) }}</td>
                  <td class="text-end">{{ formatDate(r.lease_start_date) }}</td>
                  <td class="text-end">{{ formatDate(r.lease_end_date) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Props are passed from LoanTabs
// - row: current asset row (should include is_commercial boolean from backend)
// - assetId: hub ID
// - module: 'acq' | 'am' (selects API base)
import { defineProps, ref, onMounted, watch } from 'vue'
import http from '@/lib/http'

// Import reusable components
import UnitMixTable from '@/views/acq_module/loanlvl/components/commercial/UnitMixTable.vue'
import RentRollTable from '@/views/acq_module/loanlvl/components/commercial/RentRollTable.vue'

const props = defineProps<{
  row: Record<string, any> | null
  assetId: string | number | null
  module?: 'acq' | 'am'
}>()

// Loading flags
const loading = ref({ 
  subjectUnitMix: false, 
  subjectRentRoll: false,
  compMix: false, 
  compRoll: false 
})

// Data stores
const subjectUnitMix = ref<Array<any>>([])
const subjectRentRoll = ref<Array<any>>([])
const leaseCompUnitMix = ref<Array<any>>([])
const leaseCompRentRoll = ref<Array<any>>([])

// Format helpers (kept simple; consider centralizing if used widely)
function formatCurrency(v: any) {
  const n = Number(v ?? 0)
  return isFinite(n) ? n.toLocaleString(undefined, { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }) : '-'
}
function formatInt(v: any) {
  const n = Number(v ?? 0)
  return isFinite(n) ? n.toLocaleString() : '-'
}
function formatDate(v: any) {
  if (!v) return '-'
  // Expecting YYYY-MM-DD from backend
  try { return new Date(v).toLocaleDateString() } catch { return String(v) }
}

// Fetch functions (endpoints assumed; adjust to your API naming)
async function fetchSubjectUnitMix(assetId: number) {
  loading.value.subjectUnitMix = true
  try {
    const res = await http.get(`/core/unit-mix/${assetId}/`)
    subjectUnitMix.value = Array.isArray(res.data) ? res.data : []
  } catch (e) {
    subjectUnitMix.value = []
  } finally {
    loading.value.subjectUnitMix = false
  }
}

async function fetchSubjectRentRoll(assetId: number) {
  loading.value.subjectRentRoll = true
  try {
    const res = await http.get(`/core/rent-roll/${assetId}/`)
    subjectRentRoll.value = Array.isArray(res.data) ? res.data : []
  } catch (e) {
    subjectRentRoll.value = []
  } finally {
    loading.value.subjectRentRoll = false
  }
}

async function fetchLeaseCompUnitMix(assetId: number) {
  loading.value.compMix = true
  try {
    // Example endpoint: /core/lease-comp-unit-mix/{assetId}/ (adjust to your actual routes)
    const res = await http.get(`/core/lease-comp-unit-mix/${assetId}/`)
    leaseCompUnitMix.value = Array.isArray(res.data) ? res.data : []
  } catch (e) {
    leaseCompUnitMix.value = []
  } finally {
    loading.value.compMix = false
  }
}

async function fetchLeaseCompRentRoll(assetId: number) {
  loading.value.compRoll = true
  try {
    // Example endpoint: /core/lease-comp-rent-roll/{assetId}/ (adjust to your actual routes)
    const res = await http.get(`/core/lease-comp-rent-roll/${assetId}/`)
    leaseCompRentRoll.value = Array.isArray(res.data) ? res.data : []
  } catch (e) {
    leaseCompRentRoll.value = []
  } finally {
    loading.value.compRoll = false
  }
}

function maybeNumber(v: string | number | null): number | null {
  const n = v != null ? Number(v) : NaN
  return Number.isFinite(n) ? n : null
}

async function loadAll() {
  const id = maybeNumber(props.assetId)
  if (id == null) return
  await Promise.all([
    fetchSubjectUnitMix(id),
    fetchSubjectRentRoll(id),
    fetchLeaseCompUnitMix(id),
    fetchLeaseCompRentRoll(id),
  ])
}

onMounted(loadAll)
watch(() => props.assetId, loadAll)
</script>

<style scoped>
/* Minimal; rely on Hyper UI / Bootstrap styles */
.card-title { font-weight: 600; }
</style>
