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
import { defineComponent, computed } from 'vue';
import BaseVectorMap from "@/components/base-vector-map.vue";

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
            r: 7, // Slightly larger than acquisitions
            fill: this.markerColor,
            stroke: '#ffffff',
            'stroke-width': 1.5,
            'fill-opacity': 0.9
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
        markersSelectable: true
      };
    },
    
    // Define interface for location data items
    markersComputed() {
      // If no location data provided, return empty array
      if (!this.locationData || !Array.isArray(this.locationData)) {
        return [];
      }
      
      // Static mapping of location names to coordinates
      const locationCoords: Record<string, [number, number]> = {
        'New York': [40.71, -74.00],
        'San Francisco': [37.77, -122.41],
        'Chicago': [41.88, -87.63],
        'Los Angeles': [34.05, -118.24],
        'Miami': [25.77, -80.19],
        'Seattle': [47.61, -122.33],
        'Houston': [29.76, -95.37],
        'Boston': [42.36, -71.06],
        'Denver': [39.74, -104.99],
        'Atlanta': [33.75, -84.39],
        'Dallas': [32.78, -96.80],
        'Washington DC': [38.91, -77.04],
        'Phoenix': [33.45, -112.07],
        'Minneapolis': [44.98, -93.27],
        'Philadelphia': [39.95, -75.17],
        // Foreign locations (outside US) - if needed in future
        'Sydney': [-33.86, 151.20],
        'Singapore': [1.3, 103.8],
        'London': [51.51, -0.13],
        'Tokyo': [35.68, 139.76],
        'Toronto': [43.65, -79.38]
      };
      
      // Convert locationData to markers
      return this.locationData
        .map(loc => {
          // Get location name
          let name = '';
          if (typeof loc === 'string') {
            name = loc;
          } else if (loc && typeof loc === 'object') {
            // Safely access properties with type checking
            const locObj = loc as Record<string, any>;
            name = (locObj.location as string) || (locObj.name as string) || '';
          } else {
            name = String(loc);
          }
          
          // Find coordinates for this location
          const coords = name ? locationCoords[name] : undefined;
          if (!coords) return null;
          
          // Use progress as value if available
          let value: number | null = null;
          if (loc && typeof loc === 'object') {
            const locObj = loc as Record<string, any>;
            if (typeof locObj.progress !== 'undefined') {
              value = Number(locObj.progress);
            }
          }
          
          const marker = {
            latLng: coords,
            name: name,
            ...(value !== null ? { value } : {})
          };
          
          return marker;
        })
        // Use simple non-null filter and type assertion since we know the structure
        .filter(m => m !== null) as Marker[];
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
