<template>
  <b-card class="w-100 h-100">
    <template #header>
      <div class="d-flex align-items-center justify-content-between">
        <h5 class="mb-0 d-flex align-items-center">
          <i class="fas fa-home me-2 text-info"></i>
          <span class="badge rounded-pill text-bg-info px-3 py-2">REO</span>
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
          <div class="d-flex justify-content-between"><span class="text-muted">Broker CRM</span><span class="fw-medium">{{ reo?.broker_crm ?? '—' }}</span></div>
          <div class="d-flex justify-content-between"><span class="text-muted">List Price</span><span class="fw-medium">{{ money(reo?.list_price) }}</span></div>
          <div class="d-flex justify-content-between"><span class="text-muted">List Date</span><span class="fw-medium">{{ reo?.list_date ?? '—' }}</span></div>
          <div class="d-flex justify-content-between"><span class="text-muted">Under Contract?</span><span class="fw-medium">{{ reo?.under_contract_flag ? 'Yes' : 'No' }}</span></div>
          <div class="d-flex justify-content-between"><span class="text-muted">Under Contract Date</span><span class="fw-medium">{{ reo?.under_contract_date ?? '—' }}</span></div>
          <div class="d-flex justify-content-between"><span class="text-muted">Contract Price</span><span class="fw-medium">{{ money(reo?.contract_price) }}</span></div>
          <div class="d-flex justify-content-between"><span class="text-muted">Estimated Close</span><span class="fw-medium">{{ reo?.estimated_close_date ?? '—' }}</span></div>
          <div class="d-flex justify-content-between"><span class="text-muted">Actual Close</span><span class="fw-medium">{{ reo?.actual_close_date ?? '—' }}</span></div>
          <div class="d-flex justify-content-between"><span class="text-muted">Seller Credit</span><span class="fw-medium">{{ money(reo?.seller_credit_amt) }}</span></div>
          <div class="d-flex justify-content-between"><span class="text-muted">Purchase Type</span><span class="fw-medium">{{ purchaseTypeLabel(reo?.purchase_type ?? null) }}</span></div>
          <div class="d-flex justify-content-between"><span class="text-muted">Gross Purchase Price</span><span class="fw-medium">{{ money(reo?.gross_purchase_price) }}</span></div>
        </div>
      </div>
      <div class="col-lg-6">
        <div class="mb-2 small text-muted">Quick Update</div>
        <form class="row g-2" @submit.prevent="onSave">
          <div class="col-6">
            <label class="form-label small text-muted">List Price</label>
            <input v-currency pattern="[0-9,]*" class="form-control" v-model="form.list_price" />
          </div>
          <div class="col-6">
            <label class="form-label small text-muted">List Date</label>
            <input type="date" class="form-control" v-model="form.list_date" />
          </div>
          <div class="col-6">
            <label class="form-label small text-muted">Under Contract?</label>
            <select class="form-select" v-model="form.under_contract_flag">
              <option :value="true">Yes</option>
              <option :value="false">No</option>
            </select>
          </div>
          <div class="col-6">
            <label class="form-label small text-muted">Under Contract Date</label>
            <input type="date" class="form-control" v-model="form.under_contract_date" />
          </div>
          <div class="col-6">
            <label class="form-label small text-muted">Contract Price</label>
            <input v-currency pattern="[0-9,]*" class="form-control" v-model="form.contract_price" />
          </div>
          <div class="col-6">
            <label class="form-label small text-muted">Estimated Close</label>
            <input type="date" class="form-control" v-model="form.estimated_close_date" />
          </div>
          <div class="col-6">
            <label class="form-label small text-muted">Actual Close</label>
            <input type="date" class="form-control" v-model="form.actual_close_date" />
          </div>
          <div class="col-6">
            <label class="form-label small text-muted">Seller Credit</label>
            <input v-currency pattern="[0-9,]*" class="form-control" v-model="form.seller_credit_amt" />
          </div>
          <div class="col-6">
            <label class="form-label small text-muted">Purchase Type</label>
            <select class="form-select" v-model="form.purchase_type">
              <option :value="null">—</option>
              <option value="cash">Cash</option>
              <option value="financing">Financing</option>
              <option value="seller_financing">Seller Financing</option>
            </select>
          </div>
          <div class="col-6">
            <label class="form-label small text-muted">Gross Purchase Price</label>
            <input v-currency pattern="[0-9,]*" class="form-control" v-model="form.gross_purchase_price" />
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
import { useAmOutcomesStore, type ReoData } from '@/stores/outcomes'

const props = withDefaults(defineProps<{ hubId: number }>(), {})
const store = useAmOutcomesStore()
const emit = defineEmits<{ (e: 'delete'): void }>()
const reo = ref<ReoData | null>(null)
const busy = ref(false)

function money(val: string | number | null | undefined): string {
  if (val == null || val === '') return '—'
  const num = typeof val === 'string' ? Number(val) : Number(val)
  try {
    return new Intl.NumberFormat(undefined, { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(num)
  } catch { return String(val) }
}

function purchaseTypeLabel(v: ReoData['purchase_type'] | undefined): string {
  if (!v) return '—'
  if (v === 'cash') return 'Cash'
  if (v === 'financing') return 'Financing'
  if (v === 'seller_financing') return 'Seller Financing'
  return String(v)
}

const form = reactive({
  list_price: '' as string,
  list_date: '' as string,
  under_contract_flag: false as boolean,
  under_contract_date: '' as string,
  contract_price: '' as string,
  estimated_close_date: '' as string,
  actual_close_date: '' as string,
  seller_credit_amt: '' as string,
  purchase_type: null as ReoData['purchase_type'],
  gross_purchase_price: '' as string,
})

async function load() {
  reo.value = await store.fetchReo(props.hubId)
  if (reo.value) {
    form.list_price = reo.value.list_price || ''
    form.list_date = reo.value.list_date || ''
    form.under_contract_flag = !!reo.value.under_contract_flag
    form.under_contract_date = reo.value.under_contract_date || ''
    form.contract_price = reo.value.contract_price || ''
    form.estimated_close_date = reo.value.estimated_close_date || ''
    form.actual_close_date = reo.value.actual_close_date || ''
    form.seller_credit_amt = reo.value.seller_credit_amt || ''
    form.purchase_type = reo.value.purchase_type
    form.gross_purchase_price = reo.value.gross_purchase_price || ''
  }
}

async function onSave() {
  try {
    busy.value = true
    const payload: Record<string, any> = {}
    for (const k of Object.keys(form)) {
      const v = (form as any)[k]
      if (v !== '' && v !== null && v !== undefined) payload[k] = v
    }
    if (!Object.keys(payload).length) return
    await store.patchReo(props.hubId, payload)
    await load()
  } finally {
    busy.value = false
  }
}

onMounted(load)
</script>
