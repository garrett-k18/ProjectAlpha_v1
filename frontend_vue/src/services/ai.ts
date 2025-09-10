// src/services/ai.ts
// Service wrapper for AI-related API calls.
// - Uses centralized Axios instance from src/lib/http.ts
// - Exposes a typed function to request bullet-point summaries from the backend
// Docs reviewed:
// * Axios: https://axios-http.com/docs/instance
// * DRF basics: https://www.django-rest-framework.org/

import http from '@/lib/http'

export interface QuickSummaryResponse {
  bullets: string[]
  /** Optional 2–3 sentence executive summary paragraph */
  summary?: string
  error?: string
}

/**
 * getQuickSummary
 * Calls the backend endpoint to generate 4–6 bullet points for a given context.
 * @param context - Raw text to summarize
 * @param maxBullets - Desired bullet count (4–6); defaults to 5
 */
// ----------------------------------------------------------------------------------
// Client-side cache and optional dev mocking
// ----------------------------------------------------------------------------------

// Normalize a context string to improve cache hit rate: trim and collapse whitespace
function normalizeContext(input: string): string {
  return (input || '').trim().replace(/\s+/g, ' ')
}

// Shared in-memory cache: key -> { data, ts }
const CACHE = new Map<string, { data: QuickSummaryResponse; ts: number }>()

// TTL and max entries are configurable via Vite env, with sane defaults
const TTL_MS = Number(import.meta.env.VITE_AI_SUMMARY_CACHE_TTL_MS || 10 * 60 * 1000) // default 10 minutes
const MAX_ENTRIES = Number(import.meta.env.VITE_AI_SUMMARY_CACHE_MAX || 200)

// Dev-only mocking flag
const MOCK = !!(import.meta.env.DEV && import.meta.env.VITE_MOCK_AI_SUMMARY === 'true')

// Insert/trim helper
function cacheSet(key: string, value: QuickSummaryResponse) {
  // Trim if needed
  if (CACHE.size >= MAX_ENTRIES) {
    // Remove oldest (linear scan is fine for small sizes)
    let oldestKey: string | null = null
    let oldestTs = Number.POSITIVE_INFINITY
    for (const [k, v] of CACHE.entries()) {
      if (v.ts < oldestTs) {
        oldestTs = v.ts
        oldestKey = k
      }
    }
    if (oldestKey) CACHE.delete(oldestKey)
  }
  CACHE.set(key, { data: value, ts: Date.now() })
}

// Mock generator for dev to avoid token usage
function mockSummary(context: string, maxBullets: number): QuickSummaryResponse {
  const preview = normalizeContext(context).slice(0, 120)
  const base = [
    `Summary preview: ${preview}${preview.length === 120 ? '…' : ''}`,
    'Current balance and debt noted.',
    'Status and flags reviewed.',
    'No critical risks detected in mock.',
    'Use production to fetch real AI summary.',
  ]
  const bullets = base.slice(0, Math.min(Math.max(maxBullets, 1), 6))
  // Dev placeholder paragraph for the executive summary section.
  // NOTE: This is intentionally static in mock mode so the UI reliably shows
  // a paragraph even before the real backend AI summary is wired.
  const summary = 'This is an AI-generated executive summary of the asset. This paragraph will contain a high-level overview and any pertinent data points.'
  return { bullets, summary }
}

export async function getQuickSummary(context: string, maxBullets: number = 5): Promise<QuickSummaryResponse> {
  const ctx = normalizeContext(context)
  const key = `${ctx}::${maxBullets}`

  // Cache hit
  const cached = CACHE.get(key)
  if (cached && Date.now() - cached.ts < TTL_MS) {
    return cached.data
  }

  // Dev mock path to completely avoid backend calls
  if (MOCK) {
    const data = mockSummary(ctx, maxBullets)
    cacheSet(key, data)
    return data
  }

  // Post to the server-side AI endpoint; baseURL is '/api' in dev via Vite proxy
  const res = await http.post<QuickSummaryResponse>('/acq/ai/summary/', {
    context: ctx,
    max_bullets: maxBullets,
  })
  const data = res.data
  cacheSet(key, data)
  return data
}
