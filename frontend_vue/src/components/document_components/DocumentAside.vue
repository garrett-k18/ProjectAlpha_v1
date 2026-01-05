<template>
  <!--
    DocumentAside: Left sidebar for the Document Manager
    What: Renders Create New dropdown, View modes list, Quick Access, External links
    Why: Reusable across document views; keeps index lean and modular
    Where: Used inside `index_document_manager.vue` within `.page-aside-left`
    How: Accepts `viewModes` and `currentViewId` as props; emits `switch:view` when user changes view
  -->
  <div>
    <!-- Upload Button -->
    <input
      ref="fileInput"
      type="file"
      multiple
      style="display: none"
      @change="handleFileSelect"
    />
    <b-button
      variant="success"
      class="w-100"
      @click="triggerFilePicker"
    >
      <i class="mdi mdi-upload"></i> Upload Files
    </b-button>

    <!-- View Modes List -->
    <div class="email-menu-list mt-3">
      <h6 class="text-muted text-uppercase font-13 mb-2 mt-4">Views</h6>
      <a
        v-for="view in viewModes"
        :key="view.id"
        href="#"
        class="list-group-item border-0"
        :class="{ 'active': currentViewId === view.id }"
        @click.prevent="$emit('switch:view', view.id)"
      >
        <i :class="view.icon" class="font-18 align-middle me-2"></i>
        {{ view.label }}</a
      >
    </div>

    <!-- Quick Access -->
    <div class="email-menu-list mt-3">
      <h6 class="text-muted text-uppercase font-13 mb-2 mt-4">Quick Access</h6>
      <a href="#" class="list-group-item border-0">
        <i class="mdi mdi-clock-outline font-18 align-middle me-2"></i>
        Recent
      </a>
      <a href="#" class="list-group-item border-0">
        <i class="mdi mdi-star-outline font-18 align-middle me-2"></i>
        Starred
      </a>
      <a href="#" class="list-group-item border-0">
        <i class="mdi mdi-delete font-18 align-middle me-2"></i>
        Deleted Files
      </a>
    </div>

    <!-- External Storage Links -->
    <div class="email-menu-list mt-3">
      <h6 class="text-muted text-uppercase font-13 mb-2 mt-4">External Storage</h6>
      <a
        href="https://firstliencapitaldom.sharepoint.com/sites/ProjectAlpha/Shared%20Documents/Forms/AllItems.aspx?id=%2Fsites%2FProjectAlpha%2FShared%20Documents%2FTrades%2FFLC%2D40%20%2D%20HUD&sortField=DefaultSortOrder&isAscending=true&viewid=52551d4e%2D0079%2D4db6%2Daf37%2Dd7bb02165568&newTargetListUrl=%2Fsites%2FProjectAlpha%2FShared%20Documents&viewpath=%2Fsites%2FProjectAlpha%2FShared%20Documents%2FForms%2FAllItems%2Easpx"
        target="_blank"
        class="list-group-item border-0"
      >
        <i class="mdi mdi-microsoft-sharepoint font-18 align-middle me-2"></i>
        SharePoint
        <i class="mdi mdi-open-in-new font-12 ms-1"></i>
      </a>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import type { PropType } from 'vue'
import type { ViewMode } from '@/components/document_components/types'

export default defineComponent({
  name: 'DocumentAside',
  props: {
    viewModes: { type: Array as PropType<ViewMode[]>, required: true },
    currentViewId: { type: String, required: true },
  },
  emits: ['switch:view', 'upload:files'],
  methods: {
    triggerFilePicker() {
      const el = this.$refs.fileInput as HTMLInputElement | undefined
      el?.click()
    },
    handleFileSelect(event: Event) {
      console.log('File select triggered', event)
      const target = event.target as HTMLInputElement
      const files = target.files
      console.log('Files selected:', files?.length)
      if (files && files.length > 0) {
        console.log('Emitting upload:files with', files.length, 'files')
        this.$emit('upload:files', Array.from(files))
        // Reset input so same file can be selected again
        target.value = ''
      }
    },
  },
})
</script>
