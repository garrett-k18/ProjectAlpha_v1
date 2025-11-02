<template>
  <!-- Model Outcome Selector -->
  <div class="card mb-3">
    <div class="card-body p-3">
      <div class="d-flex align-items-center justify-content-between mb-3">
        <h5 class="mb-0 fw-semibold text-body">
          <i class="mdi mdi-calculator-variant me-2 text-primary"></i>
          Model Outcomes
        </h5>
        <button 
          v-if="hasRecommendations"
          type="button" 
          class="btn btn-sm btn-outline-success"
          @click="applyRecommendedModels"
        >
          <i class="mdi mdi-auto-fix me-1"></i>
          Apply Recommendations
        </button>
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

    </div>
  </div>

  <!-- Model Cards (conditionally rendered based on selection) -->
  <div class="row g-3">
    <div v-if="selectedModels.has('fc_sale')" class="col-12">
      <ForeclosureModelCard 
        :row="row"
        :assetId="assetId"
        :is-only-selected-model="selectedModels.size === 1"
        :shared-acquisition-price="sharedAcquisitionPrice"
        @assumptions-changed="handleFcAssumptionsChanged"
        @probability-changed="handleFcProbabilityChanged"
        @acquisition-price-changed="handleAcquisitionPriceChanged"
      />
    </div>

    <div v-if="selectedModels.has('reo_sale')" class="col-12">
      <REOSaleModelCard 
        :row="row"
        :assetId="assetId"
        :is-only-selected-model="selectedModels.size === 1"
        :shared-acquisition-price="sharedAcquisitionPrice"
        @assumptions-changed="handleReoAssumptionsChanged"
        @probability-changed="handleReoProbabilityChanged"
        @acquisition-price-changed="handleAcquisitionPriceChanged"
      />
    </div>

    <div v-if="selectedModels.has('mod_reperform')" class="col-12">
      <div class="card border-primary">
        <div class="card-header bg-primary-subtle">
          <h5 class="mb-0 d-flex align-items-center">
            <i class="fas fa-handshake me-2 text-primary"></i>
            Modification & Re-Performance Model
            <span class="badge bg-primary ms-2">{{ modelProbabilities.mod_reperform }}% Probability</span>
          </h5>
        </div>
        <div class="card-body">
          <p class="text-muted">Modification model detailed inputs will go here (payment reduction, term extension, interest rate adjustment)</p>
          <!-- TODO: Add detailed assumption inputs -->
        </div>
      </div>
    </div>

    <div v-if="selectedModels.has('short_sale')" class="col-12">
      <div class="card border-primary">
        <div class="card-header bg-primary-subtle">
          <h5 class="mb-0 d-flex align-items-center">
            <i class="fas fa-percent me-2 text-primary"></i>
            Short Sale Model
            <span class="badge bg-primary ms-2">{{ modelProbabilities.short_sale }}% Probability</span>
          </h5>
        </div>
        <div class="card-body">
          <p class="text-muted">Short Sale model detailed inputs will go here (discount expectations, timeline, approval process)</p>
          <!-- TODO: Add detailed assumption inputs -->
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch, onMounted } from 'vue'
import ForeclosureModelCard from './ForeclosureModelCard.vue'
import REOSaleModelCard from './REOSaleModelCard.vue'

// WHAT: Props for the ModelOutcomes component
const props = defineProps<{
  recommendations?: any | null
  loadingRecommendations?: boolean
  row?: Record<string, any> | null
  assetId?: string | number | null
}>()

// WHAT: Emits for parent component communication
const emit = defineEmits<{
  modelsChanged: [selectedModels: Set<string>, probabilities: Record<string, number>]
}>()

// WHAT: Available disposition models with their configuration
// WHY: Professional dark color scheme for selected models
const availableModels = [
  {
    key: 'fc_sale',
    label: 'FC Sale',
    icon: 'fas fa-gavel',
    activeClass: 'btn-primary'  // Professional blue instead of bright red
  },
  {
    key: 'reo_sale', 
    label: 'REO Sale',
    icon: 'fas fa-house-chimney',
    activeClass: 'btn-primary'  // Consistent primary blue
  },
  {
    key: 'mod_reperform',
    label: 'Mod & Re-Perform',
    icon: 'fas fa-handshake',
    activeClass: 'btn-primary'  // Consistent primary blue
  },
  {
    key: 'short_sale',
    label: 'Short Sale',
    icon: 'fas fa-percent',
    activeClass: 'btn-primary'  // Consistent primary blue
  }
]

// WHAT: Reactive state for selected models and their probabilities
const selectedModels = ref(new Set<string>())
const modelProbabilities = reactive<Record<string, number>>({
  fc_sale: 0,
  reo_sale: 0,
  mod_reperform: 0,
  short_sale: 0
})

// WHAT: Shared acquisition price across all models
// WHY: Ensure acquisition price stays synchronized between all model cards
const sharedAcquisitionPrice = ref<number>(0)

// WHAT: Computed property to check if we have recommendations from backend
const hasRecommendations = computed(() => {
  return props.recommendations && 
         props.recommendations.recommendations && 
         props.recommendations.recommendations.length > 0
})


// WHAT: Toggle model selection on/off
function toggleModel(modelKey: string) {
  if (selectedModels.value.has(modelKey)) {
    selectedModels.value.delete(modelKey)
    modelProbabilities[modelKey] = 0
  } else {
    selectedModels.value.add(modelKey)
    // WHAT: If this is the only model selected, auto-set probability to 100%
    if (selectedModels.value.size === 1) {
      modelProbabilities[modelKey] = 100
    }
  }
  
  // WHAT: Save selected models to localStorage
  // WHY: Persist selection across page refreshes
  saveSelectedModels()
  
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
  
  // WHAT: Save applied recommendations to localStorage
  // WHY: Persist selections across page refreshes
  saveSelectedModels()
  
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

// WHAT: Validate that probabilities don't exceed 100% and emit changes
function validateProbabilities() {
  // Emit changes to parent whenever probabilities change
  emit('modelsChanged', selectedModels.value, modelProbabilities)
}

// WHAT: Handle foreclosure model assumptions changes
function handleFcAssumptionsChanged(assumptions: any) {
  // Store FC assumptions for future use (could emit to parent or save to store)
  console.log('[ModelOutcomes] FC assumptions changed:', assumptions)
  // TODO: Implement assumptions storage/persistence logic
}

// WHAT: Handle FC Sale probability change from ForeclosureModelCard
function handleFcProbabilityChanged(probability: number) {
  // Update local FC Sale probability
  modelProbabilities.fc_sale = probability
  
  // WHAT: Save probabilities to localStorage
  // WHY: Persist probability values across page refreshes
  saveSelectedModels()
  
  // Emit changes to parent
  emit('modelsChanged', selectedModels.value, modelProbabilities)
  
  console.log('[ModelOutcomes] FC Sale probability changed:', probability)
}

// WHAT: Handle REO Sale assumptions change from REOSaleModelCard
function handleReoAssumptionsChanged(assumptions: any) {
  // Store REO assumptions for future use
  console.log('[ModelOutcomes] REO assumptions changed:', assumptions)
  // TODO: Implement assumptions storage/persistence logic
}

// WHAT: Handle REO Sale probability change from REOSaleModelCard
function handleReoProbabilityChanged(probability: number) {
  // Update local REO Sale probability
  modelProbabilities.reo_sale = probability
  
  // WHAT: Save probabilities to localStorage
  // WHY: Persist probability values across page refreshes
  saveSelectedModels()
  
  // Emit changes to parent
  emit('modelsChanged', selectedModels.value, modelProbabilities)
  
  console.log('[ModelOutcomes] REO Sale probability changed:', probability)
}

// WHAT: Handle acquisition price change from any model card
// WHY: Synchronize acquisition price across all model cards
function handleAcquisitionPriceChanged(price: number) {
  sharedAcquisitionPrice.value = price
  console.log('[ModelOutcomes] Acquisition price changed:', price)
}

// WHAT: Get localStorage key for this asset
// WHY: Store selections per asset so each asset remembers its own models
function getStorageKey(): string {
  return `model_outcomes_${props.assetId || 'default'}`
}

// WHAT: Save selected models and probabilities to localStorage
// WHY: Persist user selections across page refreshes
function saveSelectedModels() {
  if (!props.assetId) return
  
  const data = {
    selectedModels: Array.from(selectedModels.value),
    probabilities: { ...modelProbabilities }
  }
  
  try {
    localStorage.setItem(getStorageKey(), JSON.stringify(data))
    console.log('[ModelOutcomes] Saved to localStorage:', data)
  } catch (error) {
    console.error('[ModelOutcomes] Failed to save to localStorage:', error)
  }
}

// WHAT: Load selected models and probabilities from localStorage
// WHY: Restore user selections on page refresh
function loadSelectedModels() {
  if (!props.assetId) return
  
  try {
    const stored = localStorage.getItem(getStorageKey())
    if (stored) {
      const data = JSON.parse(stored)
      
      // WHAT: Restore selected models
      selectedModels.value = new Set(data.selectedModels || [])
      
      // WHAT: Restore probabilities
      if (data.probabilities) {
        Object.assign(modelProbabilities, data.probabilities)
      }
      
      console.log('[ModelOutcomes] Loaded from localStorage:', data)
      
      // WHAT: Emit initial state to parent
      // WHY: Parent needs to know about restored selections
      emit('modelsChanged', selectedModels.value, modelProbabilities)
    }
  } catch (error) {
    console.error('[ModelOutcomes] Failed to load from localStorage:', error)
  }
}

// WHAT: Watch for assetId changes and load selections
// WHY: Load different selections when viewing different assets
watch(() => props.assetId, (newAssetId) => {
  if (newAssetId) {
    loadSelectedModels()
  }
}, { immediate: true })

// WHAT: Load selections on component mount
// WHY: Restore selections when component first renders
onMounted(() => {
  loadSelectedModels()
})
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

/* Consistent primary color styling for all model cards */
.bg-primary-subtle {
  background-color: rgba(13, 110, 253, 0.1) !important;
}

.border-primary {
  border-color: rgba(13, 110, 253, 0.3) !important;
}
</style>
