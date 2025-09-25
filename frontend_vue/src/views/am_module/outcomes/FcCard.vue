<template>
  <b-card class="w-100 h-100">
    <template #header>
      <div class="d-flex align-items-center justify-content-between">
        <h5 class="mb-0 d-flex align-items-center">
          <i class="fas fa-gavel me-2 text-danger"></i>
          <span class="badge rounded-pill text-bg-danger px-3 py-2">Foreclosure</span>
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
          <div class="d-flex justify-content-between"><span class="text-muted">Legal CRM</span><span class="fw-medium">{{ fc?.legal_crm ?? '—' }}</span></div>
          <div class="d-flex justify-content-between"><span class="text-muted">Scheduled Sale</span><span class="fw-medium">{{ fc?.fc_sale_sched_date ?? '—' }}</span></div>
          <div class="d-flex justify-content-between"><span class="text-muted">Actual Sale</span><span class="fw-medium">{{ fc?.fc_sale_actual_date ?? '—' }}</span></div>
          <div class="d-flex justify-content-between"><span class="text-muted">Bid Price</span><span class="fw-medium">{{ money(fc?.fc_bid_price) }}</span></div>
          <div class="d-flex justify-content-between"><span class="text-muted">Sale Price</span><span class="fw-medium">{{ money(fc?.fc_sale_price) }}</span></div>
        </div>
      </div>
      <div class="col-lg-6">
        <div class="mb-2 small text-muted">Quick Update</div>
        <form class="row g-2" @submit.prevent="onSave">
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
import { withDefaults, defineProps, computed, ref, reactive, onMounted, defineEmits } from 'vue'
import { useAmOutcomesStore, type FcSale } from '@/stores/outcomes'
import http from '@/lib/http'

const props = withDefaults(defineProps<{ hubId: number }>(), {})
const emit = defineEmits<{ (e: 'delete'): void }>()
const store = useAmOutcomesStore()
const fc = ref<FcSale | null>(null)
const busy = ref(false)

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

async function onSave() {
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
}

onMounted(load)
</script>
