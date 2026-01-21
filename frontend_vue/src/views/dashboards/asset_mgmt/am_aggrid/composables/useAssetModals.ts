/**
 * Asset Modals Composable
 * Manages modal state for asset detail view and custom list creation
 */

import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/lib/http'

export function useAssetModals() {
  const router = useRouter()

  // Asset detail modal state
  const showAssetModal = ref<boolean>(false)
  const selectedId = ref<string | number | null>(null)
  const selectedRow = ref<any>(null)
  const selectedAddr = ref<string | null>(null)

  // Custom list modal state
  const showAddToListModal = ref<boolean>(false)
  const newListName = ref<string>('')
  const newListDescription = ref<string>('')
  const selectedListAssetIds = ref<Array<string | number>>([])
  const isSavingCustomList = ref<boolean>(false)

  // Header ready state (prevents flash of incomplete data)
  const headerReady = computed<boolean>(() => !!selectedRow.value)

  // Form validation for custom list
  const canSaveCustomList = computed<boolean>(() => {
    const hasName = String(newListName.value || '').trim().length > 0
    return hasName && selectedListAssetIds.value.length > 0
  })

  // Build modal header text
  const modalIdText = computed<string>(() => {
    if (!headerReady.value) return ''

    // Prefer servicer identifier
    const servicerId =
      selectedRow.value?.servicer_id ?? selectedRow.value?.asset_hub?.servicer_id
    if (servicerId != null && servicerId !== '') return String(servicerId)

    // Fallback to hub id
    const hubId =
      selectedRow.value?.asset_hub_id ?? selectedRow.value?.asset_hub?.id
    if (hubId != null && hubId !== '') return String(hubId)

    // Final fallback
    return selectedId.value != null ? String(selectedId.value) : 'Asset'
  })

  const modalTradeText = computed<string>(() => {
    const rawTrade =
      selectedRow.value?.trade_name ?? selectedRow.value?.tradeName ?? ''
    return rawTrade ? String(rawTrade).trim() : ''
  })

  const modalAddrText = computed<string>(() => {
    if (!headerReady.value) return ''

    const r: any = selectedRow.value || {}
    const street = String(r.street_address ?? '').trim()
    const city = String(r.city ?? '').trim()
    const state = String(r.state ?? '').trim()
    const locality = [city, state].filter(Boolean).join(', ')
    const built = [street, locality].filter(Boolean).join(', ')
    if (built) return built

    const rawAddr = selectedAddr.value ? String(selectedAddr.value) : ''
    // Strip trailing ZIP if present
    return rawAddr.replace(/,?\s*\d{5}(?:-\d{4})?$/, '')
  })

  // Helper: Extract asset hub ID
  function getAssetHubIdFromRow(row: any): string | number | null {
    const candidates = [
      row?.asset_hub_id,
      row?.asset_hub?.id,
      row?.asset_hub?.pk,
      row?.id,
    ]
    for (const c of candidates) {
      if (c !== undefined && c !== null && c !== '') return c as any
    }
    return null
  }

  // Helper: Build address string
  function buildAddress(row: any): string {
    const zip = row?.zip ?? row?.zip_code
    const parts = [row?.street_address, row?.city, row?.state, zip]
      .map((p: any) => (p != null ? String(p).trim() : ''))
      .filter((p: string) => !!p)
    return parts.join(', ')
  }

  // Open asset detail modal
  function openAssetModal(row: any): void {
    selectedId.value = getAssetHubIdFromRow(row)
    selectedRow.value = row
    selectedAddr.value = buildAddress(row)
    showAssetModal.value = true
  }

  // Open asset modal from external source (e.g., map marker)
  function openAssetModalFromMarker(payload: {
    assetHubId: string | number
    address?: string | null
  }): void {
    const id = payload?.assetHubId
    if (!id) return

    selectedId.value = id
    selectedRow.value = null // Will be loaded by LoanLevelIndex
    selectedAddr.value = payload.address ?? null
    showAssetModal.value = true
  }

  // Handle row loaded event from LoanLevelIndex
  function onLoanRowLoaded(row: any): void {
    selectedRow.value = row
    selectedAddr.value = buildAddress(row)
  }

  // Close asset modal and reset state
  function closeAssetModal(): { shouldRefresh: boolean } {
    const shouldRefresh = selectedId.value != null
    selectedId.value = null
    selectedRow.value = null
    selectedAddr.value = null
    return { shouldRefresh }
  }

  // Open full page view
  function openFullPage(): void {
    if (!selectedId.value) return

    const query: any = { id: selectedId.value }
    if (selectedAddr.value) query.addr = selectedAddr.value
    query.module = 'am'

    showAssetModal.value = false
    router.push({ path: '/loanlvl/products-details', query })
  }

  // Open add to list modal
  function openAddToListModal(params: {
    clickedRow?: any
    selectedRows: any[]
  }): void {
    const rowsToUse =
      params.selectedRows.length > 0
        ? params.selectedRows
        : params.clickedRow
        ? [params.clickedRow]
        : []

    selectedListAssetIds.value = rowsToUse
      .map((row: any) => getAssetHubIdFromRow(row))
      .filter((id: any) => id !== null && id !== undefined) as Array<
      string | number
    >

    showAddToListModal.value = true
  }

  // Reset add to list modal
  function resetAddToListModal(): void {
    newListName.value = ''
    newListDescription.value = ''
    selectedListAssetIds.value = []
    isSavingCustomList.value = false
  }

  // Save custom list
  async function saveCustomList(): Promise<{ success: boolean }> {
    if (!canSaveCustomList.value) return { success: false }

    isSavingCustomList.value = true
    try {
      const payload = {
        name: newListName.value.trim(),
        description: newListDescription.value.trim(),
        asset_ids: selectedListAssetIds.value,
      }

      await http.post('/am/custom-lists/', payload)

      showAddToListModal.value = false
      resetAddToListModal()
      return { success: true }
    } catch (error) {
      console.error('[AssetGrid] Failed to create custom list:', error)
      alert('Failed to create custom list. Please try again.')
      return { success: false }
    } finally {
      isSavingCustomList.value = false
    }
  }

  return {
    // Asset modal state
    showAssetModal,
    selectedId,
    selectedRow,
    selectedAddr,
    headerReady,
    modalIdText,
    modalTradeText,
    modalAddrText,

    // Custom list modal state
    showAddToListModal,
    newListName,
    newListDescription,
    selectedListAssetIds,
    isSavingCustomList,
    canSaveCustomList,

    // Methods
    openAssetModal,
    openAssetModalFromMarker,
    onLoanRowLoaded,
    closeAssetModal,
    openFullPage,
    openAddToListModal,
    resetAddToListModal,
    saveCustomList,
    getAssetHubIdFromRow,
  }
}
