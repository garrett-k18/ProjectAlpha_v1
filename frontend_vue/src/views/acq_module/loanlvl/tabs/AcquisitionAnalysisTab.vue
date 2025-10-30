<template>
  <div class="acquisition-analysis-tab">
    <!-- Asset Snapshot spanning full width -->
    <AssetSnapshot :row="row" />

    <div class="row g-3 mb-3">
      <!-- Left Column: Assumptions Summary -->
      <div class="col-lg-6">
        <AssumptionsSummary
          :fcTimeline="fcTimeline"
          :commercialUnits="commercialUnits"
        />
      </div>

      <!-- Right Column: Investment Metrics -->
      <div class="col-lg-6">
        <InvestmentMetrics :row="row" :assetId="assetId" />
      </div>
    </div>

    <!-- Model Outcome Selector -->
    <div class="card mb-3">
      <div class="card-body p-3">
        <div class="d-flex align-items-center justify-content-between mb-3">
          <h5 class="mb-0 fw-semibold text-body">
            <i class="mdi mdi-calculator-variant me-2 text-primary"></i>
            Model Outcomes
          </h5>
          <small class="text-muted">Select models to analyze</small>
        </div>
        
        <!-- Model Toggle Pills -->
        <div class="d-flex flex-wrap gap-2 mb-3">
          <button
            v-for="model in availableModels"
            :key="model.key"
            type="button"
            class="btn btn-sm d-inline-flex align-items-center gap-2 px-3 py-2"
            :class="selectedModels.has(model.key) ? model.activeClass : 'btn-outline-secondary'"
            @click="toggleModel(model.key)"
          >
            <i :class="model.icon"></i>
            <span>{{ model.label }}</span>
            <i v-if="selectedModels.has(model.key)" class="mdi mdi-check-circle ms-1"></i>
          </button>
        </div>

        <!-- Outcome Probabilities (only show for selected models) -->
        <div v-if="selectedModels.size > 0" class="border-top pt-3">
          <div class="d-flex align-items-center justify-content-between mb-2">
            <h6 class="mb-0 fw-semibold text-body">
              <i class="mdi mdi-percent me-1 text-secondary"></i>
              Outcome Probabilities
            </h6>
            <small class="text-muted">Total: {{ totalProbability }}%</small>
          </div>
          <div class="row g-2">
            <div v-for="model in availableModels" :key="model.key" v-show="selectedModels.has(model.key)" class="col-md-6 col-lg-3">
              <label class="form-label small mb-1 d-flex align-items-center gap-1">
                <i :class="model.icon" class="small"></i>
                {{ model.label }}
              </label>
              <div class="input-group input-group-sm">
                <input
                  type="number"
                  class="form-control"
                  v-model.number="modelProbabilities[model.key]"
                  @input="validateProbabilities"
                  min="0"
                  max="100"
                  step="1"
                  placeholder="0"
                />
                <span class="input-group-text">%</span>
              </div>
            </div>
          </div>
          <div v-if="totalProbability !== 100" class="alert alert-warning py-2 px-3 mt-2 mb-0 small">
            <i class="mdi mdi-alert me-1"></i>
            Probabilities should total 100%. Current total: <strong>{{ totalProbability }}%</strong>
          </div>
        </div>
      </div>
    </div>

    <!-- Model Cards (conditionally rendered based on selection) -->
    <div class="row g-3">
      <div v-if="selectedModels.has('fc_sale')" class="col-12">
        <div class="card border-danger">
          <div class="card-header bg-danger-subtle">
            <h5 class="mb-0 d-flex align-items-center">
              <i class="fas fa-gavel me-2 text-danger"></i>
              Foreclosure Sale Model
            </h5>
          </div>
          <div class="card-body">
            <p class="text-muted">FC Sale model card content goes here</p>
          </div>
        </div>
      </div>

      <div v-if="selectedModels.has('reo_sale')" class="col-12">
        <div class="card border-info">
          <div class="card-header bg-info-subtle">
            <h5 class="mb-0 d-flex align-items-center">
              <i class="fas fa-house-chimney me-2 text-info"></i>
              REO Sale Model
            </h5>
          </div>
          <div class="card-body">
            <p class="text-muted">REO Sale model card content goes here</p>
          </div>
        </div>
      </div>

      <div v-if="selectedModels.has('short_sale')" class="col-12">
        <div class="card border-warning">
          <div class="card-header bg-warning-subtle">
            <h5 class="mb-0 d-flex align-items-center">
              <i class="fas fa-tags me-2 text-warning"></i>
              Short Sale Model
            </h5>
          </div>
          <div class="card-body">
            <p class="text-muted">Short Sale model card content goes here</p>
          </div>
        </div>
      </div>

      <div v-if="selectedModels.has('modification')" class="col-12">
        <div class="card border-success">
          <div class="card-header bg-success-subtle">
            <h5 class="mb-0 d-flex align-items-center">
              <i class="fas fa-pen-alt me-2 text-success"></i>
              Modification Model
            </h5>
          </div>
          <div class="card-body">
            <p class="text-muted">Modification model card content goes here</p>
          </div>
        </div>
      </div>
    </div>
  </div>
  
</template>

<script setup lang="ts">
import { withDefaults, defineProps, ref, computed, onMounted } from 'vue'
import AssumptionsSummary from '@/views/acq_module/loanlvl/components/model/assumptionsSummary.vue'
import AssetSnapshot from '@/views/acq_module/loanlvl/components/model/assetSnapshot.vue'
import InvestmentMetrics from '@/views/acq_module/loanlvl/components/InvestmentMetrics.vue'

const props = withDefaults(defineProps<{
  row?: Record<string, any> | null
  assetId?: string | number | null
}>(), {
  row: null,
  assetId: null,
})

console.log('[AcquisitionAnalysisTab] MOUNTED with props assetId=', props.assetId, 'row=', props.row)

// WHAT: Model outcome selector state
// WHY: Allow users to toggle which acquisition models to display
type ModelKey = 'fc_sale' | 'reo_sale' | 'short_sale' | 'modification'

const availableModels = [
  { key: 'fc_sale' as ModelKey, label: 'FC Sale', icon: 'fas fa-gavel', activeClass: 'btn-danger' },
  { key: 'reo_sale' as ModelKey, label: 'REO Sale', icon: 'fas fa-house-chimney', activeClass: 'btn-info' },
  { key: 'short_sale' as ModelKey, label: 'Short Sale', icon: 'fas fa-tags', activeClass: 'btn-warning' },
  { key: 'modification' as ModelKey, label: 'Modification', icon: 'fas fa-pen-alt', activeClass: 'btn-success' },
]

const selectedModels = ref<Set<ModelKey>>(new Set(['fc_sale', 'reo_sale']))

// WHAT: Outcome probability percentages for each model
// WHY: Allow users to assign probability weights to different exit strategies
const modelProbabilities = ref<Record<ModelKey, number>>({
  fc_sale: 40,
  reo_sale: 30,
  short_sale: 20,
  modification: 10,
})

// WHAT: Computed total probability across selected models only
// WHY: Validate that probabilities sum to 100% for active models
const totalProbability = computed(() => {
  let total = 0
  for (const key of selectedModels.value) {
    total += modelProbabilities.value[key] || 0
  }
  return total
})

function toggleModel(key: ModelKey) {
  if (selectedModels.value.has(key)) {
    selectedModels.value.delete(key)
  } else {
    selectedModels.value.add(key)
  }
  // Force reactivity update
  selectedModels.value = new Set(selectedModels.value)
}

// WHAT: Validate probability inputs
// WHY: Ensure values stay within 0-100 range
function validateProbabilities() {
  for (const key in modelProbabilities.value) {
    const val = modelProbabilities.value[key as ModelKey]
    if (val < 0) modelProbabilities.value[key as ModelKey] = 0
    if (val > 100) modelProbabilities.value[key as ModelKey] = 100
  }
}

// State for summary props
const fcTimeline = ref<any | null>(null)
const commercialUnits = ref<any[]>([])

// Fetch data from existing DRF endpoints
async function loadSummaryData() {
  try {
    // Commercial units
    const cuRes = await fetch('/api/core/commercial-units/', { credentials: 'include' })
    commercialUnits.value = await cuRes.json()

    // Asset-scoped FC timeline
    const id = props.assetId != null ? String(props.assetId) : ''
    console.log('[AcquisitionAnalysisTab] assetId=', props.assetId, 'using id=', id)
    if (id) {
      const fcRes = await fetch(`/api/acq/assets/${id}/fc-timeline/`, { credentials: 'include' })
      console.log('[AcquisitionAnalysisTab] FC timeline fetch status=', fcRes.status, 'ok=', fcRes.ok)
      if (fcRes.ok) fcTimeline.value = await fcRes.json()
      else fcTimeline.value = null
      console.log('[AcquisitionAnalysisTab] fcTimeline=', fcTimeline.value)
    } else {
      fcTimeline.value = null
      console.log('[AcquisitionAnalysisTab] No id provided, fcTimeline set to null')
    }
  } catch (e) {
    console.warn('Failed to load acquisition assumptions summary', e)
  }
}

onMounted(loadSummaryData)
</script>
