<template>
  <!-- WHAT: Panel listing REO Scopes for a given task (Trashout/Renovation) with add modal -->
  <!-- WHY: Track vendor bids/scopes and tie them to a specific REO subtask -->
  <!-- WHERE: AM Tasking -> REO Card -> Subtask details -->
  <!-- HOW: Uses Pinia store (useAmOutcomesStore) and backend endpoints /am/outcomes/reo-scopes/ and /acq/brokers/ -->
  <div class="card border-0 bg-white shadow-sm my-2">
    <div class="card-body py-2">
      <div class="d-flex align-items-center justify-content-between">
        <div class="d-flex align-items-center gap-2">
          <i class="fas" :class="taskType === 'trashout' ? 'fa-dumpster' : 'fa-screwdriver-wrench'"></i>
          <span class="fw-medium">Scopes/Bids</span>
          <span class="badge text-bg-light">{{ items.length }}</span>
        </div>
        <button type="button" class="btn btn-sm btn-primary" @click="openAddModal">
          <i class="fas fa-plus me-1"></i> Add Scope
        </button>
      </div>

      <div v-if="loading" class="small text-muted mt-2">Loading scopes...</div>
      <div v-else>
        <div v-if="items.length" class="list-group list-group-flush mt-2">
          <div v-for="s in items" :key="s.id" class="list-group-item px-0 d-flex align-items-center justify-content-between">
            <div class="d-flex flex-column">
              <div class="d-flex align-items-center gap-2">
                <strong>{{ vendorFirm(s.crm) }}</strong>
                <span v-if="s.total_cost" class="text-muted">$ {{ s.total_cost }}</span>
              </div>
              <div class="small text-muted">
                <span v-if="vendorContact(s.crm)">{{ vendorContact(s.crm) }}</span>
              </div>
              <div class="small" v-if="s.notes">{{ s.notes }}</div>
            </div>
            <div class="text-end small text-muted">
              <div v-if="s.scope_date">Scoped: {{ localDate(s.scope_date) }}</div>
              <div v-if="s.expected_completion">ETA: {{ localDate(s.expected_completion) }}</div>
            </div>
          </div>
        </div>
        <div v-else class="small text-muted mt-2">No scopes yet.</div>
      </div>
    </div>
  </div>

  <!-- Add Scope Modal -->
  <div v-if="showModal" class="modal d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h6 class="modal-title">Add Scope ({{ taskTypeLabel }})</h6>
          <button type="button" class="btn-close" @click="closeModal"></button>
        </div>
        <div class="modal-body">
          <div class="row g-3">
            <!-- Vendor selection -->
            <div class="col-12">
              <label class="form-label small text-muted">Choose Vendor</label>
              <div class="d-flex gap-2">
                <select
                  v-model="form.crm"
                  class="form-select form-select-sm"
                  :style="{ flex: '0 0 80%', maxWidth: '80%' }"
                >
                  <option :value="null">-- Select existing vendor --</option>
                  <option v-for="v in vendorOptions" :key="v.id" :value="v.id">
                    {{ v.firm || 'Unknown' }}
                    <span v-if="v.contact_name"> ({{ v.contact_name }})</span>
                  </option>
                </select>
                <button type="button" class="btn btn-outline-secondary btn-sm" @click="openVendorModal">
                  <i class="fas fa-user-plus me-1"></i> New Vendor
                </button>
              </div>
            </div>

            <!-- Snapshot vendor fields removed; CRM is the single source of truth -->

            <!-- Dates and totals -->
            <div class="col-md-6">
              <label class="form-label small text-muted">Bid Date</label>
              <input v-model="form.scope_date" type="date" class="form-control form-control-sm" />
            </div>
            <div class="col-md-6">
              <label class="form-label small text-muted">Expected Completion</label>
              <input v-model="form.expected_completion" type="date" class="form-control form-control-sm" />
            </div>
            <div class="col-12">
              <label class="form-label small text-muted">Total Cost</label>
              <input v-model="form.total_cost" type="number" step="0.01" class="form-control" placeholder="25000" />
            </div>
            <div class="col-12">
              <label class="form-label small text-muted">Notes</label>
              <textarea v-model="form.notes" rows="3" class="form-control" placeholder="Itemization or notes..."></textarea>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="closeModal">Cancel</button>
          <button type="button" class="btn btn-primary" :disabled="submitting || !form.crm" @click="submit">
            <span v-if="!submitting"><i class="fas fa-save me-1"></i> Save</span>
            <span v-else>Saving...</span>
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- New Vendor Modal -->
  <div v-if="showVendorModal" class="modal d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);">
    <div class="modal-dialog modal-md">
      <div class="modal-content">
        <div class="modal-header">
          <h6 class="modal-title">New Vendor (MasterCRM)</h6>
          <button type="button" class="btn-close" @click="showVendorModal = false"></button>
        </div>
        <div class="modal-body">
          <div class="row g-3">
            <div class="col-12">
              <label class="form-label small text-muted">Company</label>
              <input v-model="newVendor.firm" type="text" class="form-control" placeholder="ACME Construction" />
            </div>
            <div class="col-12">
              <label class="form-label small text-muted">Contact Name</label>
              <input v-model="newVendor.name" type="text" class="form-control" placeholder="Jane Smith" />
            </div>
            <div class="col-md-6">
              <label class="form-label small text-muted">Email</label>
              <input v-model="newVendor.email" type="email" class="form-control" />
            </div>
            <div class="col-md-6">
              <label class="form-label small text-muted">Phone</label>
              <input v-model="newVendor.phone" type="text" class="form-control" />
            </div>
            <div class="col-md-6">
              <label class="form-label small text-muted">City</label>
              <input v-model="newVendor.city" type="text" class="form-control" />
            </div>
            <div class="col-md-6">
              <label class="form-label small text-muted">State</label>
              <input v-model="newVendor.state" type="text" maxlength="2" class="form-control" />
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="showVendorModal = false">Cancel</button>
          <button type="button" class="btn btn-primary" :disabled="creatingVendor || !newVendor.firm" @click="createVendor">
            <span v-if="!creatingVendor">Create</span>
            <span v-else>Creating...</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { withDefaults, defineProps, ref, onMounted, watch, computed } from 'vue'
import { useAmOutcomesStore, type ReoScope, type ReoScopeKind } from '@/stores/outcomes'
import http from '@/lib/http'

// Props: hub id, task id, and type ('trashout' | 'renovation')
const props = withDefaults(defineProps<{ hubId: number; taskId: number; taskType: ReoScopeKind }>(), {})

// Store
const store = useAmOutcomesStore()

// State
const items = ref<ReoScope[]>([])
const loading = ref(false)

// Add modal state
const showModal = ref(false)
const submitting = ref(false)
const form = ref<{ crm: number | null; scope_date: string | null; total_cost: string | null; expected_completion: string | null; notes: string | null }>({
  crm: null,
  scope_date: null,
  total_cost: null,
  expected_completion: null,
  notes: null,
})

// Vendor selection
const vendorOptions = ref<Array<{ id: number; firm: string | null; contact_name: string | null }>>([])
const vendorById = ref<Record<number, { firm: string | null; name: string | null }>>({})
const showVendorModal = ref(false)
const creatingVendor = ref(false)
const newVendor = ref<{ firm: string | null; name: string | null; email: string | null; phone: string | null; city: string | null; state: string | null }>({
  firm: null,
  name: null,
  email: null,
  phone: null,
  city: null,
  state: null,
})

const taskTypeLabel = computed(() => (props.taskType === 'trashout' ? 'Trashout' : 'Renovation'))

function localDate(iso: string): string { try { const d = new Date(iso); return d.toLocaleDateString() } catch { return iso } }

async function loadItems() {
  loading.value = true
  try {
    items.value = await store.listReoScopes(props.hubId, { scopeKind: props.taskType, reoTaskId: props.taskId }, true)
    await loadVendorDetails()
  } finally {
    loading.value = false
  }
}

function openAddModal() {
  showModal.value = true
  loadVendors()
}
function closeModal() {
  showModal.value = false
  submitting.value = false
}

function openVendorModal() { showVendorModal.value = true }

async function loadVendors() {
  // Use existing internal brokers endpoint filtered by tag=vendor
  try {
    const res = await fetch(`/api/acq/brokers/?tag=vendor`)
    const data = await res.json()
    const results = (data?.results || data || []) as any[]
    vendorOptions.value = results.map((crm: any) => ({ id: crm.id, firm: crm.firm || null, contact_name: crm.name || crm.contact_name || null }))
  } catch (e) {
    vendorOptions.value = []
  }
}

async function loadVendorDetails() {
  // Fetch minimal CRM details for vendors referenced by scopes
  const ids = Array.from(new Set(items.value.map(s => s.crm).filter((v): v is number => typeof v === 'number')))
  for (const id of ids) {
    if (vendorById.value[id]) continue
    try {
      const res = await fetch(`/api/acq/brokers/${id}/`)
      if (!res.ok) continue
      const v = await res.json()
      vendorById.value[id] = { firm: v.firm || null, name: v.name || v.contact_name || null }
    } catch {}
  }
}

function vendorFirm(crmId: number | null): string {
  if (!crmId) return 'Vendor'
  const v = vendorById.value[crmId]
  // Prefer firm; fall back to contact name; avoid showing raw ID label
  return v?.firm || v?.name || 'Vendor'
}
function vendorContact(crmId: number | null): string | null {
  if (!crmId) return null
  const v = vendorById.value[crmId]
  return v?.name || null
}

async function createVendor() {
  creatingVendor.value = true
  try {
    const payload = { ...newVendor.value, tag: 'vendor' }
    const res = await fetch('/api/acq/brokers/', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
    if (!res.ok) throw new Error('Failed to create vendor')
    const v = await res.json()
    // Add to options and preselect
    vendorOptions.value.unshift({ id: v.id, firm: v.firm || null, contact_name: v.name || v.contact_name || null })
    form.value.crm = v.id
    showVendorModal.value = false
  } catch (e) {
    // no-op; keep modal open
  } finally {
    creatingVendor.value = false
  }
}

async function submit() {
  submitting.value = true
  try {
    const payload = {
      asset_hub_id: props.hubId,
      scope_kind: props.taskType,
      reo_task: props.taskId,
      crm: form.value.crm,
      scope_date: form.value.scope_date,
      total_cost: form.value.total_cost,
      expected_completion: form.value.expected_completion,
      notes: form.value.notes,
    }
    await store.createReoScope(payload as any)
    closeModal()
    await loadItems()
  } finally {
    submitting.value = false
  }
}

onMounted(() => { loadItems() })
watch(() => [props.hubId, props.taskId, props.taskType], () => loadItems())
</script>

<style scoped>
</style>
