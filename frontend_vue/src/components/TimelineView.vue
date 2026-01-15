<template>
  <div class="timeline-view">
    <Timeline :value="events" layout="horizontal" align="alternate">
      <template #content="slotProps">
        <div class="timeline-content">
          <div class="fw-semibold">{{ slotProps.item.status }}</div>
          <div class="text-muted small">{{ slotProps.item.date }}</div>
        </div>
      </template>
    </Timeline>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Timeline from 'primevue/timeline'

const events = ref([
  {
    status: 'Acquisition',
    date: '10/09/2025',
    icon: 'ri-home-4-line',
    color: '#0d6efd',
    description: 'Asset acquired and onboarded into portfolio'
  },
  {
    status: 'Processing',
    date: '15/10/2020 14:00',
    icon: 'pi pi-cog',
    color: '#673AB7',
    description: 'Inventore sed consequuntur error repudiandae numquam deserunt.'
  },
  {
    status: 'Shipped',
    date: '15/10/2020 16:15',
    icon: 'pi pi-shopping-cart',
    color: '#FF9800',
    description: 'Quisquam repellat libero asperiores earum nam nobis.'
  },
  {
    status: 'Delivered',
    date: '16/10/2020 10:00',
    icon: 'pi pi-check',
    color: '#607D8B',
    description: 'Culpa ratione quam perferendis esse, cupiditate neque quas!'
  }
])
</script>

<style scoped>
.timeline-view {
  padding: 1rem;
  overflow-x: auto;
}

:deep(.p-timeline-horizontal) {
  min-width: max-content;
}

.timeline-content {
  text-align: center;
  padding: 0.5rem;
}
</style>
