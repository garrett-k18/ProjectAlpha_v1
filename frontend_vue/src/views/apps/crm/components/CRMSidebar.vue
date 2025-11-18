<template>
  <!--
    CRM Sidebar Component
    Sidebar selector for switching between CRM types (Brokers, Trading Partners, etc.)
    Component path: frontend_vue/src/views/apps/crm/components/CRMSidebar.vue
  -->
  <div class="card h-100">
    <div class="card-header">
      <h5 class="card-title mb-0">CRM Lists</h5>
    </div>
    <div class="card-body p-0">
      <div class="crm-list">
        <div
          v-for="crmType in crmTypes"
          :key="crmType.key"
          class="crm-list-item"
          :class="{ 'crm-list-item-selected': crmType.key === modelValue }"
          role="button"
          @click="$emit('update:modelValue', crmType.key)"
        >
          <span class="crm-item-icon">
            <i :class="crmType.icon"></i>
          </span>
          <div class="crm-item-content">
            <div class="crm-item-title">{{ crmType.label }}</div>
            <small class="crm-item-caption">{{ crmType.caption }}</small>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, type PropType } from 'vue'

export interface CRMType {
  key: string
  label: string
  caption: string
  icon: string
}

export default defineComponent({
  name: 'CRMSidebar',
  
  props: {
    crmTypes: {
      type: Array as PropType<CRMType[]>,
      required: true,
    },
    modelValue: {
      type: String,
      required: true,
    },
  },
  
  emits: ['update:modelValue'],
})
</script>

<style scoped>
.crm-list-item {
  display: flex;
  align-items: flex-start;
  padding: 0.75rem 0.5rem; /* Reduced padding for narrower sidebar */
  border-bottom: 1px solid #dee2e6;
  cursor: pointer;
}

.crm-list-item:not(.crm-list-item-selected):hover {
  background-color: #f8f9fa;
}

.crm-item-icon {
  margin-right: 0.375rem; /* Reduced margin for compact layout */
  font-size: 1.1rem; /* Slightly larger icon to compensate for less space */
}

.crm-item-content {
  flex: 1;
  min-width: 0; /* Allow text to wrap/truncate */
}

.crm-item-title {
  font-weight: 600;
  font-size: 0.9rem; /* Slightly smaller text for compact layout */
  line-height: 1.2;
}

.crm-item-caption {
  color: #6c757d;
  font-size: 0.75rem; /* Smaller caption text */
  line-height: 1.1;
  display: -webkit-box;
  -webkit-line-clamp: 2; /* Limit to 2 lines */
  line-clamp: 2; /* Standard property for compatibility */
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.crm-list-item-selected {
  background-color: #727cf5;
}

.crm-list-item-selected .crm-item-title,
.crm-list-item-selected .crm-item-caption,
.crm-list-item-selected i {
  color: white;
}
</style>
