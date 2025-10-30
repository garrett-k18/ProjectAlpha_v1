<template>
  <div class="acquisition-analysis-tab">
    <!-- Asset Snapshot spanning full width -->
    <AssetSnapshot :row="row" />

    <!-- Smart Recommendations Banner -->
    <div v-if="recommendations && recommendations.models" class="card mb-3 border-primary">
      <div class="card-body p-3">
        <div class="d-flex align-items-center justify-content-between mb-2">
          <h5 class="mb-0 fw-semibold text-primary">
            <i class="mdi mdi-brain me-2"></i>
            Smart Recommendations
          </h5>
          <button 
            v-if="!loadingRecommendations"
            type="button" 
            class="btn btn-sm btn-outline-primary"
            @click="fetchRecommendations"
          >
            <i class="mdi mdi-refresh me-1"></i>
            Refresh
          </button>
        </div>
        
        <!-- Loading state -->
        <div v-if="loadingRecommendations" class="text-center py-3">
          <div class="spinner-border spinner-border-sm text-primary me-2" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <span class="text-muted">Analyzing asset characteristics...</span>
        </div>

        <!-- Asset Metrics Display -->
        <div v-else-if="recommendations.metrics" class="mb-3">
          <small class="text-muted d-block mb-2">Asset Analysis:</small>
          <div class="d-flex flex-wrap gap-2">
            <span v-if="recommendations.metrics.ltv !== null" class="badge bg-light text-dark border">
              LTV: <strong>{{ recommendations.metrics.ltv.toFixed(1) }}%</strong>
            </span>
            <span v-if="recommendations.metrics.tdtv !== null" class="badge bg-light text-dark border">
              TDTV: <strong>{{ recommendations.metrics.tdtv.toFixed(1) }}%</strong>
            </span>
            <span v-if="recommendations.metrics.is_delinquent" class="badge bg-warning">
              {{ recommendations.metrics.delinquency_months }} Months DLQ
            </span>
            <span v-if="recommendations.metrics.is_foreclosure" class="badge bg-danger">
              <i class="mdi mdi-gavel me-1"></i>Foreclosure Active
            </span>
            <span v-if="recommendations.metrics.has_equity" class="badge bg-success">
              <i class="mdi mdi-check me-1"></i>Has Equity
            </span>
            <span v-else class="badge bg-danger">
              <i class="mdi mdi-alert me-1"></i>Underwater
            </span>
          </div>
        </div>

        <!-- Recommended Models -->
        <div v-if="recommendedModelsFromAPI.length > 0" class="alert alert-info py-2 px-3 mb-0 small">
          <i class="mdi mdi-lightbulb-on me-1"></i>
          <strong>Recommended models based on asset profile:</strong>
          {{ recommendedModelsFromAPI.map(m => m.model_name).join(', ') }}
        </div>
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
          <div class="d-flex gap-2">
            <button 
              v-if="hasRecommendations"
              type="button" 
              class="btn btn-sm btn-outline-success"
              @click="applyRecommendedModels"
            >
              <i class="mdi mdi-auto-fix me-1"></i>
              Apply Recommendations
            </button>
            <button 
              type="button" 
              class="btn btn-sm btn-outline-secondary"
              @click="clearAllModels"
            >
              <i class="mdi mdi-close me-1"></i>
              Clear All
            </button>
          </div>
        </div>
        
        <!-- Model Toggle Pills -->
        <div class="d-flex flex-wrap gap-2 mb-3">
          <button
            v-for="model in availableModels"
            :key="model.key"
            type="button"
            class="btn btn-sm d-inline-flex align-items-center gap-2 px-3 py-2 position-relative"
            :class="selectedModels.has(model.key) ? model.activeClass : 'btn-outline-secondary'"
            @click="toggleModel(model.key)"
          >
            <i :class="model.icon"></i>
            <span>{{ model.label }}</span>
            <i v-if="selectedModels.has(model.key)" class="mdi mdi-check-circle ms-1"></i>
            <!-- Recommended badge -->
            <span 
              v-if="isModelRecommended(model.key)" 
              class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-success"
              style="font-size: 0.6rem; padding: 0.15rem 0.4rem;"
              title="Recommended by system"
            >
              <i class="mdi mdi-star"></i>
            </span>
          </button>
        </div>

        <!-- Model Reasons (Expandable) -->
        <div v-if="hasRecommendations && selectedModels.size > 0" class="border rounded p-2 mb-3 bg-light">
          <button 
            class="btn btn-link btn-sm p-0 text-decoration-none w-100 text-start"
            type="button"
            @click="showModelReasons = !showModelReasons"
          >
            <i :class="showModelReasons ? 'mdi mdi-chevron-up' : 'mdi mdi-chevron-down'" class="me-1"></i>
            <strong>Why these models?</strong>
            <small class="text-muted ms-2">(Click to {{ showModelReasons ? 'hide' : 'show' }})</small>
          </button>
          
          <div v-show="showModelReasons" class="mt-2">
            <div 
              v-for="model in availableModels" 
              :key="model.key" 
              v-show="selectedModels.has(model.key)"
              class="mb-2"
            >
              <div class="d-flex align-items-start gap-2">
                <i :class="model.icon" class="mt-1"></i>
                <div class="flex-grow-1">
                  <strong class="d-block">{{ model.label }}</strong>
                  <ul v-if="getModelReasons(model.key).length > 0" class="mb-0 small text-muted ps-3">
                    <li v-for="(reason, idx) in getModelReasons(model.key)" :key="idx">
                      {{ reason }}
                    </li>
                  </ul>
                  <small v-else class="text-muted">No specific reasons available</small>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Outcome Probabilities (only show for selected models) -->
        <div v-if="selectedModels.size > 0" class="border-top pt-3">
          <div class="d-flex align-items-center justify-content-between mb-2">
            <h6 class="mb-0 fw-semibold text-body">
              <i class="mdi mdi-percent me-1 text-secondary"></i>
              Outcome Probabilities
            </h6>
            <div class="d-flex align-items-center gap-2">
              <small class="text-muted">Total: <strong :class="totalProbabilityClass">{{ totalProbability }}%</strong></small>
              <button 
                v-if="hasRecommendations"
                type="button" 
                class="btn btn-xs btn-outline-primary"
                @click="applyRecommendedProbabilities"
                title="Apply AI-suggested probabilities"
              >
                <i class="mdi mdi-auto-fix me-1"></i>Auto-fill
              </button>
            </div>
          </div>
          <div class="row g-2">
            <div v-for="model in availableModels" :key="model.key" v-show="selectedModels.has(model.key)" class="col-md-6 col-lg-3">
              <label class="form-label small mb-1 d-flex align-items-center gap-1">
                <i :class="model.icon" class="small"></i>
                {{ model.label }}
                <span v-if="getRecommendedProbability(model.key) > 0" class="text-muted small">
                  (Suggested: {{ getRecommendedProbability(model.key) }}%)
                </span>
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
          <div v-else class="alert alert-success py-2 px-3 mt-2 mb-0 small">
            <i class="mdi mdi-check-circle me-1"></i>
            Probabilities are properly balanced at 100%
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
              <span class="badge bg-danger ms-2">{{ modelProbabilities.fc_sale }}% Probability</span>
            </h5>
          </div>
          <div class="card-body">
            <p class="text-muted">FC Sale model detailed inputs will go here (timeline, costs, recovery expectations)</p>
            <!-- TODO: Add detailed assumption inputs -->
          </div>
        </div>
      </div>

      <div v-if="selectedModels.has('reo_sale')" class="col-12">
        <div class="card border-info">
          <div class="card-header bg-info-subtle">
            <h5 class="mb-0 d-flex align-items-center">
              <i class="fas fa-house-chimney me-2 text-info"></i>
              REO Sale Model
              <span class="badge bg-info ms-2">{{ modelProbabilities.reo_sale }}% Probability</span>
            </h5>
          </div>
          <div class="card-body">
            <p class="text-muted">REO Sale model detailed inputs will go here (rehab costs, holding period, resale value)</p>
            <!-- TODO: Add detailed assumption inputs -->
          </div>
        </div>
      </div>

      <div v-if="selectedModels.has('short_sale')" class="col-12">
        <div class="card border-warning">
          <div class="card-header bg-warning-subtle">
            <h5 class="mb-0 d-flex align-items-center">
              <i class="fas fa-tags me-2 text-warning"></i>
              Short Sale Model
              <span class="badge bg-warning ms-2">{{ modelProbabilities.short_sale }}% Probability</span>
            </h5>
          </div>
          <div class="card-body">
            <p class="text-muted">Short Sale model detailed inputs will go here (timeline, discount expectations)</p>
            <!-- TODO: Add detailed assumption inputs -->
          </div>
        </div>
      </div>

      <div v-if="selectedModels.has('modification')" class="col-12">
        <div class="card border-success">
          <div class="card-header bg-success-subtle">
            <h5 class="mb-0 d-flex align-items-center">
              <i class="fas fa-pen-alt me-2 text-success"></i>
              Modification Model
              <span class="badge bg-success ms-2">{{ modelProbabilities.modification }}% Probability</span>
            </h5>
          </div>
          <div class="card-body">
            <p class="text-muted">Modification model detailed inputs will go here (rate, term, LTV limits)</p>
            <!-- TODO: Add detailed assumption inputs -->
          </div>
        </div>
      </div>

      <div v-if="selectedModels.has('note_sale')" class="col-12">
        <div class="card border-primary">
          <div class="card-header bg-primary-subtle">
            <h5 class="mb-0 d-flex align-items-center">
              <i class="fas fa-file-contract me-2 text-primary"></i>
              Note Sale Model
              <span class="badge bg-primary ms-2">{{ modelProbabilities.note_sale }}% Probability</span>
            </h5>
          </div>
          <div class="card-body">
            <p class="text-muted">Note Sale model detailed inputs will go here (discount factors, buyer profiles)</p>
            <!-- TODO: Add detailed assumption inputs -->
          </div>
        </div>
      </div>
    </div>
  </div>
  
</template>

<script setup lang="ts">
import { withDefaults, defineProps, ref, computed, onMounted, watch } from 'vue'
import AssetSnapshot from '@/views/acq_module/loanlvl/components/model/assetSnapshot.vue'
import http from '@/lib/http'

const props = withDefaults(defineProps<{
  row?: Record<string, any> | null
  assetId?: string | number | null
  module?: 'acq' | 'am'
}>(), {
  row: null,
  assetId: null,
  module: 'acq'
})

console.log('[AcquisitionAnalysisTab] MOUNTED with props assetId=', props.assetId, 'row=', props.row)

// WHAT: Model outcome selector state
// WHY: Allow users to toggle which acquisition models to display
type ModelKey = 'fc_sale' | 'reo_sale' | 'short_sale' | 'modification' | 'note_sale'

const availableModels = [
  { key: 'fc_sale' as ModelKey, label: 'FC Sale', icon: 'fas fa-gavel', activeClass: 'btn-danger' },
  { key: 'reo_sale' as ModelKey, label: 'REO Sale', icon: 'fas fa-house-chimney', activeClass: 'btn-info' },
  { key: 'short_sale' as ModelKey, label: 'Short Sale', icon: 'fas fa-tags', activeClass: 'btn-warning' },
  { key: 'modification' as ModelKey, label: 'Modification', icon: 'fas fa-pen-alt', activeClass: 'btn-success' },
  { key: 'note_sale' as ModelKey, label: 'Note Sale', icon: 'fas fa-file-contract', activeClass: 'btn-primary' },
]

// Backend recommendations state
const recommendations = ref<any>(null)
const loadingRecommendations = ref(false)
const showModelReasons = ref(false)

// User selections
const selectedModels = ref<Set<ModelKey>>(new Set())

// WHAT: Outcome probability percentages for each model
// WHY: Allow users to assign probability weights to different exit strategies
const modelProbabilities = ref<Record<ModelKey, number>>({
  fc_sale: 0,
  reo_sale: 0,
  short_sale: 0,
  modification: 0,
  note_sale: 0,
})

// WHAT: Fetch recommendations from backend API
async function fetchRecommendations() {
  if (!props.assetId) {
    console.warn('[AcquisitionAnalysisTab] No assetId provided, cannot fetch recommendations')
    return
  }

  loadingRecommendations.value = true
  try {
    const response = await http.get(`/${props.module}/assets/${props.assetId}/model-recommendations/`)
    recommendations.value = response.data
    console.log('[AcquisitionAnalysisTab] Received recommendations:', recommendations.value)
  } catch (error) {
    console.error('[AcquisitionAnalysisTab] Failed to fetch recommendations:', error)
    recommendations.value = null
  } finally {
    loadingRecommendations.value = false
  }
}

// Fetch recommendations on mount and when assetId changes
onMounted(() => {
  if (props.assetId) {
    fetchRecommendations()
  }
})

watch(() => props.assetId, (newId) => {
  if (newId) {
    fetchRecommendations()
  }
})

// Helper computed properties
const hasRecommendations = computed(() => {
  return recommendations.value && recommendations.value.models && recommendations.value.models.length > 0
})

const recommendedModelsFromAPI = computed(() => {
  if (!hasRecommendations.value) return []
  return recommendations.value.models.filter((m: any) => m.is_recommended)
})

function isModelRecommended(key: ModelKey): boolean {
  if (!hasRecommendations.value) return false
  const model = recommendations.value.models.find((m: any) => m.model_key === key)
  return model?.is_recommended || false
}

function getModelReasons(key: ModelKey): string[] {
  if (!hasRecommendations.value) return []
  const model = recommendations.value.models.find((m: any) => m.model_key === key)
  return model?.reasons || []
}

function getRecommendedProbability(key: ModelKey): number {
  if (!hasRecommendations.value) return 0
  const model = recommendations.value.models.find((m: any) => m.model_key === key)
  return model?.probability || 0
}

// WHAT: Apply recommended models from backend
function applyRecommendedModels() {
  if (!hasRecommendations.value) return
  
  selectedModels.value.clear()
  recommendedModelsFromAPI.value.forEach((model: any) => {
    selectedModels.value.add(model.model_key as ModelKey)
  })
  
  // Force reactivity update
  selectedModels.value = new Set(selectedModels.value)
}

// WHAT: Apply recommended probabilities from backend
function applyRecommendedProbabilities() {
  if (!hasRecommendations.value) return
  
  recommendations.value.models.forEach((model: any) => {
    if (selectedModels.value.has(model.model_key as ModelKey)) {
      modelProbabilities.value[model.model_key as ModelKey] = model.probability
    } else {
      modelProbabilities.value[model.model_key as ModelKey] = 0
    }
  })
}

// WHAT: Clear all selected models
function clearAllModels() {
  selectedModels.value.clear()
  selectedModels.value = new Set()
  
  // Reset all probabilities
  Object.keys(modelProbabilities.value).forEach(key => {
    modelProbabilities.value[key as ModelKey] = 0
  })
}

// WHAT: Computed total probability across selected models only
// WHY: Validate that probabilities sum to 100% for active models
const totalProbability = computed(() => {
  let total = 0
  for (const key of selectedModels.value) {
    total += modelProbabilities.value[key] || 0
  }
  return total
})

const totalProbabilityClass = computed(() => {
  const total = totalProbability.value
  if (total === 100) return 'text-success'
  if (total > 100) return 'text-danger'
  return 'text-warning'
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
</script>

<style scoped>
/* Button size adjustments */
.btn-xs {
  padding: 0.15rem 0.4rem;
  font-size: 0.75rem;
  line-height: 1.2;
}

/* Smooth transitions for expandable sections */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
