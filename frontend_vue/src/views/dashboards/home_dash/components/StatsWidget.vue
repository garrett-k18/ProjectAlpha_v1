<template>
  <!--
    Stats Widget
    Displays key metrics tiles (Assets, Tasks, Brokers, Docs)
    Component path: frontend_vue/src/views/dashboards/home_dash/components/StatsWidget.vue
  -->
  <b-row>
    <b-col 
      v-for="(stat, idx) in stats" 
      :key="`stat-${idx}`" 
      cols="12" 
      md="6" 
      xl="3" 
      class="mb-2"
    >
      <div class="card border h-100 cursor-pointer hover-card" :title="stat.description" @click="handleClick(idx)">
        <div class="card-body d-flex align-items-center py-2">
          <!-- Icon circle -->
          <div class="me-2 flex-shrink-0">
            <div class="avatar-xs">
              <span class="avatar-title rounded bg-primary text-white">
                <i :class="stat.icon"></i>
              </span>
            </div>
          </div>
          <!-- Metric content -->
          <div class="flex-grow-1">
            <div class="text-muted text-uppercase small mb-0">{{ stat.label }}</div>
            <h5 class="mb-0 fw-bold">{{ stat.value }}</h5>
          </div>
          <!-- Arrow icon to indicate clickability -->
          <div class="ms-2">
            <i class="mdi mdi-chevron-right text-muted"></i>
          </div>
        </div>
      </div>
    </b-col>
  </b-row>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'StatsWidget',
  emits: ['open-pipeline'],
  data() {
    return {
      // stats: array of user-specific metric tiles for personalized dashboard
      // Each object includes: label (string), value (string/number), icon (mdi class)
      // Note: These are placeholder values. Wire to backend API via Pinia store for real data.
      stats: [
        { 
          label: "My Pipeline", 
          value: "12", 
          icon: "mdi mdi-clipboard-check-outline",
          description: "View your asset pipeline breakdown"
        },
        { 
          label: "My Follow Ups", 
          value: "34", 
          icon: "mdi mdi-home-city-outline",
          description: "Loans you're currently managing"
        },
        { 
          label: "Pending Reviews", 
          value: "8", 
          icon: "mdi mdi-file-document-edit-outline",
          description: "Items awaiting your approval"
        },
        { 
          label: "Notifications", 
          value: "5", 
          icon: "mdi mdi-bell-outline",
          description: "Unread updates and alerts"
        },
      ],
    };
  },
  methods: {
    handleClick(idx: number) {
      if (idx === 0) {
        this.$emit('open-pipeline');
      }
    },
  },
});
</script>

<style scoped>
/* Hover effect for stat cards */
.hover-card {
  transition: all 0.2s ease-in-out;
}

.hover-card:hover {
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

/* Cursor pointer for clickable cards */
.cursor-pointer {
  cursor: pointer;
}
</style>
