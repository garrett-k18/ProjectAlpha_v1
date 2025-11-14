<template>
  <div class="card h-100">
    <div class="card-body">
      <!-- Filters Section -->
      <div class="mb-4">
        <h5 class="card-title mb-3">
          <i class="mdi mdi-filter-variant me-2"></i>
          Filters
        </h5>

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
              <div class="dropdown-item-custom" v-for="trade in tradeOptions" :key="trade.id">
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
              <div class="dropdown-item-custom" v-for="track in trackOptions" :key="track.value">
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
              <div class="dropdown-item-custom" v-for="task in taskStatusOptions" :key="task.value">
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

        <!-- Multi-select Entities -->
        <div class="mb-3">
          <label class="form-label fw-semibold">
            <i class="mdi mdi-domain me-1"></i>
            Entities
          </label>
          <div class="dropdown-multiselect">
            <button 
              class="btn btn-outline-secondary btn-sm w-100 text-start d-flex justify-content-between align-items-center"
              type="button"
              @click="toggleDropdown('entities')"
            >
              <span>{{ selectedEntitiesLabel }}</span>
              <i class="mdi mdi-chevron-down"></i>
            </button>
            <div v-if="showEntitiesDropdown" class="dropdown-menu-custom show" @click.stop>
              <div class="dropdown-item-custom" v-for="entity in entityOptions" :key="entity.id">
                <input
                  type="checkbox"
                  :id="`entity-${entity.id}`"
                  :value="entity.id"
                  v-model="localEntityIds"
                  class="form-check-input me-2"
                />
                <label :for="`entity-${entity.id}`" class="form-check-label">
                  <span class="badge rounded-pill bg-light text-dark me-2 text-uppercase small">
                    {{ entity.entity_type_label }}
                  </span>
                  {{ entity.name }}
                  <span v-if="entity.fund_name" class="text-muted small"> · {{ entity.fund_name }}</span>
                  <span v-if="entity.owned_asset_count" class="text-muted small ms-1">
                    ({{ entity.owned_asset_count }} assets)
                  </span>
                </label>
              </div>
              <div v-if="entityOptions.length === 0" class="text-muted small p-2">
                {{ loadingEntities ? 'Loading...' : 'No entities available' }}
              </div>
            </div>
          </div>
        </div>

        <!-- Date Range -->
        <div class="mb-3">
          <label class="form-label fw-semibold">
            <i class="mdi mdi-calendar-range me-1"></i>
            Date Range
          </label>
          <div class="row g-2">
            <div class="col-6">
              <input
                type="date"
                class="form-control form-control-sm"
                v-model="localDateStart"
              />
            </div>
            <div class="col-6">
              <input
                type="date"
                class="form-control form-control-sm"
                v-model="localDateEnd"
              />
            </div>
          </div>
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

      <hr class="my-3" />

      <!-- Views Section -->
      <div>
        <h5 class="card-title mb-3">
          <i class="mdi mdi-view-dashboard-outline me-2"></i>
          Views
        </h5>
        
        <div class="list-group list-group-flush">
          <a
            href="#"
            class="list-group-item list-group-item-action"
            :class="{ 'active': currentView === 'overview' }"
            @click.prevent="changeView('overview')"
          >
            <i class="mdi mdi-view-dashboard me-2"></i>
            Overview
          </a>
          <a
            href="#"
            class="list-group-item list-group-item-action"
            :class="{ 'active': currentView === 'by-trade' }"
            @click.prevent="changeView('by-trade')"
          >
            <i class="mdi mdi-briefcase-outline me-2"></i>
            By Trade
          </a>
          <a
            href="#"
            class="list-group-item list-group-item-action"
            :class="{ 'active': currentView === 'by-status' }"
            @click.prevent="changeView('by-status')"
          >
            <i class="mdi mdi-tag-outline me-2"></i>
            By Status
          </a>
          <a
            href="#"
            class="list-group-item list-group-item-action"
            :class="{ 'active': currentView === 'by-fund' }"
            @click.prevent="changeView('by-fund')"
          >
            <i class="mdi mdi-wallet-outline me-2"></i>
            By Fund
          </a>
          <a
            href="#"
            class="list-group-item list-group-item-action"
            :class="{ 'active': currentView === 'by-entity' }"
            @click.prevent="changeView('by-entity')"
          >
            <i class="mdi mdi-domain me-2"></i>
            By Entity
          </a>
          <a
            href="#"
            class="list-group-item list-group-item-action"
            :class="{ 'active': currentView === 'geographic' }"
            @click.prevent="changeView('geographic')"
          >
            <i class="mdi mdi-map-marker-outline me-2"></i>
            Geographic
          </a>
          <a
            href="#"
            class="list-group-item list-group-item-action"
            :class="{ 'active': currentView === 'collateral' }"
            @click.prevent="changeView('collateral')"
          >
            <i class="mdi mdi-home-outline me-2"></i>
            Collateral
          </a>
          <a
            href="#"
            class="list-group-item list-group-item-action"
            :class="{ 'active': currentView === 'timeseries' }"
            @click.prevent="changeView('timeseries')"
          >
            <i class="mdi mdi-chart-line me-2"></i>
            Time Series
          </a>
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
  selectedEntityIds,
  dateRangeStart,
  dateRangeEnd,
  tradeOptions,
  trackOptions,
  taskStatusOptions,
  entityOptions,
  loadingTrades,
  loadingTracks,
  loadingTaskStatuses,
  loadingEntities,
  errorTrades,
  errorTracks,
  errorTaskStatuses,
  errorEntities,
  hasActiveFilters,
} = storeToRefs(reportingStore)

// **WHAT**: Local state for multi-select filters
// **WHY**: Allow users to select multiple trades, tracks, tasks before applying
const localTradeIds = ref<number[]>([])
const localTracks = ref<string[]>([])
const localTaskStatuses = ref<string[]>([])
const localEntityIds = ref<number[]>([])
const localDateStart = ref<string | null>(null)
const localDateEnd = ref<string | null>(null)

// **WHAT**: Dropdown visibility toggles
// **WHY**: Control which multi-select dropdown is currently open
const showTradesDropdown = ref<boolean>(false)
const showTracksDropdown = ref<boolean>(false)
const showTasksDropdown = ref<boolean>(false)
const showEntitiesDropdown = ref<boolean>(false)

// **WHAT**: Sync local state with store on mount
// **WHY**: Initialize local filters from store state
watch([selectedTradeIds, selectedTracks, selectedTaskStatuses, selectedEntityIds, dateRangeStart, dateRangeEnd], () => {
  localTradeIds.value = [...selectedTradeIds.value]
  localTracks.value = [...selectedTracks.value]
  localTaskStatuses.value = [...selectedTaskStatuses.value]
  localEntityIds.value = [...selectedEntityIds.value]
  localDateStart.value = dateRangeStart.value
  localDateEnd.value = dateRangeEnd.value
}, { immediate: true })

// **WHAT**: Check if any filters have changed from store state
// **WHY**: Enable/disable Apply button
const hasChanges = computed(() => {
  const tradesChanged = JSON.stringify([...selectedTradeIds.value].sort()) !== JSON.stringify([...localTradeIds.value].sort())
  const tracksChanged = JSON.stringify([...selectedTracks.value].sort()) !== JSON.stringify([...localTracks.value].sort())
  const tasksChanged = JSON.stringify([...selectedTaskStatuses.value].sort()) !== JSON.stringify([...localTaskStatuses.value].sort())
  const entitiesChanged = JSON.stringify([...selectedEntityIds.value].sort()) !== JSON.stringify([...localEntityIds.value].sort())
  const dateStartChanged = dateRangeStart.value !== localDateStart.value
  const dateEndChanged = dateRangeEnd.value !== localDateEnd.value
  
  return tradesChanged || tracksChanged || tasksChanged || entitiesChanged || dateStartChanged || dateEndChanged
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

// **WHAT**: Computed label for selected entities
// **WHY**: Show count or "All Entities" in dropdown button
const selectedEntitiesLabel = computed(() => {
  if (localEntityIds.value.length === 0) return 'All Entities'
  if (localEntityIds.value.length === 1) {
    const entity = entityOptions.value.find(e => e.id === localEntityIds.value[0])
    return entity?.name || '1 selected'
  }
  return `${localEntityIds.value.length} selected`
})

function toggleDropdown(type: 'trades' | 'tracks' | 'tasks' | 'entities'): void {
  showTradesDropdown.value = type === 'trades' ? !showTradesDropdown.value : false
  showTracksDropdown.value = type === 'tracks' ? !showTracksDropdown.value : false
  showTasksDropdown.value = type === 'tasks' ? !showTasksDropdown.value : false
  showEntitiesDropdown.value = type === 'entities' ? !showEntitiesDropdown.value : false
}

// **WHAT**: Apply local filters to store
// **WHY**: Update store state and trigger data refresh
function applyFilters(): void {
  selectedTradeIds.value = [...localTradeIds.value]
  selectedTracks.value = [...localTracks.value]
  selectedTaskStatuses.value = [...localTaskStatuses.value]
  selectedEntityIds.value = [...localEntityIds.value]
  dateRangeStart.value = localDateStart.value
  dateRangeEnd.value = localDateEnd.value
  
  // Close all dropdowns
  showTradesDropdown.value = false
  showTracksDropdown.value = false
  showTasksDropdown.value = false
  showEntitiesDropdown.value = false
  
  emit('filters-change')
}

// **WHAT**: Reset all filters to default
// **WHY**: Clear button to start fresh
function resetFilters(): void {
  localTradeIds.value = []
  localTracks.value = []
  localTaskStatuses.value = []
  localEntityIds.value = []
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

.form-check-input:checked {
  background-color: var(--bs-success);
  border-color: var(--bs-success);
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
  transition: background-color 0.15s ease-in-out;
}

.dropdown-item-custom:hover {
  background-color: #f8f9fa;
}

.dropdown-item-custom label {
  cursor: pointer;
  margin-bottom: 0;
  flex-grow: 1;
}
</style>
