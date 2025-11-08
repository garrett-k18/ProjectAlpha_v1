<template>
  <div>
    <h5 class="mb-3">Value Reconciliation</h5>
    
    <!-- WHAT: Advanced Filters Section -->
    <!-- WHY: Allow users to filter reconciliation data by state, city, value ranges, grade -->
    <div class="card bg-light border mb-3">
      <div class="card-body py-2">
        <div class="row g-2 align-items-end">
          <!-- Search Box (City or Loan Number) -->
          <div class="col-md-3">
            <label class="form-label small mb-1">Search</label>
            <input 
              v-model="filters.search" 
              type="text" 
              class="form-control form-control-sm" 
              placeholder="Search by city or loan number..."
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
          
          <!-- Grade Filter -->
          <div class="col-md-1">
            <label class="form-label small mb-1">Grade</label>
            <select 
              v-model="filters.grade" 
              class="form-select form-select-sm"
              @change="applyFilters"
            >
              <option value="">All Grades</option>
              <option value="none">No Grade</option>
              <option value="A+">A+</option>
              <option value="A">A</option>
              <option value="B">B</option>
              <option value="C">C</option>
              <option value="D">D</option>
              <option value="F">F</option>
            </select>
          </div>
          
          <!-- Value Operator -->
          <div class="col-md-2">
            <label class="form-label small mb-1">Operator</label>
            <select 
              v-model="filters.valueOperator" 
              class="form-select form-select-sm"
              @change="applyFilters"
            >
              <option value=">">Greater Than</option>
              <option value="<">Less Than</option>
              <option value="=">Equal To</option>
              <option value=">=">Greater or Equal</option>
              <option value="<=">Less or Equal</option>
            </select>
          </div>
          
          <!-- Value Filter -->
          <div class="col-md-2">
            <label class="form-label small mb-1">Value</label>
            <input 
              type="text" 
              class="form-control form-control-sm" 
              :value="formatNumberWithCommas(filters.valueAmount)"
              @input="handleValueFilterInput"
              placeholder="Enter amount"
            />
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
    
    <!-- WHAT: Reconciliation Table -->
    <!-- WHY: Compare all valuation sources side-by-side for reconciliation -->
    <div class="table-responsive">
      <table class="table table-centered table-hover mb-0">
        <thead class="table-light">
          <tr>
            <th>Loan #</th>
            <th>Address</th>
            <th class="text-center">Grade</th>
            <th class="text-center">Internal AIV</th>
            <th class="text-center">Internal ARV</th>
            <th class="text-center">Rehab Est</th>
            <th class="text-center">Recommend Rehab</th>
            <th class="text-center">Notes</th>
          </tr>
        </thead>
        <tbody>
          <!-- WHAT: Empty state row when no data or no filtered results -->
          <tr v-if="!filteredRows || filteredRows.length === 0">
            <td colspan="8" class="text-center text-muted py-3">
              <span v-if="filters.search || filters.state || filters.valueAmount || filters.grade">
                No assets match your filters
              </span>
              <span v-else>
                No assets to display
              </span>
            </td>
          </tr>
          <!-- WHAT: Asset row showing editable internal and reconciled valuations -->
          <tr v-for="(asset, index) in paginatedRows" :key="`recon-asset-${asset?.asset_hub_id || asset?.id || index}`">
            <!-- WHAT: Seller Tape ID (Loan Number) - Clickable -->
            <!-- WHY: Primary identifier for the asset/loan, opens modal on click -->
            <td>
              <div class="loan-number-container" @click="emit('openLoanModal', asset)">
                {{ asset.sellertape_id || '-' }}
              </div>
            </td>
            <!-- WHAT: Address column with clickable link -->
            <td>
              <div class="address-container" @click="emit('openLoanModal', asset)">
                <div class="fw-semibold">
                  {{ formatAddress(asset) }}
                </div>
                <div class="small">
                  {{ formatCityState(asset) }}
                </div>
              </div>
            </td>
            <!-- WHAT: Internal valuation grade - Editable dropdown -->
            <td class="text-center">
              <select 
                class="form-select form-select-sm grade-select"
                :value="asset.internal_initial_uw_grade || ''"
                @change="(e) => handleSaveGrade(asset, e)"
              >
                <option value="">-</option>
                <option value="A+">A+</option>
                <option value="A">A</option>
                <option value="B">B</option>
                <option value="C">C</option>
                <option value="D">D</option>
                <option value="F">F</option>
              </select>
            </td>
            <!-- WHAT: Internal AIV - Editable -->
            <td class="text-center">
              <input 
                type="text"
                class="editable-value-inline"
                :value="formatCurrencyForInput(asset.internal_initial_uw_asis_value)"
                @input="(e) => formatInputOnType(e)"
                @blur="(e) => handleSaveInternalValue(asset, 'asis', e)"
                @keyup.enter="(e) => handleSaveInternalValue(asset, 'asis', e)"
                placeholder="Add Value"
              />
            </td>
            <!-- WHAT: Internal ARV - Editable -->
            <td class="text-center">
              <input 
                type="text"
                class="editable-value-inline"
                :value="formatCurrencyForInput(asset.internal_initial_uw_arv_value)"
                @input="(e) => formatInputOnType(e)"
                @blur="(e) => handleSaveInternalValue(asset, 'arv', e)"
                @keyup.enter="(e) => handleSaveInternalValue(asset, 'arv', e)"
                placeholder="Add Value"
              />
            </td>
            <!-- WHAT: Rehab estimate total - Editable -->
            <td class="text-center">
              <input 
                type="text"
                class="editable-value-inline"
                :value="formatCurrencyForInput(asset.broker_rehab_est)"
                @input="(e) => formatInputOnType(e)"
                @blur="(e) => handleSaveRehabEst(asset, e)"
                @keyup.enter="(e) => handleSaveRehabEst(asset, e)"
                placeholder="Add Value"
              />
            </td>
            <!-- WHAT: Recommend rehab flag - Editable dropdown -->
            <td class="text-center">
              <select 
                class="form-select form-select-sm recommend-rehab-select"
                :value="asset.broker_recommend_rehab ? 'yes' : 'no'"
                @change="(e) => handleSaveRecommendRehab(asset, e)"
              >
                <option value="no">No</option>
                <option value="yes">Yes</option>
              </select>
            </td>
            <!-- WHAT: Internal valuation notes column with 2-line display -->
            <!-- WHY: Display internal UW notes in table with 2-line wrapping for better readability -->
            <td class="notes-column text-center">
              <div v-if="asset.internal_initial_uw_notes" :title="asset.internal_initial_uw_notes">
                {{ asset.internal_initial_uw_notes }}
              </div>
              <span v-else class="text-muted">-</span>
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
  saveInternalUW: [asset: any, field: 'asis' | 'arv', value: any]
  saveGrade: [asset: any, grade: string]
  saveRehabEst: [asset: any, value: number]
  saveRecommendRehab: [asset: any, value: boolean]
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
  valueOperator: '>' as '>' | '<' | '=' | '>=' | '<=',
  valueAmount: null as number | null,
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
  
  // WHAT: Apply search filter (city or loan number)
  // WHY: Allow users to search by either city or loan number
  if (filters.value.search) {
    const searchTerm = filters.value.search.toLowerCase()
    filtered = filtered.filter((row: any) => 
      (row.city || '').toLowerCase().includes(searchTerm) ||
      (row.sellertape_id || '').toLowerCase().includes(searchTerm)
    )
  }
  
  // WHAT: Apply state filter
  if (filters.value.state) {
    filtered = filtered.filter((row: any) => row.state === filters.value.state)
  }
  
  // WHAT: Apply grade filter
  // WHY: Allow users to view only assets with specific grades or no grade
  // HOW: Check internal_initial_uw_grade field, handle 'none' for assets without grades
  if (filters.value.grade) {
    if (filters.value.grade === 'none') {
      filtered = filtered.filter((row: any) => !row.internal_initial_uw_grade)
    } else {
      filtered = filtered.filter((row: any) => row.internal_initial_uw_grade === filters.value.grade)
    }
  }
  
  // WHAT: Apply value filter with operator (filters internal_initial_uw_asis_value)
  // WHY: Allow flexible value filtering with different operators
  if (filters.value.valueAmount != null && filters.value.valueAmount > 0) {
    filtered = filtered.filter((row: any) => {
      const value = row.internal_initial_uw_asis_value
      if (value == null) return false
      
      const filterAmount = filters.value.valueAmount!
      switch (filters.value.valueOperator) {
        case '>': return value > filterAmount
        case '<': return value < filterAmount
        case '=': return value === filterAmount
        case '>=': return value >= filterAmount
        case '<=': return value <= filterAmount
        default: return true
      }
    })
  }
  
  return filtered
})

// WHAT: Paginated rows for current page
// WHY: Display only one page of results at a time
const paginatedRows = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredRows.value.slice(start, end)
})

// WHAT: Calculate total pages
// WHY: Show pagination controls
const totalPages = computed(() => {
  return Math.ceil(filteredRows.value.length / pageSize.value) || 1
})

// WHAT: Calculate visible page numbers for pagination
// WHY: Show limited page numbers to avoid cluttering UI
const visiblePages = computed(() => {
  const total = totalPages.value
  const current = currentPage.value
  const pages: number[] = []
  
  // Show max 5 page numbers
  let start = Math.max(1, current - 2)
  let end = Math.min(total, start + 4)
  
  // Adjust start if we're near the end
  if (end - start < 4) {
    start = Math.max(1, end - 4)
  }
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

// WHAT: Navigate to a specific page
// WHY: Handle pagination clicks
function goToPage(page: number) {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

// WHAT: Apply filters
// WHY: Trigger filter recalculation
function applyFilters() {
  currentPage.value = 1
}

// WHAT: Clear all filters
// WHY: Reset to show all data
function clearFilters() {
  filters.value = {
    search: '',
    state: '',
    valueOperator: '>',
    valueAmount: null,
    grade: '',
  }
  currentPage.value = 1
}

// WHAT: Format full address from asset data
function formatAddress(asset: any): string {
  return asset.street_address || asset.property_address || asset.address || '-'
}

// WHAT: Format city and state
function formatCityState(asset: any): string {
  const city = asset.city
  const state = asset.state
  return [city, state].filter(Boolean).join(', ') || '-'
}

// WHAT: Format currency values for display
function formatCurrency(val: number | null | undefined): string {
  if (val == null) return '-'
  return new Intl.NumberFormat('en-US', { 
    style: 'currency', 
    currency: 'USD', 
    maximumFractionDigits: 0 
  }).format(val)
}

// WHAT: Format currency for input field (with $ symbol and commas)
// WHY: Display values in familiar currency format
function formatCurrencyForInput(val: any): string {
  const num = typeof val === 'number' ? val : null
  if (num == null) return ''
  return '$' + new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 }).format(num)
}

// WHAT: Format input field as user types (add $ and commas)
// WHY: Provide real-time feedback as users enter currency values
function formatInputOnType(event: Event) {
  const input = event.target as HTMLInputElement
  
  // WHAT: Store cursor position and old value before formatting
  const oldValue = input.value
  const oldCursorPosition = input.selectionStart || 0
  
  // WHAT: Get raw numeric value from input (remove all non-digits)
  const rawValue = oldValue.replace(/[^0-9]/g, '')
  
  if (rawValue === '') {
    input.value = ''
    return
  }
  
  // WHAT: Format the numeric value with currency symbol and commas
  const numericValue = parseInt(rawValue, 10)
  const formattedValue = '$' + new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 }).format(numericValue)
  
  // WHAT: Update input value with formatted string
  input.value = formattedValue
  
  // WHAT: Restore cursor position (adjust for added/removed characters)
  const lengthDiff = formattedValue.length - oldValue.length
  const newCursorPosition = Math.max(0, oldCursorPosition + lengthDiff)
  input.setSelectionRange(newCursorPosition, newCursorPosition)
}

// WHAT: Save internal valuation value (AIV or ARV)
// WHY: Update internal underwriting values on blur or enter
function handleSaveInternalValue(asset: any, field: string, event: Event) {
  const input = event.target as HTMLInputElement
  const rawValue = input.value.replace(/[^0-9]/g, '')
  const numericValue = rawValue ? parseFloat(rawValue) : null
  
  emit('saveInternalUW', asset, field, numericValue)
}

// WHAT: Save grade selection
// WHY: Update internal underwriting grade
function handleSaveGrade(asset: any, event: Event) {
  const select = event.target as HTMLSelectElement
  const grade = select.value || null
  
  if (grade) {
    emit('saveGrade', asset, grade)
  }
}

// WHAT: Save rehab estimate
// WHY: Update broker rehab estimate value
function handleSaveRehabEst(asset: any, event: Event) {
  const input = event.target as HTMLInputElement
  const rawValue = input.value.replace(/[^0-9]/g, '')
  const numericValue = rawValue ? parseFloat(rawValue) : null
  
  if (numericValue !== null) {
    emit('saveRehabEst', asset, numericValue)
  }
}

// WHAT: Save recommend rehab flag
// WHY: Update broker recommendation for rehabilitation
function handleSaveRecommendRehab(asset: any, event: Event) {
  const select = event.target as HTMLSelectElement
  const value = select.value === 'yes'
  
  emit('saveRecommendRehab', asset, value)
}

// WHAT: Get CSS class for grade badge
// WHY: Color-code grades for easy visual identification
function getGradeBadgeClass(grade: string | null | undefined): string {
  if (!grade) return 'badge bg-secondary'
  
  const gradeUpper = grade.toUpperCase()
  
  switch (gradeUpper) {
    case 'A+':
    case 'A':
      return 'badge bg-success'
    case 'B':
      return 'badge bg-primary'
    case 'C':
      return 'badge bg-warning'
    case 'D':
    case 'F':
      return 'badge bg-danger'
    default:
      return 'badge bg-secondary'
  }
}

// WHAT: Format number with commas for display
// WHY: Make large numbers more readable in filter input
function formatNumberWithCommas(val: number | null | undefined): string {
  if (val == null) return ''
  return new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 }).format(val)
}

// WHAT: Handle value filter input with comma formatting
// WHY: Auto-format numbers as user types in filter input
function handleValueFilterInput(event: Event) {
  const input = event.target as HTMLInputElement
  const rawValue = input.value.replace(/[^0-9]/g, '')
  
  if (rawValue === '') {
    filters.value.valueAmount = null
    input.value = ''
    return
  }
  
  const numericValue = parseInt(rawValue, 10)
  filters.value.valueAmount = numericValue
  input.value = formatNumberWithCommas(numericValue)
  
  applyFilters()
}
</script>

<style scoped>
/* WHAT: Loan number container - clickable to open modal */
/* WHY: Make loan number interactive like address */
.loan-number-container {
  cursor: pointer;
  color: #3577f1;
  font-weight: 600;
}

.loan-number-container:hover {
  text-decoration: underline;
}

/* WHAT: Address container - entire address block is clickable as one unit */
/* WHY: Better UX with single click area, blue text indicates it's interactive */
.address-container {
  cursor: pointer;
  color: #3577f1;
}

.address-container:hover {
  text-decoration: underline;
}

/* WHAT: Inline editable value styling - matches OverviewTab style */
/* WHY: Clean, minimal input that blends with table */
.editable-value-inline {
  border: none;
  background: transparent;
  text-align: center;
  padding: 0.25rem 0.5rem;
  width: 120px;
  font-weight: 500;
  color: #3577f1;
}

.editable-value-inline:focus {
  outline: 1px solid #3577f1;
  background-color: #f8f9fa;
  border-radius: 0.25rem;
}

.editable-value-inline::placeholder {
  color: #3577f1;
  font-style: italic;
  font-weight: normal;
}

/* WHAT: Grade select dropdown styling */
/* WHY: Compact dropdown for grade selection */
.grade-select {
  min-width: 80px;
  max-width: 100px;
  margin: 0 auto;
}

/* WHAT: Recommend rehab dropdown styling */
/* WHY: Make dropdown compact for Yes/No selection */
.recommend-rehab-select {
  min-width: 70px;
  max-width: 90px;
  margin: 0 auto;
}

/* WHAT: Notes column styling */
/* WHY: Set width and allow text to wrap naturally to 2 lines */
.notes-column {
  min-width: 280px;
  max-width: 350px;
  vertical-align: middle;
  font-size: 0.875rem;
}

.notes-column div {
  line-height: 1.5;
  max-height: 3em; /* Approximately 2 lines */
  overflow: hidden;
  word-wrap: break-word;
  text-align: center;
  margin: 0 auto;
}
</style>
