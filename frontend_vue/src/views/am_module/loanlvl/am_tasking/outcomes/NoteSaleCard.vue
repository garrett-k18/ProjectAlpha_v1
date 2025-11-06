<template>
  <!-- Subtle secondary-colored border (no fill) to match the Note Sale pill -->
  <b-card class="w-100 h-100 border border-1 border-secondary rounded-2 shadow-sm">
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
          <i class="fas fa-file-invoice-dollar me-2 text-secondary"></i>
          <UiBadge tone="secondary" size="lg">Note Sale</UiBadge>
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
    <div class="p-3" v-show="!collapsed">
      <div class="row g-3">
        <!-- Left Column: Subtasks -->
        <div class="col-md-6">
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
            <!-- WHAT: Offers section for Out to Market and Pending Sale tasks -->
            <!-- WHY: Track offers received while note is being marketed -->
            <div v-if="t.task_type === 'out_to_market' || t.task_type === 'pending_sale'" class="mb-3">
              <OffersSection
                :hub-id="props.hubId"
                offer-source="note_sale"
                :readonly="t.task_type === 'pending_sale'"
                @task-created="handleTaskCreated"
              />
            </div>
            <!-- When the subtask is 'Sold', render extra fields -->
            <div v-else-if="t.task_type === 'sold'" class="mb-2 p-1 bg-transparent">
              <div class="row g-2">
                <div class="col-md-6">
                  <label class="form-label small text-muted">Sold Date</label>
                  <div class="d-block">
                    <EditableDate
                      :model-value="soldDateLocal || ''"
                      @update:model-value="onSoldDateChange"
                      title="Click to edit sold date"
                    />
                  </div>
                </div>
                <div class="col-md-6">
                  <label class="form-label small text-muted">Proceeds</label>
                  <div class="input-group input-group-sm">
                    <span class="input-group-text">$</span>
                    <input
                      type="text"
                      class="form-control form-control-sm"
                      v-model="proceedsLocal"
                      placeholder="0"
                      @input="onProceedsInput"
                    />
                  </div>
                </div>
                <div class="col-12">
                  <label class="form-label small text-muted">Trading Partner</label>
                  <select
                    class="form-select form-select-sm"
                    v-model="tradingPartnerLocal"
                    @change="onTradingPartnerChange"
                  >
                    <option :value="null">Select Trading Partner...</option>
                    <option v-for="tp in tradingPartners" :key="tp.id" :value="tp.id">
                      {{ tp.firm || tp.name || `TP ${tp.id}` }}
                    </option>
                  </select>
                </div>
              </div>
            </div>

            <!-- Delete button -->
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
          <SubtaskNotes :hubId="props.hubId" outcome="note_sale" :taskType="null" :taskId="null" />
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
// Component for managing Note Sale subtasks
// Docs: Pinia https://pinia.vuejs.org/ ; DRF ViewSets https://www.django-rest-framework.org/api-guide/viewsets/

import { onMounted, computed, ref, withDefaults, defineProps, defineEmits, onBeforeUnmount, watch } from 'vue'
import { useAmOutcomesStore, type NoteSaleTask, type NoteSaleTaskType, type NoteSaleOutcome } from '@/stores/outcomes'
import { useTradingPartnersStore, type TradingPartnerItem } from '@/stores/tradingPartners'
import http from '@/lib/http'
import UiBadge from '@/components/ui/UiBadge.vue'
import { useDataRefresh } from '@/composables/useDataRefresh'
// Reusable editable date component with inline picker
// Path: src/components/ui/EditableDate.vue
import EditableDate from '@/components/ui/EditableDate.vue'
// Feature-local notes component (moved for AM Tasking scope)
// Path: src/views/am_module/loanlvl/am_tasking/components/SubtaskNotes.vue
import SubtaskNotes from '@/views/am_module/loanlvl/am_tasking/components/SubtaskNotes.vue'
// Offers section for Out to Market tasks (shared component for offers management)
// Path: src/views/am_module/loanlvl/am_tasking/components/OffersSection.vue
import OffersSection from '@/views/am_module/loanlvl/am_tasking/components/OffersSection.vue'

const props = withDefaults(defineProps<{ hubId: number; masterCollapsed?: boolean }>(), { masterCollapsed: false })
const emit = defineEmits<{ (e: 'delete'): void }>()

const store = useAmOutcomesStore()
const tradingPartnersStore = useTradingPartnersStore()

// WHAT: Setup data refresh functionality
// WHY: Auto-refresh when other components modify data
const { emitTaskAdded, emitTaskDeleted, emitTaskUpdated } = useDataRefresh(props.hubId, async () => {
  // WHAT: Refresh tasks when data changes
  await store.listNoteSaleTasks(props.hubId, true)
})

// Collapsed state for the entire card body (subtasks section hidden when true)
const localCollapsed = ref<boolean>(false)
const collapsed = computed(() => props.masterCollapsed || localCollapsed.value)
const tasks = computed<NoteSaleTask[]>(() => store.getNoteSaleTasks(props.hubId))
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

const taskOptions: Array<{ value: NoteSaleTaskType; label: string }> = [
  { value: 'potential_note_sale', label: 'Potential Note Sale' },
  { value: 'out_to_market', label: 'Out to Market' },
  { value: 'pending_sale', label: 'Pending Sale' },
  { value: 'sold', label: 'Sold' },
]

const tasksBusy = ref(false)

// Delete task confirmation modal state
const deleteTaskConfirm = ref({ open: false, taskId: null as number | null, busy: false })

function taskLabel(v: NoteSaleTaskType): string {
  const m = taskOptions.find(o => o.value === v)
  return m?.label ?? v
}

const existingTypes = computed<Set<NoteSaleTaskType>>(() => new Set(tasks.value.map(t => t.task_type)))

// Map Note Sale task types to UiBadge tones
function pillTone(tp: NoteSaleTaskType): import('@/config/badgeTokens').BadgeToneKey {
  const m: Record<NoteSaleTaskType, import('@/config/badgeTokens').BadgeToneKey> = {
    potential_note_sale: 'secondary',
    out_to_market: 'info',
    pending_sale: 'warning',
    sold: 'success',
  }
  return m[tp]
}

// Robust left-edge stripe using inset box-shadow + Bootstrap CSS vars with fallbacks
function leftEdgeStyle(tp: NoteSaleTaskType): Record<string, string> {
  const colorMap: Record<NoteSaleTaskType, string> = {
    potential_note_sale: 'var(--bs-secondary, #6c757d)',
    out_to_market: 'var(--bs-info, #0dcaf0)',
    pending_sale: 'var(--bs-warning, #ffc107)',
    sold: 'var(--bs-success, #198754)',
  }
  return {
    boxShadow: `inset 3px 0 0 ${colorMap[tp]}, var(--bs-box-shadow-sm, 0 .125rem .25rem rgba(0,0,0,.075))`,
  }
}

// Note Sale outcome data
const noteSale = computed<NoteSaleOutcome | null>(() => store.getNoteSale(props.hubId))

// Local state for editable fields
const soldDateLocal = ref<string | null>(null)
const proceedsLocal = ref<string>('')
const tradingPartnerLocal = ref<number | null>(null)
const tradingPartners = computed<TradingPartnerItem[]>(() => tradingPartnersStore.results)

// Debounce timers
const saveTimers = ref<Record<string, number | undefined>>({})

// Update task_started date via PATCH request
async function updateTaskStarted(taskId: number, newDate: string) {
  try {
    await http.patch(`/am/outcomes/note-sale-tasks/${taskId}/`, { task_started: newDate })
    await store.listNoteSaleTasks(props.hubId, true)
    emitTaskUpdated('note_sale', taskId)
  } catch (err: any) {
    console.error('Failed to update task start date:', err)
    alert('Failed to update start date. Please try again.')
  }
}

function toggleAddMenu() { addMenuOpen.value = !addMenuOpen.value }
function onSelectPill(tp: NoteSaleTaskType) {
  if (existingTypes.value.has(tp) || tasksBusy.value) return
  tasksBusy.value = true
  store.createNoteSaleTask(props.hubId, tp)
    .then(async (newTask) => {
      await store.listNoteSaleTasks(props.hubId, true)
      emitTaskAdded('note_sale', newTask?.id || 0)
    })
    .finally(() => { tasksBusy.value = false; addMenuOpen.value = false })
}

function toggleExpand(id: number) { 
  userInteracted.value = true
  localExpandedId.value = localExpandedId.value === id ? null : id
  if (localExpandedId.value === id) {
    // Initialize local values from outcome data
    const outcome = noteSale.value
    if (outcome) {
      soldDateLocal.value = outcome.sold_date
      proceedsLocal.value = formatNumberWithCommas((outcome.proceeds || '').toString().replace(/[^0-9.]/g, ''))
      tradingPartnerLocal.value = outcome.trading_partner
    }
  }
}

onMounted(async () => {
  // Load tasks and outcome when card mounts
  await store.listNoteSaleTasks(props.hubId)
  await store.fetchNoteSale(props.hubId, true)
  // Load trading partners for dropdown
  await tradingPartnersStore.fetchPartners()
})

// Handle sold date change
function onSoldDateChange(newDate: string) {
  soldDateLocal.value = newDate
  debounceSave('sold_date', async () => {
    if (!store.getNoteSale(props.hubId)) {
      await store.ensureNoteSale(props.hubId)
    }
    await store.patchNoteSale(props.hubId, { sold_date: soldDateLocal.value })
    await store.fetchNoteSale(props.hubId, true)
  })
}

// Handle proceeds input with formatting
function onProceedsInput() {
  const raw = proceedsLocal.value
  const numeric = raw.replace(/[^0-9.]/g, '')
  proceedsLocal.value = formatNumberWithCommas(numeric)
  debounceSave('proceeds', async () => {
    if (!store.getNoteSale(props.hubId)) {
      await store.ensureNoteSale(props.hubId)
    }
    await store.patchNoteSale(props.hubId, { proceeds: (numeric || null) as any })
    await store.fetchNoteSale(props.hubId, true)
  })
}

// Handle trading partner change
function onTradingPartnerChange() {
  debounceSave('trading_partner', async () => {
    if (!store.getNoteSale(props.hubId)) {
      await store.ensureNoteSale(props.hubId)
    }
    await store.patchNoteSale(props.hubId, { trading_partner: tradingPartnerLocal.value })
    await store.fetchNoteSale(props.hubId, true)
  })
}

// Generic debounce save helper
function debounceSave(key: string, saveFn: () => Promise<void>) {
  if (saveTimers.value[key]) window.clearTimeout(saveTimers.value[key])
  saveTimers.value[key] = window.setTimeout(async () => {
    try {
      await saveFn()
    } catch (err) {
      console.error(`Failed to save ${key}:`, err)
    }
  }, 400)
}

// Insert commas in the integer portion of a numeric string
function formatNumberWithCommas(n: string): string {
  if (!n) return ''
  const [intPart, decPart] = n.split('.')
  const withCommas = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, ',')
  return decPart !== undefined ? `${withCommas}.${decPart}` : withCommas
}

// WHAT: Handle task-created event from OffersSection
// WHY: Refresh tasks when auto-created from accepted offer
async function handleTaskCreated() {
  await store.listNoteSaleTasks(props.hubId, true)
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
    await store.deleteNoteSaleTask(props.hubId, taskId)
    await store.listNoteSaleTasks(props.hubId, true)
    emitTaskDeleted('note_sale', taskId)
    cancelDeleteTask()
  } catch (err) {
    console.error('Failed to delete task:', err)
    alert('Failed to delete task. Please try again.')
    deleteTaskConfirm.value.busy = false
  }
}
</script>

<style scoped>
/* Keep component-scoped styles lean; use Bootstrap utilities for most styling */
</style>

