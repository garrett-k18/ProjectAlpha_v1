<template>
  <b-card class="w-100 h-100">
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

    <!-- Tasks Timeline -->
    <div>
      <div class="d-flex align-items-center justify-content-between mb-2">
        <h6 class="mb-0">Task Timeline</h6>
        <div class="d-flex gap-2">
          <select class="form-select form-select-sm" v-model="newTaskType">
            <option disabled value="">Select Task</option>
            <option v-for="opt in taskOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
          </select>
          <button class="btn btn-sm btn-outline-primary" :disabled="!newTaskType || tasksBusy" @click="onAddTask">
            <span v-if="tasksBusy" class="spinner-border spinner-border-sm me-1"></span>
            Add Task
          </button>
        </div>
      </div>

      <div class="list-group list-group-flush">
        <div v-if="!tasks.length && !tasksBusy" class="text-muted small">No tasks yet.</div>
        <div v-for="t in tasks" :key="t.id" class="list-group-item px-0">
          <div class="d-flex align-items-start justify-content-between">
            <div class="d-flex align-items-center">
              <span class="badge bg-success me-2">
                <i class="me-1 fas fa-check-circle"></i>
                {{ taskLabel(t.task_type) }}
              </span>
              <span class="fw-medium">DIL Task</span>
            </div>
            <span class="small text-muted">{{ isoDate(t.created_at) }}</span>
          </div>
          <div class="d-flex align-items-center justify-content-between small text-muted">
            <div class="d-flex align-items-center">
              <i class="fas fa-user me-1"></i>
              System
            </div>
            <span class="text-success">Updated: {{ isoDate(t.updated_at) }}</span>
          </div>
        </div>
      </div>
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

const newTaskType = ref<DilTaskType | ''>('')
const tasksBusy = ref(false)

function taskLabel(v: DilTaskType): string {
  const m = taskOptions.find(o => o.value === v)
  return m?.label ?? v
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

async function onAddTask() {
  if (!newTaskType.value) return
  try {
    tasksBusy.value = true
    await store.createDilTask(props.hubId, newTaskType.value)
    newTaskType.value = ''
  } finally {
    tasksBusy.value = false
  }
}

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
.list-group-item { background: transparent; }
</style>
