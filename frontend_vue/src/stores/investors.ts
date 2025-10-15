// src/stores/investors.ts
// Pinia store for listing and managing MasterCRM entries (investors).
// Uses unified MasterCRM model fields: firm, contact_name (as 'name'), email, phone, city, state
// Connected to backend API: /api/core/crm/investors/ (InvestorViewSet)

import { defineStore } from 'pinia'
import http from '@/lib/http'

// Types for MasterCRM entries (investor tag)
export interface InvestorItem {
  id: number
  firm: string | null          // Maps to MasterCRM.firm
  name: string | null          // Maps to MasterCRM.contact_name
  email: string | null         // Maps to MasterCRM.email
  phone: string | null         // Maps to MasterCRM.phone
  city: string | null          // Maps to MasterCRM.city
  states?: string[]             // New multi-select (MasterCRM.states m2m codes)
  created_at: string | null
}

export interface InvestorsState {
  results: InvestorItem[]
  count: number
  page: number
  pageSize: number
  q: string
  loading: boolean
  error: string | null
}

export const useInvestorsStore = defineStore('investors', {
  state: (): InvestorsState => ({
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
    // Fetch investors with current filters and pagination
    async fetchInvestors(params?: { page?: number; pageSize?: number; q?: string }) {
      if (params?.page !== undefined) this.page = params.page
      if (params?.pageSize !== undefined) this.pageSize = params.pageSize
      if (params?.q !== undefined) this.q = params.q

      this.loading = true
      this.error = null
      try {
        // Call the real API endpoint for investors
        // Backend automatically filters by tag='investor'
        const resp = await http.get('/core/crm/investors/', {
          params: {
            page: this.page,
            page_size: this.pageSize,
            q: this.q || undefined,
          },
        })
        
        // Map backend response to frontend format
        // Backend returns: { results: [...], count: N }
        const data = resp.data
        this.results = (data.results || []).map((item: any) => ({
          id: item.id,
          firm: item.firm,
          name: item.contact_name,  // Backend uses 'contact_name', frontend uses 'name'
          email: item.email,
          phone: item.phone,
          city: item.city,
          states: Array.isArray(item.states) ? item.states : [],
          created_at: item.created_at,
        }))
        this.count = data.count || 0
      } catch (e: any) {
        console.error('[investors] fetchInvestors failed:', e)
        this.error = e?.response?.data?.detail || 'Failed to load investors.'
        this.results = []
        this.count = 0
      } finally {
        this.loading = false
      }
    },

    // Create a new MasterCRM entry (investor)
    async createInvestor(payload: Partial<Omit<InvestorItem, 'id' | 'created_at'>>) {
      this.error = null
      try {
        // Map frontend field names to backend field names
        const backendPayload = {
          firm: payload.firm,
          contact_name: payload.name,  // Frontend 'name' -> backend 'contact_name'
          email: payload.email,
          phone: payload.phone,
          city: payload.city,
          states: payload as any && (payload as any).states ? (payload as any).states : undefined,
          // tag is automatically set to 'investor' by InvestorSerializer
        }
        
        await http.post('/core/crm/investors/', backendPayload)
        await this.fetchInvestors({ page: 1 })
        return true
      } catch (e: any) {
        console.error('[investors] createInvestor failed:', e)
        this.error = e?.response?.data?.detail || 'Failed to create investor.'
        return false
      }
    },

    // Update an existing MasterCRM entry (investor)
    async updateInvestor(id: number, payload: Partial<Omit<InvestorItem, 'id' | 'created_at'>>) {
      this.error = null
      try {
        // Map frontend field names to backend field names
        const backendPayload = {
          firm: payload.firm,
          contact_name: payload.name,  // Frontend 'name' -> backend 'contact_name'
          email: payload.email,
          phone: payload.phone,
          city: payload.city,
          states: (payload as any).states,
        }
        
        await http.patch(`/core/crm/investors/${id}/`, backendPayload)
        await this.fetchInvestors({ page: this.page })
        return true
      } catch (e: any) {
        console.error('[investors] updateInvestor failed:', e)
        this.error = e?.response?.data?.detail || 'Failed to update investor.'
        return false
      }
    },
  },
})
