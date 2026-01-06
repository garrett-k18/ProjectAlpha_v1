<template>
  <!--
    Stats Widget
    Displays key metrics tiles (Assets, Tasks, Brokers, Docs)
    Component path: frontend_vue/src/views/dashboards/home_dash/components/StatsWidget.vue
  -->
  <b-row class="g-2">
    <b-col 
      v-for="(stat, idx) in stats" 
      :key="`stat-${idx}`"
    >
      <div class="card border h-100 cursor-pointer hover-card" :title="stat.description" @click="handleClick(idx)">
        <div class="card-body d-flex align-items-center py-1">
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
  emits: ['open-pipeline', 'open-followups', 'open-trades'],
  props: {
    followupCount: {
      type: [String, Number],
      default: null,
    },
    tradesCount: {
      type: [String, Number],
      default: null,
    },
  },
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
          label: "My Tasks", 
          value: "5", 
          icon: "mdi mdi-bell-outline",
          description: "Unread updates and alerts"
        },
        { 
          label: "My Lists", 
          value: "0", 
          icon: "mdi mdi-plus-circle-outline",
          description: "New metric item"
        },
        { 
          label: "Active Trades", 
          value: "0", 
          icon: "mdi mdi-swap-horizontal-bold",
          description: "Active trades with assets"
        },
      ],
    };
  },
  watch: {
    followupCount: {
      immediate: true,
      handler(val: string | number | null) {
        if (val == null) return
        if (!Array.isArray((this as any).stats) || (this as any).stats.length < 2) return
        ;(this as any).stats[1].value = String(val)
      },
    },
    tradesCount: {
      immediate: true,
      handler(val: string | number | null) {
        if (val == null) return
        if (!Array.isArray((this as any).stats) || (this as any).stats.length < 5) return
        ;(this as any).stats[4].value = String(val)
      },
    },
  },
  methods: {
    handleClick(idx: number) {
      if (idx === 0) {
        this.$emit('open-pipeline');
      } else if (idx === 1) {
        this.$emit('open-followups');
      } else if (idx === 4) {
        this.$emit('open-trades');
      }
      // idx 2 = My Tasks, idx 3 = New Item - add handlers as needed
    },
  },
});
</script>

<style scoped>
/* Hover effect for stat cards */
.hover-card {
  transition: all 0.2s ease;
  background-color: #F5F3EE !important;
  border: none !important;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2) !important;
}

.hover-card:hover {
  background-color: #D4AF37 !important;
  color: #ffffff !important;
  border: none !important;
  box-shadow: 0 4px 12px rgba(212, 175, 55, 0.4) !important;
  transform: translateX(4px);
}

.hover-card:hover .text-muted,
.hover-card:hover .text-uppercase,
.hover-card:hover span,
.hover-card:hover h5,
.hover-card:hover i {
  color: #ffffff !important;
}

/* Cursor pointer for clickable cards */
.cursor-pointer {
  cursor: pointer;
}
</style>
