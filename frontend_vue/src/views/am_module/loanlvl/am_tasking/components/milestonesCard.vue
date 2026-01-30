<!--
  WHAT: Milestones widget - CLEAN REBUILD
  WHY: Display upcoming task deadlines organized by track
  WHERE: AM Tasking tab, activity widgets row
  HOW: Fetches milestone data from backend API
-->
<template>
  <div class="milestones-card">
    <!-- Header -->
    <div class="milestones-card-header">
      <h4 class="milestones-card-title">Milestones</h4>
      <i class="mdi mdi-calendar-clock text-muted"></i>
    </div>

    <!-- Body -->
    <div class="milestones-card-body">
      <div v-if="!trackGroups || trackGroups.length === 0" class="text-muted small">
        No active tracks.
      </div>
      <div v-else class="track-groups">
        <!-- Loop through each track -->
        <div v-for="track in trackGroups" :key="track.trackName" class="track-section">
          <!-- Track Header -->
          <div class="track-header">
            <span :class="getTrackBadgeClass(track.trackName)">{{ track.trackName }}</span>
          </div>
          
          <!-- Current Task -->
          <div v-if="track.currentTask" class="task-item">
            <div class="task-content">
              <div class="task-info">
                <span class="task-label current">Current: {{ track.currentTask.label }}</span>
                <span class="task-due">Due: {{ fmtDate(track.currentTask.dueDate) }}</span>
              </div>
              <span v-if="track.currentTask.tone" :class="badgeClass(track.currentTask.tone)">
                {{ toneLabel(track.currentTask.tone) }}
              </span>
            </div>
          </div>
          
          <!-- Upcoming Task -->
          <div v-if="track.upcomingTask" class="task-item">
            <div class="task-content">
              <div class="task-info">
                <span class="task-label upcoming">Next: {{ track.upcomingTask.label }}</span>
                <span class="task-due">Due: {{ fmtDate(track.upcomingTask.dueDate) }}</span>
              </div>
              <span v-if="track.upcomingTask.tone" :class="badgeClass(track.upcomingTask.tone)">
                {{ toneLabel(track.upcomingTask.tone) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import http from '@/lib/http'
import { eventBus } from '@/lib/eventBus'

export type DeadlineTone = 'danger' | 'warning' | 'info' | 'secondary'

export interface DeadlineItem {
  id: number | string
  label: string
  dueDate: string
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

const trackGroups = ref<TrackGroup[]>([])

// WHAT: Load milestones from API
async function loadMilestones() {
  try {
    const response = await http.get(`/am/outcomes/track-milestones/`, {
      params: { asset_hub_id: props.hubId }
    })
    
    if (response.data && Array.isArray(response.data.tracks)) {
      trackGroups.value = response.data.tracks
    }
  } catch (err) {
    console.error('Failed to load milestones:', err)
    trackGroups.value = []
  }
}

// WHAT: Format date compactly
function fmtDate(d?: string | null): string {
  if (!d) return '—'
  try {
    const dt = new Date(d)
    return dt.toLocaleDateString('en-US', { month: 'numeric', day: 'numeric', year: '2-digit' })
  } catch {
    return d
  }
}

// WHAT: Get badge class for track name
function getTrackBadgeClass(trackName: string): string {
  const map: Record<string, string> = {
    'Foreclosure': 'badge bg-danger',
    'DIL': 'badge bg-primary',
    'Modification': 'badge bg-secondary',
    'REO': 'badge bg-info',
    'Short Sale': 'badge bg-warning',
    'Note Sale': 'badge bg-secondary',
    'Performing': 'badge bg-success',
    'Delinquent': 'badge bg-warning',
  }
  return map[trackName] || 'badge bg-secondary'
}

// WHAT: Get badge class for tone
function badgeClass(tone: DeadlineTone): string {
  return `badge bg-${tone}`
}

// WHAT: Get label for tone
function toneLabel(tone: DeadlineTone): string {
  const labels: Record<DeadlineTone, string> = {
    danger: 'Urgent',
    warning: 'Soon',
    info: 'Upcoming',
    secondary: 'Other',
  }
  return labels[tone] || 'Other'
}

// WHAT: Lifecycle hooks
onMounted(() => {
  loadMilestones()
  eventBus.on('task-created', loadMilestones)
  eventBus.on('task-updated', loadMilestones)
  eventBus.on('task-deleted', loadMilestones)
})

onBeforeUnmount(() => {
  eventBus.off('task-created', loadMilestones)
  eventBus.off('task-updated', loadMilestones)
  eventBus.off('task-deleted', loadMilestones)
})

watch(() => props.hubId, () => {
  if (props.hubId) {
    loadMilestones()
  }
})
</script>

<style scoped>
/* WHAT: Card container */
.milestones-card {
  background: #FDFBF7;
  border-radius: 0.375rem;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

/* WHAT: Card header */
.milestones-card-header {
  background: transparent;
  border-bottom: 1px solid #dee2e6;
  padding: 1rem;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.milestones-card-title {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0;
  color: #212529;
}

/* WHAT: Card body */
.milestones-card-body {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
}

/* WHAT: Track groups */
.track-groups {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.track-section {
  border-left: 3px solid #dee2e6;
  padding-left: 0.75rem;
}

.track-header {
  margin-bottom: 0.5rem;
}

.track-header .badge {
  font-size: 0.7rem;
  font-weight: 600;
}

/* WHAT: Task items */
.task-item {
  background: #f8f9fa;
  border-radius: 0.25rem;
  padding: 0.5rem;
  border-left: 2px solid #dee2e6;
  margin-bottom: 0.5rem;
}

.task-item:last-child {
  margin-bottom: 0;
}

.task-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.task-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.task-label {
  font-weight: 600;
  font-size: 0.875rem;
}

.task-label.current {
  color: #0d6efd;
}

.task-label.upcoming {
  color: #6c757d;
}

.task-due {
  color: #6c757d;
  font-size: 0.75rem;
}

.task-content .badge {
  font-size: 0.7rem;
  flex-shrink: 0;
}
</style>
