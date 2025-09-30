<template>
  <!-- WHAT: Neutral wrapper card for a single subtask with top-aligned tabs -->
  <!-- WHY: Reduce visual noise from multiple nested cards and colored badges -->
  <!-- WHERE: Used inside outcome cards (e.g., REO) for each subtask item -->
  <!-- HOW: Provides small nav-tabs and renders slot content per selected tab -->
  <div class="card border-0 bg-body">
    <!-- Header row: compact title + optional summary chips -->
    <div class="d-flex align-items-center justify-content-between px-2 pt-2">
      <div class="d-flex align-items-center gap-2">
        <span class="small text-muted">{{ title }}</span>
      </div>
      <!-- Optional right side slot (e.g., actions) -->
      <div><slot name="actions" /></div>
    </div>

    <!-- Tabs: small, neutral -->
    <ul class="nav nav-tabs nav-tabs-sm px-2 mt-2" role="tablist" style="--bs-nav-link-padding-y: .25rem; --bs-nav-link-padding-x: .5rem;">
      <li v-for="t in tabs" :key="t.key" class="nav-item" role="presentation">
        <button
          class="nav-link"
          :class="{ active: current === t.key }"
          type="button"
          role="tab"
          @click="current = t.key"
        >
          <i v-if="t.icon" :class="t.icon" class="me-1"></i>{{ t.label }}
          <span v-if="typeof t.count === 'number'" class="badge text-bg-secondary ms-1">{{ t.count }}</span>
        </button>
      </li>
    </ul>

    <!-- Body -->
    <div class="p-2">
      <div v-show="current === 'bids'">
        <slot name="bids" />
      </div>
      <div v-show="current === 'notes'">
        <slot name="notes" />
      </div>
      <div v-show="current === 'docs'">
        <slot name="docs" />
      </div>
      <div v-show="current === 'history'">
        <slot name="history" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// WHAT: Lightweight tab wrapper for subtask content areas
// WHY: Centralize layout to keep child components focused and UI consistent
// HOW: Parent passes tabs meta; this component manages selected state
import { withDefaults, defineProps, ref, watchEffect } from 'vue'

interface TabMeta {
  key: 'bids' | 'notes' | 'docs' | 'history'
  label: string
  icon?: string | null
  count?: number | null
}

const props = withDefaults(defineProps<{
  title: string
  tabs: TabMeta[]
  initial?: TabMeta['key']
}>(), {
  initial: 'bids',
})

const current = ref<TabMeta['key']>(props.initial || 'bids')
const tabs = props.tabs

// Ensure current stays a valid key if tabs change
watchEffect(() => {
  if (!tabs.find(t => t.key === current.value)) {
    current.value = tabs[0]?.key || 'bids'
  }
})
</script>

<style scoped>
/* Keep tabs visually light; rely on default Bootstrap variables */
.nav-tabs .nav-link {
  font-size: .85rem;
}
</style>
