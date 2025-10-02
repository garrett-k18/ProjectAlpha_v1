<template>
  <!--
    ForeclosureTimelinesTable.vue
    - Displays and allows editing of foreclosure timeline assumptions
    - Matrix layout: States as columns, FC Statuses as rows
    - Shows duration (in days) for each state/status combination
    
    Location: frontend_vue/src/1_global/assumptions/components/ForeclosureTimelinesTable.vue
  -->
  <div class="foreclosure-timelines-container">
    <!-- Table Header with Actions -->
    <div class="d-flex justify-content-between align-items-center mb-3">
      <div>
        <h5 class="mb-1">Foreclosure Timelines Matrix</h5>
        <p class="text-muted small mb-0">Duration in days for each foreclosure status by state</p>
      </div>
      <div class="d-flex gap-2">
        <input 
          type="text" 
          class="form-control form-control-sm" 
          placeholder="Search state or status..."
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
      <p class="text-muted mt-2">Loading foreclosure timelines...</p>
    </div>

      <!-- Matrix Table -->
    <div v-if="!isLoading" class="table-responsive">
      <table class="table table-sm table-bordered table-hover matrix-table">
        <thead class="table-light">
          <tr>
            <!-- First column: FC Status -->
            <th class="status-header sticky-col">Foreclosure Status</th>
            
            <!-- State columns -->
            <th 
              v-for="stateCode in filteredStates" 
              :key="stateCode"
              class="text-center state-header"
            >
              {{ stateCode }}
            </th>
          </tr>
        </thead>
        <tbody>
          <!-- State Type row (judicial vs non-judicial) -->
          <tr>
            <td class="fw-bold status-cell sticky-col">State Type</td>
            <td
              v-for="stateCode in filteredStates"
              :key="`type-${stateCode}`"
              class="timeline-cell text-center"
            >
              <span
                class="badge rounded-pill"
                :class="matrixData.stateMeta?.[stateCode]?.judicial ? 'bg-danger' : 'bg-success'"
              >
                {{ matrixData.stateMeta?.[stateCode]?.typeDisplay || '—' }}
              </span>
            </td>
          </tr>
          <!-- Each row is a foreclosure status -->
          <tr v-for="statusRow in filteredStatuses" :key="statusRow.id">
            <!-- Status name (row header) -->
            <td class="fw-bold status-cell sticky-col">
              {{ statusRow.statusDisplay }}
            </td>
            
            <!-- Timeline cells for each state -->
            <td 
              v-for="stateCode in filteredStates" 
              :key="`${statusRow.id}-${stateCode}`"
              class="timeline-cell"
            >
              <input 
                type="number"
                class="form-control form-control-sm text-center"
                v-model.number="statusRow.timelines[stateCode].durationDays"
                @input="markAsChanged(statusRow.timelines[stateCode])"
                min="0"
                step="1"
                placeholder="—"
              />
            </td>
          </tr>
        </tbody>
      </table>
    </div> 
  </div>
</template>

<script setup lang="ts">
/**
 * ForeclosureTimelinesTable.vue
 * 
 * What this does:
 * - Displays editable matrix of foreclosure timeline assumptions
 * - States as columns, FC statuses as rows
 * - Shows duration in days for each state/status combination
 * - Emits 'changed' event when data is modified
 * 
 * How it works:
 * - Loads timeline data from backend API in matrix format on mount
 * - Tracks changes locally before save
 * - Sends bulk update to backend when user clicks Save
 * 
 * Backend API:
 * - GET /api/core/fc-timelines/matrix/ - Load timelines in matrix format
 * - POST /api/core/fc-timelines/bulk_update/ - Save modified timelines
 */
import { ref, onMounted, computed } from 'vue'
import http from '@/lib/http'

// Component emits
const emit = defineEmits<{
  (e: 'changed'): void
}>()

// Timeline cell interface
interface TimelineCell {
  id: number | null  // Null for new records that don't exist yet
  durationDays: number | null
  costAvg: number | null
  notes: string
  changed?: boolean  // Track if this cell has been modified
  stateCode?: string  // Only present for new records (id == null)
  statusId?: number   // Only present for new records (id == null)
}

// Status row interface
interface StatusRow {
  id: number
  status: string
  statusDisplay: string
  order: number
  timelines: Record<string, TimelineCell>  // Map of state_code -> timeline data
}

// Matrix data structure
interface MatrixData {
  states: string[]  // Array of state codes (column headers)
  statuses: StatusRow[]  // Array of status rows
  stateMeta?: Record<string, { name: string; judicial: boolean; typeDisplay: string }>
}

// Component state
const isLoading = ref(true)
const isSaving = ref(false)
const hasChanges = ref(false)
const matrixData = ref<MatrixData>({
  states: [],
  statuses: []
})

// Unified filter input
const searchQuery = ref('')   // What: Filters states (code/name) and statuses (display)

/**
 * Computed: filteredStates
 * - Filters state columns by state code or state name (case-insensitive)
 * - Why: Allow quick narrowing of visible columns in the matrix
 */
// Does the query look like a status search?
const isStatusQuery = computed(() => {
  const q = searchQuery.value.toLowerCase()
  if (!q) return false
  return (matrixData.value.statuses || []).some(r => r.statusDisplay.toLowerCase().includes(q))
})

// Does the query look like a state search?
const isStateQuery = computed(() => {
  const q = searchQuery.value.toLowerCase()
  if (!q) return false
  return (matrixData.value.states || []).some((code) => {
    const name = matrixData.value.stateMeta?.[code]?.name?.toLowerCase?.() || ''
    return code.toLowerCase().includes(q) || name.includes(q)
  })
})

const filteredStates = computed(() => {
  const q = searchQuery.value.toLowerCase()
  if (!q) return matrixData.value.states
  // If the query matches a status, do NOT filter state columns (show all states)
  if (isStatusQuery.value) return matrixData.value.states
  // Otherwise, treat it as a state search and filter states
  return matrixData.value.states.filter((code) => {
    const name = matrixData.value.stateMeta?.[code]?.name?.toLowerCase?.() || ''
    return code.toLowerCase().includes(q) || name.includes(q)
  })
})

/**
 * Computed: filteredStatuses
 * - Filters status rows by statusDisplay (case-insensitive)
 * - Where: Used by template v-for for status rows
 */
const filteredStatuses = computed(() => {
  const q = searchQuery.value.toLowerCase()
  if (!q) return matrixData.value.statuses
  // If the query matches a state, do NOT filter statuses (show all rows)
  if (isStateQuery.value) return matrixData.value.statuses
  // Otherwise, treat it as a status search and filter by statusDisplay
  return matrixData.value.statuses.filter((row) => row.statusDisplay.toLowerCase().includes(q))
})

/**
 * Load foreclosure timelines from backend in matrix format
 */
async function loadForeclosureTimelines() {
  isLoading.value = true
  try {
    console.log('Fetching foreclosure timelines matrix...')
    
    // Call the matrix endpoint to get data in the right format
    // Note: http client already has /api as baseURL, so we don't include it here
    const response = await http.get('/core/fc-timelines/matrix/')
    
    console.log('API Response:', response)
    console.log('Response data:', response.data)
    
    matrixData.value = response.data
    
    console.log('Matrix data loaded:', {
      stateCount: matrixData.value.states?.length || 0,
      statusCount: matrixData.value.statuses?.length || 0,
      states: matrixData.value.states,
      statuses: matrixData.value.statuses
    })
  } catch (error) {
    console.error('Error loading foreclosure timelines:', error)
    console.error('Error details:', error)
    // TODO: Show error toast notification
  } finally {
    isLoading.value = false
  }
}

/**
 * Mark that a specific timeline cell has been changed
 * 
 * @param cell - The timeline cell that was modified
 */
function markAsChanged(cell: TimelineCell) {
  // Mark this specific cell as changed
  cell.changed = true
  
  // Mark that the overall form has changes
  hasChanges.value = true
  
  // Emit changed event to parent
  emit('changed')
}

/**
 * Save changes to backend
 * 
 * Collects all modified timeline cells and sends them to bulk update/create endpoint
 * Handles both existing records (id != null) and new records (id == null)
 */
async function saveChanges() {
  isSaving.value = true
  try {
    // Collect all changed timeline cells
    const changedTimelines: any[] = []
    const newTimelines: any[] = []
    
    for (const statusRow of matrixData.value.statuses) {
      for (const stateCode in statusRow.timelines) {
        const cell = statusRow.timelines[stateCode]
        
        // Only include cells that have been modified
        if (cell.changed) {
          if (cell.id) {
            // Existing record - update it
            changedTimelines.push({
              id: cell.id,
              durationDays: cell.durationDays,
              costAvg: cell.costAvg,
              notes: cell.notes
            })
          } else {
            // New record - create it (need state and status info)
            newTimelines.push({
              stateCode: cell.stateCode,
              statusId: cell.statusId,
              durationDays: cell.durationDays,
              costAvg: cell.costAvg,
              notes: cell.notes
            })
          }
        }
      }
    }
    
    if (changedTimelines.length === 0 && newTimelines.length === 0) {
      console.log('No changes to save')
      return
    }
    
    console.log(`Saving ${changedTimelines.length} updates and ${newTimelines.length} new records...`)
    
    // Send bulk update for existing records
    if (changedTimelines.length > 0) {
      await http.post('/core/fc-timelines/bulk_update/', changedTimelines)
    }
    
    // TODO: Create endpoint for bulk create of new records
    // For now, just log them
    if (newTimelines.length > 0) {
      console.warn('New timeline creation not yet implemented:', newTimelines)
    }
    
    // Clear all change flags
    for (const statusRow of matrixData.value.statuses) {
      for (const stateCode in statusRow.timelines) {
        delete statusRow.timelines[stateCode].changed
      }
    }
    
    hasChanges.value = false
    console.log('Foreclosure timelines saved successfully')
    
    // TODO: Show success toast notification
  } catch (error) {
    console.error('Error saving foreclosure timelines:', error)
    // TODO: Show error toast notification
  } finally {
    isSaving.value = false
  }
}

// Load data on mount
onMounted(() => {
  loadForeclosureTimelines()
})
</script>

<style scoped>
/**
 * Foreclosure timelines matrix table styling
 * 
 * What this does:
 * - Creates a scrollable matrix table with sticky first column and header
 * - Styles input cells for inline editing
 * - Ensures proper spacing and alignment
 */

/* Container styling */
.foreclosure-timelines-container {
  min-height: 400px;
  position: relative;
}

/* Table responsive wrapper - enable horizontal scroll */
.table-responsive {
  max-height: 600px;
  overflow-x: auto;
  overflow-y: auto;
}

/* Matrix table styling */
.matrix-table {
  min-width: 100%;
  white-space: nowrap;
}

/* Sticky first column (status names) */
.sticky-col {
  position: sticky;
  left: 0;
  z-index: 5;
  background-color: #f8f9fa;
}

/* Header styling */
.matrix-table thead {
  position: sticky;
  top: 0;
  z-index: 10;
  background-color: #f8f9fa;
}

.matrix-table thead .sticky-col {
  z-index: 15; /* Higher than both sticky header and sticky column */
}

/* Status header column */
.status-header {
  min-width: 250px;
  max-width: 200px;
  font-weight: 600;
}

/* State header columns */
/* State header columns
   Increased width to accommodate 'Judicial'/'Non-Judicial' pills in the new
   State Type row without wrapping. */
.state-header {
  min-width: 120px;
  max-width: 120px;
  font-size: 0.875rem;
  font-weight: 600;
}

/* Status cell (first column in each row) */
.status-cell {
  min-width: 200px;
  max-width: 200px;
  font-size: 0.875rem;
  vertical-align: middle;
  padding: 0.5rem;
}

/* Timeline data cells */
/* Data cells width matches header width for consistent column sizing. */
.timeline-cell {
  min-width: 120px;
  max-width: 120px;
  padding: 0.25rem;
  vertical-align: middle;
}

/* Input fields in cells */
.timeline-cell input {
  width: 100%;
  font-size: 0.875rem;
  padding: 0.25rem 0.5rem;
  border: 1px solid #dee2e6;
  border-radius: 0.25rem;
}

/* Input focus state */
.timeline-cell input:focus {
  border-color: #0d6efd;
  box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25);
  outline: none;
}

/* Empty cell styling */
.timeline-cell .text-muted {
  font-size: 1rem;
  color: #adb5bd;
}

/* Badge styling */
.badge {
  font-size: 0.75rem;
  font-weight: 500;
}
</style>
