<template>
  <!-- Valuation Matrix Option 2: Comparison Grid -->
  <div class="card">
    <!-- Card Header -->
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Valuation Summary</h4>
      <div v-if="saving" class="text-muted small">
        <i class="mdi mdi-reload mdi-spin me-1"></i>Saving…
      </div>
    </div>

    <!-- Card Body -->
    <div class="card-body pt-0">
      <div class="table-responsive">
        <table class="table table-centered table-hover mb-0">
          <thead class="table-light">
            <tr>
              <th class="text-center">Quick Links</th>
              <th class="text-center">Seller AIV - ARV</th>
              <th class="text-center">BPO AIV - ARV</th>
              <th class="text-center">Broker AIV - ARV</th>
              <th class="text-center">Internal AIV - ARV</th>
            </tr>
          </thead>
          <tbody>
            <!-- Single row showing all valuation sources -->
            <tr>
              <td class="text-center py-1">
                <!-- WHAT: 3rd Party Site Links - stacked vertically with minimal spacing -->
                <div class="d-flex flex-column align-items-center" style="gap: 1px; line-height: 1.3;">
                  <a 
                    :href="getZillowUrl()" 
                    target="_blank" 
                    class="third-party-link small"
                  >
                    Zillow <i class="ri-external-link-line"></i>
                  </a>
                  <a 
                    :href="getRedfinUrl()" 
                    target="_blank" 
                    class="third-party-link small"
                  >
                    Redfin <i class="ri-external-link-line"></i>
                  </a>
                  <a 
                    :href="getRealtorUrl()" 
                    target="_blank" 
                    class="third-party-link small"
                  >
                    Realtor <i class="ri-external-link-line"></i>
                  </a>
                </div>
              </td>
              <td class="text-center">
                <span>{{ formatCurrency(getSellerAsIs()) }}</span>
                <span class="mx-2"> - </span>
                <span>{{ formatCurrency(getSellerArv()) }}</span>
              </td>
              <td class="text-center">
                <span>{{ formatCurrency(getBpoAsIs()) }}</span>
                <span class="mx-2"> - </span>
                <span>{{ formatCurrency(getBpoArv()) }}</span>
              </td>
              <td class="text-center">
                <span>{{ formatCurrency(getBrokerAsIs()) }}</span>
                <span class="mx-2"> - </span>
                <span>{{ formatCurrency(getBrokerArv()) }}</span>
              </td>
              <td class="text-center">
                <!-- WHAT: Editable Internal UW As-Is Value - already formatted by composable -->
                <input
                  type="text"
                  class="editable-value-inline"
                  :value="formatInternalCurrency(internalAsIs)"
                  @input="onInternalAsIsInput"
                  @blur="onAsIsBlur"
                  @keyup.enter="onAsIsBlur"
                  placeholder="-"
                />
                <span style="margin: 0 0px;"> - </span>
                <!-- WHAT: Editable Internal UW ARV Value - already formatted by composable -->
                <input
                  type="text"
                  class="editable-value-inline"
                  :value="formatInternalCurrency(internalArv)"
                  @input="onInternalArvInput"
                  @blur="onArvBlur"
                  @keyup.enter="onArvBlur"
                  placeholder="-"
                />
              </td>
            </tr>

            <!-- Empty State (only show if no row data at all) -->
            <tr v-if="!props.row">
              <td colspan="5" class="text-center text-muted py-3">
                No asset data available.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Valuation Matrix Option 2: Comparison Grid
 * 
 * Displays a clean grid layout with side-by-side comparison of all valuation sources.
 * Internal reconciled values are editable inputs, supporting values are read-only.
 * Uses color-coded badges for easy source identification.
 */
import { withDefaults } from 'vue'
import { useValuationLogic } from './valuationLogic'

// Props definition
const props = withDefaults(defineProps<{
  rows?: any[]
  row?: Record<string, any> | null
  assetId?: string | number | null
}>(), {
  row: null,
  assetId: null,
})

// Use shared valuation logic composable
const {
  internalAsIs,
  internalArv,
  internalRehab,
  asIsTouched,
  arvTouched,
  rehabTouched,
  saving,
  sellerId,
  otherRows,
  onCurrencyModel,
  onAsIsBlur,
  onArvBlur,
  onRehabBlur,
  isWholeNumberDisplay,
} = useValuationLogic(props)

// WHAT: Helper functions to extract valuation data from row
// WHY: Centralize data extraction logic and handle multiple field name variations
function getSellerAsIs(): number | null {
  const r = props.row
  return r?.seller_asis_value ?? r?.seller_as_is ?? r?.seller_as_is_value ?? null
}

function getSellerArv(): number | null {
  const r = props.row
  return r?.seller_arv_value ?? r?.seller_arv ?? null
}

function getBpoAsIs(): number | null {
  const r = props.row
  return r?.additional_asis_value ?? r?.bpo_as_is ?? r?.third_party_bpo_as_is_value ?? null
}

function getBpoArv(): number | null {
  const r = props.row
  return r?.additional_arv_value ?? r?.bpo_arv ?? r?.third_party_bpo_arv_value ?? null
}

function getBrokerAsIs(): number | null {
  const r = props.row
  return r?.broker_asis_value ?? r?.local_agent_as_is ?? r?.agent_as_is_value ?? null
}

function getBrokerArv(): number | null {
  const r = props.row
  return r?.broker_arv_value ?? r?.local_agent_arv ?? r?.agent_arv_value ?? null
}

// WHAT: Get Internal UW values from row data
// WHY: Display existing internal valuations loaded from database
function getInternalAsIs(): number | null {
  const r = props.row
  return r?.internal_initial_uw_asis_value ?? r?.internal_uw_asis_value ?? null
}

function getInternalArv(): number | null {
  const r = props.row
  return r?.internal_initial_uw_arv_value ?? r?.internal_uw_arv_value ?? null
}

// WHAT: Format currency for display
function formatCurrency(val: number | null): string {
  if (val == null) return '-'
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val)
}

// WHAT: Generate 3rd party site URLs using property address from row
function getZillowUrl(): string {
  const r = props.row
  const street = r?.property_address || r?.street_address || r?.address || ''
  const city = r?.property_city || r?.city || ''
  const state = r?.property_state || r?.state || ''
  const fullAddress = `${street}, ${city}, ${state}`.replace(/\s+/g, '-').replace(/,/g, '')
  return `https://www.zillow.com/homes/${encodeURIComponent(fullAddress)}_rb/`
}

function getRedfinUrl(): string {
  const r = props.row
  const street = (r?.property_address || r?.street_address || r?.address || '').replace(/\s+/g, '-')
  const city = (r?.property_city || r?.city || '').replace(/\s+/g, '-')
  const state = (r?.property_state || r?.state || '').toUpperCase()
  
  if (!street || !city || !state) {
    return 'https://www.redfin.com'
  }
  
  return `https://www.redfin.com/${state}/${city}/${street}`
}

function getRealtorUrl(): string {
  const r = props.row
  const street = (r?.property_address || r?.street_address || r?.address || '').replace(/\s+/g, '-')
  const city = (r?.property_city || r?.city || '').replace(/\s+/g, '-')
  const state = (r?.property_state || r?.state || '').toUpperCase()
  const zip = r?.property_zip || r?.zip || r?.zipcode || ''
  
  if (!street || !city || !state || !zip) {
    return 'https://www.realtor.com'
  }
  
  return `https://www.realtor.com/realestateandhomes-detail/${street}_${city}_${state}_${zip}`
}

// WHAT: Format internal values for display in input (add $ sign if value exists)
// WHY: Show currency format to match other columns
// HOW: The composable stores values as formatted strings like "200,000" - add $ prefix
function formatInternalCurrency(val: string): string {
  if (!val || val.trim() === '') return ''
  // WHAT: If value already has commas, it's formatted - add $ if not present
  if (val.includes(',') && !val.includes('$')) {
    return '$' + val
  }
  // WHAT: If it already has $, return as is
  if (val.includes('$')) {
    return val
  }
  // WHAT: If it's just digits, add $ and commas
  const cleaned = val.replace(/\D/g, '')
  if (cleaned) {
    return '$' + new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 }).format(Number(cleaned))
  }
  return val
}

// WHAT: Handle input for Internal As-Is field
// WHY: Keep composable's onCurrencyModel in sync
function onInternalAsIsInput(event: Event) {
  const input = event.target as HTMLInputElement
  onCurrencyModel('asIs', input.value)
}

// WHAT: Handle input for Internal ARV field
// WHY: Keep composable's onCurrencyModel in sync
function onInternalArvInput(event: Event) {
  const input = event.target as HTMLInputElement
  onCurrencyModel('arv', input.value)
}
</script>

<style scoped>
/* WHAT: 3rd party site link styling - compact */
/* WHY: Make external links visually consistent and appealing with minimal spacing */
.third-party-link {
  color: #0d6efd;
  text-decoration: none;
  transition: all 0.2s ease;
  font-size: 0.8rem;
  white-space: nowrap;
  line-height: 1.1;
  padding: 0;
  margin: 0;
  display: inline-block;
}

.third-party-link:hover {
  color: #0b5ed7;
  text-decoration: underline;
}

.third-party-link i {
  font-size: 0.7rem;
  opacity: 0.7;
  margin-left: 2px;
}

/* WHAT: Editable inline value styling - blend with table text */
/* WHY: Make editable fields look seamless, only showing they're editable via color and underline */
.editable-value-inline {
  /* WHAT: Remove all borders and background to blend in */
  border: none;
  background: transparent;
  padding: 0;
  
  /* WHAT: Match table text styling */
  font-family: inherit;
  font-size: inherit;
  text-align: center;
  
  /* WHAT: Blue color with underline to indicate editability */
  color: #0d6efd;
  text-decoration: underline;
  text-decoration-style: solid;
  text-underline-offset: 2px;
  
  /* WHAT: Set width to accommodate currency values */
  width: 90px;
  display: inline-block;
  
  /* WHAT: Smooth cursor transition */
  cursor: text;
  transition: all 0.2s ease;
}

/* WHAT: Hover state - slightly darker blue */
.editable-value-inline:hover {
  color: #0b5ed7;
  text-decoration-thickness: 2px;
}

/* WHAT: Focus state - remove outline, keep underline, slightly bolder */
.editable-value-inline:focus {
  outline: none;
  color: #0a58ca;
  text-decoration-thickness: 2px;
  font-weight: 500;
}

/* WHAT: Placeholder styling to match empty cells */
.editable-value-inline::placeholder {
  color: #6c757d;
  opacity: 0.5;
}

/* Purple badge variant (not in Bootstrap by default) */
.bg-purple-subtle {
  background-color: #f3e5f5 !important;
}

.text-purple {
  color: #6a1b9a !important;
}
</style>


