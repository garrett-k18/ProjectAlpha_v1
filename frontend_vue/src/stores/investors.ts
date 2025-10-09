// src/stores/investors.ts
// Pinia store for listing and managing MasterCRM entries (investors).
// Uses unified MasterCRM model fields: firm, contact_name (as 'name'), email, phone, city, state
// TODO: Connect to backend API endpoint when available

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
  state: string | null         // Maps to MasterCRM.state
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
        // TODO: Replace with actual API endpoint when backend is ready
        // const resp = await http.get('/acq/investors/', {
        //   params: {
        //     page: this.page,
        //     page_size: this.pageSize,
        //     q: this.q || undefined,
        //     tag: 'investor',  // Only fetch investor-tagged MasterCRM entries
        //   },
        // })
        
        // Mock data for now - replace with actual API call
        await new Promise(resolve => setTimeout(resolve, 500))
        this.results = [
          {
            id: 1,
            firm: 'Alpha Capital',
            name: 'Sarah Johnson',
            email: 'sarah@alphacapital.com',
            phone: '5551234567',
            city: 'New York',
            state: 'NY',
            created_at: new Date().toISOString(),
          },
          {
            id: 2,
            firm: 'Beta Ventures',
            name: 'Michael Chen',
            email: 'mchen@betaventures.com',
            phone: '5559876543',
            city: 'San Francisco',
            state: 'CA',
            created_at: new Date().toISOString(),
          },
        ]
        this.count = 2
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
        // TODO: Replace with actual API call
        // await http.post('/acq/investors/', payload)
        console.log('Create investor:', payload)
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
        // TODO: Replace with actual API call
        // await http.patch(`/acq/investors/${id}/`, payload)
        console.log('Update investor:', id, payload)
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
