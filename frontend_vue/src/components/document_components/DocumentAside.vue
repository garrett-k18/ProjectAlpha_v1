<template>
  <!--
    DocumentAside: Left sidebar for the Document Manager
    What: Renders Create New dropdown, View modes list, Quick Access, External links
    Why: Reusable across document views; keeps index lean and modular
    Where: Used inside `index_document_manager.vue` within `.page-aside-left`
    How: Accepts `viewModes` and `currentViewId` as props; emits `switch:view` when user changes view
  -->
  <div>
    <!-- Upload / Create New Dropdown -->
    <b-dropdown menu-class="dropdown-menu" toggle-class="btn btn-lg btn-link arrow-none">
      <template #button-content>
        <b-button
          variant="success"
          class="dropdown-toggle w-100"
          data-bs-toggle="dropdown"
          aria-haspopup="true"
          aria-expanded="false"
        >
          <i class="mdi mdi-plus"></i> Create New
        </b-button>
      </template>
      <b-dropdown-item class="mb-0" href="#">
        <i class="mdi mdi-folder-plus-outline me-1"></i> Folder
      </b-dropdown-item>
      <b-dropdown-item class="mb-0" href="#">
        <i class="mdi mdi-file-plus-outline me-1"></i> File
      </b-dropdown-item>
      <b-dropdown-item class="mb-0" href="#">
        <i class="mdi mdi-upload me-1"></i> Upload File
      </b-dropdown-item>
    </b-dropdown>

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
      <a href="https://egnyte.com" target="_blank" class="list-group-item border-0">
        <i class="mdi mdi-cloud font-18 align-middle me-2"></i>
        Egnyte Portal
        <i class="mdi mdi-open-in-new font-12 ms-1"></i>
      </a>
      <a href="https://sharepoint.com" target="_blank" class="list-group-item border-0">
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
  emits: ['switch:view'],
})
</script>
