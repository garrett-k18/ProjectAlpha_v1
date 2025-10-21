<template>
  <!--
    StateAssumptionsTable.vue
    - Displays and allows editing of state-level assumptions
    - Includes judicial status, foreclosure timelines, property tax rates, etc.
    
    Location: frontend_vue/src/1_global/components/assumptions/StateAssumptionsTable.vue
  -->
  <div class="state-assumptions-container">
    <!-- Table Header with Search -->
    <div class="d-flex justify-content-between align-items-center mb-3">
      <div>
        <h5 class="mb-1">State Assumptions</h5>
        <p class="text-muted small mb-0">Configure state-specific modeling assumptions</p>
      </div>
      <div class="d-flex gap-2">
        <input 
          type="text" 
          class="form-control form-control-sm" 
          placeholder="Search states..."
          v-model="searchQuery"
          style="width: 200px;"
        />
        <button 
          class="btn btn-sm btn-primary"
          @click="saveChanges"
          :disabled="!hasChanges || isSaving"
        >
          <i class="mdi mdi-content-save me-1"></i>
          {{ isSaving ? 'Saving...' : 'Save' }}
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="text-muted mt-2">Loading state assumptions...</p>
    </div>

    <!-- Data Table -->
    <div v-else class="table-responsive">
      <table class="table table-sm table-hover table-bordered">
        <thead class="table-light">
          <tr>
            <th style="width: 70px;">State</th>
            <th style="width: 130px;">State Name</th>
            <th style="width: 90px;">Judicial</th>
            <th style="width: 110px;">Foreclosure (mo)</th>
            <th style="width: 110px;">Eviction (mo)</th>
            <th style="width: 110px;">Rehab (mo)</th>
            <th style="width: 110px;">REO Mkt (mo)</th>
            <th style="width: 110px;">REO Ext (mo)</th>
            <th style="width: 110px;">DIL (mo)</th>
            <th style="width: 130px;">Property Tax (%)</th>
            <th style="width: 130px;">Transfer Tax (%)</th>
            <th style="width: 130px;">Insurance (%)</th>
            <th style="width: 110px;">FC Legal $</th>
            <th style="width: 110px;">DIL Cost $</th>
            <th style="width: 110px;">CFK Cost $</th>
            <th style="width: 130px;">Val Adj (%)</th>
            <th>Notes</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="state in filteredStates" :key="state.code">
            <!-- State Code (read-only) -->
            <td class="fw-bold">{{ state.code }}</td>
            
            <!-- State Name (read-only) -->
            <td class="fw-bold">{{ state.name }}</td>
            
            <!-- Judicial Status (read-only) -->
            <td class="text-center">
              <UiBadge
                :tone="state.isJudicial ? 'warning' : 'success'"
                size="md"
                :label="state.isJudicial ? 'Yes' : 'No'"
              />
            </td>
            
            <!-- FC State Months -->
            <td>
              <input 
                type="number"
                class="form-control form-control-sm"
                v-model.number="state.fcStateMonths"
                @input="markAsChanged"
                min="0"
                step="1"
              />
            </td>
            
            <!-- Eviction Duration -->
            <td>
              <input 
                type="number"
                class="form-control form-control-sm"
                v-model.number="state.evictionDuration"
                @input="markAsChanged"
                min="0"
                step="1"
              />
            </td>
            
            <!-- Rehab Duration -->
            <td>
              <input 
                type="number"
                class="form-control form-control-sm"
                v-model.number="state.rehabDuration"
                @input="markAsChanged"
                min="0"
                step="1"
              />
            </td>
            
            <!-- REO Marketing Duration -->
            <td>
              <input 
                type="number"
                class="form-control form-control-sm"
                v-model.number="state.reoMarketingDuration"
                @input="markAsChanged"
                min="0"
                step="1"
              />
            </td>
            
            <!-- REO Local Market Ext Duration -->
            <td>
              <input 
                type="number"
                class="form-control form-control-sm"
                v-model.number="state.reoLocalMarketExtDuration"
                @input="markAsChanged"
                min="0"
                step="1"
              />
            </td>
            
            <!-- DIL Duration Avg -->
            <td>
              <input 
                type="number"
                class="form-control form-control-sm"
                v-model.number="state.dilDurationAvg"
                @input="markAsChanged"
                min="0"
                step="1"
              />
            </td>
            
            <!-- Property Tax Rate -->
            <td>
              <div class="input-group input-group-sm">
                <input
                  type="number"
                  class="form-control form-control-sm"
                  :value="formatPercentage(state.propertyTaxRate)"
                  @input="state.propertyTaxRate = parsePercentage(($event.target as HTMLInputElement).value); markAsChanged()"
                  min="0"
                  max="10"
                  step="0.01"
                  placeholder="1.20"
                />
                <span class="input-group-text">%</span>
              </div>
            </td>

            <!-- Transfer Tax Rate -->
            <td>
              <div class="input-group input-group-sm">
                <input
                  type="number"
                  class="form-control form-control-sm"
                  :value="formatPercentage(state.transferTaxRate)"
                  @input="state.transferTaxRate = parsePercentage(($event.target as HTMLInputElement).value); markAsChanged()"
                  min="0"
                  max="10"
                  step="0.01"
                  placeholder="0.50"
                />
                <span class="input-group-text">%</span>
              </div>
            </td>

            <!-- Insurance Rate Avg -->
            <td>
              <div class="input-group input-group-sm">
                <input
                  type="number"
                  class="form-control form-control-sm"
                  :value="formatPercentage(state.insuranceRateAvg)"
                  @input="state.insuranceRateAvg = parsePercentage(($event.target as HTMLInputElement).value); markAsChanged()"
                  min="0"
                  max="10"
                  step="0.01"
                  placeholder="0.50"
                />
                <span class="input-group-text">%</span>
              </div>
            </td>
            
            <!-- FC Legal Fees Avg -->
            <td>
              <input 
                type="text"
                class="form-control form-control-sm"
                :value="formatCurrency(state.fcLegalFeesAvg)"
                @input="state.fcLegalFeesAvg = parseFloat(($event.target as HTMLInputElement).value.replace(/,/g, '')); markAsChanged()"
                placeholder="500"
              />
            </td>

            <!-- DIL Cost Avg -->
            <td>
              <input 
                type="text"
                class="form-control form-control-sm"
                :value="formatCurrency(state.dilCostAvg)"
                @input="state.dilCostAvg = parseFloat(($event.target as HTMLInputElement).value.replace(/,/g, '')); markAsChanged()"
                placeholder="300"
              />
            </td>

            <!-- CFK Cost Avg -->
            <td>
              <input 
                type="text"
                class="form-control form-control-sm"
                :value="formatCurrency(state.cfkCostAvg)"
                @input="state.cfkCostAvg = parseFloat(($event.target as HTMLInputElement).value.replace(/,/g, '')); markAsChanged()"
                placeholder="200"
              />
            </td>
            
            <!-- Value Adjustment Annual -->
            <td>
              <div class="input-group input-group-sm">
                <input
                  type="number"
                  class="form-control form-control-sm"
                  :value="formatPercentage(state.valueAdjustmentAnnual)"
                  @input="state.valueAdjustmentAnnual = parsePercentage(($event.target as HTMLInputElement).value); markAsChanged()"
                  min="-100"
                  max="100"
                  step="0.01"
                  placeholder="2.00"
                />
                <span class="input-group-text">%</span>
              </div>
            </td>
            
            <!-- Notes -->
            <td>
              <input 
                type="text"
                class="form-control form-control-sm"
                v-model="state.notes"
                @input="markAsChanged"
                placeholder="Optional notes..."
              />
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Empty State -->
    <div v-if="!isLoading && filteredStates.length === 0" class="text-center py-5">
      <i class="mdi mdi-magnify mdi-48px text-muted"></i>
      <p class="text-muted mt-2">No states match your search</p>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * StateAssumptionsTable.vue
 * 
 * What this does:
 * - Displays editable table of state-level assumptions
 * - Allows inline editing of judicial status, timelines, rates
 * - Emits 'changed' event when data is modified
 * 
 * How it works:
 * - Loads state data from backend API on mount
 * - Tracks changes locally before save
 * - Filters states based on search query
 * 
 * Backend API:
 * - GET /api/core/state-assumptions/ - Load all state assumptions
 * - PUT /api/core/state-assumptions/ - Save modified assumptions
 * 
 * Components used:
 * - UiBadge: Centralized badge component from @/components/ui/UiBadge.vue
 */
import { ref, computed, onMounted } from 'vue'
import UiBadge from '@/components/ui/UiBadge.vue'

// Component emits
const emit = defineEmits<{
  (e: 'changed'): void
}>()

// State interface matching backend StateReference model
interface StateAssumption {
  code: string
  name: string
  isJudicial: boolean
  fcStateMonths: number
  evictionDuration: number
  rehabDuration: number
  reoMarketingDuration: number
  reoLocalMarketExtDuration: number
  dilDurationAvg: number
  propertyTaxRate: number
  transferTaxRate: number
  insuranceRateAvg: number
  fcLegalFeesAvg: number
  dilCostAvg: number
  cfkCostAvg: number
  valueAdjustmentAnnual: number
  notes: string
}

// Component state
const isLoading = ref(true)
const isSaving = ref(false)
const hasChanges = ref(false)
const searchQuery = ref('')
const stateData = ref<StateAssumption[]>([])

/**
 * Convert decimal to percentage for display
 * Backend stores: 0.0063 (0.63% as decimal with 4 places)
 * Frontend displays: 0.63 (percentage value)
 * Example: 0.0063 -> "0.63"
 */
function formatPercentage(value: number | undefined | null): string {
  if (value === undefined || value === null || isNaN(value)) return '0.00'
  const percentage = value * 100
  return percentage.toFixed(2)
}

/**
 * Convert percentage input back to decimal for saving
 * User types: 0.63
 * Backend saves: 0.0063 (divided by 100)
 * Example: "0.63" -> 0.0063
 */
function parsePercentage(value: string): number {
  const num = parseFloat(value)
  return isNaN(num) ? 0 : num / 100
}

/**
 * Format currency values with commas and no decimals
 * Example: 2155 -> "2,155"
 */
function formatCurrency(value: number | undefined | null): string {
  if (value === undefined || value === null || isNaN(value)) return '0'
  return Math.round(value).toLocaleString('en-US')
}

// Computed: Filtered states based on search
const filteredStates = computed(() => {
  if (!searchQuery.value) return stateData.value
  
  const query = searchQuery.value.toLowerCase()
  return stateData.value.filter(state => 
    state.code.toLowerCase().includes(query)
  )
})

/**
 * Load state assumptions from backend API
 * 
 * API Endpoint: GET /api/core/state-assumptions/
 * Returns: Array of StateReference objects with all fields
 */
async function loadStateAssumptions() {
  isLoading.value = true
  try {
    const response = await fetch('/api/core/state-assumptions/', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        // Add auth token if using JWT/session auth
        // 'Authorization': `Bearer ${getAuthToken()}`
      },
      credentials: 'include'  // Include cookies for session auth
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    const normalizedStates = Array.isArray(data)
      ? data
      : Array.isArray(data?.results)
        ? data.results
        : []

    stateData.value = normalizedStates
    
    console.log(`Loaded ${normalizedStates.length} states from backend`)
    console.log('Sample state data:', normalizedStates[0])
  } catch (error) {
    console.error('Error loading state assumptions:', error)
    // Fallback to mock data if API fails (for development)
    console.warn('Falling back to mock data')
    stateData.value = generateMockStateData()
  } finally {
    isLoading.value = false
  }
}

/**
 * Mark that changes have been made
 */
function markAsChanged() {
  hasChanges.value = true
  emit('changed')
}

/**
 * Save changes to backend using bulk update API
 * 
 * API Endpoint: POST /api/core/state-assumptions/bulk_update/
 * Sends: Array of modified StateReference objects
 * Returns: Confirmation with updated records
 */
async function saveChanges() {
  isSaving.value = true
  try {
    const response = await fetch('/api/core/state-assumptions/bulk_update/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // Add CSRF token for Django
        'X-CSRFToken': getCsrfToken(),
        // Add auth token if using JWT
        // 'Authorization': `Bearer ${getAuthToken()}`
      },
      credentials: 'include',  // Include cookies for session auth
      body: JSON.stringify(stateData.value)
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`)
    }

    const result = await response.json()
    hasChanges.value = false
    console.log('State assumptions saved successfully:', result.message)
    
    // Optionally show success notification to user
    // showNotification('Success', result.message, 'success')
  } catch (error) {
    console.error('Error saving state assumptions:', error)
    // Optionally show error notification to user
    // showNotification('Error', 'Failed to save changes', 'error')
    const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred'
    alert(`Failed to save changes: ${errorMessage}`)
  } finally {
    isSaving.value = false
  }
}

/**
 * Generate mock state data (temporary until backend is ready)
 */
function generateMockStateData(): StateAssumption[] {
  // All 50 US states + DC + territories (56 total)
  const statesData = [
    { code: 'AL', name: 'Alabama', judicial: false },
    { code: 'AK', name: 'Alaska', judicial: false },
    { code: 'AZ', name: 'Arizona', judicial: false },
    { code: 'AR', name: 'Arkansas', judicial: true },
    { code: 'CA', name: 'California', judicial: false },
    { code: 'CO', name: 'Colorado', judicial: false },
    { code: 'CT', name: 'Connecticut', judicial: true },
    { code: 'DE', name: 'Delaware', judicial: true },
    { code: 'FL', name: 'Florida', judicial: true },
    { code: 'GA', name: 'Georgia', judicial: false },
    { code: 'HI', name: 'Hawaii', judicial: false },
    { code: 'ID', name: 'Idaho', judicial: false },
    { code: 'IL', name: 'Illinois', judicial: true },
    { code: 'IN', name: 'Indiana', judicial: true },
    { code: 'IA', name: 'Iowa', judicial: true },
    { code: 'KS', name: 'Kansas', judicial: true },
    { code: 'KY', name: 'Kentucky', judicial: true },
    { code: 'LA', name: 'Louisiana', judicial: true },
    { code: 'ME', name: 'Maine', judicial: true },
    { code: 'MD', name: 'Maryland', judicial: true },
    { code: 'MA', name: 'Massachusetts', judicial: true },
    { code: 'MI', name: 'Michigan', judicial: false },
    { code: 'MN', name: 'Minnesota', judicial: true },
    { code: 'MS', name: 'Mississippi', judicial: true },
    { code: 'MO', name: 'Missouri', judicial: true },
    { code: 'MT', name: 'Montana', judicial: false },
    { code: 'NE', name: 'Nebraska', judicial: true },
    { code: 'NV', name: 'Nevada', judicial: false },
    { code: 'NH', name: 'New Hampshire', judicial: true },
    { code: 'NJ', name: 'New Jersey', judicial: true },
    { code: 'NM', name: 'New Mexico', judicial: true },
    { code: 'NY', name: 'New York', judicial: true },
    { code: 'NC', name: 'North Carolina', judicial: true },
    { code: 'ND', name: 'North Dakota', judicial: true },
    { code: 'OH', name: 'Ohio', judicial: true },
    { code: 'OK', name: 'Oklahoma', judicial: true },
    { code: 'OR', name: 'Oregon', judicial: false },
    { code: 'PA', name: 'Pennsylvania', judicial: true },
    { code: 'RI', name: 'Rhode Island', judicial: true },
    { code: 'SC', name: 'South Carolina', judicial: true },
    { code: 'SD', name: 'South Dakota', judicial: true },
    { code: 'TN', name: 'Tennessee', judicial: true },
    { code: 'TX', name: 'Texas', judicial: false },
    { code: 'UT', name: 'Utah', judicial: false },
    { code: 'VT', name: 'Vermont', judicial: true },
    { code: 'VA', name: 'Virginia', judicial: false },
    { code: 'WA', name: 'Washington', judicial: false },
    { code: 'WV', name: 'West Virginia', judicial: true },
    { code: 'WI', name: 'Wisconsin', judicial: true },
    { code: 'WY', name: 'Wyoming', judicial: false },
    { code: 'DC', name: 'District of Columbia', judicial: true },
    { code: 'AS', name: 'American Samoa', judicial: false },
    { code: 'GU', name: 'Guam', judicial: false },
    { code: 'MP', name: 'Northern Mariana Islands', judicial: false },
    { code: 'PR', name: 'Puerto Rico', judicial: true },
    { code: 'VI', name: 'U.S. Virgin Islands', judicial: true },
  ]
  
  return statesData.map(state => ({
    code: state.code,
    name: state.name,
    isJudicial: state.judicial,
    fcStateMonths: Math.floor(Math.random() * 18) + 6,
    evictionDuration: Math.floor(Math.random() * 6) + 2,
    rehabDuration: Math.floor(Math.random() * 8) + 3,
    reoMarketingDuration: Math.floor(Math.random() * 6) + 3,
    reoLocalMarketExtDuration: Math.floor(Math.random() * 4) + 1,
    dilDurationAvg: Math.floor(Math.random() * 12) + 3,
    propertyTaxRate: parseFloat((Math.random() * 0.02 + 0.005).toFixed(4)), // 0.5-2.5% as decimal
    transferTaxRate: parseFloat((Math.random() * 0.01 + 0.001).toFixed(4)), // 0.1-1.1% as decimal
    insuranceRateAvg: parseFloat((Math.random() * 0.005 + 0.003).toFixed(4)), // 0.3-0.8% as decimal
    fcLegalFeesAvg: parseFloat((Math.random() * 1000 + 300).toFixed(2)),
    dilCostAvg: parseFloat((Math.random() * 500 + 200).toFixed(2)),
    cfkCostAvg: parseFloat((Math.random() * 300 + 100).toFixed(2)),
    valueAdjustmentAnnual: parseFloat((Math.random() * 0.05 + 0.01).toFixed(4)), // 1-6% as decimal
    notes: ''
  }))
}

/**
 * Get CSRF token from cookie for Django POST requests
 * Django requires CSRF token for all POST/PUT/DELETE requests
 */
function getCsrfToken(): string {
  const name = 'csrftoken'
  const cookies = document.cookie.split(';')
  for (let cookie of cookies) {
    const trimmed = cookie.trim()
    if (trimmed.startsWith(name + '=')) {
      return trimmed.substring(name.length + 1)
    }
  }
  return ''
}

// Load data on mount
onMounted(() => {
  loadStateAssumptions()
})
</script>

<style scoped>
/**
 * State assumptions table styling
 * Uses Bootstrap utilities with minimal custom CSS
 */
.state-assumptions-container {
  min-height: 400px; /* Ensure minimum height for better UX */
  position: relative; /* For absolute positioning of loading state */
}

.table-responsive {
  /* Remove internal scrolling - let page scroll instead */
  max-height: none;
  overflow-y: visible;
  overflow-x: auto; /* Allow horizontal scroll for wide table */
}

/* Sticky header */
.table thead {
  position: sticky;
  top: 0;
  z-index: 10;
}

/* Prevent text wrapping in table cells - keep everything on one line */
.table td,
.table th {
  white-space: nowrap;
}

/* Allow inputs to expand to fit content */
.table input.form-control-sm {
  min-width: 80px;
}

/* Make percentage input groups narrower to fit on one line */
.table .input-group-sm input.form-control-sm {
  min-width: 60px;
  max-width: 80px;
}

.table .input-group-sm .input-group-text {
  padding: 0.25rem 0.5rem;
}
</style>
