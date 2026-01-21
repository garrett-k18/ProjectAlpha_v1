<template>
  <!-- Subtle info-colored border (no fill) to match the REO pill -->
  <b-card class="w-100 h-100 border border-1 border-info rounded-2 shadow-sm">
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
          <i class="fas fa-house-chimney me-2 text-info"></i>
          <UiBadge tone="info" size="lg">REO</UiBadge>
        </h5>
        <div class="d-flex align-items-center gap-2">
          <div class="position-relative ms-2" ref="menuRef">
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
                <button class="list-group-item list-group-item-action d-flex align-items-center gap-2 text-danger" @click="onDelete">
                  <i class="fas fa-trash"></i>
                  <span>Delete</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- WHAT: Single column layout for Subtasks only -->
    <!-- WHY: Notes moved to master notes section -->
    <!-- HOW: Removed two-column wrapper, subtasks take full width -->
    <div class="p-3" v-show="!collapsed">
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
                <UiBadge :tone="badgeClass(opt.value)" size="sm">{{ opt.label }}</UiBadge>
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
            'bg-secondary-subtle',
            'border', 'border-1', 'border-light',
            'rounded-2', 'shadow-sm',
            'mb-2',
            'border-start'
          ]"
          :style="leftEdgeStyle(t.task_type)"
        >
          <div class="d-flex align-items-center justify-content-between" role="button" @click="toggleExpand(t.id)">
            <div class="d-flex align-items-center ps-2">
              <UiBadge :tone="badgeClass(t.task_type)" size="sm" class="me-2">{{ labelFor(t.task_type) }}</UiBadge>
            </div>
            <div class="d-flex align-items-center small text-muted">
              <i :class="expandedIds.has(t.id) ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
            </div>
          </div>
          <!-- Expandable section for task-specific data fields -->
          <div v-if="expandedIds.has(t.id)" class="mt-2 p-2 border-top">
            <!-- WHAT: REO Scopes/Bids for Trashout or Renovation tasks -->
            <!-- WHY: These tasks require bid collection and scope management -->
            <div v-if="t.task_type === 'trashout' || t.task_type === 'renovation'" class="mb-3">
              <ReoScopesSection
                :hub-id="props.hubId"
                :task-id="t.id"
                :task-type="t.task_type as 'trashout' | 'renovation'"
              />
            </div>
            <!-- WHAT: Offers section for Pre-Marketing, Listed, Under Contract tasks -->
            <!-- WHY: Track offers received during pre-marketing, listing, and sale phases -->
            <div v-else-if="t.task_type === 'pre_marketing' || t.task_type === 'listed' || t.task_type === 'under_contract'" class="mb-3">
              <OffersSection
                :hub-id="props.hubId"
                offer-source="reo"
                :readonly="t.task_type === 'under_contract'"
                @task-created="handleTaskCreated"
              />
            </div>
            <!-- WHAT: Sale completion fields for Sold task -->
            <!-- WHY: Capture final proceeds and close date when REO is sold -->
            <div v-else-if="t.task_type === 'sold'" class="mb-3">
              <div class="row g-2 mb-3">
                <div class="col-md-6">
                  <label class="form-label small text-muted">Close Date</label>
                  <div class="d-block">
                    <EditableDate
                      :model-value="reoData?.actual_close_date || ''"
                      @update:model-value="handleCloseDateChange"
                      title="Click to edit close date"
                    />
                  </div>
                </div>
                <div class="col-md-6">
                  <label class="form-label small text-muted">Gross Sale Proceeds</label>
                  <UiCurrencyInput 
                    :model-value="reoData?.gross_purchase_price || ''"
                    @update:model-value="handleProceedsChange"
                    prefix="$"
                    :debounce-ms="1000"
                    size="sm"
                    placeholder="0.00"
                  />
                </div>
              </div>
              <!-- WHAT: Offers section for sold properties -->
              <!-- WHY: Show accepted offer details -->
              <OffersSection
                :hub-id="props.hubId"
                offer-source="reo"
                :readonly="true"
              />
            </div>
            <div v-else class="small text-muted mb-3">Task data fields can be added here</div>
            
            <!-- Delete button at bottom of expanded section -->
            <div class="d-flex justify-content-end mt-2">
              <button class="btn btn-sm btn-outline-danger px-2 py-1" @click.stop="requestDeleteTask(t.id)" style="font-size: 0.75rem;">
                <i class="mdi mdi-delete me-1"></i>
                Delete Task
              </button>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="text-muted small">No subtasks yet. Choose one from the dropdown and click Add.</div>
    </div>
  </b-card>

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
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useAmOutcomesStore, type ReoTask, type ReoTaskType, type ReoData } from '@/stores/outcomes'
import http from '@/lib/http'
import UiBadge from '@/components/ui/UiBadge.vue'
import type { BadgeToneKey } from '@/GlobalStandardizations/badges'
import { useDataRefresh } from '@/composables/useDataRefresh'
// Reusable editable date component with inline picker
// Path: src/components/ui/EditableDate.vue
import EditableDate from '@/components/ui/EditableDate.vue'
// Feature-local notes component (moved for AM Tasking scope)
// Path: src/views/am_module/loanlvl/am_tasking/components/SubtaskNotes.vue
import SubtaskNotes from '@/views/am_module/loanlvl/am_tasking/components/SubtaskNotes.vue'
// Scopes section for Trashout/Renovation tasks (refactored to match OffersSection pattern)
// Path: src/views/am_module/loanlvl/am_tasking/components/ReoScopesSection.vue
import ReoScopesSection from '@/views/am_module/loanlvl/am_tasking/components/ReoScopesSection.vue'
// Offers section for Pre-Marketing/Listed tasks (shows REO-tagged offers)
// Path: src/views/am_module/loanlvl/am_tasking/components/OffersSection.vue
import OffersSection from '@/views/am_module/loanlvl/am_tasking/components/OffersSection.vue'
// Hyper UI currency input component
// Path: src/components/ui/UiCurrencyInput.vue
import UiCurrencyInput from '@/components/ui/UiCurrencyInput.vue'
// Import jQuery for date picker initialization
import $ from 'jquery'
import 'bootstrap-datepicker'

const props = withDefaults(defineProps<{ hubId: number; masterCollapsed?: boolean }>(), { masterCollapsed: false })
const emit = defineEmits<{ (e: 'delete'): void }>()
// Pinia store for outcomes/tasks
const store = useAmOutcomesStore()

// WHAT: Setup data refresh functionality
// WHY: Auto-refresh when other components modify data
const { emitTaskAdded, emitTaskDeleted, emitTaskUpdated } = useDataRefresh(props.hubId, async () => {
  // WHAT: Refresh tasks when data changes
  tasks.value = await store.listReoTasks(props.hubId, true)
})
// Local state: list of tasks and busy flag
const tasks = ref<ReoTask[]>([])
const busy = ref(false)
const newType = ref<ReoTaskType | ''>('')
// REO completion data
const reoData = ref<any>(null)
// Allow multiple subtasks to be expanded at the same time
const localExpandedIds = ref<Set<number>>(new Set())
const userInteracted = ref(false)

watch(() => props.masterCollapsed, (newVal: boolean) => {
  if (newVal) {
    userInteracted.value = false
    localExpandedIds.value.clear()
  }
})

// WHAT: Computed expandedIds that includes all task IDs when master is not collapsed
// WHY: Master expand button should expand all tasks within the card
const expandedIds = computed(() => {
  if (!props.masterCollapsed && !userInteracted.value) {
    // When master is expanded, return set with all task IDs
    return new Set(tasks.value.map(t => t.id))
  }
  return localExpandedIds.value
})
// Collapsed state for the entire card body (subtasks section hidden when true)
const localCollapsed = ref<boolean>(false)
const collapsed = computed(() => props.masterCollapsed || localCollapsed.value)
// Add Task custom dropdown state
const addMenuOpen = ref(false)
const addMenuRef = ref<HTMLElement | null>(null)

// WHAT: Track delete confirmation modal state for REO subtasks
// WHY: Ensure delete button opens a confirm dialog instead of immediately removing data
// HOW: Store open flag, selected task id, and busy spinner state
const deleteTaskConfirm = ref<{ open: boolean; taskId: number | null; busy: boolean }>({ open: false, taskId: null, busy: false })

// Options for creating tasks (mirrors Django TextChoices in REOtask.TaskType)
const taskOptions: ReadonlyArray<{ value: ReoTaskType; label: string }> = [
  { value: 'eviction', label: 'Eviction' },
  { value: 'trashout', label: 'Trashout' },
  { value: 'renovation', label: 'Renovation' },
  { value: 'pre_marketing', label: 'Pre-Marketing' },
  { value: 'listed', label: 'Listed' },
  { value: 'under_contract', label: 'Under Contract' },
  { value: 'sold', label: 'Sold' },
]

// Set of existing task types used to disable duplicate adds
const existingTypes = computed<Set<ReoTaskType>>(() => new Set(tasks.value.map(t => t.task_type)))

// Map a task type to its human label
function labelFor(tp: ReoTaskType): string {
  const m = taskOptions.find(o => o.value === tp)
  return m ? m.label : tp
}

// Return Bootstrap pill badge class matching the task type
function badgeClass(tp: ReoTaskType): BadgeToneKey {
  const tones: Record<ReoTaskType, BadgeToneKey> = {
    eviction: 'danger',
    trashout: 'warning',
    renovation: 'info',
    pre_marketing: 'primary',
    listed: 'primary',
    under_contract: 'success',
    sold: 'success',
  }
  return tones[tp]
}

// Return Bootstrap border classes for subtle left border matching the pill color
function itemBorderClass(tp: ReoTaskType): string {
  // Keep a thin outline (border-1) from the container, then thicken the left edge
  const map: Record<ReoTaskType, string> = {
    eviction: 'border-start',
    trashout: 'border-start',
    renovation: 'border-start',
    pre_marketing: 'border-start',
    listed: 'border-start',
    under_contract: 'border-start',
    sold: 'border-start',
  }
  return map[tp]
}

// Compute per-type left-edge style using Bootstrap CSS variables for exact color match
function leftEdgeStyle(tp: ReoTaskType): Record<string, string> {
  const leftEdgeColors: Record<ReoTaskType, string> = {
    eviction: 'var(--bs-danger, #dc3545)',
    trashout: 'var(--bs-warning, #ffc107)',
    renovation: 'var(--bs-info, #0dcaf0)',
    pre_marketing: 'var(--bs-primary, #0d6efd)',
    listed: 'var(--bs-primary, #0d6efd)',
    under_contract: 'var(--bs-success, #198754)',
    sold: 'var(--bs-success, #198754)',
  }
  // Subtle but visible left edge; keep other sides neutral via border-light
  return {
    // Use inset box-shadow to draw a reliable left stripe and keep Bootstrap's small drop shadow
    boxShadow: `inset 3px 0 0 ${leftEdgeColors[tp]}, var(--bs-box-shadow-sm, 0 .125rem .25rem rgba(0,0,0,.075))`,
  }
}

// Load tasks from API
async function loadTasks() {
  tasks.value = await store.listReoTasks(props.hubId, true)
}

// WHAT: Handle task-created event from OffersSection
// WHY: Refresh tasks when auto-created from accepted offer
async function handleTaskCreated() {
  await loadTasks()
}

// WHAT: Load REO outcome data
// WHY: Need access to completion fields like close date and gross purchase price
async function loadReoData() {
  try {
    const response = await http.get(`/am/outcomes/reo/?asset_hub_id=${props.hubId}`)
    if (response.data && response.data.length > 0) {
      reoData.value = response.data[0]
    } else {
      // No REO outcome exists yet, create one
      const payload = { asset_hub_id: props.hubId }
      const createResponse = await http.post('/am/outcomes/reo/', payload)
      reoData.value = createResponse.data
    }
  } catch (err: any) {
    console.error('Failed to load/create REO data:', err)
    reoData.value = {
      asset_hub: null,
      actual_close_date: null,
      gross_purchase_price: null
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
    return usDate
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
    return backendDate
  }
}

// WHAT: Handle close date changes from EditableDate component
// WHY: EditableDate already provides yyyy-mm-dd format
function handleCloseDateChange(newDate: string) {
  updateReoField('actual_close_date', newDate)
}

// WHAT: Handle proceeds changes from UiCurrencyInput component
// WHY: Save proceeds values with built-in debouncing
function handleProceedsChange(value: string) {
  updateReoField('gross_purchase_price', value)
}

// WHAT: Update REO completion fields
// WHY: Save completion data when user enters close date or proceeds
async function updateReoField(fieldName: string, value: string) {
  try {
    if (!reoData.value || !reoData.value.asset_hub) {
      await loadReoData()
    }
    
    if (!reoData.value?.asset_hub) {
      throw new Error('Unable to create or find REO outcome')
    }
    
    let processedValue = value || null
    if (fieldName === 'gross_purchase_price' && processedValue) {
      const numValue = parseFloat(processedValue)
      processedValue = isNaN(numValue) ? null : numValue.toString()
    }
    
    const payload = { [fieldName]: processedValue }
    await http.patch(`/am/outcomes/reo/${reoData.value.asset_hub}/`, payload)
    
    // Update local data immediately
    if (reoData.value) {
      reoData.value[fieldName] = processedValue
    }
  } catch (err: any) {
    console.error(`Failed to update ${fieldName}:`, err)
    alert(`Failed to update ${fieldName}. Please try again.`)
  }
}

// Add a new task of a given type
async function addTask(tp: ReoTaskType) {
  try {
    busy.value = true
    const created = await store.createReoTask(props.hubId, tp)
    await loadTasks()
    // WHAT: Emit task added event
    // WHY: Notify other components to refresh their data
    emitTaskAdded('reo', created.id)
    expandedIds.value.add(created.id)
  } finally {
    busy.value = false
  }
}

function onSelectAdd() {
  if (!newType.value) return
  const selected = newType.value
  // Immediately create then reset selection
  addTask(selected)
  newType.value = ''
}

// Toggle the custom Add Task menu
function toggleAddMenu() {
  addMenuOpen.value = !addMenuOpen.value
}

// Handle clicking a pill inside the custom menu
function onSelectPill(tp: ReoTaskType) {
  if (existingTypes.value.has(tp) || busy.value) return
  addTask(tp)
  addMenuOpen.value = false
}

function toggleExpand(id: number) {
  userInteracted.value = true
  if (localExpandedIds.value.has(id)) localExpandedIds.value.delete(id)
  else localExpandedIds.value.add(id)
}

function isoDate(iso: string | null): string {
  if (!iso) return 'N/A'
  try { const d = new Date(iso); return d.toLocaleDateString() } catch { return iso }
}

// Update task_started date via PATCH request
async function updateTaskStarted(taskId: number, newDate: string) {
  try {
    await http.patch(`/am/outcomes/reo-tasks/${taskId}/`, { task_started: newDate })
    // Refresh tasks to show updated date
    await loadTasks()
  } catch (err: any) {
    console.error('Failed to update task start date:', err)
    alert('Failed to update start date. Please try again.')
  }
}

// WHAT: Open delete confirmation modal for a selected REO task card row
// WHY: Prevent accidental deletions by requiring explicit confirmation
// HOW: Store task id and display modal
function requestDeleteTask(taskId: number) {
  deleteTaskConfirm.value = { open: true, taskId, busy: false }
}

// WHAT: Close delete confirmation modal without deleting
// WHY: Allow users to cancel deletion safely
// HOW: Reset modal state object to defaults
function cancelDeleteTask() {
  deleteTaskConfirm.value = { open: false, taskId: null, busy: false }
}

// WHAT: Delete selected REO subtask after confirmation
// WHY: Provide consistent delete UX and update list
// HOW: Call store delete, reload tasks, close modal, handle errors with alert
async function confirmDeleteTask() {
  const taskId = deleteTaskConfirm.value.taskId
  if (!taskId) return
  try {
    deleteTaskConfirm.value.busy = true
    await store.deleteReoTask(props.hubId, taskId)
    await loadTasks()
    // WHAT: Emit task deleted event
    // WHY: Notify other components that task was removed
    emitTaskDeleted('reo', taskId)
    cancelDeleteTask()
  } catch (err: any) {
    console.error('Failed to delete REO task:', err)
    alert('Failed to delete task. Please try again.')
    deleteTaskConfirm.value.busy = false
  }
}

// Settings menu state and handlers
const menuOpen = ref(false)
const menuRef = ref<HTMLElement | null>(null)
function toggleMenu() { menuOpen.value = !menuOpen.value }
function onDelete() { menuOpen.value = false; emit('delete') }
function handleDocClick(e: MouseEvent) {
  const root = menuRef.value
  const addRoot = addMenuRef.value
  if (menuOpen.value && root && !root.contains(e.target as Node)) menuOpen.value = false
  if (addMenuOpen.value && addRoot && !addRoot.contains(e.target as Node)) addMenuOpen.value = false
}
onMounted(() => { 
  document.addEventListener('click', handleDocClick); 
  loadTasks();
  loadReoData();
})
onBeforeUnmount(() => document.removeEventListener('click', handleDocClick))

</script>
