<template>
  <!-- Subtle warning-colored border (no fill) to match the Short Sale pill -->
  <b-card class="w-100 h-100 border border-1 border-warning rounded-2 shadow-sm">
    <template #header>
      <div class="d-flex align-items-center justify-content-between">
        <h5 class="mb-0 d-flex align-items-center">
          <i class="fas fa-tags me-2 text-warning"></i>
          <span class="badge rounded-pill text-bg-warning px-3 py-2">Short Sale</span>
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
          <div class="d-flex justify-content-between"><span class="text-muted">Broker CRM</span><span class="fw-medium">{{ ss?.broker_crm ?? '—' }}</span></div>
          <div class="d-flex justify-content-between"><span class="text-muted">Acceptable Min Offer</span><span class="fw-medium">{{ money(ss?.acceptable_min_offer) }}</span></div>
          <div class="d-flex justify-content-between"><span class="text-muted">Short Sale Date</span><span class="fw-medium">{{ ss?.short_sale_date ?? '—' }}</span></div>
        </div>
      </div>
      <div class="col-lg-6">
        <div class="mb-2 small text-muted">Quick Update</div>
        <form class="row g-2" @submit.prevent>
          <div class="col-6">
            <label class="form-label small text-muted">Acceptable Min Offer</label>
            <input v-currency pattern="[0-9,]*" class="form-control" v-model="form.acceptable_min_offer" />
          </div>
          <div class="col-6">
            <label class="form-label small text-muted">Short Sale Date</label>
            <input type="date" class="form-control" v-model="form.short_sale_date" />
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
            'bg-body-secondary',
            'border', 'border-1',
            'rounded-2', 'shadow-sm',
            itemBorderClass(t.task_type)
          ]"
        >
          <div class="d-flex align-items-center justify-content-between" role="button" @click="toggleExpand(t.id)">
            <div class="d-flex align-items-center">
              <span :class="badgeClass(t.task_type)" class="me-2">{{ labelFor(t.task_type) }}</span>
            </div>
            <div class="d-flex align-items-center small text-muted">
              <span class="me-3">Created: {{ isoDate(t.created_at) }}</span>
              <i :class="expandedId === t.id ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
            </div>
          </div>
          <div v-if="expandedId === t.id" class="mt-2 small text-muted">
            Subtask details coming soon for "{{ labelFor(t.task_type) }}".
          </div>
        </div>
      </div>
      <div v-else class="text-muted small">No subtasks yet. Use Add Task to create one.</div>
    </div>
  </b-card>
</template>

<script setup lang="ts">
import { withDefaults, defineProps, defineEmits, ref, onMounted, onBeforeUnmount, computed, reactive, watch } from 'vue'
import { useAmOutcomesStore, type ShortSaleOutcome, type ShortSaleTask, type ShortSaleTaskType } from '@/stores/outcomes'

const props = withDefaults(defineProps<{ hubId: number }>(), {})
const emit = defineEmits<{ (e: 'delete'): void }>()
const store = useAmOutcomesStore()
const ss = ref<ShortSaleOutcome | null>(null)
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

function money(val: string | number | null | undefined): string {
  if (val == null || val === '') return '—'
  const num = typeof val === 'string' ? Number(val) : Number(val)
  try {
    return new Intl.NumberFormat(undefined, { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(num)
  } catch { return String(val) }
}

const form = reactive({
  acceptable_min_offer: '' as string,
  short_sale_date: '' as string,
})

async function load() {
  ss.value = await store.fetchShortSale(props.hubId)
  if (ss.value) {
    form.acceptable_min_offer = ss.value.acceptable_min_offer || ''
    form.short_sale_date = ss.value.short_sale_date || ''
  }
  // Load subtasks
  tasks.value = await store.listShortSaleTasks(props.hubId, true)
}

// Debounced auto-save on form changes
let timer: number | undefined
watch(form, async () => {
  if (!ss.value) return
  if (timer) window.clearTimeout(timer)
  timer = window.setTimeout(async () => {
    try {
      busy.value = true
      const payload: Record<string, any> = {}
      if (form.acceptable_min_offer) payload.acceptable_min_offer = form.acceptable_min_offer
      if (form.short_sale_date) payload.short_sale_date = form.short_sale_date
      if (!Object.keys(payload).length) return
      await store.patchShortSale(props.hubId, payload)
      await load()
    } finally {
      busy.value = false
    }
  }, 600)
}, { deep: true })

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
function isoDate(iso: string): string { try { return new Date(iso).toLocaleDateString() } catch { return iso } }
function badgeClass(tp: ShortSaleTaskType): string {
  const map: Record<ShortSaleTaskType, string> = {
    list_price_accepted: 'badge rounded-pill text-bg-warning',
    listed: 'badge rounded-pill text-bg-info',
    under_contract: 'badge rounded-pill text-bg-primary',
    sold: 'badge rounded-pill text-bg-success',
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
</script>
