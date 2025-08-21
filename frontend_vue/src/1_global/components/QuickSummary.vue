<template>
  <!--
    QuickSummary.vue
    - Hyper UI styled card that fetches 4–6 AI-generated bullets from the backend
    - Totally data-agnostic: parent provides a `context` string to summarize
  -->
  <div ref="rootEl" class="card h-100 d-flex flex-column">
    <div class="card-body d-flex flex-column">
      <!-- Title row -->
      <div class="d-flex align-items-center mb-3">
        <h5 class="card-title mb-0">{{ title }}</h5>
        <div class="ms-auto d-flex align-items-center gap-2">
          <slot name="actions"></slot>
        </div>
      </div>

      <!-- Loading state: centered spinner and 'Generating…' text -->
      <div
        v-if="loading"
        class="flex-grow-1 d-flex justify-content-center align-items-center text-center py-4 w-100"
      >
        <!-- Using Bootstrap/Hyper UI spinner for consistency -->
        <b-spinner small variant="primary" class="me-2">
          <span class="visually-hidden">Generating…</span>
        </b-spinner>
        <small class="text-muted">Generating…</small>
      </div>

      <!-- Error state -->
      <div v-else-if="error" class="alert alert-warning py-2 mb-0">
        <small class="mb-0">{{ errorMessage }}</small>
      </div>

      <!-- Bullets -->
      <div v-else>
        <ul class="mb-0 ps-3">
          <li v-for="(b, idx) in bullets" :key="idx" class="mb-1">
            {{ b }}
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// ----------------------------------------------------------------------------------
// QuickSummary.vue
// ----------------------------------------------------------------------------------
// Purpose: Renders a compact AI-generated summary as 4–6 bullet points.
// Behavior: Calls a secure Django endpoint so the API key never hits the client.
// Styling: Hyper UI / Bootstrap card styles for consistency with the app.
// ----------------------------------------------------------------------------------

import { ref, watch, computed, onMounted, onBeforeUnmount } from 'vue'
import { getQuickSummary } from '@/services/ai'

interface Props {
  /** The raw content to summarize (required) */
  context: string
  /** Desired bullet count (4–6). Default: 5 */
  maxBullets?: number
  /** Card title text */
  title?: string
  /** Auto-fetch when component mounts or context changes. Default: true */
  autoFetch?: boolean
  /** If true, defer fetching until the component becomes visible (IntersectionObserver). Default: false */
  lazy?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  maxBullets: 5,
  title: 'Quick Summary',
  autoFetch: true,
  lazy: false,
})

// Reactive state for the async request
const loading = ref(false)       // whether a request is in flight
const error = ref<string | null>(null) // error code or message from server
const bullets = ref<string[]>([])      // array of bullet strings to render

// Lazy-loading visibility and lifecycle state
const rootEl = ref<HTMLElement | null>(null) // root element to observe visibility
const isVisible = ref(false)                 // whether the card is in viewport
const hasFetchedOnce = ref(false)            // prevent duplicate fetches on first reveal
let observer: IntersectionObserver | null = null

// Derived friendly error message for display
const errorMessage = computed(() => {
  if (!error.value) return ''
  if (error.value === 'insufficient_context') return 'Provide more context to summarize.'
  if (error.value === 'missing_api_key') return 'Server is missing Anthropic API key.'
  if (error.value === 'anthropic_sdk_missing') return 'Server missing Anthropic SDK dependency.'
  if (error.value === 'provider_error') return 'AI provider error. Please try again.'
  return error.value
})

/**
 * fetchSummary
 * Calls the backend to summarize `props.context`.
 */
async function fetchSummary() {
  // Skip if context is too short to be meaningful
  if (!props.context || props.context.trim().length < 10) {
    bullets.value = []
    error.value = 'insufficient_context'
    return
  }

  loading.value = true
  error.value = null
  try {
    const { bullets: arr, error: err } = await getQuickSummary(props.context, props.maxBullets)
    if (err) {
      error.value = err
      bullets.value = []
    } else {
      bullets.value = arr || []
    }
  } catch (e: any) {
    // Network or unexpected error
    error.value = 'provider_error'
    bullets.value = []
  } finally {
    loading.value = false
  }
}

// IntersectionObserver for lazy loading: fetch only when visible
onMounted(() => {
  if (!props.lazy) {
    // If not lazy, we still want to auto-fetch below via the watcher
    return
  }
  try {
    observer = new IntersectionObserver((entries) => {
      for (const e of entries) {
        if (e.isIntersecting) {
          isVisible.value = true
          // Fetch once when first visible, if autoFetch is enabled
          if (props.autoFetch && !hasFetchedOnce.value) {
            hasFetchedOnce.value = true
            fetchSummary()
          }
        }
      }
    }, { threshold: 0.1 })
    if (rootEl.value) observer.observe(rootEl.value)
  } catch (err) {
    // If IntersectionObserver not available, fallback to immediate fetch
    console.warn('[QuickSummary] IntersectionObserver unavailable, fetching immediately')
    if (props.autoFetch) fetchSummary()
  }
})

onBeforeUnmount(() => {
  try {
    if (observer && rootEl.value) observer.unobserve(rootEl.value)
    observer = null
  } catch {}
})

// Auto-fetch on mount / prop change
watch(
  () => [props.context, props.maxBullets, props.autoFetch, props.lazy, isVisible.value] as const,
  (newVals, oldVals) => {
    const [ctx, _n, auto, lazy, visible] = newVals
    const prevCtx = oldVals ? oldVals[0] : undefined
    // Reset when context changes so we refetch
    if (ctx !== prevCtx) {
      hasFetchedOnce.value = false
    }
    if (!auto) return
    // If lazy, wait until visible; otherwise fetch immediately
    if (lazy) {
      if (visible && !hasFetchedOnce.value) {
        hasFetchedOnce.value = true
        fetchSummary()
      }
    } else {
      fetchSummary()
    }
  },
  { immediate: true }
)

// Expose manual reload for parent via template ref if needed
// Usage: <QuickSummary ref="qs" ... /> and then `qs.fetch()`
// NOTE: keep this minimal and documented for modularity
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
defineExpose({ fetch: fetchSummary })
</script>

<style scoped>
/* Keep styles minimal; prefer Hyper UI/Bootstrap utilities. */
ul { list-style: disc; }
</style>
