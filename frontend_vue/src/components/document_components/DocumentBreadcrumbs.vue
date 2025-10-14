<template>
  <!--
    DocumentBreadcrumbs: Breadcrumb navigation for folder drilling
    What: Renders a breadcrumb from Root through current folders
    Why: Reusable wherever hierarchical navigation is needed
    Where: Below the top bar on right side
    How: Accepts `currentPath`; emits `go:root` and `go:folder(index)`
  -->
  <div v-if="currentPath.length > 0" class="mb-3">
    <nav aria-label="breadcrumb">
      <ol class="breadcrumb mb-0">
        <li class="breadcrumb-item">
          <a href="#" @click.prevent="$emit('go:root')">
            <i class="mdi mdi-home"></i> Root
          </a>
        </li>
        <li
          v-for="(folder, idx) in currentPath"
          :key="idx"
          class="breadcrumb-item"
          :class="{ active: idx === currentPath.length - 1 }"
        >
          <a v-if="idx < currentPath.length - 1" href="#" @click.prevent="$emit('go:folder', idx)">
            {{ folder.name }}
          </a>
          <span v-else>{{ folder.name }}</span>
        </li>
      </ol>
    </nav>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import type { PropType } from 'vue'
import type { EgnyteFolder } from '@/components/document_components/types'

export default defineComponent({
  name: 'DocumentBreadcrumbs',
  props: {
    currentPath: { type: Array as PropType<EgnyteFolder[]>, required: true },
  },
  emits: ['go:root', 'go:folder'],
})
</script>
