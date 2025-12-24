<template>
  <!--
    DocumentFilesTable: Files table view
    What: Renders files with name, type, size, modified, tags, and actions
    Why: Reusable across document-related pages for consistent UX
    Where: Right pane below folders section
    How: Accepts `files` and formatting helpers (or pass preformatted fields)
  -->
  <div>
    <h6 class="text-muted mb-3">Files</h6>
    <div class="table-responsive">
      <table class="table table-hover table-centered mb-0">
        <thead class="table-light">
          <tr>
            <th>Name</th>
            <th>Type</th>
            <th>Size</th>
            <th>Modified</th>
            <th>Tags</th>
            <th style="width: 100px;">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="file in files" :key="file.id">
            <td>
              <i :class="getFileIcon(file.type)" class="me-2"></i>
              <span class="fw-semibold">{{ file.name }}</span>
            </td>
            <td>
              <span class="badge bg-light text-dark">{{ file.type }}</span>
            </td>
            <td>{{ formatFileSize(file.size) }}</td>
            <td>{{ formatDate(file.modified) }}</td>
            <td>
              <span
                v-for="tag in file.tags"
                :key="tag"
                class="badge bg-primary-subtle text-primary me-1"
              >
                {{ tag }}
              </span>
            </td>
            <td>
              <b-dropdown variant="link" size="sm" no-caret toggle-class="text-muted p-0">
                <template #button-content>
                  <i class="mdi mdi-dots-horizontal font-18"></i>
                </template>
                <b-dropdown-item @click="$emit('download:file', file)">
                  <i class="mdi mdi-download me-2"></i>Download
                </b-dropdown-item>
                <b-dropdown-item @click="$emit('preview:file', file)">
                  <i class="mdi mdi-eye me-2"></i>Preview in panel
                </b-dropdown-item>
                <b-dropdown-item @click="$emit('open:sharepoint', file)">
                  <i class="mdi mdi-open-in-new me-2"></i>Open in SharePoint
                </b-dropdown-item>
                <b-dropdown-item>
                  <i class="mdi mdi-tag me-2"></i>Edit Tags
                </b-dropdown-item>
                <b-dropdown-divider />
                <b-dropdown-item variant="danger">
                  <i class="mdi mdi-delete me-2"></i>Delete
                </b-dropdown-item>
              </b-dropdown>
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
import type { EgnyteFile } from '@/components/document_components/types'

export default defineComponent({
  name: 'DocumentFilesTable',
  props: {
    files: { type: Array as PropType<EgnyteFile[]>, required: true },
    getFileIcon: { type: Function as PropType<(type: string) => string>, required: true },
    formatFileSize: { type: Function as PropType<(bytes: number) => string>, required: true },
    formatDate: { type: Function as PropType<(dateStr: string) => string>, required: true },
  },
})
</script>
