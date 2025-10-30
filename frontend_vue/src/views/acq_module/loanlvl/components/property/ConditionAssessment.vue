<template>
  <!--
    ConditionAssessment.vue
    - Displays property condition scores across 6 categories with letter grades
    - Each category shows a grade (A+ through F) with color-coded badge
    - Shows last inspection date
    - Uses Bootstrap/Hyper UI card pattern
  -->
  <div class="card">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title mb-0">Condition Assessment</h4>
      <span class="badge bg-success">Good</span>
    </div>
    <div class="card-body">
      <div class="row g-3">
        <!-- Condition categories with grade badges in 2-column layout -->
        <div class="col-12 col-md-6" v-for="(item, idx) in conditionMetrics" :key="idx">
          <div class="border rounded p-3 h-100">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <span class="fw-semibold">{{ item.category }}</span>
              <span class="badge" :class="item.badgeClass">{{ item.grade }}</span>
            </div>
            <p class="text-muted small mb-0">{{ item.summary }}</p>
          </div>
        </div>
      </div>
      <div class="alert alert-info mt-3 mb-0 py-2">
        <i class="mdi mdi-information-outline me-1"></i>
        <small>
          Overall Grade: <span class="fw-semibold">{{ overallGrade }}</span>
          &nbsp;•&nbsp; Last inspection: {{ lastInspectionDate }}
        </small>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * ConditionAssessment.vue
 * 
 * Property condition assessment card showing scores for 6 major systems.
 * Each category is mapped to a letter grade with contextual summary text.
 * TODO: Wire to backend inspection data when available.
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

// Condition Assessment Metrics - Property condition scores by category
const gradeConfig = {
  'A+': { badgeClass: 'bg-success', summary: 'Outstanding condition; recently updated with no visible deficiencies.' },
  'A': { badgeClass: 'bg-success', summary: 'Excellent condition with minor cosmetic wear consistent with age.' },
  'B': { badgeClass: 'bg-info', summary: 'Good condition; moderate wear but no critical repairs required.' },
  'C': { badgeClass: 'bg-warning', summary: 'Fair condition; monitor aging systems and plan targeted maintenance.' },
  'D': { badgeClass: 'bg-danger', summary: 'Poor condition; multiple systems approaching failure, schedule repairs.' },
  'F': { badgeClass: 'bg-dark', summary: 'Critical condition; immediate remediation required.' },
}

const conditionMetrics = computed(() => [
  { category: 'Exterior', grade: 'A', ...gradeConfig['A'] },
  { category: 'Interior', grade: 'B', ...gradeConfig['B'] },
  { category: 'Roof', grade: 'A+', ...gradeConfig['A+'] },
  { category: 'HVAC', grade: 'C', ...gradeConfig['C'] },
  { category: 'Plumbing', grade: 'B', ...gradeConfig['B'] },
  { category: 'Electrical', grade: 'B', ...gradeConfig['B'] },
])

const overallGrade = computed(() => 'B+')

const lastInspectionDate = computed(() => '06/10/2023')
</script>
