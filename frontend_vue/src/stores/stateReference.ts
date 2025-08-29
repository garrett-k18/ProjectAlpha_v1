// State Reference Pinia Store
// Manages fetching and caching judicial/non-judicial state data from Django backend

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from '@/lib/http'

// TypeScript interface for state data
interface JudicialStateData {
  [stateCode: string]: boolean
}

// Define the store with name 'stateReference'
export const useStateReferenceStore = defineStore('stateReference', () => {
  // State
  const judicialStateMap = ref<JudicialStateData>({})
  const isLoading = ref(false)
  const error = ref('')
  const lastFetched = ref(0) // timestamp to check if we need a refresh

  // Getters
  const isJudicialState = computed(() => {
    return (stateCode: string): boolean => {
      const normalizedCode = stateCode?.trim().toUpperCase() || ''
      return !!judicialStateMap.value[normalizedCode]
    }
  })

  const allJudicialStates = computed(() => {
    return Object.entries(judicialStateMap.value)
      .filter(([_code, isJudicial]) => isJudicial)
      .map(([code]) => code)
  })

  const allNonJudicialStates = computed(() => {
    return Object.entries(judicialStateMap.value)
      .filter(([_code, isJudicial]) => !isJudicial)
      .map(([code]) => code)
  })

  const hasData = computed(() => Object.keys(judicialStateMap.value).length > 0)

  // Actions
  async function fetchJudicialStates(force = false) {
    // Skip if already loaded and not forced
    const now = Date.now()
    const cacheExpired = (now - lastFetched.value) > (15 * 60 * 1000) // 15 min cache
    
    if (hasData.value && !force && !cacheExpired) {
      return
    }

    isLoading.value = true
    error.value = ''

    try {
      const response = await axios.get('/api/acq/state-references/judicial/')
      judicialStateMap.value = response.data.states || {}
      lastFetched.value = now
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch judicial state data'
      console.error('Error fetching judicial states:', err)
    } finally {
      isLoading.value = false
    }
  }

  // Clear store (mainly for testing)
  function clearCache() {
    judicialStateMap.value = {}
    lastFetched.value = 0
  }

  return {
    // State
    judicialStateMap,
    isLoading,
    error,
    lastFetched,

    // Getters
    isJudicialState,
    allJudicialStates,
    allNonJudicialStates,
    hasData,

    // Actions
    fetchJudicialStates,
    clearCache
  }
})
