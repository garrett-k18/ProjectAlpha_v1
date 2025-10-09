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
              <!-- Upload Button -->
              <b-dropdown
                menu-class="dropdown-menu"
                toggle-class="btn btn-lg btn-link arrow-none"
              >
                <template v-slot:button-content>
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
                  @click.prevent="switchView(view.id)"
                >
                  <i :class="view.icon" class="font-18 align-middle me-2"></i>
                  {{ view.label }}
                </a>
              </div>

              <!-- Quick Actions -->
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

              <!-- External Links -->
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

            <!-- Main Content Area -->
            <div class="page-aside-right">

            <!-- Top Bar with View Toggle -->
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h5 class="mb-0">{{ currentView.label }}</h5>
              <div class="btn-group">
                <button 
                  class="btn btn-sm"
                  :class="displayMode === 'grid' ? 'btn-primary' : 'btn-outline-secondary'"
                  @click="displayMode = 'grid'"
                >
                  <i class="mdi mdi-view-grid"></i>
                </button>
                <button 
                  class="btn btn-sm"
                  :class="displayMode === 'list' ? 'btn-primary' : 'btn-outline-secondary'"
                  @click="displayMode = 'list'"
                >
                  <i class="mdi mdi-view-list"></i>
                </button>
              </div>
            </div>

            <!-- Breadcrumb Navigation (for folder drilling) -->
            <div v-if="currentPath.length > 0" class="mb-3">
              <nav aria-label="breadcrumb">
                <ol class="breadcrumb mb-0">
                  <li class="breadcrumb-item">
                    <a href="#" @click.prevent="navigateToRoot">
                      <i class="mdi mdi-home"></i> Root
                    </a>
                  </li>
                  <li 
                    v-for="(folder, idx) in currentPath" 
                    :key="idx"
                    class="breadcrumb-item"
                    :class="{ active: idx === currentPath.length - 1 }"
                  >
                    <a 
                      v-if="idx < currentPath.length - 1"
                      href="#" 
                      @click.prevent="navigateToFolder(idx)"
                    >
                      {{ folder.name }}
                    </a>
                    <span v-else>{{ folder.name }}</span>
                  </li>
                </ol>
              </nav>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="text-center py-5">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>

            <!-- Folders Grid View -->
            <div v-else-if="folders.length > 0 && displayMode === 'grid'" class="mb-4">
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
                  <div 
                    class="card folder-card h-100 cursor-pointer"
                    @click="openFolder(folder)"
                  >
                    <div class="card-body text-center py-3">
                      <i class="mdi mdi-folder font-24 text-warning"></i>
                      <div class="mt-2 small fw-semibold text-truncate">
                        {{ folder.name }}
                      </div>
                      <div class="text-muted" style="font-size: 0.7rem;">
                        {{ folder.count }} items
                      </div>
                    </div>
                  </div>
                </b-col>
              </b-row>
            </div>

            <!-- Folders List View -->
            <div v-else-if="folders.length > 0 && displayMode === 'list'" class="mb-4">
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
                      @click="openFolder(folder)"
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

            <!-- Files Table -->
            <div v-if="files.length > 0">
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
                        <b-dropdown 
                          variant="link" 
                          size="sm" 
                          no-caret
                          toggle-class="text-muted p-0"
                        >
                          <template #button-content>
                            <i class="mdi mdi-dots-horizontal font-18"></i>
                          </template>
                          <b-dropdown-item>
                            <i class="mdi mdi-download me-2"></i>Download
                          </b-dropdown-item>
                          <b-dropdown-item>
                            <i class="mdi mdi-eye me-2"></i>Preview
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

            <!-- Empty State -->
            <div v-if="!loading && folders.length === 0 && files.length === 0" class="text-center py-5">
              <i class="mdi mdi-folder-open-outline font-48 text-muted"></i>
              <p class="text-muted mt-3">No documents found</p>
            </div>

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

// Mock data structure matching Egnyte API format
interface EgnyteFolder {
  id: string;
  name: string;
  path: string;
  count: number;
  metadata?: Record<string, any>;
}

interface EgnyteFile {
  id: string;
  name: string;
  path: string;
  type: string;
  size: number;
  modified: string;
  tags: string[];
  metadata?: Record<string, any>;
}

interface ViewMode {
  id: string;
  label: string;
  icon: string;
  description: string;
}

export default defineComponent({
  name: 'FileManagerNew',
  components: {
    Layout,
  },

  data() {
    return {
      // View modes available
      viewModes: [
        { id: 'by-trade', label: 'By Trade', icon: 'mdi mdi-home-city', description: 'Organize by property/asset' },
        { id: 'by-type', label: 'By Document Type', icon: 'mdi mdi-file-document', description: 'Group by document category' },
        { id: 'by-date', label: 'By Date', icon: 'mdi mdi-calendar', description: 'Timeline view' },
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
        } else if (this.currentViewId === 'by-date') {
          this.loadByDate();
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
