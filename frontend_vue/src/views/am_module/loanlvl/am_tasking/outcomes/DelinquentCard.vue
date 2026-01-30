<template>
  <b-card class="w-100 h-100 border border-1 border-warning rounded-2 shadow-sm" style="background: var(--ui-bg-card-primary, #FDFBF7);">
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
          <i class="fas fa-exclamation-triangle me-2 text-warning"></i>
          <UiBadge tone="warning" size="lg">Delinquent</UiBadge>
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

    <div class="p-3" v-show="!collapsed">
      <div class="d-flex align-items-center justify-content-between mb-3 pb-2 border-bottom">
        <h5 class="mb-0 fw-bold text-body">Sub Tasks</h5>
        <div class="position-relative" ref="addMenuRef">
          <button type="button" class="btn btn-sm btn-outline-secondary d-inline-flex align-items-center gap-2" @click.stop="toggleAddMenu">
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
                <UiBadge :tone="pillTone(opt.value)" size="sm" class="me-0">{{ opt.label }}</UiBadge>
              </button>
            </div>
          </div>
        </div>
      </div>

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
          ]"
          :style="leftEdgeStyle(t.task_type)"
        >
          <div class="d-flex align-items-center justify-content-between" role="button" @click="toggleExpand(t.id)">
            <div class="d-flex align-items-center ps-2">
              <UiBadge :tone="pillTone(t.task_type)" size="sm" class="me-2">{{ taskLabel(t.task_type) }}</UiBadge>
            </div>
            <div class="d-flex align-items-center small text-muted gap-2">
              <i :class="(expandedId === t.id || expandedId === 'all') ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
            </div>
          </div>
          <div v-if="expandedId === t.id || expandedId === 'all'" class="mt-2 p-2 border-top">
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
import { onMounted, computed, ref, onBeforeUnmount, watch } from 'vue'
import { useAmOutcomesStore, type DelinquentTask, type DelinquentTaskType } from '@/stores/outcomes'
import UiBadge from '@/components/ui/UiBadge.vue'
import { useDataRefresh } from '@/composables/useDataRefresh'

const props = withDefaults(defineProps<{ hubId: number; masterCollapsed?: boolean }>(), { masterCollapsed: false })
const emit = defineEmits<{ (e: 'delete'): void }>()

const store = useAmOutcomesStore()

const { emitTaskAdded, emitTaskDeleted } = useDataRefresh(props.hubId, async () => {
  await store.listDelinquentTasks(props.hubId, true)
})

const localCollapsed = ref<boolean>(false)
const collapsed = computed(() => props.masterCollapsed || localCollapsed.value)
const tasks = computed<DelinquentTask[]>(() => store.delinquentTasksByHub[props.hubId] ?? [])
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

const addMenuOpen = ref(false)
const addMenuRef = ref<HTMLElement | null>(null)

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

const taskOptions: Array<{ value: DelinquentTaskType; label: string }> = [
  { value: 'dq_30', label: '30 DLQ' },
  { value: 'dq_60', label: '60 DLQ' },
  { value: 'dq_90', label: '90 DLQ' },
  { value: 'dq_120_plus', label: '120+ DLQ' },
  { value: 'loss_mit', label: 'Loss Mit' },
  { value: 'fc_dil', label: 'FC/DIL' },
]

const tasksBusy = ref(false)
const deleteTaskConfirm = ref({ open: false, taskId: null as number | null, busy: false })

function taskLabel(v: DelinquentTaskType): string {
  const m = taskOptions.find(o => o.value === v)
  return m?.label ?? v
}

const existingTypes = computed<Set<DelinquentTaskType>>(() => new Set(tasks.value.map(t => t.task_type)))

function pillTone(tp: DelinquentTaskType): import('@/GlobalStandardizations/badges').BadgeToneKey {
  const m: Record<DelinquentTaskType, import('@/GlobalStandardizations/badges').BadgeToneKey> = {
    dq_30: 'warning',
    dq_60: 'warning',
    dq_90: 'danger',
    dq_120_plus: 'danger',
    loss_mit: 'success',
    fc_dil: 'primary',
  }
  return m[tp]
}

function leftEdgeStyle(tp: DelinquentTaskType): Record<string, string> {
  const colorMap: Record<DelinquentTaskType, string> = {
    dq_30: 'var(--bs-warning, #ffc107)',
    dq_60: 'var(--bs-warning, #ffc107)',
    dq_90: 'var(--bs-danger, #dc3545)',
    dq_120_plus: 'var(--bs-danger, #dc3545)',
    loss_mit: 'var(--bs-success, #198754)',
    fc_dil: 'var(--bs-primary, #0d6efd)',
  }
  return {
    boxShadow: `inset 3px 0 0 ${colorMap[tp]}, var(--bs-box-shadow-sm, 0 .125rem .25rem rgba(0,0,0,.075))`,
  }
}

function toggleAddMenu() { addMenuOpen.value = !addMenuOpen.value }
function onSelectPill(tp: DelinquentTaskType) {
  if (existingTypes.value.has(tp) || tasksBusy.value) return
  tasksBusy.value = true
  store.createDelinquentTask(props.hubId, tp)
    .then(async (newTask) => {
      await store.listDelinquentTasks(props.hubId, true)
      emitTaskAdded('delinquent', newTask?.id || 0)
    })
    .finally(() => { tasksBusy.value = false; addMenuOpen.value = false })
}

function toggleExpand(id: number) { 
  userInteracted.value = true
  localExpandedId.value = localExpandedId.value === id ? null : id
}

onMounted(async () => {
  await store.listDelinquentTasks(props.hubId)
})

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
    await store.deleteDelinquentTask(props.hubId, taskId)
    await store.listDelinquentTasks(props.hubId, true)
    emitTaskDeleted('delinquent', taskId)
    cancelDeleteTask()
  } catch (err) {
    console.error('Failed to delete task:', err)
    alert('Failed to delete task. Please try again.')
    deleteTaskConfirm.value.busy = false
  }
}
</script>

<style scoped>
</style>
