<template>
  <!-- Subtle danger-colored border (no fill) to match the Foreclosure pill -->
  <b-card class="w-100 h-100 border border-1 border-danger rounded-2 shadow-sm">
    <template #header>
      <div class="d-flex align-items-center justify-content-between">
        <h5 class="mb-0 d-flex align-items-center">
          <i class="fas fa-gavel me-2 text-danger"></i>
          <span class="badge rounded-pill text-bg-danger size_med">Foreclosure</span>
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
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
                    <path d="M5.5 5.5a.5.5 0 0 1 .5.5v7a.5.5 0 0 1-1 0v-7a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v7a.5.5 0 0 1-1 0v-7a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v7a.5.5 0 0 0 1 0v-7z"/>
                    <path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4H2.5a1 1 0 1 1 0-2H6h4h3.5a1 1 0 0 1 1 1zM5 4v9a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4H5zm1-2a1 1 0 0 0-1 1h6a1 1 0 0 0-1-1H6z"/>
                  </svg>
                  <span>Delete</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <div class="row g-3">
      <div class="col-lg-6">
        <div class="mb-2 small text-muted">Outcome Details</div>
        <div class="d-flex flex-column gap-2">
          <div class="d-flex justify-content-between"><span class="text-muted">Legal CRM</span><span class="fw-medium">{{ fc?.legal_crm ?? '—' }}</span></div>
          <div class="d-flex justify-content-between"><span class="text-muted">Scheduled Sale</span><span class="fw-medium">{{ fc?.fc_sale_sched_date ?? '—' }}</span></div>
          <div class="d-flex justify-content-between"><span class="text-muted">Actual Sale</span><span class="fw-medium">{{ fc?.fc_sale_actual_date ?? '—' }}</span></div>
          <div class="d-flex justify-content-between"><span class="text-muted">Bid Price</span><span class="fw-medium">{{ money(fc?.fc_bid_price) }}</span></div>
          <div class="d-flex justify-content-between"><span class="text-muted">Sale Price</span><span class="fw-medium">{{ money(fc?.fc_sale_price) }}</span></div>
        </div>
      </div>
      <div class="col-lg-6">
        <div class="mb-2 small text-muted">Quick Update</div>
        <form class="row g-2" @submit.prevent>
          <div class="col-6">
            <label class="form-label small text-muted">Scheduled Sale</label>
            <input type="date" class="form-control" v-model="form.fc_sale_sched_date" />
          </div>
          <div class="col-6">
            <label class="form-label small text-muted">Actual Sale</label>
            <input type="date" class="form-control" v-model="form.fc_sale_actual_date" />
          </div>
          <div class="col-6">
            <label class="form-label small text-muted">Bid Price</label>
            <input v-currency pattern="[0-9,]*" class="form-control" v-model="form.fc_bid_price" />
          </div>
          <div class="col-6">
            <label class="form-label small text-muted">Sale Price</label>
            <input v-currency pattern="[0-9,]*" class="form-control" v-model="form.fc_sale_price" />
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
            'bg-secondary-subtle', // subtle neutral fill with slight contrast
            'border', 'border-1', 'border-light', // neutral thin outline
            'rounded-2', 'shadow-sm',
            'mb-2', // spacing between cards
            'border-start', // ensure left edge area
          ]"
          :style="leftEdgeStyle(t.task_type)"
        >
          <div class="d-flex align-items-center justify-content-between" role="button" @click="toggleExpand(t.id)">
            <div class="d-flex align-items-center ps-2">
              <span :class="badgeClass(t.task_type)" class="me-2">{{ labelFor(t.task_type) }}</span>
            </div>
            <div class="d-flex align-items-center small text-muted">
              <span class="me-3">Created: {{ isoDate(t.created_at) }}</span>
              <i :class="expandedId === t.id ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
            </div>
          </div>
          <div v-if="expandedId === t.id" class="mt-2">
            <SubtaskNotes :hubId="props.hubId" outcome="fc" :taskType="t.task_type" :taskId="t.id" />
          </div>
        </div>
      </div>
      <div v-else class="text-muted small">No subtasks yet. Use Add Task to create one.</div>
    </div>
  </b-card>
</template>

<script setup lang="ts">
import { withDefaults, defineProps, computed, ref, reactive, onMounted, defineEmits, watch, onBeforeUnmount } from 'vue'
import { useAmOutcomesStore, type FcSale, type FcTask, type FcTaskType } from '@/stores/outcomes'
import SubtaskNotes from '@/components/notes/SubtaskNotes.vue'
import http from '@/lib/http'

const props = withDefaults(defineProps<{ hubId: number }>(), {})
const emit = defineEmits<{ (e: 'delete'): void }>()
const store = useAmOutcomesStore()
const fc = ref<FcSale | null>(null)
const busy = ref(false)
// FC Subtasks state
const tasks = ref<FcTask[]>([])
const expandedId = ref<number | null>(null)
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

function money(val: string | number | null | undefined): string {
  if (val == null || val === '') return '—'
  const num = typeof val === 'string' ? Number(val) : Number(val)
  try {
    return new Intl.NumberFormat(undefined, { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(num)
  } catch { return String(val) }
}

const form = reactive({
  fc_sale_sched_date: '' as string,
  fc_sale_actual_date: '' as string,
  fc_bid_price: '' as string,
  fc_sale_price: '' as string,
})

async function load() {
  fc.value = await store.fetchFc(props.hubId)
  if (fc.value) {
    form.fc_sale_sched_date = fc.value.fc_sale_sched_date || ''
    form.fc_sale_actual_date = fc.value.fc_sale_actual_date || ''
    form.fc_bid_price = fc.value.fc_bid_price || ''
    form.fc_sale_price = fc.value.fc_sale_price || ''
  }
  // Load subtasks
  tasks.value = await store.listFcTasks(props.hubId, true)
}

// Debounced auto-save on form changes
let timer: number | undefined
watch(form, async () => {
  if (!fc.value) return
  if (timer) window.clearTimeout(timer)
  timer = window.setTimeout(async () => {
    try {
      busy.value = true
      const payload: Record<string, any> = {}
      if (form.fc_sale_sched_date) payload.fc_sale_sched_date = form.fc_sale_sched_date
      if (form.fc_sale_actual_date) payload.fc_sale_actual_date = form.fc_sale_actual_date
      if (form.fc_bid_price) payload.fc_bid_price = form.fc_bid_price
      if (form.fc_sale_price) payload.fc_sale_price = form.fc_sale_price
      if (!Object.keys(payload).length) return
      await store.patchFc(props.hubId, payload)
      await load()
    } finally {
      busy.value = false
    }
  }, 600)
}, { deep: true })

onMounted(load)

// ---------- Subtasks helpers ----------
const taskOptions: ReadonlyArray<{ value: FcTaskType; label: string }> = [
  { value: 'nod_noi', label: 'NOD/NOI' },
  { value: 'fc_filing', label: 'FC Filing' },
  { value: 'mediation', label: 'Mediation' },
  { value: 'judgement', label: 'Judgement' },
  { value: 'redemption', label: 'Redemption' },
  { value: 'sale_scheduled', label: 'Sale Scheduled' },
  { value: 'sold', label: 'Sold' },
]
function labelFor(tp: FcTaskType): string {
  const m = taskOptions.find(o => o.value === tp)
  return m ? m.label : tp
}
const existingTypes = computed<Set<FcTaskType>>(() => new Set(tasks.value.map(t => t.task_type)))
function toggleAddMenu() { addMenuOpen.value = !addMenuOpen.value }
function onSelectPill(tp: FcTaskType) {
  if (existingTypes.value.has(tp) || busy.value) return
  busy.value = true
  store.createFcTask(props.hubId, tp)
    .then(async () => { tasks.value = await store.listFcTasks(props.hubId, true) })
    .finally(() => { busy.value = false; addMenuOpen.value = false })
}
function toggleExpand(id: number) { expandedId.value = expandedId.value === id ? null : id }
function isoDate(iso: string): string { try { return new Date(iso).toLocaleDateString() } catch { return iso } }
function badgeClass(tp: FcTaskType): string {
  const map: Record<FcTaskType, string> = {
    nod_noi: 'badge rounded-pill size_small text-bg-warning',
    fc_filing: 'badge rounded-pill size_small text-bg-primary',
    mediation: 'badge rounded-pill size_small text-bg-info',
    judgement: 'badge rounded-pill size_small text-bg-secondary',
    redemption: 'badge rounded-pill size_small text-bg-success',
    sale_scheduled: 'badge rounded-pill size_small text-bg-dark',
    sold: 'badge rounded-pill size_small text-bg-danger',
  }
  return map[tp]
}
function itemBorderClass(tp: FcTaskType): string {
  const map: Record<FcTaskType, string> = {
    nod_noi: 'border-start border-2 border-warning',
    fc_filing: 'border-start border-2 border-primary',
    mediation: 'border-start border-2 border-info',
    judgement: 'border-start border-2 border-secondary',
    redemption: 'border-start border-2 border-success',
    sale_scheduled: 'border-start border-2 border-dark',
    sold: 'border-start border-2 border-danger',
  }
  return map[tp]
}

// Robust left-edge stripe using inset box-shadow + Bootstrap CSS vars with fallbacks
function leftEdgeStyle(tp: FcTaskType): Record<string, string> {
  const colorMap: Record<FcTaskType, string> = {
    nod_noi: 'var(--bs-warning, #ffc107)',
    fc_filing: 'var(--bs-primary, #0d6efd)',
    mediation: 'var(--bs-info, #0dcaf0)',
    judgement: 'var(--bs-secondary, #6c757d)',
    redemption: 'var(--bs-success, #198754)',
    sale_scheduled: 'var(--bs-dark, #212529)',
    sold: 'var(--bs-danger, #dc3545)',
  }
  return {
    boxShadow: `inset 3px 0 0 ${colorMap[tp]}, var(--bs-box-shadow-sm, 0 .125rem .25rem rgba(0,0,0,.075))`,
  }
}
</script>
