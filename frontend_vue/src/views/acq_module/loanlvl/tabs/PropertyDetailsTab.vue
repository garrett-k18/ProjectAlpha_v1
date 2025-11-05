<template>
  <div class="p-3">
    <!-- Row 1: Core Property Information -->
    <div class="row g-3 mb-3">
      <div class="col-12 col-lg-6 col-xl-4 d-flex">
        <PropertyDetails class="w-100 h-100" :row="row" :assetId="assetId" />
      </div>

      <div class="col-12 col-lg-6 col-xl-4 d-flex">
        <DemographicsGrid class="w-100 h-100" :row="row" :assetId="assetId" />
      </div>

      <div class="col-12 col-lg-6 col-xl-4 d-flex">
        <ConditionAssessment class="w-100 h-100" :row="row" :assetId="assetId" />
      </div>
    </div>

    <!-- Row 3: Comparable Sales -->
    <div class="row g-3 mb-2">
      <div class="col-12">
        <ComparableSales :row="row" :assetId="assetId" />
      </div>
    </div>

    <!-- Row 4: Neighborhood Insights & Risk Factors -->
    <div class="row g-3 mb-1">
      <div class="col-12 col-lg-6">
        <NeighborhoodInsights :row="row" :assetId="assetId" />
      </div>

      <div class="col-12 col-lg-6">
        <RiskAssessment :row="row" :assetId="assetId" />
      </div>
    </div>

    <!-- Row 5: Tax Analysis (Full Width) -->
    <div class="row g-3 mb-3">
      <div class="col-12">
        <TaxAnalysis
          :tax-authorities="taxAuthorities"
          :authority-total="taxAuthorityTotal"
          :special-assessments="specialAssessments"
          :assessment-total="specialAssessmentTotal"
          :totals="taxTotals"
          :parcel="taxParcelDetails"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { withDefaults, defineProps, computed } from 'vue'
// Import components (now using shared components from general folder for reusability across modules)
import PropertyMap from '@/components/PropertyMap.vue'
import PropertyDetails from '@/components/property_tabs_components/propertydetails.vue'
import DemographicsGrid from '@/components/property_tabs_components/DemographicsGrid.vue'
import TaxAnalysis from '@/components/property_tabs_components/TaxAnalysis.vue'
import ConditionAssessment from '@/components/property_tabs_components/ConditionAssessment.vue'
import ComparableSales from '@/components/property_tabs_components/ComparableSales.vue'
import NeighborhoodInsights from '@/components/property_tabs_components/NeighborhoodInsights.vue'
import RiskAssessment from '@/components/property_tabs_components/RiskAssessment.vue'

// Keep props consistent with other tabs so parent can pass row/assetId
const props = withDefaults(defineProps<{
  row?: Record<string, any> | null
  assetId?: string | number | null
}>(), {
  row: null,
  assetId: null,
})

// Extract tax analysis payload from row while guarding against undefined structures
const taxAnalysisSource = computed(() => (props.row as any)?.tax_analysis ?? null)

// Derive taxing authority rows for the line-item table
const taxAuthorities = computed(() => taxAnalysisSource.value?.authorities ?? [])

// Aggregate total for ad valorem taxes
const taxAuthorityTotal = computed(() => taxAnalysisSource.value?.authority_total ?? null)

// Provide direct charges and special assessment entries
const specialAssessments = computed(() => taxAnalysisSource.value?.special_assessments ?? [])

// Summarize special assessment total amount
const specialAssessmentTotal = computed(() => taxAnalysisSource.value?.assessment_total ?? null)

// Package summary totals (total tax, payments, balance)
const taxTotals = computed(() => taxAnalysisSource.value?.totals ?? null)

// Surface parcel level metadata for three-column detail grid
const taxParcelDetails = computed(() => taxAnalysisSource.value?.parcel ?? null)
</script>