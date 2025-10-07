<template>
  <!-- Commercial Analysis Tab
       - Subject summary: Unit Mix (if any)
       - Lease Comp Unit Mix (common)
       - Lease Comp Rent Roll (rare)
       Uses Hyper UI utilities + Bootstrap classes for clean layout.
  -->
  <div class="row g-3">
    <!-- Subject Unit Mix and Rent Roll side by side -->
    <div class="col-md-6">
      <UnitMixTable 
        :unit-mix-data="subjectUnitMix"
        :loading="loading.subjectUnitMix"
        title="Subject Unit Mix"
        :show-rent-per-sqft="true"
        :show-totals="true"
      />
    </div>
    <div class="col-md-6">
      <div class="card h-100 rent-roll-card">
        <div class="card-header d-flex align-items-center justify-content-between">
          <h5 class="card-title mb-0">Subject Rent Roll</h5>
        </div>
        <div class="card-body p-0">
          <div class="rent-roll-content">
            <RentRollTable
              :rent-roll-data="subjectRentRoll"
              :loading="loading.subjectRentRoll"
              title=""
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Historical Property Cash Flow - full width below -->
    <div class="col-12">
      <div class="card">
        <div class="card-header d-flex align-items-center justify-content-between">
          <h5 class="card-title mb-0">Historical Property Cash Flow</h5>
        </div>
        <div class="card-body p-0">
          <div class="cashflow-content">
            <HistoricalCashFlowTable
              :cash-flow-data="historicalCashFlow"
              :loading="loading.historicalCashFlow"
              title=""
            />
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
import HistoricalCashFlowTable from '@/views/acq_module/loanlvl/components/commercial/HistoricalCashFlowTable.vue'

const props = defineProps<{
  row: Record<string, any> | null
  assetId: string | number | null
  module?: 'acq' | 'am'
}>()

// Loading flags
const loading = ref({ 
  subjectUnitMix: false, 
  subjectRentRoll: false,
  historicalCashFlow: false
})

// Data stores
const subjectUnitMix = ref<Array<any>>([])
const subjectRentRoll = ref<Array<any>>([])
const historicalCashFlow = ref<Array<any>>([])

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

async function fetchHistoricalCashFlow(assetId: number) {
  loading.value.historicalCashFlow = true
  try {
    const res = await http.get(`/core/historical-cashflow/${assetId}/`)
    historicalCashFlow.value = Array.isArray(res.data) ? res.data : []
  } catch (e) {
    historicalCashFlow.value = []
  } finally {
    loading.value.historicalCashFlow = false
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
    fetchHistoricalCashFlow(id),
  ])
}

onMounted(loadAll)
watch(() => props.assetId, loadAll)
</script>

<style scoped>
/* Minimal; rely on Hyper UI / Bootstrap styles */
.card-title { font-weight: 600; }

/* Rent Roll Card - Taller with scroll */
.rent-roll-card {
  min-height: 600px;
  max-height: 800px;
  display: flex;
  flex-direction: column;
}

.rent-roll-card .card-body {
  flex: 1;
  overflow: hidden;
}

.rent-roll-content {
  height: 100%;
  max-height: calc(100vh - 300px);
  overflow-y: auto;
  padding: 1.25rem;
}

/* Cash Flow Content - Horizontal scroll for wide table */
.cashflow-content {
  overflow-x: auto;
  padding: 1.25rem;
}
</style>
