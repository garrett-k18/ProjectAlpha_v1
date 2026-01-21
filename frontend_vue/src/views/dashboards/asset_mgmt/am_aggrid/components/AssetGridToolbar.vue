<template>
  <div class="d-flex justify-content-between flex-wrap gap-2 mb-2 align-items-center">
    <!-- Left side: Quick filter + Dropdown filters -->
    <div class="d-flex flex-wrap gap-2 align-items-center">
      <!-- Quick Filter -->
      <div class="input-group input-group-sm" style="width: 200px;">
        <span class="input-group-text"><i class="mdi mdi-magnify"></i></span>
        <input
          v-model="quickFilterModel"
          type="text"
          class="form-control"
          placeholder="Quick filter..."
          aria-label="Quick filter"
        />
        <button
          v-if="quickFilterModel"
          class="btn btn-light"
          type="button"
          title="Clear"
          @click="quickFilterModel = ''"
        >
          <i class="mdi mdi-close"></i>
        </button>
      </div>

      <!-- Trade Name Filter -->
      <MultiSelectDropdown
        label="Trade"
        :options="uniqueTrades"
        v-model="selectedTradesModel"
        v-model:isOpen="showTradeDropdown"
        @change="handleFilterChange"
      />

      <!-- Seller Name Filter -->
      <MultiSelectDropdown
        label="Seller"
        :options="uniqueSellers"
        v-model="selectedSellersModel"
        v-model:isOpen="showSellerDropdown"
        @change="handleFilterChange"
      />

      <!-- Fund/Partnership Filter -->
      <MultiSelectDropdown
        label="Fund"
        :options="uniqueFunds"
        v-model="selectedFundsModel"
        v-model:isOpen="showFundDropdown"
        @change="handleFilterChange"
      />

      <!-- Active Tracks Filter -->
      <MultiSelectDropdown
        label="Tracks"
        :options="uniqueTracks"
        v-model="selectedTracksModel"
        v-model:isOpen="showTracksDropdown"
        @change="handleFilterChange"
      />

      <!-- Clear Filters Button -->
      <button
        v-if="hasActiveFilters"
        class="btn btn-sm btn-light"
        type="button"
        title="Clear all filters"
        @click="handleClearFilters"
      >
        <i class="mdi mdi-filter-remove"></i>
      </button>
    </div>

    <!-- Right side: View dropdown -->
    <div class="d-flex flex-wrap gap-2 align-items-center justify-content-center">
      <div class="d-flex align-items-center gap-1">
        <label for="viewSelect" class="small mb-0 text-nowrap">View:</label>
        <select
          id="viewSelect"
          class="form-select form-select-sm"
          v-model="activeViewModel"
          @change="handleViewChange"
          style="min-width: 100px;"
        >
          <option value="snapshot">Snapshot</option>
          <option value="performance">Performance</option>
          <option value="valuation">Valuation</option>
          <option value="servicing">Servicing</option>
          <option value="all">All</option>
        </select>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import MultiSelectDropdown from './MultiSelectDropdown.vue'

const props = defineProps<{
  quickFilter: string
  selectedTrades: string[]
  selectedSellers: string[]
  selectedFunds: string[]
  selectedTracks: string[]
  uniqueTrades: string[]
  uniqueSellers: string[]
  uniqueFunds: string[]
  uniqueTracks: string[]
  showTradeDropdown: boolean
  showSellerDropdown: boolean
  showFundDropdown: boolean
  showTracksDropdown: boolean
  hasActiveFilters: boolean
  activeView: string
}>()

const emit = defineEmits<{
  'update:quickFilter': [value: string]
  'update:selectedTrades': [value: string[]]
  'update:selectedSellers': [value: string[]]
  'update:selectedFunds': [value: string[]]
  'update:selectedTracks': [value: string[]]
  'update:showTradeDropdown': [value: boolean]
  'update:showSellerDropdown': [value: boolean]
  'update:showFundDropdown': [value: boolean]
  'update:showTracksDropdown': [value: boolean]
  'update:activeView': [value: string]
  'filterChange': []
  'clearFilters': []
  'viewChange': []
}>()

// Two-way binding helpers
const quickFilterModel = computed({
  get: () => props.quickFilter,
  set: (val) => emit('update:quickFilter', val),
})

const selectedTradesModel = computed({
  get: () => props.selectedTrades,
  set: (val) => emit('update:selectedTrades', val),
})

const selectedSellersModel = computed({
  get: () => props.selectedSellers,
  set: (val) => emit('update:selectedSellers', val),
})

const selectedFundsModel = computed({
  get: () => props.selectedFunds,
  set: (val) => emit('update:selectedFunds', val),
})

const selectedTracksModel = computed({
  get: () => props.selectedTracks,
  set: (val) => emit('update:selectedTracks', val),
})

const activeViewModel = computed({
  get: () => props.activeView,
  set: (val) => emit('update:activeView', val),
})

const showTradeDropdown = computed({
  get: () => props.showTradeDropdown,
  set: (val) => emit('update:showTradeDropdown', val),
})

const showSellerDropdown = computed({
  get: () => props.showSellerDropdown,
  set: (val) => emit('update:showSellerDropdown', val),
})

const showFundDropdown = computed({
  get: () => props.showFundDropdown,
  set: (val) => emit('update:showFundDropdown', val),
})

const showTracksDropdown = computed({
  get: () => props.showTracksDropdown,
  set: (val) => emit('update:showTracksDropdown', val),
})

function handleFilterChange(): void {
  emit('filterChange')
}

function handleClearFilters(): void {
  emit('clearFilters')
}

function handleViewChange(): void {
  emit('viewChange')
}
</script>

<style scoped>
/* Inherits parent styles */
</style>
