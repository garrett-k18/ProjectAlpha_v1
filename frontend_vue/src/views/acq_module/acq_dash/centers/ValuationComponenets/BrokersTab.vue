<template>
  <div>
    <h5 class="mb-3">Broker Valuations</h5>
    
    <!-- WHAT: Advanced Filters Section -->
    <!-- WHY: Allow users to filter broker valuations by state, city, value ranges, grade -->
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
    
    <!-- WHAT: Brokers Table with consistent styling -->
    <!-- WHY: Match OverviewTab table design for consistency, show broker valuation data -->
    <div class="table-responsive">
      <table class="table table-centered table-hover mb-0">
        <thead class="table-light">
          <tr>
            <th>Loan #</th>
            <th>Address</th>
            <th class="text-center" style="width: 250px;">Assigned Broker</th>
            <th class="text-center">Grade</th>
            <th class="text-center">Broker AIV</th>
            <th class="text-center">Broker ARV</th>
            <th class="text-center">Est. Rehab</th>
            <th class="text-center">Recommend Rehab</th>
            <th class="text-center">Notes</th>
            <th class="text-center">Links</th>
            <th class="text-center">Inspection Report</th>
          </tr>
        </thead>
        <tbody>
          <!-- WHAT: Empty state row when no data or no filtered results -->
          <tr v-if="!filteredRows || filteredRows.length === 0">
            <td colspan="11" class="text-center text-muted py-3">
              <span v-if="filters.search || filters.state || filters.valueAmount || filters.grade">
                No assets match your filters
              </span>
              <span v-else>
                No assets to display
              </span>
            </td>
          </tr>
          <!-- WHAT: Asset row with clickable address, broker assignment, and broker valuations -->
          <!-- WHY: Allow users to click address, assign brokers, and view broker-provided values -->
          <tr v-for="(asset, index) in paginatedRows" :key="`broker-asset-${asset?.asset_hub_id || asset?.id || index}`">
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
            <!-- WHAT: Broker assignment dropdown -->
            <!-- WHY: Allow users to assign brokers from CRM to individual assets -->
            <td class="text-center">
              <select 
                class="form-select form-select-sm broker-dropdown"
                :value="getAssignedBrokerId(asset)"
                @change="(e) => assignBroker(asset, e)"
                :disabled="brokersLoading"
              >
                <option value="">-- Select Broker --</option>
                <option 
                  v-for="broker in brokers" 
                  :key="broker.id" 
                  :value="broker.id"
                >
                  {{ broker.contact_name || broker.firm || broker.email || `Broker #${broker.id}` }}
                </option>
              </select>
            </td>
            <!-- WHAT: Broker valuation grade -->
            <!-- WHY: Display grade assigned to broker valuation -->
            <td class="text-center">
              <span v-if="asset.broker_grade" :class="getGradeBadgeClass(asset.broker_grade)">
                {{ asset.broker_grade }}
              </span>
              <span v-else class="text-muted">-</span>
            </td>
            <!-- WHAT: Broker As-Is value (read-only from broker portal) -->
            <!-- WHY: Display broker-provided as-is valuation -->
            <td class="text-center">
              <span class="read-only-value">{{ formatCurrency(asset.broker_asis_value) }}</span>
            </td>
            <!-- WHAT: Broker ARV value (read-only from broker portal) -->
            <!-- WHY: Display broker-provided after-repair value -->
            <td class="text-center">
              <span class="read-only-value">{{ formatCurrency(asset.broker_arv_value) }}</span>
            </td>
            <!-- WHAT: Broker estimated rehab (read-only from broker portal) -->
            <!-- WHY: Display broker-provided rehab estimate -->
            <td class="text-center">
              <span class="read-only-value">{{ formatCurrency(asset.broker_rehab_est) }}</span>
            </td>
            <!-- WHAT: Rehab recommendation flag -->
            <!-- WHY: Show if broker recommends rehabilitation -->
            <td class="text-center">
              <span v-if="asset.broker_recommend_rehab" class="badge bg-warning">Yes</span>
              <span v-else class="badge bg-secondary">No</span>
            </td>
            <!-- WHAT: Broker notes column with 2-line display -->
            <!-- WHY: Display broker notes in table with 2-line wrapping for better readability -->
            <td class="notes-column text-center">
              <div v-if="asset.broker_notes" :title="asset.broker_notes">
                {{ asset.broker_notes }}
              </div>
              <span v-else class="text-muted">-</span>
            </td>
            <!-- WHAT: External links column -->
            <!-- WHY: Provide quick access to broker-provided external documentation -->
            <td class="text-center">
              <a 
                v-if="asset.broker_links" 
                :href="asset.broker_links" 
                target="_blank" 
                class="btn btn-sm btn-outline-secondary"
                @click.stop
              >
                <i class="ri-external-link-line"></i>
              </a>
              <span v-else class="text-muted">-</span>
            </td>
            <!-- WHAT: Inspection report button -->
            <!-- WHY: Open modal to view detailed rehab breakdown -->
            <td class="text-center">
              <button 
                class="btn btn-sm btn-outline-primary"
                @click="openInspectionModal(asset)"
                :disabled="!hasDetailedRehab(asset)"
              >
                <i class="ri-file-text-line me-1"></i>View
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

    <!-- WHAT: Detailed Rehab Breakdown Modal (using shared component) -->
    <!-- WHY: Display itemized rehab estimates from broker inspection -->
    <div v-if="showInspectionModal" class="modal fade show d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="ri-hammer-line me-2"></i>Detailed Rehab Breakdown
            </h5>
            <button type="button" class="btn-close" @click="closeInspectionModal"></button>
          </div>
          <div class="modal-body">
            <DetailedRehabBreakdown 
              v-if="selectedInspectionAsset"
              :asset="selectedInspectionAsset" 
              :editable="false"
              :showHeader="true"
              :showTotal="true"
            />
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeInspectionModal">Close</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import http from '@/lib/http'
import DetailedRehabBreakdown from '@/components/property_tabs_components/DetailedRehabBreakdown.vue'

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
  
  // WHAT: Apply value filter with operator (filters broker_asis_value)
  // WHY: Allow flexible value filtering with different operators
  if (filters.value.valueAmount != null && filters.value.valueAmount > 0) {
    filtered = filtered.filter((row: any) => {
      const value = row.broker_asis_value
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

// WHAT: Brokers list for dropdown
// WHY: Allow users to assign brokers from CRM to assets
const brokers = ref<any[]>([])
const brokersLoading = ref(false)

// WHAT: Fetch brokers from API
// WHY: Populate dropdown with available brokers
async function fetchBrokers() {
  brokersLoading.value = true
  try {
    // WHAT: Fetch brokers from CRM API (baseURL already includes /api prefix)
    const response = await http.get('/core/crm/brokers/', { params: { page_size: 1000 } })
    brokers.value = response.data.results || []
  } catch (error) {
    console.error('Failed to fetch brokers:', error)
    brokers.value = []
  } finally {
    brokersLoading.value = false
  }
}

// WHAT: Assign broker to asset
// WHY: User selects broker from dropdown
async function assignBroker(asset: any, event: Event) {
  const select = event.target as HTMLSelectElement
  const brokerId = select.value ? parseInt(select.value) : null
  const assetHubId = asset.asset_hub_id || asset.id
  
  if (!assetHubId) {
    console.error('No asset hub ID found')
    return
  }
  
  try {
    // WHAT: Update the broker_contact on the broker valuation for this asset
    // WHY: Link the selected broker to this asset's broker valuation
    await http.put(`/acq/valuations/internal/${assetHubId}/`, {
      broker_contact_id: brokerId
    }, {
      params: { source: 'broker' }
    })
    
    // WHAT: Refresh the asset data to show updated broker assignment
    // TODO: In future, could update local state instead of refetching
    console.log('Broker assigned successfully')
  } catch (error) {
    console.error('Failed to assign broker:', error)
    // Revert the dropdown to previous value on error
    select.value = asset.broker_contact_id || ''
  }
}

// WHAT: Get assigned broker ID for an asset
// WHY: Show correct broker in dropdown and persist selection after refresh
function getAssignedBrokerId(asset: any): string {
  // WHAT: Try multiple possible field names for broker assignment
  // WHY: Serializer may use broker_contact_id, broker_crm_id, or other naming
  // HOW: Check all possible field variations and return first non-null value
  const brokerId = asset.broker_contact_id || asset.broker_crm_id || asset.assigned_broker_id || asset.broker_id
  
  // WHAT: Log to help debug which field name is actually being used
  if (brokerId) {
    console.log('Found broker ID:', brokerId, 'for asset:', asset.asset_hub_id || asset.id)
  }
  
  return brokerId ? String(brokerId) : ''
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

// WHAT: Initialize component
onMounted(() => {
  fetchBrokers()
})

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

// WHAT: Format currency values for display
// WHY: Show broker valuation amounts in consistent currency format
function formatCurrency(val: number | null | undefined): string {
  if (val == null) return '-'
  return new Intl.NumberFormat('en-US', { 
    style: 'currency', 
    currency: 'USD', 
    maximumFractionDigits: 0 
  }).format(val)
}

// WHAT: Truncate text to specified length
// WHY: Keep table rows compact by limiting note display length
function truncateText(text: string, maxLength: number): string {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
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

// WHAT: Inspection modal state
// WHY: Control modal visibility and track selected asset for inspection
const showInspectionModal = ref(false)
const selectedInspectionAsset = ref<any>(null)

// WHAT: Open inspection modal for an asset
// WHY: Display broker notes, links, and detailed rehab breakdown
function openInspectionModal(asset: any) {
  selectedInspectionAsset.value = asset
  showInspectionModal.value = true
}

// WHAT: Close inspection modal
function closeInspectionModal() {
  showInspectionModal.value = false
  selectedInspectionAsset.value = null
}

// WHAT: Check if asset has detailed rehab breakdown
// WHY: Show rehab table only if at least one category has data, disable "View" button if no data
function hasDetailedRehab(asset: any): boolean {
  return !!(
    asset.broker_roof_est ||
    asset.broker_kitchen_est ||
    asset.broker_bath_est ||
    asset.broker_flooring_est ||
    asset.broker_windows_est ||
    asset.broker_appliances_est ||
    asset.broker_plumbing_est ||
    asset.broker_electrical_est ||
    asset.broker_landscaping_est
  )
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

/* WHAT: Broker dropdown styling */
/* WHY: Consistent sizing and appearance for broker assignment dropdown */
.broker-dropdown {
  min-width: 200px;
  max-width: 250px;
}

.broker-dropdown:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

/* WHAT: Read-only value styling for broker-provided data */
/* WHY: Display broker portal values in a clean, non-editable format */
.read-only-value {
  color: #495057;
  font-weight: 500;
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

