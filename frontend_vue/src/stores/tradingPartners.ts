// src/stores/tradingPartners.ts
// Pinia store for listing and managing TradingPartnerCRM directory entries.
// Docs reviewed:
// - Pinia: https://pinia.vuejs.org/core-concepts/
// - Axios Instances: https://axios-http.com/docs/instance
// - DRF list endpoints: expect { count, page, page_size, results }

import { defineStore } from 'pinia'
import http from '@/lib/http'

// Types for TradingPartnerCRM list entries returned by the API
export interface TradingPartnerItem {
  id: number
  firm: string
  name: string | null
  email: string | null
  phone: string | null
  altname: string | null
  altemail: string | null
  alt_phone: string | null
  nda_flag: boolean
  nda_signed: string | null // ISO date string YYYY-MM-DD
  created_at: string | null // ISO8601 datetime string
}

export interface TradingPartnersState {
  results: TradingPartnerItem[]
  count: number
  page: number
  pageSize: number
  q: string
  loading: boolean
  error: string | null
}

export const useTradingPartnersStore = defineStore('tradingPartners', {
  state: (): TradingPartnersState => ({
    results: [],
    count: 0,
    page: 1,
    pageSize: 25,
    q: '',
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
    // Fetch trading partners with current filters and pagination
    async fetchPartners(params?: { page?: number; pageSize?: number; q?: string }) {
      if (params?.page !== undefined) this.page = params.page
      if (params?.pageSize !== undefined) this.pageSize = params.pageSize
      if (params?.q !== undefined) this.q = params.q

      this.loading = true
      this.error = null
      try {
        const resp = await http.get('/acq/trading-partners/', {
          params: {
            page: this.page,
            page_size: this.pageSize,
            q: this.q || undefined,
          },
        })
        const data = resp.data as { count: number; page: number; page_size: number; results: TradingPartnerItem[] }
        this.count = data.count
        this.page = data.page
        this.pageSize = data.page_size
        this.results = Array.isArray(data.results) ? data.results : []
      } catch (e: any) {
        console.error('[tradingPartners] fetchPartners failed:', e)
        this.error = e?.response?.data?.detail || 'Failed to load trading partners.'
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
      await this.fetchPartners({ page: 1 })
    },

    // Create a new TradingPartnerCRM entry via POST /acq/trading-partners/
    async createPartner(payload: Partial<Omit<TradingPartnerItem, 'id' | 'created_at'>>) {
      this.error = null
      try {
        await http.post('/acq/trading-partners/', payload)
        await this.fetchPartners({ page: 1 })
        return true
      } catch (e: any) {
        console.error('[tradingPartners] createPartner failed:', e)
        // Try to surface serializer errors if present
        this.error = e?.response?.data?.detail || 'Failed to create trading partner.'
        return false
      }
    },

    // Update an existing TradingPartnerCRM entry via PATCH /acq/trading-partners/:id/
    async updatePartner(id: number, payload: Partial<Omit<TradingPartnerItem, 'id' | 'created_at'>>) {
      this.error = null
      try {
        await http.patch(`/acq/trading-partners/${id}/`, payload)
        await this.fetchPartners({ page: this.page })
        return true
      } catch (e: any) {
        console.error('[tradingPartners] updatePartner failed:', e)
        this.error = e?.response?.data?.detail || 'Failed to update trading partner.'
        return false
      }
    },
  },
})
