/*
Pinia store for AM Outcomes (DIL first pass) and their Tasks.

Docs reviewed:
- Pinia core concepts: https://pinia.vuejs.org/core-concepts/
- Axios instance reuse: src/lib/http.ts
- DRF endpoints implemented in am_module: /api/am/outcomes/*

Design:
- Cache outcome records by assetHubId to avoid duplicate network round-trips
- Idempotent ensure-create: POST /am/outcomes/dil/ with asset_hub_id returns existing or creates new
- Tasks keyed by assetHubId; DIL primary key equals assetHubId (OneToOne PK)
*/

import { defineStore } from 'pinia'
import http from '@/lib/http'

// -----------------------------
// Type Definitions
// -----------------------------
export type DilTaskType = 'owner_contacted' | 'no_cooperation' | 'dil_drafted' | 'dil_executed'

// Allow a generic start for any outcome
export type OutcomeType = 'dil' | 'fc' | 'reo' | 'short_sale' | 'modification'
const outcomePath: Record<OutcomeType, string> = {
  dil: 'dil',
  fc: 'fc',
  reo: 'reo',
  short_sale: 'short-sale',
  modification: 'modification',
}

// FC Task support
export type FcTaskType = 'nod_noi' | 'fc_filing' | 'mediation' | 'judgement' | 'redemption' | 'sale_scheduled' | 'sold'
export interface FcTask {
  id: number
  asset_hub: number
  fc_sale: number
  task_type: FcTaskType
  task_started: string | null
  nod_noi_sent_date?: string | null
  nod_noi_expire_date?: string | null
  created_at: string
  updated_at: string
}

// Short Sale Task support
export type ShortSaleTaskType = 'list_price_accepted' | 'listed' | 'under_contract' | 'sold'
export interface ShortSaleTask {
  id: number
  asset_hub: number
  short_sale: number
  task_type: ShortSaleTaskType
  task_started: string | null
  created_at: string
  updated_at: string
}

// Modification Task support
export type ModificationTaskType = 'mod_drafted' | 'mod_executed' | 'mod_rpl' | 'mod_failed'
export interface ModificationTask {
  id: number
  asset_hub: number
  modification: number
  task_type: ModificationTaskType
  task_started: string | null
  created_at: string
  updated_at: string
}

export interface Dil {
  // hub-owned PK; serializer returns foreign key field name
  asset_hub: number
  // nullable relationships
  crm: number | null
  // business fields (stringified decimals/dates from DRF)
  dil_completion_date: string | null
  dil_cost: string | null
  cfk_cost: string | null
}

// CRM contact details
export interface CrmContact {
  id: number
  contact_name: string | null
  firm: string | null
  email: string | null
  phone: string | null
  tag: string | null
}

// FC outcome interface aligns to FCSale model in backend
export interface FcSale {
  asset_hub: number
  crm: number | null
  crm_details: CrmContact | null
  fc_sale_sched_date: string | null
  fc_sale_actual_date: string | null
  fc_bid_price: string | null
  fc_sale_price: string | null
}

// REOData interface
export interface ReoData {
  asset_hub: number
  crm: number | null
  list_price: string | null
  list_date: string | null
  under_contract_flag: boolean
  under_contract_date: string | null
  contract_price: string | null
  estimated_close_date: string | null
  actual_close_date: string | null
  seller_credit_amt: string | null
  purchase_type: 'cash' | 'financing' | 'seller_financing' | null
  gross_purchase_price: string | null
}

// Short Sale interface
export interface ShortSaleOutcome {
  asset_hub: number
  crm: number | null
  acceptable_min_offer: string | null
  short_sale_date: string | null
}

// Modification interface
export interface ModificationOutcome {
  asset_hub: number
  crm: number | null
  modification_date: string | null
  modification_cost: string | null
  modification_upb: string | null
  modification_term: number | null
  modification_rate: string | null
  modification_maturity_date: string | null
  modification_pi: 'pi' | 'io' | 'other' | null
  modification_down_payment: string | null
}

export interface DilTask {
  id: number
  asset_hub: number
  // Parent DIL PK equals hub id
  dil: number
  task_type: DilTaskType
  task_started: string | null
  created_at: string
  updated_at: string
}

// REO Task support
export type ReoTaskType = 'eviction' | 'trashout' | 'renovation' | 'marketing' | 'under_contract' | 'sold'
export interface ReoTask {
  id: number
  asset_hub: number
  reo_outcome: number
  task_type: ReoTaskType
  task_started: string | null
  created_at: string
  updated_at: string
}

// REO Scope support
export type ReoScopeKind = 'trashout' | 'renovation'
export interface ReoScope {
  id: number
  asset_hub: number
  crm: number | null
  scope_kind: ReoScopeKind | null
  reo_task: number | null
  scope_date: string | null
  total_cost: string | null
  expected_completion: string | null
  notes: string | null
  created_at: string
  updated_at: string
}

interface StateShape {
  // outcomes by hub id
  dilByHub: Record<number, Dil | null>
  reoByHub: Record<number, ReoData | null>
  fcByHub: Record<number, FcSale | null>
  shortSaleByHub: Record<number, ShortSaleOutcome | null>
  modificationByHub: Record<number, ModificationOutcome | null>
  // tasks by hub id
  dilTasksByHub: Record<number, DilTask[]>
  // REO tasks by hub id
  reoTasksByHub: Record<number, ReoTask[]>
  // FC tasks by hub id
  fcTasksByHub: Record<number, FcTask[]>
  // Short Sale tasks by hub id
  shortSaleTasksByHub: Record<number, ShortSaleTask[]>
  // Modification tasks by hub id
  modificationTasksByHub: Record<number, ModificationTask[]>
  // loading + error per hub for fine-grained UI control
  loadingDil: Record<number, boolean>
  loadingDilTasks: Record<number, boolean>
  loadingReoTasks: Record<number, boolean>
  loadingFcTasks: Record<number, boolean>
  loadingShortSaleTasks: Record<number, boolean>
  loadingModificationTasks: Record<number, boolean>
  errorDil: Record<number, string | null>
  errorDilTasks: Record<number, string | null>
  errorReoTasks: Record<number, string | null>
  errorFcTasks: Record<number, string | null>
  errorShortSaleTasks: Record<number, string | null>
  errorModificationTasks: Record<number, string | null>
}

export const useAmOutcomesStore = defineStore('amOutcomes', {
  state: (): StateShape => ({
    dilByHub: {},
    reoByHub: {},
    fcByHub: {},
    shortSaleByHub: {},
    modificationByHub: {},
    dilTasksByHub: {},
    reoTasksByHub: {},
    fcTasksByHub: {},
    shortSaleTasksByHub: {},
    modificationTasksByHub: {},
    loadingDil: {},
    loadingDilTasks: {},
    loadingReoTasks: {},
    loadingFcTasks: {},
    loadingShortSaleTasks: {},
    loadingModificationTasks: {},
    errorDil: {},
    errorDilTasks: {},
    errorReoTasks: {},
    errorFcTasks: {},
    errorShortSaleTasks: {},
    errorModificationTasks: {},
    // dynamic extension: attach caches for other outcomes
    // REO scopes cache keyed by `${hubId}:${taskId || 0}:${scopeKind || ''}`
    // Keep loading and error maps with same key
  }),

  getters: {
    getDil: (state) => (hubId: number) => state.dilByHub[hubId] ?? null,
    getDilTasks: (state) => (hubId: number) => state.dilTasksByHub[hubId] ?? [],
    getReo: (state) => (hubId: number) => state.reoByHub[hubId] ?? null,
    getReoTasks: (state) => (hubId: number) => state.reoTasksByHub[hubId] ?? [],
    isDilLoading: (state) => (hubId: number) => !!state.loadingDil[hubId],
    isDilTasksLoading: (state) => (hubId: number) => !!state.loadingDilTasks[hubId],
  },

  actions: {
    // Generic ensure-create for any outcome. Returns the outcome payload (shape varies per outcome).
    // WHAT: Creates a new outcome record if it doesn't exist
    // WHY: Called when user selects a track from the dropdown
    // HOW: POSTs to backend and caches the created outcome in store
    async ensureOutcome(hubId: number, type: OutcomeType): Promise<any> {
      const path = outcomePath[type]
      const url = `/am/outcomes/${path}/`
      const res = await http.post(url, { asset_hub_id: hubId })
      // Cache the created outcome in the appropriate store property
      if (type === 'dil') this.dilByHub[hubId] = res.data as Dil
      else if (type === 'fc') this.fcByHub[hubId] = res.data as FcSale
      else if (type === 'reo') this.reoByHub[hubId] = res.data as ReoData
      else if (type === 'short_sale') this.shortSaleByHub[hubId] = res.data as ShortSaleOutcome
      else if (type === 'modification') this.modificationByHub[hubId] = res.data as ModificationOutcome
      return res.data
    },

    // -----------------------------
    // REO Scopes helpers
    // -----------------------------
    async listReoScopes(
      hubId: number,
      params: { scopeKind?: ReoScopeKind; reoTaskId?: number },
      force = true,
    ): Promise<ReoScope[]> {
      const key = `${hubId}:${params.reoTaskId ?? 0}:${params.scopeKind ?? ''}`
      // Lazy init maps on first use
      // @ts-ignore add dynamic maps on store instance
      this.reoScopesByKey = this.reoScopesByKey || {}
      // @ts-ignore
      this.loadingReoScopes = this.loadingReoScopes || {}
      // @ts-ignore
      this.errorReoScopes = this.errorReoScopes || {}
      // Return cache if present and not forcing
      // @ts-ignore
      if (!force && this.reoScopesByKey[key] !== undefined) return this.reoScopesByKey[key]
      try {
        // @ts-ignore
        this.loadingReoScopes[key] = true
        // @ts-ignore
        this.errorReoScopes[key] = null
        const res = await http.get<ReoScope[]>('/am/outcomes/reo-scopes/', {
          params: {
            asset_hub_id: hubId,
            scope_kind: params.scopeKind,
            reo_task: params.reoTaskId,
          },
        })
        const items = Array.isArray(res.data) ? res.data : []
        // @ts-ignore
        this.reoScopesByKey[key] = items
        return items
      } catch (err: any) {
        const msg = err?.response?.data?.detail || err?.message || 'Failed to load REO scopes'
        // @ts-ignore
        this.errorReoScopes[key] = msg
        throw err
      } finally {
        // @ts-ignore
        this.loadingReoScopes[key] = false
      }
    },

    async createReoScope(payload: Partial<ReoScope> & { asset_hub_id: number }): Promise<ReoScope> {
      const res = await http.post<ReoScope>('/am/outcomes/reo-scopes/', payload)
      return res.data
    },

    // -----------------------------
    // REO Tasks helpers
    // -----------------------------
    async listReoTasks(hubId: number, force = false): Promise<ReoTask[]> {
      if (!force && this.reoTasksByHub[hubId] !== undefined) return this.reoTasksByHub[hubId]
      try {
        this.loadingReoTasks[hubId] = true
        this.errorReoTasks[hubId] = null
        const res = await http.get<ReoTask[]>('/am/outcomes/reo-tasks/', { params: { asset_hub_id: hubId } })
        const items = Array.isArray(res.data) ? res.data : []
        // Sort newest first (created_at desc); fallback to id desc
        const itemsSorted = [...items].sort((a, b) => {
          const aT = Date.parse(a.created_at)
          const bT = Date.parse(b.created_at)
          if (!isNaN(aT) && !isNaN(bT)) return bT - aT
          return (b.id ?? 0) - (a.id ?? 0)
        })
        this.reoTasksByHub[hubId] = itemsSorted
        return itemsSorted
      } catch (err: any) {
        const msg = err?.response?.data?.detail || err?.message || 'Failed to load REO tasks'
        this.errorReoTasks[hubId] = msg
        throw err
      } finally {
        this.loadingReoTasks[hubId] = false
      }
    },

    // Update DIL fields (e.g., cfk_cost, dil_cost). Also updates local cache.
    async patchDil(hubId: number, payload: Partial<Dil>): Promise<Dil> {
      const res = await http.patch<Dil>(`/am/outcomes/dil/${hubId}/`, payload)
      this.dilByHub[hubId] = res.data
      return res.data
    },
    async createReoTask(hubId: number, taskType: ReoTaskType): Promise<ReoTask> {
      try {
        this.loadingReoTasks[hubId] = true
        this.errorReoTasks[hubId] = null
        // Ensure parent REO outcome exists (idempotent on backend)
        await this.ensureOutcome(hubId, 'reo')
        // REOData uses hub-owned PK, so reo_outcome equals hubId
        const res = await http.post<ReoTask>('/am/outcomes/reo-tasks/', {
          asset_hub_id: hubId,
          reo_outcome: hubId,
          task_type: taskType,
        })
        const current = this.reoTasksByHub[hubId] ?? []
        // Prepend newly-created task so it appears at the top
        const next = [res.data, ...current]
        // Ensure unique by id in case of stale cache
        const seen = new Set<number>()
        this.reoTasksByHub[hubId] = next.filter(t => {
          if (seen.has(t.id)) return false
          seen.add(t.id)
          return true
        })
        return res.data
      } catch (err: any) {
        const msg = err?.response?.data?.detail || err?.message || 'Failed to create REO task'
        this.errorReoTasks[hubId] = msg
        throw err
      } finally {
        this.loadingReoTasks[hubId] = false
      }
    },
    async deleteReoTask(hubId: number, taskId: number): Promise<void> {
      try {
        this.loadingReoTasks[hubId] = true
        this.errorReoTasks[hubId] = null
        await http.delete(`/am/outcomes/reo-tasks/${taskId}/`, { params: { asset_hub_id: hubId } })
        const list = this.reoTasksByHub[hubId] ?? []
        this.reoTasksByHub[hubId] = list.filter(t => t.id !== taskId)
      } catch (err: any) {
        const msg = err?.response?.data?.detail || err?.message || 'Failed to delete REO task'
        this.errorReoTasks[hubId] = msg
        throw err
      } finally {
        this.loadingReoTasks[hubId] = false
      }
    },

    // Delete an outcome by hub id and type, then clear caches for that type
    async deleteOutcome(hubId: number, type: OutcomeType): Promise<void> {
      const path = outcomePath[type]
      const url = `/am/outcomes/${path}/${hubId}/`
      await http.delete(url)
      // Purge caches for the deleted outcome to avoid stale UI
      if (type === 'dil') {
        delete this.dilByHub[hubId]
        delete this.dilTasksByHub[hubId]
        delete this.loadingDil[hubId]
        delete this.loadingDilTasks[hubId]
        delete this.errorDil[hubId]
        delete this.errorDilTasks[hubId]
      } else if (type === 'reo') {
        delete this.reoByHub[hubId]
        delete this.reoTasksByHub[hubId]
        delete this.loadingReoTasks[hubId]
        delete this.errorReoTasks[hubId]
      } else if (type === 'fc') {
        delete this.fcByHub[hubId]
        delete this.fcTasksByHub[hubId]
        delete this.loadingFcTasks[hubId]
        delete this.errorFcTasks[hubId]
      } else if (type === 'short_sale') {
        delete this.shortSaleByHub[hubId]
        delete this.shortSaleTasksByHub[hubId]
        delete this.loadingShortSaleTasks[hubId]
        delete this.errorShortSaleTasks[hubId]
      } else if (type === 'modification') {
        delete this.modificationByHub[hubId]
        delete this.modificationTasksByHub[hubId]
        delete this.loadingModificationTasks[hubId]
        delete this.errorModificationTasks[hubId]
      }
    },

    // Generic fetch to detect if an outcome exists for a hub. Returns first match or null.
    // WHAT: Fetches outcome record from backend and caches it in store
    // WHY: Needed to determine which outcome cards to show on page load
    // HOW: Queries by asset_hub_id and caches the first result per outcome type
    async fetchOutcome(hubId: number, type: OutcomeType): Promise<any | null> {
      const path = outcomePath[type]
      const url = `/am/outcomes/${path}/`
      const res = await http.get<any>(url, { params: { asset_hub_id: hubId } })
      // Handle both paginated (DRF) and non-paginated responses
      const results = res.data?.results || res.data
      const first = Array.isArray(results) && results.length ? results[0] : null
      // Cache the outcome in the appropriate store property
      if (type === 'dil') this.dilByHub[hubId] = first as Dil | null
      else if (type === 'fc') this.fcByHub[hubId] = first as FcSale | null
      else if (type === 'reo') this.reoByHub[hubId] = first as ReoData | null
      else if (type === 'short_sale') this.shortSaleByHub[hubId] = first as ShortSaleOutcome | null
      else if (type === 'modification') this.modificationByHub[hubId] = first as ModificationOutcome | null
      return first
    },

    // -----------------------------
    // FC (FCSale) helpers
    // -----------------------------
    async fetchFc(hubId: number): Promise<FcSale | null> {
      const res = await http.get<any>(`/am/outcomes/fc/`, { params: { asset_hub_id: hubId } })
      const results = res.data?.results || res.data
      return Array.isArray(results) && results.length ? results[0] : null
    },
    async patchFc(hubId: number, payload: Partial<FcSale>): Promise<FcSale> {
      const res = await http.patch<FcSale>(`/am/outcomes/fc/${hubId}/`, payload)
      return res.data
    },

    // -----------------------------
    // REO helpers
    // -----------------------------
    async fetchReo(hubId: number): Promise<ReoData | null> {
      const res = await http.get<any>(`/am/outcomes/reo/`, { params: { asset_hub_id: hubId } })
      const results = res.data?.results || res.data
      return Array.isArray(results) && results.length ? results[0] : null
    },
    async patchReo(hubId: number, payload: Partial<ReoData>): Promise<ReoData> {
      const res = await http.patch<ReoData>(`/am/outcomes/reo/${hubId}/`, payload)
      return res.data
    },

    // -----------------------------
    // Short Sale helpers
    // -----------------------------
    async fetchShortSale(hubId: number): Promise<ShortSaleOutcome | null> {
      const res = await http.get<any>(`/am/outcomes/short-sale/`, { params: { asset_hub_id: hubId } })
      const results = res.data?.results || res.data
      return Array.isArray(results) && results.length ? results[0] : null
    },
    async patchShortSale(hubId: number, payload: Partial<ShortSaleOutcome>): Promise<ShortSaleOutcome> {
      const res = await http.patch<ShortSaleOutcome>(`/am/outcomes/short-sale/${hubId}/`, payload)
      return res.data
    },

    // -----------------------------
    // Modification helpers
    // -----------------------------
    async fetchModification(hubId: number): Promise<ModificationOutcome | null> {
      const res = await http.get<any>(`/am/outcomes/modification/`, { params: { asset_hub_id: hubId } })
      const results = res.data?.results || res.data
      return Array.isArray(results) && results.length ? results[0] : null
    },
    async patchModification(hubId: number, payload: Partial<ModificationOutcome>): Promise<ModificationOutcome> {
      const res = await http.patch<ModificationOutcome>(`/am/outcomes/modification/${hubId}/`, payload)
      return res.data
    },

    // Ensure a DIL record exists (POST is idempotent on backend). Returns the Dil.
    async ensureDil(hubId: number): Promise<Dil> {
      try {
        this.loadingDil[hubId] = true
        this.errorDil[hubId] = null
        const res = await http.post<Dil>('/am/outcomes/dil/', { asset_hub_id: hubId })
        this.dilByHub[hubId] = res.data
        return res.data
      } catch (err: any) {
        const msg = err?.response?.data?.detail || err?.message || 'Failed to ensure DIL'
        this.errorDil[hubId] = msg
        throw err
      } finally {
        this.loadingDil[hubId] = false
      }
    },

    // Fetch existing DIL for hub; returns null if not present
    async fetchDil(hubId: number, force = false): Promise<Dil | null> {
      if (!force && this.dilByHub[hubId] !== undefined) return this.dilByHub[hubId]
      try {
        this.loadingDil[hubId] = true
        this.errorDil[hubId] = null
        const res = await http.get<any>('/am/outcomes/dil/', { params: { asset_hub_id: hubId } })
        const results = res.data?.results || res.data
        const item = Array.isArray(results) && results.length ? results[0] : null
        this.dilByHub[hubId] = item
        return item
      } catch (err: any) {
        const msg = err?.response?.data?.detail || err?.message || 'Failed to load DIL'
        this.errorDil[hubId] = msg
        throw err
      } finally {
        this.loadingDil[hubId] = false
      }
    },

    // List DIL tasks by hub id (newest-first)
    async listDilTasks(hubId: number, force = false): Promise<DilTask[]> {
      if (!force && this.dilTasksByHub[hubId] !== undefined) return this.dilTasksByHub[hubId]
      try {
        this.loadingDilTasks[hubId] = true
        this.errorDilTasks[hubId] = null
        const res = await http.get<DilTask[]>('/am/outcomes/dil-tasks/', { params: { asset_hub_id: hubId } })
        const items = Array.isArray(res.data) ? res.data : []
        const itemsSorted = [...items].sort((a, b) => {
          const aT = Date.parse(a.created_at)
          const bT = Date.parse(b.created_at)
          if (!isNaN(aT) && !isNaN(bT)) return bT - aT
          return (b.id ?? 0) - (a.id ?? 0)
        })
        this.dilTasksByHub[hubId] = itemsSorted
        return itemsSorted
      } catch (err: any) {
        const msg = err?.response?.data?.detail || err?.message || 'Failed to load DIL tasks'
        this.errorDilTasks[hubId] = msg
        throw err
      } finally {
        this.loadingDilTasks[hubId] = false
      }
    },

    // Create a new DIL task (parent PK equals hub id); prepend to cache
    async createDilTask(hubId: number, taskType: DilTaskType): Promise<DilTask> {
      try {
        this.loadingDilTasks[hubId] = true
        this.errorDilTasks[hubId] = null
        const res = await http.post<DilTask>('/am/outcomes/dil-tasks/', {
          asset_hub_id: hubId,
          dil: hubId, // parent PK equals hub id due to OneToOne primary_key
          task_type: taskType,
        })
        const current = this.dilTasksByHub[hubId] ?? []
        const next = [res.data, ...current]
        const seen = new Set<number>()
        this.dilTasksByHub[hubId] = next.filter(t => {
          if (seen.has(t.id)) return false
          seen.add(t.id)
          return true
        })
        return res.data
      } catch (err: any) {
        const msg = err?.response?.data?.detail || err?.message || 'Failed to create DIL task'
        this.errorDilTasks[hubId] = msg
        throw err
      } finally {
        this.loadingDilTasks[hubId] = false
      }
    },
    async deleteDilTask(hubId: number, taskId: number): Promise<void> {
      try {
        this.loadingDilTasks[hubId] = true
        this.errorDilTasks[hubId] = null
        await http.delete(`/am/outcomes/dil-tasks/${taskId}/`, { params: { asset_hub_id: hubId } })
        const list = this.dilTasksByHub[hubId] ?? []
        this.dilTasksByHub[hubId] = list.filter(t => t.id !== taskId)
      } catch (err: any) {
        const msg = err?.response?.data?.detail || err?.message || 'Failed to delete DIL task'
        this.errorDilTasks[hubId] = msg
        throw err
      } finally {
        this.loadingDilTasks[hubId] = false
      }
    },

    // -----------------------------
    // FC Tasks helpers
    // -----------------------------
    async listFcTasks(hubId: number, force = false): Promise<FcTask[]> {
      if (!force && this.fcTasksByHub[hubId] !== undefined) return this.fcTasksByHub[hubId]
      try {
        this.loadingFcTasks[hubId] = true
        this.errorFcTasks[hubId] = null
        const res = await http.get<FcTask[]>('/am/outcomes/fc-tasks/', { params: { asset_hub_id: hubId } })
        const items = Array.isArray(res.data) ? res.data : []
        const itemsSorted = [...items].sort((a, b) => {
          const aT = Date.parse(a.created_at)
          const bT = Date.parse(b.created_at)
          if (!isNaN(aT) && !isNaN(bT)) return bT - aT
          return (b.id ?? 0) - (a.id ?? 0)
        })
        this.fcTasksByHub[hubId] = itemsSorted
        return itemsSorted
      } catch (err: any) {
        const msg = err?.response?.data?.detail || err?.message || 'Failed to load FC tasks'
        this.errorFcTasks[hubId] = msg
        throw err
      } finally {
        this.loadingFcTasks[hubId] = false
      }
    },
    async createFcTask(hubId: number, taskType: FcTaskType): Promise<FcTask> {
      try {
        this.loadingFcTasks[hubId] = true
        this.errorFcTasks[hubId] = null
        // Ensure parent FC outcome exists
        await this.ensureOutcome(hubId, 'fc')
        const res = await http.post<FcTask>('/am/outcomes/fc-tasks/', {
          asset_hub_id: hubId,
          fc_sale: hubId,
          task_type: taskType,
        })
        const current = this.fcTasksByHub[hubId] ?? []
        const next = [res.data, ...current]
        const seen = new Set<number>()
        this.fcTasksByHub[hubId] = next.filter(t => {
          if (seen.has(t.id)) return false
          seen.add(t.id)
          return true
        })
        return res.data
      } catch (err: any) {
        const msg = err?.response?.data?.detail || err?.message || 'Failed to create FC task'
        this.errorFcTasks[hubId] = msg
        throw err
      } finally {
        this.loadingFcTasks[hubId] = false
      }
    },
    async deleteFcTask(hubId: number, taskId: number): Promise<void> {
      try {
        this.loadingFcTasks[hubId] = true
        this.errorFcTasks[hubId] = null
        await http.delete(`/am/outcomes/fc-tasks/${taskId}/`, { params: { asset_hub_id: hubId } })
        // Remove from cache
        const list = this.fcTasksByHub[hubId] ?? []
        this.fcTasksByHub[hubId] = list.filter(t => t.id !== taskId)
      } catch (err: any) {
        const msg = err?.response?.data?.detail || err?.message || 'Failed to delete FC task'
        this.errorFcTasks[hubId] = msg
        throw err
      } finally {
        this.loadingFcTasks[hubId] = false
      }
    },

    // -----------------------------
    // Short Sale Tasks helpers
    // -----------------------------
    async listShortSaleTasks(hubId: number, force = false): Promise<ShortSaleTask[]> {
      if (!force && this.shortSaleTasksByHub[hubId] !== undefined) return this.shortSaleTasksByHub[hubId]
      try {
        this.loadingShortSaleTasks[hubId] = true
        this.errorShortSaleTasks[hubId] = null
        const res = await http.get<ShortSaleTask[]>('/am/outcomes/short-sale-tasks/', { params: { asset_hub_id: hubId } })
        const items = Array.isArray(res.data) ? res.data : []
        const itemsSorted = [...items].sort((a, b) => {
          const aT = Date.parse(a.created_at)
          const bT = Date.parse(b.created_at)
          if (!isNaN(aT) && !isNaN(bT)) return bT - aT
          return (b.id ?? 0) - (a.id ?? 0)
        })
        this.shortSaleTasksByHub[hubId] = itemsSorted
        return itemsSorted
      } catch (err: any) {
        const msg = err?.response?.data?.detail || err?.message || 'Failed to load Short Sale tasks'
        this.errorShortSaleTasks[hubId] = msg
        throw err
      } finally {
        this.loadingShortSaleTasks[hubId] = false
      }
    },
    async createShortSaleTask(hubId: number, taskType: ShortSaleTaskType): Promise<ShortSaleTask> {
      try {
        this.loadingShortSaleTasks[hubId] = true
        this.errorShortSaleTasks[hubId] = null
        // Ensure parent Short Sale outcome exists
        await this.ensureOutcome(hubId, 'short_sale')
        const res = await http.post<ShortSaleTask>('/am/outcomes/short-sale-tasks/', {
          asset_hub_id: hubId,
          short_sale: hubId,
          task_type: taskType,
        })
        const current = this.shortSaleTasksByHub[hubId] ?? []
        const next = [res.data, ...current]
        const seen = new Set<number>()
        this.shortSaleTasksByHub[hubId] = next.filter(t => {
          if (seen.has(t.id)) return false
          seen.add(t.id)
          return true
        })
        return res.data
      } catch (err: any) {
        const msg = err?.response?.data?.detail || err?.message || 'Failed to create Short Sale task'
        this.errorShortSaleTasks[hubId] = msg
        throw err
      } finally {
        this.loadingShortSaleTasks[hubId] = false
      }
    },
    async deleteShortSaleTask(hubId: number, taskId: number): Promise<void> {
      try {
        this.loadingShortSaleTasks[hubId] = true
        this.errorShortSaleTasks[hubId] = null
        await http.delete(`/am/outcomes/short-sale-tasks/${taskId}/`, { params: { asset_hub_id: hubId } })
        const list = this.shortSaleTasksByHub[hubId] ?? []
        this.shortSaleTasksByHub[hubId] = list.filter(t => t.id !== taskId)
      } catch (err: any) {
        const msg = err?.response?.data?.detail || err?.message || 'Failed to delete Short Sale task'
        this.errorShortSaleTasks[hubId] = msg
        throw err
      } finally {
        this.loadingShortSaleTasks[hubId] = false
      }
    },

    // -----------------------------
    // Modification Tasks helpers
    // -----------------------------
    async listModificationTasks(hubId: number, force = false): Promise<ModificationTask[]> {
      if (!force && this.modificationTasksByHub[hubId] !== undefined) return this.modificationTasksByHub[hubId]
      try {
        this.loadingModificationTasks[hubId] = true
        this.errorModificationTasks[hubId] = null
        const res = await http.get<ModificationTask[]>('/am/outcomes/modification-tasks/', { params: { asset_hub_id: hubId } })
        const items = Array.isArray(res.data) ? res.data : []
        const itemsSorted = [...items].sort((a, b) => {
          const aT = Date.parse(a.created_at)
          const bT = Date.parse(b.created_at)
          if (!isNaN(aT) && !isNaN(bT)) return bT - aT
          return (b.id ?? 0) - (a.id ?? 0)
        })
        this.modificationTasksByHub[hubId] = itemsSorted
        return itemsSorted
      } catch (err: any) {
        const msg = err?.response?.data?.detail || err?.message || 'Failed to load Modification tasks'
        this.errorModificationTasks[hubId] = msg
        throw err
      } finally {
        this.loadingModificationTasks[hubId] = false
      }
    },
    async createModificationTask(hubId: number, taskType: ModificationTaskType): Promise<ModificationTask> {
      try {
        this.loadingModificationTasks[hubId] = true
        this.errorModificationTasks[hubId] = null
        // Ensure parent Modification outcome exists
        await this.ensureOutcome(hubId, 'modification')
        const res = await http.post<ModificationTask>('/am/outcomes/modification-tasks/', {
          asset_hub_id: hubId,
          modification: hubId,
          task_type: taskType,
        })
        const current = this.modificationTasksByHub[hubId] ?? []
        const next = [res.data, ...current]
        const seen = new Set<number>()
        this.modificationTasksByHub[hubId] = next.filter(t => {
          if (seen.has(t.id)) return false
          seen.add(t.id)
          return true
        })
        return res.data
      } catch (err: any) {
        const msg = err?.response?.data?.detail || err?.message || 'Failed to create Modification task'
        this.errorModificationTasks[hubId] = msg
        throw err
      } finally {
        this.loadingModificationTasks[hubId] = false
      }
    },
    async deleteModificationTask(hubId: number, taskId: number): Promise<void> {
      try {
        this.loadingModificationTasks[hubId] = true
        this.errorModificationTasks[hubId] = null
        await http.delete(`/am/outcomes/modification-tasks/${taskId}/`, { params: { asset_hub_id: hubId } })
        const list = this.modificationTasksByHub[hubId] ?? []
        this.modificationTasksByHub[hubId] = list.filter(t => t.id !== taskId)
      } catch (err: any) {
        const msg = err?.response?.data?.detail || err?.message || 'Failed to delete Modification task'
        this.errorModificationTasks[hubId] = msg
        throw err
      } finally {
        this.loadingModificationTasks[hubId] = false
      }
    },
  },
})
