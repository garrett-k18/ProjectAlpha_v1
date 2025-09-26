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
    <hr class="my-3" />

    <!-- Legal Contact (simplified clickable field) -->
    <div class="px-3">
      <div class="d-flex align-items-center justify-content-between">
        <div class="d-flex align-items-center gap-2 small text-muted">
          <i class="fas fa-scale-balanced"></i>
          <span>Legal</span>
        </div>
        <button 
          type="button" 
          class="btn btn-link p-0 text-decoration-none fw-medium"
          @click="showLegalModal = true"
          :title="'Click for contact details'"
        >
          {{ legal.company || 'Assign Legal Firm' }}
        </button>
      </div>
    </div>

    <!-- Legal Contact Modal -->
    <div v-if="showLegalModal" class="modal d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-sm">
        <div class="modal-content">
          <div class="modal-header">
            <h6 class="modal-title">Legal Contact</h6>
            <button type="button" class="btn-close" @click="showLegalModal = false"></button>
          </div>
          <div class="modal-body">
            <div class="mb-2">
              <strong>{{ legal.company || 'No firm assigned' }}</strong>
            </div>
            <div class="mb-2" v-if="legal.name">
              <small class="text-muted">Contact:</small><br>
              {{ legal.name }}
            </div>
            <div class="mb-2" v-if="legal.phone">
              <small class="text-muted">Phone:</small><br>
              <a :href="`tel:${legal.phone}`" class="text-decoration-none">{{ legal.phone }}</a>
            </div>
            <div class="mb-2" v-if="legal.email">
              <small class="text-muted">Email:</small><br>
              <button class="btn btn-sm btn-outline-primary" @click="sendEmail">
                <i class="fas fa-envelope me-1"></i>Send Email
              </button>
            </div>
            <div v-if="!legal.company" class="text-muted small">
              No legal firm assigned to this DIL.
            </div>
          </div>
        </div>
      </div>
    </div>

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
            'bg-secondary-subtle', // subtle neutral fill with slight contrast vs. card
            'border', 'border-1', 'border-light', // subtle neutral outline
            'rounded-2', 'shadow-sm',
            'mb-2', // minimal spacing between cards
          ]"
          :style="leftEdgeStyle(t.task_type)"
        >
          <div class="d-flex align-items-center justify-content-between" role="button" @click="toggleExpand(t.id)">
            <div class="d-flex align-items-center ps-2">
              <UiBadge :tone="pillTone(t.task_type)" size="sm" class="me-2">{{ taskLabel(t.task_type) }}</UiBadge>
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
                  <!-- Read-only text display; not an input field -->
                  <div class="small fw-semibold">{{ legalCostFormatted }}</div>
                </div>
                <div class="col-md-6">
                  <label class="form-label small text-muted">Cash-for-Keys Offered</label>
                  <!-- Editable; tracked locally per subtask id. Shows a $ prefix via input-group without affecting v-model -->
                  <div class="input-group input-group-sm">
                    <span class="input-group-text">$</span>
                    <input
                      type="text"
                      class="form-control form-control-sm"
                      v-model="cashForKeysByTask[t.id]"
                      placeholder="0"
                      @input="onCfkInput(t.id)"
                    />
                  </div>
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
import { useAmOutcomesStore, type Dil, type DilTask, type DilTaskType } from '@/stores/outcomes'
import UiBadge from '@/components/ui/UiBadge.vue'
// Feature-local notes component (moved for AM Tasking scope)
// Path: src/views/am_module/loanlvl/am_tasking/components/SubtaskNotes.vue
import SubtaskNotes from '@/views/am_module/loanlvl/am_tasking/components/SubtaskNotes.vue'

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
  { value: 'owner_contacted', label: 'Borrowers/Heirs Cooperation' },
  { value: 'no_cooperation', label: 'No Cooperation' },
  { value: 'dil_drafted', label: 'Drafted' },
  { value: 'dil_successful', label: 'Executed' },
]

const tasksBusy = ref(false)

function taskLabel(v: DilTaskType): string {
  const m = taskOptions.find(o => o.value === v)
  return m?.label ?? v
}

const existingTypes = computed<Set<DilTaskType>>(() => new Set(tasks.value.map(t => t.task_type)))

// Badge classes per DIL task type (pill style)
function badgeClass(tp: DilTaskType): string {
  const map: Record<DilTaskType, string> = {
    owner_contacted: 'badge rounded-pill text-bg-primary',
    no_cooperation: 'badge rounded-pill text-bg-secondary',
    dil_drafted: 'badge rounded-pill text-bg-warning',
    dil_successful: 'badge rounded-pill text-bg-success',
  }
  return map[tp]
}

// Map DIL task types to UiBadge tones so all pills follow our shared badge template.
function pillTone(tp: DilTaskType): import('@/config/badgeTokens').BadgeToneKey {
  const m: Record<DilTaskType, import('@/config/badgeTokens').BadgeToneKey> = {
    owner_contacted: 'primary',
    no_cooperation: 'secondary',
    dil_drafted: 'warning',
    dil_successful: 'success',
  }
  return m[tp]
}

// Left border color per DIL task type
function itemBorderClass(tp: DilTaskType): string {
  const map: Record<DilTaskType, string> = {
    owner_contacted: 'border-start border-2 border-primary',
    no_cooperation: 'border-start border-2 border-secondary',
    dil_drafted: 'border-start border-2 border-warning',
    dil_successful: 'border-start border-2 border-success',
  }
  return map[tp]
}

// Robust left-edge stripe using inset box-shadow + Bootstrap CSS vars with fallbacks
function leftEdgeStyle(tp: DilTaskType): Record<string, string> {
  const colorMap: Record<DilTaskType, string> = {
    owner_contacted: 'var(--bs-primary, #0d6efd)',
    no_cooperation: 'var(--bs-secondary, #6c757d)',
    dil_drafted: 'var(--bs-warning, #ffc107)',
    dil_successful: 'var(--bs-success, #198754)',
  }
  return {
    boxShadow: `inset 3px 0 0 ${colorMap[tp]}, var(--bs-box-shadow-sm, 0 .125rem .25rem rgba(0,0,0,.075))`,
  }
}

const latestStatusValue = computed<string | null>(() => tasks.value[0]?.task_type ?? null)
const latestStatusLabel = computed<string | null>(() => latestStatusValue.value ? taskLabel(latestStatusValue.value as DilTaskType) : null)

// DIL outcome data for displaying dil_cost and syncing cfk_cost
const dil = computed<Dil | null>(() => store.getDil(props.hubId))
// Placeholder legal contact view model until CRM wiring is implemented.
// WHAT: Minimal fields we expect from CRM (company, name, email, phone).
// WHY: Provide immediate links (mailto/tel) and show linked CRM id.
// HOW: For now, only legal_crm id is known; others display as placeholders.
// Legal contact modal state
const showLegalModal = ref(false)

// Placeholder legal contact view model until CRM wiring is implemented.
// WHAT: Minimal fields we expect from CRM (company, name, email, phone).
// WHY: Provide immediate contact access via modal and prepare for Outlook API integration.
// HOW: For now, only legal_crm id is known; others display as placeholders.
const legal = computed<{ id: number | null; company: string | null; name: string | null; email: string | null; phone: string | null }>(() => {
  return {
    id: dil.value?.crm ?? null,
    company: null, // Will be populated from CRM lookup
    name: null,
    email: null,
    phone: null,
  }
})

// Placeholder for Outlook API email integration
// WHAT: Opens email compose window using platform's Outlook API.
// WHY: Allows in-platform email without leaving the DIL workflow.
// HOW: Will integrate with Outlook API; for now shows placeholder alert.
function sendEmail() {
  // TODO: Integrate with Outlook API to compose email to legal.email
  alert(`Email integration coming soon. Would send to: ${legal.value.email || 'legal contact'}`)
  showLegalModal.value = false
}
const legalCostDisplay = computed<string>(() => dil.value?.dil_cost ?? '—')
// Currency formatting for read-only display of legal cost
function money(val: string | number | null | undefined): string {
  if (val == null || val === '') return '—'
  const num = typeof val === 'string' ? Number(val) : Number(val)
  try {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(num)
  } catch { return String(val) }
}
const legalCostFormatted = computed<string>(() => money(dil.value?.dil_cost ?? null))

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
// Initialize CFK input when expanding the drafted subtask
function toggleExpand(id: number) {
  expandedId.value = expandedId.value === id ? null : id
  if (expandedId.value === id) {
    const t = tasks.value.find(x => x.id === id)
    if (t && t.task_type === 'dil_drafted' && cashForKeysByTask.value[id] === undefined) {
      // Format initial value from backend with thousand separators for display
      const initialRaw = (dil.value?.cfk_cost ?? '') as string
      cashForKeysByTask.value[id] = formatNumberWithCommas(initialRaw.replace(/[^0-9.]/g, ''))
    }
  }
}

onMounted(async () => {
  // Load tasks when card mounts
  await store.listDilTasks(props.hubId)
  // Fetch DIL so we can show dil_cost and current cfk_cost
  await store.fetchDil(props.hubId, true)
})

// --- Extra UI state for 'dil_drafted' subtask fields ---
// Map of subtask id -> Cash-for-Keys offered input value. This is frontend-only until backend wiring is added.
const cashForKeysByTask = ref<Record<number, string>>({})
// Debounce timers keyed by subtask id so multiple drafted rows won't conflict
const saveTimers = ref<Record<number, number | undefined>>({})

// Sanitize to digits + optional decimal and PATCH to backend
function onCfkInput(taskId: number) {
  const raw = cashForKeysByTask.value[taskId] ?? ''
  // keep digits and dot only
  const numeric = raw.replace(/[^0-9.]/g, '')
  // live-format with thousand separators while typing
  const formatted = formatNumberWithCommas(numeric)
  cashForKeysByTask.value[taskId] = formatted
  // debounce
  if (saveTimers.value[taskId]) window.clearTimeout(saveTimers.value[taskId])
  saveTimers.value[taskId] = window.setTimeout(async () => {
    try {
      // Ensure the DIL outcome exists before patching
      if (!store.getDil(props.hubId)) {
        await store.ensureDil(props.hubId)
      }
      const payload: Partial<Dil> = { cfk_cost: (numeric || null) as any }
      // optimistic cache update
      const current = store.getDil(props.hubId)
      if (current) current.cfk_cost = payload.cfk_cost as any
      await store.patchDil(props.hubId, payload)
      // refresh cached DIL
      await store.fetchDil(props.hubId, true)
      // sync input from canonical value (e.g., backend rounding)
      const refreshed = store.getDil(props.hubId)
      if (refreshed) {
        const back = (refreshed.cfk_cost ?? '') as string
        cashForKeysByTask.value[taskId] = formatNumberWithCommas(back.replace(/[^0-9.]/g, ''))
      }
    } catch (err) {
      // Log for debugging if save fails (endpoint/serializer issues)
      console.error('Failed to save Cash-for-Keys (cfk_cost):', err)
    }
  }, 400)
}

// Insert commas in the integer portion of a numeric string, preserving decimal portion if present.
function formatNumberWithCommas(n: string): string {
  if (!n) return ''
  const [intPart, decPart] = n.split('.')
  const withCommas = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, ',')
  return decPart !== undefined ? `${withCommas}.${decPart}` : withCommas
}
</script>

<style scoped>
/* Keep component-scoped styles lean; use Bootstrap utilities for most styling */
</style>
