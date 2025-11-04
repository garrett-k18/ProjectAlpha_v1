<!-- This Vue component displays a map with markers for each state in the pool
     and a chart showing the states by count -->



<template>
  <div class="card">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Asset Dispersion</h4>
      <div class="d-flex align-items-center"><!-- controls removed by request --></div>
    </div>

    <div class="card-body pt-0">
      <b-row>
        <b-col lg="8">
          <!-- Loading spinner overlay -->
          <div v-if="markersLoading" class="position-relative" style="min-height: 300px;">
            <div class="d-flex flex-column align-items-center justify-content-center h-100 position-absolute w-100" style="z-index: 10;">
              <div class="spinner-border text-primary mb-2" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
              <p class="text-muted mb-0">Fetching Map Markers...</p>
            </div>
            <!-- Show faded map behind spinner -->
            <div style="opacity: 0.3;">
              <BaseVectorMap
                :key="mapKey"
                id="acq-vector-map"
                class="mt-3 mb-3"
                :map-height="300"
                :options="mapOptions"
                :markers="[]"
              />
            </div>
          </div>
          <!-- Normal map when not loading -->
          <BaseVectorMap
            v-else
            :key="mapKey"
            id="acq-vector-map"
            class="mt-3 mb-3"
            :map-height="300"
            :options="mapOptions"
            :markers="markersForMap"
          />
        </b-col>
        <b-col lg="4" dir="ltr">
          <!-- Replace Apex chart with embedded state strat table (scrollable) -->
          <StratsStates :embedded="true" />
        </b-col>
      </b-row>
    </div>
  </div>
</template>

<script lang="ts">
// Vector map + embedded State Strat table for the acquisitions dashboard
// Docs reviewed:
// - Pinia: https://pinia.vuejs.org/core-concepts/
// - Vue Options API with setup: https://vuejs.org/api/options-state.html#setup
// - jVectorMap API (markers/options): https://jvectormap.com/documentation/javascript-api/
// - ApexCharts Vue: https://apexcharts.com/docs/vue-charts/

import BaseVectorMap from "@/components/base-vector-map.vue";
import StratsStates from "./strats/strats-states.vue";
import { useAcqSelectionsStore } from "@/stores/acqSelections";
import { useAgGridRowsStore } from "@/stores/agGridRows";
// no-op

export default {
  components: { BaseVectorMap, StratsStates },
  // Use setup to access Pinia stores while keeping an Options API component
  setup() {
    const acqStore = useAcqSelectionsStore();
    const gridStore = useAgGridRowsStore();

    return {
      // Expose the store instances to use their reactive state/getters directly
      acqStore,
      gridStore,
      // Actions
      fetchMarkers: acqStore.fetchMarkers,
    };
  },
  data() {
    return {
      // No explicit version; rely on BaseVectorMap internal updates
    }
  },
  computed: {
    // WHAT: jsVectorMap options with event handlers
    // WHY: Computed property allows access to 'this' context for handler methods
    mapOptions() {
      const self = this  // WHAT: Capture 'this' reference for use in arrow functions
      return {
        map: 'us_mill_en',
        normalizeFunction: 'polynomial',
        hoverOpacity: 0.7,
        hoverColor: false,
        regionStyle: {
          initial: {
            // Light gray-blue for all states
            fill: '#91a6bd40',
            stroke: '#ffffff',
            'stroke-width': 1
          },
          hover: {
            fill: '#91a6bd80',
            'stroke-width': 1
          }
        },
        // High-visibility marker styling
        markerStyle: {
          initial: {
            r: 6,
            fill: '#e83e8c',
            stroke: '#ffffff',
            'stroke-width': 2,
            'fill-opacity': 1
          },
          hover: {
            fill: '#ff6fa8',
            'stroke-width': 2
          },
          selected: {
            fill: '#d63384'
          }
        },
        // Keep background transparent; disable scroll zoom
        backgroundColor: 'transparent',
        zoomOnScroll: false,
        zoomButtons: false,
        // Allow selecting markers (visual feedback)
        markersSelectable: true,
        // WHAT: Customize marker tooltip to show Servicer ID, address, and LTVs
        // WHY: Provide quick property details on hover per user requirement
        // HOW: Use onMarkerTooltipShow callback (jsVectorMap API)
        onMarkerTooltipShow: (event, tooltip, index) => {
          console.log('[VectorMap] onMarkerTooltipShow called from map options', { event, tooltip, index })
          self.handleMarkerTooltip(event, tooltip, index)
        },
        // WHAT: Handle marker click to open asset modal
        // WHY: Allow users to access full asset details from map
        onMarkerClick: (event, index) => {
          console.log('[VectorMap] onMarkerClick called from map options')
          self.handleMarkerClick(event, index)
        }
      }
    },
    /** selectionKey and flags proxied from the store to ensure reactivity */
    selectionKey(): string {
      const v = (this.acqStore as any).selectionKey
      return typeof v?.value !== 'undefined' ? v.value : v
    },
    hasBothSelections(): boolean {
      const v = (this.acqStore as any).hasBothSelections
      return typeof v?.value !== 'undefined' ? v.value : v
    },
    selectedSellerId(): number | null {
      const v = (this.acqStore as any).selectedSellerId
      return typeof v?.value !== 'undefined' ? v.value : v
    },
    selectedTradeId(): number | null {
      const v = (this.acqStore as any).selectedTradeId
      return typeof v?.value !== 'undefined' ? v.value : v
    },
    markersLoading(): boolean {
      const v = (this.acqStore as any).loadingMarkers
      return typeof v?.value !== 'undefined' ? v.value : v
    },
    /**
     * mapKey
     * Force remount of BaseVectorMap when either selection changes or
     * markers length changes (ensures jVectorMap re-inits with markers).
     */
    // Build vector map markers from raw store markers to avoid getter unwrap issues
    markersForMap(): any[] {
      const raw = Array.isArray((this.acqStore as any).markers)
        ? (this.acqStore as any).markers
        : ((this.acqStore as any).markers?.value ?? [])
      const safe = Array.isArray(raw) ? raw : []
      console.debug('[VectorMap] markersForMap raw data:', { rawCount: safe.length, firstRaw: safe[0] })
      const out = safe
        .map((m: any) => {
          const lat = typeof m?.lat === 'string' ? parseFloat(m.lat) : m?.lat
          const lng = typeof m?.lng === 'string' ? parseFloat(m.lng) : m?.lng
          const mapped = { latLng: [lat, lng], name: m?.name, id: m?.id }
          console.debug('[VectorMap] Mapping marker:', { input: m, output: mapped })
          return mapped
        })
        .filter((mk: any) => Number.isFinite(mk.latLng?.[0]) && Number.isFinite(mk.latLng?.[1]))
      console.debug('[VectorMap] markersForMap final', { rawCount: safe.length, count: out.length, first: out[0] })
      return out
    },
    /**
     * mapKey
     * Force remount of BaseVectorMap whenever the selection or marker count changes.
     * Prevents duplicate SVGs by ensuring a fresh component instance.
     */
    mapKey(): string {
      const count = Array.isArray(this.markersForMap) ? this.markersForMap.length : 0
      return `${this.selectionKey}:${count}`
    },
    
  },
  mounted() {
    // Initial fetch once mounted, if both seller and trade are selected
    this.fetchMarkersIfReady();
  },
  watch: {
    // When the seller/trade selection pair changes, keep data in sync
    selectionKey() {
      const key = this.selectionKey
      console.count(`[VectorMap] selectionKey changed`)
      this.fetchMarkersIfReady()
      // Note: summaries are fetched exclusively by <StratsStates/> embedded component
    },
    // Removed remount-on-markers-change to reduce re-render churn
  },
  methods: {
    // Fetch markers only when both selections are present.
    async fetchMarkersIfReady() {
      if (this.hasBothSelections) {
        const sid = this.selectedSellerId as number
        const tid = this.selectedTradeId as number
        const label = `[VectorMap] markers ${sid}:${tid}`
        console.time(label)
        try {
          console.debug('[VectorMap] fetchMarkersIfReady calling fetchMarkers', { sid, tid })
          await this.fetchMarkers()
        } finally {
          console.timeEnd(label)
        }
      }
    },
    
    /**
     * WHAT: Handle marker tooltip display with enriched property data
     * WHY: Show Servicer ID, address, and LTV on hover per user requirement
     * HOW: Cross-reference marker ID with grid rows to get full asset data
     */
    handleMarkerTooltip(event, tooltip, index) {
      console.log('[VectorMap] ===== handleMarkerTooltip FIRED =====', { event, tooltip, index })
      
      try {
        // WHAT: Convert index to number (jsVectorMap passes it as string)
        // WHY: Array lookup requires numeric index
        const numericIndex = typeof index === 'string' ? parseInt(index, 10) : index
        
        // WHAT: Get the marker data from our own markersForMap array (not jsvectormap's internal config)
        // WHY: jsvectormap may not preserve custom fields like 'id' in its internal markersConfig
        // HOW: Use the index to look up our original marker data
        const marker = this.markersForMap[numericIndex]
        const markerId = marker?.id
        
        console.log('[VectorMap] Numeric index:', numericIndex)
        console.log('[VectorMap] Our marker data:', marker)
        console.log('[VectorMap] Marker ID:', markerId)
        
        // WHAT: Simple test - just show the marker name first
        const testText = `TEST TOOLTIP\nMarker ${index}\nName: ${marker?.name || 'Unknown'}`
        tooltip.text(testText)  // IMPORTANT: tooltip.text is a METHOD, not a property!
        console.log('[VectorMap] Set tooltip text to:', testText)
        
        // WHAT: Find the corresponding row in grid store using asset_hub_id
        const rows = Array.isArray((this.gridStore as any).rows)
          ? (this.gridStore as any).rows
          : ((this.gridStore as any).rows?.value ?? [])
        
        console.log('[VectorMap] Available rows:', rows.length)
        console.log('[VectorMap] First row sample:', rows[0])
        console.log('[VectorMap] Looking for marker ID:', markerId, 'Type:', typeof markerId)
        
        const asset = rows.find((row: any) => {
          const rowId = row?.id ?? row?.asset_hub_id
          const matches = rowId && rowId === markerId
          if (matches) {
            console.log('[VectorMap] MATCH FOUND!', { rowId, markerId })
          }
          return matches
        })
        
        console.log('[VectorMap] Found asset:', !!asset, asset?.sellertape_id)
        
        // WHAT: If no match, show first 5 row IDs for debugging
        if (!asset && rows.length > 0) {
          const sampleIds = rows.slice(0, 5).map((r: any) => ({ 
            id: r?.id, 
            asset_hub_id: r?.asset_hub_id,
            sellertape_id: r?.sellertape_id
          }))
          console.log('[VectorMap] Sample row IDs (first 5):', sampleIds)
          console.log('[VectorMap] We are looking for markerId:', markerId)
        }
        
        if (asset) {
          // WHAT: Build tooltip content with Servicer ID, address, and LTV
          const servicerId = asset.sellertape_id || 'N/A'
          const address = asset.street_address || marker?.name || 'Unknown Address'
          const city = asset.city || ''
          const state = asset.state || ''
          const cityState = [city, state].filter(Boolean).join(', ')
          
          // WHAT: Calculate LTV (Loan-to-Value ratio)
          // LTV = Total Debt / Property Value (using seller as-is value)
          const totalDebt = parseFloat(asset.total_debt) || 0
          const propertyValue = parseFloat(asset.seller_asis_value) || parseFloat(asset.origination_value) || 0
          const ltv = propertyValue > 0 ? ((totalDebt / propertyValue) * 100).toFixed(1) : 'N/A'
          const ltvNum = typeof ltv === 'string' ? parseFloat(ltv) : ltv
          
          // WHAT: Format currency values
          const formatCurrency = (val) => {
            if (!val || isNaN(val)) return 'N/A'
            return new Intl.NumberFormat('en-US', { 
              style: 'currency', 
              currency: 'USD', 
              maximumFractionDigits: 0 
            }).format(val)
          }
          
          // WHAT: Color code LTV based on risk level
          // WHY: Visual indicator of risk - green (good), yellow (caution), red (high risk)
          const ltvColor = ltvNum !== 'N/A' 
            ? (ltvNum <= 80 ? '#10b981' : ltvNum <= 100 ? '#f59e0b' : '#ef4444')
            : '#6b7280'
          
          // WHAT: Build styled HTML tooltip with better formatting
          // WHY: More visually appealing and easier to read than plain text
          const tooltipHtml = `
            <div style="font-family: 'Inter', -apple-system, sans-serif; padding: 2px 0;">
              <div style="font-size: 11px; color: #6b7280; font-weight: 500; margin-bottom: 6px;">
                ID: ${servicerId}
              </div>
              <div style="font-size: 13px; font-weight: 600; color: #1f2937; margin-bottom: 2px; line-height: 1.3;">
                ${address}
              </div>
              <div style="font-size: 12px; color: #4b5563; margin-bottom: 8px;">
                ${cityState}
              </div>
              <div style="border-top: 1px solid #e5e7eb; padding-top: 6px; font-size: 11px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 3px;">
                  <span style="color: #6b7280;">UPB:</span>
                  <span style="font-weight: 600; color: #1f2937;">${formatCurrency(asset.current_balance)}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 3px;">
                  <span style="color: #6b7280;">Total Debt:</span>
                  <span style="font-weight: 600; color: #1f2937;">${formatCurrency(totalDebt)}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 3px;">
                  <span style="color: #6b7280;">Seller AIV:</span>
                  <span style="font-weight: 600; color: #1f2937;">${formatCurrency(asset.seller_asis_value)}</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding-top: 4px; border-top: 1px solid #e5e7eb; margin-top: 4px;">
                  <span style="color: #6b7280; font-weight: 500;">LTV:</span>
                  <span style="font-weight: 700; color: ${ltvColor}; font-size: 12px;">${ltv}%</span>
                </div>
              </div>
            </div>
          `
          
          tooltip.text(tooltipHtml, true)  // IMPORTANT: Second param 'true' enables HTML rendering
          console.log('[VectorMap] Final tooltip HTML set')
        } else {
          // WHAT: Fallback to address only if asset data not found
          const fallbackText = marker?.name || 'Property'
          tooltip.text(fallbackText)  // IMPORTANT: tooltip.text is a METHOD, not a property!
          console.log('[VectorMap] No asset found, showing fallback:', fallbackText)
        }
      } catch (error) {
        console.error('[VectorMap] handleMarkerTooltip error:', error)
        // WHAT: Graceful fallback on error
        tooltip.text('Error loading tooltip')  // IMPORTANT: tooltip.text is a METHOD, not a property!
      }
    },
    
    /**
     * WHAT: Handle marker click to open asset modal
     * WHY: Allow users to navigate to full asset details from map
     * HOW: Emit event to parent (index_acq_dash) with asset data in correct format
     */
    handleMarkerClick(event, index) {
      try {
        console.log('[VectorMap] handleMarkerClick called', { event, index })
        
        // WHAT: Convert index to number (jsVectorMap passes it as string)
        // WHY: Array lookup requires numeric index
        const numericIndex = typeof index === 'string' ? parseInt(index, 10) : index
        
        // WHAT: Get the marker data to find corresponding asset
        const markers = this.markersForMap
        if (!markers || numericIndex >= markers.length) {
          console.warn('[VectorMap] handleMarkerClick: invalid index', numericIndex, 'markers length:', markers?.length)
          return
        }
        
        const marker = markers[numericIndex]
        const markerId = marker?.id
        
        console.log('[VectorMap] Marker clicked:', { markerId, marker })
        console.log('[VectorMap] Marker keys:', marker ? Object.keys(marker) : 'no marker')
        console.log('[VectorMap] Marker.id value:', marker?.id, 'Type:', typeof marker?.id)
        
        // WHAT: Find the corresponding row in grid store
        const rows = Array.isArray((this.gridStore as any).rows)
          ? (this.gridStore as any).rows
          : ((this.gridStore as any).rows?.value ?? [])
        
        console.log('[VectorMap] Searching in rows:', rows.length)
        
        const asset = rows.find((row: any) => {
          const rowId = row?.id ?? row?.asset_hub_id
          return rowId && rowId === markerId
        })
        
        console.log('[VectorMap] Found asset:', !!asset, asset)
        
        if (asset) {
          // WHAT: Format address the same way the grid does
          const street = asset.street_address || asset.property_address || asset.address || ''
          const city = asset.property_city || asset.city || ''
          const state = asset.property_state || asset.state || ''
          const zip = asset.property_zip || asset.zip || ''
          const addr = [street, city, state, zip].filter(Boolean).join(', ')
          
          // WHAT: Build payload in the exact format expected by onOpenLoan
          // WHY: Match the format used by the grid's View button for consistent modal display
          // CRITICAL: Use database primary key (id), not sellertape_id
          // The backend API endpoints expect the SellerRawData primary key for lookups
          const payload = {
            id: String(asset.id || asset.asset_hub_id),
            row: asset,
            addr: addr
          }
          
          console.log('[VectorMap] Emitting open-loan with payload:', payload)
          this.$emit('open-loan', payload)
        } else {
          console.warn('[VectorMap] handleMarkerClick: asset not found for marker', markerId)
        }
      } catch (error) {
        console.error('[VectorMap] handleMarkerClick error:', error)
      }
    }
  }
}
</script>

<style scoped>
/* Hide jVectorMap zoom buttons for this specific map instance */
#acq-vector-map :deep(.jvectormap-zoomin),
#acq-vector-map :deep(.jvectormap-zoomout) {
  display: none !important;
}

/* WHAT: Style the tooltip container for a modern, polished look */
/* WHY: Make tooltips more visually appealing and easier to read */
#acq-vector-map :deep(.jvectormap-tip) {
  background-color: #ffffff !important;
  border: 1px solid #e5e7eb !important;
  border-radius: 8px !important;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 
              0 4px 6px -2px rgba(0, 0, 0, 0.05) !important;
  padding: 12px 14px !important;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
  min-width: 240px !important;
  max-width: 280px !important;
  pointer-events: none !important;
}

/* WHAT: Remove default jsvectormap tooltip styling artifacts */
#acq-vector-map :deep(.jvectormap-tip)::before,
#acq-vector-map :deep(.jvectormap-tip)::after {
  display: none !important;
}
</style>
