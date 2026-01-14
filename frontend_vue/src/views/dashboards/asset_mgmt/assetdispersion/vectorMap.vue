<template>
  <!-- US-focused vector map component for Asset Management dashboard -->
  <div class="d-flex justify-content-center">
    <BaseVectorMap
      :id="id || 'asset-mgmt-us-map'"
      :map-height="mapHeight"
      :options="mapOptions"
      :markers="markersComputed"
      class="w-100"
    />
  </div>
</template>

<script lang="ts">
/**
 * US Vector Map for Asset Management
 * Uses the same base-vector-map component as the acquisitions dashboard
 * but with a different marker style and focused on the US (including HI and AK)
 */
import { defineComponent, computed } from 'vue';
import BaseVectorMap from "@/components/base-vector-map.vue";

export interface Marker {
  latLng: [number, number];
  name: string;
  value?: number | null;
}

export default defineComponent({
  name: 'AssetMgmtVectorMap',
  components: { BaseVectorMap },
  
  props: {
    id: {
      type: String,
      default: null
    },
    mapHeight: {
      type: Number,
      default: 217
    },
    locationData: {
      type: Array,
      default: () => []
    },
    markerColor: {
      type: String,
      default: '#727cf5'
    },
    markerHoverColor: {
      type: String,
      default: '#4A6FA5' // Using Brand Steel Blue for hover
    },
    markerSelectedColor: {
      type: String,
      default: '#1B3B5F' // Using Brand Navy for selected
    }
  },

  computed: {
    mapOptions() {
      return {
        map: 'us_mill_en',
        normalizeFunction: 'polynomial',
        hoverOpacity: 0.8,
        hoverColor: false,
        regionStyle: {
          initial: {
            fill: '#E9ECEF', // Neutral light gray for professional look
            stroke: '#FFFFFF',
            'stroke-width': 1.5
          },
          hover: {
            fill: '#DEE2E6'
          }
        },
        markerStyle: {
          initial: {
            r: 4,
            fill: this.markerColor,
            stroke: '#ffffff',
            'stroke-width': 1.5,
            'fill-opacity': 0.7
          },
          hover: {
            fill: this.markerHoverColor,
            'stroke-width': 2,
            'fill-opacity': 1
          },
          selected: {
            fill: this.markerSelectedColor
          }
        },
        backgroundColor: 'transparent',
        zoomOnScroll: false,
        zoomButtons: false,
        markersSelectable: true,
        labels: {
          markers: {
            render: (marker: any) => {
              const count = marker?.config?.data?.count
              return typeof count === 'number' && count > 1 ? `${count}` : ''
            },
            offsets: (marker: any) => {
              void marker
              return [0, 0]
            },
          },
        },
        onMarkerTooltipShow: (event: any, tooltip: any, index: number) => {
          void event
          const markerConfig = (tooltip?.mapObject?.markersConfig ?? [])[index]
          const data = markerConfig?.data || {}

          const loanId = data.asset_hub_id ?? ''
          const street = (data.street_address ?? '').toString().trim()
          const city = (data.city ?? '').toString().trim()
          const state = (data.state ?? '').toString().trim()

          const cityState = [city, state].filter(Boolean).join(', ')
          const addressParts = [street, cityState].filter(Boolean)
          let address = addressParts.join(' - ')

          if (!address) {
            const fallbackLabel = (markerConfig?.name ?? '').toString().trim()
            address = fallbackLabel
          }

          const pieces: string[] = []
          if (loanId) pieces.push(String(loanId))
          if (address) pieces.push(address)

          tooltip.text = pieces.join(' - ') || 'Asset'
        },
        onMarkerClick: (event: any, index: number) => {
          void event
          const raw = Array.isArray((this as any).locationData) ? (this as any).locationData : []
          const entry: any = raw[index] || {}
          const assetHubId = entry?.asset_hub_id ?? entry?.asset_hubId ?? null

          const city = (entry?.city ?? '').toString().trim()
          const state = (entry?.state ?? '').toString().trim()
          const street = (entry?.street_address ?? '').toString().trim()
          const cityState = [city, state].filter(Boolean).join(', ')
          let address = [street, cityState].filter(Boolean).join(', ')

          if (!address) {
            const label = (entry?.label ?? entry?.name ?? '').toString().trim()
            address = label
          }

          if (!assetHubId) return

          ;(this as any).$emit('marker-click', {
            assetHubId,
            address,
          })
        },
      };
    },
    
    markersComputed() {
      const raw = Array.isArray(this.locationData) ? this.locationData : [];
      return raw
        .map((entry: any, index: number) => {
          const explicitLatLng = Array.isArray(entry?.latLng) ? entry.latLng : null;
          const latFromFields = typeof entry?.lat === 'number' ? entry.lat : (typeof entry?.lat === 'string' ? Number(entry.lat) : null);
          const lngFromFields = typeof entry?.lng === 'number' ? entry.lng : (typeof entry?.lng === 'string' ? Number(entry.lng) : null);
          const latLngTuple = explicitLatLng ?? (latFromFields !== null && lngFromFields !== null ? [latFromFields, lngFromFields] : null);
          if (!Array.isArray(latLngTuple)) return null;
          const lat = Number(latLngTuple[0]);
          const lng = Number(latLngTuple[1]);
          if (!Number.isFinite(lat) || !Number.isFinite(lng)) return null;
          const preferredName = typeof entry?.name === 'string' && entry.name.trim().length > 0 ? entry.name.trim() : null;
          const fallbackLabel = typeof entry?.label === 'string' && entry.label.trim().length > 0 ? entry.label.trim() : null;
          const defaultLabel = `${lat.toFixed(2)}, ${lng.toFixed(2)}`;
          const markerName = preferredName ?? fallbackLabel ?? defaultLabel;
          const explicitId = typeof entry?.id === 'string' ? entry.id : (typeof entry?.id === 'number' ? String(entry.id) : null);
          const syntheticId = `${lat}-${lng}-${index}`;
          const baseId = explicitId ?? syntheticId;
          const markerLifecycle = (entry?.lifecycle_status ?? entry?.asset_status ?? '').toString().trim().toUpperCase()
          const statusFill = markerLifecycle === 'ACTIVE'
            ? '#28a745'
            : (markerLifecycle === 'LIQUIDATED' ? '#ffc107' : null)

          const explicitStyle = typeof entry?.style === 'object' && entry.style !== null ? entry.style : undefined;
          const style = explicitStyle ?? (statusFill ? {
            initial: { fill: statusFill },
            hover: { fill: statusFill },
            selected: { fill: statusFill },
            selectedHover: { fill: statusFill },
          } : undefined);
          const dataPayload = typeof entry?.data === 'object' && entry.data !== null ? { ...entry.data } : {};
          if (typeof entry?.count !== 'undefined') { dataPayload.count = entry.count; }
          if (typeof entry?.asset_hub_id !== 'undefined') { (dataPayload as any).asset_hub_id = entry.asset_hub_id; }
          if (typeof entry?.state === 'string') { (dataPayload as any).state = entry.state; }
          if (typeof entry?.city === 'string') { (dataPayload as any).city = entry.city; }
          if (typeof entry?.street_address === 'string') { (dataPayload as any).street_address = entry.street_address; }
          if (typeof entry?.lifecycle_status === 'string') { (dataPayload as any).lifecycle_status = entry.lifecycle_status; }
          return {
            latLng: [lat, lng] as [number, number],
            name: markerName,
            id: baseId,
            ...(style ? { style } : {}),
            ...(Object.keys(dataPayload).length > 0 ? { data: dataPayload } : {}),
          };
        })
        .filter((marker: Marker | null): marker is Marker => marker !== null);
    }
  }
});
</script>

<style scoped>
:deep(.jvectormap-zoomin),
:deep(.jvectormap-zoomout) {
  display: none !important;
}
/* Ensure the SVG is centered within the injected jvm container */
:deep(.jvm-container svg) {
  display: block;
  margin: 0 auto;
}
</style>
