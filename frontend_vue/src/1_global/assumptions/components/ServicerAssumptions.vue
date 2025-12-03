<template>
  <!--
    ServicerAssumptions.vue
    - Displays Servicer records from backend with a dropdown to select by Servicer Name
    - Shows corresponding servicer data in a read-only grid for now (can be made editable later)

    Location: frontend_vue/src/1_global/assumptions/components/ServicerAssumptions.vue
  -->
  <div class="servicer-assumptions-container">
    <!-- Header: title on left, actions (Save) on right -->
    <div class="d-flex justify-content-between align-items-center mb-3">
      <div>
        <h5 class="mb-1">Servicer Assumptions</h5>
        <p class="text-muted small mb-0">Select a servicer to view its configured fees and durations</p>
      </div>
      <div class="d-flex gap-2">
        <button
          class="btn btn-sm btn-outline-secondary"
          :disabled="!selectedServicerId || isSettingDefault"
          @click="setAsTradeDefault"
        >
          <i
            class="mdi me-1"
            :class="isSelectedDefault ? 'mdi-star' : 'mdi-star-outline'"
          ></i>
          {{ isSelectedDefault ? 'Default for Trades' : 'Make Default' }}
        </button>
        <button 
          class="btn btn-sm btn-primary"
          :disabled="!hasChanges || isSaving || !selectedServicerId"
          @click="saveServicer"
        >
          <i class="mdi mdi-content-save me-1"></i>
          {{ isSaving ? 'Saving...' : 'Save' }}
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="text-muted mt-2">Loading servicers...</p>
    </div>

    <!-- Content -->
    <div v-else>
      <!-- Selector Row -->
      <div class="row g-3 align-items-center mb-3">
        <div class="col-auto">
          <label for="servicerSelect" class="col-form-label col-form-label-sm fw-semibold">Servicer</label>
        </div>
        <div class="col-auto">
          <!-- Dropdown to select by Servicer Name -->
          <select
            id="servicerSelect"
            class="form-select form-select-sm"
            v-model.number="selectedServicerId"
          >
            <option :value="null">Select a servicer...</option>
            <option v-for="s in servicers" :key="s.id" :value="s.id">
              {{ s.servicerName }}
            </option>
          </select>
        </div>
      </div>

      <!-- Empty state when none selected -->
      <div v-if="!selectedServicer" class="text-muted small">
        Choose a servicer to view details.
      </div>

      <!-- Details Form -->
      <div v-else class="card">
        <div class="card-body">
          <div class="row g-3">
            <!-- Contact -->
            <div class="col-md-6">
              <h6 class="text-uppercase text-muted fw-semibold mb-2">Contact</h6>
              <div class="mb-2">
                <label class="form-label form-label-sm text-muted">Name</label>
                <input type="text" class="form-control form-control-sm" v-model="form.contactName" @input="markChanged" placeholder="Jane Doe" />
              </div>
              <div class="mb-2">
                <label class="form-label form-label-sm text-muted">Email</label>
                <input type="email" class="form-control form-control-sm" v-model="form.contactEmail" @input="markChanged" placeholder="jane@company.com" />
              </div>
              <div class="mb-2">
                <label class="form-label form-label-sm text-muted">Phone</label>
                <input type="text" class="form-control form-control-sm" v-model="form.contactPhone" @input="markChanged" placeholder="(555) 123-4567" />
              </div>
            </div>
            <div class="col-md-6">
              <h6 class="text-uppercase text-muted fw-semibold mb-2">General</h6>
              <div class="mb-2">
                <label class="form-label form-label-sm text-muted">Servicing Transfer Duration (Months)</label>
                <input type="number" class="form-control form-control-sm" v-model.number="form.servicingTransferDuration" @input="markChanged" min="0" step="1" />
              </div>
              <div class="mb-2">
                <label class="form-label form-label-sm text-muted">REO Days</label>
                <input type="number" class="form-control form-control-sm" v-model.number="form.reoDays" @input="markChanged" min="0" step="1" />
              </div>
            </div>
          </div>

          <hr/>

          <div class="row g-3">
            <div class="col-md-6">
              <h6 class="text-uppercase text-muted fw-semibold mb-2">Fees (Core)</h6>
              <div class="mb-1">
                <label class="form-label form-label-sm text-muted">Boarding Fee</label>
                <input 
                  type="text" 
                  class="form-control form-control-sm" 
                  :value="formatCurrency0(form.boardFee)" 
                  @input="onCurrency0Input($event, 'boardFee')"
                  inputmode="numeric"
                />
              </div>
              <div class="mb-1">
                <label class="form-label form-label-sm text-muted">Current Fee</label>
                <input 
                  type="text" 
                  class="form-control form-control-sm" 
                  :value="formatCurrency0(form.currentFee)" 
                  @input="onCurrency0Input($event, 'currentFee')"
                  inputmode="numeric"
                />
              </div>
              <div class="mb-1">
                <label class="form-label form-label-sm text-muted">30 Day Delinquent Fee</label>
                <input 
                  type="text" 
                  class="form-control form-control-sm" 
                  :value="formatCurrency0(form.thirtdayFee)" 
                  @input="onCurrency0Input($event, 'thirtdayFee')"
                  inputmode="numeric"
                />
              </div>
              <div class="mb-1">
                <label class="form-label form-label-sm text-muted">60 Day Delinquent Fee</label>
                <input 
                  type="text" 
                  class="form-control form-control-sm" 
                  :value="formatCurrency0(form.sixtydayFee)" 
                  @input="onCurrency0Input($event, 'sixtydayFee')"
                  inputmode="numeric"
                />
              </div>
              <div class="mb-1">
                <label class="form-label form-label-sm text-muted">90 Day Delinquent Fee</label>
                <input 
                  type="text" 
                  class="form-control form-control-sm" 
                  :value="formatCurrency0(form.ninetydayFee)" 
                  @input="onCurrency0Input($event, 'ninetydayFee')"
                  inputmode="numeric"
                />
              </div>
              <div class="mb-1">
                <label class="form-label form-label-sm text-muted">120 Day Delinquent Fee</label>
                <input 
                  type="text" 
                  class="form-control form-control-sm" 
                  :value="formatCurrency0(form.onetwentydayFee)" 
                  @input="onCurrency0Input($event, 'onetwentydayFee')"
                  inputmode="numeric"
                />
              </div>
            </div>
            <div class="col-md-6">
              <h6 class="text-uppercase text-muted fw-semibold mb-2">Fees (Actions)</h6>
              <div class="mb-1">
                <label class="form-label form-label-sm text-muted">Foreclosure Fee</label>
                <input type="text" class="form-control form-control-sm" :value="formatCurrency0(form.fcFee)" @input="onCurrency0Input($event, 'fcFee')" inputmode="numeric" />
              </div>
              <div class="mb-1">
                <label class="form-label form-label-sm text-muted">Bankruptcy Fee</label>
                <input type="text" class="form-control form-control-sm" :value="formatCurrency0(form.bkFee)" @input="onCurrency0Input($event, 'bkFee')" inputmode="numeric" />
              </div>
              <div class="mb-1">
                <label class="form-label form-label-sm text-muted">Modification Fee</label>
                <input type="text" class="form-control form-control-sm" :value="formatCurrency0(form.modFee)" @input="onCurrency0Input($event, 'modFee')" inputmode="numeric" />
              </div>
              <div class="mb-1">
                <label class="form-label form-label-sm text-muted">DIL Fee</label>
                <input type="text" class="form-control form-control-sm" :value="formatCurrency0(form.dilFee)" @input="onCurrency0Input($event, 'dilFee')" inputmode="numeric" />
              </div>
              <div class="mb-1">
                <label class="form-label form-label-sm text-muted">Third-Party Fee</label>
                <input type="text" class="form-control form-control-sm" :value="formatCurrency0(form.thirdpartyFee)" @input="onCurrency0Input($event, 'thirdpartyFee')" inputmode="numeric" />
              </div>
              <div class="mb-1">
                <label class="form-label form-label-sm text-muted">REO Fee</label>
                <input type="text" class="form-control form-control-sm" :value="formatCurrency0(form.reoFee)" @input="onCurrency0Input($event, 'reoFee')" inputmode="numeric" />
              </div>
            </div>
          </div>

          <hr/>

          <div class="row g-3">
            <div class="col-md-6">
              <h6 class="text-uppercase text-muted fw-semibold mb-2">Liquidation Fees</h6>
              <div class="mb-1">
                <label class="form-label form-label-sm text-muted">Liquidation Fee (%)</label>
                <input 
                  type="text" 
                  class="form-control form-control-sm" 
                  :value="formatPercentage(form.liqfeePct)" 
                  @input="onPercentageInput($event, 'liqfeePct')"
                  @blur="formatPercentageOnBlur($event, 'liqfeePct')"
                  inputmode="decimal"
                  placeholder="e.g., 1.50" 
                />
                <small class="form-text text-muted">Enter as percentage (e.g., 1.50 for 1.5%)</small>
              </div>
              <div class="mb-1">
                <label class="form-label form-label-sm text-muted">Liquidation Fee (Flat)</label>
                <input type="text" class="form-control form-control-sm" :value="formatCurrency0(form.liqfeeFlat)" @input="onCurrency0Input($event, 'liqfeeFlat')" inputmode="numeric" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * What/Why/Where/How (developer notes)
 * - What: Client-side UI to browse Servicer model records.
 * - Why: Lets users quickly switch between servicers and view their fee/duration assumptions.
 * - Where: assumptions hub tab, same layout as other tabs.
 * - How: Load list via GET /api/core/servicers/; bind dropdown; show selected via local state.
 */
import { ref, computed, onMounted, reactive, watch } from 'vue'

// Types aligning with ServicerSerializer (projectalphav1/core/serializers/assumptions.py)
interface ServicerDto {
  id: number
  servicerName: string
  contactName: string
  contactEmail: string
  contactPhone: string
  servicingTransferDuration: number
  boardFee: number
  currentFee: number
  thirtdayFee: number
  sixtydayFee: number
  ninetydayFee: number
  onetwentydayFee: number
  fcFee: number
  bkFee: number
  modFee: number
  dilFee: number
  thirdpartyFee: number
  reoFee: number
  reoDays: number
  liqfeePct: number
  liqfeeFlat: number
  defaultForTradeAssumptions?: boolean
}

// Local state
const isLoading = ref(true)
const servicers = ref<ServicerDto[]>([])
const selectedServicerId = ref<number | null>(null)

// Derived selection
const selectedServicer = computed(() => servicers.value.find(s => s.id === selectedServicerId.value))
const isSelectedDefault = computed(() => !!selectedServicer.value?.defaultForTradeAssumptions)

// Reactive form copy of the selected servicer
const form = reactive<Partial<ServicerDto>>({})
const hasChanges = ref(false)
const isSaving = ref(false)
const isSettingDefault = ref(false)

// Sync form when selection changes
watch(selectedServicer, (val) => {
  // Reset form and change state
  for (const k of Object.keys(form)) delete (form as any)[k]
  if (val) Object.assign(form, val)
  hasChanges.value = false
})

// Load all servicers for the dropdown
async function loadServicers() {
  isLoading.value = true
  try {
    const resp = await fetch('/api/core/servicers/', {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include'
    })
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
    const payload = await resp.json()
    const normalizedServicers = Array.isArray(payload)
      ? payload
      : Array.isArray(payload?.results)
        ? payload.results
        : []

    servicers.value = normalizedServicers

    // Auto-select default-for-trades servicer if present, else first
    if (servicers.value.length > 0) {
      const defaultServicer = servicers.value.find(s => s.defaultForTradeAssumptions)
      selectedServicerId.value = defaultServicer ? defaultServicer.id : servicers.value[0].id
    }
  } catch (err) {
    console.error('Error loading servicers:', err)
  } finally {
    isLoading.value = false
  }
}

// Set the selected servicer as default for trade assumptions
async function setAsTradeDefault() {
  if (!selectedServicerId.value) return
  isSettingDefault.value = true
  try {
    const resp = await fetch(`/api/core/servicers/${selectedServicerId.value}/`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ defaultForTradeAssumptions: true })
    })
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
    const updated = await resp.json()
    // Ensure only this servicer is marked as default in local state
    servicers.value = servicers.value.map(s =>
      s.id === updated.id
        ? { ...s, ...updated }
        : { ...s, defaultForTradeAssumptions: false }
    )
  } catch (err) {
    console.error('Error setting default servicer for trades:', err)
    alert('Failed to set default servicer for trade assumptions')
  } finally {
    isSettingDefault.value = false
  }
}

// Utility: format currency/percent for display
function fmtCurrency(v: number | null | undefined): string {
  if (v === null || v === undefined) return '$0'
  try { return `$${Number(v).toLocaleString('en-US', { maximumFractionDigits: 2 })}` } catch { return String(v) }
}
function fmtPercent(v: number | null | undefined): string {
  if (v === null || v === undefined) return '0%'
  try { return `${Number(v).toFixed(2)}%` } catch { return String(v) }
}

onMounted(() => {
  loadServicers()
})

// Mark change
function markChanged() {
  hasChanges.value = true
}

// Display formatter: integers with comma separators, no decimals
function formatCurrency0(v: number | null | undefined): string {
  if (v === null || v === undefined || isNaN(Number(v))) return ''
  try {
    return Number(v).toLocaleString('en-US', { maximumFractionDigits: 0 })
  } catch {
    return String(v)
  }
}

// Input handler: keep only digits, update form as integer, and reflect formatted value
function onCurrency0Input(evt: Event, key: keyof ServicerDto) {
  const el = evt.target as HTMLInputElement
  const digits = (el.value || '').replace(/[^0-9]/g, '')
  const num = digits ? parseInt(digits, 10) : null
  ;(form as any)[key] = num as any
  el.value = num !== null ? formatCurrency0(num) : ''
  markChanged()
}

// WHAT: Format percentage with exactly 2 decimal places
// WHY: Display percentage like "1.50" not "1.5"
// HOW: Use toFixed(2) to ensure trailing zeros
function formatPercentage(v: number | null | undefined): string {
  if (v === null || v === undefined || isNaN(Number(v))) return ''
  try {
    return Number(v).toFixed(2)
  } catch {
    return String(v)
  }
}

// WHAT: Handle percentage input, allow decimals
// WHY: User can enter values like 1.5, 1.50, 2.25, etc.
// HOW: Allow digits and one decimal point
function onPercentageInput(evt: Event, key: keyof ServicerDto) {
  const el = evt.target as HTMLInputElement
  const raw = el.value || ''
  // WHAT: Keep only digits and one decimal point
  let cleaned = raw.replace(/[^0-9.]/g, '')
  // WHAT: Ensure only one decimal point
  const parts = cleaned.split('.')
  if (parts.length > 2) {
    cleaned = parts[0] + '.' + parts.slice(1).join('')
  }
  const num = cleaned ? parseFloat(cleaned) : null
  ;(form as any)[key] = num as any
  markChanged()
}

// WHAT: Format percentage on blur to ensure 2 decimal places
// WHY: When user leaves field, show formatted value like "1.50"
// HOW: Update input value on blur event
function formatPercentageOnBlur(evt: Event, key: keyof ServicerDto) {
  const el = evt.target as HTMLInputElement
  const val = (form as any)[key]
  if (val !== null && val !== undefined && !isNaN(Number(val))) {
    el.value = Number(val).toFixed(2)
  }
}

// Save handler: PATCH selected servicer with form payload
async function saveServicer() {
  if (!selectedServicerId.value) return
  isSaving.value = true
  try {
    const resp = await fetch(`/api/core/servicers/${selectedServicerId.value}/`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(form)
    })
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
    const updated = await resp.json()
    // Update list and selection with returned data
    const idx = servicers.value.findIndex(s => s.id === selectedServicerId.value)
    if (idx !== -1) servicers.value[idx] = updated
    hasChanges.value = false
  } catch (err) {
    console.error('Error saving servicer:', err)
    alert('Failed to save servicer changes')
  } finally {
    isSaving.value = false
  }
}
</script>

<style scoped>
.servicer-assumptions-container { min-height: 200px; }
</style>
