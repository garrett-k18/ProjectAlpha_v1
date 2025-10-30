<template>
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

    <div v-if="selectedModels.has('mod_reperform')" class="col-12">
      <div class="card border-success">
        <div class="card-header bg-success-subtle">
          <h5 class="mb-0 d-flex align-items-center">
            <i class="fas fa-handshake me-2 text-success"></i>
            Modification & Re-Performance Model
            <span class="badge bg-success ms-2">{{ modelProbabilities.mod_reperform }}% Probability</span>
          </h5>
        </div>
        <div class="card-body">
          <p class="text-muted">Modification model detailed inputs will go here (payment reduction, term extension, interest rate adjustment)</p>
          <!-- TODO: Add detailed assumption inputs -->
        </div>
      </div>
    </div>

    <div v-if="selectedModels.has('short_sale')" class="col-12">
      <div class="card border-warning">
        <div class="card-header bg-warning-subtle">
          <h5 class="mb-0 d-flex align-items-center">
            <i class="fas fa-percent me-2 text-warning"></i>
            Short Sale Model
            <span class="badge bg-warning ms-2">{{ modelProbabilities.short_sale }}% Probability</span>
          </h5>
        </div>
        <div class="card-body">
          <p class="text-muted">Short Sale model detailed inputs will go here (discount expectations, timeline, approval process)</p>
          <!-- TODO: Add detailed assumption inputs -->
        </div>
      </div>
    </div>

    <div v-if="selectedModels.has('deed_in_lieu')" class="col-12">
      <div class="card border-secondary">
        <div class="card-header bg-secondary-subtle">
          <h5 class="mb-0 d-flex align-items-center">
            <i class="fas fa-file-contract me-2 text-secondary"></i>
            Deed in Lieu Model
            <span class="badge bg-secondary ms-2">{{ modelProbabilities.deed_in_lieu }}% Probability</span>
          </h5>
        </div>
        <div class="card-body">
          <p class="text-muted">Deed in Lieu model detailed inputs will go here (property condition, borrower cooperation, legal costs)</p>
          <!-- TODO: Add detailed assumption inputs -->
        </div>
      </div>
    </div>

    <div v-if="selectedModels.has('charge_off')" class="col-12">
      <div class="card border-dark">
        <div class="card-header bg-dark-subtle">
          <h5 class="mb-0 d-flex align-items-center">
            <i class="fas fa-times-circle me-2 text-dark"></i>
            Charge Off Model
            <span class="badge bg-dark ms-2">{{ modelProbabilities.charge_off }}% Probability</span>
          </h5>
        </div>
        <div class="card-body">
          <p class="text-muted">Charge Off model detailed inputs will go here (recovery expectations, tax implications, accounting treatment)</p>
          <!-- TODO: Add detailed assumption inputs -->
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'

// WHAT: Props for the ModelOutcomes component
const props = defineProps<{
  recommendations?: any | null
  loadingRecommendations?: boolean
}>()

// WHAT: Emits for parent component communication
const emit = defineEmits<{
  modelsChanged: [selectedModels: Set<string>, probabilities: Record<string, number>]
}>()

// WHAT: Available disposition models with their configuration
const availableModels = [
  {
    key: 'fc_sale',
    label: 'FC Sale',
    icon: 'fas fa-gavel',
    activeClass: 'btn-danger'
  },
  {
    key: 'reo_sale', 
    label: 'REO Sale',
    icon: 'fas fa-house-chimney',
    activeClass: 'btn-info'
  },
  {
    key: 'mod_reperform',
    label: 'Mod & Re-Perform',
    icon: 'fas fa-handshake',
    activeClass: 'btn-success'
  },
  {
    key: 'short_sale',
    label: 'Short Sale',
    icon: 'fas fa-percent',
    activeClass: 'btn-warning'
  },
  {
    key: 'deed_in_lieu',
    label: 'Deed in Lieu',
    icon: 'fas fa-file-contract',
    activeClass: 'btn-secondary'
  },
  {
    key: 'charge_off',
    label: 'Charge Off',
    icon: 'fas fa-times-circle',
    activeClass: 'btn-dark'
  }
]

// WHAT: Reactive state for selected models and their probabilities
const selectedModels = ref(new Set<string>())
const modelProbabilities = reactive<Record<string, number>>({
  fc_sale: 0,
  reo_sale: 0,
  mod_reperform: 0,
  short_sale: 0,
  deed_in_lieu: 0,
  charge_off: 0
})

// WHAT: Computed property to check if we have recommendations from backend
const hasRecommendations = computed(() => {
  return props.recommendations && 
         props.recommendations.recommendations && 
         props.recommendations.recommendations.length > 0
})

// WHAT: Computed property to calculate total probability percentage
const totalProbability = computed(() => {
  return Object.values(modelProbabilities).reduce((sum, prob) => sum + (prob || 0), 0)
})

// WHAT: Computed property for total probability styling
const totalProbabilityClass = computed(() => {
  const total = totalProbability.value
  if (total === 100) return 'text-success'
  if (total > 100) return 'text-danger'
  return 'text-warning'
})

// WHAT: Toggle model selection on/off
function toggleModel(modelKey: string) {
  if (selectedModels.value.has(modelKey)) {
    selectedModels.value.delete(modelKey)
    modelProbabilities[modelKey] = 0
  } else {
    selectedModels.value.add(modelKey)
  }
  
  // Emit changes to parent
  emit('modelsChanged', selectedModels.value, modelProbabilities)
}

// WHAT: Clear all selected models and reset probabilities
function clearAllModels() {
  selectedModels.value.clear()
  Object.keys(modelProbabilities).forEach(key => {
    modelProbabilities[key] = 0
  })
  
  // Emit changes to parent
  emit('modelsChanged', selectedModels.value, modelProbabilities)
}

// WHAT: Apply recommended models from backend AI analysis
function applyRecommendedModels() {
  if (!hasRecommendations.value) return
  
  // Clear existing selections
  clearAllModels()
  
  // Apply recommended models
  props.recommendations.recommendations.forEach((rec: any) => {
    selectedModels.value.add(rec.model_type)
  })
  
  // Emit changes to parent
  emit('modelsChanged', selectedModels.value, modelProbabilities)
}

// WHAT: Apply recommended probabilities from backend AI analysis
function applyRecommendedProbabilities() {
  if (!hasRecommendations.value) return
  
  props.recommendations.recommendations.forEach((rec: any) => {
    if (selectedModels.value.has(rec.model_type)) {
      modelProbabilities[rec.model_type] = rec.probability
    }
  })
  
  // Emit changes to parent
  emit('modelsChanged', selectedModels.value, modelProbabilities)
}

// WHAT: Check if a specific model is recommended by the system
function isModelRecommended(modelKey: string): boolean {
  if (!hasRecommendations.value) return false
  
  return props.recommendations.recommendations.some((rec: any) => 
    rec.model_type === modelKey && rec.is_recommended
  )
}

// WHAT: Get recommended probability for a specific model
function getRecommendedProbability(modelKey: string): number {
  if (!hasRecommendations.value) return 0
  
  const recommendation = props.recommendations.recommendations.find((rec: any) => 
    rec.model_type === modelKey
  )
  
  return recommendation ? recommendation.probability : 0
}

// WHAT: Validate that probabilities don't exceed 100% and emit changes
function validateProbabilities() {
  // Emit changes to parent whenever probabilities change
  emit('modelsChanged', selectedModels.value, modelProbabilities)
}
</script>

<style scoped>
/* WHAT: Component-specific styles for ModelOutcomes */
.btn-xs {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
}

.position-relative {
  position: relative;
}

.position-absolute {
  position: absolute;
}

.top-0 {
  top: 0;
}

.start-100 {
  left: 100%;
}

.translate-middle {
  transform: translate(-50%, -50%);
}
</style>
