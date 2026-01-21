/**
 * Asset Grid Pagination Composable
 * Manages pagination state and navigation
 */

import { ref, computed } from 'vue'

export function useAssetPagination() {
  const page = ref<number>(1)
  const pageSize = ref<number>(50)
  const pageSizeSelection = ref<number | 'ALL'>(50)
  const viewAll = ref<boolean>(false)
  const totalCount = ref<number | null>(null)
  const totalPages = ref<number | null>(null)

  // Check if pagination controls should be disabled
  const canGoToPrevPage = computed(() => page.value > 1 && !viewAll.value)
  const canGoToNextPage = computed(() => {
    const tp = totalPages.value || 1
    return page.value < tp && !viewAll.value
  })

  // Get pagination params for API request
  function getPaginationParams(): Record<string, any> {
    return {
      page: page.value,
      page_size: pageSize.value,
    }
  }

  // Update pagination from API response
  function updateFromResponse(data: any): void {
    totalCount.value = typeof data?.count === 'number' ? data.count : null

    if (totalCount.value != null && pageSize.value > 0) {
      totalPages.value = Math.max(1, Math.ceil(totalCount.value / pageSize.value))
    } else {
      totalPages.value = null
    }
  }

  // Handle page size change
  function handlePageSizeChange(): { shouldFetchAll: boolean } {
    if (pageSizeSelection.value === 'ALL') {
      viewAll.value = true
      return { shouldFetchAll: true }
    } else {
      viewAll.value = false
      const newSize =
        typeof pageSizeSelection.value === 'number'
          ? pageSizeSelection.value
          : Number(pageSizeSelection.value)

      if (newSize > 0 && Number.isFinite(newSize)) {
        pageSize.value = newSize
      }
      page.value = 1
      return { shouldFetchAll: false }
    }
  }

  // Navigate to previous page
  function prevPage(): boolean {
    if (!canGoToPrevPage.value) return false
    page.value -= 1
    return true
  }

  // Navigate to next page
  function nextPage(): boolean {
    if (!canGoToNextPage.value) return false
    page.value += 1
    return true
  }

  // Reset to first page (used when filters change)
  function resetToFirstPage(): void {
    page.value = 1
  }

  // Reset pagination state
  function resetPagination(): void {
    totalCount.value = null
    totalPages.value = null
  }

  // Sync page size on mount (handles browser autofill)
  function syncPageSize(): void {
    if (pageSizeSelection.value !== 'ALL' && typeof pageSizeSelection.value === 'number') {
      pageSize.value = pageSizeSelection.value
    }
  }

  return {
    // State
    page,
    pageSize,
    pageSizeSelection,
    viewAll,
    totalCount,
    totalPages,

    // Computed
    canGoToPrevPage,
    canGoToNextPage,

    // Methods
    getPaginationParams,
    updateFromResponse,
    handlePageSizeChange,
    prevPage,
    nextPage,
    resetToFirstPage,
    resetPagination,
    syncPageSize,
  }
}
