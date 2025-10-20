<template>
  <!-- US-focused vector map component for Asset Management dashboard -->
  <div>
    <BaseVectorMap
      :id="id || 'asset-mgmt-us-map'"
      :map-height="mapHeight"
      :options="mapOptions"
      :markers="markersComputed"
    />
  </div>
</template>

<script lang="ts">
/**
 * US Vector Map for Asset Management
 * Uses the same base-vector-map component as the acquisitions dashboard
 * but with a different marker style and focused on the US (including HI and AK)
 */
import { defineComponent, computed } from 'vue'; // WHAT: Import Vue helpers to create the component with computed props.
import BaseVectorMap from "@/components/base-vector-map.vue"; // WHAT: Import shared vector map wrapper built on jsVectorMap.

// Define interface for map markers
export interface Marker {
  latLng: [number, number];
  name: string;
  value?: number | null;
}

export default defineComponent({
  name: 'AssetMgmtVectorMap',
  components: { BaseVectorMap },
  
  props: {
    // Allow custom ID for the map element
    id: {
      type: String,
      default: null
    },
    // Custom height for the map
    mapHeight: {
      type: Number,
      default: 217
    },
    // Location data to display on the map
    locationData: {
      type: Array,
      default: () => []
    },
    // Optional custom marker color (can be changed from parent)
    markerColor: {
      type: String,
      default: '#4fc6e1' // Default: blue-ish color (different from acquisitions pink)
    },
    // Optional custom marker hover color
    markerHoverColor: {
      type: String,
      default: '#69d3ea' // Lighter blue for hover
    },
    // Optional custom marker selected color
    markerSelectedColor: {
      type: String,
      default: '#3db9d3' // Darker blue for selected
    }
  },

  computed: {
    // jVectorMap options for US map with markers
    mapOptions() {
      return {
        // Use US Miller map that includes HI and AK
        map: 'us_mill_en',
        normalizeFunction: 'polynomial',
        hoverOpacity: 0.7,
        hoverColor: false,
        regionStyle: {
          initial: {
            fill: '#91a6bd40' // Light gray-blue for states
          }
        },
        // Custom marker styling (different from acquisitions)
        markerStyle: {
          initial: {
            r: 2.5, // WHAT: Further shrink single-asset pins to size 3 per latest requirement.
            fill: this.markerColor,
            stroke: '#ffffff',
            'stroke-width': 1.5,
            'fill-opacity': 0.5
          },
          hover: {
            fill: this.markerHoverColor,
            'stroke-width': 2
          },
          selected: {
            fill: this.markerSelectedColor
          }
        },
        // Keep background transparent; disable scroll zoom
        backgroundColor: 'transparent',
        zoomOnScroll: false,
        zoomButtons: false,
        // Enable marker selection for interaction
        markersSelectable: true,
        labels: { // WHAT: Configure inline marker labels so clusters display counts (docs: https://github.com/themustafaomar/jsvectormap#labels).
          markers: {
            render: (marker: any) => { // WHAT: Render callback receives marker configuration object from jsVectorMap.
              const count = marker?.config?.data?.count // WHAT: Extract density count injected via Pinia store for this cluster.
              return typeof count === 'number' ? `${count}` : '' // WHAT: Return numeric count as string to display inside the cluster bubble.
            },
            offsets: (marker: any) => { // WHAT: Provide zero offsets to keep labels centered in the marker circle.
              void marker // WHAT: Explicitly touch argument to satisfy lint for unused variables.
              return [0, 0]
            },
          },
        },
        onMarkerTooltipShow: (event: any, tooltip: any, index: number) => { // WHAT: Customize tooltip text to show location label + density count.
          void event // WHAT: Prevent unused variable lint for emitted event parameter.
          const markerConfig = (tooltip?.mapObject?.markersConfig ?? [])[index] // WHAT: Access normalized markers array maintained by jsVectorMap instance.
          const name = markerConfig?.name ?? 'Active Assets' // WHAT: Fallback label when no explicit name is provided by backend.
          const count = markerConfig?.data?.count ?? 0 // WHAT: Density metadata provided via Pinia store for this marker.
          tooltip.text = `${name}\n${count} assets` // WHAT: Use documented jsVectorMap tooltip API (https://jsvectormap.com/documentation) to set two-line content.
        },
      };
    },
    
    // Define interface for location data items
    markersComputed() {
      const raw = Array.isArray(this.locationData) ? this.locationData : []; // WHAT: Ensure we always iterate over an array to avoid runtime errors.
      return raw
        .map((entry: any, index: number) => { // WHAT: Transform each raw marker entry into jsVectorMap format.
          const explicitLatLng = Array.isArray(entry?.latLng) ? entry.latLng : null; // WHAT: Detect pre-normalized lat/lng tuples provided by store.
          const latFromFields = typeof entry?.lat === 'number' ? entry.lat : (typeof entry?.lat === 'string' ? Number(entry.lat) : null); // WHAT: Handle markers exposing lat numeric or string fields for flexibility.
          const lngFromFields = typeof entry?.lng === 'number' ? entry.lng : (typeof entry?.lng === 'string' ? Number(entry.lng) : null); // WHAT: Handle markers exposing lng numeric or string fields for flexibility.
          const latLngTuple = explicitLatLng ?? (latFromFields !== null && lngFromFields !== null ? [latFromFields, lngFromFields] : null); // WHAT: Pick the best available coordinate source for the marker.
          if (!Array.isArray(latLngTuple)) return null; // WHAT: Abort markers without coordinates so map renders cleanly.
          const lat = Number(latLngTuple[0]); // WHAT: Force latitude into numeric form for jsVectorMap consumption.
          const lng = Number(latLngTuple[1]); // WHAT: Force longitude into numeric form for jsVectorMap consumption.
          if (!Number.isFinite(lat) || !Number.isFinite(lng)) return null; // WHAT: Skip entries with invalid numeric coordinates.
          const preferredName = typeof entry?.name === 'string' && entry.name.trim().length > 0 ? entry.name.trim() : null; // WHAT: Capture explicit marker name when present.
          const fallbackLabel = typeof entry?.label === 'string' && entry.label.trim().length > 0 ? entry.label.trim() : null; // WHAT: Use backend label fallback when explicit name absent.
          const defaultLabel = `${lat.toFixed(2)}, ${lng.toFixed(2)}`; // WHAT: Generate coordinate-based label as last resort for readability.
          const markerName = preferredName ?? fallbackLabel ?? defaultLabel; // WHAT: Pick the most descriptive label available for tooltips.
          const explicitId = typeof entry?.id === 'string' ? entry.id : (typeof entry?.id === 'number' ? String(entry.id) : null); // WHAT: Use provided identifier when available for Vue keying.
          const syntheticId = `${lat}-${lng}-${index}`; // WHAT: Build fallback identifier combining coordinates and index to ensure uniqueness.
          const baseId = explicitId ?? syntheticId; // WHAT: Finalize marker identifier for stable rendering.
          const style = typeof entry?.style === 'object' && entry.style !== null ? entry.style : undefined; // WHAT: Respect custom marker style (e.g., radius) supplied by store.
          const dataPayload = typeof entry?.data === 'object' && entry.data !== null ? { ...entry.data } : {}; // WHAT: Clone ancillary data for safe downstream consumption.
          if (typeof entry?.count !== 'undefined') { dataPayload.count = entry.count; } // WHAT: Inline density count metric for tooltips when count provided separately.
          const marker = {
            latLng: [lat, lng] as [number, number], // WHAT: Provide coordinates in jsVectorMap format.
            name: markerName, // WHAT: Attach resolved label to marker for tooltip display.
            id: baseId, // WHAT: Attach identifier to help Vue track marker updates.
            ...(style ? { style } : {}), // WHAT: Include style block only when defined to keep payload lean.
            ...(Object.keys(dataPayload).length > 0 ? { data: dataPayload } : {}), // WHAT: Include data object only when it carries at least one property.
          }; // WHAT: Compose normalized marker object required by BaseVectorMap.
          return marker; // WHAT: Emit normalized marker for current entry.
        })
        .filter((marker: Marker | null): marker is Marker => marker !== null); // WHAT: Remove null placeholders while asserting type for TypeScript.
    }
  }
});
</script>

<style scoped>
/* Hide jVectorMap zoom buttons */
:deep(.jvectormap-zoomin),
:deep(.jvectormap-zoomout) {
  display: none !important;
}
</style>
