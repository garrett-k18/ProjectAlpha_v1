/*
Pinia store for Broker detail and assigned loans.

Docs reviewed:
- Pinia: https://pinia.vuejs.org/core-concepts/
- Axios instance usage (local): src/lib/http.ts
- Vue reactivity + TypeScript stores: https://pinia.vuejs.org/cookbook/typescript.html

This store centralizes fetching and caching for:
- GET /api/acq/brokers/:brokerId/
- GET /api/acq/brokers/:brokerId/assigned-loans/
*/
import { defineStore } from 'pinia'
import http from '@/lib/http'

// -----------------------------
// Type Definitions (Interfaces)
// -----------------------------
export interface BrokerStats {
  // total count of invites created targeting this broker
  total_invites: number
  // count of unique loans assigned to this broker via tokens
  assigned_loan_count: number
  // count of unique loans where BrokerValues exists
  submissions_count: number
}

export interface BrokerDetail {
  // primary key id for Brokercrm record
  id: number
  // display name of the broker (may be null)
  broker_name: string | null
  // email address for the broker (may be null)
  broker_email: string | null
  // firm/company name (may be null)
  broker_firm: string | null
  // city portion of location (may be null)
  broker_city: string | null
  // 2-letter state code (may be null)
  broker_state: string | null
  // stats block for quick UI headers
  stats: BrokerStats
}

export interface AssignedLoanTokenInfo {
  // raw token value (opaque string) used in public URL
  value: string
  // ISO string expiration timestamp, or null if missing
  expires_at: string | null
  // true if single-use locked on first submit
  single_use: boolean
  // ISO string of when first used, or null
  used_at: string | null
  // backend computed flag: is expired
  is_expired: boolean
  // backend computed flag: has been used at least once
  is_used: boolean
}

export interface AssignedLoanEntry {
  // SellerRawData primary key id
  seller_raw_data: number
  // Related seller info (minimal for UI linking)
  seller: { id: number | null, name: string | null }
  // Related trade info (minimal for UI linking)
  trade: { id: number | null, name: string | null }
  // Address context for the asset
  address: {
    street_address: string | null
    city: string | null
    state: string | null
    zip: string | null
  }
  // Snapshot financial field exposed by the API (stringified decimal or null)
  current_balance: string | null
  // Token information for the most recent invite related to this broker+loan
  token: AssignedLoanTokenInfo
  // whether any BrokerValues exist for this SRD
  has_submission: boolean
}

interface StateShape {
  // cache map of broker details by id
  brokerById: Record<number, BrokerDetail>
  // cache map of assigned loans arrays by broker id
  assignedByBrokerId: Record<number, AssignedLoanEntry[]>
  // separate loading flags for detail and assigned lists keyed by broker id
  loadingDetail: Record<number, boolean>
  loadingAssigned: Record<number, boolean>
  // optional error strings keyed by broker id
  errorDetail: Record<number, string | null>
  errorAssigned: Record<number, string | null>
}

export const useBrokerLoansStore = defineStore('brokerLoans', {
  // -----------------------------
  // State
  // -----------------------------
  state: (): StateShape => ({
    brokerById: {},        // holds BrokerDetail by id
    assignedByBrokerId: {},// holds AssignedLoanEntry[] by broker id
    loadingDetail: {},     // loading flags for broker detail fetches
    loadingAssigned: {},   // loading flags for assigned loans fetches
    errorDetail: {},       // error messages for detail requests
    errorAssigned: {},     // error messages for assigned requests
  }),

  // -----------------------------
  // Getters (optional)
  // -----------------------------
  getters: {
    // retrieve a broker detail safely
    getBroker: (state) => (brokerId: number): BrokerDetail | undefined => state.brokerById[brokerId],
    // retrieve assigned loans safely
    getAssignedLoans: (state) => (brokerId: number): AssignedLoanEntry[] => state.assignedByBrokerId[brokerId] ?? [],
    // combine loading flags for simpler UI
    isLoadingAny: (state) => (brokerId: number): boolean => !!state.loadingDetail[brokerId] || !!state.loadingAssigned[brokerId],
  },

  // -----------------------------
  // Actions
  // -----------------------------
  actions: {
    // Fetch broker detail; cache by broker id; optionally force refresh
    async fetchBrokerDetail(brokerId: number, force = false): Promise<BrokerDetail> {
      // if cached and not forced, return cache
      if (!force && this.brokerById[brokerId]) return this.brokerById[brokerId]
      // set loading true while request is in-flight
      this.loadingDetail[brokerId] = true
      this.errorDetail[brokerId] = null
      try {
        // perform GET request against backend API
        const res = await http.get<BrokerDetail>(`/api/acq/brokers/${brokerId}/`)
        // store result in cache map
        this.brokerById[brokerId] = res.data
        return res.data
      } catch (err: any) {
        // capture best-effort error message for UI display
        const msg = err?.response?.data?.detail || err?.message || 'Failed to load broker detail'
        this.errorDetail[brokerId] = msg
        throw err
      } finally {
        // always clear loading flag when finished
        this.loadingDetail[brokerId] = false
      }
    },

    // Fetch assigned loans; cache by broker id; optionally force refresh
    async fetchAssignedLoans(brokerId: number, force = false): Promise<AssignedLoanEntry[]> {
      // if cached and not forced, return cache
      if (!force && this.assignedByBrokerId[brokerId]) return this.assignedByBrokerId[brokerId]
      // set loading true while request is in-flight
      this.loadingAssigned[brokerId] = true
      this.errorAssigned[brokerId] = null
      try {
        // perform GET request against backend API
        const res = await http.get<{ results: AssignedLoanEntry[] }>(`/api/acq/brokers/${brokerId}/assigned-loans/`)
        // store results list in cache map
        this.assignedByBrokerId[brokerId] = res.data.results
        return res.data.results
      } catch (err: any) {
        // capture best-effort error message for UI display
        const msg = err?.response?.data?.detail || err?.message || 'Failed to load assigned loans'
        this.errorAssigned[brokerId] = msg
        throw err
      } finally {
        // always clear loading flag when finished
        this.loadingAssigned[brokerId] = false
      }
    },

    // Simple API to reset cached records for a broker id
    reset(brokerId: number): void {
      // delete cached detail and list to force refresh next time
      delete this.brokerById[brokerId]
      delete this.assignedByBrokerId[brokerId]
      delete this.loadingDetail[brokerId]
      delete this.loadingAssigned[brokerId]
      delete this.errorDetail[brokerId]
      delete this.errorAssigned[brokerId]
    },

    // Clear the entire cache (use with care)
    clearAll(): void {
      // reset to initial state
      this.brokerById = {}
      this.assignedByBrokerId = {}
      this.loadingDetail = {}
      this.loadingAssigned = {}
      this.errorDetail = {}
      this.errorAssigned = {}
    },
  },
})
