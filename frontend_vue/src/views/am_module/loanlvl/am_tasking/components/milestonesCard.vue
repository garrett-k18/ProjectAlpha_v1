<template>
  <!--
    WHAT
    - A small card that lists upcoming deadlines (due dates) across outcomes/tasks.

    WHY
    - Gives a quick glance at what's due soon without opening each card.

    WHERE
    - AM Tasking (loan-level) page, typically near KPIs or Recent Activity.

    HOW
    - Pass an array of DeadlineItem via the `items` prop.
    - Each item shows a label, a due date (compact), and an optional tone badge.
  -->
  <div class="card h-100">
    <div class="card-header d-flex align-items-center justify-content-between">
      <h4 class="header-title mb-0">Milestones</h4>
      <i class="mdi mdi-calendar-clock text-muted"></i>
    </div>
    <div class="card-body py-2">
      <div v-if="!trackGroups || trackGroups.length === 0" class="text-muted small">No active tracks.</div>
      <div v-else class="track-groups">
        <!-- Loop through each track -->
        <div v-for="track in trackGroups" :key="track.trackName" class="track-section mb-3">
          <!-- Track Header -->
          <div class="track-header d-flex align-items-center mb-2">
            <span :class="getTrackBadgeClass(track.trackName)" class="me-2">{{ track.trackName }}</span>
          </div>
          
          <!-- Current Task -->
          <div v-if="track.currentTask" class="task-item mb-2">
            <div class="d-flex align-items-center justify-content-between">
              <div class="d-flex flex-column">
                <span class="fw-bold text-primary small">Current: {{ track.currentTask.label }}</span>
                <span class="text-muted" style="font-size: 0.75rem;">Due: {{ fmtDate(track.currentTask.dueDate) }}</span>
              </div>
              <span v-if="track.currentTask.tone" :class="badgeClass(track.currentTask.tone)" style="font-size: 0.7rem;">{{ toneLabel(track.currentTask.tone) }}</span>
            </div>
          </div>
          
          <!-- Upcoming Task -->
          <div v-if="track.upcomingTask" class="task-item">
            <div class="d-flex align-items-center justify-content-between">
              <div class="d-flex flex-column">
                <span class="fw-bold text-secondary small">Next: {{ track.upcomingTask.label }}</span>
                <span class="text-muted" style="font-size: 0.75rem;">Due: {{ fmtDate(track.upcomingTask.dueDate) }}</span>
              </div>
              <span v-if="track.upcomingTask.tone" :class="badgeClass(track.upcomingTask.tone)" style="font-size: 0.7rem;">{{ toneLabel(track.upcomingTask.tone) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// WHAT: Milestones card - self-contained component for AM Tasking
// WHY: Display upcoming deadlines/milestones for the asset
// WHERE: AM Tasking page, activity widgets row
// HOW: Accepts hubId prop, fetches and displays milestone data
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import http from '@/lib/http'
import { eventBus } from '@/lib/eventBus'

export type DeadlineTone = 'danger' | 'warning' | 'info' | 'secondary'
export interface DeadlineItem {
  id: number | string  // Allow both number and string for demo data
  label: string
  dueDate: string // ISO or display string; we format compactly
  tone?: DeadlineTone
}

export interface TrackGroup {
  trackName: string
  currentTask?: DeadlineItem
  upcomingTask?: DeadlineItem
}

const props = defineProps<{
  hubId: number
}>()

// WHAT: Track groups with current and upcoming tasks
// WHY: Store organized task data by track type
// WHERE: Populated by loadMilestones()
const trackGroups = ref<TrackGroup[]>([])

// WHAT: Load milestones for this asset hub
// WHY: Fetch deadline data from backend and organize by track
// HOW: Call track-milestones API endpoint
async function loadMilestones() {
  try {
    console.log('Loading milestones for hubId:', props.hubId)
    
    // WHAT: Call backend API for track milestones
    // WHY: Get real task progression data organized by track
    // WHERE: /api/am/outcomes/track-milestones/?asset_hub_id=${hubId}
    const response = await http.get(`/am/outcomes/track-milestones/`, {
      params: { asset_hub_id: props.hubId }
    })
    
    console.log('Milestones API response:', response.data)
    
    // WHAT: Transform backend data to match frontend interface
    // WHY: Backend uses snake_case, frontend uses camelCase
    // HOW: Map response fields to expected format
    trackGroups.value = response.data.map((track: any) => ({
      trackName: track.track_name,
      currentTask: track.current_task ? {
        id: track.current_task.id,
        label: track.current_task.label,
        dueDate: track.current_task.due_date,
        tone: track.current_task.tone
      } : null,
      upcomingTask: track.upcoming_task ? {
        id: track.upcoming_task.id,
        label: track.upcoming_task.label,
        dueDate: track.upcoming_task.due_date,
        tone: track.upcoming_task.tone
      } : null
    }))
    
    console.log('Transformed trackGroups:', trackGroups.value)
    
    // WHAT: Log empty response for debugging
    // WHY: Help identify why real data isn't being returned
    if (trackGroups.value.length === 0) {
      console.log('No milestone data returned from API - check Django logs for debug info')
    }
  } catch (err: any) {
    console.error('Failed to load track milestones:', err)
    console.error('Error details:', err.response?.data)
    console.error('Error status:', err.response?.status)
    // WHAT: Fallback to empty state on error
    // WHY: Prevent UI crashes, show "No active tracks" message
    trackGroups.value = []
  }
}

// WHAT: Event listener for data refresh
// WHY: Reload milestones when other components modify data
// HOW: Listen for refresh events and reload if hubId matches
const handleDataRefresh = (payload: { hubId: number }) => {
  if (payload.hubId === props.hubId) {
    console.log('Refreshing milestones due to data change')
    loadMilestones()
  }
}

// WHAT: Load milestones on mount and when hubId changes
// WHY: Keep data fresh when navigating between assets
watch(() => props.hubId, () => {
  if (props.hubId) loadMilestones()
}, { immediate: true })

// WHAT: Setup event listeners on mount
// WHY: Listen for data changes from other components
onMounted(() => {
  eventBus.on('milestones:refresh', handleDataRefresh)
  eventBus.on('data:refresh', handleDataRefresh)
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
  eventBus.off('milestones:refresh', handleDataRefresh)
  eventBus.off('data:refresh', handleDataRefresh)
  eventBus.off('track:added', handleDataRefresh)
  eventBus.off('track:updated', handleDataRefresh)
  eventBus.off('track:deleted', handleDataRefresh)
  eventBus.off('task:added', handleDataRefresh)
  eventBus.off('task:updated', handleDataRefresh)
  eventBus.off('task:deleted', handleDataRefresh)
})

// WHAT: Helper functions for formatting and styling
// WHY: Format dates and style badges consistently
function fmtDate(iso: string): string {
  try {
    const d = new Date(iso)
    return d.toLocaleDateString(undefined, { year: '2-digit', month: 'numeric', day: 'numeric' })
  } catch { return iso }
}

function badgeClass(tone?: DeadlineTone): string {
  if (!tone) return 'badge bg-secondary-subtle text-secondary'
  const map: Record<DeadlineTone, string> = {
    danger: 'badge bg-danger-subtle text-danger',
    warning: 'badge bg-warning-subtle text-warning',
    info: 'badge bg-info-subtle text-info',
    secondary: 'badge bg-secondary-subtle text-secondary',
  }
  return map[tone] ?? map.secondary
}

function toneLabel(tone?: DeadlineTone): string {
  const map: Record<DeadlineTone, string> = {
    danger: 'Urgent',
    warning: 'Soon',
    info: 'Info',
    secondary: 'Other',
  }
  return tone ? map[tone] : 'Other'
}

/**
 * Get badge class for track names
 * WHAT: Returns Bootstrap badge classes for different track types
 * WHY: Visual distinction between different outcome tracks
 * HOW: Maps track names to appropriate badge colors
 */
function getTrackBadgeClass(trackName: string): string {
  const trackMap: Record<string, string> = {
    'Foreclosure': 'badge bg-danger-subtle text-danger',
    'Modification': 'badge bg-secondary-subtle text-secondary',
    'Short Sale': 'badge bg-warning-subtle text-warning',
    'Deed-in-Lieu': 'badge bg-primary-subtle text-primary',
    'DIL': 'badge bg-primary-subtle text-primary',
    'FC': 'badge bg-danger-subtle text-danger',
    'MOD': 'badge bg-secondary-subtle text-secondary',
    'SS': 'badge bg-warning-subtle text-warning'
  }
  return trackMap[trackName] || 'badge bg-secondary-subtle text-secondary'
}
</script>

<style scoped>
/* ============================================================================ */
/* TRACK GROUPING STYLES */
/* ============================================================================ */

.track-section {
  border-left: 3px solid #e9ecef;
  padding-left: 0.75rem;
}

.track-section:last-child {
  margin-bottom: 0 !important;
}

.task-item {
  background: #f8f9fa;
  border-radius: 0.25rem;
  padding: 0.5rem;
  border-left: 2px solid #dee2e6;
}

.task-item:hover {
  background: #e9ecef;
  transition: background-color 0.15s ease;
}

/* Track badge styling */
.track-header .badge {
  font-size: 0.7rem;
  font-weight: 600;
}
</style>
