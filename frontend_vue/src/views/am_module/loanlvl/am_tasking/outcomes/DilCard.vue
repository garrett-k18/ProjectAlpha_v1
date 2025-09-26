<template>
  <!-- Subtle primary-colored border (no fill) to match the DIL pill -->
  <b-card class="w-100 h-100 border border-1 border-primary rounded-2 shadow-sm">
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
          <i class="fas fa-handshake me-2 text-primary"></i>
          <span class="badge rounded-pill text-bg-primary size_med">Deed-in-Lieu</span>
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


    <!-- Sub Tasks (collapsible body) -->
    <div class="p-3" v-show="!collapsed">
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
                :disabled="existingTypes.has(opt.value) || tasksBusy"
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
            'border-start', // ensure left edge area
          ]"
          :style="leftEdgeStyle(t.task_type)"
        >
          <div class="d-flex align-items-center justify-content-between" role="button" @click="toggleExpand(t.id)">
            <div class="d-flex align-items-center ps-2">
              <span :class="badgeClass(t.task_type)" class="me-2">{{ taskLabel(t.task_type) }}</span>
            </div>
            <div class="d-flex align-items-center small text-muted">
              <span class="me-3">Created: {{ isoDate(t.created_at) }}</span>
              <i :class="expandedId === t.id ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
            </div>
          </div>
          <div v-if="expandedId === t.id" class="mt-2">
            <!-- When the subtask is 'Deed-in-Lieu Drafted', render extra fields -->
            <div v-if="t.task_type === 'dil_drafted'" class="mb-2 p-1 bg-transparent">
              <div class="row g-1 align-items-center">
                <div class="col-md-6">
                  <label class="form-label small text-muted">Current Legal Cost</label>
                  <!-- Read-only placeholder; actual value to be wired to GL entry later -->
                  <input type="text" class="form-control form-control-sm" :value="legalCostPlaceholder" readonly aria-describedby="legalCostHelp" />
                  <div id="legalCostHelp" class="form-text">Pulled from GL (to be wired).</div>
                </div>
                <div class="col-md-6">
                  <label class="form-label small text-muted">Cash-for-Keys Offered</label>
                  <!-- Editable; tracked locally per subtask id. Use simple text/number for now; can swap to currency directive -->
                  <input
                    type="text"
                    class="form-control form-control-sm"
                    v-model="cashForKeysByTask[t.id]"
                    placeholder="$0"
                    aria-describedby="cfkHelp"
                  />
                  <div id="cfkHelp" class="form-text">User-entered; backend wiring TBD.</div>
                </div>
              </div>
            </div>

            <SubtaskNotes :hubId="props.hubId" outcome="dil" :taskType="t.task_type" :taskId="t.id" />
          </div>
        </div>
      </div>
      <div v-else class="text-muted small">No subtasks yet. Use Add Task to create one.</div>
    </div>
  </b-card>
</template>

<script setup lang="ts">
// Component for managing DIL subtasks only (details/quick-edit removed by request).
// Docs: Pinia https://pinia.vuejs.org/ ; DRF ViewSets https://www.django-rest-framework.org/api-guide/viewsets/

import { onMounted, computed, ref, withDefaults, defineProps, defineEmits, onBeforeUnmount } from 'vue'
import { useAmOutcomesStore, type DilTask, type DilTaskType } from '@/stores/outcomes'
import SubtaskNotes from '@/components/notes/SubtaskNotes.vue'

const props = withDefaults(defineProps<{ hubId: number }>(), {})
const emit = defineEmits<{ (e: 'delete'): void }>()

const store = useAmOutcomesStore()
// Collapsed state for the entire card body (subtasks section hidden when true)
const collapsed = ref<boolean>(false)
const tasks = computed<DilTask[]>(() => store.getDilTasks(props.hubId))
const expandedId = ref<number | null>(null)
// Add Task custom dropdown state
const addMenuOpen = ref(false)
const addMenuRef = ref<HTMLElement | null>(null)

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

const taskOptions: Array<{ value: DilTaskType; label: string }> = [
  { value: 'owner_contacted', label: 'Owner/Heirs contacted' },
  { value: 'dil_drafted', label: 'Deed-in-Lieu Drafted' },
  { value: 'dil_successful', label: 'Deed-in-Lieu Successful' },
]

const tasksBusy = ref(false)

function taskLabel(v: DilTaskType): string {
  const m = taskOptions.find(o => o.value === v)
  return m?.label ?? v
}

// Set of existing task types used to disable duplicate adds
const existingTypes = computed<Set<DilTaskType>>(() => new Set(tasks.value.map(t => t.task_type)))

// Badge classes per DIL task type (pill style)
function badgeClass(tp: DilTaskType): string {
  const map: Record<DilTaskType, string> = {
    owner_contacted: 'badge rounded-pill size_small text-bg-primary',
    dil_drafted: 'badge rounded-pill size_small text-bg-warning',
    dil_successful: 'badge rounded-pill size_small text-bg-success',
  }
  return map[tp]
}

// Left border color per DIL task type
function itemBorderClass(tp: DilTaskType): string {
  const map: Record<DilTaskType, string> = {
    owner_contacted: 'border-start border-2 border-primary',
    dil_drafted: 'border-start border-2 border-warning',
    dil_successful: 'border-start border-2 border-success',
  }
  return map[tp]
}

// Robust left-edge stripe using inset box-shadow + Bootstrap CSS vars with fallbacks
function leftEdgeStyle(tp: DilTaskType): Record<string, string> {
  const colorMap: Record<DilTaskType, string> = {
    owner_contacted: 'var(--bs-primary, #0d6efd)',
    dil_drafted: 'var(--bs-warning, #ffc107)',
    dil_successful: 'var(--bs-success, #198754)',
  }
  return {
    boxShadow: `inset 3px 0 0 ${colorMap[tp]}, var(--bs-box-shadow-sm, 0 .125rem .25rem rgba(0,0,0,.075))`,
  }
}

const latestStatusValue = computed<string | null>(() => tasks.value[0]?.task_type ?? null)
const latestStatusLabel = computed<string | null>(() => latestStatusValue.value ? taskLabel(latestStatusValue.value as DilTaskType) : null)

function isoDate(iso: string): string {
  try {
    const d = new Date(iso)
    return d.toLocaleDateString()
  } catch { return iso }
}

function toggleAddMenu() { addMenuOpen.value = !addMenuOpen.value }
function onSelectPill(tp: DilTaskType) {
  if (existingTypes.value.has(tp) || tasksBusy.value) return
  tasksBusy.value = true
  store.createDilTask(props.hubId, tp)
    .finally(() => { tasksBusy.value = false; addMenuOpen.value = false })
}
function toggleExpand(id: number) { expandedId.value = expandedId.value === id ? null : id }

onMounted(async () => {
  // Load tasks when card mounts
  await store.listDilTasks(props.hubId)
})

// --- Extra UI state for 'dil_drafted' subtask fields ---
// Map of subtask id -> Cash-for-Keys offered input value. This is frontend-only until backend wiring is added.
const cashForKeysByTask = ref<Record<number, string>>({})
// Placeholder for Current Legal Cost (GL integration pending). Using dash until wired.
const legalCostPlaceholder = '—'
</script>

<style scoped>
/* Keep component-scoped styles lean; use Bootstrap utilities for most styling */
</style>
