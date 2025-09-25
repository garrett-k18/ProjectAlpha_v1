<template>
  <!-- Subtle primary-colored border (no fill) to match the DIL pill -->
  <b-card class="w-100 h-100 border border-1 border-primary rounded-2 shadow-sm">
    <template #header>
      <div class="d-flex align-items-center justify-content-between">
        <h5 class="mb-0 d-flex align-items-center">
          <i class="fas fa-handshake me-2 text-primary"></i>
          <span class="badge rounded-pill text-bg-primary px-3 py-2">Deed-in-Lieu</span>
        </h5>
        <div class="d-flex align-items-center gap-2">
          <span v-if="latestStatusLabel" class="badge bg-success" :title="latestStatusValue ?? undefined">{{ latestStatusLabel }}</span>
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

    <!-- Details + Quick Edit -->
    <div class="row g-3">
      <div class="col-lg-6">
        <div class="mb-2 small text-muted">Outcome Details</div>
        <div class="d-flex flex-column gap-2">
          <div class="d-flex justify-content-between">
            <span class="text-muted">Legal CRM</span>
            <span class="fw-medium">{{ dil?.legal_crm ?? '—' }}</span>
          </div>
          <div class="d-flex justify-content-between">
            <span class="text-muted">Completion Date</span>
            <span class="fw-medium">{{ dil?.dil_completion_date ?? '—' }}</span>
          </div>
          <div class="d-flex justify-content-between">
            <span class="text-muted">DIL Cost</span>
            <span class="fw-medium">{{ formatCurrency(dil?.dil_cost) }}</span>
          </div>
          <div class="d-flex justify-content-between">
            <span class="text-muted">CFK Cost</span>
            <span class="fw-medium">{{ formatCurrency(dil?.cfk_cost) }}</span>
          </div>
        </div>
      </div>
      <div class="col-lg-6">
        <div class="mb-2 small text-muted">Quick Update</div>
        <form class="row g-2" @submit.prevent>
          <div class="col-6">
            <label class="form-label small text-muted">Completion Date</label>
            <input type="date" class="form-control" v-model="form.completionDate" />
          </div>
          <div class="col-6">
            <label class="form-label small text-muted">DIL Cost</label>
            <input v-currency pattern="[0-9,]*" class="form-control" v-model="form.dilCostDigits" />
          </div>
          <div class="col-6">
            <label class="form-label small text-muted">CFK Cost</label>
            <input v-currency pattern="[0-9,]*" class="form-control" v-model="form.cfkCostDigits" />
          </div>
          <!-- Auto-save enabled, no Save button -->
        </form>
      </div>
    </div>

    <hr class="my-3" />

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
            'bg-body-secondary', // darker grey for better contrast
            'border', 'border-1', // subtle outline
            'rounded-2', 'shadow-sm',
            itemBorderClass(t.task_type) // colored left border
          ]"
        >
          <div class="d-flex align-items-center justify-content-between" role="button" @click="toggleExpand(t.id)">
            <div class="d-flex align-items-center">
              <span :class="badgeClass(t.task_type)" class="me-2">{{ taskLabel(t.task_type) }}</span>
            </div>
            <div class="d-flex align-items-center small text-muted">
              <span class="me-3">Created: {{ isoDate(t.created_at) }}</span>
              <i :class="expandedId === t.id ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
            </div>
          </div>
          <div v-if="expandedId === t.id" class="mt-2 small text-muted">
            Subtask details coming soon for "{{ taskLabel(t.task_type) }}".
          </div>
        </div>
      </div>
      <div v-else class="text-muted small">No subtasks yet. Use Add Task to create one.</div>
    </div>
  </b-card>
</template>

<script setup lang="ts">
// Component for viewing/updating DIL outcome and managing its tasks.
// Uses Hyper UI/Bootstrap utilities; currency fields leverage global v-currency directive.
// Docs: Pinia https://pinia.vuejs.org/ ; DRF ViewSets https://www.django-rest-framework.org/api-guide/viewsets/

import { onMounted, computed, reactive, ref, withDefaults, defineProps, defineEmits, watch, onBeforeUnmount } from 'vue'
import { useAmOutcomesStore, type Dil, type DilTask, type DilTaskType } from '@/stores/outcomes'
import http from '@/lib/http'

const props = withDefaults(defineProps<{ hubId: number }>(), {})
const emit = defineEmits<{ (e: 'delete'): void }>()

const store = useAmOutcomesStore()
const dil = computed<Dil | null>(() => store.getDil(props.hubId))
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
    owner_contacted: 'badge rounded-pill text-bg-primary',
    dil_drafted: 'badge rounded-pill text-bg-warning',
    dil_successful: 'badge rounded-pill text-bg-success',
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

const latestStatusValue = computed<string | null>(() => tasks.value[0]?.task_type ?? null)
const latestStatusLabel = computed<string | null>(() => latestStatusValue.value ? taskLabel(latestStatusValue.value as DilTaskType) : null)

function isoDate(iso: string): string {
  try {
    const d = new Date(iso)
    return d.toLocaleDateString()
  } catch { return iso }
}

function formatCurrency(val: string | number | null | undefined): string {
  if (val == null || val === '') return '—'
  try {
    const num = typeof val === 'string' ? Number(val) : Number(val)
    return new Intl.NumberFormat(undefined, { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(num)
  } catch { return String(val) }
}

// Quick edit form state
const saveBusy = ref(false)
const form = reactive({
  completionDate: '' as string,
  dilCostDigits: '' as string, // numeric digits only, formatted by v-currency
  cfkCostDigits: '' as string,
})

// Debounced auto-save on quick edit changes
let dilTimer: number | undefined
watch(form, async () => {
  if (!dil.value) return
  if (dilTimer) window.clearTimeout(dilTimer)
  dilTimer = window.setTimeout(async () => {
    try {
      saveBusy.value = true
      const payload: Record<string, any> = {}
      if (form.completionDate) payload['dil_completion_date'] = form.completionDate
      if (form.dilCostDigits) payload['dil_cost'] = form.dilCostDigits
      if (form.cfkCostDigits) payload['cfk_cost'] = form.cfkCostDigits
      if (!Object.keys(payload).length) return
      await http.patch(`/am/outcomes/dil/${props.hubId}/`, payload)
      await store.fetchDil(props.hubId, true)
    } finally {
      saveBusy.value = false
    }
  }, 600)
}, { deep: true })

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
  // Initialize quick edit form with current dil values
  if (dil.value) {
    form.completionDate = dil.value.dil_completion_date || ''
    form.dilCostDigits = dil.value.dil_cost || ''
    form.cfkCostDigits = dil.value.cfk_cost || ''
  }
})
</script>

<style scoped>
/* Keep component-scoped styles lean; use Bootstrap utilities for most styling */
</style>
