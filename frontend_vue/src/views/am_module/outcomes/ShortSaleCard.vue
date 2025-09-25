<template>
  <b-card class="w-100 h-100">
    <template #header>
      <div class="d-flex align-items-center justify-content-between">
        <h5 class="mb-0 d-flex align-items-center">
          <i class="fas fa-tags me-2 text-warning"></i>
          <span class="badge rounded-pill text-bg-warning px-3 py-2">Short Sale</span>
        </h5>
        <div class="d-flex align-items-center gap-2">
          <div class="text-muted small">Hub {{ hubId }}</div>
          <button type="button" class="btn btn-sm btn-outline-danger d-inline-flex align-items-center justify-content-center px-3 py-1 lh-1" @click="emit('delete')">
            <span class="text-center w-100">Delete</span>
          </button>
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
        <form class="row g-2" @submit.prevent="onSave">
          <div class="col-6">
            <label class="form-label small text-muted">Acceptable Min Offer</label>
            <input v-currency pattern="[0-9,]*" class="form-control" v-model="form.acceptable_min_offer" />
          </div>
          <div class="col-6">
            <label class="form-label small text-muted">Short Sale Date</label>
            <input type="date" class="form-control" v-model="form.short_sale_date" />
          </div>
          <div class="col-12 d-flex align-items-end">
            <button type="submit" class="btn btn-primary ms-auto" :disabled="busy">
              <span v-if="busy" class="spinner-border spinner-border-sm me-2"></span>
              Save
            </button>
          </div>
        </form>
      </div>
    </div>
  </b-card>
</template>

<script setup lang="ts">
import { withDefaults, defineProps, ref, reactive, onMounted, defineEmits } from 'vue'
import { useAmOutcomesStore, type ShortSaleOutcome } from '@/stores/outcomes'

const props = withDefaults(defineProps<{ hubId: number }>(), {})
const store = useAmOutcomesStore()
const emit = defineEmits<{ (e: 'delete'): void }>()
const ss = ref<ShortSaleOutcome | null>(null)
const busy = ref(false)

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
}

async function onSave() {
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
}

onMounted(load)
</script>
