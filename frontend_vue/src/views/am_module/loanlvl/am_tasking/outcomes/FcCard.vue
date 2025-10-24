<template>
  <!-- Subtle danger-colored border (no fill) to match the Foreclosure pill -->
  <b-card class="w-100 h-100 border border-1 border-danger rounded-2 shadow-sm">
    <template #header>
      <div
        class="d-flex align-items-center justify-content-between"
        role="button"
        :aria-expanded="!collapsed"
        title="Toggle sub tasks"
        style="cursor: pointer;"
        @click="collapsed = !collapsed"
      >
        <h5 class="mb-0 d-flex align-items-center">
          <i class="fas fa-gavel me-2 text-danger"></i>
          <span class="badge rounded-pill text-bg-danger size_med">Foreclosure</span>
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
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
                    <path d="M5.5 5.5a.5.5 0 0 1 .5.5v7a.5.5 0 0 1-1 0v-7a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v7a.5.5 0 0 1-1 0v-7a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v7a.5.5 0 0 0 1 0v-7z"/>
                    <path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4H2.5a1 1 0 1 1 0-2H6h4h3.5a1 1 0 0 1 1 1zM5 4v9a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4H5zm1-2a1 1 0 0 0-1 1h6a1 1 0 0 0-1-1H6z"/>
                  </svg>
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
                <span :class="badgeClass(opt.value)" class="me-0">{{ opt.label }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Subtask cards list (expandable for data fields) -->
      <div v-if="tasks.length" class="list-group list-group-flush">
        <div
          v-for="t in tasks"
          :key="t.id"
          :class="[
            'list-group-item',
            'px-2',
            'py-2',
            'bg-secondary-subtle',
            'border', 'border-1', 'border-light',
            'rounded-2', 'shadow-sm',
            'mb-2',
            'border-start',
          ]"
          :style="leftEdgeStyle(t.task_type)"
        >
          <div class="d-flex align-items-center justify-content-between" role="button" @click="toggleExpand(t.id)">
            <div class="d-flex align-items-center">
              <span :class="badgeClass(t.task_type)" class="me-2">{{ labelFor(t.task_type) }}</span>
            </div>
            <div class="d-flex align-items-center small text-muted gap-2">
              <span class="me-2">
                Started: 
                <EditableDate 
                  :model-value="t.task_started" 
                  @update:model-value="(newDate) => updateTaskStarted(t.id, newDate)"
                />
              </span>
              <i :class="expandedId === t.id ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
            </div>
          </div>
          <!-- Expandable section for task-specific data fields -->
          <div v-if="expandedId === t.id" class="mt-2 p-2 border-top">
            <!-- NOD/NOI specific date fields -->
            <div v-if="t.task_type === 'nod_noi'" class="row g-3 mb-3">
              <div class="col-md-6">
                <label class="form-label small">NOD/NOI Sent Date</label>
                <input 
                  type="text" 
                  class="form-control form-control-sm date" 
                  data-toggle="date-picker" 
                  data-single-date-picker="true"
                  :value="getTaskField(t, 'nod_noi_sent_date')"
                  @change="(e) => updateTaskField(t.id, 'nod_noi_sent_date', (e.target as HTMLInputElement).value)"
                  placeholder="Select date"
                >
              </div>
              <div class="col-md-6">
                <label class="form-label small">NOD/NOI Expire Date</label>
                <input 
                  type="text" 
                  class="form-control form-control-sm date" 
                  data-toggle="date-picker" 
                  data-single-date-picker="true"
                  :value="getTaskField(t, 'nod_noi_expire_date')"
                  @change="(e) => updateTaskField(t.id, 'nod_noi_expire_date', (e.target as HTMLInputElement).value)"
                  placeholder="Select date"
                >
              </div>
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
      <div v-else class="text-muted small">No subtasks yet. Use Add Task to create one.</div>
        </div>

        <!-- Right Column: Shared Notes for this Outcome -->
        <div class="col-md-6">
          <div class="d-flex align-items-center justify-content-between mb-3 pb-2 border-bottom">
            <h5 class="mb-0 fw-bold text-body">Notes</h5>
          </div>
          <SubtaskNotes :hubId="props.hubId" outcome="fc" :taskType="null" :taskId="null" />
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
import { withDefaults, defineProps, ref, computed, onMounted, onBeforeUnmount, defineEmits } from 'vue'
import { useAmOutcomesStore, type FcTask, type FcTaskType, type FcSale } from '@/stores/outcomes'
import http from '@/lib/http'
// Feature-local notes component (moved for AM Tasking scope)
// Path: src/views/am_module/loanlvl/am_tasking/components/SubtaskNotes.vue
import SubtaskNotes from '@/views/am_module/loanlvl/am_tasking/components/SubtaskNotes.vue'
// Reusable editable date component with inline picker
// Path: src/components/ui/EditableDate.vue
import EditableDate from '@/components/ui/EditableDate.vue'

const props = withDefaults(defineProps<{ hubId: number }>(), {})
const emit = defineEmits<{ (e: 'delete'): void }>()
const store = useAmOutcomesStore()
// Collapsed state for the entire card body (subtasks section hidden when true)
const collapsed = ref<boolean>(false)
const busy = ref(false)
// FC Subtasks state
const tasks = ref<FcTask[]>([])
const expandedId = ref<number | null>(null)
const addMenuOpen = ref(false)
const addMenuRef = ref<HTMLElement | null>(null)

// Delete task confirmation modal state
const deleteTaskConfirm = ref({ open: false, taskId: null as number | null, busy: false })

// Settings menu (3-dot) state and handlers
const menuOpen = ref(false)
const menuRef = ref<HTMLElement | null>(null)
function toggleMenu() { menuOpen.value = !menuOpen.value }
function onDelete() { menuOpen.value = false; emit('delete') }

function handleDocClick(e: MouseEvent) {
  const root = menuRef.value
  if (!root) return
  if (menuOpen.value && !root.contains(e.target as Node)) menuOpen.value = false
}
onMounted(() => document.addEventListener('click', handleDocClick))
onBeforeUnmount(() => document.removeEventListener('click', handleDocClick))

async function load() {
  // Load FC tasks
  tasks.value = await store.listFcTasks(props.hubId, true)
}

onMounted(load)

// ---------- Subtasks helpers ----------
const taskOptions: ReadonlyArray<{ value: FcTaskType; label: string }> = [
  { value: 'nod_noi', label: 'NOD/NOI' },
  { value: 'fc_filing', label: 'FC Filing' },
  { value: 'mediation', label: 'Mediation' },
  { value: 'judgement', label: 'Judgement' },
  { value: 'redemption', label: 'Redemption' },
  { value: 'sale_scheduled', label: 'Sale Scheduled' },
  { value: 'sold', label: 'Sold' },
]
function labelFor(tp: FcTaskType): string {
  const m = taskOptions.find(o => o.value === tp)
  return m ? m.label : tp
}
const existingTypes = computed<Set<FcTaskType>>(() => new Set(tasks.value.map(t => t.task_type)))
function toggleAddMenu() { addMenuOpen.value = !addMenuOpen.value }
function onSelectPill(tp: FcTaskType) {
  if (existingTypes.value.has(tp) || busy.value) return
  busy.value = true
  store.createFcTask(props.hubId, tp)
    .then(async () => { tasks.value = await store.listFcTasks(props.hubId, true) })
    .finally(() => { busy.value = false; addMenuOpen.value = false })
}
function toggleExpand(id: number) { expandedId.value = expandedId.value === id ? null : id }
function isoDate(iso: string | null): string { 
  if (!iso) return 'N/A'
  try { return new Date(iso).toLocaleDateString() } catch { return iso } 
}

// Update task_started date via PATCH request
async function updateTaskStarted(taskId: number, newDate: string) {
  try {
    await http.patch(`/am/outcomes/fc-tasks/${taskId}/`, { task_started: newDate })
    // Refresh tasks to show updated date
    tasks.value = await store.listFcTasks(props.hubId, true)
  } catch (err: any) {
    console.error('Failed to update task start date:', err)
    alert('Failed to update start date. Please try again.')
  }
}

// Get task field value (for NOD/NOI date fields)
function getTaskField(task: FcTask, fieldName: string): string | null {
  return (task as any)[fieldName] || null
}

// Update any task field via PATCH request
async function updateTaskField(taskId: number, fieldName: string, newValue: string) {
  try {
    await http.patch(`/am/outcomes/fc-tasks/${taskId}/`, { [fieldName]: newValue })
    // Refresh tasks to show updated value
    tasks.value = await store.listFcTasks(props.hubId, true)
  } catch (err: any) {
    console.error(`Failed to update ${fieldName}:`, err)
    alert(`Failed to update ${fieldName}. Please try again.`)
  }
}

function badgeClass(tp: FcTaskType): string {
  const map: Record<FcTaskType, string> = {
    nod_noi: 'badge rounded-pill size_small text-bg-warning',
    fc_filing: 'badge rounded-pill size_small text-bg-primary',
    mediation: 'badge rounded-pill size_small text-bg-info',
    judgement: 'badge rounded-pill size_small text-bg-secondary',
    redemption: 'badge rounded-pill size_small text-bg-success',
    sale_scheduled: 'badge rounded-pill size_small text-bg-dark',
    sold: 'badge rounded-pill size_small text-bg-success',
  }
  return map[tp]
}
function itemBorderClass(tp: FcTaskType): string {
  const map: Record<FcTaskType, string> = {
    nod_noi: 'border-start border-2 border-warning',
    fc_filing: 'border-start border-2 border-primary',
    mediation: 'border-start border-2 border-info',
    judgement: 'border-start border-2 border-secondary',
    redemption: 'border-start border-2 border-success',
    sale_scheduled: 'border-start border-2 border-dark',
    sold: 'border-start border-2 border-success',
  }
  return map[tp]
}

// Robust left-edge stripe using inset box-shadow + Bootstrap CSS vars with fallbacks
function leftEdgeStyle(tp: FcTaskType): Record<string, string> {
  const colorMap: Record<FcTaskType, string> = {
    nod_noi: 'var(--bs-warning, #ffc107)',
    fc_filing: 'var(--bs-primary, #0d6efd)',
    mediation: 'var(--bs-info, #0dcaf0)',
    judgement: 'var(--bs-secondary, #6c757d)',
    redemption: 'var(--bs-success, #198754)',
    sale_scheduled: 'var(--bs-dark, #212529)',
    sold: 'var(--bs-success, #198754)',
  }
  return {
    boxShadow: `inset 3px 0 0 ${colorMap[tp]}, var(--bs-box-shadow-sm, 0 .125rem .25rem rgba(0,0,0,.075))`,
  }
}

// Delete task confirmation handlers
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
    await store.deleteFcTask(props.hubId, taskId)
    await load()
    cancelDeleteTask()
  } catch (err) {
    console.error('Failed to delete task:', err)
    alert('Failed to delete task. Please try again.')
    deleteTaskConfirm.value.busy = false
  }
}
</script>

