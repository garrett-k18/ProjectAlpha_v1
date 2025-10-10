// src/stores/legal.ts
// Pinia store for listing and managing MasterCRM entries (legal contacts).
// Uses unified MasterCRM model fields: firm, contact_name (as 'name'), email, phone, city, state
// Connected to backend API: /api/core/crm/legal/ (LegalViewSet)

import { defineStore } from 'pinia'
import http from '@/lib/http'

// Types for MasterCRM entries (legal tag)
export interface LegalItem {
  id: number
  firm: string | null          // Maps to MasterCRM.firm
  name: string | null          // Maps to MasterCRM.contact_name
  email: string | null         // Maps to MasterCRM.email
  phone: string | null         // Maps to MasterCRM.phone
  city: string | null          // Maps to MasterCRM.city
  state: string | null         // Maps to MasterCRM.state
  created_at: string | null
}

export interface LegalState {
  results: LegalItem[]
  count: number
  page: number
  pageSize: number
  q: string
  loading: boolean
  error: string | null
}

export const useLegalStore = defineStore('legal', {
  state: (): LegalState => ({
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
    // Fetch legal contacts with current filters and pagination
    async fetchLegal(params?: { page?: number; pageSize?: number; q?: string }) {
      if (params?.page !== undefined) this.page = params.page
      if (params?.pageSize !== undefined) this.pageSize = params.pageSize
      if (params?.q !== undefined) this.q = params.q

      this.loading = true
      this.error = null
      try {
        // Call the real API endpoint for legal contacts
        // Backend automatically filters by tag='legal'
        const resp = await http.get('/core/crm/legal/', {
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
          state: item.state,
          created_at: item.created_at,
        }))
        this.count = data.count || 0
      } catch (e: any) {
        console.error('[legal] fetchLegal failed:', e)
        this.error = e?.response?.data?.detail || 'Failed to load legal contacts.'
        this.results = []
        this.count = 0
      } finally {
        this.loading = false
      }
    },

    // Create a new MasterCRM entry (legal)
    async createLegal(payload: Partial<Omit<LegalItem, 'id' | 'created_at'>>) {
      this.error = null
      try {
        // Map frontend field names to backend field names
        const backendPayload = {
          firm: payload.firm,
          contact_name: payload.name,  // Frontend 'name' -> backend 'contact_name'
          email: payload.email,
          phone: payload.phone,
          city: payload.city,
          state: payload.state,
          // tag is automatically set to 'legal' by LegalSerializer
        }
        
        await http.post('/core/crm/legal/', backendPayload)
        await this.fetchLegal({ page: 1 })
        return true
      } catch (e: any) {
        console.error('[legal] createLegal failed:', e)
        this.error = e?.response?.data?.detail || 'Failed to create legal contact.'
        return false
      }
    },

    // Update an existing MasterCRM entry (legal)
    async updateLegal(id: number, payload: Partial<Omit<LegalItem, 'id' | 'created_at'>>) {
      this.error = null
      try {
        // Map frontend field names to backend field names
        const backendPayload = {
          firm: payload.firm,
          contact_name: payload.name,  // Frontend 'name' -> backend 'contact_name'
          email: payload.email,
          phone: payload.phone,
          city: payload.city,
          state: payload.state,
        }
        
        await http.patch(`/core/crm/legal/${id}/`, backendPayload)
        await this.fetchLegal({ page: this.page })
        return true
      } catch (e: any) {
        console.error('[legal] updateLegal failed:', e)
        this.error = e?.response?.data?.detail || 'Failed to update legal contact.'
        return false
      }
    },
  },
})
