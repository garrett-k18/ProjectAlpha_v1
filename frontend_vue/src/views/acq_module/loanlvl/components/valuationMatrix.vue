<template>
  <!-- Valuation matrix table only; parent provides the card wrapper and spacing -->
  <div class="table-responsive mb-0">
    <table class="table table-bordered table-centered align-middle mb-0">
      <colgroup>
        <col />
        <col style="width: 28%" />
        <col style="width: 28%" />
        <col style="width: 28%" />
      </colgroup>
      <thead class="table-light">
        <tr>
          <th>Valuation Matrix</th>
          <th>As-Is Value</th>
          <th>After Rehab Value</th>
          <th>Rehab Est.</th>
        </tr>
      </thead>
      <tbody>
        <!-- Top editable Internal Reconciled row (uses Hyper UI/BootstrapVue Next inputs)
             Use text+inputmode to avoid native number spinners; whole-number validation handled in-component.
             Width reduced via Bootstrap grid (~1/3 width). Comma formatting applied on blur and load. -->
        <tr>
          <td>Internal Reconciled</td>
          <td>
            <div class="row gx-0">
              <div class="col-7 col-lg-8">
                <b-form-input
                  v-model="internalAsIs"
                  type="text"
                  inputmode="numeric"
                  size="sm"
                  class="text-start"
                  :disabled="!sellerId || saving"
                  @keydown.enter.prevent="onAsIsBlur"
                  @blur="onAsIsBlur"
                  @keyup.enter="onAsIsBlur"
                />
              </div>
            </div>
            <small v-if="asIsTouched && internalAsIs !== '' && !isWholeNumberDisplay(internalAsIs)" class="text-danger">Enter a whole number (e.g., 123,456).</small>
          </td>
          <td>
            <div class="row gx-0">
              <div class="col-7 col-lg-8">
                <b-form-input
                  v-model="internalArv"
                  type="text"
                  inputmode="numeric"
                  size="sm"
                  class="text-start"
                  :disabled="!sellerId || saving"
                  @keydown.enter.prevent="onArvBlur"
                  @blur="onArvBlur"
                  @keyup.enter="onArvBlur"
                />
              </div>
            </div>
            <small v-if="arvTouched && internalArv !== '' && !isWholeNumberDisplay(internalArv)" class="text-danger">Enter a whole number (e.g., 789,000).</small>
          </td>
          <!-- Internal Rehab Estimate: same numeric flow as As-Is/ARV -->
          <td>
            <div class="row gx-0">
              <div class="col-7 col-lg-8">
                <b-form-input
                  v-model="internalRehab"
                  type="text"
                  inputmode="numeric"
                  size="sm"
                  class="text-start"
                  :disabled="!sellerId || saving"
                  @keydown.enter.prevent="onRehabBlur"
                  @blur="onRehabBlur"
                  @keyup.enter="onRehabBlur"
                />
              </div>
            </div>
            <small v-if="rehabTouched && internalRehab !== '' && !isWholeNumberDisplay(internalRehab)" class="text-danger">Enter a whole number (e.g., 25,000).</small>
          </td>
        </tr>
        <!-- Render remaining live valuation rows (Seller, Agent, BPO, and any props.rows) -->
        <tr v-for="(r, idx) in otherRows" :key="idx">
          <td>{{ r.source }}</td>
          <td>
            <div class="row gx-0">
              <div class="col-7 col-lg-8">
                <div class="form-control-plaintext text-start ps-2 pe-0">{{ r.asIs }}</div>
              </div>
            </div>
          </td>
          <td>
            <div class="row gx-0">
              <div class="col-7 col-lg-8">
                <div class="form-control-plaintext text-start ps-2 pe-0">{{ r.arv }}</div>
              </div>
            </div>
          </td>
          <td>
            <div class="row gx-0">
              <div class="col-7 col-lg-8">
                <div class="form-control-plaintext text-start ps-2 pe-0">{{ r.rehab }}</div>
              </div>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
// valuationMatrix.vue
// Purpose: Reusable Hyper UI/Bootstrap valuation table WITHOUT an outer card.
// The parent component should wrap this with a single card container and control spacing.
// Notes: Live-data only; no demo/fallback rows. When a field is missing, the cell is left blank.

import { withDefaults, defineProps, computed, unref, ref, watch } from 'vue'
// Centralized Axios instance for API calls (baseURL from Vite env)
import http from '@/lib/http'

/**
 * Row model for the valuation table (live data only).
 * - source: label of the value source (e.g., "Seller Values")
 * - asIs: formatted As-Is value (grouped number, no symbol) or '' when missing
 * - arv: formatted After-Rehab value (grouped number, no symbol) or '' when missing
 * - rehab: formatted Rehab estimate (grouped number, no symbol) or '' when missing
 */
export type ValuationRow = {
  source: string
  asIs: string
  arv: string
  rehab: string
}

// Props: accept multiple valuation rows and/or a live SellerRawData row. No demo defaults.
const props = withDefaults(defineProps<{ rows?: ValuationRow[]; row?: Record<string, any> | null; productId?: string | number | null }>(), {
  row: null,
  productId: null,
})

// -----------------------------------------------------------------------------
// Helpers (mirroring snapshotdetails.vue formatting behavior)
// -----------------------------------------------------------------------------
/** Format currency like snapshotdetails.vue: grouped number, no symbol, 0 decimals.
 * Return blank string when value is missing/non-numeric as requested (no fallback text).
 */
const formatCurrency = (value: any) => {
  if (value != null && value !== '' && !isNaN(value)) {
    return new Intl.NumberFormat('en-US', {
      style: 'decimal',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(Number(value))
  }
  return ''
}

// Determine the active row (prefer explicit prop)
const activeRow = computed<Record<string, any> | null>(() => props.row ?? null)

// Compute SellerRawData id used by API calls. Falls back to props.row.id when productId is not provided.
const sellerId = computed<number | null>(() => {
  const idFromProduct = props.productId != null ? Number(props.productId) : null
  const idFromRow = props.row && props.row.id != null ? Number(props.row.id) : null
  return idFromProduct ?? idFromRow ?? null
})

/** Build non-internal default valuation rows from a live data row.
 * Returns Local Agent and 3rd Party BPO rows.
 */
function buildOtherDerivedRows(r: Record<string, any>): ValuationRow[] {
  // Local Agent / Broker
  // Prefer broker values loaded from InternalValuation API; fallback to any fields present on the raw row.
  const agentAsIs = brokerAsIsDigits.value || (r as any).local_agent_as_is || (r as any).agent_as_is_value || (r as any).agent_as_is || null
  const agentArv = brokerArvDigits.value || (r as any).local_agent_arv || (r as any).agent_arv_value || (r as any).agent_arv || null
  const agentRehab = brokerRehabDigits.value || (r as any).local_agent_rehab_estimate || (r as any).agent_rehab_estimate || null

  // 3rd Party BPO
  // Prefer values from InternalValuation API (thirdparty_* fields), which are authoritative
  // Fallback to any fields present on the raw row if available.
  const bpoAsIs = thirdPartyAsIsDigits.value || (r as any).bpo_as_is || (r as any).third_party_bpo_as_is_value || (r as any).third_party_as_is || null
  const bpoArv = thirdPartyArvDigits.value || (r as any).bpo_arv || (r as any).third_party_bpo_arv_value || (r as any).third_party_arv || null
  const bpoRehab = (r as any).bpo_rehab_estimate ?? (r as any).third_party_rehab_estimate ?? null

  return [
    { source: 'Local Agent',         asIs: formatCurrency(agentAsIs),    arv: formatCurrency(agentArv),    rehab: formatCurrency(agentRehab) },
    { source: '3rd Party BPO',       asIs: formatCurrency(bpoAsIs),      arv: formatCurrency(bpoArv),      rehab: formatCurrency(bpoRehab) },
  ]
}

/**
 * Build rows below the editable Internal row by combining:
 * - any rows passed via props.rows (already formatted by caller), and
 * - default rows derived from props.row (Seller + Agent + BPO)
 */
const otherRows = computed<ValuationRow[]>(() => {
  // Unwrap refs and accept reactive arrays; normalize to a plain array
  const rowsInput: any = unref(props.rows) as any
  const baseList: any[] = Array.isArray(rowsInput)
    ? rowsInput
    : rowsInput && typeof rowsInput.length === 'number'
      ? Array.from(rowsInput as any)
      : []
  const fromProps = (baseList as ValuationRow[]).map((r) => ({
    source: r?.source ?? '',
    asIs: r?.asIs ?? '',
    arv: r?.arv ?? '',
    rehab: r?.rehab ?? '',
  }))

  const r = activeRow.value
  if (r) {
    const asIsRaw = (r as any).seller_asis_value ?? (r as any).seller_as_is ?? (r as any).seller_as_is_value ?? null
    const arvRaw = (r as any).seller_arv_value ?? (r as any).seller_arv ?? null
    const rehabRaw = (r as any).seller_rehab_estimate ?? (r as any).rehab_estimate ?? null
    const sellerRow: ValuationRow = {
      source: 'Seller Values',
      asIs: formatCurrency(asIsRaw),
      arv: formatCurrency(arvRaw),
      rehab: formatCurrency(rehabRaw),
    }
    const derived = buildOtherDerivedRows(r)
    return [sellerRow, ...derived, ...fromProps]
  }
  return fromProps
})

// -----------------------------------------------------------------------------
// Editable Internal Reconciled state + API wiring
// -----------------------------------------------------------------------------
/** Internal As-Is numeric input value as a string (allows partial input like "123."). */
const internalAsIs = ref<string>('')
/** Internal ARV numeric input value as a string. */
const internalArv = ref<string>('')
/** Internal Rehab estimate numeric input value as a string. */
const internalRehab = ref<string>('')
/** Server-side values as last loaded from API, used to detect changes. */
const serverAsIs = ref<string | null>(null)
const serverArv = ref<string | null>(null)
const serverRehab = ref<string | null>(null)
/** Third-party values (digits) loaded from InternalValuation for 3rd Party BPO row. */
const thirdPartyAsIsDigits = ref<string>('')
const thirdPartyArvDigits = ref<string>('')
/** Broker values (digits) loaded from InternalValuation for Local Agent/Broker row. */
const brokerAsIsDigits = ref<string>('')
const brokerArvDigits = ref<string>('')
const brokerRehabDigits = ref<string>('')
/** Flag to disable inputs during save. */
const saving = ref<boolean>(false)
/** UI flags to show errors only after user interaction. */
const asIsTouched = ref<boolean>(false)
const arvTouched = ref<boolean>(false)
const rehabTouched = ref<boolean>(false)

/**
 * Whole-number input/formatting helpers for Internal row
 * - digitsOnly: strips all non-digits to produce a clean numeric string for backend
 * - formatWithCommasFromDigits: formats a digits string with grouping (e.g., "123456" -> "123,456")
 * - isWholeNumberDisplay: validates display string (allows 1, 12,345, 1,234,567)
 * - toDigitsFromValue: converts any incoming numeric-ish value to rounded whole-number digits
 */
function digitsOnly(v: string): string {
  // Remove everything except digits; empty when nothing valid
  return (v || '').replace(/\D+/g, '')
}

function formatWithCommasFromDigits(d: string | null | undefined): string {
  const s = (d || '').replace(/\D+/g, '')
  if (!s) return ''
  return new Intl.NumberFormat('en-US', { style: 'decimal', maximumFractionDigits: 0 }).format(Number(s))
}

function isWholeNumberDisplay(v: string): boolean {
  if (v === '') return true // treat empty as neutral
  // Accept any combination of digits and commas (no decimals). We'll reformat on blur.
  return /^\s*\d[\d,]*\s*$/.test(v)
}

function toDigitsFromValue(value: any): string {
  if (value == null || value === '' || Number.isNaN(Number(value))) return ''
  // Round to nearest whole number and return as digits string
  const n = Math.round(Number(value))
  return String(Math.max(0, n))
}

// No BootstrapVue :state to avoid checkmark/X icons; we show our own small error text on blur.

/** Load internal underwriting values from backend for the given seller id. */
async function loadInternalValuation(id: number) {
  try {
    const res = await http.get(`/acq/valuations/internal/${id}/`)
    const d = res.data || {}
    // API may return decimals; we display as whole numbers with commas and keep digits-only for server cache
    const asIsDigits = toDigitsFromValue(d.internal_uw_asis_value)
    const arvDigits = toDigitsFromValue(d.internal_uw_arv_value)
    const rehabDigits = toDigitsFromValue(d.internal_rehab_est_total)
    // Third-party (BPO) values are read-only here; use them to populate the BPO row
    const tpAsIsDigits = toDigitsFromValue(d.thirdparty_asis_value)
    const tpArvDigits = toDigitsFromValue(d.thirdparty_arv_value)
    // Broker values (Local Agent row) are read-only here; populate from API
    const brAsIsDigits = toDigitsFromValue(d.broker_asis_value)
    const brArvDigits = toDigitsFromValue(d.broker_arv_value)
    const brRehabDigits = toDigitsFromValue(d.broker_rehab_est)
    serverAsIs.value = asIsDigits || null
    serverArv.value = arvDigits || null
    serverRehab.value = rehabDigits || null
    internalAsIs.value = formatWithCommasFromDigits(asIsDigits)
    internalArv.value = formatWithCommasFromDigits(arvDigits)
    internalRehab.value = formatWithCommasFromDigits(rehabDigits)
    // Store raw digits for formatting in computed rows
    thirdPartyAsIsDigits.value = tpAsIsDigits
    thirdPartyArvDigits.value = tpArvDigits
    brokerAsIsDigits.value = brAsIsDigits
    brokerArvDigits.value = brArvDigits
    brokerRehabDigits.value = brRehabDigits
    asIsTouched.value = false
    arvTouched.value = false
    rehabTouched.value = false
  } catch (err) {
    // Non-fatal: leave inputs blank
    console.warn('[ValuationMatrix] failed to load internal valuation for', id, err)
    serverAsIs.value = null
    serverArv.value = null
    serverRehab.value = null
    internalAsIs.value = ''
    internalArv.value = ''
    internalRehab.value = ''
    thirdPartyAsIsDigits.value = ''
    thirdPartyArvDigits.value = ''
    brokerAsIsDigits.value = ''
    brokerArvDigits.value = ''
    brokerRehabDigits.value = ''
    asIsTouched.value = false
    arvTouched.value = false
    rehabTouched.value = false
  }
}

/** Persist changes to backend. Creates the row if it does not exist (requires both fields). */
async function saveInternalValuation() {
  if (!sellerId.value) return
  // Prepare clean digits for validation and payload
  const asIsDigits = digitsOnly(internalAsIs.value)
  const arvDigits = digitsOnly(internalArv.value)
  const rehabDigits = digitsOnly(internalRehab.value)

  const creating = serverAsIs.value === null && serverArv.value === null
  const payload: Record<string, any> = {}

  // For creation, send both; for updates, only send changed fields to minimize churn
  if (creating) {
    if (asIsDigits === '' || arvDigits === '') {
      // Require both values to create per backend contract
      return
    }
    payload.internal_uw_asis_value = asIsDigits
    payload.internal_uw_arv_value = arvDigits
    // Rehab is optional (nullable); include when provided
    if (rehabDigits !== '') payload.internal_rehab_est_total = rehabDigits
  } else {
    if (asIsDigits !== '' && asIsDigits !== (serverAsIs.value ?? '')) {
      payload.internal_uw_asis_value = asIsDigits
    }
    if (arvDigits !== '' && arvDigits !== (serverArv.value ?? '')) {
      payload.internal_uw_arv_value = arvDigits
    }
    if (rehabDigits !== '' && rehabDigits !== (serverRehab.value ?? '')) {
      payload.internal_rehab_est_total = rehabDigits
    }
    if (Object.keys(payload).length === 0) return
  }

  try {
    saving.value = true
    const res = await http.patch(`/acq/valuations/internal/${sellerId.value}/`, payload)
    const d = res.data || {}
    const asIsDigitsNew = toDigitsFromValue(d.internal_uw_asis_value)
    const arvDigitsNew = toDigitsFromValue(d.internal_uw_arv_value)
    const rehabDigitsNew = toDigitsFromValue(d.internal_rehab_est_total)
    serverAsIs.value = asIsDigitsNew || null
    serverArv.value = arvDigitsNew || null
    serverRehab.value = rehabDigitsNew || null
    internalAsIs.value = formatWithCommasFromDigits(asIsDigitsNew)
    internalArv.value = formatWithCommasFromDigits(arvDigitsNew)
    internalRehab.value = formatWithCommasFromDigits(rehabDigitsNew)
  } catch (err) {
    console.warn('[ValuationMatrix] failed to save internal valuation for', sellerId.value, err)
  } finally {
    saving.value = false
  }
}

/** Blur handlers for each input; mark touched and attempt save when valid. */
function onAsIsBlur() {
  asIsTouched.value = true
  // If invalid display, do not save; otherwise format and save
  if (internalAsIs.value === '' || !isWholeNumberDisplay(internalAsIs.value)) return
  // Normalize to digits and format with commas for display
  const d = digitsOnly(internalAsIs.value)
  internalAsIs.value = formatWithCommasFromDigits(d)
  saveInternalValuation()
}

function onArvBlur() {
  arvTouched.value = true
  if (internalArv.value === '' || !isWholeNumberDisplay(internalArv.value)) return
  const d = digitsOnly(internalArv.value)
  internalArv.value = formatWithCommasFromDigits(d)
  saveInternalValuation()
}

function onRehabBlur() {
  rehabTouched.value = true
  if (internalRehab.value === '' || !isWholeNumberDisplay(internalRehab.value)) return
  const d = digitsOnly(internalRehab.value)
  internalRehab.value = formatWithCommasFromDigits(d)
  saveInternalValuation()
}

// Load values whenever the target id changes
watch(sellerId, (id) => {
  if (id && !Number.isNaN(id)) {
    loadInternalValuation(id)
  } else {
    serverAsIs.value = null
    serverArv.value = null
    serverRehab.value = null
    internalAsIs.value = ''
    internalArv.value = ''
    internalRehab.value = ''
    thirdPartyAsIsDigits.value = ''
    thirdPartyArvDigits.value = ''
    brokerAsIsDigits.value = ''
    brokerArvDigits.value = ''
    brokerRehabDigits.value = ''
    asIsTouched.value = false
    arvTouched.value = false
    rehabTouched.value = false
  }
}, { immediate: true })
</script>

<style scoped>
/* Uses Bootstrap/Hyper UI built-ins only; no custom styles necessary. */
</style>
