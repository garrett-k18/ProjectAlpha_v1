<template>
  <!--
    propertydetails.vue
    - Reusable Property Details card showing address, property attributes, and seller/additional values.
    - Accepts either a full `row` object or, if absent, fetches data by `productId`.
    - Styled per Hyper UI/Bootstrap with acquisitions-consistent header.
  -->
  <div class="card h-100">
    <!-- Header -->
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Property Details</h4>
    </div>

    <!-- Body -->
    <div class="card-body pt-0">
      <!-- Empty state -->
      <div v-if="!hasAnyData" class="text-muted text-center py-3">No property details available.</div>

      <!-- Content -->
      <div v-else class="row g-3">
        <!-- Column 1: Core property attributes -->
        <div class="col-md-6">
          <div v-if="fullAddress" class="mb-2">
            <small class="text-muted d-block">Address</small>
            <span class="fw-semibold text-dark">{{ fullAddress }}</span>
          </div>

          <div v-if="rowActive?.property_type" class="mb-2">
            <small class="text-muted d-block">Property Type</small>
            <span
              v-if="propertyBadge"
              class="badge rounded-pill px-3 py-1 fs-6 fw-semibold"
              :class="propertyBadge.color"
              :title="propertyBadge.title || propertyBadge.label"
            >
              {{ propertyBadge.label }}
            </span>
            <span v-else class="fw-semibold text-dark">{{ rowActive?.property_type }}</span>
          </div>

          <div v-if="rowActive?.beds !== null || rowActive?.baths !== null" class="mb-2">
            <small class="text-muted d-block">Bed / Bath</small>
            <span class="fw-semibold text-dark">
              {{ formatBeds(rowActive?.beds) }} bd / {{ formatBaths(rowActive?.baths) }} ba
            </span>
          </div>

          <div v-if="rowActive?.sq_ft" class="mb-2">
            <small class="text-muted d-block">Square Feet</small>
            <span class="fw-semibold text-dark">
              {{ new Intl.NumberFormat().format(rowActive.sq_ft) }} sq ft
            </span>
          </div>

          <div v-if="rowActive?.lot_size" class="mb-2">
            <small class="text-muted d-block">Lot Size</small>
            <span class="fw-semibold text-dark">
              {{ new Intl.NumberFormat().format(rowActive.lot_size) }} sq ft
            </span>
          </div>

          <div v-if="rowActive?.year_built" class="mb-2">
            <small class="text-muted d-block">Year Built</small>
            <span class="fw-semibold text-dark">{{ rowActive.year_built }}</span>
          </div>

          <div v-if="rowActive?.occupancy" class="mb-2">
            <small class="text-muted d-block">Occupancy</small>
            <span
              v-if="occupancyBadge"
              class="badge rounded-pill px-3 py-1 fs-6 fw-semibold"
              :class="occupancyBadge.color"
              :title="occupancyBadge.title || occupancyBadge.label"
            >
              {{ occupancyBadge.label }}
            </span>
            <span v-else class="fw-semibold text-dark">{{ rowActive?.occupancy }}</span>
          </div>
        </div>

        <!-- Column 2: Financials (HOA & Tax) -->
        <div class="col-md-6">
          <!-- HOA Flag / HOA $ (combined) -->
          <!-- TODO: Wire to backend fields once available. Suggested fields:
               - rowActive.hoa_flag: boolean | 'Y' | 'N'
               - rowActive.hoa_amount: number (monthly dollars) -->
          <div class="mb-2">
            <small class="text-muted d-block">HOA</small>
            <span class="fw-semibold text-dark">
              <template v-if="rowActive != null">
                {{ rowActive?.hoa_flag == null ? blankDisplay : (normalizeBool(rowActive?.hoa_flag) ? 'Yes' : 'No') }}
                <template v-if="normalizeBool(rowActive?.hoa_flag) && rowActive?.hoa_amount != null">
                  - {{ formatMoney(rowActive.hoa_amount) }}
                </template>
              </template>
              <template v-else>{{ blankDisplay }}</template>
            </span>
          </div>

          <!-- Property Tax Rate (percentage) -->
          <!-- TODO: Wire to backend: rowActive.property_tax_rate (e.g., 0.0125 for 1.25%) -->
          <div class="mb-2">
            <small class="text-muted d-block">Property Tax Rate</small>
            <span class="fw-semibold text-dark">
              <template v-if="rowActive != null && rowActive.property_tax_rate != null">
                {{ formatPercent(rowActive.property_tax_rate) }}
              </template>
              <template v-else>{{ blankDisplay }}</template>
            </span>
          </div>

          <!-- Assessed Value (currency) -->
          <!-- TODO: Wire to backend: rowActive.assessed_value (number) -->
          <div class="mb-2">
            <small class="text-muted d-block">Assessed Value</small>
            <span class="fw-semibold text-dark">
              <template v-if="rowActive != null && rowActive.assessed_value != null">
                {{ formatMoney(rowActive.assessed_value) }}
              </template>
              <template v-else>{{ blankDisplay }}</template>
            </span>
          </div>

          <!-- Property Taxes (Prev Year) (currency) -->
          <!-- TODO: Wire to backend: rowActive.property_taxes_prev_year (number) -->
          <div class="mb-2">
            <small class="text-muted d-block">Property Taxes (Prev Year)</small>
            <span class="fw-semibold text-dark">
              <template v-if="rowActive != null && rowActive.property_taxes_prev_year != null">
                {{ formatMoney(rowActive.property_taxes_prev_year) }}
              </template>
              <template v-else>{{ blankDisplay }}</template>
            </span>
          </div>
        </div>

        <!-- Removed seller/additional valuation fields per request -->
      </div>
    </div>
  </div>
</template>

<script lang="ts">
/**
 * propertydetails.vue
 * - Displays address (street, city, state, zip), property_type, occupancy,
 *   and seller/additional values and dates.
 * - Props allow passing a `row` directly or fetching by `productId`.
 */
import { defineComponent, computed, ref, watch } from 'vue'
import type { PropType } from 'vue'
import http from '@/lib/http'

export default defineComponent({
  name: 'PropertyDetails',
  props: {
    row: { type: Object as PropType<Record<string, any> | null>, default: null },
    assetId: { type: [String, Number] as PropType<string | number | null>, default: null },
  },
  setup(props) {
    const fetchedRow = ref<Record<string, any> | null>(null)
    const rowActive = computed(() => props.row ?? fetchedRow.value)

    const blankDisplay = '' // WHAT: Centralized blank display string so property details omit placeholder glyphs when data is unavailable

    const fullAddress = computed(() => {
      const r = rowActive.value as any
      if (!r) return ''
      const parts = [r.street_address, r.city, r.state, r.zip].filter(Boolean)
      return parts.join(', ')
    })

    const hasAnyData = computed<boolean>(() => {
      const r = rowActive.value as any
      return !!(r && (
        r.street_address || r.city || r.state || r.zip ||
        r.property_type || r.occupancy ||
        r.beds != null || r.baths != null || r.sq_ft != null || r.lot_size != null || r.year_built != null ||
        r.hoa_flag != null || r.hoa_amount != null || r.property_tax_rate != null ||
        r.assessed_value != null || r.property_taxes_prev_year != null
      ))
    })

    async function loadRowById(id: number) {
      try {
        const res = await http.get(`/acq/raw-data/by-id/${id}/`)
        fetchedRow.value = res.data && Object.keys(res.data).length ? res.data : null
        // eslint-disable-next-line no-console
        console.debug('[PropertyDetails] loaded row for', id)
      } catch (err) {
        // eslint-disable-next-line no-console
        console.warn('[PropertyDetails] failed to load row for', id, err)
        fetchedRow.value = null
      }
    }

    watch(
      () => props.assetId,
      (raw) => {
        const id = raw != null ? Number(raw) : NaN
        if (!props.row && Number.isFinite(id)) {
          loadRowById(id)
        } else if (!Number.isFinite(id)) {
          fetchedRow.value = null
        }
      },
      { immediate: true }
    )

    const formatCurrency = (v: any) => {
      if (v != null && !isNaN(v)) {
        return new Intl.NumberFormat('en-US', { style: 'decimal', minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(Number(v))
      }
      return blankDisplay // WHAT: Return empty string so UI leaves cells blank when numeric value missing
    }

    const formatDate = (v: any) => (v ? new Date(v).toLocaleDateString('en-US') : blankDisplay) // WHAT: Render blank string if date absent

    // Format currency with USD symbol and no decimals per platform convention for most UI readouts
    const formatMoney = (v: any) => {
      if (v != null && !isNaN(v)) {
        return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(Number(v))
      }
      return blankDisplay // WHAT: Keep financial fields blank when values missing per AM UX guidance
    }

    // Format percent from decimal input (e.g., 0.0125 -> 1.25%)
    const formatPercent = (v: any) => {
      if (v != null && !isNaN(v)) {
        const pct = Number(v) * 100
        return `${pct.toFixed(2)}%`
      }
      return blankDisplay // WHAT: Leave percentage cells empty when source data missing
    }

    const formatBeds = (v: any): string => {
      if (v == null || v === '') return blankDisplay // WHAT: Provide empty string when bed count missing so snapshot card shows blank per UX request
      const num = Number(v)
      return Number.isFinite(num) ? String(num) : String(v)
    }

    const formatBaths = (v: any): string => {
      if (v == null || v === '') return blankDisplay // WHAT: Mirror bed formatter for bath values while keeping decimals intact when available
      const num = Number(v)
      if (!Number.isFinite(num)) return String(v)
      return num % 1 === 0 ? `${num.toFixed(0)}` : `${num.toFixed(1)}`
    }

    // Normalize boolean-like fields (true/'Y'/'YES' -> true)
    const normalizeBool = (v: any): boolean => {
      if (typeof v === 'boolean') return v
      if (v == null) return false
      const s = String(v).trim().toLowerCase()
      return s === 'y' || s === 'yes' || s === 'true' || s === '1'
    }

    // Badge color maps copied from AG Grid configuration to keep visual parity
    // Property Type badge colors
    const propertyTypeBadgeMap: Record<string, { label: string; color: string; title?: string }> = {
      'SFR': { label: 'SFR', color: 'bg-success', title: 'Single Family Residence' },
      'Manufactured': { label: 'Manufactured', color: 'bg-info', title: 'Manufactured Home' },
      'Condo': { label: 'Condo', color: 'bg-primary', title: 'Condominium' },
      '2-4 Family': { label: '2-4 Family', color: 'bg-warning', title: '2-4 Family Property' },
      'Land': { label: 'Land', color: 'bg-danger', title: 'Vacant Land' },
      'Multifamily 5+': { label: 'Multifamily 5+', color: 'bg-secondary', title: 'Multifamily 5+ Units' },
    }

    // Occupancy badge colors
    const occupancyBadgeMap: Record<string, { label: string; color: string; title?: string }> = {
      'Vacant': { label: 'Vacant', color: 'bg-danger', title: 'Property is Vacant' },
      'Occupied': { label: 'Occupied', color: 'bg-success', title: 'Property is Occupied' },
      'Unknown': { label: 'Unknown', color: 'bg-warning', title: 'Occupancy Status Unknown' },
    }

    // Compute badges from current row
    const propertyBadge = computed(() => {
      const r = rowActive.value as any
      if (!r || !r.property_type) return null
      const key = String(r.property_type)
      return propertyTypeBadgeMap[key] || null
    })

    const occupancyBadge = computed(() => {
      const r = rowActive.value as any
      if (!r || !r.occupancy) return null
      const key = String(r.occupancy)
      return occupancyBadgeMap[key] || null
    })

    return { rowActive, hasAnyData, fullAddress, formatCurrency, formatDate, formatMoney, formatPercent, normalizeBool, propertyBadge, occupancyBadge, blankDisplay, formatBeds, formatBaths }
  },
})
</script>

<style scoped>
/* No custom styles beyond Hyper/Bootstrap utilities */
</style>
