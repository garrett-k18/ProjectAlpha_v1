<template>
  <!-- Subtle secondary-colored border (no fill) to match the Modification pill -->
  <b-card class="w-100 h-100 border border-1 border-secondary rounded-2 shadow-sm">
    <template #header>
      <div class="d-flex align-items-center justify-content-between">
        <h5 class="mb-0 d-flex align-items-center">
          <i class="fas fa-pen-alt me-2" style="color: #198754;"></i>
          <UiBadge tone="modification-green" size="lg">Modification</UiBadge>
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
    <!-- Two-column layout: Subtasks | Notes -->
    <div class="p-3">
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
        >
          <div class="d-flex align-items-center justify-content-between" role="button" @click="toggleExpand(t.id)">
            <div class="d-flex align-items-center ps-2">
              <UiBadge :tone="badgeClass(t.task_type)" size="sm" class="me-2">{{ labelFor(t.task_type) }}</UiBadge>
            </div>
            <div class="d-flex align-items-center small text-muted">
              <span class="me-3">
                Started: 
                <EditableDate 
                  :model-value="t.task_started" 
                  @update:model-value="(newDate) => updateTaskStarted(t.id, newDate)"
                />
              </span>
              <i :class="(expandedId === t.id || expandedId === 'all') ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
            </div>
          </div>
          <div v-if="expandedId === t.id || expandedId === 'all'" class="mt-2 p-2 border-top">
            <div class="small text-muted">Task data fields can be added here</div>
            <!-- TODO: Add task-specific form fields here -->
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
          <SubtaskNotes :hubId="props.hubId" outcome="modification" :taskType="null" :taskId="null" />
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
import { useAmOutcomesStore, type ModificationTask, type ModificationTaskType } from '@/stores/outcomes'
import http from '@/lib/http'
import UiBadge from '@/components/ui/UiBadge.vue'
import type { BadgeToneKey } from '@/config/badgeTokens'
import { useDataRefresh } from '@/composables/useDataRefresh'
import EditableDate from '@/components/ui/EditableDate.vue'
// Feature-local notes component (moved for AM Tasking scope)
// Path: src/views/am_module/loanlvl/am_tasking/components/SubtaskNotes.vue
import SubtaskNotes from '@/views/am_module/loanlvl/am_tasking/components/SubtaskNotes.vue'

const props = withDefaults(defineProps<{ hubId: number; masterCollapsed?: boolean }>(), { masterCollapsed: false })
const emit = defineEmits<{ (e: 'delete'): void }>()
const store = useAmOutcomesStore()

// WHAT: Collapsed state for the entire card body (subtasks section hidden when true)
// WHY: Allow both individual card collapse and master collapse control
const localCollapsed = ref<boolean>(false)
const collapsed = computed(() => props.masterCollapsed || localCollapsed.value)

// Settings menu state/handlers
const menuOpen = ref(false)
const menuRef = ref<HTMLElement | null>(null)
function toggleMenu() { menuOpen.value = !menuOpen.value }
function onDelete() { menuOpen.value = false; emit('delete') }
// Add Task custom dropdown state
const addMenuOpen = ref(false)
const addMenuRef = ref<HTMLElement | null>(null)
// Subtasks state
const tasks = ref<ModificationTask[]>([])
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
const busy = ref(false)
// WHAT: Track confirmation modal state for deletion (open flag, target id, spinner)
// WHY: Keep UX consistent with other outcome cards and avoid accidental deletions
// HOW: Local reactive object toggled by request/cancel/confirm handlers
const deleteTaskConfirm = ref<{ open: boolean; taskId: number | null; busy: boolean }>({ open: false, taskId: null, busy: false })
function handleDocClick(e: MouseEvent) {
  const root = menuRef.value
  const addRoot = addMenuRef.value
  if (menuOpen.value && root && !root.contains(e.target as Node)) menuOpen.value = false
  if (addMenuOpen.value && addRoot && !addRoot.contains(e.target as Node)) addMenuOpen.value = false
}
onMounted(() => document.addEventListener('click', handleDocClick))
onBeforeUnmount(() => document.removeEventListener('click', handleDocClick))

// WHAT: Setup data refresh functionality
// WHY: Auto-refresh when other components modify data
const { emitTaskAdded, emitTaskDeleted, emitTaskUpdated } = useDataRefresh(props.hubId, async () => {
  // WHAT: Refresh tasks when data changes
  tasks.value = await store.listModificationTasks(props.hubId, true)
})

// Load subtasks on mount
onMounted(async () => {
  tasks.value = await store.listModificationTasks(props.hubId, true)
})

// ---------- Subtasks helpers ----------
const taskOptions: ReadonlyArray<{ value: ModificationTaskType; label: string }> = [
  { value: 'mod_drafted', label: 'Drafted' },
  { value: 'mod_executed', label: 'Executed' },
  { value: 'mod_rpl', label: 'Re-Performing' },
  { value: 'mod_failed', label: 'Failed' },
]
function labelFor(tp: ModificationTaskType): string {
  const m = taskOptions.find(o => o.value === tp)
  return m ? m.label : tp
}
const existingTypes = computed<Set<ModificationTaskType>>(() => new Set(tasks.value.map(t => t.task_type)))
function toggleAddMenu() { addMenuOpen.value = !addMenuOpen.value }
function onSelectPill(tp: ModificationTaskType) {
  if (existingTypes.value.has(tp) || busy.value) return
  busy.value = true
  store.createModificationTask(props.hubId, tp)
    .then(async (newTask) => { 
      tasks.value = await store.listModificationTasks(props.hubId, true)
      // WHAT: Emit task added event
      // WHY: Notify other components to refresh their data
      emitTaskAdded('modification', newTask?.id || 0)
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
    await http.patch(`/am/outcomes/modification-tasks/${taskId}/`, { task_started: newDate })
    // Refresh tasks to show updated date
    tasks.value = await store.listModificationTasks(props.hubId, true)
    // WHAT: Emit task updated event
    // WHY: Notify other components that task data changed
    emitTaskUpdated('modification', taskId)
  } catch (err: any) {
    console.error('Failed to update task start date:', err)
    alert('Failed to update start date. Please try again.')
  }
}

// WHAT: Open deletion confirm modal for a modification task row
function requestDeleteTask(taskId: number) {
  deleteTaskConfirm.value = { open: true, taskId, busy: false }
}

// WHAT: Cancel deletion request and hide modal
function cancelDeleteTask() {
  deleteTaskConfirm.value = { open: false, taskId: null, busy: false }
}

// WHAT: Permanently delete modification task after confirmation
async function confirmDeleteTask() {
  const taskId = deleteTaskConfirm.value.taskId
  if (!taskId) return
  try {
    deleteTaskConfirm.value.busy = true
    await store.deleteModificationTask(props.hubId, taskId)
    tasks.value = await store.listModificationTasks(props.hubId, true)
    // WHAT: Emit task deleted event
    // WHY: Notify other components that task was removed
    emitTaskDeleted('modification', taskId)
    cancelDeleteTask()
  } catch (err: any) {
    console.error('Failed to delete modification task:', err)
    alert('Failed to delete task. Please try again.')
    deleteTaskConfirm.value.busy = false
  }
}

function badgeClass(tp: ModificationTaskType): BadgeToneKey {
  const map: Record<ModificationTaskType, BadgeToneKey> = {
    mod_drafted: 'info',
    mod_executed: 'success',
    mod_rpl: 'primary',
    mod_failed: 'danger',
  }
  return map[tp]
}
function itemBorderClass(tp: ModificationTaskType): string {
  // Return empty string for clean appearance like ShortSaleCard
  return ''
}
</script>
