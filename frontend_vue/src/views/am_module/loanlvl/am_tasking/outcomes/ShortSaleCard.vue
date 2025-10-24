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
        @click.stop="collapsed = !collapsed"
      >
        <h5 class="mb-0 d-flex align-items-center">
          <i class="fas fa-tags me-2 text-warning"></i>
          <span class="badge rounded-pill text-bg-warning size_med text-dark">Short Sale</span>
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
              <i class="fas fa-ellipsis-vertical"></i>
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
          <SubtaskNotes :hubId="props.hubId" outcome="short_sale" :taskType="null" :taskId="null" />
        </div>
      </div>
    </div>
  </b-card>
</template>

<script setup lang="ts">
import { withDefaults, defineProps, ref, computed, onMounted, onBeforeUnmount, defineEmits } from 'vue'
import { useAmOutcomesStore, type ShortSaleTask, type ShortSaleTaskType } from '@/stores/outcomes'
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
// Collapsed state for the entire card body (subtasks section hidden when true)
const collapsed = ref<boolean>(false)
const busy = ref(false)
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
const expandedId = ref<number | null>(null)
function handleDocClick(e: MouseEvent) {
  const root = menuRef.value
  const addRoot = addMenuRef.value
  if (menuOpen.value && root && !root.contains(e.target as Node)) menuOpen.value = false
  if (addMenuOpen.value && addRoot && !addRoot.contains(e.target as Node)) addMenuOpen.value = false
}
onMounted(() => document.addEventListener('click', handleDocClick))
onBeforeUnmount(() => document.removeEventListener('click', handleDocClick))

async function load() {
  // Load subtasks
  tasks.value = await store.listShortSaleTasks(props.hubId, true)
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
    .then(async () => { tasks.value = await store.listShortSaleTasks(props.hubId, true) })
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
    await http.patch(`/am/outcomes/short-sale-tasks/${taskId}/`, { task_started: newDate })
    // Refresh tasks to show updated date
    tasks.value = await store.listShortSaleTasks(props.hubId, true)
  } catch (err: any) {
    console.error('Failed to update task start date:', err)
    alert('Failed to update start date. Please try again.')
  }
}

function badgeClass(tp: ShortSaleTaskType): string {
  const map: Record<ShortSaleTaskType, string> = {
    list_price_accepted: 'badge rounded-pill size_small text-bg-warning',
    listed: 'badge rounded-pill size_small text-bg-info',
    under_contract: 'badge rounded-pill size_small text-bg-primary',
    sold: 'badge rounded-pill size_small text-bg-success',
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
