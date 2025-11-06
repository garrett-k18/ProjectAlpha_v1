<template>
  <!-- Subtle warning-colored border (no fill) to match the Short Sale pill -->
  <b-card class="w-100 h-100 border border-1 border-warning rounded-2 shadow-sm">
    <template #header>
      <div
        class="d-flex align-items-center justify-content-between"
        role="button"
        :aria-expanded="!collapsed"
        title="Toggle sub tasks"
        style="cursor: pointer;"
        @click="localCollapsed = !localCollapsed"
      >
        <h5 class="mb-0 d-flex align-items-center">
          <i class="fas fa-tags me-2 text-warning"></i>
          <UiBadge tone="warning" size="lg" class="text-dark">Short Sale</UiBadge>
        </h5>
        <div class="d-flex align-items-center gap-2">
          <div class="position-relative" ref="menuRef">
            <button
              type="button"
              class="btn btn-sm btn-outline-secondary d-inline-flex align-items-center justify-content-center px-2 lh-1"
              @click.stop="toggleMenu"
              :aria-expanded="menuOpen ? 'true' : 'false'"
              aria-label="Card settings"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
                <circle cx="8" cy="2.5" r="1.5" />
                <circle cx="8" cy="8" r="1.5" />
                <circle cx="8" cy="13.5" r="1.5" />
              </svg>
            </button>
            <div v-if="menuOpen" class="card shadow-sm mt-1" style="position: absolute; right: 0; min-width: 160px; z-index: 1060;" @click.stop>
              <div class="list-group list-group-flush">
                <button class="list-group-item list-group-item-action d-flex align-items-center gap-2 text-danger" @click.stop="onDelete">
                  <i class="fas fa-trash"></i>
                  <span>Delete</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Two-column layout: Subtasks | Notes -->
    <div class="p-3" v-show="!collapsed">
      <div class="row g-3">
        <!-- Left Column: Subtasks -->
        <div class="col-md-6">
          <div class="d-flex align-items-center justify-content-between mb-3 pb-2 border-bottom">
            <h5 class="mb-0 fw-bold text-body">Sub Tasks</h5>
            <div class="position-relative" ref="addMenuRef">
              <button type="button" class="btn btn-sm btn-outline-primary d-inline-flex align-items-center gap-2" @click.stop="toggleAddMenu">
                <i class="fas" :class="addMenuOpen ? 'fa-minus' : 'fa-plus'"></i>
                <span>Add Task</span>
                <i class="fas fa-chevron-down small"></i>
              </button>
          <div v-if="addMenuOpen" class="card shadow-sm mt-1" style="position: absolute; right: 0; min-width: 260px; z-index: 1060;">
            <div class="list-group list-group-flush p-2 d-flex flex-wrap gap-2">
              <button
                v-for="opt in taskOptions"
                :key="opt.value"
                type="button"
                class="btn btn-sm border-0 p-0"
                :disabled="existingTypes.has(opt.value) || busy"
                @click="onSelectPill(opt.value)"
                :title="existingTypes.has(opt.value) ? 'Already added' : 'Add ' + opt.label"
              >
                <UiBadge :tone="badgeClass(opt.value)" size="sm" class="me-0">{{ opt.label }}</UiBadge>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Subtask cards list -->
      <div v-if="tasks.length" class="list-group list-group-flush">
        <div
          v-for="t in tasks"
          :key="t.id"
          :class="[
            'list-group-item',
            'px-0',
            'bg-secondary-subtle', // subtle neutral fill
            'border', 'border-1', 'border-light', // neutral thin outline
            'rounded-2', 'shadow-sm',
            'mb-2', // spacing
            'border-start', // ensure left edge area
          ]"
          :style="leftEdgeStyle(t.task_type)"
        >
          <div class="d-flex align-items-center justify-content-between" role="button" @click="toggleExpand(t.id)">
            <div class="d-flex align-items-center ps-2">
              <UiBadge :tone="badgeClass(t.task_type)" size="sm" class="me-2">{{ labelFor(t.task_type) }}</UiBadge>
            </div>
            <div class="d-flex align-items-center small text-muted">
              <i :class="(expandedId === t.id || expandedId === 'all') ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
            </div>
          </div>
          <div v-if="expandedId === t.id || expandedId === 'all'" class="mt-2 p-2 border-top">
            <!-- WHAT: Task-specific fields based on task type -->
            <!-- WHY: Different tasks need different data collection -->
            <div v-if="t.task_type === 'sold'" class="mb-3">
              <div class="row g-2">
                <div class="col-md-6">
                  <label class="form-label small text-muted">Sale Date</label>
                  <div class="d-block">
                    <EditableDate
                      :model-value="shortSaleData?.short_sale_date || ''"
                      @update:model-value="handleDateChange"
                      title="Click to edit sale date"
                    />
                  </div>
                </div>
                <div class="col-md-6">
                  <label class="form-label small text-muted">Gross Proceeds</label>
                  <UiCurrencyInput 
                    :model-value="shortSaleData?.gross_proceeds || ''"
                    @update:model-value="handleCurrencyChange"
                    prefix="$"
                    :debounce-ms="1000"
                    size="sm"
                    placeholder="0.00"
                  />
                </div>
              </div>
            </div>
            <!-- WHAT: Listed task completion fields -->
            <!-- WHY: Track listing date and price for listed properties -->
            <div v-else-if="t.task_type === 'listed'" class="mb-3">
              <div class="row g-2">
                <div class="col-md-6">
                  <label class="form-label small text-muted">List Date</label>
                  <div class="d-block">
                    <EditableDate
                      :model-value="shortSaleData?.short_sale_list_date || ''"
                      @update:model-value="handleListDateChange"
                      title="Click to edit list date"
                    />
                  </div>
                </div>
                <div class="col-md-6">
                  <label class="form-label small text-muted">List Price</label>
                  <UiCurrencyInput 
                    :model-value="shortSaleData?.short_sale_list_price || ''"
                    @update:model-value="handleListPriceChange"
                    prefix="$"
                    :debounce-ms="1000"
                    size="sm"
                    placeholder="0.00"
                  />
                </div>
              </div>
              
              <!-- WHAT: Reusable offers section -->
              <!-- WHY: Shared component for offers management -->
              <OffersSection 
                :hub-id="hubId" 
                offer-source="short_sale"
                :readonly="t.task_type === 'under_contract'"
                ref="offersSection"
                @task-created="handleTaskCreated"
              />
            </div>
            <div v-else class="small text-muted mb-2">Task-specific fields for {{ labelFor(t.task_type) }}</div>
            
            
            <div class="d-flex justify-content-end mt-2">
              <button
                type="button"
                class="btn btn-sm btn-outline-danger d-inline-flex align-items-center gap-1 px-2 py-1"
                style="font-size: 0.75rem;"
                @click.stop="requestDeleteTask(t.id)"
              >
                <i class="mdi mdi-delete me-1"></i>
                <span>Delete Task</span>
              </button>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="text-muted small">No subtasks yet. Use Add Task to create one.</div>
        </div>

        <!-- Right Column: Shared Notes for this Outcome -->
        <div class="col-md-6">
          <div class="d-flex align-items-center justify-content-between mb-3 pb-2 border-bottom">
            <h5 class="mb-0 fw-bold text-body">Notes</h5>
          </div>
          <SubtaskNotes :hubId="props.hubId" outcome="short_sale" :taskType="null" :taskId="null" />
        </div>
      </div>
    </div>
  </b-card>

  <!-- Confirm Delete Task Modal -->
  <template v-if="deleteTaskConfirm.open">
    <div class="modal-backdrop fade show" style="z-index: 1050;"></div>
    <div class="modal fade show" tabindex="-1" role="dialog" aria-modal="true"
         style="display: block; position: fixed; inset: 0; z-index: 1055;">
      <div class="modal-dialog modal-dialog-centered" role="document">
        <div class="modal-content">
          <div class="modal-header bg-danger-subtle">
            <h5 class="modal-title d-flex align-items-center">
              <i class="fas fa-triangle-exclamation text-danger me-2"></i>
              Confirm Task Deletion
            </h5>
            <button type="button" class="btn-close" aria-label="Close" @click="cancelDeleteTask"></button>
          </div>
          <div class="modal-body">
            <p class="mb-0">Are you sure you want to delete this task? This action cannot be undone.</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-light" @click="cancelDeleteTask">Cancel</button>
            <button type="button" class="btn btn-danger" @click="confirmDeleteTask" :disabled="deleteTaskConfirm.busy">
              <span v-if="deleteTaskConfirm.busy" class="spinner-border spinner-border-sm me-2"></span>
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>
  </template>
</template>

<script setup lang="ts">
import { withDefaults, defineProps, ref, computed, watch, onMounted, onBeforeUnmount, defineEmits } from 'vue'
import { useAmOutcomesStore, type ShortSaleTask, type ShortSaleTaskType } from '@/stores/outcomes'
import http from '@/lib/http'
import { useDataRefresh } from '@/composables/useDataRefresh'
// Reusable editable date component with inline picker
// Path: src/components/ui/EditableDate.vue
import EditableDate from '@/components/ui/EditableDate.vue'
import UiBadge from '@/components/ui/UiBadge.vue'
// Hyper UI currency input component
// Path: src/components/ui/UiCurrencyInput.vue
import UiCurrencyInput from '@/components/ui/UiCurrencyInput.vue'
// Feature-local notes component (moved for AM Tasking scope)
// Path: src/views/am_module/loanlvl/am_tasking/components/SubtaskNotes.vue
import SubtaskNotes from '@/views/am_module/loanlvl/am_tasking/components/SubtaskNotes.vue'
import OffersSection from '../components/OffersSection.vue'

const props = withDefaults(defineProps<{ hubId: number; masterCollapsed?: boolean }>(), { masterCollapsed: false })
const emit = defineEmits<{ (e: 'delete'): void }>()
const store = useAmOutcomesStore()
// WHAT: Collapsed state for the entire card body (subtasks section hidden when true)
// WHY: Allow both individual card collapse and master collapse control
const localCollapsed = ref<boolean>(false)
const collapsed = computed(() => props.masterCollapsed || localCollapsed.value)
const busy = ref(false)
const deleteTaskConfirm = ref<{ open: boolean; taskId: number | null; busy: boolean }>({ open: false, taskId: null, busy: false })
// Settings menu state/handlers
const menuOpen = ref(false)
const menuRef = ref<HTMLElement | null>(null)
function toggleMenu() { menuOpen.value = !menuOpen.value }
function onDelete() { menuOpen.value = false; emit('delete') }
// Add Task custom dropdown state
const addMenuOpen = ref(false)
const addMenuRef = ref<HTMLElement | null>(null)
// Subtasks state
const tasks = ref<ShortSaleTask[]>([])
const localExpandedId = ref<number | null>(null)
const userInteracted = ref(false)

watch(() => props.masterCollapsed, (newVal: boolean) => {
  if (newVal) {
    userInteracted.value = false
    localExpandedId.value = null
  }
})

const expandedId = computed(() => {
  if (!props.masterCollapsed && !userInteracted.value) return 'all' as any
  return localExpandedId.value
})
// Short Sale completion data
const shortSaleData = ref<any>(null)
// Reference to offers section component
const offersSection = ref<any>(null)
function handleDocClick(e: MouseEvent) {
  const root = menuRef.value
  const addRoot = addMenuRef.value
  if (menuOpen.value && root && !root.contains(e.target as Node)) menuOpen.value = false
  if (addMenuOpen.value && addRoot && !addRoot.contains(e.target as Node)) addMenuOpen.value = false
}
onMounted(() => document.addEventListener('click', handleDocClick))
onBeforeUnmount(() => {
  document.removeEventListener('click', handleDocClick)
})

// WHAT: Setup data refresh functionality
// WHY: Auto-refresh when other components modify data
const { emitTaskAdded, emitTaskDeleted, emitTaskUpdated } = useDataRefresh(props.hubId, async () => {
  // WHAT: Refresh tasks and completion data when changes occur
  tasks.value = await store.listShortSaleTasks(props.hubId, true)
  await loadShortSaleData()
})

async function load() {
  // Load subtasks
  tasks.value = await store.listShortSaleTasks(props.hubId, true)
  // Load Short Sale outcome data for completion fields
  await loadShortSaleData()
}

// WHAT: Handle task-created event from OffersSection
// WHY: Refresh tasks when auto-created from accepted offer
async function handleTaskCreated() {
  await load()
}

// WHAT: Load Short Sale outcome data
// WHY: Need access to completion fields like sale date and gross proceeds
async function loadShortSaleData() {
  try {
    // Get Short Sale outcome for this asset
    const response = await http.get(`/am/outcomes/short-sale/?asset_hub_id=${props.hubId}`)
    if (response.data && response.data.length > 0) {
      shortSaleData.value = response.data[0] // Take the first (should be only) result
    } else {
      // No Short Sale outcome exists yet, create one
      const payload = {
        asset_hub_id: props.hubId
      }
      console.log('Creating Short Sale outcome with payload:', payload)
      const createResponse = await http.post('/am/outcomes/short-sale/', payload)
      shortSaleData.value = createResponse.data
    }
  } catch (err: any) {
    console.error('Failed to load/create short sale data:', err)
    console.error('Error response:', err.response?.data)
    console.error('Error status:', err.response?.status)
    console.error('Full error object:', err)
    // Initialize empty data as fallback
    shortSaleData.value = {
      asset_hub: null,
      short_sale_date: null,
      gross_proceeds: null,
      short_sale_list_date: null,
      short_sale_list_price: null
    }
  }
}


// WHAT: Convert US date format to backend format
// WHY: Backend expects yyyy-mm-dd but users see mm/dd/yyyy
function convertToBackendDate(usDate: string): string {
  if (!usDate) return ''
  try {
    const [month, day, year] = usDate.split('/')
    return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`
  } catch {
    return usDate // Return as-is if parsing fails
  }
}

// WHAT: Convert backend date format to US display format
// WHY: Display mm/dd/yyyy to users but store yyyy-mm-dd
function convertToDisplayDate(backendDate: string): string {
  if (!backendDate) return ''
  try {
    const [year, month, day] = backendDate.split('-')
    return `${month}/${day}/${year}`
  } catch {
    return backendDate // Return as-is if parsing fails
  }
}

// WHAT: Handle sale date changes from EditableDate component
// WHY: EditableDate already provides yyyy-mm-dd format
function handleDateChange(newDate: string) {
  updateShortSaleField('short_sale_date', newDate, false)
}

// WHAT: Handle currency changes from UiCurrencyInput component
// WHY: Save currency values with built-in debouncing
function handleCurrencyChange(value: string) {
  updateShortSaleField('gross_proceeds', value, false)
}

// WHAT: Handle list date changes from EditableDate component
// WHY: EditableDate already provides yyyy-mm-dd format
function handleListDateChange(newDate: string) {
  updateShortSaleField('short_sale_list_date', newDate, false)
}

// WHAT: Handle list price changes from UiCurrencyInput component
// WHY: Save list price values with built-in debouncing
function handleListPriceChange(value: string) {
  updateShortSaleField('short_sale_list_price', value, false)
}


// WHAT: Update Short Sale completion fields
// WHY: Save completion data when user enters sale date or proceeds
async function updateShortSaleField(fieldName: string, value: string, emitEvent: boolean = true) {
  try {
    console.log(`Updating ${fieldName} with value:`, value)
    
    // Ensure we have a Short Sale outcome to update
    if (!shortSaleData.value || !shortSaleData.value.asset_hub) {
      console.log('No Short Sale outcome found, creating one first')
      await loadShortSaleData()
    }
    
    if (!shortSaleData.value?.asset_hub) {
      throw new Error('Unable to create or find Short Sale outcome')
    }
    
    // WHAT: Convert value to proper format for backend
    // WHY: Ensure consistent data storage
    let processedValue = value || null
    if (fieldName === 'gross_proceeds' && processedValue) {
      // For currency fields, ensure we store as number
      const numValue = parseFloat(processedValue)
      processedValue = isNaN(numValue) ? null : numValue.toString()
      console.log(`Processed currency value:`, processedValue)
    }
    
    const payload = { [fieldName]: processedValue }
    console.log(`Sending PATCH to /am/outcomes/short-sale/${shortSaleData.value.asset_hub}/ with payload:`, payload)
    
    const response = await http.patch(`/am/outcomes/short-sale/${shortSaleData.value.asset_hub}/`, payload)
    console.log(`Backend response:`, response.data)
    
    // Update local data immediately
    if (shortSaleData.value) {
      shortSaleData.value[fieldName] = processedValue
    }
    
    // WHAT: Emit task updated event only when requested
    // WHY: Avoid excessive refresh events for field updates
    if (emitEvent) {
      emitTaskUpdated('short_sale', 0) // Use 0 as placeholder task ID for outcome updates
    }
  } catch (err: any) {
    console.error(`Failed to update ${fieldName}:`, err)
    console.error('Error details:', err.response?.data)
    alert(`Failed to update ${fieldName}. Please try again.`)
  }
}

onMounted(load)

// ---------- Subtasks helpers ----------
const taskOptions: ReadonlyArray<{ value: ShortSaleTaskType; label: string }> = [
  { value: 'list_price_accepted', label: 'List Price Accepted' },
  { value: 'listed', label: 'Listed' },
  { value: 'under_contract', label: 'Under Contract' },
  { value: 'sold', label: 'Sold' },
]
function labelFor(tp: ShortSaleTaskType): string {
  const m = taskOptions.find(o => o.value === tp)
  return m ? m.label : tp
}
const existingTypes = computed<Set<ShortSaleTaskType>>(() => new Set(tasks.value.map(t => t.task_type)))
function toggleAddMenu() { addMenuOpen.value = !addMenuOpen.value }
function onSelectPill(tp: ShortSaleTaskType) {
  if (existingTypes.value.has(tp) || busy.value) return
  busy.value = true
  store.createShortSaleTask(props.hubId, tp)
    .then(async (newTask) => { 
      tasks.value = await store.listShortSaleTasks(props.hubId, true)
      // WHAT: Emit task added event
      // WHY: Notify other components to refresh their data
      emitTaskAdded('short_sale', newTask?.id || 0)
    })
    .finally(() => { busy.value = false; addMenuOpen.value = false })
}
function toggleExpand(id: number) { 
  userInteracted.value = true
  localExpandedId.value = localExpandedId.value === id ? null : id 
}
function isoDate(iso: string | null): string { 
  if (!iso) return 'N/A'
  try { return new Date(iso).toLocaleDateString() } catch { return iso } 
}

// Update task_started date via PATCH request
async function updateTaskStarted(taskId: number, newDate: string) {
  try {
    await http.patch(`/am/outcomes/short-sale-tasks/${taskId}/`, { task_started: newDate })
    // Refresh tasks to show updated date
    tasks.value = await store.listShortSaleTasks(props.hubId, true)
    // WHAT: Emit task updated event
    // WHY: Notify other components that task data changed
    emitTaskUpdated('short_sale', taskId)
  } catch (err: any) {
    console.error('Failed to update task start date:', err)
    alert('Failed to update start date. Please try again.')
  }
}

function requestDeleteTask(taskId: number) {
  deleteTaskConfirm.value = { open: true, taskId, busy: false }
}

function cancelDeleteTask() {
  deleteTaskConfirm.value = { open: false, taskId: null, busy: false }
}

async function confirmDeleteTask() {
  const taskId = deleteTaskConfirm.value.taskId
  if (!taskId) return
  try {
    deleteTaskConfirm.value.busy = true
    await store.deleteShortSaleTask(props.hubId, taskId)
    tasks.value = await store.listShortSaleTasks(props.hubId, true)
    // WHAT: Emit task deleted event
    // WHY: Notify other components that task was removed
    emitTaskDeleted('short_sale', taskId)
    cancelDeleteTask()
  } catch (err: any) {
    console.error('Failed to delete short sale task:', err)
    alert('Failed to delete task. Please try again.')
    deleteTaskConfirm.value.busy = false
  }
}

function badgeClass(tp: ShortSaleTaskType): import('@/config/badgeTokens').BadgeToneKey {
  const map: Record<ShortSaleTaskType, import('@/config/badgeTokens').BadgeToneKey> = {
    list_price_accepted: 'warning',
    listed: 'info',
    under_contract: 'primary',
    sold: 'success',
  }
  return map[tp]
}
function itemBorderClass(tp: ShortSaleTaskType): string {
  const map: Record<ShortSaleTaskType, string> = {
    list_price_accepted: 'border-start border-2 border-warning',
    listed: 'border-start border-2 border-info',
    under_contract: 'border-start border-2 border-primary',
    sold: 'border-start border-2 border-success',
  }
  return map[tp]
}

// Robust left-edge stripe using inset box-shadow + Bootstrap CSS vars with fallbacks
function leftEdgeStyle(tp: ShortSaleTaskType): Record<string, string> {
  const colorMap: Record<ShortSaleTaskType, string> = {
    list_price_accepted: 'var(--bs-warning, #ffc107)',
    listed: 'var(--bs-info, #0dcaf0)',
    under_contract: 'var(--bs-primary, #0d6efd)',
    sold: 'var(--bs-success, #198754)',
  }
  return {
    boxShadow: `inset 3px 0 0 ${colorMap[tp]}, var(--bs-box-shadow-sm, 0 .125rem .25rem rgba(0,0,0,.075))`,
  }
}
</script>
