/**
 * Full Window Mode Composable
 * Manages full-window toggle and document body overflow locking
 */

import { ref, onBeforeUnmount } from 'vue'

export function useFullWindowMode() {
  const isFullWindow = ref<boolean>(false)
  const bodyOverflowStack = ref<number>(0)

  // Toggle full window mode
  function toggleFullWindow(): void {
    const next = !isFullWindow.value
    isFullWindow.value = next
    manageDocumentOverflow(next)
  }

  // Manage document body overflow locking
  function manageDocumentOverflow(lock: boolean): void {
    const body = document.body
    if (!body) return

    if (lock) {
      bodyOverflowStack.value += 1
      if (bodyOverflowStack.value === 1) {
        body.dataset.assetGridOverflow = body.style.overflow || ''
        body.style.overflow = 'hidden'
      }
    } else {
      bodyOverflowStack.value = Math.max(0, bodyOverflowStack.value - 1)
      if (bodyOverflowStack.value === 0) {
        const prev = body.dataset.assetGridOverflow ?? ''
        body.style.overflow = prev
        delete body.dataset.assetGridOverflow
      }
    }
  }

  // Cleanup on unmount
  onBeforeUnmount(() => {
    if (isFullWindow.value) {
      manageDocumentOverflow(false)
    }
  })

  return {
    isFullWindow,
    toggleFullWindow,
  }
}
