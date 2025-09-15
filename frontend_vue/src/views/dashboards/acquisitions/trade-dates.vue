<template>
  <div class="d-flex flex-wrap align-items-center justify-content-center gap-2 mt-2" v-if="showDates">
    <!-- Bid Date -->
    <div class="d-flex flex-column align-items-center">
      <label class="form-label fw-bold text-center w-100 fs-5 mb-1" for="bidDateInput">Bid Date</label>
      <input
        type="date"
        id="bidDateInput"
        class="form-control form-control-sm text-center"
        style="width: 200px; min-width: 200px; max-width: 200px;"
        v-model="bidDateModel"
        :disabled="loading || !tradeId"
        @change="handleBidDateChange"
      />
    </div>

    <!-- Settlement Date -->
    <div class="d-flex flex-column align-items-center">
      <label class="form-label fw-bold text-center w-100 fs-5 mb-1" for="settlementDateInput">Settlement Date</label>
      <input
        type="date"
        id="settlementDateInput"
        class="form-control form-control-sm text-center"
        style="width: 200px; min-width: 200px; max-width: 200px;"
        v-model="settlementDateModel"
        :disabled="loading || !tradeId"
        @change="handleSettlementDateChange"
      />
    </div>

    <!-- Save button -->
    <div class="d-flex align-items-end" v-if="hasChanges && tradeId">
      <button
        class="btn btn-sm btn-primary mb-0"
        :disabled="loading"
        @click="saveChanges"
      >
        <i class="mdi mdi-content-save me-1"></i> Save
      </button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, watch, onMounted } from 'vue';
import { useTradeAssumptionsStore } from '@/stores/tradeAssumptions';
import { useAcqSelectionsStore } from '@/stores/acqSelections';

export default defineComponent({
  name: 'TradeDates',
  
  setup() {
    // Import stores
    const tradeAssumptionsStore = useTradeAssumptionsStore();
    const acqSelectionsStore = useAcqSelectionsStore();
    
    // Local form models
    const bidDateModel = ref<string>('');
    const settlementDateModel = ref<string>('');
    const originalBidDate = ref<string>('');
    const originalSettlementDate = ref<string>('');
    
    // Track if there are unsaved changes
    const hasChanges = computed(() => {
      return bidDateModel.value !== originalBidDate.value || 
             settlementDateModel.value !== originalSettlementDate.value;
    });
    
    // Current trade ID from selections store
    const tradeId = computed(() => acqSelectionsStore.selectedTradeId);
    
    // Only show dates when a trade is selected
    const showDates = computed(() => !!tradeId.value);
    
    // Loading state from store
    const loading = computed(() => tradeAssumptionsStore.loading);
    
    // Watch for trade ID changes to load assumptions
    watch(tradeId, async (newTradeId) => {
      if (newTradeId) {
        await tradeAssumptionsStore.fetchAssumptions(newTradeId);
        updateLocalModels();
      } else {
        resetLocalModels();
      }
    }, { immediate: true });
    
    // Watch for assumption changes in store
    watch(() => tradeAssumptionsStore.assumptions, () => {
      updateLocalModels();
    });
    
    // Update local models from store
    function updateLocalModels() {
      const assumptions = tradeAssumptionsStore.assumptions;
      if (assumptions) {
        // Format date strings to YYYY-MM-DD for input[type="date"]
        bidDateModel.value = assumptions.bid_date ? assumptions.bid_date.substring(0, 10) : '';
        settlementDateModel.value = assumptions.settlement_date ? assumptions.settlement_date.substring(0, 10) : '';
        
        // Store original values to detect changes
        originalBidDate.value = bidDateModel.value;
        originalSettlementDate.value = settlementDateModel.value;
      } else {
        resetLocalModels();
      }
    }
    
    // Reset local models
    function resetLocalModels() {
      bidDateModel.value = '';
      settlementDateModel.value = '';
      originalBidDate.value = '';
      originalSettlementDate.value = '';
    }
    
    // Handlers for input changes
    function handleBidDateChange() {
      // Optional validation could be added here
    }
    
    function handleSettlementDateChange() {
      // Optional validation could be added here
    }
    
    // Save changes to the backend
    async function saveChanges() {
      if (!tradeId.value) return;
      
      const data = {
        bid_date: bidDateModel.value || null,
        settlement_date: settlementDateModel.value || null,
      };
      
      const success = await tradeAssumptionsStore.updateAssumptions(tradeId.value, data);
      
      if (success) {
        // Update our original values to match current values
        originalBidDate.value = bidDateModel.value;
        originalSettlementDate.value = settlementDateModel.value;
      }
    }
    
    // Load data on component mount if trade is already selected
    onMounted(async () => {
      if (tradeId.value) {
        await tradeAssumptionsStore.fetchAssumptions(tradeId.value);
        updateLocalModels();
      }
    });
    
    return {
      bidDateModel,
      settlementDateModel,
      hasChanges,
      tradeId,
      showDates,
      loading,
      handleBidDateChange,
      handleSettlementDateChange,
      saveChanges,
    };
  }
});
</script>

<style scoped>
/* Add any component-specific styles here */
</style>
