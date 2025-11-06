<template>
  <!--
    Card: Judicial vs Non-Judicial States
    - Uses backend judicial stratification API for consistent metrics
    - Displays counts and financial metrics (UPB, Total Debt, Seller As-Is)
    - Minimal UI with progress bars, consistent with Hyper/Bootstrap card styles
  -->
  <div class="card h-100">
    <!-- Card header: title + optional action -->
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Judicial vs Non-Judicial</h4>
    </div>

    <!-- Card body: table with two rows -->
    <div :class='["card-body", "pt-0", "pb-3", hasData ? "strat-card-body" : ""]'>
      <!-- Loading state -->
      <div v-if="isLoading" class="text-muted small py-3 d-flex align-items-center justify-content-center text-center">
        <i class="mdi mdi-loading mdi-spin me-1"></i> Loading...
      </div>
      
      <!-- Empty-state helper when no seller/trade or no rows loaded -->
      <div v-else-if="!hasData" class="text-muted small py-3 d-flex align-items-center justify-content-center text-center">
        Select a seller and trade to see state counts.
      </div>

      <div v-else class="mt-2">
        <div class="table-responsive">
          <table class="table table-borderless table-striped align-middle mb-0 bands-table">
            <thead class="text-uppercase text-muted small">
              <tr>
                <th style="width: 40%;">Band</th>
                <th class="text-center" style="width: 15%;">Count</th>
                <th class="text-center" style="width: 15%;">Current Balance</th>
                <th class="text-center" style="width: 15%;">Total Debt</th>
                <th class="text-center" style="width: 15%;">As-Is Value</th>
              </tr>
            </thead>
            <tbody>
              <!-- Judicial row -->
              <tr>
                <td class="py-2">Judicial</td>
                <td class="py-2 text-center fw-semibold">{{ formatInt(judicialData.count) }}</td>
                <td class="py-2 text-center">{{ formatCurrency(judicialData.sum_current_balance) }}</td>
                <td class="py-2 text-center">{{ formatCurrency(judicialData.sum_total_debt) }}</td>
                <td class="py-2 text-center">{{ formatCurrency(judicialData.sum_seller_asis_value) }}</td>
              </tr>
              <!-- Non-Judicial row -->
              <tr>
                <td class="py-2">Non-Judicial</td>
                <td class="py-2 text-center fw-semibold">{{ formatInt(nonJudicialData.count) }}</td>
                <td class="py-2 text-center">{{ formatCurrency(nonJudicialData.sum_current_balance) }}</td>
                <td class="py-2 text-center">{{ formatCurrency(nonJudicialData.sum_total_debt) }}</td>
                <td class="py-2 text-center">{{ formatCurrency(nonJudicialData.sum_seller_asis_value) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      
    </div>
  </div>
</template>

<script setup lang="ts">
// Documentation reviewed (per project standards):
// - Vue 3 <script setup>: https://vuejs.org/api/sfc-script-setup.html
// - Pinia stores: https://pinia.vuejs.org/core-concepts/
// - Array/Set helpers (MDN): https://developer.mozilla.org/
// - Axios: https://axios-http.com/docs/api_intro

import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useAcqSelectionsStore } from '@/stores/acqSelections'
import axios from '@/lib/http'

// Type definitions for the judicial stratification API response
interface JudicialDataItem {
  key: string;
  index: number;
  label: string;
  count: number;
  sum_current_balance: number;
  sum_total_debt: number;
  sum_seller_asis_value: number;
}

interface JudicialStratificationResponse {
  bands: JudicialDataItem[];
}

// Access global selections (seller and trade)
const sel = useAcqSelectionsStore() // Pinia store instance for selections
const { selectedSellerId, selectedTradeId } = storeToRefs(sel) // reactive refs

// Define reactive state for judicial data
const isLoading = ref(false)
const hasData = ref(false)
const error = ref('')

// Abort controller to cancel in-flight API when selection changes quickly
const abortCtrl = ref<AbortController | null>(null)

// Data containers for judicial/non-judicial stats
const judicialData = ref<JudicialDataItem>({
  key: 'judicial',
  index: 1,
  label: 'Judicial',
  count: 0,
  sum_current_balance: 0,
  sum_total_debt: 0,
  sum_seller_asis_value: 0
})

const nonJudicialData = ref<JudicialDataItem>({
  key: 'non_judicial',
  index: 2,
  label: 'Non-Judicial',
  count: 0,
  sum_current_balance: 0,
  sum_total_debt: 0,
  sum_seller_asis_value: 0
})

// Function to fetch data from the judicial stratification API
async function fetchJudicialStratification() {
  // Guard: need both IDs to fetch
  if (!selectedSellerId.value || !selectedTradeId.value) {
    hasData.value = false
    return
  }
  // Cancel any in-flight request before starting a new one
  try { abortCtrl.value?.abort() } catch {}
  abortCtrl.value = new AbortController()

  isLoading.value = true
  error.value = ''
  
  try {
    // Call the backend API endpoint
    const response = await axios.get<JudicialStratificationResponse>(
      `/acq/summary/strat/judicial/${selectedSellerId.value}/${selectedTradeId.value}/`,
      { signal: abortCtrl.value.signal }
    )
    
    // Extract data from response
    const bands = response.data.bands || []
    
    // Process the data - find judicial and non-judicial items
    if (bands.length > 0) {
      // Find and assign judicial data
      const judicial = bands.find(band => band.key === 'judicial')
      if (judicial) {
        judicialData.value = judicial
      }
      
      // Find and assign non-judicial data
      const nonJudicial = bands.find(band => band.key === 'non_judicial')
      if (nonJudicial) {
        nonJudicialData.value = nonJudicial
      }
      
      hasData.value = true
    } else {
      hasData.value = false
    }
  } catch (err: any) {
    // Ignore abort errors; these are expected during rapid changes
    if (err?.name === 'CanceledError' || err?.name === 'AbortError') {
      return
    }
    console.error('Error fetching judicial stratification:', err)
    error.value = err?.message || 'Failed to load judicial stratification'
    hasData.value = false
  } finally {
    isLoading.value = false
    abortCtrl.value = null
  }
}

// Fetch data on mount and when selections change
onMounted(() => {
  if (selectedSellerId.value && selectedTradeId.value) {
    fetchJudicialStratification()
  }
})

watch([selectedSellerId, selectedTradeId], () => {
  fetchJudicialStratification()
})

// Clean up on unmount
onUnmounted(() => {
  try { abortCtrl.value?.abort() } catch {}
  abortCtrl.value = null
})

// Total loans count
const totalCount = computed<number>(() => judicialData.value.count + nonJudicialData.value.count || 0)

// Percent helpers for progress bars (0-100)
const pctStatesJudicial = computed<number>(() => {
  const total = totalCount.value || 1 // avoid divide-by-zero
  return Math.round((judicialData.value.count / total) * 100)
})

const pctStatesNonJudicial = computed<number>(() => 100 - pctStatesJudicial.value)

// Number formatters
function formatInt(n: number): string {
  return new Intl.NumberFormat('en-US', { 
    minimumFractionDigits: 0, 
    maximumFractionDigits: 0 
  }).format(n)
}

function formatCurrency(n: number): string {
  // Format currency with full numbers and commas without $ sign
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(n)
}
</script>

<style scoped>
/* Keep visuals subtle and aligned with other cards */
.font-14 { font-size: 14px; }

/* Ensure consistent vertical size across strat cards by reserving space.
   Uses minimal custom CSS per project rules; prefers utilities otherwise. */
.strat-card-body {
  min-height: 280px; /* adjust if needed to align with tallest card */
  display: flex;
  flex-direction: column;
}
</style>
