<template>
  <!--
    RiskAssessment.vue
    - Displays environmental and property risk factors
    - Shows risk levels (Low/Medium/High) for various categories
    - Color-coded badges for quick visual assessment
    - Uses Bootstrap/Hyper UI card pattern
  -->
  <div class="card">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title mb-0">Risk Assessment</h4>
      <span class="badge bg-warning-subtle text-warning">Review</span>
    </div>
    <div class="card-body">
      <div class="list-group list-group-flush">
        <div class="list-group-item d-flex justify-content-between align-items-center px-0" 
             v-for="(risk, idx) in riskFactors" :key="idx">
          <div>
            <i :class="`mdi ${risk.icon} me-2 text-${risk.level === 'Low' ? 'success' : risk.level === 'Medium' ? 'warning' : 'danger'}`"></i>
            <span class="fw-semibold">{{ risk.category }}</span>
          </div>
          <span class="badge" :class="`bg-${risk.level === 'Low' ? 'success' : risk.level === 'Medium' ? 'warning' : 'danger'}`">
            {{ risk.level }}
          </span>
        </div>
      </div>
      <div class="alert alert-warning mt-3 mb-0 py-2">
        <i class="mdi mdi-alert-outline me-1"></i>
        <small>Review flood zone and environmental reports before acquisition</small>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * RiskAssessment.vue
 * 
 * Displays environmental and property risk factors with color-coded levels.
 * Helps identify potential issues before acquisition.
 * TODO: Wire to backend risk assessment API when available.
 */
import { computed, withDefaults } from 'vue'

// Props definition
const props = withDefaults(defineProps<{
  row?: Record<string, any> | null
  assetId?: string | number | null
}>(), {
  row: null,
  assetId: null,
})

// Risk Assessment - Environmental and other risk factors
const riskFactors = computed(() => [
  { category: 'Flood Zone', level: 'Low', icon: 'mdi-water' },
  { category: 'Earthquake Risk', level: 'Low', icon: 'mdi-image-filter-hdr' },
  { category: 'Fire Risk', level: 'Medium', icon: 'mdi-fire' },
  { category: 'Crime Rate', level: 'Low', icon: 'mdi-shield-alert' },
  { category: 'Environmental Hazards', level: 'Low', icon: 'mdi-leaf' }
])
</script>
