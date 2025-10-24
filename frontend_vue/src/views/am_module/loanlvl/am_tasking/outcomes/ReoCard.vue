<template>
  <!-- Subtle info-colored border (no fill) to match the REO pill -->
  <b-card class="w-100 h-100 border border-1 border-info rounded-2 shadow-sm">
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
          <i class="fas fa-house-chimney me-2 text-info"></i>
          <span class="badge rounded-pill text-bg-info size_med">REO</span>
        </h5>
        <div class="d-flex align-items-center gap-2">
          <div class="position-relative ms-2" ref="menuRef">
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

    <!-- Assign Brokerage (compact; will wire to CRM later) -->
    <div class="px-3 pt-3">
      <div class="d-flex align-items-center justify-content-between">
        <div class="d-flex align-items-center gap-2 small text-muted">
          <i class="fas fa-handshake"></i>
          <span>Brokerage</span>
        </div>
        <button 
          type="button" 
          class="btn btn-link p-0 text-decoration-none fw-medium"
          @click="openBrokerModal"
          :title="'Click to assign brokerage'"
        >
          {{ broker.company || 'Assign Brokerage' }}
        </button>
      </div>
    </div>

    <!-- Brokerage Assignment Modal -->
    <div v-if="showBrokerModal" class="modal d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-md">
        <div class="modal-content">
          <div class="modal-header">
            <h6 class="modal-title">Assign Brokerage</h6>
            <button type="button" class="btn-close" @click="showBrokerModal = false"></button>
          </div>
          <div class="modal-body">
            <div v-if="loadingBrokers" class="text-center py-3">
              <div class="spinner-border spinner-border-sm" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
              <div class="small text-muted mt-2">Loading brokerages...</div>
            </div>
            <div v-else-if="brokerOptions.length">
              <div class="mb-3">
                <label class="form-label small text-muted">Select Brokerage</label>
                <select v-model="selectedBrokerId" class="form-select">
                  <option value="">-- Choose Brokerage --</option>
                  <option v-for="b in brokerOptions" :key="b.id" :value="b.id">
                    {{ b.firm }} {{ b.name ? `(${b.name})` : '' }}
                  </option>
                </select>
              </div>
              <div class="d-flex gap-2">
                <button 
                  type="button" 
                  class="btn btn-primary btn-sm"
                  @click="assignBroker"
                  :disabled="!selectedBrokerId"
                >
                  Assign
                </button>
                <button type="button" class="btn btn-secondary btn-sm" @click="showBrokerModal = false">
                  Cancel
                </button>
              </div>
            </div>
            <div v-else class="text-muted small">
              No brokerages found. Add broker contacts in CRM with tag "broker".
            </div>
          </div>
        </div>
      </div>
    </div>

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
            'bg-secondary-subtle',
            'border', 'border-1', 'border-light',
            'rounded-2', 'shadow-sm',
            'mb-2',
            'border-start'
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
              <i :class="expandedIds.has(t.id) ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
            </div>
          </div>
          <div v-if="expandedIds.has(t.id)" class="mt-2">
            <SubtaskPanel
              :title="labelFor(t.task_type)"
              :tabs="[
                { key: 'bids', label: 'Bids', icon: 'fas fa-file-invoice-dollar' },
                { key: 'notes', label: 'Notes', icon: 'fas fa-note-sticky' },
                { key: 'docs', label: 'Docs', icon: 'fas fa-folder' },
              ]"
              initial="bids"
            >
              <template #bids>
                <!-- REO Scopes/Bids (only for Trashout or Renovation) -->
                <ReoScopesPanel
                  v-if="t.task_type === 'trashout' || t.task_type === 'renovation'"
                  :hub-id="props.hubId"
                  :task-id="t.id"
                  :task-type="t.task_type as 'trashout' | 'renovation'"
                />
                <div v-else class="text-muted small">No bids for this task type.</div>
              </template>

              <template #notes>
                <!-- Notes moved to right column (outcome-level) -->
                <div class="text-muted small">Task notes moved to outcome-level notes panel</div>
              </template>

              <template #docs>
                <!-- Reuse global quick view; wire real items later -->
                <DocumentsQuickView :items="[]" title="Documents" :showViewAll="false" />
              </template>
            </SubtaskPanel>
          </div>
        </div>
      </div>
      <div v-else class="text-muted small">No subtasks yet. Choose one from the dropdown and click Add.</div>
        </div>

        <!-- Right Column: Shared Notes for this Outcome -->
        <div class="col-md-6">
          <div class="d-flex align-items-center justify-content-between mb-3 pb-2 border-bottom">
            <h5 class="mb-0 fw-bold text-body">Notes</h5>
          </div>
          <SubtaskNotes :hubId="props.hubId" outcome="reo" :taskType="null" :taskId="null" />
        </div>
      </div>
    </div>
  </b-card>
</template>

<script setup lang="ts">
import { withDefaults, defineProps, ref, computed, onMounted, defineEmits, onBeforeUnmount } from 'vue'
import { useAmOutcomesStore, type ReoTask, type ReoTaskType, type ReoData } from '@/stores/outcomes'
import http from '@/lib/http'
// Reusable editable date component with inline picker
// Path: src/components/ui/EditableDate.vue
import EditableDate from '@/components/ui/EditableDate.vue'
// Feature-local notes component (moved for AM Tasking scope)
// Path: src/views/am_module/loanlvl/am_tasking/components/SubtaskNotes.vue
import SubtaskNotes from '@/views/am_module/loanlvl/am_tasking/components/SubtaskNotes.vue'
// Scopes panel for Trashout/Renovation tasks
// Path: src/views/am_module/loanlvl/am_tasking/components/ReoScopesPanel.vue
import ReoScopesPanel from '@/views/am_module/loanlvl/am_tasking/components/ReoScopesPanel.vue'
// New tab wrapper for subtask sections (Bids/Notes/Docs)
// Path: src/views/am_module/loanlvl/am_tasking/components/SubtaskPanel.vue
import SubtaskPanel from '@/views/am_module/loanlvl/am_tasking/components/SubtaskPanel.vue'
// Global documents quick view card
// Path: src/components/DocumentsQuickView.vue
import DocumentsQuickView from '@/components/DocumentsQuickView.vue'

const props = withDefaults(defineProps<{ hubId: number }>(), {})
const emit = defineEmits<{ (e: 'delete'): void }>()
// Pinia store for outcomes/tasks
const store = useAmOutcomesStore()
// Local state: list of tasks and busy flag
const tasks = ref<ReoTask[]>([])
const busy = ref(false)
const newType = ref<ReoTaskType | ''>('')
// Allow multiple subtasks to be expanded at the same time
const expandedIds = ref<Set<number>>(new Set())
// Collapsed state for the entire card body (subtasks section hidden when true)
const collapsed = ref<boolean>(false)
// Add Task custom dropdown state
const addMenuOpen = ref(false)
const addMenuRef = ref<HTMLElement | null>(null)

// Brokerage assignment modal state
const showBrokerModal = ref(false)
const selectedBrokerId = ref<number | ''>()

// REO outcome data for displaying broker assignment
const reo = computed<ReoData | null>(() => store.getReo(props.hubId))

// Placeholder broker contact view model until CRM wiring is implemented.
// WHAT: Minimal fields we expect from CRM (company, name, email, phone).
// WHY: Provide immediate contact access and prepare for broker assignment.
// HOW: For now, only crm id is known; others display as placeholders.
const broker = computed<{ id: number | null; company: string | null; name: string | null; email: string | null; phone: string | null }>(() => {
  return {
    id: reo.value?.crm ?? null,
    company: null, // Will be populated from CRM lookup
    name: null,
    email: null,
    phone: null,
  }
})

// Broker options from CRM API
// WHAT: List of available brokerages from MasterCRM with tag="broker".
// WHY: Allow selection of broker to assign to REO.
// HOW: Fetches from CRM API when modal opens.
const brokerOptions = ref<Array<{ id: number; firm: string; name: string | null }>>([])  
const loadingBrokers = ref(false)

// Fetch broker options from CRM API
// WHAT: Loads MasterCRM records filtered by tag="broker".
// WHY: Populate dropdown with available brokerages for assignment.
// HOW: Calls /api/core/mastercrm/ with tag filter.
async function loadBrokerOptions() {
  try {
    loadingBrokers.value = true
    // Fetch MasterCRM records with broker tag
    const response = await fetch('/api/acq/brokers/?tag=broker')
    if (!response.ok) throw new Error('Failed to fetch brokers')
    const data = await response.json()
    
    // Map to dropdown format
    brokerOptions.value = (data.results || data || []).map((crm: any) => ({
      id: crm.id,
      firm: crm.firm || 'Unknown Firm',
      name: crm.name
    }))
  } catch (error) {
    console.error('Error loading broker options:', error)
    brokerOptions.value = []
  } finally {
    loadingBrokers.value = false
  }
}

// Open modal and load broker options
function openBrokerModal() {
  showBrokerModal.value = true
  loadBrokerOptions()
}

// Placeholder for broker assignment
// WHAT: Assigns selected broker to the REO outcome.
// WHY: Links REO to specific brokerage for management.
// HOW: Will update REO.crm field; for now shows placeholder alert.
function assignBroker() {
  if (!selectedBrokerId.value) return
  // TODO: Update REO outcome with selected broker CRM ID
  alert(`Broker assignment coming soon. Would assign broker ID: ${selectedBrokerId.value}`)
  showBrokerModal.value = false
  selectedBrokerId.value = ''
}

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
    expandedIds.value.add(created.id)
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
  if (expandedIds.value.has(id)) expandedIds.value.delete(id)
  else expandedIds.value.add(id)
}

function isoDate(iso: string | null): string {
  if (!iso) return 'N/A'
  try { const d = new Date(iso); return d.toLocaleDateString() } catch { return iso }
}

// Update task_started date via PATCH request
async function updateTaskStarted(taskId: number, newDate: string) {
  try {
    await http.patch(`/am/outcomes/reo-tasks/${taskId}/`, { task_started: newDate })
    // Refresh tasks to show updated date
    await loadTasks()
  } catch (err: any) {
    console.error('Failed to update task start date:', err)
    alert('Failed to update start date. Please try again.')
  }
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
  // Close broker modal when clicking outside
  if (showBrokerModal.value && !(e.target as Element)?.closest('.modal-content')) {
    showBrokerModal.value = false
  }
}
onMounted(() => { document.addEventListener('click', handleDocClick); loadTasks() })
onBeforeUnmount(() => document.removeEventListener('click', handleDocClick))

</script>
