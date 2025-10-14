<template>
  <!--
    DocumentFoldersGrid: Grid view for folders
    What: Displays folders as cards in a responsive grid
    Why: Reusable grid renderer for folder items
    Where: Right pane when displayMode === 'grid'
    How: Accepts `folders`; emits `open:folder(folder)`
  -->
  <div>
    <h6 class="text-muted mb-3">Folders</h6>
    <b-row>
      <b-col
        v-for="folder in folders"
        :key="folder.id"
        cols="6"
        md="4"
        lg="3"
        xl="2"
        class="mb-3"
      >
        <div class="card folder-card h-100 cursor-pointer" @click="$emit('open:folder', folder)">
          <div class="card-body text-center py-3">
            <i class="mdi mdi-folder font-24 text-warning"></i>
            <div class="mt-2 small fw-semibold text-truncate">{{ folder.name }}</div>
            <div class="text-muted" style="font-size: 0.7rem;">{{ folder.count }} items</div>
          </div>
        </div>
      </b-col>
    </b-row>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import type { PropType } from 'vue'

export interface EgnyteFolder {
  id: string
  name: string
  path: string
  count: number
  metadata?: Record<string, any>
}

export default defineComponent({
  name: 'DocumentFoldersGrid',
  props: {
    folders: { type: Array as PropType<EgnyteFolder[]>, required: true },
  },
  emits: ['open:folder'],
})
</script>

<style scoped>
.folder-card {
  transition: all 0.2s ease;
  cursor: pointer;
}
.folder-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.1);
}
</style>
