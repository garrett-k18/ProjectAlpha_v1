/*
  Pinia store for AM Notes with contextual filtering.

  Documentation reviewed:
  - Pinia core concepts: https://pinia.vuejs.org/core-concepts/
  - Axios instance reuse (http client): src/lib/http.ts
  - DRF ViewSets & filtering: https://www.django-rest-framework.org/api-guide/filtering/

  Design goals:
  - Single source of truth for all notes per asset hub (centralized storage).
  - Typed helpers to list/create/update/delete notes.
  - Context-aware listing: filter by outcome, task type, task id, and tag.
  - Heavily commented per user preference for clarity and maintainability.
*/

import { defineStore } from 'pinia'
import http from '@/lib/http'

// -----------------------------
// Type Definitions
// -----------------------------

// Canonical token types for tone mapping and filters are maintained in badgeTokens.
// Notes use tags for categorization and their own context fields for scoping.
export type NoteTag = 'general' | 'legal' | 'escrow' | 'foreclosure' | 'reo' | 'borrower_heir' | null

export type NoteScope = 'asset' | 'outcome' | 'task'

// Outcome type keys must match backend AMNote.OUTCOME_CHOICES values
export type OutcomeKey = 'dil' | 'fc' | 'reo' | 'short_sale' | 'modification' | 'note_sale'

// API shape returned by DRF serializer for AM Note entries
export interface NoteItem {
  // Primary key assigned by backend
  id: number
  // Foreign key to the asset hub (centralized asset identifier)
  asset_hub: number | null
  // Scope of the note (asset/outcome/task) as determined by backend
  scope?: NoteScope | null
  // Optional context fields used for scoping notes to a track/outcome and/or specific task
  context_outcome?: OutcomeKey | null
  context_task_type?: string | null
  context_task_id?: number | null
  // Free-form note content authored by users
  body: string
  // Optional single-select tag used for categorization (e.g., urgent/legal)
  tag: NoteTag
  // Pinned state for surfacing important notes in UI feeds
  pinned: boolean
  // Audit fields stamped by backend
  created_at: string
  updated_at: string
  created_by: number | null
  updated_by: number | null
  created_by_username: string | null
  updated_by_username: string | null
}

// Parameters for listing notes with optional context filters
export interface ListNotesParams {
  // Required asset hub id to scope the query
  assetHubId: number
  // Optional filters to narrow result set in UI
  contextOutcome?: OutcomeKey
  contextTaskType?: string
  contextTaskId?: number
  tag?: NoteTag
  search?: string
}

// Payload for creating a note; asset hub id flows via query param
export interface CreateNoteInput {
  body: string
  tag?: NoteTag
  pinned?: boolean
  scope?: NoteScope
  context_outcome?: OutcomeKey | null
  context_task_type?: string | null
  context_task_id?: number | null
}

// -----------------------------
// Store Definition
// -----------------------------

export const useNotesStore = defineStore('amNotes', {
  // State holds note lists keyed by hub id for quick access
  state: () => ({
    // Cache of notes per asset hub id
    notesByHub: {} as Record<number, NoteItem[]>,
    // Loading flags per hub id
    loadingByHub: {} as Record<number, boolean>,
    // Error messages per hub id
    errorByHub: {} as Record<number, string | null>,
  }),

  getters: {
    // Retrieve a list of notes for a hub from cache (empty array if not loaded)
    getNotesForHub: (state) => (hubId: number): NoteItem[] => state.notesByHub[hubId] ?? [],
    // Simple pinned subset for quick UI badges or sections
    getPinnedForHub: (state) => (hubId: number): NoteItem[] => (state.notesByHub[hubId] ?? []).filter(n => n.pinned),
  },

  actions: {
    // List notes for a hub with optional context filters. Results are cached by hub id.
    async listNotes(params: ListNotesParams): Promise<NoteItem[]> {
      // Destructure inputs for clarity
      const { assetHubId, contextOutcome, contextTaskType, contextTaskId, tag, search } = params

      // Build query string with only provided filters to keep URLs clean
      const q: Record<string, any> = { asset_hub_id: assetHubId }
      if (contextOutcome) q.context_outcome = contextOutcome
      if (contextTaskType) q.context_task_type = contextTaskType
      if (typeof contextTaskId === 'number') q.context_task_id = contextTaskId
      if (tag) q.tag = tag
      if (search) q.search = search

      try {
        // Raise loading flag for this hub id
        this.loadingByHub[assetHubId] = true
        // Clear previous error to ensure fresh UI state
        this.errorByHub[assetHubId] = null

        // Perform GET request against DRF endpoint; expects array of NoteItem
        const res = await http.get<any>('/am/notes/', { params: q })

        // Handle paginated DRF response (results array) or plain array
        const results = res.data?.results || res.data
        const items = Array.isArray(results) ? results : []
        // Sort pinned first then chronological order (Oldest -> Newest)
        this.notesByHub[assetHubId] = this.sortNotes(items)
        return this.notesByHub[assetHubId]
      } catch (err: any) {
        // Capture error message in a user-friendly way
        const msg = err?.response?.data?.detail || err?.message || 'Failed to load notes'
        this.errorByHub[assetHubId] = msg
        throw err
      } finally {
        // Reset the loading flag even if the request failed
        this.loadingByHub[assetHubId] = false
      }
    },

    // Create a new note for a given hub; returns created NoteItem and updates cache optimistically
    async createNote(assetHubId: number, payload: CreateNoteInput): Promise<NoteItem> {
      try {
        // Mark hub as loading to disable UI controls as needed
        this.loadingByHub[assetHubId] = true
        this.errorByHub[assetHubId] = null

        // POST the payload; pass hub via query param to match backend viewset flexibility
        const res = await http.post<NoteItem>(
          '/am/notes/',
          payload,
          { params: { asset_hub_id: assetHubId } },
        )

        // Merge the new note into the cached list for this hub id
        const current = this.notesByHub[assetHubId] ?? []
        const next = [...current, res.data]
        // Ensure uniqueness by id in case of stale cache
        const seen = new Set<number>()
        const unique = next.filter(n => {
          if (seen.has(n.id)) return false
          seen.add(n.id)
          return true
        })
        this.notesByHub[assetHubId] = this.sortNotes(unique)
        return res.data
      } catch (err: any) {
        const msg = err?.response?.data?.detail || err?.message || 'Failed to create note'
        this.errorByHub[assetHubId] = msg
        throw err
      } finally {
        this.loadingByHub[assetHubId] = false
      }
    },

    // Patch a note (e.g., pin/unpin or edit body/tag). Returns updated item and updates cache.
    async patchNote(assetHubId: number, noteId: number, patch: Partial<Pick<NoteItem, 'body' | 'tag' | 'pinned'>>): Promise<NoteItem> {
      try {
        this.loadingByHub[assetHubId] = true
        this.errorByHub[assetHubId] = null
        // Include asset_hub_id query param for backend queryset filtering
        const res = await http.patch<NoteItem>(`/am/notes/${noteId}/`, patch, { params: { asset_hub_id: assetHubId } })
        const list = this.notesByHub[assetHubId] ?? []
        const next = list.map(n => (n.id === noteId ? res.data : n))
        this.notesByHub[assetHubId] = this.sortNotes(next)
        return res.data
      } catch (err: any) {
        const msg = err?.response?.data?.detail || err?.message || 'Failed to update note'
        this.errorByHub[assetHubId] = msg
        throw err
      } finally {
        this.loadingByHub[assetHubId] = false
      }
    },

    // Delete a note; removes it from cache if present
    async deleteNote(assetHubId: number, noteId: number): Promise<void> {
      try {
        this.loadingByHub[assetHubId] = true
        this.errorByHub[assetHubId] = null
        // Include asset_hub_id query param for backend queryset filtering
        await http.delete(`/am/notes/${noteId}/`, { params: { asset_hub_id: assetHubId } })
        const list = this.notesByHub[assetHubId] ?? []
        this.notesByHub[assetHubId] = list.filter(n => n.id !== noteId)
      } catch (err: any) {
        const msg = err?.response?.data?.detail || err?.message || 'Failed to delete note'
        this.errorByHub[assetHubId] = msg
        throw err
      } finally {
        this.loadingByHub[assetHubId] = false
      }
    },

    // WHAT: Helper to sort notes consistently across list/create/patch
    // WHY: Keep reverse-chronological order (newest first) while respecting pinned items
    sortNotes(items: NoteItem[]): NoteItem[] {
      return [...items].sort((a, b) => {
        // Pinned notes always stay at the top
        if (a.pinned !== b.pinned) return a.pinned ? -1 : 1
        
        // Non-pinned notes sorted by created_at descending (Newest -> Oldest)
        const aT = Date.parse(a.created_at)
        const bT = Date.parse(b.created_at)
        if (!Number.isNaN(aT) && !Number.isNaN(bT)) return bT - aT
        
        // Fallback to ID descending
        return (b.id ?? 0) - (a.id ?? 0)
      })
    },
  },
})
