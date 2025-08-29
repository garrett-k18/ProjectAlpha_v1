<template>
  <!--
    Card: Judicial vs Non-Judicial States
    - Counts how many UNIQUE states in the current dataset are judicial vs non-judicial
    - Uses cached AG Grid rows from Pinia store so we don't refetch
    - Minimal UI with progress bars, consistent with Hyper/Bootstrap card styles
  -->
  <div class="card">
    <!-- Card header: title + optional action -->
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Judicial vs Non-Judicial</h4>
      <!-- Simple export stub (wire up later if needed) -->
      <a href="javascript:void(0);" class="btn btn-sm btn-light">Export <i class="mdi mdi-download ms-1"></i></a>
    </div>

    <!-- Card body: table with two rows -->
    <div class="card-body pt-0">
      <!-- Empty-state helper when no seller/trade or no rows loaded -->
      <div v-if="!hasRows" class="text-muted small py-3 d-flex align-items-center justify-content-center text-center">
        Select a seller and trade to see state counts.
      </div>

      <b-table-simple v-else responsive centered class="table-sm mb-0 font-14">
        <b-thead head-variant="light">
          <b-tr>
            <b-th>Category</b-th>
            <b-th class="text-end">States</b-th>
            <b-th style="width: 45%;"></b-th>
          </b-tr>
        </b-thead>
        <b-tbody>
          <!-- Judicial row -->
          <b-tr>
            <b-td>Judicial</b-td>
            <b-td class="text-end">{{ formatInt(judicialStatesCount) }}</b-td>
            <b-td>
              <div class="progress mt-2" style="height: 3px;">
                <div class="progress-bar bg-danger" role="progressbar"
                     :aria-valuenow="pctStatesJudicial"
                     aria-valuemin="0" aria-valuemax="100"
                     :style="{ width: pctStatesJudicial + '%' }"></div>
              </div>
            </b-td>
          </b-tr>
          <!-- Non-Judicial row -->
          <b-tr>
            <b-td>Non-Judicial</b-td>
            <b-td class="text-end">{{ formatInt(nonJudicialStatesCount) }}</b-td>
            <b-td>
              <div class="progress mt-2" style="height: 3px;">
                <div class="progress-bar bg-success" role="progressbar"
                     :aria-valuenow="pctStatesNonJudicial"
                     aria-valuemin="0" aria-valuemax="100"
                     :style="{ width: pctStatesNonJudicial + '%' }"></div>
              </div>
            </b-td>
          </b-tr>
        </b-tbody>
      </b-table-simple>
    </div>
  </div>
</template>

<script setup lang="ts">
// Documentation reviewed (per project standards):
// - Vue 3 <script setup>: https://vuejs.org/api/sfc-script-setup.html
// - Pinia stores: https://pinia.vuejs.org/core-concepts/
// - Array/Set helpers (MDN): https://developer.mozilla.org/

import { computed, onMounted, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useAcqSelectionsStore } from '@/stores/acqSelections'
import { useAgGridRowsStore } from '@/stores/agGridRows'

// Access global selections (seller and trade)
const sel = useAcqSelectionsStore() // Pinia store instance for selections
const { selectedSellerId, selectedTradeId } = storeToRefs(sel) // reactive refs

// Access cached grid rows (shared with the AG Grid card)
const gridStore = useAgGridRowsStore() // Pinia store for grid rows
const { rows } = storeToRefs(gridStore) // reactive rows array

// Whether we have any rows for the active seller/trade
const hasRows = computed<boolean>(() => Array.isArray(rows.value) && rows.value.length > 0)

// Ensure rows are loaded when both IDs are selected (idempotent thanks to store cache)
async function ensureRows() {
  // Guard: need both IDs to fetch
  if (!selectedSellerId.value || !selectedTradeId.value) return
  // Fetch using store (uses cache to avoid duplicate network calls)
  await gridStore.fetchRows(selectedSellerId.value as number, selectedTradeId.value as number)
}

onMounted(ensureRows)
watch([selectedSellerId, selectedTradeId], ensureRows)

// ---------------------------------------------------------------------------
// Judicial states configuration (TO BE PROVIDED by you)
// ---------------------------------------------------------------------------
// IMPORTANT: Please provide the authoritative list of judicial foreclosure
// states. For now this is an empty placeholder to avoid incorrect counts.
// Example expected values: ['FL', 'NY', 'NJ', ...] (2-letter USPS abbreviations)
const judicialStatesSource: string[] = [
  // TODO: Replace with your canonical list of judicial states
]

// Normalize the provided list into a Set for O(1) lookups, uppercase to match data
const judicialStateSet = computed<Set<string>>(() => {
  return new Set(judicialStatesSource.map(s => String(s).trim().toUpperCase()).filter(Boolean))
})

// Build a Set of unique states present in the current dataset
const uniqueStatesInData = computed<Set<string>>(() => {
  const s = new Set<string>() // accumulator for unique states
  for (const r of rows.value || []) {
    // Extract state from common field name 'state'; skip blanks
    const st = String((r as any)?.state ?? '').trim().toUpperCase()
    if (st) s.add(st)
  }
  return s
})

// Total unique states count represented in data
const totalStatesCount = computed<number>(() => uniqueStatesInData.value.size)

// Count how many of those unique states are judicial vs non-judicial
const judicialStatesCount = computed<number>(() => {
  if (uniqueStatesInData.value.size === 0) return 0
  let n = 0
  for (const st of uniqueStatesInData.value) if (judicialStateSet.value.has(st)) n++
  return n
})

const nonJudicialStatesCount = computed<number>(() => {
  const total = totalStatesCount.value
  const j = judicialStatesCount.value
  return total >= j ? total - j : 0
})

// Percent helpers for progress bars (0-100)
const pctStatesJudicial = computed<number>(() => {
  const total = totalStatesCount.value || 1 // avoid divide-by-zero
  return Math.round((judicialStatesCount.value / total) * 100)
})

const pctStatesNonJudicial = computed<number>(() => 100 - pctStatesJudicial.value)

// Integer formatter (no decimals)
function formatInt(n: number): string {
  return new Intl.NumberFormat(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(n)
}
</script>

<style scoped>
/* Keep visuals subtle and aligned with other cards */
.font-14 { font-size: 14px; }
</style>
