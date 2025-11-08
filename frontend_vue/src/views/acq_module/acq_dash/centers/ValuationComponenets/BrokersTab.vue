<template>
  <div>
    <h5 class="mb-3">Broker Valuations</h5>
    
    <!-- WHAT: Advanced Filters Section -->
    <!-- WHY: Allow users to filter broker valuations by state, city, value ranges, grade -->
    <div class="card bg-light border mb-3">
      <div class="card-body py-2">
        <div class="row g-2 align-items-end">
          <!-- Search Box (City Only) -->
          <div class="col-md-3">
            <label class="form-label small mb-1">Search City</label>
            <input 
              v-model="filters.search" 
              type="text" 
              class="form-control form-control-sm" 
              placeholder="Search by city..."
              @input="applyFilters"
            />
          </div>
          
          <!-- State Filter -->
          <div class="col-md-2">
            <label class="form-label small mb-1">State</label>
            <select 
              v-model="filters.state" 
              class="form-select form-select-sm"
              @change="applyFilters"
            >
              <option value="">All States</option>
              <option v-for="state in availableStates" :key="state" :value="state">
                {{ state }}
              </option>
            </select>
          </div>
          
          <!-- Value Range Min -->
          <div class="col-md-2">
            <label class="form-label small mb-1">Min Value</label>
            <input 
              v-model="filters.minValue" 
              type="number" 
              class="form-control form-control-sm" 
              placeholder="0"
              @input="applyFilters"
            />
          </div>
          
          <!-- Value Range Max -->
          <div class="col-md-2">
            <label class="form-label small mb-1">Max Value</label>
            <input 
              v-model="filters.maxValue" 
              type="number" 
              class="form-control form-control-sm" 
              placeholder="999999999"
              @input="applyFilters"
            />
          </div>
          
          <!-- Grade Filter -->
          <div class="col-md-1">
            <label class="form-label small mb-1">Grade</label>
            <select 
              v-model="filters.grade" 
              class="form-select form-select-sm"
              @change="applyFilters"
            >
              <option value="">All Grades</option>
              <option value="A+">A+</option>
              <option value="A">A</option>
              <option value="B">B</option>
              <option value="C">C</option>
              <option value="D">D</option>
              <option value="F">F</option>
            </select>
          </div>
          
          <!-- Clear Filters Button -->
          <div class="col-md-1">
            <button 
              class="btn btn-sm btn-light w-100" 
              @click="clearFilters"
              title="Clear all filters"
            >
              <i class="ri-filter-off-line"></i>
            </button>
          </div>
        </div>
        
        <!-- Filter Results Count -->
        <div class="mt-2 small text-muted">
          Showing {{ paginatedRows.length }} of {{ filteredRows.length }} assets
          <span v-if="filteredRows.length < (rows?.length || 0)">
            (filtered from {{ rows?.length || 0 }} total)
          </span>
        </div>
      </div>
    </div>
    
    <!-- Brokers Table -->
    <div class="table-responsive">
      <table class="table table-centered table-hover mb-0">
        <thead class="table-light">
          <tr>
            <th>Address</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!filteredRows || filteredRows.length === 0">
            <td class="text-center text-muted py-3">
              <span v-if="filters.search || filters.state || filters.minValue || filters.maxValue || filters.grade">
                No assets match your filters
              </span>
              <span v-else>
                No assets to display
              </span>
            </td>
          </tr>
          <tr v-for="(asset, index) in paginatedRows" :key="`broker-asset-${asset?.asset_hub_id || asset?.id || index}`">
            <td>
              <div class="fw-semibold address-link" @click="emit('openLoanModal', asset)">
                {{ formatAddress(asset) }}
              </div>
              <div class="small address-link address-link-secondary" @click="emit('openLoanModal', asset)">
                {{ formatCityState(asset) }}
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- Pagination Controls -->
    <div class="d-flex justify-content-between align-items-center mt-3">
      <div class="text-muted small">
        Page {{ currentPage }} of {{ totalPages }}
      </div>
      <nav>
        <ul class="pagination pagination-sm mb-0">
          <li class="page-item" :class="{ disabled: currentPage === 1 }">
            <a class="page-link" href="#" @click.prevent="goToPage(currentPage - 1)">Previous</a>
          </li>
          <li 
            class="page-item" 
            v-for="page in visiblePages" 
            :key="page"
            :class="{ active: page === currentPage }"
          >
            <a class="page-link" href="#" @click.prevent="goToPage(page)">{{ page }}</a>
          </li>
          <li class="page-item" :class="{ disabled: currentPage === totalPages }">
            <a class="page-link" href="#" @click.prevent="goToPage(currentPage + 1)">Next</a>
          </li>
        </ul>
      </nav>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

// WHAT: Props passed from parent ValuationCenter
// WHY: Tab needs data from parent
const props = defineProps<{
  rows: any[] | null
}>()

// WHAT: Emits for parent component
// WHY: Tab needs to communicate actions back to parent
const emit = defineEmits<{
  openLoanModal: [asset: any]
}>()

// WHAT: Pagination state
// WHY: Control page display and navigation
const currentPage = ref(1)
const pageSize = ref(50)

// WHAT: Filter state
// WHY: Allow users to search and filter table data
const filters = ref({
  search: '',
  state: '',
  minValue: null as number | null,
  maxValue: null as number | null,
  grade: '',
})

// WHAT: Extract unique states from rows for filter dropdown
// WHY: Populate state filter options
const availableStates = computed(() => {
  const states = new Set<string>()
  if (props.rows) {
    props.rows.forEach((row: any) => {
      if (row.state) states.add(row.state)
    })
  }
  return Array.from(states).sort()
})

// WHAT: Filtered rows based on user filters
// WHY: Apply search and filter criteria to rows
const filteredRows = computed(() => {
  if (!props.rows) return []
  
  let filtered = props.rows
  
  // WHAT: Apply city search filter
  if (filters.value.search) {
    filtered = filtered.filter((row: any) => 
      (row.city || '').toLowerCase().includes(filters.value.search.toLowerCase())
    )
  }
  
  // WHAT: Apply state filter
  if (filters.value.state) {
    filtered = filtered.filter((row: any) => row.state === filters.value.state)
  }
  
  // WHAT: Apply min value filter (seller_asis_value)
  if (filters.value.minValue != null && filters.value.minValue > 0) {
    filtered = filtered.filter((row: any) => 
      (row.seller_asis_value || 0) >= filters.value.minValue!
    )
  }
  
  // WHAT: Apply max value filter (seller_asis_value)
  if (filters.value.maxValue != null && filters.value.maxValue > 0) {
    filtered = filtered.filter((row: any) => 
      (row.seller_asis_value || 0) <= filters.value.maxValue!
    )
  }
  
  // WHAT: Apply grade filter
  // WHY: Allow users to view only assets with specific grades
  // HOW: Check internal_initial_uw_grade field
  if (filters.value.grade) {
    filtered = filtered.filter((row: any) => row.internal_initial_uw_grade === filters.value.grade)
  }
  
  return filtered
})

// WHAT: Total number of pages based on filtered results
const totalPages = computed(() => Math.ceil(filteredRows.value.length / pageSize.value) || 1)

// WHAT: Visible page numbers for pagination (show 5 pages max)
const visiblePages = computed(() => {
  const pages: number[] = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

// WHAT: Paginated rows for current page
// WHY: Show only rows for current page
const paginatedRows = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredRows.value.slice(start, end)
})

// Helper functions
// WHAT: Apply filters and reset to page 1
// WHY: User changed filter criteria, show first page of results
function applyFilters() {
  currentPage.value = 1
}

// WHAT: Clear all filters and reset pagination
// WHY: User wants to see all data again
function clearFilters() {
  filters.value.search = ''
  filters.value.state = ''
  filters.value.minValue = null
  filters.value.maxValue = null
  filters.value.grade = ''
  currentPage.value = 1
}

// WHAT: Navigate to specific page
// WHY: User clicks pagination controls
function goToPage(page: number) {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

// WHAT: Format full address from asset data
function formatAddress(asset: any): string {
  return asset.street_address || asset.property_address || asset.address || '-'
}

// WHAT: Format city and state
function formatCityState(asset: any): string {
  const city = asset.city || asset.property_city || ''
  const state = asset.state || asset.property_state || ''
  return [city, state].filter(Boolean).join(', ') || '-'
}
</script>

<style scoped>
.address-link {
  cursor: pointer;
  color: #3577f1;
}

.address-link:hover {
  text-decoration: underline;
}

.address-link-secondary {
  color: #6c757d;
}
</style>

