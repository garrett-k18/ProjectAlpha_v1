/**
 * WHAT: Pinia store for General Ledger Entries
 * WHY: Centralized state management for GL data, filters, and analytics
 * HOW: Uses Axios for API calls and reactive state for UI synchronization
 * WHERE: Used by GL dashboard and entry management components
 * 
 * Documentation reviewed:
 * - Pinia: https://pinia.vuejs.org/core-concepts/
 * - Axios: https://axios-http.com/docs/intro
 */

import { defineStore } from 'pinia'
import http from '@/lib/http'
import type { AxiosResponse } from 'axios'

// -----------------------------
// Type Definitions
// -----------------------------

/**
 * WHAT: GL Entry Tag types for categorization
 * WHY: Type-safe tag filtering and display
 * HOW: Matches backend EntryTag choices
 */
export type GLEntryTag = 
  | 'loan_origination'
  | 'loan_payment'
  | 'loan_modification'
  | 'property_acquisition'
  | 'property_disposition'
  | 'operating_expense'
  | 'capital_expense'
  | 'interest_income'
  | 'interest_expense'
  | 'fee_income'
  | 'impairment'
  | 'recovery'
  | 'adjustment'
  | 'other'
  | null

/**
 * WHAT: GL Entry Bucket types for strategic grouping
 * WHY: Type-safe bucket filtering and analysis
 * HOW: Matches backend EntryBucket choices
 */
export type GLEntryBucket =
  | 'acquisition'
  | 'servicing'
  | 'asset_management'
  | 'disposition'
  | 'capital_markets'
  | 'fund_operations'
  | 'overhead'
  | 'special_situations'
  | null

/**
 * WHAT: GL Entry interface matching backend serializer
 * WHY: Type-safe GL entry data handling
 * HOW: Mirrors GeneralLedgerEntriesSerializer fields
 */
export interface GLEntry {
  id: number
  entry: string
  company_name: string
  loan_number: string | null
  asset_hub: number | null
  asset_hub_display: {
    id: number
    sellertape_id: string | null
    servicer_id: string | null
  } | null
  borrower_name: string | null
  document_number: string | null
  external_document_number: string | null
  document_type: string | null
  loan_type: string | null
  date_funded: string | null
  posting_date: string
  entry_date: string
  amount: string | null
  credit_amount: string
  debit_amount: string
  net_amount: string
  is_balanced: boolean
  account_number: string
  account_name: string
  description: string | null
  reason_code: string | null
  comment: string | null
  cost_center: string | null
  cost_center_name: string | null
  tag: GLEntryTag
  bucket: GLEntryBucket
  ai_notes: string | null
  requires_review: boolean
  review_notes: string | null
  created_by: number | null
  created_by_username: string | null
  updated_by: number | null
  updated_by_username: string | null
  created_at: string
  updated_at: string
}

/**
 * WHAT: Lightweight GL Entry for list displays
 * WHY: Reduce data transfer for grid views
 * HOW: Subset of GLEntry fields
 */
export interface GLEntryListItem {
  id: number
  entry: string
  posting_date: string
  entry_date: string
  company_name: string
  loan_number: string | null
  asset_hub: number | null
  account_number: string
  account_name: string
  debit_amount: string
  credit_amount: string
  net_amount: string
  tag: GLEntryTag
  bucket: GLEntryBucket
  requires_review: boolean
  created_by_username: string | null
  created_at: string
}

/**
 * WHAT: Summary statistics interface
 * WHY: Type-safe summary data for dashboard KPIs
 * HOW: Matches GLEntrySummarySerializer
 */
export interface GLEntrySummary {
  total_entries: number
  total_debits: string
  total_credits: string
  net_total: string
  entries_requiring_review: number
  date_range_start: string | null
  date_range_end: string | null
  by_tag: Record<string, number>
  by_bucket: Record<string, number>
}

/**
 * WHAT: Filter parameters for GL entry queries
 * WHY: Type-safe filter handling for API requests
 * HOW: Optional fields matching backend filter capabilities
 */
export interface GLEntryFilters {
  posting_date_start?: string | null
  posting_date_end?: string | null
  entry_date_start?: string | null
  entry_date_end?: string | null
  company_name?: string | null
  loan_number?: string | null
  asset_hub?: number | null
  account_number?: string | null
  cost_center?: string | null
  tag?: GLEntryTag
  bucket?: GLEntryBucket
  requires_review?: boolean | null
  search?: string | null
}

/**
 * WHAT: Chart data point for analytics
 * WHY: Type-safe chart data handling
 * HOW: Generic structure for various chart types
 */
export interface ChartDataPoint {
  label: string
  value: number
  [key: string]: any
}

// -----------------------------
// Store Definition
// -----------------------------

interface StateShape {
  // WHAT: GL entries list (lightweight)
  entries: GLEntryListItem[]
  
  // WHAT: Currently selected entry (full detail)
  currentEntry: GLEntry | null
  
  // WHAT: Summary statistics
  summary: GLEntrySummary | null
  
  // WHAT: Active filters
  filters: GLEntryFilters
  
  // WHAT: Chart data for analytics
  byTagData: ChartDataPoint[]
  byBucketData: ChartDataPoint[]
  byAccountData: ChartDataPoint[]
  monthlyTrendData: ChartDataPoint[]
  
  // WHAT: Loading states
  loadingEntries: boolean
  loadingEntry: boolean
  loadingSummary: boolean
  loadingCharts: boolean
  
  // WHAT: Pagination
  currentPage: number
  pageSize: number
  totalEntries: number
}

/**
 * WHAT: General Ledger store implementation
 * WHY: Centralized GL data management and API interactions
 * HOW: Pinia store with actions for CRUD and analytics
 */
export const useGeneralLedgerStore = defineStore('generalLedger', {
  // -----------------------------
  // State
  // -----------------------------
  state: (): StateShape => ({
    entries: [],
    currentEntry: null,
    summary: null,
    filters: {},
    byTagData: [],
    byBucketData: [],
    byAccountData: [],
    monthlyTrendData: [],
    loadingEntries: false,
    loadingEntry: false,
    loadingSummary: false,
    loadingCharts: false,
    currentPage: 1,
    pageSize: 50,
    totalEntries: 0,
  }),

  // -----------------------------
  // Getters
  // -----------------------------
  getters: {
    /**
     * WHAT: Check if any filters are active
     * WHY: Show filter status in UI
     * HOW: Check if filters object has any non-null values
     */
    hasActiveFilters: (state): boolean => {
      return Object.values(state.filters).some(v => v !== null && v !== undefined && v !== '')
    },

    /**
     * WHAT: Get entries requiring review
     * WHY: Quick access to flagged entries
     * HOW: Filter entries array
     */
    entriesRequiringReview: (state): GLEntryListItem[] => {
      return state.entries.filter(entry => entry.requires_review)
    },

    /**
     * WHAT: Get formatted summary statistics
     * WHY: Display-ready numbers for UI
     * HOW: Parse and format decimal strings
     */
    formattedSummary: (state): Record<string, string> | null => {
      if (!state.summary) return null
      
      return {
        totalEntries: state.summary.total_entries.toLocaleString(),
        totalDebits: parseFloat(state.summary.total_debits).toLocaleString('en-US', {
          style: 'currency',
          currency: 'USD'
        }),
        totalCredits: parseFloat(state.summary.total_credits).toLocaleString('en-US', {
          style: 'currency',
          currency: 'USD'
        }),
        netTotal: parseFloat(state.summary.net_total).toLocaleString('en-US', {
          style: 'currency',
          currency: 'USD'
        }),
        entriesRequiringReview: state.summary.entries_requiring_review.toLocaleString(),
      }
    },
  },

  // -----------------------------
  // Actions
  // -----------------------------
  actions: {
    /**
     * WHAT: Fetch GL entries with current filters
     * WHY: Load entries for grid display
     * HOW: GET request to /api/gl-entries/ with filters
     */
    async fetchEntries(): Promise<void> {
      this.loadingEntries = true
      try {
        // WHAT: Build query params from filters
        const params: Record<string, any> = {
          page: this.currentPage,
          page_size: this.pageSize,
          ...this.filters,
        }

        // WHAT: Make API request
        const response: AxiosResponse<{ results: GLEntryListItem[]; count: number }> = 
          await http.get('/core/gl-entries/', { params })

        // WHAT: Update state
        this.entries = response.data.results
        this.totalEntries = response.data.count
      } catch (error) {
        console.error('[GL Store] Error fetching entries:', error)
        throw error
      } finally {
        this.loadingEntries = false
      }
    },

    /**
     * WHAT: Fetch single GL entry detail
     * WHY: Load full entry data for detail view/editing
     * HOW: GET request to /api/gl-entries/{id}/
     */
    async fetchEntry(entryId: number): Promise<void> {
      this.loadingEntry = true
      try {
        const response: AxiosResponse<GLEntry> = await http.get(`/core/gl-entries/${entryId}/`)
        this.currentEntry = response.data
      } catch (error) {
        console.error('[GL Store] Error fetching entry:', error)
        throw error
      } finally {
        this.loadingEntry = false
      }
    },

    /**
     * WHAT: Fetch summary statistics
     * WHY: Update dashboard KPIs
     * HOW: GET request to /api/gl-entries/summary/ with filters
     */
    async fetchSummary(): Promise<void> {
      this.loadingSummary = true
      try {
        const params = { ...this.filters }
        const response: AxiosResponse<GLEntrySummary> = 
          await http.get('/core/gl-entries/summary/', { params })
        this.summary = response.data
      } catch (error) {
        console.error('[GL Store] Error fetching summary:', error)
        throw error
      } finally {
        this.loadingSummary = false
      }
    },

    /**
     * WHAT: Fetch all chart data for analytics
     * WHY: Update dashboard charts
     * HOW: Parallel requests to analytics endpoints
     */
    async fetchChartData(): Promise<void> {
      this.loadingCharts = true
      try {
        const params = { ...this.filters }

        // WHAT: Fetch all chart data in parallel
        const [byTagRes, byBucketRes, byAccountRes, monthlyTrendRes] = await Promise.all([
          http.get('/core/gl-entries/by-tag/', { params }),
          http.get('/core/gl-entries/by-bucket/', { params }),
          http.get('/core/gl-entries/by-account/', { params: { ...params, limit: 10 } }),
          http.get('/core/gl-entries/monthly-trend/', { params: { ...params, months: 12 } }),
        ])

        // WHAT: Update state with chart data
        this.byTagData = byTagRes.data
        this.byBucketData = byBucketRes.data
        this.byAccountData = byAccountRes.data
        this.monthlyTrendData = monthlyTrendRes.data
      } catch (error) {
        console.error('[GL Store] Error fetching chart data:', error)
        throw error
      } finally {
        this.loadingCharts = false
      }
    },

    /**
     * WHAT: Create new GL entry
     * WHY: Add entry from UI form
     * HOW: POST request to /api/gl-entries/
     */
    async createEntry(entryData: Partial<GLEntry>): Promise<GLEntry> {
      try {
        const response: AxiosResponse<GLEntry> = await http.post('/core/gl-entries/', entryData)
        // WHAT: Refresh entries list
        await this.fetchEntries()
        return response.data
      } catch (error) {
        console.error('[GL Store] Error creating entry:', error)
        throw error
      }
    },

    /**
     * WHAT: Update existing GL entry
     * WHY: Save changes from edit form
     * HOW: PATCH request to /api/gl-entries/{id}/
     */
    async updateEntry(entryId: number, entryData: Partial<GLEntry>): Promise<GLEntry> {
      try {
        const response: AxiosResponse<GLEntry> = 
          await http.patch(`/core/gl-entries/${entryId}/`, entryData)
        // WHAT: Update current entry if it's the one we just edited
        if (this.currentEntry?.id === entryId) {
          this.currentEntry = response.data
        }
        // WHAT: Refresh entries list
        await this.fetchEntries()
        return response.data
      } catch (error) {
        console.error('[GL Store] Error updating entry:', error)
        throw error
      }
    },

    /**
     * WHAT: Delete GL entry
     * WHY: Remove entry from system
     * HOW: DELETE request to /api/gl-entries/{id}/
     */
    async deleteEntry(entryId: number): Promise<void> {
      try {
        await http.delete(`/core/gl-entries/${entryId}/`)
        // WHAT: Refresh entries list
        await this.fetchEntries()
      } catch (error) {
        console.error('[GL Store] Error deleting entry:', error)
        throw error
      }
    },

    /**
     * WHAT: Flag entry for review
     * WHY: Mark entry needing attention
     * HOW: POST to /api/gl-entries/{id}/flag-for-review/
     */
    async flagForReview(entryId: number, reviewNotes?: string): Promise<void> {
      try {
        await http.post(`/core/gl-entries/${entryId}/flag-for-review/`, { review_notes: reviewNotes })
        await this.fetchEntries()
      } catch (error) {
        console.error('[GL Store] Error flagging entry:', error)
        throw error
      }
    },

    /**
     * WHAT: Clear review flag from entry
     * WHY: Mark entry as resolved
     * HOW: POST to /api/gl-entries/{id}/clear-review-flag/
     */
    async clearReviewFlag(entryId: number): Promise<void> {
      try {
        await http.post(`/core/gl-entries/${entryId}/clear-review-flag/`)
        await this.fetchEntries()
      } catch (error) {
        console.error('[GL Store] Error clearing flag:', error)
        throw error
      }
    },

    /**
     * WHAT: Set active filters
     * WHY: Update filters and trigger data refresh
     * HOW: Update filters state and fetch new data
     */
    setFilters(newFilters: GLEntryFilters): void {
      this.filters = { ...newFilters }
      this.currentPage = 1 // Reset to first page when filters change
    },

    /**
     * WHAT: Reset all filters
     * WHY: Clear filters and show all entries
     * HOW: Clear filters object and refresh data
     */
    resetFilters(): void {
      this.filters = {}
      this.currentPage = 1
    },

    /**
     * WHAT: Set pagination page
     * WHY: Navigate through paginated results
     * HOW: Update currentPage and fetch entries
     */
    setPage(page: number): void {
      this.currentPage = page
    },

    /**
     * WHAT: Refresh all dashboard data
     * WHY: Reload everything after changes
     * HOW: Fetch entries, summary, and charts in parallel
     */
    async refreshAll(): Promise<void> {
      await Promise.all([
        this.fetchEntries(),
        this.fetchSummary(),
        this.fetchChartData(),
      ])
    },
  },
})

