<template>
  <b-card class="w-100 h-100">
    <template #header>
      <div class="d-flex align-items-center justify-content-between">
        <h5 class="mb-0 d-flex align-items-center">
          <i class="fas fa-gavel me-2 text-danger"></i>
          <span class="badge rounded-pill text-bg-danger px-3 py-2">Foreclosure</span>
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
  </b-card>
</template>

<script setup lang="ts">
import { withDefaults, defineProps, computed, ref, reactive, onMounted, defineEmits, watch, onBeforeUnmount } from 'vue'
import { useAmOutcomesStore, type FcSale } from '@/stores/outcomes'
import http from '@/lib/http'

const props = withDefaults(defineProps<{ hubId: number }>(), {})
const emit = defineEmits<{ (e: 'delete'): void }>()
const store = useAmOutcomesStore()
const fc = ref<FcSale | null>(null)
const busy = ref(false)

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
</script>
