<template>
  <!-- WHAT: Reusable filter component for asset tables across the application -->
  <!-- WHY: Eliminates duplication and provides consistent filtering UX -->
  <!-- HOW: Accepts props to customize which filters are shown and emits filter changes to parent -->
  <div class="card bg-light border mb-3">
    <div class="card-body py-2">
      <div class="row g-2 align-items-end">
        <!-- Search Box (City or Loan Number) -->
        <!-- WHAT: Text search input for filtering by city, county, MSA, or loan number -->
        <!-- WHY: Allow quick searching by multiple common fields -->
        <div v-if="config.showSearch" :class="getColClass('search')">
          <label class="form-label small mb-1">{{ config.searchLabel || 'Search' }}</label>
          <input 
            v-model="localFilters.search" 
            type="text" 
            class="form-control form-control-sm" 
            :placeholder="config.searchPlaceholder || 'Search...'"
            @input="emitFilters"
          />
        </div>
        
        <!-- State Filter -->
        <!-- WHAT: Dropdown to filter assets by state -->
        <!-- WHY: Geographic filtering is common requirement -->
        <div v-if="config.showState" :class="getColClass('state')">
          <label class="form-label small mb-1">State</label>
          <select 
            v-model="localFilters.state" 
            class="form-select form-select-sm"
            @change="emitFilters"
          >
            <option value="">All States</option>
            <option v-for="state in availableStates" :key="state" :value="state">
              {{ state }}
            </option>
          </select>
        </div>
        
        <!-- Grade Filter -->
        <!-- WHAT: Dropdown to filter assets by internal UW grade -->
        <!-- WHY: Users need to focus on specific grade cohorts -->
        <div v-if="config.showGrade" :class="getColClass('grade')">
          <label class="form-label small mb-1">Grade</label>
          <select 
            v-model="localFilters.grade" 
            class="form-select form-select-sm"
            @change="emitFilters"
          >
            <option value="">All Grades</option>
            <option value="none">No Grade</option>
            <option v-for="grade in config.availableGrades || defaultGrades" :key="grade" :value="grade">
              {{ grade }}
            </option>
          </select>
        </div>
        
        <!-- Value Source Selector -->
        <!-- WHAT: Dropdown to choose which valuation source to filter by -->
        <!-- WHY: Different stakeholders focus on different valuation sources -->
        <div v-if="config.showValueSource" :class="getColClass('valueSource')">
          <label class="form-label small mb-1">Value Source</label>
          <select 
            v-model="localFilters.valueSource" 
            class="form-select form-select-sm"
            @change="emitFilters"
          >
            <option 
              v-for="option in config.valueSourceOptions || defaultValueSourceOptions" 
              :key="option.value" 
              :value="option.value"
            >
              {{ option.label }}
            </option>
          </select>
        </div>
        
        <!-- Value Operator -->
        <!-- WHAT: Dropdown to select comparison operator for value filtering -->
        <!-- WHY: Enable flexible numeric comparisons (greater than, less than, etc.) -->
        <div v-if="config.showValueOperator" :class="getColClass('valueOperator')">
          <label class="form-label small mb-1">Operator</label>
          <select 
            v-model="localFilters.valueOperator" 
            class="form-select form-select-sm"
            @change="emitFilters"
          >
            <option value=">">Greater Than</option>
            <option value="<">Less Than</option>
            <option value="=">Equal To</option>
            <option value=">=">Greater or Equal</option>
            <option value="<=">Less or Equal</option>
          </select>
        </div>
        
        <!-- Value Filter -->
        <!-- WHAT: Numeric input with auto-formatting for filtering by valuation amount -->
        <!-- WHY: Allow users to filter assets by value thresholds -->
        <div v-if="config.showValueAmount" :class="getColClass('valueAmount')">
          <label class="form-label small mb-1">Value</label>
          <input 
            type="text" 
            class="form-control form-control-sm" 
            :value="formatNumberWithCommas(localFilters.valueAmount)"
            @input="handleValueFilterInput"
            placeholder="Enter amount"
          />
        </div>
        
        <!-- MSA Filter (Optional) -->
        <!-- WHAT: Dropdown to filter assets by Metropolitan Statistical Area -->
        <!-- WHY: Market analysis often focuses on specific MSAs -->
        <div v-if="config.showMsa" :class="getColClass('msa')">
          <label class="form-label small mb-1">MSA</label>
          <select 
            v-model="localFilters.msa" 
            class="form-select form-select-sm"
            @change="emitFilters"
          >
            <option value="">All MSAs</option>
            <option v-for="msa in availableMsas" :key="msa" :value="msa">
              {{ msa }}
            </option>
          </select>
        </div>
        
        <!-- County Filter (Optional) -->
        <!-- WHAT: Dropdown to filter assets by county -->
        <!-- WHY: Regulatory and market conditions vary by county -->
        <div v-if="config.showCounty" :class="getColClass('county')">
          <label class="form-label small mb-1">County</label>
          <select 
            v-model="localFilters.county" 
            class="form-select form-select-sm"
            @change="emitFilters"
          >
            <option value="">All Counties</option>
            <option v-for="county in availableCounties" :key="county" :value="county">
              {{ county }}
            </option>
          </select>
        </div>
        
        <!-- Clear Filters Button -->
        <!-- WHAT: Button to reset all filters to default state -->
        <!-- WHY: Quick way to remove all filters and view full dataset -->
        <div :class="getColClass('clear')">
          <button 
            class="btn btn-sm btn-light w-100" 
            @click="clearAllFilters"
            title="Clear all filters"
          >
            <i class="ri-filter-off-line"></i>
          </button>
        </div>
      </div>
      
      <!-- Filter Results Count -->
      <!-- WHAT: Display count of filtered vs total rows -->
      <!-- WHY: Provide feedback on filter effectiveness -->
      <div v-if="config.showResultsCount" class="mt-2 small text-muted">
        {{ resultsCountText }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// WHAT: Vue composition imports for reactive state and computed properties
// WHY: Enables reactive filtering with automatic UI updates
import { ref, computed, watch } from 'vue'

// WHAT: Interface defining which filters to show and their configuration
// WHY: Makes component flexible and reusable across different contexts
export interface FilterConfig {
  showSearch?: boolean
  showState?: boolean
  showGrade?: boolean
  showValueSource?: boolean
  showValueOperator?: boolean
  showValueAmount?: boolean
  showMsa?: boolean
  showCounty?: boolean
  showResultsCount?: boolean
  searchLabel?: string
  searchPlaceholder?: string
  availableGrades?: string[]
  valueSourceOptions?: Array<{ value: string; label: string }>
  columnSizes?: {
    search?: string
    state?: string
    grade?: string
    valueSource?: string
    valueOperator?: string
    valueAmount?: string
    msa?: string
    county?: string
    clear?: string
  }
}

// WHAT: Interface for filter values emitted to parent
// WHY: Type safety and clear contract between component and parent
export interface FilterValues {
  search: string
  state: string
  grade: string
  valueSource: string
  valueOperator: string
  valueAmount: number | null
  msa: string
  county: string
}

// WHAT: Props passed from parent component
// WHY: Configure which filters to display and populate dropdown options
const props = withDefaults(defineProps<{
  config: FilterConfig
  availableStates?: string[]
  availableMsas?: string[]
  availableCounties?: string[]
  totalRows?: number
  filteredRows?: number
}>(), {
  availableStates: () => [],
  availableMsas: () => [],
  availableCounties: () => [],
  totalRows: 0,
  filteredRows: 0,
})

// WHAT: Event emitter for sending filter changes to parent
// WHY: Parent needs to know when filters change to update displayed data
const emit = defineEmits<{
  'filter-change': [filters: FilterValues]
  'clear-filters': []
}>()

// WHAT: Default grade options if not provided by parent
// WHY: Common grade scale used across real estate portfolios
const defaultGrades = ['A+', 'A', 'B', 'C', 'D', 'F']

// WHAT: Default valuation source options if not provided by parent
// WHY: Standard valuation sources in real estate acquisition workflows
const defaultValueSourceOptions = [
  { value: 'seller', label: 'Seller' },
  { value: 'bpo', label: 'BPO' },
  { value: 'broker', label: 'Broker' },
  { value: 'internal', label: 'Internal' },
]

// WHAT: Local reactive state for all filter values
// WHY: Track user selections and emit changes to parent
const localFilters = ref<FilterValues>({
  search: '',
  state: '',
  grade: '',
  valueSource: 'seller',
  valueOperator: '>',
  valueAmount: null,
  msa: '',
  county: '',
})

// WHAT: Computed property for results count text
// WHY: Display clear feedback about filtering results
const resultsCountText = computed(() => {
  const filtered = props.filteredRows
  const total = props.totalRows
  const hasActiveFilters = 
    localFilters.value.search || 
    localFilters.value.state || 
    localFilters.value.grade || 
    localFilters.value.valueAmount ||
    localFilters.value.msa ||
    localFilters.value.county
  
  if (hasActiveFilters && filtered < total) {
    return `Showing ${filtered} of ${total} assets (filtered from ${total} total)`
  }
  return `Showing ${filtered} assets`
})

// WHAT: Helper function to get responsive column classes
// WHY: Allow parent to customize column widths while providing sensible defaults
function getColClass(field: keyof FilterConfig['columnSizes']): string {
  const customSize = props.config.columnSizes?.[field]
  if (customSize) return customSize
  
  // WHAT: Default column sizes based on field type
  // WHY: Balance space utilization with readability
  const defaults: Record<string, string> = {
    search: 'col-md-3',
    state: 'col-md-2',
    grade: 'col-md-1',
    valueSource: 'col-md-2',
    valueOperator: 'col-md-1',
    valueAmount: 'col-md-2',
    msa: 'col-md-2',
    county: 'col-md-2',
    clear: 'col-md-1',
  }
  return defaults[field] || 'col-md-2'
}

// WHAT: Emit current filter state to parent
// WHY: Parent needs to apply filters to data
function emitFilters() {
  emit('filter-change', { ...localFilters.value })
}

// WHAT: Clear all filters and notify parent
// WHY: Quick reset functionality requested by user
function clearAllFilters() {
  localFilters.value = {
    search: '',
    state: '',
    grade: '',
    valueSource: 'seller',
    valueOperator: '>',
    valueAmount: null,
    msa: '',
    county: '',
  }
  emit('clear-filters')
  emitFilters()
}

// WHAT: Format number with commas for display
// WHY: Make large numbers more readable
function formatNumberWithCommas(val: number | null | undefined): string {
  if (val == null) return ''
  return new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 }).format(val)
}

// WHAT: Handle value filter input with comma formatting
// WHY: Auto-format numbers as user types for better UX
function handleValueFilterInput(event: Event) {
  const input = event.target as HTMLInputElement
  const rawValue = input.value.replace(/[^0-9]/g, '')
  
  if (rawValue === '') {
    localFilters.value.valueAmount = null
    input.value = ''
    emitFilters()
    return
  }
  
  const numericValue = parseInt(rawValue, 10)
  localFilters.value.valueAmount = numericValue
  input.value = formatNumberWithCommas(numericValue)
  
  emitFilters()
}

// WHAT: Define public methods that parent can call via ref
// WHY: Allow parent to programmatically control filters
defineExpose({
  clearAllFilters,
  getFilters: () => ({ ...localFilters.value }),
  setFilters: (filters: Partial<FilterValues>) => {
    Object.assign(localFilters.value, filters)
    emitFilters()
  },
})
</script>

<style scoped>
/* WHAT: Minimal scoped styles since we're using Bootstrap classes */
/* WHY: Keep styling consistent with existing dashboard components */
</style>

