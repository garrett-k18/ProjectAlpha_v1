<template>
  <!-- Full card variant (default) -->
  <div v-if="!embedded" class="card h-100">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">States</h4>
    </div>

    <div class="card-body pt-0" :class="emptyBodyClasses">
      <!-- Error state -->
      <div v-if="error" class="alert alert-danger d-flex align-items-center my-3" role="alert">
        <i class="mdi mdi-alert-circle-outline me-2"></i>
        <div>
          {{ error }}
        </div>
      </div>

      <!-- Loading state (reserve space) -->
      <div v-else-if="loading" class="d-flex align-items-center text-muted small py-3">
        <div class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></div>
        Loading state stratification…
      </div>

      <!-- Empty state when no data -->
      <div v-else-if="rows.length === 0" class="empty-center text-muted small text-center">
        Select a seller and trade to see state counts.
      </div>

      <!-- Compact top-4 + Other table (no in-card scroll) -->
      <div v-else class="mt-2">
        <table class="table table-borderless table-striped align-middle mb-0 bands-table">
          <thead class="text-uppercase text-muted small">
            <tr>
              <th style="width: 25%">State</th>
              <th class="text-center" style="width: 15%">Count</th>
              <th class="text-center" style="width: 20%">Current Balance</th>
              <th class="text-center" style="width: 20%">Total Debt</th>
              <th class="text-center" style="width: 20%">As-Is Value</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in visibleRows" :key="r.state">
              <td class="py-2">{{ r.state }}</td>
              <td class="py-2 text-center fw-semibold">{{ formatInt(r.count) }}</td>
              <td class="py-2 text-center">{{ formatCurrencyNoDecimals(r.currentBalance) }}</td>
              <td class="py-2 text-center">{{ formatCurrencyNoDecimals(r.totalDebt) }}</td>
              <td class="py-2 text-center">{{ formatCurrencyNoDecimals(r.sellerAsIs) }}</td>
            </tr>
          </tbody>
        </table>
        <div class="d-flex justify-content-end mt-2">
          <button
            class="btn btn-sm btn-light"
            type="button"
            :disabled="rows.length === 0"
            @click="openAll()"
          >
            All States
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Embedded variant (no header/card wrapper) for use inside other cards -->
  <div v-else class="h-100">
    <!-- Error state -->
    <div v-if="error" class="alert alert-danger d-flex align-items-center my-2" role="alert">
      <i class="mdi mdi-alert-circle-outline me-2"></i>
      <div>
        {{ error }}
      </div>
    </div>

    <!-- Loading state -->
    <div v-else-if="loading" class="d-flex align-items-center text-muted small py-2">
      <div class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></div>
      Loading state stratification…
    </div>

    <!-- Empty -->
    <div v-else-if="rows.length === 0" class="empty-center text-muted small text-center">
      Select a seller and trade to see stratification.
    </div>

    <!-- Embedded: compact top-4 + Other with bottom-right button -->
    <div v-else>
      <table class="table table-borderless table-striped align-middle mb-0 bands-table">
        <thead class="text-uppercase text-muted small">
          <tr>
            <th style="width: 25%">State</th>
            <th class="text-center" style="width: 15%">Count</th>
            <th class="text-center" style="width: 20%">Current Balance</th>
            <th class="text-center" style="width: 20%">Total Debt</th>
            <th class="text-center" style="width: 20%">As-Is Value</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in visibleRows" :key="'embed-' + r.state">
            <td class="py-2">{{ r.state }}</td>
            <td class="py-2 text-center fw-semibold">{{ formatInt(r.count) }}</td>
            <td class="py-2 text-center">{{ formatCurrencyNoDecimals(r.currentBalance) }}</td>
            <td class="py-2 text-center">{{ formatCurrencyNoDecimals(r.totalDebt) }}</td>
            <td class="py-2 text-center">{{ formatCurrencyNoDecimals(r.sellerAsIs) }}</td>
          </tr>
        </tbody>
      </table>
      <div class="d-flex justify-content-end mt-2">
        <button
          class="btn btn-xs btn-light btn-sm"
          type="button"
          :disabled="rows.length === 0"
          @click="openAll()"
        >
          All States
        </button>
      </div>
    </div>
  </div>

  <!-- Centered modal with full state breakdown (plain Bootstrap) -->
  <div class="modal fade" :id="modalId" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">All States</h5>
          <button type="button" class="btn-close" aria-label="Close" @click="closeAll()"></button>
        </div>
        <div class="modal-body">
          <table class="table table-borderless table-striped align-middle mb-0 bands-table">
            <thead class="text-uppercase text-muted small">
              <tr>
                <th style="width: 25%">State</th>
                <th class="text-center" style="width: 15%">Count</th>
                <th class="text-center" style="width: 20%">Current Balance</th>
                <th class="text-center" style="width: 20%">Total Debt</th>
                <th class="text-center" style="width: 20%">As-Is Value</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="r in rows" :key="'modal-' + r.state">
                <td class="py-2">{{ r.state }}</td>
                <td class="py-2 text-center fw-semibold">{{ formatInt(r.count) }}</td>
                <td class="py-2 text-center">{{ formatCurrencyNoDecimals(r.currentBalance) }}</td>
                <td class="py-2 text-center">{{ formatCurrencyNoDecimals(r.totalDebt) }}</td>
                <td class="py-2 text-center">{{ formatCurrencyNoDecimals(r.sellerAsIs) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// strats-states.vue
// Purpose: A state-level stratification table listing ALL states, sorted by occurrence (count desc),
// with sums for Current Balance, Total Debt, and Seller As-Is value.
// Documentation reviewed per project standards:
// - Vue 3 <script setup>: https://vuejs.org/api/sfc-script-setup.html
// - Pinia: https://pinia.vuejs.org/core-concepts/
// - Intl.NumberFormat: MDN docs for number formatting

import { computed, onMounted, watch, onUnmounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useAcqSelectionsStore } from '@/stores/acqSelections'
import { useStateSummariesStore } from '@/stores/stateSummaries'

// Selections (seller and trade)
const sel = useAcqSelectionsStore()
const { selectedSellerId, selectedTradeId, hasBothSelections } = storeToRefs(sel)

// State summaries store
const summaries = useStateSummariesStore()
const loading = summaries.loading
const error = summaries.error

// Allow embedding inside another card (no header/wrapper)
const props = defineProps<{ embedded?: boolean }>()
const embedded = computed<boolean>(() => !!(props.embedded))

// Fetch on mount and whenever selection changes
async function ensureSummaries() {
  if (!hasBothSelections.value) return
  const sid = selectedSellerId.value as number
  const tid = selectedTradeId.value as number
  if (!sid || !tid) return
  const label = `[StratsStates] summaries ${sid}:${tid}`
  console.time(label)
  try {
    console.debug('[StratsStates] ensureSummaries -> fetchAll', { sid, tid })
    await summaries.fetchAll(sid, tid)
  } finally {
    console.timeEnd(label)
  }
}

onMounted(() => {
  console.debug('[StratsStates] onMounted')
  ensureSummaries()
})
let debounceTimer: ReturnType<typeof setTimeout> | null = null
watch([selectedSellerId, selectedTradeId], () => {
  console.count('[StratsStates] selection change')
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    ensureSummaries()
  }, 200)
})

// Define row type for better type safety
interface StateRow {
  state: string;
  count: number;
  currentBalance: number;
  totalDebt: number;
  sellerAsIs: number;
}

// Build table rows from countsByState + sumsFor()
const rows = computed<StateRow[]>(() => {
  if (!hasBothSelections.value) return [];
  const src = Array.isArray(summaries.countsByState) ? summaries.countsByState : [];
  const counts = Array.isArray(src) ? src : [];
  const sorted = [...counts].sort((a, b) => (b?.count || 0) - (a?.count || 0));
  return sorted.map((r) => {
    const st = (r?.state || '').toString().trim().toUpperCase();
    const s = summaries.sumsFor(st);
    return {
      state: st,
      count: Number(r?.count) || 0,
      currentBalance: Number(s.currentBalance) || 0,
      totalDebt: Number(s.totalDebt) || 0,
      sellerAsIs: Number(s.sellerAsIs) || 0,
    };
  });
});

// Top 4 + Other aggregator for compact view
const visibleRows = computed<StateRow[]>(() => {
  const all = rows.value
  if (all.length <= 5) return all
  const top = all.slice(0, 4)
  const rest = all.slice(4)
  const other: StateRow = {
    state: 'Other',
    count: rest.reduce((acc, x) => acc + (x.count || 0), 0),
    currentBalance: rest.reduce((acc, x) => acc + (x.currentBalance || 0), 0),
    totalDebt: rest.reduce((acc, x) => acc + (x.totalDebt || 0), 0),
    sellerAsIs: rest.reduce((acc, x) => acc + (x.sellerAsIs || 0), 0),
  }
  return [...top, other]
})

// Unique modal id per selection to avoid clashing with other instances
const modalId = computed<string>(() => {
  const sid = selectedSellerId.value ?? 'x'
  const tid = selectedTradeId.value ?? 'x'
  return `statesModal-${sid}-${tid}`
})

// Open modal via Bootstrap JS API, fallback to data-bs attributes if unavailable
function openAll(): void {
  try {
    const id = modalId.value
    const el = document.getElementById(id)
    if (!el) return
    // @ts-ignore - bootstrap may be globally available
    const Bootstrap = (window as any).bootstrap
    if (Bootstrap && Bootstrap.Modal) {
      const modal = Bootstrap.Modal.getOrCreateInstance(el)
      modal.show()
    } else {
      // Fallback: toggle classes as a last resort
      el.classList.add('show')
      el.style.display = 'block'
      el.removeAttribute('aria-hidden')
      el.setAttribute('aria-modal', 'true')
    }
    // Bind ESC to close while open
    document.addEventListener('keydown', onEsc)
  } catch (e) {
    // no-op
  }
}

function closeAll(): void {
  try {
    const id = modalId.value
    const el = document.getElementById(id)
    if (!el) return
    // @ts-ignore
    const Bootstrap = (window as any).bootstrap
    if (Bootstrap && Bootstrap.Modal) {
      const modal = Bootstrap.Modal.getOrCreateInstance(el)
      modal.hide()
    } else {
      el.classList.remove('show')
      el.style.display = 'none'
      el.setAttribute('aria-hidden', 'true')
      el.removeAttribute('aria-modal')
    }
  } catch (_) { /* no-op */ }
  finally {
    document.removeEventListener('keydown', onEsc)
  }
}

function onEsc(e: KeyboardEvent): void {
  if (e.key === 'Escape') {
    closeAll()
  }
}

onUnmounted(() => {
  document.removeEventListener('keydown', onEsc)
})

// When there is no data and no error/loading, center the helper inside the full card body
const isEmpty = computed<boolean>(() => !embedded.value && !summaries.loading && !summaries.error && (rows.value.length === 0));
const emptyBodyClasses = computed<string>(() => (isEmpty.value ? 'd-flex align-items-center justify-content-center' : ''));

// Display helpers
function formatInt(n: number): string {
  return new Intl.NumberFormat(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(n)
}

function formatCurrencyNoDecimals(n: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'decimal',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(n)
}
</script>

<style scoped>
/* Keep parity with other strat tables */
.bands-table.table-striped {
  --bs-table-striped-bg: rgba(13, 110, 253, 0.06); /* light primary */
  --bs-table-striped-color: inherit;
}

/* Center helper text nicely in the card area */
.empty-center {
  display: flex;
  align-items: center;
  justify-content: center;
  padding-top: 0.75rem; /* ~py-3 visual parity */
  padding-bottom: 0.75rem;
  min-height: 360px; /* slightly taller to align with other cards' visual middle */
  width: 100%;
}
</style>
