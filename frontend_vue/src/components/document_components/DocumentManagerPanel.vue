<template>
  <div class="card" style="min-height: calc(100vh - 200px);">
    <div class="card-body">
      <div class="page-aside-left">
        <DocumentAside
          :viewModes="effectiveViewModes"
          :currentViewId="currentViewId"
          @switch:view="switchView"
          @upload:files="handleUpload"
        />
      </div>

      <div
        class="page-aside-right"
        @drop.prevent="handleDrop"
        @dragover.prevent="dragOver = true"
        @dragleave="dragOver = false"
        :class="{ 'drag-over': dragOver }"
      >
        <DocumentTopBar :currentView="currentView" v-model:displayMode="displayMode" />

        <DocumentBreadcrumbs
          :currentPath="currentPath"
          @go:root="navigateToRoot"
          @go:folder="navigateToFolder"
        />

        <DocumentLoading v-if="loading" />

        <div v-else-if="folders.length > 0 && displayMode === 'grid'" class="mb-4">
          <DocumentFoldersGrid :folders="folders" @open:folder="openFolder" />
        </div>

        <div v-else-if="folders.length > 0 && displayMode === 'list'" class="mb-4">
          <DocumentFoldersList :folders="folders" @open:folder="openFolder" />
        </div>

        <div v-if="files.length > 0">
          <DocumentFilesTable
            :files="files"
            :getFileIcon="getFileIcon"
            :formatFileSize="formatFileSize"
            :formatDate="formatDate"
            @preview:file="handlePreviewFile"
            @download:file="handleDownloadFile"
            @open:sharepoint="handleOpenInSharePoint"
          />
        </div>

        <div v-if="previewFile" class="mt-3">
          <h6 class="text-muted mb-2">Preview</h6>
          <div style="height: 70vh;">
            <iframe
              :src="(previewFile as any).download_url || (previewFile as any).web_url || previewFile.path"
              width="100%"
              height="100%"
              frameborder="0"
            ></iframe>
          </div>
        </div>

        <DocumentEmptyState v-if="!loading && folders.length === 0 && files.length === 0" />
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, nextTick } from 'vue'
import type { PropType } from 'vue'
import DocumentAside from '@/components/document_components/DocumentAside.vue'
import DocumentTopBar from '@/components/document_components/DocumentTopBar.vue'
import DocumentBreadcrumbs from '@/components/document_components/DocumentBreadcrumbs.vue'
import DocumentFoldersGrid from '@/components/document_components/DocumentFoldersGrid.vue'
import DocumentFoldersList from '@/components/document_components/DocumentFoldersList.vue'
import DocumentFilesTable from '@/components/document_components/DocumentFilesTable.vue'
import DocumentLoading from '@/components/document_components/DocumentLoading.vue'
import DocumentEmptyState from '@/components/document_components/DocumentEmptyState.vue'
import type { EgnyteFolder, EgnyteFile, ViewMode } from '@/components/document_components/types'

export default defineComponent({
  name: 'DocumentManagerPanel',
  components: {
    DocumentAside,
    DocumentTopBar,
    DocumentBreadcrumbs,
    DocumentFoldersGrid,
    DocumentFoldersList,
    DocumentFilesTable,
    DocumentLoading,
    DocumentEmptyState,
  },
  props: {
    assetId: { type: [String, Number], required: false, default: null },
    tradeId: { type: [String, Number], required: false, default: null },
    row: { type: Object as () => Record<string, any> | null, required: false, default: null },
    module: { type: String as () => 'acq' | 'am' | undefined, required: false, default: undefined },
    // Optional override for available view modes (e.g., hide 'by-trade' in tab usage)
    viewModesInput: { type: Array as PropType<ViewMode[]>, required: false, default: undefined },
    // Optional initial view id (e.g., default to 'by-type' when by-trade is removed)
    initialViewId: { type: String as PropType<string | undefined>, required: false, default: undefined },
  },
  data() {
    return {
      // Default set of view modes used when no override is provided
      viewModesDefault: [
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
      displayMode: 'grid' as 'grid' | 'list',
      dragOver: false,
      uploading: false,
      tradeFoldersCache: [] as any[],
      assetFoldersCache: [] as any[],
      folderContentsCache: {} as Record<string, any>,
      previewFile: null as EgnyteFile | null,
    }
  },
  computed: {
    // Use override when provided, otherwise fallback to defaults
    effectiveViewModes(): ViewMode[] {
      return (this.viewModesInput && this.viewModesInput.length) ? this.viewModesInput : this.viewModesDefault
    },
    currentView(): ViewMode {
      return this.effectiveViewModes.find(v => v.id === this.currentViewId) || this.effectiveViewModes[0]
    },
  },
  watch: {
    assetId(newVal, oldVal) {
      // Reload data when assetId changes (e.g., when parent sets it)
      if (newVal && newVal !== oldVal) {
        console.log('Asset ID changed to:', newVal, '- reloading data')
        this.loadData()
      }
    },
    tradeId(newVal, oldVal) {
      // WHAT: Reload data when tradeId changes (e.g., when modal opens with trade selected)
      // WHY: Trade-level documents need to load when tradeId becomes available
      // HOW: Call loadData() when tradeId is set or changes
      if (newVal && newVal !== oldVal) {
        console.log('Trade ID changed to:', newVal, '- reloading data')
        this.loadData()
      }
    },
    row: {
      deep: true,
      handler(newVal, oldVal) {
        // Reload when row changes
        if (newVal && newVal !== oldVal && newVal.id) {
          console.log('Row changed - reloading data')
          this.loadData()
        }
      }
    }
  },
  async mounted() {
    // WHAT: Set initial view from prop or default to first available
    // WHY: Ensure correct view mode is selected when component mounts
    // HOW: Check if initialViewId exists in available view modes, otherwise use first available
    if (this.initialViewId) {
      const exists = this.effectiveViewModes.some(m => m.id === this.initialViewId)
      this.currentViewId = exists ? this.initialViewId : (this.effectiveViewModes[0]?.id || this.currentViewId)
    } else if (!this.effectiveViewModes.some(m => m.id === this.currentViewId)) {
      this.currentViewId = this.effectiveViewModes[0]?.id || this.currentViewId
    }
    
    console.log('DocumentManagerPanel mounted - initialViewId:', this.initialViewId, 'currentViewId:', this.currentViewId, 'tradeId:', this.tradeId, 'assetId:', this.assetId, 'row:', this.row)
    
    // WHAT: Wait for next tick to ensure props are fully available, then load data
    // WHY: Props might not be set immediately on mount, especially in modals
    // HOW: Use nextTick to ensure tradeId/assetId props are available before loading
    await nextTick()
    
    // WHAT: Always load data on mount - loadData() will handle empty states
    // WHY: Show folders immediately when modal opens with correct view, don't wait for user interaction
    // HOW: Call loadData() which checks currentViewId and loads appropriate data (or shows empty state)
    // NOTE: loadData() handles cases where tradeId/assetId might not be available yet
    this.loadData()
  },
  methods: {
    getFolderCountFromCacheOrTemplate(folder: any): number {
      const cached = this.folderContentsCache[folder.path]
      if (cached) {
        return (cached.files?.length || 0) + (cached.folders?.length || 0)
      }
      // Fallback to any counts present on the template structure
      if (Array.isArray(folder.files) || Array.isArray(folder.subfolders)) {
        return (folder.files?.length || 0) + (folder.subfolders?.length || 0)
      }
      if (typeof folder.file_count === 'number') {
        return folder.file_count
      }
      return 0
    },
    switchView(viewId: string) {
      this.currentViewId = viewId
      this.currentPath = [] as EgnyteFolder[]
      this.previewFile = null
      this.loadData()
    },
    async loadData() {
      this.loading = true
      try {
        if (this.currentViewId === 'by-trade') {
          this.loadByTrade()
          this.applySelectedFilter()  // Only filter for mock data views
        }
        else if (this.currentViewId === 'by-type') {
          await this.loadByType()  // SharePoint data - lazy-load files per folder
        }
        else if (this.currentViewId === 'by-status') {
          this.loadByStatus()
          this.applySelectedFilter()
        }
        else if (this.currentViewId === 'recent') {
          this.loadRecent()
          this.applySelectedFilter()
        }
      } finally {
        this.loading = false
      }
    },
    applySelectedFilter() {
      const key = this.assetId != null ? String(this.assetId) : (this.row && (this.row as any).id != null ? String((this.row as any).id) : '')
      if (!key) return
      // Filter folders by name or path containing the key
      this.folders = this.folders.filter(f => f.name.includes(key) || f.path.includes(key))
      // Filter files by name, path, or tags containing the key
      this.files = this.files.filter(file => {
        const inName = file.name.includes(key)
        const inPath = file.path.includes(key)
        const inTags = Array.isArray(file.tags) ? file.tags.some(t => String(t).includes(key)) : false
        return inName || inPath || inTags
      })
    },
    updateVisibleFolderCountsFromCache() {
      if (!this.folders || this.folders.length === 0) return
      this.folders = this.folders.map(folder => {
        const cached = this.folderContentsCache[folder.path]
        if (!cached) return folder
        const count = (cached.files?.length || 0) + (cached.folders?.length || 0)
        return { ...folder, count }
      })
    },
    loadByTrade() {
      if (this.currentPath.length === 0) {
        this.folders = [
          { id: '1', name: 'Trade 2024-001', path: '/trades/2024-001', count: 24 },
          { id: '2', name: 'Trade 2024-002', path: '/trades/2024-002', count: 18 },
          { id: '3', name: 'Trade 2024-003', path: '/trades/2024-003', count: 31 },
          { id: '4', name: 'Trade 2023-045', path: '/trades/2023-045', count: 42 },
        ]
        this.files = []
      } else if (this.currentPath.length === 1) {
        this.folders = [
          { id: 't1', name: 'Contracts', path: '/contracts', count: 5 },
          { id: 't2', name: 'Financials', path: '/financials', count: 12 },
          { id: 't3', name: 'Legal Documents', path: '/legal', count: 3 },
          { id: 't4', name: 'Photos', path: '/photos', count: 4 },
        ]
        this.files = []
      } else {
        this.folders = []
        this.files = [
          { id: 'f1', name: 'Purchase Agreement.pdf', path: '/file1.pdf', type: 'PDF', size: 2456789, modified: '2024-01-15T10:30:00Z', tags: ['Contract', 'Signed'] },
          { id: 'f2', name: 'Property Appraisal.xlsx', path: '/file2.xlsx', type: 'Excel', size: 1234567, modified: '2024-01-14T14:22:00Z', tags: ['Financial', 'Appraisal'] },
          { id: 'f3', name: 'Title Report.pdf', path: '/file3.pdf', type: 'PDF', size: 3456789, modified: '2024-01-10T09:15:00Z', tags: ['Legal', 'Title'] },
        ]
      }
    },
    async loadByType() {
      // WHAT: Check if this is trade-level or asset-level documents
      // WHY: Trade-level uses tradeId, asset-level uses assetId
      // HOW: Check tradeId prop first, then fall back to assetId
      const tradeId = this.tradeId || (this.row && (this.row as any).tradeId) || (this.row && (this.row as any).trade?.id)
      const assetHubId = this.assetId || (this.row && this.row.id)
      
      console.log('loadByType - tradeId:', tradeId, 'assetId:', this.assetId, 'row:', this.row, 'assetHubId:', assetHubId)
      
      // WHAT: Handle trade-level documents
      // WHY: Trade-level shows Bid, Legal, Post Close folders (static structure)
      // HOW: Call trade documents API which returns static folder structure
      if (tradeId && !assetHubId) {
        console.log('Fetching SharePoint documents for trade:', tradeId)
        try {
          const response = await fetch(`/api/sharepoint/trades/${tradeId}/documents/`)
          const data = await response.json()
          
          console.log('SharePoint trade API response:', data)
          
          if (!data.success) {
            console.error('SharePoint trade fetch failed:', data.error)
            this.folders = []
            this.files = []
            return
          }
          
          // Cache static Trade Level folder structure for instant first-level navigation
          this.tradeFoldersCache = data.folders || []

          if (this.currentPath.length === 0) {
          // WHAT: Show trade-level category folders (Seller Data Dump, Due Diligence, Bid, Award, Settlement, etc.)
          // WHY: Static folder structure from backend; files are lazy-loaded per folder
          console.log('Mapping trade folders:', data.folders)
          this.folders = (data.folders || []).map((folder: any) => {
            return {
              id: folder.name,
              name: folder.name,
              path: folder.path,
              count: this.getFolderCountFromCacheOrTemplate(folder),
            }
          })
          console.log('Mapped trade folders:', this.folders)
          this.files = []

          // Bulk prefetch contents for all Trade Level folders in the background
          // so that counts and first drill-ins are fast after the trade is loaded.
          this.prefetchChildFolders(data.folders || [])
          } else {
            // WHAT: In a trade-level folder - we lazy-load contents via openFolder()
            // Just keep current folders/files as-is here.
          }
        } catch (error) {
          console.error('Error loading SharePoint trade documents:', error)
          this.folders = []
          this.files = []
        }
        return
      }
      
      // WHAT: Handle asset-level documents (existing logic)
      // WHY: Asset-level shows Valuation, Collateral, Legal, Tax, Title, Photos folders
      if (!assetHubId) {
        // No asset selected yet - show empty state
        this.folders = []
        this.files = []
        return
      }
      
      // Fetch from SharePoint API for asset
      console.log('Fetching SharePoint documents for asset:', assetHubId)
      try {
        const response = await fetch(`/api/sharepoint/assets/${assetHubId}/documents/`)
        const data = await response.json()
        
        console.log('SharePoint API response:', data)
        console.log('Folders count:', data.folders?.length)
        console.log('Files count:', data.files?.length)
        
        if (!data.success) {
          console.error('SharePoint fetch failed:', data.error)
          this.folders = []
          this.files = []
          return
        }
        
        // Cache static asset-level folder structure for instant first-level navigation
        this.assetFoldersCache = data.folders || []

        if (this.currentPath.length === 0) {
          // Show main asset-level category folders (Valuation, Loan File, etc.)
          console.log('Mapping folders:', data.folders)
          this.folders = (data.folders || []).map((folder: any) => {
            console.log('Mapping folder:', folder)
            return {
              id: folder.name,
              name: folder.name,
              path: folder.path,
              count: this.getFolderCountFromCacheOrTemplate(folder),
            }
          })
          console.log('Mapped folders:', this.folders)
          this.files = []
        } else {
          // WHAT: In an asset-level folder; contents are lazy-loaded via openFolder()
          // Keep existing state here.
        }
      } catch (error) {
        console.error('Error loading SharePoint documents:', error)
        this.folders = []
        this.files = []
      }
    },
    loadByDate() {
      this.folders = [
        { id: 'd1', name: 'January 2024', path: '/dates/2024-01', count: 67 },
        { id: 'd2', name: 'December 2023', path: '/dates/2023-12', count: 54 },
        { id: 'd3', name: 'November 2023', path: '/dates/2023-11', count: 43 },
      ]
      this.files = []
    },
    loadByStatus() {
      this.folders = [
        { id: 's1', name: 'Active', path: '/status/active', count: 234 },
        { id: 's2', name: 'Under Review', path: '/status/review', count: 45 },
        { id: 's3', name: 'Archived', path: '/status/archived', count: 789 },
      ]
      this.files = []
    },
    loadRecent() {
      this.folders = []
      this.files = [
        { id: 'r1', name: 'Recent Upload 1.pdf', path: '/recent1.pdf', type: 'PDF', size: 2456789, modified: '2024-01-16T15:30:00Z', tags: ['Trade-2024-003', 'Contract'] },
        { id: 'r2', name: 'Recent Upload 2.xlsx', path: '/recent2.xlsx', type: 'Excel', size: 1234567, modified: '2024-01-16T14:22:00Z', tags: ['Trade-2024-001', 'Financial'] },
      ]
    },
    async openFolder(folder: EgnyteFolder) {
      // Non-SharePoint (mock) views keep old behavior
      if (this.currentViewId !== 'by-type') {
        this.currentPath.push(folder)
        this.loadData()
        return
      }

      const previousDepth = this.currentPath.length
      this.previewFile = null
      this.currentPath.push(folder)

      const path = folder.path

      // If we already have contents cached for this path, use them instantly
      const cached = this.folderContentsCache[path]
      if (cached) {
        this.folders = (cached.folders || []).map((sub: any) => ({
          id: sub.name,
          name: sub.name,
          path: sub.path,
          count: (sub.files?.length || 0) + (sub.subfolders?.length || 0),
        }))
        this.files = cached.files || []
        // Predictively prefetch next-level children in the background
        this.prefetchChildFolders(cached.folders || [])
        this.updateVisibleFolderCountsFromCache()
        return
      }

      const tradeId = this.tradeId || (this.row && (this.row as any).tradeId) || (this.row && (this.row as any).trade?.id)
      const assetHubId = this.assetId || (this.row && this.row.id)

      // Trade-level: instant navigation from root into known Trade Level categories
      if (tradeId && !assetHubId && previousDepth === 0) {
        const folderData = (this.tradeFoldersCache || []).find((f: any) => f.name === folder.name)
        if (folderData && Array.isArray(folderData.subfolders) && folderData.subfolders.length > 0) {
          this.folders = (folderData.subfolders || []).map((sub: any) => ({
            id: sub.name,
            name: sub.name,
            path: sub.path,
            count: sub.file_count || 0,
          }))
          this.files = []

          // Predictively prefetch each subfolder's files in the background
          this.prefetchChildFolders(folderData.subfolders || [])
          this.updateVisibleFolderCountsFromCache()
          return
        }
        // If no predefined subfolders, fall through to lazy-load files via API
      }

      // Asset-level: instant navigation from root into known category subfolders (e.g., Loan File children)
      if (assetHubId && previousDepth === 0) {
        const folderData = (this.assetFoldersCache || []).find((f: any) => f.name === folder.name)
        if (folderData && Array.isArray(folderData.subfolders) && folderData.subfolders.length > 0) {
          this.folders = (folderData.subfolders || []).map((sub: any) => ({
            id: sub.name,
            name: sub.name,
            path: sub.path,
            count: sub.file_count || 0,
          }))
          this.files = []

          // Predictively prefetch each subfolder's files in the background
          this.prefetchChildFolders(folderData.subfolders || [])
          this.updateVisibleFolderCountsFromCache()
          return
        }
        // If no predefined subfolders, fall through to lazy-load via API
      }

      // Lazy-load contents of the selected folder from backend
      try {
        const response = await fetch(`/api/sharepoint/folder-contents/?path=${encodeURIComponent(path)}`)
        const data = await response.json()
        console.log('Folder contents response for', path, ':', data)

        if (!data.success) {
          console.error('Failed to load folder contents:', data.error)
          this.folders = []
          this.files = []
          return
        }

        // Cache contents for this path so revisits are instant
        this.folderContentsCache[path] = data

        // Also update any matching template folder entry so root cards
        // (e.g. Seller Data Dump) can show the correct item count when
        // you navigate back.
        const totalCount = (data.files?.length || 0) + (data.folders?.length || 0)
        const tradeIdx = (this.tradeFoldersCache || []).findIndex((f: any) => f.path === path)
        if (tradeIdx >= 0) {
          const existing = this.tradeFoldersCache[tradeIdx]
          this.tradeFoldersCache.splice(tradeIdx, 1, { ...existing, file_count: totalCount })
        }
        const assetIdx = (this.assetFoldersCache || []).findIndex((f: any) => f.path === path)
        if (assetIdx >= 0) {
          const existing = this.assetFoldersCache[assetIdx]
          this.assetFoldersCache.splice(assetIdx, 1, { ...existing, file_count: totalCount })
        }

        this.folders = (data.folders || []).map((sub: any) => ({
          id: sub.name,
          name: sub.name,
          path: sub.path,
          count: (sub.files?.length || 0) + (sub.subfolders?.length || 0),
        }))
        this.files = data.files || []

        // Predictively prefetch next-level children
        this.prefetchChildFolders(data.folders || [])
        this.updateVisibleFolderCountsFromCache()
      } catch (error) {
        console.error('Error lazy-loading folder contents:', error)
        this.folders = []
        this.files = []
      }
    },
    prefetchChildFolders(childFolders: any[]) {
      childFolders.forEach((sub: any) => {
        const subPath = sub && sub.path
        if (!subPath || this.folderContentsCache[subPath]) return

        fetch(`/api/sharepoint/folder-contents/?path=${encodeURIComponent(subPath)}`)
          .then(res => res.json())
          .then(data => {
            if (data && data.success) {
              this.folderContentsCache[subPath] = data
              this.updateVisibleFolderCountsFromCache()
            }
          })
          .catch(err => {
            console.error('Error prefetching folder contents for', subPath, err)
          })
      })
    },
    navigateToRoot() {
      this.currentPath = []
      this.previewFile = null
      this.loadData()
    },
    navigateToFolder(index: number) {
      // Navigate to a specific folder in the breadcrumb trail.
      // For SharePoint (by-type) view, treat this like clicking that folder
      // in the grid/list so openFolder() applies caching and lazy-loading
      // logic correctly.
      const targetFolder = this.currentPath[index]
      if (!targetFolder) return

      // Trim path so openFolder pushes targetFolder as the new last segment
      this.currentPath = this.currentPath.slice(0, index)
      this.openFolder(targetFolder)
    },
    getFileIcon(type: string): string {
      const icons: Record<string, string> = {
        'PDF': 'mdi mdi-file-pdf text-danger',
        'Excel': 'mdi mdi-file-excel text-success',
        'Word': 'mdi mdi-file-word text-primary',
        'Image': 'mdi mdi-file-image text-info',
      }
      return icons[type] || 'mdi mdi-file-document text-muted'
    },
    formatFileSize(bytes: number): string {
      if (bytes < 1024) return bytes + ' B'
      if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
      return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
    },
    formatDate(dateStr: string): string {
      const date = new Date(dateStr)
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    },
    handleDrop(event: DragEvent) {
      this.dragOver = false
      const files = event.dataTransfer?.files
      if (files && files.length > 0) {
        this.handleUpload(Array.from(files))
      }
    },
    async handleUpload(files: File[]) {
      console.log('handleUpload called with', files.length, 'files')
      const assetHubId = this.assetId || (this.row && this.row.id)
      console.log('Asset ID:', assetHubId)
      if (!assetHubId) {
        alert('No asset selected')
        return
      }
      
      // Get category from current path (folder user is viewing)
      let category = 'Valuation'  // Default
      let subcategory = null
      
      if (this.currentPath.length > 0) {
        category = this.currentPath[0].name  // Main category folder
        if (this.currentPath.length > 1) {
          subcategory = this.currentPath[1].name  // Subfolder
        }
      }
      
      console.log('Uploading to category:', category, 'subcategory:', subcategory)
      
      this.uploading = true
      
      for (const file of files) {
        try {
          const formData = new FormData()
          formData.append('file', file)
          formData.append('asset_hub_id', String(assetHubId))
          formData.append('category', category)
          
          const response = await fetch('/api/sharepoint/upload/', {
            method: 'POST',
            body: formData
          })
          
          if (response.ok) {
            console.log(`✓ Uploaded: ${file.name}`)
          } else {
            console.error(`✗ Failed: ${file.name}`)
          }
        } catch (error) {
          console.error(`Error uploading ${file.name}:`, error)
        }
      }
      
      this.uploading = false
      this.loadData()  // Refresh to show new files
    },
    handlePreviewFile(file: EgnyteFile) {
      const name = (file && file.name) || ''
      const ext = name.split('.').pop()?.toLowerCase() || ''
      const isPdf = ext === 'pdf'

      // Only attempt in-panel iframe preview for PDFs.
      // For other types (Excel, Word, etc.), open in SharePoint instead
      // to avoid triggering OS save dialogs for binary downloads.
      if (!isPdf) {
        this.previewFile = null
        this.handleOpenInSharePoint(file)
        return
      }

      this.previewFile = file
    },
    handleDownloadFile(file: EgnyteFile) {
      // Prefer direct download URL when available, fallback to web_url
      const url = (file as any).download_url || (file as any).web_url || (file as any).path
      if (!url) return
      window.open(url, '_blank')
    },
    handleOpenInSharePoint(file: EgnyteFile) {
      const url = (file as any).web_url || (file as any).path
      if (!url) return
      window.open(url, '_blank')
    },
  },
})
</script>

<style scoped>
/* Keep minimal; panel reuses page styles */
.drag-over {
  border: 2px dashed #4CAF50;
  background-color: rgba(76, 175, 80, 0.05);
}
</style>
