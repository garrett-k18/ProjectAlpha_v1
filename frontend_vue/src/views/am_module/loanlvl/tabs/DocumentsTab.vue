<template>
  <!-- 
    WHAT: AM Documents Tab - full document management interface
    WHY: Provides organized document access for asset management workflow
    HOW: Composes DocumentManagerPanel with AM-specific view modes
    WHERE: Used in AM loan-level tabs (frontend_vue/src/views/am_module/loanlvl/tabs/)
  -->
  <b-row class="g-3 g-lg-4 px-3 px-lg-4">
    <b-col lg="12" class="d-flex">
      <div class="w-100 h-100">
        <!-- WHAT: Reusable document manager panel -->
        <!-- WHY: Consistent document UX across AM and Acquisitions modules -->
        <!-- WHERE: Component at frontend_vue/src/components/document_components/DocumentManagerPanel.vue -->
        <DocumentManagerPanel
          :row="row"
          :assetId="assetHubId ?? undefined"
          :module="module"
          :viewModesInput="viewModesAM"
          initialViewId="by-type"
        />
      </div>
    </b-col>
  </b-row>

  <!-- Slot for future document viewer/details area if needed -->
  <slot />
</template>

<script setup lang="ts">
// WHAT: AM Documents tab - composes reusable DocumentManagerPanel
// WHY: Provides full document management features in asset management context
// HOW: Imports DocumentManagerPanel and defines AM-specific view modes
// WHERE: Used in AM loan-level modal tabs
import { withDefaults, defineProps } from 'vue'
import DocumentManagerPanel from '@/components/document_components/DocumentManagerPanel.vue'
import type { ViewMode } from '@/components/document_components/types'

// WHAT: Component props interface
// WHY: Accept row data and asset hub ID from parent LoanTabs component
// HOW: Optional props with defaults for flexible usage
withDefaults(defineProps<{
  row?: Record<string, any> | null
  assetHubId?: string | number
  module?: 'acq' | 'am'
}>(), {
  row: null,
  module: 'am',
})

// WHAT: View modes configuration for AM Documents tab
// WHY: Exclude 'by-trade' view (not relevant in asset-level context)
// HOW: Define 3 view modes - by type (default), by status, and recent
const viewModesAM: ViewMode[] = [
  { id: 'by-type', label: 'By Document Type', icon: 'mdi mdi-file-document', description: 'Group by document category' },
  { id: 'by-status', label: 'By Status', icon: 'mdi mdi-check-circle', description: 'Active, Archived, etc.' },
  { id: 'recent', label: 'Recent', icon: 'mdi mdi-clock-outline', description: 'Recently uploaded' },
]
</script>
