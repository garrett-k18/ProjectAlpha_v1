<template>
  <div>
    <h5 class="mb-3">Valuation Summary Table</h5>
    
    <!-- WHAT: Advanced Filters Section -->
    <!-- WHY: Allow users to filter table by state, city, value ranges, grade -->
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
          
          <!-- Value Source Selector -->
          <div class="col-md-2">
            <label class="form-label small mb-1">Value Source</label>
            <select 
              v-model="filters.valueSource" 
              class="form-select form-select-sm"
              @change="applyFilters"
            >
              <option value="seller">Seller</option>
              <option value="bpo">BPO</option>
              <option value="broker">Broker</option>
              <option value="internal">Internal</option>
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
    
    <!-- Overview Table -->
    <div class="table-responsive">
      <table class="table table-centered table-hover mb-0">
        <thead class="table-light">
          <tr>
            <th>Loan #</th>
            <th>Address</th>
            <th class="text-center">Grade</th>
            <th class="text-center">Quick Links</th>
            <th class="text-center">Seller AIV - ARV</th>
            <th class="text-center">BPO AIV - ARV</th>
            <th class="text-center">Broker AIV - ARV</th>
            <th class="text-center">Internal AIV - ARV</th>
            <th class="text-center">Status</th>
            <th class="text-center">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!filteredRows || filteredRows.length === 0">
            <td colspan="10" class="text-center text-muted py-3">
              <span v-if="filters.search || filters.state || filters.valueAmount || filters.grade">
                No assets match your filters
              </span>
              <span v-else>
                No assets to display
              </span>
            </td>
          </tr>
          <tr v-for="(asset, index) in paginatedRows" :key="`asset-${asset?.asset_hub_id || asset?.id || index}`">
            <!-- WHAT: Seller Tape ID (Loan Number) - Clickable -->
            <!-- WHY: Primary identifier for the asset/loan, opens modal on click -->
            <td>
              <div class="loan-number-container" @click="emit('openLoanModal', asset)">
                {{ asset.sellertape_id || '-' }}
              </div>
            </td>
            <!-- WHAT: Entire address block is clickable as one unit -->
            <!-- WHY: Better UX - single click area for the whole address -->
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
            <td class="text-center">
              <!-- WHAT: Grade dropdown for Internal Initial UW valuation -->
              <!-- WHY: Allow users to assign grade to internal UW valuations -->
              <select 
                class="form-select form-select-sm grade-select"
                :value="getInternalUWGrade(asset)"
                @change="(e) => handleSaveGrade(asset, (e.target as HTMLSelectElement).value)"
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
            <td class="text-center py-1">
              <!-- WHAT: 3rd Party Site Links - stacked vertically with minimal spacing -->
              <div class="d-flex flex-column align-items-center" style="gap: 1px; line-height: 1.3;">
                <a 
                  :href="getZillowUrl(asset)" 
                  target="_blank" 
                  class="third-party-link small"
                  @click.stop
                >
                  Zillow <i class="ri-external-link-line"></i>
                </a>
                <a 
                  :href="getRedfinUrl(asset)" 
                  target="_blank" 
                  class="third-party-link small"
                  @click.stop
                >
                  Redfin <i class="ri-external-link-line"></i>
                </a>
                <a 
                  :href="getRealtorUrl(asset)" 
                  target="_blank" 
                  class="third-party-link small"
                  @click.stop
                >
                  Realtor <i class="ri-external-link-line"></i>
                </a>
              </div>
            </td>
            <td class="text-center">
              <span>{{ formatCurrency(asset.seller_asis_value as number) }}</span>
              <span class="mx-2"> - </span>
              <span>{{ formatCurrency(asset.seller_arv_value as number) }}</span>
            </td>
            <td class="text-center">
              <span>{{ formatCurrency(asset.additional_asis_value as number) }}</span>
              <span class="mx-2"> - </span>
              <span>{{ formatCurrency(asset.additional_arv_value as number) }}</span>
            </td>
            <td class="text-center">
              <span>{{ formatCurrency(asset.broker_asis_value as number) }}</span>
              <span class="mx-2"> - </span>
              <span>{{ formatCurrency(asset.broker_arv_value as number) }}</span>
            </td>
            <td class="text-center">
              <!-- WHAT: Editable Internal UW Initial As-Is Value - blue styling indicates user can edit -->
              <input
                type="text"
                class="editable-value-inline"
                :value="formatCurrencyForInput(asset.internal_initial_uw_asis_value)"
                @input="(e) => formatInputOnType(e)"
                @blur="(e) => handleSaveInternalUW(asset, 'asis', e)"
                @keyup.enter="(e) => handleSaveInternalUW(asset, 'asis', e)"
                placeholder="Add Value"
              />
              <span style="margin: 0 0px;"> - </span>
              <!-- WHAT: Editable Internal UW Initial ARV Value - blue styling indicates user can edit -->
              <input
                type="text"
                class="editable-value-inline"
                :value="formatCurrencyForInput(asset.internal_initial_uw_arv_value)"
                @input="(e) => formatInputOnType(e)"
                @blur="(e) => handleSaveInternalUW(asset, 'arv', e)"
                @keyup.enter="(e) => handleSaveInternalUW(asset, 'arv', e)"
                placeholder="Add Value"
              />
            </td>
            <td class="text-center">
              <!-- WHAT: Show multiple status badges for missing valuations -->
              <!-- WHY: Display all missing items at once for clarity -->
              <div class="d-flex flex-column gap-1 align-items-center">
                <span v-if="!asset.additional_asis_value" class="badge bg-warning">Pending BPO</span>
                <span v-if="!asset.broker_asis_value" class="badge bg-warning">Pending Broker</span>
                <span v-if="!asset.internal_initial_uw_asis_value" class="badge bg-warning">Pending Reconciled</span>
                <span v-if="asset.seller_asis_value && asset.additional_asis_value && asset.broker_asis_value && asset.internal_initial_uw_asis_value" class="badge bg-success">Approved</span>
              </div>
            </td>
            <td class="text-center">
              <button class="btn btn-sm btn-light me-1" title="View Details">
                <i class="ri-eye-line"></i>
              </button>
              <button class="btn btn-sm btn-light" title="Edit">
                <i class="ri-pencil-line"></i>
              </button>
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
import http from '@/lib/http'

// WHAT: Props passed from parent ValuationCenter
// WHY: Tab needs data and callbacks from parent
const props = defineProps<{
  rows: any[] | null
  selectedSellerId: number | null
  selectedTradeId: number | null
}>()

// WHAT: Emits for parent component
// WHY: Tab needs to communicate actions back to parent
const emit = defineEmits<{
  openLoanModal: [asset: any]
  saveGrade: [asset: any, gradeCode: string]
  saveInternalUW: [asset: any, field: 'asis' | 'arv', event: Event]
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
  valueSource: 'seller' as 'seller' | 'bpo' | 'broker' | 'internal',
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
  
  // WHAT: Apply value filter with operator
  // WHY: Allow flexible value filtering with different operators and sources
  if (filters.value.valueAmount != null && filters.value.valueAmount > 0) {
    filtered = filtered.filter((row: any) => {
      // WHAT: Get the value based on selected source
      let value: number | null = null
      switch (filters.value.valueSource) {
        case 'seller':
          value = row.seller_asis_value
          break
        case 'bpo':
          value = row.additional_asis_value
          break
        case 'broker':
          value = row.broker_asis_value
          break
        case 'internal':
          value = row.internal_initial_uw_asis_value
          break
      }
      
      if (value == null) return false
      
      // WHAT: Apply operator comparison
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
  filters.value.valueSource = 'seller'
  filters.value.valueOperator = '>'
  filters.value.valueAmount = null
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

// WHAT: Calculate variance between seller and broker values
function calculateVariance(asset: any): number | null {
  const seller = asset.seller_asis_value
  const broker = asset.broker_asis_value
  if (!seller || !broker) return null
  return (broker - seller) / seller
}

// WHAT: Determine valuation status based on available data
// WHY: Show appropriate status tag for each asset's valuation completion
function getValuationStatus(asset: any): string {
  const hasSeller = asset.seller_asis_value != null
  const hasBPO = asset.additional_asis_value != null
  const hasBroker = asset.broker_asis_value != null
  const hasInternal = asset.internal_initial_uw_asis_value != null
  
  // WHAT: If all valuations complete, check for variance issues
  if (hasSeller && hasBPO && hasBroker && hasInternal) {
    const variance = calculateVariance(asset)
    if (variance && Math.abs(variance) > 0.1) return 'Review'
    return 'Approved'
  }
  
  // WHAT: Check what's missing and show the most critical pending item
  // WHY: Prioritize showing what's blocking progress
  if (!hasBPO) return 'Pending BPO'
  if (!hasBroker) return 'Pending Broker'
  if (!hasInternal) return 'Pending Reconciled'
  
  return 'In Progress'
}

// WHAT: Format currency display
function formatCurrency(val: number | null): string {
  if (val == null) return '-'
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val)
}

// WHAT: Format currency for input field (with $ symbol and commas)
// WHY: Display values in familiar currency format
// HOW: Accept any type and safely convert to number or null
function formatCurrencyForInput(val: any): string {
  const num = typeof val === 'number' ? val : null
  if (num == null) return ''
  return '$' + new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 }).format(num)
}

// WHAT: Format input field as user types (add $ and commas)
// WHY: Provide real-time feedback as users enter currency values
// HOW: Extract numeric value, format with currency, update input while preserving cursor position
function formatInputOnType(event: Event) {
  const input = event.target as HTMLInputElement
  
  // WHAT: Store cursor position and old value before formatting
  const oldValue = input.value
  const oldCursorPosition = input.selectionStart || 0
  
  // WHAT: Get raw numeric value from input (remove all non-digits)
  const rawValue = oldValue.replace(/[^0-9]/g, '')
  
  // WHAT: If empty, keep it empty
  if (!rawValue) {
    input.value = ''
    return
  }
  
  // WHAT: Parse to number and format with $ and commas
  const numValue = parseInt(rawValue, 10)
  const formatted = '$' + new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 }).format(numValue)
  
  // WHAT: Only update if the formatted value is different
  if (oldValue === formatted) {
    return
  }
  
  // WHAT: Calculate cursor position adjustment
  // WHY: Account for added $ and comma characters
  const digitsBeforeCursor = oldValue.substring(0, oldCursorPosition).replace(/[^0-9]/g, '').length
  
  // WHAT: Find where those digits are in the new formatted string
  let newCursorPosition = 0
  let digitCount = 0
  for (let i = 0; i < formatted.length; i++) {
    if (/[0-9]/.test(formatted[i])) {
      digitCount++
      if (digitCount >= digitsBeforeCursor) {
        newCursorPosition = i + 1
        break
      }
    }
  }
  
  // WHAT: Update value and restore cursor
  input.value = formatted
  input.setSelectionRange(newCursorPosition, newCursorPosition)
}

// WHAT: Format percentage display
function formatPercent(val: number | null): string {
  if (val == null) return '-'
  return `${(val * 100).toFixed(1)}%`
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

// WHAT: Get current grade for Internal UW valuation
// WHY: Display current grade in dropdown
// HOW: Extract from asset data returned by serializer
function getInternalUWGrade(asset: any): string {
  return asset.internal_initial_uw_grade || ''
}

// WHAT: Handle save grade event
// WHY: Emit to parent component to handle actual save logic
function handleSaveGrade(asset: any, gradeCode: string) {
  emit('saveGrade', asset, gradeCode)
}

// WHAT: Handle save internal UW event
// WHY: Emit to parent component to handle actual save logic
function handleSaveInternalUW(asset: any, field: 'asis' | 'arv', event: Event) {
  emit('saveInternalUW', asset, field, event)
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

// WHAT: Generate Zillow search URL
function getZillowUrl(asset: any): string {
  const address = formatAddress(asset)
  const cityState = formatCityState(asset)
  const query = encodeURIComponent(`${address} ${cityState}`)
  return `https://www.zillow.com/homes/${query}`
}

// WHAT: Generate Redfin search URL  
function getRedfinUrl(asset: any): string {
  const address = formatAddress(asset)
  const cityState = formatCityState(asset)
  const query = encodeURIComponent(`${address} ${cityState}`)
  return `https://www.redfin.com/search?query=${query}`
}

// WHAT: Generate Realtor.com search URL
function getRealtorUrl(asset: any): string {
  const address = formatAddress(asset)
  const cityState = formatCityState(asset)
  const query = encodeURIComponent(`${address} ${cityState}`)
  return `https://www.realtor.com/realestateandhomes-search/${query}`
}

// WHAT: CSS class for status badge
// WHY: Color-code different status states for quick visual identification
function statusBadgeClass(status: string): string {
  switch (status) {
    case 'Approved': return 'bg-success'
    case 'Review': return 'bg-warning'
    case 'In Progress': return 'bg-info'
    case 'Pending BPO': return 'bg-secondary'
    case 'Pending Broker': return 'bg-secondary'
    case 'Pending UW': return 'bg-secondary'
    case 'Pending Reconciled': return 'bg-warning'
    default: return 'bg-secondary'
  }
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

.third-party-link {
  color: #3577f1;
  text-decoration: none;
  white-space: nowrap;
}

.third-party-link:hover {
  text-decoration: underline;
}

/* WHAT: Editable inline input fields styled in blue to indicate user can edit */
/* WHY: Visual indicator that these values are editable by the user */
.editable-value-inline {
  border: none;
  background: transparent;
  text-align: center;
  width: 100px;
  padding: 2px 4px;
  font-size: inherit;
  color: #3577f1;
  font-weight: 500;
  cursor: pointer;
}

/* WHAT: Blue italicized placeholder text for editable inputs */
/* WHY: Consistent blue styling to indicate this field is user-editable */
.editable-value-inline::placeholder {
  color: #3577f1;
  opacity: 0.7;
  font-style: italic;
}

.editable-value-inline:hover {
  background-color: #e7f1ff;
  border: 1px solid #3577f1;
  border-radius: 3px;
}

.editable-value-inline:focus {
  outline: none;
  background-color: #fff;
  border: 1px solid #3577f1;
  border-radius: 3px;
  color: #3577f1;
}

.grade-select {
  width: auto;
  min-width: 70px;
  display: inline-block;
}
</style>

