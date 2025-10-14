<template>
  <!-- DocumentFoldersList: List/table view for folders -->
  <div>
    <h6 class="text-muted mb-3">Folders</h6>
    <div class="table-responsive">
      <table class="table table-hover table-centered mb-0">
        <thead class="table-light">
          <tr>
            <th>Name</th>
            <th>Items</th>
            <th style="width: 100px;">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="folder in folders"
            :key="folder.id"
            class="cursor-pointer"
            @click="$emit('open:folder', folder)"
          >
            <td>
              <i class="mdi mdi-folder text-warning me-2 font-18"></i>
              <span class="fw-semibold">{{ folder.name }}</span>
            </td>
            <td>{{ folder.count }} items</td>
            <td>
              <button class="btn btn-sm btn-link text-muted p-0">
                <i class="mdi mdi-dots-horizontal font-18"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import type { PropType } from 'vue'
import type { EgnyteFolder } from '@/components/document_components/types'

export default defineComponent({
  name: 'DocumentFoldersList',
  props: {
    folders: { type: Array as PropType<EgnyteFolder[]>, required: true },
  },
  emits: ['open:folder'],
})
</script>

<style scoped>
.cursor-pointer { cursor: pointer; }
</style>
