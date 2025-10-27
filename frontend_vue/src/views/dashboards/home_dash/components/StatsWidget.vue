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
      <div class="card border h-100">
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
            <h5 class="mb-0">{{ stat.value }}</h5>
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
  
  data() {
    return {
      // stats: array of compact metric tiles
      // Each object includes: label (string), value (string/number), icon (mdi class)
      stats: [
        { label: "Total AUM", value: "1,248", icon: "mdi mdi-home-city" },
        { label: "Liquidated Assets", value: "32", icon: "mdi mdi-clipboard-text" },
        { label: "TBD", value: "87", icon: "mdi mdi-account-tie" },
        { label: "TBD", value: "542", icon: "mdi mdi-file-document" },
      ],
    };
  },
});
</script>
