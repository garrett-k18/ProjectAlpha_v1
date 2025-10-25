// ============================================================================
// WHAT: Composable for automatic data refresh functionality
// WHY: Reusable pattern for components that need to refresh on data changes
// WHERE: Used by components that display data that can be modified elsewhere
// HOW: Provides event listeners and emit helpers for data synchronization
// ============================================================================

import { onMounted, onBeforeUnmount } from 'vue'
import { eventBus, refreshHubData } from '@/lib/eventBus'

/**
 * WHAT: Composable for automatic data refresh
 * WHY: Standardize refresh behavior across components
 * WHERE: Use in components that display data modified by other components
 * HOW: Setup event listeners and provide refresh helper functions
 */
export function useDataRefresh(hubId: number, refreshCallback: () => void) {
  // WHAT: Event listener for data refresh
  // WHY: Reload data when other components modify it
  // HOW: Check hubId matches and call refresh callback
  const handleDataRefresh = (payload: { hubId: number }) => {
    if (payload.hubId === hubId) {
      console.log('Refreshing data due to change event')
      refreshCallback()
    }
  }

  // WHAT: Setup event listeners on mount
  // WHY: Listen for all types of data changes
  onMounted(() => {
    eventBus.on('data:refresh', handleDataRefresh)
    eventBus.on('milestones:refresh', handleDataRefresh)
    eventBus.on('track:added', handleDataRefresh)
    eventBus.on('track:updated', handleDataRefresh)
    eventBus.on('track:deleted', handleDataRefresh)
    eventBus.on('task:added', handleDataRefresh)
    eventBus.on('task:updated', handleDataRefresh)
    eventBus.on('task:deleted', handleDataRefresh)
  })

  // WHAT: Cleanup event listeners on unmount
  // WHY: Prevent memory leaks
  onBeforeUnmount(() => {
    eventBus.off('data:refresh', handleDataRefresh)
    eventBus.off('milestones:refresh', handleDataRefresh)
    eventBus.off('track:added', handleDataRefresh)
    eventBus.off('track:updated', handleDataRefresh)
    eventBus.off('track:deleted', handleDataRefresh)
    eventBus.off('task:added', handleDataRefresh)
    eventBus.off('task:updated', handleDataRefresh)
    eventBus.off('task:deleted', handleDataRefresh)
  })

  // WHAT: Helper functions for emitting events
  // WHY: Standardize how components notify others of changes
  // HOW: Emit specific events with proper payload structure
  return {
    // WHAT: Emit when a track/outcome is added
    emitTrackAdded: (trackType: string) => {
      eventBus.emit('track:added', { trackType, hubId })
      refreshHubData(hubId)
    },

    // WHAT: Emit when a track/outcome is updated
    emitTrackUpdated: (trackType: string) => {
      eventBus.emit('track:updated', { trackType, hubId })
      refreshHubData(hubId)
    },

    // WHAT: Emit when a track/outcome is deleted
    emitTrackDeleted: (trackType: string) => {
      eventBus.emit('track:deleted', { trackType, hubId })
      refreshHubData(hubId)
    },

    // WHAT: Emit when a task is added
    emitTaskAdded: (trackType: string, taskId: number) => {
      eventBus.emit('task:added', { trackType, taskId, hubId })
      refreshHubData(hubId)
    },

    // WHAT: Emit when a task is updated
    emitTaskUpdated: (trackType: string, taskId: number) => {
      eventBus.emit('task:updated', { trackType, taskId, hubId })
      refreshHubData(hubId)
    },

    // WHAT: Emit when a task is deleted
    emitTaskDeleted: (trackType: string, taskId: number) => {
      eventBus.emit('task:deleted', { trackType, taskId, hubId })
      refreshHubData(hubId)
    },

    // WHAT: Emit general data refresh
    emitDataRefresh: () => {
      refreshHubData(hubId)
    }
  }
}
