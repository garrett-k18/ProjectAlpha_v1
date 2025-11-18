<template>
  <div class="card h-100">
    <div class="card-body">
      <!-- Filters Section -->
      <div class="mb-4">
        <h5 class="card-title mb-3">
          <i class="mdi mdi-filter-variant me-2"></i>
          Filters
        </h5>

        <!-- Multi-select Fund/Partnerships -->
        <div class="mb-3">
          <label class="form-label fw-semibold">
            <i class="mdi mdi-domain me-1"></i>
            Fund
          </label>
          <div class="dropdown-multiselect">
            <button 
              class="btn btn-outline-secondary btn-sm w-100 text-start d-flex justify-content-between align-items-center"
              type="button"
              @click="toggleDropdown('partnerships')"
            >
              <span>{{ selectedPartnershipsLabel }}</span>
              <i class="mdi mdi-chevron-down"></i>
            </button>
            <div v-if="showPartnershipsDropdown" class="dropdown-menu-custom show" @click.stop>
              <div
                class="dropdown-item-custom"
                v-for="partnership in partnershipOptions"
                :key="partnership.id"
                role="menuitemcheckbox"
                :aria-checked="isPartnershipSelected(partnership.id)"
                :class="{ 'is-selected': isPartnershipSelected(partnership.id) }"
              >
                <input
                  type="checkbox"
                  :id="`partnership-${partnership.id}`"
                  :value="partnership.id"
                  v-model="localPartnershipIds"
                  class="form-check-input me-2"
                />
                <label :for="`partnership-${partnership.id}`" class="form-check-label">
                  {{ partnership.nickname || partnership.fund_name || `Partnership #${partnership.id}` }}
                  <span v-if="partnership.entity_role_label" class="text-muted small"> · {{ partnership.entity_role_label }}</span>
                  <span v-if="partnership.fund_name" class="text-muted small"> · {{ partnership.fund_name }}</span>
                </label>
              </div>
              <div v-if="partnershipOptions.length === 0" class="text-muted small p-2">
                {{ loadingPartnerships ? 'Loading...' : 'No partnerships available' }}
              </div>
            </div>
          </div>
          <div v-if="errorPartnerships" class="text-danger small mt-1">{{ errorPartnerships }}</div>
        </div>

        <!-- Multi-select Trades -->
        <div class="mb-3">
          <label class="form-label fw-semibold">
            <i class="mdi mdi-briefcase-outline me-1"></i>
            Trades
          </label>
          <div class="dropdown-multiselect">
            <button 
              class="btn btn-outline-secondary btn-sm w-100 text-start d-flex justify-content-between align-items-center"
              type="button"
              @click="toggleDropdown('trades')"
            >
              <span>{{ selectedTradesLabel }}</span>
              <i class="mdi mdi-chevron-down"></i>
            </button>
            <div v-if="showTradesDropdown" class="dropdown-menu-custom show" @click.stop>
              <div
                class="dropdown-item-custom"
                v-for="trade in tradeOptions"
                :key="trade.id"
                role="menuitemcheckbox"
                :aria-checked="isTradeSelected(trade.id)"
                :class="{ 'is-selected': isTradeSelected(trade.id) }"
              >
                <input
                  type="checkbox"
                  :id="`trade-${trade.id}`"
                  :value="trade.id"
                  v-model="localTradeIds"
                  class="form-check-input me-2"
                />
                <label :for="`trade-${trade.id}`" class="form-check-label">
                  {{ trade.trade_name }} <span class="text-muted small">({{ trade.asset_count }} assets)</span>
                </label>
              </div>
              <div v-if="tradeOptions.length === 0" class="text-muted small p-2">
                {{ loadingTrades ? 'Loading...' : 'No trades available' }}
              </div>
            </div>
          </div>
          <div v-if="errorTrades" class="text-danger small mt-1">{{ errorTrades }}</div>
        </div>

        <!-- Multi-select Asset Track Status -->
        <div class="mb-3">
          <label class="form-label fw-semibold">
            <i class="mdi mdi-sitemap me-1"></i>
            Asset Track Status
          </label>
          <div class="dropdown-multiselect">
            <button 
              class="btn btn-outline-secondary btn-sm w-100 text-start d-flex justify-content-between align-items-center"
              type="button"
              @click="toggleDropdown('tracks')"
            >
              <span>{{ selectedTracksLabel }}</span>
              <i class="mdi mdi-chevron-down"></i>
            </button>
            <div v-if="showTracksDropdown" class="dropdown-menu-custom show" @click.stop>
              <div
                class="dropdown-item-custom"
                v-for="track in trackOptions"
                :key="track.value"
                role="menuitemcheckbox"
                :aria-checked="isTrackSelected(track.value)"
                :class="{ 'is-selected': isTrackSelected(track.value) }"
              >
                <input
                  type="checkbox"
                  :id="`track-${track.value}`"
                  :value="track.value"
                  v-model="localTracks"
                  class="form-check-input me-2"
                />
                <label :for="`track-${track.value}`" class="form-check-label">
                  {{ track.label }} <span class="text-muted small">({{ track.count }} assets)</span>
                </label>
              </div>
              <div v-if="trackOptions.length === 0" class="text-muted small p-2">
                {{ loadingTracks ? 'Loading...' : 'No tracks available' }}
              </div>
            </div>
          </div>
          <div v-if="errorTracks" class="text-danger small mt-1">{{ errorTracks }}</div>
        </div>

        <!-- Multi-select Asset Task Status -->
        <div class="mb-3">
          <label class="form-label fw-semibold">
            <i class="mdi mdi-checkbox-marked-circle-outline me-1"></i>
            Asset Task Status
          </label>
          <div class="dropdown-multiselect">
            <button 
              class="btn btn-outline-secondary btn-sm w-100 text-start d-flex justify-content-between align-items-center"
              type="button"
              @click="toggleDropdown('tasks')"
            >
              <span>{{ selectedTasksLabel }}</span>
              <i class="mdi mdi-chevron-down"></i>
            </button>
            <div v-if="showTasksDropdown" class="dropdown-menu-custom show" @click.stop>
              <div
                class="dropdown-item-custom"
                v-for="task in taskStatusOptions"
                :key="task.value"
                role="menuitemcheckbox"
                :aria-checked="isTaskSelected(task.value)"
                :class="{ 'is-selected': isTaskSelected(task.value) }"
              >
                <input
                  type="checkbox"
                  :id="`task-${task.value}`"
                  :value="task.value"
                  v-model="localTaskStatuses"
                  class="form-check-input me-2"
                />
                <label :for="`task-${task.value}`" class="form-check-label">
                  {{ task.label }} <span class="badge bg-secondary">{{ task.track.toUpperCase() }}</span> <span class="text-muted small">({{ task.count }})</span>
                </label>
              </div>
              <div v-if="taskStatusOptions.length === 0" class="text-muted small p-2">
                {{ loadingTaskStatuses ? 'Loading...' : 'No tasks available' }}
              </div>
            </div>
          </div>
          <div v-if="errorTaskStatuses" class="text-danger small mt-1">{{ errorTaskStatuses }}</div>
        </div>

        <!-- Action Buttons -->
        <div class="d-flex gap-2">
          <button
            class="btn btn-primary btn-sm flex-grow-1"
            @click="applyFilters"
            :disabled="!hasChanges"
          >
            <i class="mdi mdi-check me-1"></i>
            Apply
          </button>
          <button
            class="btn btn-outline-secondary btn-sm"
            @click="resetFilters"
            :disabled="!hasActiveFilters"
          >
            <i class="mdi mdi-refresh me-1"></i>
            Reset
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useReportingStore } from '@/stores/reporting'

const props = defineProps<{
  currentView: string
}>()

const emit = defineEmits<{
  (e: 'view-change', view: string): void
  (e: 'filters-change'): void
  (e: 'reset-filters'): void
}>()

const reportingStore = useReportingStore()
const {
  selectedTradeIds,
  selectedTracks,
  selectedTaskStatuses,
  selectedPartnershipIds,
  dateRangeStart,
  dateRangeEnd,
  tradeOptions,
  trackOptions,
  taskStatusOptions,
  partnershipOptions,
  loadingTrades,
  loadingTracks,
  loadingTaskStatuses,
  loadingPartnerships,
  errorTrades,
  errorTracks,
  errorTaskStatuses,
  errorPartnerships,
  hasActiveFilters,
} = storeToRefs(reportingStore)

// **WHAT**: Local state for multi-select filters
// **WHY**: Allow users to select multiple trades, tracks, tasks before applying
const localTradeIds = ref<number[]>([])
const localTracks = ref<string[]>([])
const localTaskStatuses = ref<string[]>([])
const localPartnershipIds = ref<number[]>([])
const localDateStart = ref<string | null>(null)
const localDateEnd = ref<string | null>(null)

// **WHAT**: Dropdown visibility toggles
// **WHY**: Control which multi-select dropdown is currently open
const showTradesDropdown = ref<boolean>(false)
const showTracksDropdown = ref<boolean>(false)
const showTasksDropdown = ref<boolean>(false)
const showPartnershipsDropdown = ref<boolean>(false)

// **WHAT**: Sync local state with store on mount
// **WHY**: Initialize local filters from store state
watch([selectedTradeIds, selectedTracks, selectedTaskStatuses, selectedPartnershipIds, dateRangeStart, dateRangeEnd], () => {
  localTradeIds.value = [...selectedTradeIds.value]
  localTracks.value = [...selectedTracks.value]
  localTaskStatuses.value = [...selectedTaskStatuses.value]
  localPartnershipIds.value = [...selectedPartnershipIds.value]
  localDateStart.value = dateRangeStart.value
  localDateEnd.value = dateRangeEnd.value
}, { immediate: true })

// **WHAT**: Check if any filters have changed from store state
// **WHY**: Enable/disable Apply button
const hasChanges = computed(() => {
  const tradesChanged = JSON.stringify([...selectedTradeIds.value].sort()) !== JSON.stringify([...localTradeIds.value].sort())
  const tracksChanged = JSON.stringify([...selectedTracks.value].sort()) !== JSON.stringify([...localTracks.value].sort())
  const tasksChanged = JSON.stringify([...selectedTaskStatuses.value].sort()) !== JSON.stringify([...localTaskStatuses.value].sort())
  const partnershipsChanged = JSON.stringify([...selectedPartnershipIds.value].sort()) !== JSON.stringify([...localPartnershipIds.value].sort())
  const dateStartChanged = dateRangeStart.value !== localDateStart.value
  const dateEndChanged = dateRangeEnd.value !== localDateEnd.value
  
  return tradesChanged || tracksChanged || tasksChanged || partnershipsChanged || dateStartChanged || dateEndChanged
})

// **WHAT**: Computed label for selected trades
// **WHY**: Show count or "All Trades" in dropdown button
const selectedTradesLabel = computed(() => {
  if (localTradeIds.value.length === 0) return 'All Trades'
  if (localTradeIds.value.length === 1) {
    const trade = tradeOptions.value.find(t => t.id === localTradeIds.value[0])
    return trade?.trade_name || '1 selected'
  }
  return `${localTradeIds.value.length} selected`
})

// **WHAT**: Computed label for selected tracks
// **WHY**: Show count or "All Tracks" in dropdown button
const selectedTracksLabel = computed(() => {
  if (localTracks.value.length === 0) return 'All Tracks'
  if (localTracks.value.length === 1) {
    const track = trackOptions.value.find(t => t.value === localTracks.value[0])
    return track?.label || '1 selected'
  }
  return `${localTracks.value.length} selected`
})

// **WHAT**: Computed label for selected task statuses
// **WHY**: Show count or "All Tasks" in dropdown button
const selectedTasksLabel = computed(() => {
  if (localTaskStatuses.value.length === 0) return 'All Tasks'
  if (localTaskStatuses.value.length === 1) {
    const task = taskStatusOptions.value.find(t => t.value === localTaskStatuses.value[0])
    return task?.label || '1 selected'
  }
  return `${localTaskStatuses.value.length} selected`
})

// **WHAT**: Computed label for selected partnerships
// **WHY**: Show count or "All Partnerships" in dropdown button
const selectedPartnershipsLabel = computed(() => {
  if (localPartnershipIds.value.length === 0) return 'All Partnerships'
  if (localPartnershipIds.value.length === 1) {
    const partnership = partnershipOptions.value.find(p => p.id === localPartnershipIds.value[0])
    return partnership?.nickname || partnership?.fund_name || '1 selected'
  }
  return `${localPartnershipIds.value.length} selected`
})

// **WHAT**: Cached Set of selected trade ids
// **WHY**: Provides O(1) lookups so selection indicators render instantly
const tradeSelectionSet = computed<Set<number>>(() => new Set(localTradeIds.value))

// **WHAT**: Cached Set of selected track identifiers
// **WHY**: Keeps UI responsive while toggling multiple checkboxes
const trackSelectionSet = computed<Set<string>>(() => new Set(localTracks.value))

// **WHAT**: Cached Set of selected task status identifiers
// **WHY**: Simplifies template logic and prevents repeated array scans
const taskSelectionSet = computed<Set<string>>(() => new Set(localTaskStatuses.value))

// **WHAT**: Cached Set of selected partnership ids
// **WHY**: Enables accessible visual cues tied to checkbox state
const partnershipSelectionSet = computed<Set<number>>(() => new Set(localPartnershipIds.value))

// **WHAT**: Helper reporting whether a trade is currently selected
// **WHY**: Powers aria attributes plus visual confirmation icons
function isTradeSelected(tradeId: number): boolean {
  return tradeSelectionSet.value.has(tradeId)
}

// **WHAT**: Helper reporting whether a track is selected
// **WHY**: Keeps template declarative and readable
function isTrackSelected(trackValue: string): boolean {
  return trackSelectionSet.value.has(trackValue)
}

// **WHAT**: Helper reporting whether a task status is selected
// **WHY**: Drives badges/icons without duplicating Set logic inline
function isTaskSelected(taskValue: string): boolean {
  return taskSelectionSet.value.has(taskValue)
}

// **WHAT**: Helper reporting whether a partnership is selected
// **WHY**: Aligns aria attributes with actual checkbox values
function isPartnershipSelected(partnershipId: number): boolean {
  return partnershipSelectionSet.value.has(partnershipId)
}

function toggleDropdown(type: 'trades' | 'tracks' | 'tasks' | 'partnerships'): void {
  showTradesDropdown.value = type === 'trades' ? !showTradesDropdown.value : false
  showTracksDropdown.value = type === 'tracks' ? !showTracksDropdown.value : false
  showTasksDropdown.value = type === 'tasks' ? !showTasksDropdown.value : false
  showPartnershipsDropdown.value = type === 'partnerships' ? !showPartnershipsDropdown.value : false
}

// **WHAT**: Apply local filters to store
// **WHY**: Update store state and trigger data refresh
function applyFilters(): void {
  selectedTradeIds.value = [...localTradeIds.value]
  selectedTracks.value = [...localTracks.value]
  selectedTaskStatuses.value = [...localTaskStatuses.value]
  selectedPartnershipIds.value = [...localPartnershipIds.value]
  dateRangeStart.value = localDateStart.value
  dateRangeEnd.value = localDateEnd.value
  
  // Close all dropdowns
  showTradesDropdown.value = false
  showTracksDropdown.value = false
  showTasksDropdown.value = false
  showPartnershipsDropdown.value = false
  
  emit('filters-change')
}

// **WHAT**: Reset all filters to default
// **WHY**: Clear button to start fresh
function resetFilters(): void {
  localTradeIds.value = []
  localTracks.value = []
  localTaskStatuses.value = []
  localPartnershipIds.value = []
  localDateStart.value = null
  localDateEnd.value = null
  
  emit('reset-filters')
}

// **WHAT**: Change active view
// **WHY**: Switch between report types
function changeView(viewName: string): void {
  emit('view-change', viewName)
}
</script>

<style scoped>
.list-group-item.active {
  background-color: var(--bs-primary);
  border-color: var(--bs-primary);
  color: white;
}

.list-group-item:not(.active):hover {
  background-color: rgba(var(--bs-primary-rgb), 0.1);
}

.form-check-input {
  background-repeat: no-repeat;
  background-position: center;
  background-size: 0.65rem 0.65rem;
}


/* Multi-select dropdown styles */
.dropdown-multiselect {
  position: relative;
}

.dropdown-menu-custom {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  z-index: 1000;
  max-height: 200px;
  overflow-y: auto;
  background-color: white;
  border: 1px solid #dee2e6;
  border-radius: 0.25rem;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  margin-top: 0.25rem;
}

.dropdown-item-custom {
  padding: 0.5rem 0.75rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: background-color 0.15s ease-in-out;
  border-left: 3px solid transparent;
}

.dropdown-item-custom:hover {
  background-color: #f8f9fa;
}

.dropdown-item-custom.is-selected {
  background-color: rgba(var(--bs-success-rgb), 0.08);
  border-left-color: var(--bs-success);
}

.dropdown-item-custom label {
  cursor: pointer;
  margin-bottom: 0;
  flex-grow: 1;
}

</style>
