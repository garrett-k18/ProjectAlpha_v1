<template>
  <div class="card">
    <div class="card-header d-flex justify-content-between align-items-center">
      <h4 class="header-title">{{ title }}</h4>
      <div class="float-end">
        <b-dropdown toggle-class="arrow-none card-drop p-0" variant="white" right>
          <template v-slot:button-content>
            <i class="mdi mdi-dots-vertical"></i>
          </template>
          <b-dropdown-item href="javascript:void(0);">Sales Report</b-dropdown-item>
          <b-dropdown-item href="javascript:void(0);">Export Report</b-dropdown-item>
          <b-dropdown-item href="javascript:void(0);">Profit</b-dropdown-item>
          <b-dropdown-item href="javascript:void(0);">Action</b-dropdown-item>
        </b-dropdown>
      </div>
    </div>

    <simplebar class="card-body py-0 mb-3" :style="`max-height:${activityWindowHeight}`">
      <div class="timeline-alt py-0">
        <div v-for="activity of activityData" :key="activity.id" class="timeline-item">
          <i
              :class="`mdi ${activity.icon} bg-${activity.color}-lighten text-${activity.color} timeline-icon`"
          ></i>
          <div class="timeline-item-info">
            <a
                href="#"
                :class="`text-${activity.color} fw-bold mb-1 d-block`"
            >{{ activity.title }}</a>
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
import simplebar from 'simplebar-vue'

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
      type: Array,
      default: function () {
        return []
      },
    },
  },
}
</script>

