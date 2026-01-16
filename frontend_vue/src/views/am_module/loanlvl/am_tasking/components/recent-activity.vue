<template>
  <div class="card h-100">
    <div class="card-header d-flex justify-content-between align-items-center">
      <h4 class="header-title">{{ title }}</h4>
    </div>

    <simplebar class="card-body py-0 mb-3" :style="`max-height:${activityWindowHeight}`">
      <div class="timeline-alt py-0">
        <div v-for="activity in activityData" :key="activity.id" class="timeline-item">
          <i
              :class="`mdi ${activity.icon} bg-${activity.color}-lighten text-${activity.color} timeline-icon`"
          ></i>
          <div class="timeline-item-info">
            <a
                href="#"
                class="text-body fw-bold mb-1 d-block"
            >
              <span v-if="activity.badgeText" :class="`badge bg-${activity.badgeColor || 'secondary'} me-1`">{{ activity.badgeText }}</span>
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


<script lang="ts">
// WHAT: Small, scrollable "recent activity" timeline used in AM Tasking.
// WHY: Shows a list of colored events with titles and short descriptions.
// WHERE: Feature: am_tasking (loan-level); can be reused in other panels.
// HOW: Pass an array of ActivityItem via the `activityData` prop.
import simplebar from 'simplebar-vue'
import type { PropType } from 'vue'

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

/**
 * Recent-activity component
 * 1. User specifies the title of window using the 'title' input property.
 * 2. Window height set using the 'activityWindowHeight' input property. Height would count in pixel.
 * 3. Activitydata array specify the id, icon, title, text, subtext, boldText, color
 *    id - Unique id of activity
 *    icon - Activity icon name
 *    title - Activity name specified in title.
 *    text - Activity description specify in text.
 *    subtext - Activity performed on which time, that specified in subtext.
 *    boldText - From activity description the highlight words of text specified using boldText
 *    color - Activity icon color specify using the color
 */
export default {
  components: {
    simplebar,
  },
  props: {
    title: {
      type: String,
      default: 'Recent Activity',
    },
    activityWindowHeight: {
      type: String,
      default: '424',
    },
    activityData: {
      type: Array as PropType<ActivityItem[]>,
      default: () => [],
    },
  },
}
</script>

