<template>
  <!-- Subtle info-colored border (no fill) to match the REO pill -->
  <b-card class="w-100 h-100 border border-1 border-info rounded-2 shadow-sm">
    <template #header>
      <div class="d-flex align-items-center justify-content-between">
        <h5 class="mb-0 d-flex align-items-center">
          <i class="fas fa-home me-2 text-info"></i>
          <span class="badge rounded-pill text-bg-info size_med">REO</span>
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
            <div
              v-if="menuOpen"
              class="card shadow-sm mt-1"
              style="position: absolute; right: 0; min-width: 160px; z-index: 1060;"
              @click.stop
            >
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
    <!-- Sub Tasks -->
    <div class="p-3">
      <div class="d-flex align-items-center justify-content-between mb-3">
        <div class="small text-muted">Sub Tasks</div>
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
            'bg-secondary-subtle', // subtle neutral fill with slight contrast vs. card
            'border', 'border-1', 'border-light', // subtle neutral outline
            'rounded-2', 'shadow-sm',
            'mb-2', // minimal spacing between cards
            'border-start' // ensure left edge is rendered
          ]"
          :style="leftEdgeStyle(t.task_type)"
        >
          <div class="d-flex align-items-center justify-content-between" role="button" @click="toggleExpand(t.id)">
            <div class="d-flex align-items-center ps-2">
              <span :class="badgeClass(t.task_type)" class="me-2">{{ labelFor(t.task_type) }}</span>
              <span class="fw-medium"></span>
            </div>
            <div class="d-flex align-items-center small text-muted">
              <span class="me-3">Created: {{ isoDate(t.created_at) }}</span>
              <i :class="expandedId === t.id ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
            </div>
          </div>
          <div v-if="expandedId === t.id" class="mt-2">
            <SubtaskNotes :hubId="props.hubId" outcome="reo" :taskType="t.task_type" :taskId="t.id" />
          </div>
        </div>
      </div>
      <div v-else class="text-muted small">No subtasks yet. Choose one from the dropdown and click Add.</div>
    </div>
  </b-card>
</template>

<script setup lang="ts">
import { withDefaults, defineProps, ref, computed, onMounted, defineEmits, onBeforeUnmount } from 'vue'
import { useAmOutcomesStore, type ReoTask, type ReoTaskType } from '@/stores/outcomes'
import SubtaskNotes from '@/components/notes/SubtaskNotes.vue'

const props = withDefaults(defineProps<{ hubId: number }>(), {})
const emit = defineEmits<{ (e: 'delete'): void }>()
// Pinia store for outcomes/tasks
const store = useAmOutcomesStore()
// Local state: list of tasks and busy flag
const tasks = ref<ReoTask[]>([])
const busy = ref(false)
const newType = ref<ReoTaskType | ''>('')
const expandedId = ref<number | null>(null)
// Add Task custom dropdown state
const addMenuOpen = ref(false)
const addMenuRef = ref<HTMLElement | null>(null)

// Options for creating tasks (mirrors Django TextChoices in REOtask.TaskType)
const taskOptions: ReadonlyArray<{ value: ReoTaskType; label: string }> = [
  { value: 'eviction', label: 'Eviction' },
  { value: 'trashout', label: 'Trashout' },
  { value: 'renovation', label: 'Renovation' },
  { value: 'marketing', label: 'Marketing' },
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
function badgeClass(tp: ReoTaskType): string {
  const map: Record<ReoTaskType, string> = {
    eviction: 'badge rounded-pill size_small text-bg-danger',
    trashout: 'badge rounded-pill size_small text-bg-warning',
    renovation: 'badge rounded-pill size_small text-bg-info',
    marketing: 'badge rounded-pill size_small text-bg-primary',
    under_contract: 'badge rounded-pill size_small text-bg-success',
    sold: 'badge rounded-pill size_small text-bg-secondary',
  }
  return map[tp]
}

// Return Bootstrap border classes for subtle left border matching the pill color
function itemBorderClass(tp: ReoTaskType): string {
  // Keep a thin outline (border-1) from the container, then thicken the left edge
  const map: Record<ReoTaskType, string> = {
    eviction: 'border-start',
    trashout: 'border-start',
    renovation: 'border-start',
    marketing: 'border-start',
    under_contract: 'border-start',
    sold: 'border-start',
  }
  return map[tp]
}

// Compute per-type left-edge style using Bootstrap CSS variables for exact color match
function leftEdgeStyle(tp: ReoTaskType): Record<string, string> {
  const colorMap: Record<ReoTaskType, string> = {
    eviction: 'var(--bs-danger, #dc3545)',
    trashout: 'var(--bs-warning, #ffc107)',
    renovation: 'var(--bs-info, #0dcaf0)',
    marketing: 'var(--bs-primary, #0d6efd)',
    under_contract: 'var(--bs-success, #198754)',
    sold: 'var(--bs-secondary, #6c757d)',
  }
  // Subtle but visible left edge; keep other sides neutral via border-light
  return {
    // Use inset box-shadow to draw a reliable left stripe and keep Bootstrap's small drop shadow
    boxShadow: `inset 3px 0 0 ${colorMap[tp]}, var(--bs-box-shadow-sm, 0 .125rem .25rem rgba(0,0,0,.075))`,
  }
}

// Load tasks from API
async function loadTasks() {
  tasks.value = await store.listReoTasks(props.hubId, true)
}

// Add a new task of a given type
async function addTask(tp: ReoTaskType) {
  try {
    busy.value = true
    const created = await store.createReoTask(props.hubId, tp)
    await loadTasks()
    expandedId.value = created.id
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
  expandedId.value = expandedId.value === id ? null : id
}

function isoDate(iso: string): string {
  try { const d = new Date(iso); return d.toLocaleDateString() } catch { return iso }
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
onMounted(() => { document.addEventListener('click', handleDocClick); loadTasks() })
onBeforeUnmount(() => document.removeEventListener('click', handleDocClick))

</script>
