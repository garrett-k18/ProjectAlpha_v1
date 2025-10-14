<template>
  <!--
    File Manager - Egnyte Integration
    Multiple view modes to organize documents different ways
    Component path: frontend_vue/src/views/apps/file-manager/FileManagerNew.vue
  -->
  <Layout>
    <!-- Page Title -->
    <b-row>
      <b-col cols="12">
        <div class="page-title-box">
          <h4 class="page-title">Document Manager</h4>
        </div>
      </b-col>
    </b-row>

    <b-row>
      <b-col cols="12">
        <div class="card" style="min-height: calc(100vh - 200px);">
          <div class="card-body">
            <div class="page-aside-left">
              <DocumentAside
                :viewModes="viewModes"
                :currentViewId="currentViewId"
                @switch:view="switchView"
              />
            </div>

            <!-- Main Content Area -->
            <div class="page-aside-right">
              <DocumentTopBar :currentView="currentView" v-model:displayMode="displayMode" />

              <!-- Breadcrumb Navigation (for folder drilling) -->
              <DocumentBreadcrumbs
                :currentPath="currentPath"
                @go:root="navigateToRoot"
                @go:folder="navigateToFolder"
              />

              <!-- Loading State -->
              <DocumentLoading v-if="loading" />

              <!-- Folders Grid View -->
              <div v-else-if="folders.length > 0 && displayMode === 'grid'" class="mb-4">
                <DocumentFoldersGrid :folders="folders" @open:folder="openFolder" />
              </div>

              <!-- Folders List View -->
              <div v-else-if="folders.length > 0 && displayMode === 'list'" class="mb-4">
                <DocumentFoldersList :folders="folders" @open:folder="openFolder" />
              </div>

              <!-- Files Table -->
              <div v-if="files.length > 0">
                <DocumentFilesTable
                  :files="files"
                  :getFileIcon="getFileIcon"
                  :formatFileSize="formatFileSize"
                  :formatDate="formatDate"
                />
              </div>

              <!-- Empty State -->
              <DocumentEmptyState v-if="!loading && folders.length === 0 && files.length === 0" />
            </div>
            <!-- End page-aside-right -->
          </div>
        </div>
      </b-col>
    </b-row>
  </Layout>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import Layout from '@/components/layouts/layout.vue';
import DocumentAside from '@/components/document_components/DocumentAside.vue'
import DocumentTopBar from '@/components/document_components/DocumentTopBar.vue'
import DocumentBreadcrumbs from '@/components/document_components/DocumentBreadcrumbs.vue'
import DocumentFoldersGrid from '@/components/document_components/DocumentFoldersGrid.vue'
import DocumentFoldersList from '@/components/document_components/DocumentFoldersList.vue'
import DocumentFilesTable from '@/components/document_components/DocumentFilesTable.vue'
import DocumentLoading from '@/components/document_components/DocumentLoading.vue'
import DocumentEmptyState from '@/components/document_components/DocumentEmptyState.vue'
import type { EgnyteFolder, EgnyteFile, ViewMode } from '@/components/document_components/types'

// Mock data structure matching Egnyte API format - using shared types

export default defineComponent({
  name: 'FileManagerNew',
  components: {
    Layout,
    DocumentAside,
    DocumentTopBar,
    DocumentBreadcrumbs,
    DocumentFoldersGrid,
    DocumentFoldersList,
    DocumentFilesTable,
    DocumentLoading,
    DocumentEmptyState,
  },

  data() {
    return {
      // View modes available
      viewModes: [
        { id: 'by-trade', label: 'By Trade', icon: 'mdi mdi-home-city', description: 'Organize by property/asset' },
        { id: 'by-type', label: 'By Document Type', icon: 'mdi mdi-file-document', description: 'Group by document category' },
        { id: 'by-status', label: 'By Status', icon: 'mdi mdi-check-circle', description: 'Active, Archived, etc.' },
        { id: 'recent', label: 'Recent', icon: 'mdi mdi-clock-outline', description: 'Recently uploaded' },
      ] as ViewMode[],

      currentViewId: 'by-trade' as string,
      currentPath: [] as EgnyteFolder[],
      loading: false,
      folders: [] as EgnyteFolder[],
      files: [] as EgnyteFile[],
      displayMode: 'grid' as 'grid' | 'list', // Toggle between grid and list view
    };
  },

  computed: {
    currentView(): ViewMode {
      return this.viewModes.find(v => v.id === this.currentViewId) || this.viewModes[0];
    },
  },

  mounted() {
    this.loadData();
  },

  methods: {
    /**
     * Switch between view modes
     */
    switchView(viewId: string) {
      this.currentViewId = viewId;
      this.currentPath = [];
      this.loadData();
    },

    /**
     * Load folders and files based on current view and path
     * This will be replaced with real Egnyte API calls
     */
    loadData() {
      this.loading = true;
      
      // Simulate API call
      setTimeout(() => {
        if (this.currentViewId === 'by-trade') {
          this.loadByTrade();
        } else if (this.currentViewId === 'by-type') {
          this.loadByType();
        } else if (this.currentViewId === 'by-status') {
          this.loadByStatus();
        } else if (this.currentViewId === 'recent') {
          this.loadRecent();
        }
        
        this.loading = false;
      }, 500);
    },

    /**
     * Load data organized by trade/asset
     */
    loadByTrade() {
      if (this.currentPath.length === 0) {
        // Root level: show trades
        this.folders = [
          { id: '1', name: 'Trade 2024-001', path: '/trades/2024-001', count: 24 },
          { id: '2', name: 'Trade 2024-002', path: '/trades/2024-002', count: 18 },
          { id: '3', name: 'Trade 2024-003', path: '/trades/2024-003', count: 31 },
          { id: '4', name: 'Trade 2023-045', path: '/trades/2023-045', count: 42 },
        ];
        this.files = [];
      } else if (this.currentPath.length === 1) {
        // Inside a trade: show document type folders
        this.folders = [
          { id: 't1', name: 'Contracts', path: '/contracts', count: 5 },
          { id: 't2', name: 'Financials', path: '/financials', count: 12 },
          { id: 't3', name: 'Legal Documents', path: '/legal', count: 3 },
          { id: 't4', name: 'Photos', path: '/photos', count: 4 },
        ];
        this.files = [];
      } else {
        // Inside document type: show files
        this.folders = [];
        this.files = [
          { 
            id: 'f1', 
            name: 'Purchase Agreement.pdf', 
            path: '/file1.pdf', 
            type: 'PDF', 
            size: 2456789, 
            modified: '2024-01-15T10:30:00Z',
            tags: ['Contract', 'Signed']
          },
          { 
            id: 'f2', 
            name: 'Property Appraisal.xlsx', 
            path: '/file2.xlsx', 
            type: 'Excel', 
            size: 1234567, 
            modified: '2024-01-14T14:22:00Z',
            tags: ['Financial', 'Appraisal']
          },
          { 
            id: 'f3', 
            name: 'Title Report.pdf', 
            path: '/file3.pdf', 
            type: 'PDF', 
            size: 3456789, 
            modified: '2024-01-10T09:15:00Z',
            tags: ['Legal', 'Title']
          },
        ];
      }
    },

    /**
     * Load data organized by document type
     */
    loadByType() {
      if (this.currentPath.length === 0) {
        this.folders = [
          { id: 'dt1', name: 'Contracts', path: '/types/contracts', count: 45 },
          { id: 'dt2', name: 'Financials', path: '/types/financials', count: 78 },
          { id: 'dt3', name: 'Legal Documents', path: '/types/legal', count: 23 },
          { id: 'dt4', name: 'Photos', path: '/types/photos', count: 156 },
          { id: 'dt5', name: 'Reports', path: '/types/reports', count: 34 },
        ];
        this.files = [];
      } else {
        // Show files in that type
        this.folders = [];
        this.files = [
          { 
            id: 'f1', 
            name: 'Sample Contract 1.pdf', 
            path: '/file1.pdf', 
            type: 'PDF', 
            size: 2456789, 
            modified: '2024-01-15T10:30:00Z',
            tags: ['Trade-2024-001', 'Signed']
          },
          { 
            id: 'f2', 
            name: 'Sample Contract 2.pdf', 
            path: '/file2.pdf', 
            type: 'PDF', 
            size: 1834567, 
            modified: '2024-01-12T11:45:00Z',
            tags: ['Trade-2024-002', 'Draft']
          },
        ];
      }
    },

    /**
     * Load data organized by date
     */
    loadByDate() {
      this.folders = [
        { id: 'd1', name: 'January 2024', path: '/dates/2024-01', count: 67 },
        { id: 'd2', name: 'December 2023', path: '/dates/2023-12', count: 54 },
        { id: 'd3', name: 'November 2023', path: '/dates/2023-11', count: 43 },
      ];
      this.files = [];
    },

    /**
     * Load data organized by status
     */
    loadByStatus() {
      this.folders = [
        { id: 's1', name: 'Active', path: '/status/active', count: 234 },
        { id: 's2', name: 'Under Review', path: '/status/review', count: 45 },
        { id: 's3', name: 'Archived', path: '/status/archived', count: 789 },
      ];
      this.files = [];
    },

    /**
     * Load recent files
     */
    loadRecent() {
      this.folders = [];
      this.files = [
        { 
          id: 'r1', 
          name: 'Recent Upload 1.pdf', 
          path: '/recent1.pdf', 
          type: 'PDF', 
          size: 2456789, 
          modified: '2024-01-16T15:30:00Z',
          tags: ['Trade-2024-003', 'Contract']
        },
        { 
          id: 'r2', 
          name: 'Recent Upload 2.xlsx', 
          path: '/recent2.xlsx', 
          type: 'Excel', 
          size: 1234567, 
          modified: '2024-01-16T14:22:00Z',
          tags: ['Trade-2024-001', 'Financial']
        },
      ];
    },

    /**
     * Navigate into a folder
     */
    openFolder(folder: EgnyteFolder) {
      this.currentPath.push(folder);
      this.loadData();
    },

    /**
     * Navigate back to root
     */
    navigateToRoot() {
      this.currentPath = [];
      this.loadData();
    },

    /**
     * Navigate to specific folder in path
     */
    navigateToFolder(index: number) {
      this.currentPath = this.currentPath.slice(0, index + 1);
      this.loadData();
    },

    /**
     * Get icon for file type
     */
    getFileIcon(type: string): string {
      const icons: Record<string, string> = {
        'PDF': 'mdi mdi-file-pdf text-danger',
        'Excel': 'mdi mdi-file-excel text-success',
        'Word': 'mdi mdi-file-word text-primary',
        'Image': 'mdi mdi-file-image text-info',
      };
      return icons[type] || 'mdi mdi-file-document text-muted';
    },

    /**
     * Format file size
     */
    formatFileSize(bytes: number): string {
      if (bytes < 1024) return bytes + ' B';
      if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
      return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    },

    /**
     * Format date
     */
    formatDate(dateStr: string): string {
      const date = new Date(dateStr);
      return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric', 
        year: 'numeric' 
      });
    },
  },
});
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

.cursor-pointer {
  cursor: pointer;
}
</style>
