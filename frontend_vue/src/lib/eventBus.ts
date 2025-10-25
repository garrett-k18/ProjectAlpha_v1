// ============================================================================
// WHAT: Event bus for cross-component communication
// WHY: Allow components to notify each other of data changes without tight coupling
// WHERE: Used throughout AM Tasking components for reactive updates
// HOW: Simple event emitter implementation using Map
// ============================================================================

// WHAT: Define event types for type safety
// WHY: Ensure consistent event names and payload types
export type Events = {
  // Track/outcome events
  'track:added': { trackType: string; hubId: number }
  'track:deleted': { trackType: string; hubId: number }
  'track:updated': { trackType: string; hubId: number }
  
  // Task events  
  'task:added': { trackType: string; taskId: number; hubId: number }
  'task:updated': { trackType: string; taskId: number; hubId: number }
  'task:deleted': { trackType: string; taskId: number; hubId: number }
  
  // General refresh events
  'data:refresh': { hubId: number }
  'milestones:refresh': { hubId: number }
}

// WHAT: Simple event bus implementation
// WHY: Lightweight alternative to external libraries
// HOW: Map-based event listener storage with emit/on/off methods
class EventBus {
  private events = new Map<keyof Events, Array<(payload: any) => void>>()

  // WHAT: Register event listener
  // WHY: Components can subscribe to specific events
  on<K extends keyof Events>(event: K, callback: (payload: Events[K]) => void) {
    if (!this.events.has(event)) {
      this.events.set(event, [])
    }
    this.events.get(event)!.push(callback)
  }

  // WHAT: Remove event listener
  // WHY: Prevent memory leaks when components unmount
  off<K extends keyof Events>(event: K, callback: (payload: Events[K]) => void) {
    const listeners = this.events.get(event)
    if (listeners) {
      const index = listeners.indexOf(callback)
      if (index > -1) {
        listeners.splice(index, 1)
      }
    }
  }

  // WHAT: Emit event to all listeners
  // WHY: Notify all subscribed components of data changes
  emit<K extends keyof Events>(event: K, payload: Events[K]) {
    const listeners = this.events.get(event)
    if (listeners) {
      listeners.forEach(callback => callback(payload))
    }
  }
}

// WHAT: Create and export event bus instance
// WHY: Single source of truth for all cross-component events
export const eventBus = new EventBus()

// WHAT: Helper function to emit data refresh for specific hub
// WHY: Common pattern - refresh all components when data changes
// HOW: Emit multiple specific events that components can listen to
export function refreshHubData(hubId: number) {
  eventBus.emit('data:refresh', { hubId })
  eventBus.emit('milestones:refresh', { hubId })
}
