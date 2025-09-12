// src/stores/brokerscrm.ts
// Pinia store for listing Brokercrm directory entries from the backend API.
// Docs reviewed:
// - Pinia: https://pinia.vuejs.org/core-concepts/
// - Axios Instances: https://axios-http.com/docs/instance
// - DRF list endpoint shape implemented at /api/acq/brokers/

import { defineStore } from 'pinia'
import http from '@/lib/http'

// Types for the Brokercrm list entries returned by the API
export interface BrokerCrmItem {
  id: number
  broker_name: string | null
  broker_email: string | null
  broker_phone: string | null
  broker_firm: string | null
  broker_city: string | null
  broker_state: string | null
  created_at: string | null // ISO8601 string
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
        const resp = await http.get('/acq/brokers/', {
          params: {
            page: this.page,
            page_size: this.pageSize,
            q: this.q || undefined,
            state: this.stateFilter || undefined,
          },
        })
        // Expected response shape: { count, page, page_size, results }
        const data = resp.data as { count: number; page: number; page_size: number; results: BrokerCrmItem[] }
        this.count = data.count
        this.page = data.page
        this.pageSize = data.page_size
        this.results = Array.isArray(data.results) ? data.results : []
      } catch (e: any) {
        // Provide a user-friendly error message while keeping console details
        console.error('[brokerscrm] fetchBrokers failed:', e)
        this.error = e?.response?.data?.detail || 'Failed to load brokers.'
        this.results = []
        this.count = 0
      } finally {
        this.loading = false
      }
    },

    // Convenience method to clear filters and reload first page
    async resetAndFetch() {
      this.page = 1
      this.q = ''
      this.stateFilter = ''
      await this.fetchBrokers({ page: 1 })
    },

    // Create a new Brokercrm entry via POST /acq/brokers/
    // Accepts partial fields; server handles normalization of state and timestamps.
    async createBroker(payload: {
      broker_name?: string | null
      broker_email?: string | null
      broker_firm?: string | null
      broker_city?: string | null
      broker_state?: string | null
    }) {
      this.error = null
      try {
        // POST to create; returns created broker item
        await http.post('/acq/brokers/', payload)
        // After creation, refresh the first page so the new record appears
        await this.fetchBrokers({ page: 1 })
        return true
      } catch (e: any) {
        console.error('[brokerscrm] createBroker failed:', e)
        this.error = e?.response?.data?.detail || 'Failed to create broker.'
        return false
      }
    },

    // Update an existing Brokercrm entry via PATCH /acq/brokers/:id/
    // Accepts partial fields to update only what changed.
    async updateBroker(id: number, payload: {
      broker_name?: string | null
      broker_email?: string | null
      broker_phone?: string | null
      broker_firm?: string | null
      broker_city?: string | null
      broker_state?: string | null
    }) {
      this.error = null
      try {
        await http.patch(`/acq/brokers/${id}/`, payload)
        // Refresh current page to reflect changes inline
        await this.fetchBrokers({ page: this.page })
        return true
      } catch (e: any) {
        console.error('[brokerscrm] updateBroker failed:', e)
        this.error = e?.response?.data?.detail || 'Failed to update broker.'
        return false
      }
    },
  },
})
