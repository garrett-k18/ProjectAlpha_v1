// src/stores/brokerscrm.ts
// Pinia store for broker CRM data using the clean /brokers/ API
// Uses simple BrokerCRMSerializer with minimal fields
// Docs reviewed:
// - Pinia: https://pinia.vuejs.org/core-concepts/
// - Clean API endpoint: /api/core/brokers/ (no pagination)

import { defineStore } from 'pinia'
import http from '@/lib/http'

// Types for MasterCRM entries returned by the API (broker tag)
export interface BrokerCrmItem {
  id: number
  name: string | null              // Maps to MasterCRM.contact_name
  contact_name: string | null      // Direct field mapping
  email: string | null             // Maps to MasterCRM.email
  phone: string | null             // Maps to MasterCRM.phone
  firm: string | null              // Maps to MasterCRM.firm property
  firm_ref?: {                     // FK relationship details
    id: number
    name: string
    phone: string | null
    email: string | null
    states: string[]
  } | null
  city: string | null              // Maps to MasterCRM.city (legacy)
  states?: string[]                // Multi-select (MasterCRM.states m2m codes)
  msas?: string[]                  // MSA names array (new structure)
  msa_assignments?: Array<{        // Full MSA assignment details
    id: number
    msa_id: number
    msa_name: string
    msa_code: string
    priority: number
    is_active: boolean
    notes: string | null
  }>
  preferred?: string               // Yes/No/blank
  tag?: string                     // Contact type tag
  tag_display?: string             // Human-readable tag
  created_at: string | null        // ISO8601 string
  updated_at: string | null        // ISO8601 string
}

export interface BrokersCrmState {
  results: BrokerCrmItem[]
  count: number
  page: number
  pageSize: number
  q: string
  stateFilter: string
  loading: boolean
  error: string | null
}

export const useBrokersCrmStore = defineStore('brokerscrm', {
  // State is kept minimal and serializable for easy debugging and caching
  state: (): BrokersCrmState => ({
    results: [],
    count: 0,
    page: 1,
    pageSize: 25,
    q: '',
    stateFilter: '',
    loading: false,
    error: null,
  }),

  getters: {
    // Total number of pages computed from count and pageSize
    totalPages(state): number {
      return state.pageSize > 0 ? Math.ceil(state.count / state.pageSize) : 0
    },
  },

  actions: {
    // Fetch brokers with current filters and pagination
    async fetchBrokers(params?: { page?: number; pageSize?: number; q?: string; state?: string }) {
      // Merge provided params into state before making request
      if (params?.page !== undefined) this.page = params.page
      if (params?.pageSize !== undefined) this.pageSize = params.pageSize
      if (params?.q !== undefined) this.q = params.q
      if (params?.state !== undefined) this.stateFilter = params.state

      this.loading = true
      this.error = null
      
      try {
        // Progressive loading strategy: Load first page immediately, then background load rest
        const firstPageResp = await http.get('/core/brokers/', {
          params: {
            page: 1,
            page_size: 100, // Large first page
            search: this.q || undefined,
            state: this.stateFilter || undefined,
          },
        })
        
        const firstPageData = firstPageResp.data
        if (!firstPageData.results || !Array.isArray(firstPageData.results)) {
          throw new Error('Invalid API response format')
        }
        
        // Show first page immediately
        this.results = firstPageData.results
        this.count = firstPageData.count || 0
        this.page = 1
        this.pageSize = firstPageData.results.length
        this.loading = false // Show first page while loading rest
        
        console.log(`✅ Loaded first ${this.results.length} brokers, total: ${this.count}`)
        
        // Background load remaining pages if there are more
        if (firstPageData.next && this.count > 100) {
          this.loadRemainingPages(firstPageData.count)
        }
        
      } catch (e: any) {
        console.error('[brokerscrm] fetchBrokers failed:', e)
        this.error = e?.response?.data?.detail || 'Failed to load brokers.'
        this.results = []
        this.count = 0
        this.loading = false
      }
    },
    
    async loadRemainingPages(totalCount: number) {
      try {
        const totalPages = Math.ceil(totalCount / 100)
        const remainingPages = []
        
        // Load remaining pages in parallel (but limit concurrency)
        for (let page = 2; page <= Math.min(totalPages, 5); page++) { // Max 5 pages total (500 brokers)
          remainingPages.push(
            http.get('/core/brokers/', {
              params: {
                page,
                page_size: 100,
                search: this.q || undefined,
                state: this.stateFilter || undefined,
              },
            })
          )
        }
        
        if (remainingPages.length > 0) {
          const responses = await Promise.all(remainingPages)
          
          // Append all results
          for (const resp of responses) {
            if (resp.data.results && Array.isArray(resp.data.results)) {
              this.results = this.results.concat(resp.data.results)
            }
          }
          
          this.pageSize = this.results.length
          console.log(`✅ Background loaded total ${this.results.length} brokers`)
        }
        
      } catch (e: any) {
        console.warn('Background loading failed:', e)
        // Don't show error for background loading - first page already loaded
      }
    },
    
    // Convenience method to clear filters and reload first page
    async resetAndFetch() {
      this.page = 1
      this.q = ''
      this.stateFilter = ''
      await this.fetchBrokers({ page: 1 })
    },

    // Create a new broker via POST /core/brokers/
    async createBroker(payload: {
      name?: string | null
      email?: string | null
      firm?: string | null
      city?: string | null
      states?: string[]
      msas?: string[]
      phone?: string | null
    }): Promise<BrokerCrmItem> {
      try {
        const resp = await http.post('/core/brokers/', payload)
        const newBroker = resp.data as BrokerCrmItem
        // Add to local state
        this.results.unshift(newBroker)
        this.count += 1
        return newBroker
      } catch (e: any) {
        console.error('[brokerscrm] createBroker failed:', e)
        throw new Error(e?.response?.data?.detail || 'Failed to create broker.')
      }
    },

    // Update an existing broker via PATCH /core/brokers/:id/
    async updateBroker(id: number, payload: {
      name?: string | null
      email?: string | null
      phone?: string | null
      firm?: string | null
      city?: string | null
      states?: string[]
      msas?: string[]
    }) {
      this.error = null
      console.log(`🔄 Updating broker ${id} (no loading state, no reload)`)
      
      try {
        const response = await http.patch(`/core/brokers/${id}/`, payload)
        const updatedBroker = response.data
        
        // Update the specific record in place instead of refetching all data
        const index = this.results.findIndex(broker => broker.id === id)
        if (index !== -1) {
          this.results[index] = { ...this.results[index], ...updatedBroker }
          console.log(`✅ Updated broker ${id} in place at index ${index}`)
        } else {
          console.warn(`⚠️ Broker ${id} not found in current results`)
        }
        
        return true
      } catch (e: any) {
        console.error('[brokerscrm] updateBroker failed:', e)
        this.error = e?.response?.data?.detail || 'Failed to update broker.'
        return false
      }
    },
  },
})
