<template>
  <Layout>
    <!-- Page Title -->
    <b-row>
      <b-col class="col-12">
        <div class="page-title-box">
          <div class="page-title-right">
            <div class="d-flex gap-2">
              <button class="btn btn-sm btn-success" @click="handleExport">
                <i class="mdi mdi-download me-1"></i>
                Export
              </button>
              <button class="btn btn-sm btn-primary" @click="showCreateModal = true">
                <i class="mdi mdi-plus me-1"></i>
                New Entry
              </button>
              <button class="btn btn-sm btn-secondary" @click="showFiltersModal = true">
                <i class="mdi mdi-filter me-1"></i>
                Filters
                <span v-if="hasActiveFilters" class="badge bg-danger ms-1">{{ activeFilterCount }}</span>
              </button>
            </div>
          </div>
          <h4 class="page-title">General Ledger Dashboard</h4>
        </div>
      </b-col>
    </b-row>

    <!-- Summary Stats Cards -->
    <GLSummaryCards 
      :summary="summary"
      :loading="loadingSummary"
    />

    <!-- Main Content -->
    <b-row class="g-2 mt-2">
      <!-- Charts Section -->
      <b-col xl="12" lg="12">
        <b-row class="g-2">
          <!-- Tag Distribution Chart -->
          <b-col xl="6" lg="12">
            <div class="card">
              <div class="card-body">
                <h4 class="header-title mb-3">
                  <i class="mdi mdi-tag-multiple text-primary me-1"></i>
                  By Category (Tag)
                </h4>
                <GLTagChart 
                  :data="byTagData"
                  :loading="loadingCharts"
                />
              </div>
            </div>
          </b-col>

          <!-- Bucket Distribution Chart -->
          <b-col xl="6" lg="12">
            <div class="card">
              <div class="card-body">
                <h4 class="header-title mb-3">
                  <i class="mdi mdi-briefcase text-success me-1"></i>
                  By Strategic Bucket
                </h4>
                <GLBucketChart 
                  :data="byBucketData"
                  :loading="loadingCharts"
                />
              </div>
            </div>
          </b-col>

          <!-- Monthly Trend Chart -->
          <b-col xl="8" lg="12">
            <div class="card">
              <div class="card-body">
                <h4 class="header-title mb-3">
                  <i class="mdi mdi-chart-line text-info me-1"></i>
                  Monthly Trend (12 Months)
                </h4>
                <GLMonthlyTrendChart 
                  :data="monthlyTrendData"
                  :loading="loadingCharts"
                />
              </div>
            </div>
          </b-col>

          <!-- Top Accounts -->
          <b-col xl="4" lg="12">
            <div class="card">
              <div class="card-body">
                <h4 class="header-title mb-3">
                  <i class="mdi mdi-currency-usd text-warning me-1"></i>
                  Top 10 Accounts
                </h4>
                <GLTopAccountsList 
                  :data="byAccountData"
                  :loading="loadingCharts"
                />
              </div>
            </div>
          </b-col>
        </b-row>
      </b-col>

      <!-- Entries Grid -->
      <b-col xl="12" lg="12" class="mt-2">
        <div class="card">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h4 class="header-title">
                <i class="mdi mdi-format-list-bulleted text-secondary me-1"></i>
                General Ledger Entries
              </h4>
              <div class="d-flex gap-2 align-items-center">
                <!-- Search Input -->
                <div class="input-group" style="width: 300px;">
                  <span class="input-group-text">
                    <i class="mdi mdi-magnify"></i>
                  </span>
                  <input
                    v-model="searchQuery"
                    type="text"
                    class="form-control"
                    placeholder="Search entries..."
                    @input="debouncedSearch"
                  />
                </div>
                <!-- Review Filter Toggle -->
                <button
                  class="btn btn-sm"
                  :class="showReviewOnly ? 'btn-warning' : 'btn-outline-secondary'"
                  @click="toggleReviewFilter"
                >
                  <i class="mdi mdi-flag"></i>
                  Review Only
                  <span v-if="summary?.entries_requiring_review" class="badge bg-danger ms-1">
                    {{ summary.entries_requiring_review }}
                  </span>
                </button>
              </div>
            </div>
            <GLEntriesGrid 
              :entries="entries"
              :loading="loadingEntries"
              :current-page="currentPage"
              :page-size="pageSize"
              :total-entries="totalEntries"
              @page-change="handlePageChange"
              @edit-entry="handleEditEntry"
              @delete-entry="handleDeleteEntry"
              @flag-entry="handleFlagEntry"
            />
          </div>
        </div>
      </b-col>
    </b-row>

    <!-- Modals -->
    <GLFiltersModal
      v-model="showFiltersModal"
      :filters="filters"
      @apply="handleApplyFilters"
      @reset="handleResetFilters"
    />

    <GLEntryFormModal
      v-model="showCreateModal"
      :entry="null"
      @save="handleSaveEntry"
    />

    <GLEntryFormModal
      v-model="showEditModal"
      :entry="editingEntry"
      @save="handleSaveEntry"
    />
  </Layout>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, watch } from 'vue'
import { storeToRefs } from 'pinia'
import Layout from '@/components/layouts/layout.vue'
import { useGeneralLedgerStore } from '@/stores/generalLedger'
import type { GLEntryFilters, GLEntryListItem, GLEntry } from '@/stores/generalLedger'
import GLSummaryCards from './components/GLSummaryCards.vue'
import GLTagChart from './components/GLTagChart.vue'
import GLBucketChart from './components/GLBucketChart.vue'
import GLMonthlyTrendChart from './components/GLMonthlyTrendChart.vue'
import GLTopAccountsList from './components/GLTopAccountsList.vue'
import GLEntriesGrid from './components/GLEntriesGrid.vue'
import GLFiltersModal from './components/GLFiltersModal.vue'
import GLEntryFormModal from './components/GLEntryFormModal.vue'

export default defineComponent({
  name: 'GeneralLedgerDashboard',
  components: {
    Layout,
    GLSummaryCards,
    GLTagChart,
    GLBucketChart,
    GLMonthlyTrendChart,
    GLTopAccountsList,
    GLEntriesGrid,
    GLFiltersModal,
    GLEntryFormModal,
  },
  setup() {
    // WHAT: Initialize GL store and extract reactive state
    // WHY: Access centralized GL data and actions
    // HOW: Use storeToRefs for reactive refs
    const glStore = useGeneralLedgerStore()
    const {
      entries,
      summary,
      filters,
      byTagData,
      byBucketData,
      byAccountData,
      monthlyTrendData,
      loadingEntries,
      loadingSummary,
      loadingCharts,
      currentPage,
      pageSize,
      totalEntries,
    } = storeToRefs(glStore)

    // WHAT: Local UI state
    // WHY: Manage modal visibility and user interactions
    // HOW: Vue refs for reactive UI state
    const showFiltersModal = ref<boolean>(false)
    const showCreateModal = ref<boolean>(false)
    const showEditModal = ref<boolean>(false)
    const editingEntry = ref<GLEntry | null>(null)
    const searchQuery = ref<string>('')
    const showReviewOnly = ref<boolean>(false)
    const searchDebounceTimer = ref<number | null>(null)

    // WHAT: Computed properties for UI logic
    // WHY: Reactive derived state
    // HOW: Vue computed functions
    const hasActiveFilters = computed<boolean>(() => glStore.hasActiveFilters)
    
    const activeFilterCount = computed<number>(() => {
      return Object.values(filters.value).filter(v => v !== null && v !== undefined && v !== '').length
    })

    // -----------------------------
    // Event Handlers
    // -----------------------------

    /**
     * WHAT: Handle page change in grid
     * WHY: Navigate through paginated entries
     * HOW: Update store page and fetch new data
     */
    function handlePageChange(page: number): void {
      glStore.setPage(page)
      glStore.fetchEntries()
    }

    /**
     * WHAT: Handle apply filters from modal
     * WHY: Update active filters and refresh data
     * HOW: Call store setFilters and refreshAll
     */
    async function handleApplyFilters(newFilters: GLEntryFilters): Promise<void> {
      glStore.setFilters(newFilters)
      showFiltersModal.value = false
      await glStore.refreshAll()
    }

    /**
     * WHAT: Handle reset filters
     * WHY: Clear all filters and show all entries
     * HOW: Call store resetFilters and refreshAll
     */
    async function handleResetFilters(): Promise<void> {
      glStore.resetFilters()
      showReviewOnly.value = false
      searchQuery.value = ''
      showFiltersModal.value = false
      await glStore.refreshAll()
    }

    /**
     * WHAT: Handle save entry (create or update)
     * WHY: Persist entry changes
     * HOW: Call store create/update action
     */
    async function handleSaveEntry(entryData: Partial<GLEntry>): Promise<void> {
      try {
        if (editingEntry.value?.id) {
          await glStore.updateEntry(editingEntry.value.id, entryData)
        } else {
          await glStore.createEntry(entryData)
        }
        showCreateModal.value = false
        showEditModal.value = false
        editingEntry.value = null
        await glStore.refreshAll()
      } catch (error) {
        console.error('[GL Dashboard] Error saving entry:', error)
        alert('Error saving entry. Please try again.')
      }
    }

    /**
     * WHAT: Handle edit entry from grid
     * WHY: Open edit modal with entry data
     * HOW: Fetch full entry and show modal
     */
    async function handleEditEntry(entry: GLEntryListItem): Promise<void> {
      try {
        await glStore.fetchEntry(entry.id)
        editingEntry.value = glStore.currentEntry
        showEditModal.value = true
      } catch (error) {
        console.error('[GL Dashboard] Error loading entry:', error)
        alert('Error loading entry. Please try again.')
      }
    }

    /**
     * WHAT: Handle delete entry from grid
     * WHY: Remove entry from system
     * HOW: Confirm and call store deleteEntry
     */
    async function handleDeleteEntry(entry: GLEntryListItem): Promise<void> {
      if (!confirm(`Delete GL Entry ${entry.entry}?`)) return
      
      try {
        await glStore.deleteEntry(entry.id)
        await glStore.refreshAll()
      } catch (error) {
        console.error('[GL Dashboard] Error deleting entry:', error)
        alert('Error deleting entry. Please try again.')
      }
    }

    /**
     * WHAT: Handle flag entry for review
     * WHY: Mark entry needing attention
     * HOW: Prompt for notes and call store flagForReview
     */
    async function handleFlagEntry(entry: GLEntryListItem): Promise<void> {
      const notes = prompt('Review notes (optional):')
      if (notes === null) return // User cancelled
      
      try {
        await glStore.flagForReview(entry.id, notes || undefined)
        await glStore.refreshAll()
      } catch (error) {
        console.error('[GL Dashboard] Error flagging entry:', error)
        alert('Error flagging entry. Please try again.')
      }
    }

    /**
     * WHAT: Handle export
     * WHY: Download filtered entries as CSV/Excel
     * HOW: Placeholder for future implementation
     */
    function handleExport(): void {
      alert('Export functionality coming soon!')
    }

    /**
     * WHAT: Debounced search handler
     * WHY: Avoid excessive API calls while typing
     * HOW: Clear and set timeout for search
     */
    function debouncedSearch(): void {
      if (searchDebounceTimer.value) {
        clearTimeout(searchDebounceTimer.value)
      }
      
      searchDebounceTimer.value = setTimeout(async () => {
        const newFilters: GLEntryFilters = {
          ...filters.value,
          search: searchQuery.value || null,
        }
        glStore.setFilters(newFilters)
        await glStore.refreshAll()
      }, 500) as unknown as number
    }

    /**
     * WHAT: Toggle review-only filter
     * WHY: Show/hide entries requiring review
     * HOW: Update filters and refresh data
     */
    async function toggleReviewFilter(): Promise<void> {
      showReviewOnly.value = !showReviewOnly.value
      const newFilters: GLEntryFilters = {
        ...filters.value,
        requires_review: showReviewOnly.value ? true : null,
      }
      glStore.setFilters(newFilters)
      await glStore.refreshAll()
    }

    // -----------------------------
    // Lifecycle Hooks
    // -----------------------------

    /**
     * WHAT: Initialize dashboard on mount
     * WHY: Load all data when component is created
     * HOW: Call store refreshAll action
     */
    onMounted(async () => {
      await glStore.refreshAll()
    })

    return {
      // State
      entries,
      summary,
      filters,
      byTagData,
      byBucketData,
      byAccountData,
      monthlyTrendData,
      loadingEntries,
      loadingSummary,
      loadingCharts,
      currentPage,
      pageSize,
      totalEntries,
      
      // Local UI state
      showFiltersModal,
      showCreateModal,
      showEditModal,
      editingEntry,
      searchQuery,
      showReviewOnly,
      
      // Computed
      hasActiveFilters,
      activeFilterCount,
      
      // Methods
      handlePageChange,
      handleApplyFilters,
      handleResetFilters,
      handleSaveEntry,
      handleEditEntry,
      handleDeleteEntry,
      handleFlagEntry,
      handleExport,
      debouncedSearch,
      toggleReviewFilter,
    }
  },
})
</script>

<style scoped>
/* WHAT: Custom styles for GL dashboard */
/* WHY: Enhance UI consistency and branding */
/* HOW: Scoped component-specific styles */

.page-title-box {
  margin-bottom: 1rem;
}

.input-group-text {
  background-color: #f1f3fa;
  border-color: #dee2e6;
}

@media (max-width: 768px) {
  .page-title-right .d-flex {
    flex-direction: column;
    width: 100%;
  }
  
  .page-title-right .btn {
    width: 100%;
  }
  
  .input-group {
    width: 100% !important;
  }
}
</style>

