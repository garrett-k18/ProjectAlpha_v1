<template>
  <!-- WHAT: Modal for assigning brokers to assets and sending invitations -->
  <!-- WHY: Centralized broker assignment workflow for trade management -->
  <!-- HOW: Uses AssetFilters component for consistent filtering UX -->
  <div>
    <h5 class="mb-3">Broker Assignments</h5>
    
    <!-- WHAT: Reusable AssetFilters component -->
    <!-- WHY: Consistent filtering experience across all asset views -->
    <AssetFilters
      :config="filterConfig"
      :available-states="availableStates"
      :available-msas="availableMsas"
      :available-counties="availableCounties"
      :total-rows="totalRows"
      :filtered-rows="filteredRows.length"
      @filter-change="handleFilterChange"
      @clear-filters="handleClearFilters"
    />
    
    <!-- WHAT: Assignment Actions Bar -->
    <!-- WHY: Provide bulk actions for broker assignments -->
    <div class="d-flex justify-content-between align-items-center mb-3">
      <div class="d-flex gap-2 align-items-center">
        <select 
          v-model="bulkBrokerId" 
          class="form-select form-select-sm"
          style="width: 250px;"
        >
          <option :value="null">Select broker for bulk action...</option>
          <option v-for="broker in brokers" :key="broker.id" :value="broker.id">
            {{ broker.name || broker.firm || `Broker ${broker.id}` }}
          </option>
        </select>
        <button 
          class="btn btn-sm btn-primary"
          :disabled="!bulkBrokerId || selectedAssets.length === 0 || assigningBrokers"
          @click="assignBulkBroker"
        >
          <i class="ri-user-add-line me-1"></i>
          Assign to {{ selectedAssets.length }} Selected
        </button>
        <button 
          class="btn btn-sm btn-success"
          :disabled="selectedAssets.length === 0 || sendingInvitations"
          @click="sendBulkInvitations"
        >
          <i class="ri-mail-send-line me-1"></i>
          Send Invitations ({{ selectedAssets.length }})
        </button>
      </div>
      <div class="text-muted small">
        {{ selectedAssets.length }} asset(s) selected
      </div>
    </div>
    
    <!-- WHAT: MSA grouping cards to accelerate market-level broker assignments -->
    <div v-if="msaGroups.length" class="card border-0 shadow-sm mb-3">
      <div class="card-body">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <div>
            <h6 class="mb-1">MSA Grouping</h6>
            <p class="text-muted small mb-0">
              Linked via ZIPReference crosswalk so you can bulk-assign local brokers quickly.
            </p>
          </div>
          <span class="badge bg-primary-subtle text-primary">
            {{ msaGroups.length }} market{{ msaGroups.length === 1 ? '' : 's' }}
          </span>
        </div>
        <div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-3">
          <div class="col" v-for="group in msaGroups" :key="group.key">
            <div class="h-100 border rounded-3 p-3 bg-light-subtle d-flex flex-column">
              <div class="d-flex justify-content-between align-items-start mb-2">
                <div>
                  <div class="fw-semibold">{{ group.displayName }}</div>
                  <div v-if="group.stateLabel" class="text-muted small">
                    {{ group.stateLabel }}
                  </div>
                  <div v-else class="text-warning small fw-semibold">Unmatched geography</div>
                </div>
                <span class="badge bg-secondary-subtle text-secondary">
                  {{ group.assetCount }} {{ group.assetCount === 1 ? 'asset' : 'assets' }}
                </span>
              </div>
              <div class="text-muted small mb-3">
                <template v-if="group.counties.length">
                  Counties:
                  {{ group.counties.slice(0, 2).join(', ') }}
                  <span v-if="group.counties.length > 2">
                    +{{ group.counties.length - 2 }}
                  </span>
                </template>
                <span v-else>No county match</span>
              </div>
              <div class="mt-auto d-flex gap-2">
                <button class="btn btn-sm btn-outline-primary flex-fill" @click="selectGroup(group)">
                  Select Group
                </button>
                <button
                  class="btn btn-sm btn-primary flex-fill"
                  :disabled="!bulkBrokerId || assigningBrokers"
                  @click="assignGroupBroker(group)"
                >
                  Assign
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- WHAT: Broker Assignment Table -->
    <!-- WHY: Display assets with broker assignment controls -->
    <div class="table-responsive">
      <table class="table table-centered table-hover table-sm mb-0">
        <thead class="table-light">
          <tr>
            <th style="width: 40px;">
              <!-- WHAT: Select all checkbox -->
              <!-- WHY: Enable bulk actions on all visible assets -->
              <input 
                type="checkbox" 
                class="form-check-input"
                :checked="allVisibleSelected"
                @change="toggleSelectAll"
              />
            </th>
            <th>Loan #</th>
            <th>Address</th>
            <th>County</th>
            <th>MSA</th>
            <th>Assigned Broker</th>
            <th class="text-center" style="width: 150px;">Actions</th>
          </tr>
        </thead>
        <tbody>
          <!-- WHAT: Loading state -->
          <!-- WHY: Provide feedback while fetching data -->
          <tr v-if="loading">
            <td colspan="7" class="text-center py-4">
              <div class="spinner-border spinner-border-sm text-primary me-2" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
              Loading assets...
            </td>
          </tr>
          
          <!-- WHAT: Empty state -->
          <!-- WHY: Clear messaging when no data available -->
          <tr v-else-if="!paginatedRows || paginatedRows.length === 0">
            <td colspan="7" class="text-center text-muted py-3">
              <span v-if="hasActiveFilters">
                No assets match your filters
              </span>
              <span v-else>
                No assets to display
              </span>
            </td>
          </tr>
          
          <!-- WHAT: Asset rows with broker assignment controls -->
          <!-- WHY: Allow per-asset broker assignment and invitation -->
          <tr v-for="(asset, index) in paginatedRows" :key="`asset-${asset?.asset_hub_id || asset?.id || index}`">
            <!-- WHAT: Row selection checkbox -->
            <!-- WHY: Enable bulk actions on selected rows -->
            <td>
              <input 
                type="checkbox" 
                class="form-check-input"
                :checked="isAssetSelected(asset)"
                @change="toggleAssetSelection(asset)"
              />
            </td>
            
            <!-- WHAT: Loan Number (clickable) -->
            <!-- WHY: Primary identifier, opens loan modal -->
            <td>
              <div class="loan-number-link" @click="emit('openLoanModal', asset)">
                {{ asset.sellertape_id || asset.seller_loan_id || '-' }}
              </div>
            </td>
            
            <!-- WHAT: Address (clickable) -->
            <!-- WHY: Visual identifier, opens loan modal -->
            <td>
              <div class="address-link" @click="emit('openLoanModal', asset)">
                <div class="fw-semibold">{{ formatAddress(asset) }}</div>
                <div class="small text-muted">{{ formatCityState(asset) }}</div>
              </div>
            </td>
            
            <!-- WHAT: County -->
            <!-- WHY: Geographic information for broker assignment decisions -->
            <td>
              <span class="text-muted">{{ asset.county || '-' }}</span>
            </td>
            
            <!-- WHAT: MSA (Metropolitan Statistical Area) -->
            <!-- WHY: Market-level information for broker assignment -->
            <td>
              <span class="text-muted small">{{ asset.msa || '-' }}</span>
            </td>
            
            <!-- WHAT: Broker Assignment Dropdown -->
            <!-- WHY: Allow selecting broker for this asset -->
            <td>
              <select 
                class="form-select form-select-sm"
                :value="getAssetBrokerId(asset)"
                @change="(e) => handleBrokerAssignment(asset, (e.target as HTMLSelectElement).value)"
                :disabled="assigningBrokers"
              >
                <option :value="null">Assign broker...</option>
                <option v-for="broker in brokers" :key="broker.id" :value="broker.id">
                  {{ broker.name || broker.firm || `Broker ${broker.id}` }}
                </option>
              </select>
            </td>
            
            <!-- WHAT: Action buttons per row -->
            <!-- WHY: Quick actions for individual assets -->
            <td class="text-center">
              <button 
                class="btn btn-sm btn-light me-1" 
                @click="emit('openLoanModal', asset)"
                title="View Details"
              >
                <i class="ri-eye-line"></i>
              </button>
              <button 
                class="btn btn-sm btn-success" 
                @click="sendInvitation(asset)"
                :disabled="!getAssetBrokerId(asset) || sendingInvitations"
                title="Send Broker Invitation"
              >
                <i class="ri-mail-send-line"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- WHAT: Pagination Controls -->
    <!-- WHY: Navigate through large datasets -->
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
// WHAT: Vue composition imports for reactive state management
// WHY: Enable reactive filtering, pagination, and broker assignments
import { ref, computed, onMounted, watch } from 'vue'
// WHAT: Pinia store for accessing brokers from CRM
// WHY: Centralized broker data management
import { useBrokersCrmStore } from '@/stores/brokerscrm'
import { storeToRefs } from 'pinia'
// WHAT: HTTP client for API calls
// WHY: Assign brokers and send invitations via backend
import http from '@/lib/http'
// WHAT: Reusable filter component
// WHY: Consistent filtering UX across all asset views
import AssetFilters from '@/components/custom/AssetFilters.vue'
import type { FilterValues } from '@/components/custom/AssetFilters.vue'

// WHAT: Props from parent component
// WHY: Receive asset data to display and manage
const props = defineProps<{
  rows: any[] | null
  selectedSellerId: number | null
  selectedTradeId: number | null
}>()

// WHAT: Event emitters for parent communication
// WHY: Notify parent of modal actions (loan viewing)
const emit = defineEmits<{
  openLoanModal: [asset: any]
}>()

// WHAT: Broker store instance
// WHY: Access broker list from CRM for dropdown
const brokerStore = useBrokersCrmStore()
const { results: brokers, loading: brokersLoading } = storeToRefs(brokerStore)

// WHAT: Pagination state
// WHY: Control page display and navigation
const currentPage = ref(1)
const pageSize = ref(50)

// WHAT: Data structure describing grouped MSAs
interface MsaGroup {
  key: string
  code: string | null
  name: string | null
  state: string | null
  stateLabel: string | null
  displayName: string
  counties: string[]
  assets: any[]
  assetCount: number
}

// WHAT: Filter state from AssetFilters component
// WHY: Apply user-selected filters to asset list
const filters = ref<FilterValues>({
  search: '',
  state: '',
  grade: '',
  valueSource: 'seller',
  valueOperator: '>',
  valueAmount: null,
  msa: '',
  county: '',
})

// WHAT: Selection state for bulk actions
// WHY: Track which assets are selected for bulk broker assignment
const selectedAssets = ref<any[]>([])

// WHAT: Broker assignment state
// WHY: Track bulk broker selection and loading states
const bulkBrokerId = ref<number | null>(null)
const assigningBrokers = ref(false)
const sendingInvitations = ref(false)

// WHAT: Loading state
// WHY: Show loading indicator while fetching data
const loading = computed(() => brokersLoading.value)

// WHAT: Filter configuration for AssetFilters component
// WHY: Define which filters to show for broker assignment workflow
const filterConfig = computed(() => ({
  showSearch: true,
  showState: true,
  showGrade: true,
  showMsa: true,
  showCounty: true,
  showValueSource: false, // Not needed for broker assignment
  showValueOperator: false, // Not needed for broker assignment
  showValueAmount: false, // Not needed for broker assignment
  showResultsCount: true,
  searchLabel: 'Search',
  searchPlaceholder: 'Search by loan #, address, city, county, MSA...',
}))

// WHAT: Extract unique values for filter dropdowns
// WHY: Populate filter options dynamically from data
const availableStates = computed(() => {
  const states = new Set<string>()
  if (props.rows) {
    props.rows.forEach((row: any) => {
      if (row.state) states.add(row.state)
    })
  }
  return Array.from(states).sort()
})

const availableMsas = computed(() => {
  const msas = new Set<string>()
  if (props.rows) {
    props.rows.forEach((row: any) => {
      if (row.msa) msas.add(row.msa)
    })
  }
  return Array.from(msas).sort()
})

const availableCounties = computed(() => {
  const counties = new Set<string>()
  if (props.rows) {
    props.rows.forEach((row: any) => {
      if (row.county) counties.add(row.county)
    })
  }
  return Array.from(counties).sort()
})

// WHAT: Total rows count
// WHY: Display to user in filter results
const totalRows = computed(() => props.rows?.length || 0)

// WHAT: Check if any filters are active
// WHY: Determine if empty state should show "no matches" or "no data"
const hasActiveFilters = computed(() => 
  filters.value.search || 
  filters.value.state || 
  filters.value.grade ||
  filters.value.msa ||
  filters.value.county
)

// WHAT: Apply filters to rows
// WHY: Show only assets matching user's filter criteria
const filteredRows = computed(() => {
  if (!props.rows) return []
  
  let filtered = props.rows
  
  // WHAT: Apply search filter (loan number, address, city, county, MSA)
  // WHY: Allow flexible text-based searching
  if (filters.value.search) {
    const searchTerm = filters.value.search.toLowerCase()
    filtered = filtered.filter((row: any) => 
      (row.sellertape_id || '').toLowerCase().includes(searchTerm) ||
      (row.seller_loan_id || '').toLowerCase().includes(searchTerm) ||
      (row.street_address || '').toLowerCase().includes(searchTerm) ||
      (row.city || '').toLowerCase().includes(searchTerm) ||
      (row.county || '').toLowerCase().includes(searchTerm) ||
      (row.msa || '').toLowerCase().includes(searchTerm)
    )
  }
  
  // WHAT: Apply state filter
  if (filters.value.state) {
    filtered = filtered.filter((row: any) => row.state === filters.value.state)
  }
  
  // WHAT: Apply MSA filter
  if (filters.value.msa) {
    filtered = filtered.filter((row: any) => row.msa === filters.value.msa)
  }
  
  // WHAT: Apply county filter
  if (filters.value.county) {
    filtered = filtered.filter((row: any) => row.county === filters.value.county)
  }
  
  // WHAT: Apply grade filter
  // WHY: Allow viewing assets by internal UW grade
  if (filters.value.grade) {
    if (filters.value.grade === 'none') {
      filtered = filtered.filter((row: any) => !row.internal_initial_uw_grade)
    } else {
      filtered = filtered.filter((row: any) => row.internal_initial_uw_grade === filters.value.grade)
    }
  }
  
  return filtered
})

// WHAT: Group filtered assets by MSA for fast assignment
const msaGroups = computed<MsaGroup[]>(() => {
  const map = new Map<string, {
    key: string
    code: string | null
    name: string | null
    state: string | null
    countySet: Set<string>
    assets: any[]
  }>()
  
  filteredRows.value.forEach((asset: any) => {
    const code: string | null = asset.msa_code || null
    const name: string | null = asset.msa || asset.msa_name || null
    const state: string | null = asset.msa_state || asset.state || null
    const key = code ? `code:${code}` : name ? `name:${name.toLowerCase()}` : 'unmatched'
    const countyName: string | null = asset.county || null
    if (!map.has(key)) {
      map.set(key, {
        key,
        code,
        name,
        state,
        countySet: countyName ? new Set([countyName]) : new Set(),
        assets: [asset],
      })
    } else {
      const entry = map.get(key)!
      entry.assets.push(asset)
      if (countyName) {
        entry.countySet.add(countyName)
      }
      if (!entry.name && name) entry.name = name
      if (!entry.code && code) entry.code = code
      if (!entry.state && state) entry.state = state
    }
  })
  
  return Array.from(map.values())
    .map((entry) => {
      const displayName = entry.name || (entry.code ? `MSA ${entry.code}` : 'No MSA match')
      const stateLabel = entry.state ? entry.state : null
      return {
        key: entry.key,
        code: entry.code,
        name: entry.name,
        state: entry.state,
        stateLabel,
        displayName,
        counties: Array.from(entry.countySet),
        assets: entry.assets,
        assetCount: entry.assets.length,
      }
    })
    .sort((a, b) => b.assetCount - a.assetCount)
})

// WHAT: Total number of pages
// WHY: Calculate pagination controls
const totalPages = computed(() => Math.ceil(filteredRows.value.length / pageSize.value) || 1)

// WHAT: Visible page numbers for pagination (show 5 pages max)
// WHY: Keep pagination controls compact
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

// WHAT: Check if all visible assets are selected
// WHY: Determine state of "select all" checkbox
const allVisibleSelected = computed(() => {
  if (paginatedRows.value.length === 0) return false
  return paginatedRows.value.every(asset => isAssetSelected(asset))
})

// WHAT: Handle filter changes from AssetFilters component
// WHY: Update local filter state and reset pagination
function handleFilterChange(newFilters: FilterValues) {
  filters.value = { ...newFilters }
  currentPage.value = 1
}

// WHAT: Handle clear filters event
// WHY: Reset all filters to default state
function handleClearFilters() {
  filters.value = {
    search: '',
    state: '',
    grade: '',
    valueSource: 'seller',
    valueOperator: '>',
    valueAmount: null,
    msa: '',
    county: '',
  }
  currentPage.value = 1
}

// WHAT: Navigate to specific page
// WHY: User clicks pagination controls
function goToPage(page: number) {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

// WHAT: Check if asset is selected
// WHY: Determine checkbox state
function isAssetSelected(asset: any): boolean {
  const assetId = asset.asset_hub_id || asset.id
  return selectedAssets.value.some(a => (a.asset_hub_id || a.id) === assetId)
}

// WHAT: Toggle asset selection
// WHY: Add/remove asset from selection for bulk actions
function toggleAssetSelection(asset: any) {
  const assetId = asset.asset_hub_id || asset.id
  const index = selectedAssets.value.findIndex(a => (a.asset_hub_id || a.id) === assetId)
  
  if (index >= 0) {
    selectedAssets.value.splice(index, 1)
  } else {
    selectedAssets.value.push(asset)
  }
}

// WHAT: Toggle select all visible assets
// WHY: Enable bulk selection/deselection
function toggleSelectAll() {
  if (allVisibleSelected.value) {
    // Deselect all visible
    paginatedRows.value.forEach(asset => {
      const assetId = asset.asset_hub_id || asset.id
      const index = selectedAssets.value.findIndex(a => (a.asset_hub_id || a.id) === assetId)
      if (index >= 0) {
        selectedAssets.value.splice(index, 1)
      }
    })
  } else {
    // Select all visible
    paginatedRows.value.forEach(asset => {
      if (!isAssetSelected(asset)) {
        selectedAssets.value.push(asset)
      }
    })
  }
}

// WHAT: Get currently assigned broker ID for asset
// WHY: Display in dropdown and determine if invitation can be sent
function getAssetBrokerId(asset: any): number | null {
  // WHAT: Check for broker assignment in asset data
  // TODO: Update this based on actual backend field name
  return asset.assigned_broker_id || asset.broker_id || null
}

// WHAT: Handle broker assignment for single asset
// WHY: Allow per-asset broker assignment
async function handleBrokerAssignment(asset: any, brokerIdStr: string) {
  const brokerId = brokerIdStr ? parseInt(brokerIdStr, 10) : null
  if (!brokerId) {
    asset.assigned_broker_id = null
    return
  }
  
  assigningBrokers.value = true
  
  try {
    await persistBrokerAssignments([asset], brokerId)
    console.log(`[BrokerAssignment] Assigned broker ${brokerId} to asset ${asset.asset_hub_id || asset.id}`)
  } catch (e) {
    console.error('[BrokerAssignment] Failed to assign broker:', e)
    alert('Failed to assign broker. Please try again.')
  } finally {
    assigningBrokers.value = false
  }
}

// WHAT: Assign bulk broker to selected assets
// WHY: Enable efficient bulk broker assignment
async function assignBulkBroker() {
  if (!bulkBrokerId.value || selectedAssets.value.length === 0) return
  
  assigningBrokers.value = true
  
  try {
    await persistBrokerAssignments(selectedAssets.value, bulkBrokerId.value)
    
    console.log(`[BrokerAssignment] Bulk assigned broker ${bulkBrokerId.value} to ${selectedAssets.value.length} assets`)
    
    // WHAT: Clear selections after successful assignment
    selectedAssets.value = []
    bulkBrokerId.value = null
  } catch (e) {
    console.error('[BrokerAssignment] Failed to assign bulk broker:', e)
    alert('Failed to assign broker to some assets. Please try again.')
  } finally {
    assigningBrokers.value = false
  }
}

async function assignGroupBroker(group: MsaGroup) {
  if (!bulkBrokerId.value) {
    alert('Select a broker in the bulk action bar before assigning a group.')
    return
  }
  if (!group.assets.length) return
  
  assigningBrokers.value = true
  try {
    await persistBrokerAssignments(group.assets, bulkBrokerId.value)
    console.log(`[BrokerAssignment] Assigned broker ${bulkBrokerId.value} to MSA group ${group.displayName}`)
  } catch (e) {
    console.error('[BrokerAssignment] Failed to assign broker to group:', e)
    alert('Failed to assign broker to this MSA group. Please try again.')
  } finally {
    assigningBrokers.value = false
  }
}

async function persistBrokerAssignments(targetAssets: any[], brokerId: number) {
  const assetHubIds = targetAssets
    .map(asset => asset.asset_hub_id || asset.id)
    .filter((id): id is number => Boolean(id))
  
  if (!assetHubIds.length) {
    console.warn('[BrokerAssignment] No asset IDs found for assignment batch.')
    return
  }
  
  await http.post('/acq/broker-portal/assign/', {
    broker_id: brokerId,
    asset_hub_ids: assetHubIds,
  })
  
  targetAssets.forEach(asset => {
    asset.assigned_broker_id = brokerId
  })
}

function selectGroup(group: MsaGroup) {
  group.assets.forEach(asset => {
    if (!isAssetSelected(asset)) {
      selectedAssets.value.push(asset)
    }
  })
}

// WHAT: Send invitation to single asset's assigned broker
// WHY: Notify broker of assignment
async function sendInvitation(asset: any) {
  const brokerId = getAssetBrokerId(asset)
  if (!brokerId) {
    alert('Please assign a broker before sending invitation.')
    return
  }
  
  const assetHubId = asset.asset_hub_id || asset.id
  if (!assetHubId) {
    console.error('[BrokerAssignment] No asset ID found')
    return
  }
  
  sendingInvitations.value = true
  
  try {
    // WHAT: Call backend API to send broker invitation email
    // WHY: Notify broker of assignment via email
    // TODO: Update endpoint based on actual backend route
    await http.post(`/acq/assets/${assetHubId}/send-broker-invitation/`, {
      broker_id: brokerId,
    })
    
    console.log(`[BrokerAssignment] Sent invitation for asset ${assetHubId} to broker ${brokerId}`)
    alert('Invitation sent successfully!')
  } catch (e) {
    console.error('[BrokerAssignment] Failed to send invitation:', e)
    alert('Failed to send invitation. Please try again.')
  } finally {
    sendingInvitations.value = false
  }
}

// WHAT: Send invitations to all selected assets' brokers
// WHY: Enable bulk invitation sending
async function sendBulkInvitations() {
  if (selectedAssets.value.length === 0) return
  
  // WHAT: Filter assets that have assigned brokers
  // WHY: Can only send invitations to assets with brokers
  const assetsWithBrokers = selectedAssets.value.filter(asset => getAssetBrokerId(asset))
  
  if (assetsWithBrokers.length === 0) {
    alert('None of the selected assets have assigned brokers.')
    return
  }
  
  sendingInvitations.value = true
  
  try {
    // WHAT: Send invitation for each asset with assigned broker
    const promises = assetsWithBrokers.map(asset => {
      const assetHubId = asset.asset_hub_id || asset.id
      const brokerId = getAssetBrokerId(asset)
      return http.post(`/acq/assets/${assetHubId}/send-broker-invitation/`, {
        broker_id: brokerId,
      })
    })
    
    await Promise.all(promises)
    
    console.log(`[BrokerAssignment] Sent ${assetsWithBrokers.length} bulk invitations`)
    alert(`Successfully sent ${assetsWithBrokers.length} invitation(s)!`)
    
    // WHAT: Clear selections after successful send
    selectedAssets.value = []
  } catch (e) {
    console.error('[BrokerAssignment] Failed to send bulk invitations:', e)
    alert('Failed to send some invitations. Please try again.')
  } finally {
    sendingInvitations.value = false
  }
}

// WHAT: Format full address from asset data
// WHY: Display readable address
function formatAddress(asset: any): string {
  return asset.street_address || asset.property_address || asset.address || '-'
}

// WHAT: Format city and state
// WHY: Display location information
function formatCityState(asset: any): string {
  const city = asset.city || asset.property_city || ''
  const state = asset.state || asset.property_state || ''
  return [city, state].filter(Boolean).join(', ') || '-'
}

// WHAT: Load brokers on component mount
// WHY: Populate broker dropdown options
onMounted(async () => {
  try {
    await brokerStore.fetchBrokers({ page: 1, pageSize: 1000 })
  } catch (e) {
    console.error('[BrokerAssignment] Failed to load brokers:', e)
  }
})

// WHAT: Watch for trade changes and clear selections
// WHY: Reset state when switching trades
watch(() => props.selectedTradeId, () => {
  selectedAssets.value = []
  currentPage.value = 1
})
</script>

<style scoped>
/* WHAT: Loan number styling - clickable link */
/* WHY: Indicate interactivity to user */
.loan-number-link {
  cursor: pointer;
  color: #3577f1;
  font-weight: 600;
}

.loan-number-link:hover {
  text-decoration: underline;
}

/* WHAT: Address styling - clickable link */
/* WHY: Make addresses interactive */
.address-link {
  cursor: pointer;
  color: #3577f1;
}

.address-link:hover {
  text-decoration: underline;
}
</style>

