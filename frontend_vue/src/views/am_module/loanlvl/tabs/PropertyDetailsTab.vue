<template>
  <!-- AM Property Details Tab - comprehensive property information display -->
  <div class="p-3">
    <!-- Row 1: Core Property Information -->
    <div class="row g-3 mb-3">
      <div class="col-12 col-lg-6 col-xl-4 d-flex">
        <PropertyDetails class="w-100 h-100" :row="row" :assetId="assetHubId" />
      </div>

      <div class="col-12 col-lg-6 col-xl-4 d-flex">
        <DemographicsGrid class="w-100 h-100" :row="row" :assetId="assetHubId" />
      </div>

      <div class="col-12 col-lg-6 col-xl-4 d-flex">
        <ConditionAssessment class="w-100 h-100" :row="row" :assetId="assetHubId" />
      </div>
    </div>

    <!-- Row 2: Comparable Sales -->
    <div class="row g-3 mb-2">
      <div class="col-12">
        <ComparableSales :row="row" :assetId="assetHubId" />
      </div>
    </div>

    <!-- Row 3: Neighborhood Insights & Risk Factors -->
    <div class="row g-3 mb-1">
      <div class="col-12 col-lg-6">
        <NeighborhoodInsights :row="row" :assetId="assetHubId" />
      </div>

      <div class="col-12 col-lg-6">
        <RiskAssessment :row="row" :assetId="assetHubId" />
      </div>
    </div>

    <!-- Row 4: Tax Analysis (Full Width) -->
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
/**
 * AM Module Property Details Tab
 * 
 * Purpose: Displays comprehensive property information for asset management.
 * Design: Reuses shared property tab components for consistency across modules.
 * 
 * Components:
 *   - PropertyDetails: Core property info (address, type, bed/bath, sqft)
 *   - DemographicsGrid: Neighborhood demographic data
 *   - ConditionAssessment: Property condition and maintenance status
 *   - ComparableSales: Comparable property sales data
 *   - NeighborhoodInsights: Area insights and market trends
 *   - RiskAssessment: Property and investment risk factors
 *   - TaxAnalysis: Tax assessment and payment details
 */

import { withDefaults, defineProps, computed } from 'vue'

// Import shared property tab components (now in general components folder for cross-module reusability)
import PropertyDetails from '@/components/property_tabs_components/propertydetails.vue'
import DemographicsGrid from '@/components/property_tabs_components/DemographicsGrid.vue'
import TaxAnalysis from '@/components/property_tabs_components/TaxAnalysis.vue'
import ConditionAssessment from '@/components/property_tabs_components/ConditionAssessment.vue'
import ComparableSales from '@/components/property_tabs_components/ComparableSales.vue'
import NeighborhoodInsights from '@/components/property_tabs_components/NeighborhoodInsights.vue'
import RiskAssessment from '@/components/property_tabs_components/RiskAssessment.vue'

/**
 * WHAT: Component props for asset context.
 * WHY: Provides row data and asset hub ID to child components.
 * HOW: Props forwarded from parent LoanTabs component.
 */
const props = withDefaults(defineProps<{
  row?: Record<string, any> | null
  assetHubId?: string | number | null
}>(), {
  row: null,
  assetHubId: null,
})

/**
 * WHAT: Extract tax analysis payload from row data.
 * WHY: TaxAnalysis component requires structured tax data.
 * HOW: Safely extracts tax_analysis object with null fallback.
 */
const taxAnalysisSource = computed(() => (props.row as any)?.tax_analysis ?? null)

/**
 * WHAT: Derive taxing authority rows for the line-item table.
 * WHY: Shows breakdown of taxes by authority (county, city, school district, etc.).
 * HOW: Extracts authorities array from tax analysis payload.
 */
const taxAuthorities = computed(() => taxAnalysisSource.value?.authorities ?? [])

/**
 * WHAT: Aggregate total for ad valorem taxes.
 * WHY: Shows total amount owed to taxing authorities.
 * HOW: Extracts authority_total from tax analysis.
 */
const taxAuthorityTotal = computed(() => taxAnalysisSource.value?.authority_total ?? null)

/**
 * WHAT: Provide direct charges and special assessment entries.
 * WHY: Shows non-standard tax charges (HOA, special districts, etc.).
 * HOW: Extracts special_assessments array from tax analysis.
 */
const specialAssessments = computed(() => taxAnalysisSource.value?.special_assessments ?? [])

/**
 * WHAT: Summarize special assessment total amount.
 * WHY: Shows total of all special assessments.
 * HOW: Extracts assessment_total from tax analysis.
 */
const specialAssessmentTotal = computed(() => taxAnalysisSource.value?.assessment_total ?? null)

/**
 * WHAT: Package summary totals (total tax, payments, balance).
 * WHY: Shows overall tax obligation and payment status.
 * HOW: Extracts totals object from tax analysis.
 */
const taxTotals = computed(() => taxAnalysisSource.value?.totals ?? null)

/**
 * WHAT: Surface parcel level metadata for three-column detail grid.
 * WHY: Shows parcel-specific information (parcel ID, assessment values, etc.).
 * HOW: Extracts parcel object from tax analysis.
 */
const taxParcelDetails = computed(() => taxAnalysisSource.value?.parcel ?? null)
</script>
