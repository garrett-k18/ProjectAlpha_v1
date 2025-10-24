<template>
  <!-- Subtle secondary-colored border (no fill) to match the Modification pill -->
  <b-card class="w-100 h-100 border border-1 border-secondary rounded-2 shadow-sm">
    <template #header>
      <div class="d-flex align-items-center justify-content-between">
        <h5 class="mb-0 d-flex align-items-center">
          <i class="fas fa-pen-alt me-2 text-secondary"></i>
          <span class="badge rounded-pill text-bg-secondary size_med">Modification</span>
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
                <span :class="badgeClass(opt.value)" class="me-0">{{ opt.label }}</span>
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
            'bg-body-secondary',
            'border', 'border-1',
            'rounded-2', 'shadow-sm',
            itemBorderClass(t.task_type)
          ]"
        >
          <div class="d-flex align-items-center justify-content-between" role="button" @click="toggleExpand(t.id)">
            <div class="d-flex align-items-center ps-2">
              <span :class="badgeClass(t.task_type)" class="me-2">{{ labelFor(t.task_type) }}</span>
            </div>
            <div class="d-flex align-items-center small text-muted">
              <span class="me-3">
                Started: 
                <EditableDate 
                  :model-value="t.task_started" 
                  @update:model-value="(newDate) => updateTaskStarted(t.id, newDate)"
                />
              </span>
              <i :class="expandedId === t.id ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
            </div>
          </div>
          <div v-if="expandedId === t.id" class="mt-2 p-2 border-top">
            <div class="small text-muted">Task data fields can be added here</div>
            <!-- TODO: Add task-specific form fields here -->
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
</template>

<script setup lang="ts">
import { withDefaults, defineProps, ref, computed, onMounted, onBeforeUnmount, defineEmits } from 'vue'
import { useAmOutcomesStore, type ModificationTask, type ModificationTaskType } from '@/stores/outcomes'
import http from '@/lib/http'
// Reusable editable date component with inline picker
// Path: src/components/ui/EditableDate.vue
import EditableDate from '@/components/ui/EditableDate.vue'
// Feature-local notes component (moved for AM Tasking scope)
// Path: src/views/am_module/loanlvl/am_tasking/components/SubtaskNotes.vue
import SubtaskNotes from '@/views/am_module/loanlvl/am_tasking/components/SubtaskNotes.vue'

const props = withDefaults(defineProps<{ hubId: number }>(), {})
const emit = defineEmits<{ (e: 'delete'): void }>()
const store = useAmOutcomesStore()

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
const expandedId = ref<number | null>(null)
const busy = ref(false)
function handleDocClick(e: MouseEvent) {
  const root = menuRef.value
  const addRoot = addMenuRef.value
  if (menuOpen.value && root && !root.contains(e.target as Node)) menuOpen.value = false
  if (addMenuOpen.value && addRoot && !addRoot.contains(e.target as Node)) addMenuOpen.value = false
}
onMounted(() => document.addEventListener('click', handleDocClick))
onBeforeUnmount(() => document.removeEventListener('click', handleDocClick))

// Load subtasks on mount
onMounted(async () => {
  tasks.value = await store.listModificationTasks(props.hubId, true)
})

// ---------- Subtasks helpers ----------
const taskOptions: ReadonlyArray<{ value: ModificationTaskType; label: string }> = [
  { value: 'mod_negotiations', label: 'Negotiations' },
  { value: 'mod_accepted', label: 'Accepted' },
  { value: 'mod_started', label: 'Started' },
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
    .then(async () => { tasks.value = await store.listModificationTasks(props.hubId, true) })
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
    await http.patch(`/am/outcomes/modification-tasks/${taskId}/`, { task_started: newDate })
    // Refresh tasks to show updated date
    tasks.value = await store.listModificationTasks(props.hubId, true)
  } catch (err: any) {
    console.error('Failed to update task start date:', err)
    alert('Failed to update start date. Please try again.')
  }
}

function badgeClass(tp: ModificationTaskType): string {
  const map: Record<ModificationTaskType, string> = {
    mod_negotiations: 'badge rounded-pill size_small text-bg-info',
    mod_accepted: 'badge rounded-pill size_small text-bg-success',
    mod_started: 'badge rounded-pill size_small text-bg-primary',
    mod_failed: 'badge rounded-pill size_small text-bg-danger',
  }
  return map[tp]
}
function itemBorderClass(tp: ModificationTaskType): string {
  const map: Record<ModificationTaskType, string> = {
    mod_negotiations: 'border-start border-2 border-info',
    mod_accepted: 'border-start border-2 border-success',
    mod_started: 'border-start border-2 border-primary',
    mod_failed: 'border-start border-2 border-danger',
  }
  return map[tp]
}
</script>
