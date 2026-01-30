<!--
  WHAT: Recent Activity timeline widget - CLEAN REBUILD
  WHY: Display recent activity events in a scrollable timeline
  WHERE: AM Tasking tab, activity widgets row
  HOW: Pass activityData array with ActivityItem objects
-->
<template>
  <div class="activity-card">
    <!-- Header -->
    <div class="activity-card-header">
      <h4 class="activity-card-title">{{ title }}</h4>
    </div>

    <!-- Body with scrollable content -->
    <simplebar class="activity-card-body">
      <div class="timeline-alt">
        <div v-for="activity in activityData" :key="activity.id" class="timeline-item">
          <i :class="`mdi ${activity.icon} bg-${activity.color}-lighten text-${activity.color} timeline-icon`"></i>
          <div class="timeline-item-info">
            <a href="#" class="text-body fw-bold mb-1 d-block">
              <span v-if="activity.badgeText" :class="`badge bg-${activity.badgeColor || 'secondary'} me-1`">
                {{ activity.badgeText }}
              </span>
              {{ activity.title }}
            </a>
            <small>
              {{ activity.text }}
              <span class="fw-bold">{{ activity.boldText }}</span>
            </small>
            <p class="mb-0 pb-2">
              <small class="text-muted">{{ activity.subtext }}</small>
            </p>
          </div>
        </div>
      </div>
    </simplebar>
  </div>
</template>

<script setup lang="ts">
import { type PropType } from 'vue'
import simplebar from 'simplebar-vue'

// WHAT: Activity item data structure
export interface ActivityItem {
  id: number
  icon: string
  title: string
  text: string
  subtext: string
  boldText?: string
  color: 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'secondary' | string
  badgeText?: string
  badgeColor?: 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'secondary' | string
}

// WHAT: Component props
const props = defineProps({
  title: {
    type: String,
    default: 'Recent Activity',
  },
  activityWindowHeight: {
    type: String,
    default: '280px',
  },
  activityData: {
    type: Array as PropType<ActivityItem[]>,
    default: () => [],
  },
})
</script>

<style scoped>
/* WHAT: Card container - fills parent with consistent background */
/* WHY: Ensure no gaps or color mismatches */
.activity-card {
  background: #FDFBF7;
  border-radius: 0.375rem;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

/* WHAT: Card header styling */
.activity-card-header {
  background: transparent;
  border-bottom: 1px solid #dee2e6;
  padding: 1rem;
  flex-shrink: 0;
}

.activity-card-title {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0;
  color: #212529;
}

/* WHAT: Card body - scrollable content area */
.activity-card-body {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
  max-height: v-bind(activityWindowHeight);
}

/* WHAT: Timeline styles */
.timeline-alt {
  padding: 0;
}
</style>
