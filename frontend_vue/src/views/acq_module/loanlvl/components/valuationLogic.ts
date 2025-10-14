/**
 * Shared Valuation Logic Composable
 * Extracted from valuationMatrix.vue to be reused across all option mockups
 * Handles data fetching, formatting, and persistence for valuation inputs
 * Component path: frontend_vue/src/views/acq_module/loanlvl/components/valuationLogic.ts
 */

import { ref, computed, watch, unref, type Ref, type ComputedRef } from 'vue'
import http from '@/lib/http'

/**
 * Row model for valuation data
 */
export type ValuationRow = {
  source: string
  asIs: string
  arv: string
  rehab: string
}

/**
 * Shared valuation logic composable
 * Provides reactive state and methods for managing valuation data
 */
export function useValuationLogic(props: any) {
  // Internal state for editable reconciled values
  const internalAsIs = ref<string>('')
  const internalArv = ref<string>('')
  const internalRehab = ref<string>('')
  
  // Digits-only mirrors (kept in sync during typing)
  const internalAsIsDigits = ref<string>('')
  const internalArvDigits = ref<string>('')
  const internalRehabDigits = ref<string>('')
  
  // Server-side values (for change detection)
  const serverAsIs = ref<string | null>(null)
  const serverArv = ref<string | null>(null)
  const serverRehab = ref<string | null>(null)
  
  // Third-party and broker values (for reference rows)
  const thirdPartyAsIsDigits = ref<string>('')
  const thirdPartyArvDigits = ref<string>('')
  const brokerAsIsDigits = ref<string>('')
  const brokerArvDigits = ref<string>('')
  const brokerRehabDigits = ref<string>('')
  
  // UI state
  const saving = ref<boolean>(false)
  const asIsTouched = ref<boolean>(false)
  const arvTouched = ref<boolean>(false)
  const rehabTouched = ref<boolean>(false)

  // Compute seller ID from props
  const sellerId = computed<number | null>(() => {
    const idFromAsset = props.assetId != null ? Number(props.assetId) : null
    const idFromRow = props.row && props.row.id != null ? Number(props.row.id) : null
    return idFromAsset ?? idFromRow ?? null
  })

  // Active row data
  const activeRow = computed<Record<string, any> | null>(() => props.row ?? null)

  /**
   * Format currency: grouped number, no symbol, 0 decimals
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

  /**
   * Build reference valuation rows from live data
   */
  function buildOtherDerivedRows(r: Record<string, any>): ValuationRow[] {
    // Local Agent / Broker values
    const agentAsIs = brokerAsIsDigits.value || (r as any).local_agent_as_is || (r as any).agent_as_is_value || (r as any).agent_as_is || null
    const agentArv = brokerArvDigits.value || (r as any).local_agent_arv || (r as any).agent_arv_value || (r as any).agent_arv || null
    const agentRehab = brokerRehabDigits.value || (r as any).local_agent_rehab_estimate || (r as any).agent_rehab_estimate || null

    // 3rd Party BPO values
    const bpoAsIs = thirdPartyAsIsDigits.value || (r as any).bpo_as_is || (r as any).third_party_bpo_as_is_value || (r as any).third_party_as_is || null
    const bpoArv = thirdPartyArvDigits.value || (r as any).bpo_arv || (r as any).third_party_bpo_arv_value || (r as any).third_party_arv || null
    const bpoRehab = (r as any).bpo_rehab_estimate ?? (r as any).third_party_rehab_estimate ?? null

    return [
      { source: 'Local Agent', asIs: formatCurrency(agentAsIs), arv: formatCurrency(agentArv), rehab: formatCurrency(agentRehab) },
      { source: '3rd Party BPO', asIs: formatCurrency(bpoAsIs), arv: formatCurrency(bpoArv), rehab: formatCurrency(bpoRehab) },
    ]
  }

  /**
   * Compute all reference rows (Seller + Agent + BPO + any custom rows)
   */
  const otherRows = computed<ValuationRow[]>(() => {
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

  /**
   * Whole-number formatting helpers
   */
  function digitsOnly(v: string): string {
    return (v || '').replace(/\D+/g, '')
  }

  function formatWithCommasFromDigits(d: string | null | undefined): string {
    const s = (d || '').replace(/\D+/g, '')
    if (!s) return ''
    return new Intl.NumberFormat('en-US', { style: 'decimal', maximumFractionDigits: 0 }).format(Number(s))
  }

  function isWholeNumberDisplay(v: string): boolean {
    if (v === '') return true
    return /^\s*\d[\d,]*\s*$/.test(v)
  }

  function toDigitsFromValue(value: any): string {
    if (value == null || value === '' || Number.isNaN(Number(value))) return ''
    const n = Math.round(Number(value))
    return String(Math.max(0, n))
  }

  /**
   * Live currency formatter (called on each input update)
   */
  function onCurrencyModel(field: 'asIs' | 'arv' | 'rehab', val: string) {
    const d = digitsOnly(val || '')
    const formatted = formatWithCommasFromDigits(d)
    if (field === 'asIs') {
      internalAsIs.value = formatted
      internalAsIsDigits.value = d
    } else if (field === 'arv') {
      internalArv.value = formatted
      internalArvDigits.value = d
    } else {
      internalRehab.value = formatted
      internalRehabDigits.value = d
    }
  }

  /**
   * Load internal valuation from backend
   */
  async function loadInternalValuation(id: number) {
    try {
      const res = await http.get(`/acq/valuations/internal/${id}/`)
      const d = res.data || {}
      
      const asIsDigits = toDigitsFromValue(d.internal_uw_asis_value)
      const arvDigits = toDigitsFromValue(d.internal_uw_arv_value)
      const rehabDigits = toDigitsFromValue(d.internal_rehab_est_total)
      const tpAsIsDigits = toDigitsFromValue(d.thirdparty_asis_value)
      const tpArvDigits = toDigitsFromValue(d.thirdparty_arv_value)
      const brAsIsDigits = toDigitsFromValue(d.broker_asis_value)
      const brArvDigits = toDigitsFromValue(d.broker_arv_value)
      const brRehabDigits = toDigitsFromValue(d.broker_rehab_est)
      
      serverAsIs.value = asIsDigits || null
      serverArv.value = arvDigits || null
      serverRehab.value = rehabDigits || null
      
      internalAsIs.value = formatWithCommasFromDigits(asIsDigits)
      internalArv.value = formatWithCommasFromDigits(arvDigits)
      internalRehab.value = formatWithCommasFromDigits(rehabDigits)
      
      internalAsIsDigits.value = asIsDigits
      internalArvDigits.value = arvDigits
      internalRehabDigits.value = rehabDigits
      
      thirdPartyAsIsDigits.value = tpAsIsDigits
      thirdPartyArvDigits.value = tpArvDigits
      brokerAsIsDigits.value = brAsIsDigits
      brokerArvDigits.value = brArvDigits
      brokerRehabDigits.value = brRehabDigits
      
      asIsTouched.value = false
      arvTouched.value = false
      rehabTouched.value = false
    } catch (err) {
      console.warn('[ValuationLogic] failed to load internal valuation for', id, err)
      // Reset all values on error
      serverAsIs.value = null
      serverArv.value = null
      serverRehab.value = null
      internalAsIs.value = ''
      internalArv.value = ''
      internalRehab.value = ''
      internalAsIsDigits.value = ''
      internalArvDigits.value = ''
      internalRehabDigits.value = ''
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

  /**
   * Save internal valuation to backend
   */
  async function saveInternalValuation() {
    if (!sellerId.value) return
    
    const asIsDigits = digitsOnly(internalAsIsDigits.value)
    const arvDigits = digitsOnly(internalArvDigits.value)
    const rehabDigits = digitsOnly(internalRehabDigits.value)

    const creating = serverAsIs.value === null && serverArv.value === null
    const payload: Record<string, any> = {}

    if (creating) {
      if (asIsDigits !== '') payload.internal_uw_asis_value = asIsDigits
      if (arvDigits !== '') payload.internal_uw_arv_value = arvDigits
      if (rehabDigits !== '') payload.internal_rehab_est_total = rehabDigits
      if (Object.keys(payload).length === 0) return
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
      
      internalAsIsDigits.value = asIsDigitsNew
      internalArvDigits.value = arvDigitsNew
      internalRehabDigits.value = rehabDigitsNew
    } catch (err) {
      console.warn('[ValuationLogic] failed to save internal valuation for', sellerId.value, err)
    } finally {
      saving.value = false
    }
  }

  /**
   * Blur handlers for each input field
   */
  function onAsIsBlur() {
    asIsTouched.value = true
    if (internalAsIs.value === '' || !isWholeNumberDisplay(internalAsIs.value)) return
    const d = digitsOnly(internalAsIs.value)
    internalAsIs.value = formatWithCommasFromDigits(d)
    internalAsIsDigits.value = d
    saveInternalValuation()
  }

  function onArvBlur() {
    arvTouched.value = true
    if (internalArv.value === '' || !isWholeNumberDisplay(internalArv.value)) return
    const d = digitsOnly(internalArv.value)
    internalArv.value = formatWithCommasFromDigits(d)
    internalArvDigits.value = d
    saveInternalValuation()
  }

  function onRehabBlur() {
    rehabTouched.value = true
    if (internalRehab.value === '' || !isWholeNumberDisplay(internalRehab.value)) return
    const d = digitsOnly(internalRehab.value)
    internalRehab.value = formatWithCommasFromDigits(d)
    internalRehabDigits.value = d
    saveInternalValuation()
  }

  /**
   * Watch seller ID and load data when it changes
   */
  watch(sellerId, (id) => {
    if (id && !Number.isNaN(id)) {
      loadInternalValuation(id)
    } else {
      // Reset all state when no valid ID
      serverAsIs.value = null
      serverArv.value = null
      serverRehab.value = null
      internalAsIs.value = ''
      internalArv.value = ''
      internalRehab.value = ''
      internalAsIsDigits.value = ''
      internalArvDigits.value = ''
      internalRehabDigits.value = ''
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

  // Return all reactive state and methods
  return {
    // Editable values
    internalAsIs,
    internalArv,
    internalRehab,
    // UI state
    asIsTouched,
    arvTouched,
    rehabTouched,
    saving,
    // Computed data
    sellerId,
    otherRows,
    // Methods
    onCurrencyModel,
    onAsIsBlur,
    onArvBlur,
    onRehabBlur,
    isWholeNumberDisplay,
    formatCurrency,
  }
}
