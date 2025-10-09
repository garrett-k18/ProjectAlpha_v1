<template>
  <!--
    Quick Links Widget
    Compact navigation buttons for primary app areas
    Component path: frontend_vue/src/views/home_dash/components/QuickLinksWidget.vue
  -->
  <div class="d-flex align-items-center gap-3 flex-wrap">
    <span class="text-muted fw-semibold">Quick Links:</span>
    <div class="d-flex gap-2 flex-wrap">
      <router-link 
        v-for="(item, idx) in quickLinks" 
        :key="`ql-${idx}`" 
        :to="item.to" 
        class="btn btn-sm border bg-white text-primary"
      >
        {{ item.title }}
      </router-link>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'QuickLinksWidget',
  
  data() {
    return {
      // quickLinks: compact navigation buttons for primary app areas
      // "to" values map to absolute paths defined in src/router/routes.ts
      quickLinks: [
        { title: "Acquisitions", to: "/acquisitions" },
        { title: "Asset Management", to: "/asset-mgmt" },
        { title: "CRM", to: "/crm" },
        { title: "Calendar", to: "/apps/calendar" },
      ],
    };
  },
});
</script>
