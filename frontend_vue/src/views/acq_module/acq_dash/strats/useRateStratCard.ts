/*
 * Composable: useRateStratCard
 * WHAT: Centralizes shared logic for rate-based stratification cards (Coupon, Default Rate).
 * WHY: Prevents duplicated Pinia/watch logic while keeping per-card configuration declarative.
 * WHERE: Used by components inside acquisitions stratifications folder, co-located for clarity.
 * HOW: Accepts the Pinia action/getter keys specific to the requested stratification.
 */
import { computed, onMounted, watch, toRef, type Ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useAcqSelectionsStore } from '@/stores/acqSelections'
import { useStratsStore, type StratBand } from '@/stores/strats'

type StratStore = ReturnType<typeof useStratsStore>

type RateStratConfig = {
  /** Fetch handler wired to the specific strat endpoint */
  fetch: (store: StratStore, sellerId: number, tradeId: number) => Promise<StratBand[]>
  /** Getter returning cached bands for current selection */
  get: (store: StratStore, sellerId: number | null, tradeId: number | null) => StratBand[]
  /** Property key for loading boolean */
  loadingKey: keyof StratStore
  /** Property key for error string */
  errorKey: keyof StratStore
}

export function useRateStratCard(config: RateStratConfig) {
  // Selection store primes seller/trade IDs that gate requests.
  const selectionsStore = useAcqSelectionsStore()
  const { selectedSellerId, selectedTradeId, hasBothSelections} = storeToRefs(selectionsStore)

  // Strat store hosts cached rate band payloads keyed by seller/trade.
  const stratStore = useStratsStore()
  const loadingRef = toRef(stratStore, config.loadingKey) as Ref<boolean>
  const errorRef = toRef(stratStore, config.errorKey) as Ref<string | null>

  // Defensive helper ensures strongly typed number conversion for string decimals coming from API.
  const toNumber = (value: unknown): number => {
    if (value === null || value === undefined || value === '') return 0
    const numeric = typeof value === 'number' ? value : parseFloat(String(value).replace(/,/g, ''))
    return Number.isFinite(numeric) ? numeric : 0
  }

  const bands = computed<StratBand[]>(() => {
    if (!hasBothSelections.value) return []
    return config.get(stratStore, selectedSellerId.value as number, selectedTradeId.value as number)
  })

  const ensureBands = async () => {
    if (!hasBothSelections.value) return
    await config.fetch(stratStore, selectedSellerId.value as number, selectedTradeId.value as number)
  }

  onMounted(ensureBands)
  watch([selectedSellerId, selectedTradeId], ensureBands)

  const hasRows = computed<boolean>(() => Array.isArray(bands.value) && bands.value.length > 0)

  const formatInt = (value: number): string => new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value)

  const formatCurrencyNoDecimals = (value: number): string => new Intl.NumberFormat('en-US', {
    style: 'decimal',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value)

  return {
    bands,
    isLoading: loadingRef,
    errorText: errorRef,
    hasRows,
    formatInt,
    formatCurrencyNoDecimals,
    toNumber,
  }
}
