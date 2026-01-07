<template>
  <div class="tasking-container">
    <!-- Asset Header Card -->
    <div class="header-card">
      <div class="header-badges">
        <UiBadge
          v-if="headerAsset?.delinquencyStatusLabel"
          :tone="headerAsset.delinquencyTone"
          size="sm"
          :label="headerAsset.delinquencyStatusLabel"
        />
        <span v-else class="badge-placeholder">Delinquency unknown</span>
        
        <UiBadge
          v-if="headerAsset?.propertyTypeLabel"
          :tone="headerAsset.propertyTypeTone"
          size="sm"
          :label="headerAsset.propertyTypeLabel"
        />
        <span v-else class="badge-placeholder">Property type unavailable</span>
      </div>
      
      <!-- Asset Details Fields -->
      <div class="details-fields">
        <div class="detail-field">
          <small class="text-muted d-block">Current Balance</small>
          <span class="fw-semibold text-dark">{{ formatCurrency(headerAsset?.currentBalance) }}</span>
        </div>
        <div class="detail-field">
          <small class="text-muted d-block">Total Debt</small>
          <span class="fw-semibold text-dark">{{ formatCurrency(headerAsset?.totalDebt) }}</span>
        </div>
        <div class="detail-field">
          <small class="text-muted d-block">UW As-Is - ARV</small>
          <span class="fw-semibold text-dark">{{ formatCurrencyRange(headerAsset?.uwAsIsValue, headerAsset?.uwArvValue) }}</span>
        </div>
      </div>

      <div v-if="hubId" class="d-flex gap-2">
        <button
          type="button"
          class="btn btn-sm btn-outline-primary followup-trigger"
          @click="openFollowupModal"
          :title="followups.length ? `Follow-ups: ${followups.length}` : 'Create follow-up'"
        >
          Create Follow-up
          <span v-if="followups.length" class="badge bg-primary ms-2">{{ followups.length }}</span>
        </button>
        <button
          type="button"
          class="btn btn-sm btn-outline-primary"
          @click="openTaskModal"
          title="Create task"
        >
          Create Task
        </button>
      </div>
    </div>

    <!-- KPI Cards Row -->
    <div class="kpi-cards-row">
      <div class="kpi-card">
        <div class="kpi-main">
          <div class="kpi-number">{{ taskMetrics.active_track_count || 0 }}</div>
          <div class="kpi-title">Active Tracks</div>
          <div class="kpi-badges-container">
            <UiBadge
              v-for="badge in taskMetrics.active_track_badges"
              :key="badge.key"
              :tone="badge.tone"
              size="sm"
            >{{ badge.label }}</UiBadge>
          </div>
        </div>
        <i class="kpi-icon fas fa-clock text-warning"></i>
      </div>

      <div class="kpi-card">
        <div class="kpi-main">
          <div class="kpi-number">{{ activeTaskCount }}</div>
          <div class="kpi-title">Active Tasks</div>
          <div class="kpi-badges-container">
            <UiBadge
              v-for="pill in taskMetrics.active_items"
              :key="pill.key"
              :tone="pill.tone"
              size="sm"
            >{{ pill.label }}</UiBadge>
          </div>
        </div>
        <i class="kpi-icon fas fa-spinner text-primary"></i>
      </div>

      <div class="kpi-card">
        <div class="kpi-main">
          <div class="kpi-number">{{ completedTaskCount }}</div>
          <div class="kpi-title">Completed Tasks</div>
          <div class="kpi-badges-container">
            <UiBadge
              v-for="pill in taskMetrics.completed_items"
              :key="pill.key"
              :tone="pill.tone"
              size="sm"
            >{{ pill.label }}</UiBadge>
          </div>
        </div>
        <i class="kpi-icon fas fa-check-circle text-success"></i>
      </div>
    </div>

    <!-- Activity Widgets Row -->
    <div class="activity-widgets-row">
      <div class="activity-widget">
        <RecentActivity
          title="Recent Activity"
          :activityWindowHeight="'280px'"
          :activityData="activityItems"
        />
      </div>
      <div class="activity-widget">
        <UpcomingDeadlines v-if="hubId" :hub-id="hubId" />
      </div>
      <div class="activity-widget">
        <KeyContacts v-if="hubId" :hubId="hubId" />
      </div>
    </div>

    <!-- Track Selection Card -->
    <div class="track-card">
      <div class="track-header">
        <h5 class="track-title">
          <i class="fas fa-stream"></i>
          Current Track(s)
        </h5>
        <div class="d-flex align-items-center gap-2">
          <button
            type="button"
            class="collapse-toggle-btn"
            @click.stop="toggleTracksCollapsed"
            :aria-expanded="!tracksCollapsed ? 'true' : 'false'"
            aria-label="Toggle tracks visibility"
            title="Collapse/Expand Tracks"
          >
            <svg v-if="tracksCollapsed" xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
              <path fill-rule="evenodd" d="M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z"/>
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
              <path fill-rule="evenodd" d="M7.646 4.646a.5.5 0 0 1 .708 0l6 6a.5.5 0 0 1-.708.708L8 5.707l-5.646 5.647a.5.5 0 0 1-.708-.708l6-6z"/>
            </svg>
          </button>
          <div class="track-menu-wrapper" ref="trackMenuRef">
            <button 
              type="button" 
              class="track-button"
              :disabled="!hubId || ensureBusy" 
              @click.stop="toggleTrackMenu"
            >
              Choose Track
            </button>
            
            <div v-if="showTrackMenu" class="track-dropdown" @click.stop>
              <button class="track-option" @click="selectTrack('modification')" :disabled="ensureBusy">
                <UiBadge tone="modification-green" size="md">Modification</UiBadge>
              </button>
              <button class="track-option" @click="selectTrack('short_sale')" :disabled="ensureBusy">
                <UiBadge tone="warning" size="md">Short Sale</UiBadge>
              </button>
              <button class="track-option" @click="selectTrack('dil')" :disabled="ensureBusy">
                <UiBadge tone="primary" size="md">Deed-in-Lieu</UiBadge>
              </button>
              <button class="track-option" @click="selectTrack('fc')" :disabled="ensureBusy">
                <UiBadge tone="danger" size="md">Foreclosure</UiBadge>
              </button>
              <button class="track-option" @click="selectTrack('reo')" :disabled="ensureBusy">
                <UiBadge tone="info" size="md">REO</UiBadge>
              </button>
              <button class="track-option" @click="selectTrack('note_sale')" :disabled="ensureBusy">
                <UiBadge tone="secondary" size="md">Note Sale</UiBadge>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- WHAT: Two-column layout - Outcomes | Master Notes -->
      <!-- WHY: Consolidate all notes into single section instead of per-outcome -->
      <!-- HOW: Row with two equal columns using Bootstrap grid -->
      <div class="row g-3">
        <!-- Left Column: Track Outcomes -->
        <div class="col-lg-6">
          <div class="track-outcomes">
            <DilCard v-if="visibleOutcomes.dil" :hubId="hubId!" :masterCollapsed="tracksCollapsed" @delete="() => requestDelete('dil')" />
            <FcCard v-if="visibleOutcomes.fc" :hubId="hubId!" :masterCollapsed="tracksCollapsed" @delete="() => requestDelete('fc')" />
            <ReoCard v-if="visibleOutcomes.reo" :hubId="hubId!" :masterCollapsed="tracksCollapsed" @delete="() => requestDelete('reo')" />
            <ShortSaleCard v-if="visibleOutcomes.short_sale" :hubId="hubId!" :masterCollapsed="tracksCollapsed" @delete="() => requestDelete('short_sale')" />
            <ModificationCard v-if="visibleOutcomes.modification" :hubId="hubId!" :masterCollapsed="tracksCollapsed" @delete="() => requestDelete('modification')" />
            <NoteSaleCard v-if="visibleOutcomes.note_sale" :hubId="hubId!" :masterCollapsed="tracksCollapsed" @delete="() => requestDelete('note_sale')" />
            
            <div v-if="!anyVisibleOutcome" class="no-tracks">
              <i class="fas fa-info-circle"></i>
              Pick a track above to create its card for this asset.
            </div>
          </div>
        </div>
        
        <!-- Right Column: Master Notes Section -->
        <div class="col-lg-6">
          <MasterNotesSection v-if="hubId" :hubId="hubId" />
        </div>
      </div>
    </div>

    <!-- Confirm Delete Modal (Hyper UI style) -->
    <template v-if="confirm.open">
      <!-- Backdrop behind modal -->
      <div class="modal-backdrop fade show" style="z-index: 1050;"></div>
      <!-- Modal above backdrop -->
      <div class="modal fade show" tabindex="-1" role="dialog" aria-modal="true"
           style="display: block; position: fixed; inset: 0; z-index: 1055;">
        <div class="modal-dialog modal-dialog-centered" role="document">
          <div class="modal-content">
            <div class="modal-header bg-danger-subtle">
              <h5 class="modal-title d-flex align-items-center">
                <i class="fas fa-triangle-exclamation text-danger me-2"></i>
                Confirm Deletion
              </h5>
              <button type="button" class="btn-close" aria-label="Close" @click="closeConfirm"></button>
            </div>
            <div class="modal-body">
              <p class="mb-0">Are you sure you want to delete this outcome record? This action cannot be undone.</p>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-light" @click="closeConfirm">Cancel</button>
              <button type="button" class="btn btn-danger" @click="confirmDelete" :disabled="confirm.busy">
                <span v-if="confirm.busy" class="spinner-border spinner-border-sm me-2"></span>
                Delete
              </button>
            </div>
          </div>
        </div>
      </div>
    </template>

    <template v-if="followupModalOpen">
      <div class="modal-backdrop fade show" style="z-index: 1050;"></div>
      <div class="modal fade show" tabindex="-1" role="dialog" aria-modal="true"
           style="display: block; position: fixed; inset: 0; z-index: 1055;">
        <div class="modal-dialog modal-dialog-centered modal-lg" role="document">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title d-flex align-items-center me-3">
                Follow-ups
              </h5>
              <div class="d-flex align-items-center gap-3 ms-auto">
                <div class="form-check form-switch m-0">
                  <input
                    id="followup-public"
                    v-model="newFollowup.is_public"
                    class="form-check-input"
                    type="checkbox"
                    role="switch"
                  />
                  <label class="form-check-label small" for="followup-public">Public Follow-up</label>
                </div>
                <button type="button" class="btn-close" aria-label="Close" @click="closeFollowupModal"></button>
              </div>
            </div>
            <div class="modal-body">
              <div class="row g-2 align-items-end">
                <div class="col-12 col-md-4">
                  <label class="form-label small mb-1">Reason</label>
                  <select v-model="newFollowup.reason" class="form-select form-select-sm">
                    <option value="">Select…</option>
                    <option v-for="opt in followupReasonOptions" :key="opt.value" :value="opt.value">
                      {{ opt.label }}
                    </option>
                  </select>
                </div>

                <div class="col-12 col-md-4">
                  <label class="form-label small mb-1">Date</label>
                  <div class="input-group input-group-sm">
                    <input v-model="newFollowup.date" type="date" class="form-control form-control-sm" />
                    <button type="button" class="btn btn-outline-primary" @click="setFollowupDateOffset(15)">+15</button>
                    <button type="button" class="btn btn-outline-primary" @click="setFollowupDateOffset(30)">+30</button>
                  </div>
                </div>

                <div class="col-12 col-md-4">
                  <label class="form-label small mb-1">Title (optional)</label>
                  <div class="input-group input-group-sm">
                    <input
                      v-model="newFollowup.title"
                      type="text"
                      class="form-control form-control-sm"
                      placeholder="Task title..."
                      @keyup.enter="createFollowup"
                    />
                    <button
                      type="button"
                      class="btn btn-primary"
                      :disabled="followupCreateBusy || !newFollowup.date"
                      @click="createFollowup"
                    >
                      <span v-if="followupCreateBusy" class="spinner-border spinner-border-sm me-1"></span>
                      Add
                    </button>
                  </div>
                </div>
              </div>

              <div v-if="followupsLoading" class="text-muted small d-flex align-items-center gap-2 mt-3">
                <span class="spinner-border spinner-border-sm"></span>
                Loading…
              </div>
              <div v-else-if="followupsError" class="text-danger small mt-3">{{ followupsError }}</div>

              <template v-else-if="followups.length">
                <hr class="my-3" />

                <div class="followups-list">
                  <div class="followups-items">
                    <div v-for="f in followups" :key="f.id" class="followup-item">
                      <div class="followup-main">
                        <div class="followup-line">
                          <span class="followup-date">{{ f.date }}</span>
                          <UiBadge :tone="f.is_public ? 'primary' : 'secondary'" size="sm">{{ f.is_public ? 'Public' : 'Private' }}</UiBadge>
                          <span v-if="f.reason" class="text-muted small">{{ reasonLabel(f.reason) }}</span>
                        </div>
                        <div class="followup-title">{{ f.title }}</div>
                      </div>

                      <button
                        v-if="f.editable"
                        type="button"
                        class="btn btn-sm btn-outline-success"
                        :disabled="followupDeleteBusyId === f.id"
                        @click="deleteFollowup(f.id)"
                      >
                        <span v-if="followupDeleteBusyId === f.id" class="spinner-border spinner-border-sm me-2"></span>
                        Done
                      </button>
                    </div>
                  </div>
                </div>
              </template>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-light" @click="closeFollowupModal">Close</button>
            </div>
          </div>
        </div>
      </div>
    </template>

    
    <!-- Filters and legacy outcome list removed -->
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import http from '@/lib/http'
defineOptions({
  name: 'AmLlTasking',
})
// (legacy imports removed)
import UiBadge from '@/components/ui/UiBadge.vue'
import { getDelinquencyBadgeTone, getPropertyTypeBadgeTone } from '@/config/badgeTokens'
// Outcome cards + store
import DilCard from '@/views/am_module/loanlvl/am_tasking/outcomes/DilCard.vue'
import FcCard from '@/views/am_module/loanlvl/am_tasking/outcomes/FcCard.vue'
import ReoCard from '@/views/am_module/loanlvl/am_tasking/outcomes/ReoCard.vue'
import ShortSaleCard from '@/views/am_module/loanlvl/am_tasking/outcomes/ShortSaleCard.vue'
import ModificationCard from '@/views/am_module/loanlvl/am_tasking/outcomes/ModificationCard.vue'
import NoteSaleCard from '@/views/am_module/loanlvl/am_tasking/outcomes/NoteSaleCard.vue'
import { useAmOutcomesStore, type OutcomeType } from '@/stores/outcomes'
// Recent Activity widget (feature-local). Path: views/.../am_tasking/components/recent-activity.vue
import RecentActivity, { type ActivityItem } from '@/views/am_module/loanlvl/am_tasking/components/recent-activity.vue'
// Milestones Card widget (feature-local). Path: views/.../am_tasking/components/milestonesCard.vue
import UpcomingDeadlines from '@/views/am_module/loanlvl/am_tasking/components/milestonesCard.vue'
// Key Contacts widget (feature-local). Path: views/.../am_tasking/components/KeyContacts.vue
import KeyContacts from '@/views/am_module/loanlvl/am_tasking/components/KeyContacts.vue'
// WHAT: Master notes section component - consolidated notes for all outcomes
// WHY: Replace individual notes sections in each outcome card with single master panel
// WHERE: views/am_module/loanlvl/am_tasking/components/MasterNotesSection.vue
import MasterNotesSection from '@/views/am_module/loanlvl/am_tasking/components/MasterNotesSection.vue'
// Event bus for auto-refresh functionality
import { eventBus, refreshHubData } from '@/lib/eventBus'

interface HeaderAssetView {
  propertyAddress: string
  loanNumber: string | number | undefined
  propertyType: string | null
  assetStatus: string
  monthsDelinquentLabel: string
  borrowerName: string
  originalAmount?: number
  currentBalance?: number
  totalDebt?: number
  delinquencyStatus?: string | null
  delinquencyStatusLabel?: string | null
  delinquencyTone: import('@/config/badgeTokens').BadgeToneKey
  propertyTypeLabel?: string | null
  propertyTypeTone: import('@/config/badgeTokens').BadgeToneKey
  // Underwriting values used for the UW Property Value range display
  uwAsIsValue?: number | null
  uwArvValue?: number | null
}

interface Subtask {
  id: number
  title: string
  status: 'pending' | 'in_progress' | 'completed'
  dueDate: string
  assignedTo: string
  notes?: string
  completedDate?: string
}

interface Outcome {
  id: number
  assetId: number
  outcomeType: 'foreclosure' | 'modification' | 'deed_in_lieu' | 'short_sale'
  title: string
  overallStatus: 'pending' | 'in_progress' | 'completed'
  priority: 'low' | 'medium' | 'high'
  startDate: string
  targetDate: string
  assignedTo: string
  description: string
  subtasks: Subtask[]
}

interface Asset {
  id: number
  propertyAddress: string
  borrowerName: string
  loanAmount: number
  loanNumber: string
  propertyType: string
  currentBalance: number
  monthsDelinquent: number
  assetStatus?: string
  delinquencyStatus?: string
  totalDebt?: number
}

const props = withDefaults(defineProps<{ 
  row?: Record<string, any> | null
  assetHubId?: string | number | null 
}>(), {
  row: null,
  assetHubId: null,
})

// Reactive state
const currentAssetId = ref<number>(1)

// Mock data - replace with Django API calls
const assets = ref<Asset[]>([
  {
    id: 1,
    propertyAddress: '123 Main St, Anytown, ST 12345',
    borrowerName: 'John Smith',
    loanAmount: 250000,
    loanNumber: 'LN-2024-001',
    propertyType: 'Single Family',
    currentBalance: 235000,
    monthsDelinquent: 4,
    assetStatus: 'In Review',
    delinquencyStatus: '60',
    totalDebt: 247500
  },
  {
    id: 2,
    propertyAddress: '456 Oak Ave, Another City, ST 67890',
    borrowerName: 'Jane Doe',
    loanAmount: 180000,
    loanNumber: 'LN-2024-002',
    propertyType: 'Condo',
    currentBalance: 165000,
    monthsDelinquent: 2,
    assetStatus: 'Active',
    delinquencyStatus: '30',
    totalDebt: 172250
  }
])

// Demo activity items for the RecentActivity widget (replace with backend feed later)
const activityItems = ref<ActivityItem[]>([
  { id: 1, icon: 'mdi-file-document', title: 'DIL Drafted', text: 'Waiting on legal', boldText: 'for signature', subtext: 'Today', color: 'warning' },
  { id: 2, icon: 'mdi-gavel', title: 'FC Filing', text: 'Filed with county', boldText: 'NOD/NOI', subtext: 'Yesterday', color: 'primary' },
])


const outcomes = ref<Outcome[]>([
  {
    id: 1,
    assetId: 1,
    outcomeType: 'foreclosure',
    title: 'Foreclosure Proceedings',
    overallStatus: 'in_progress',
    priority: 'high',
    startDate: '2024-09-15',
    targetDate: '2024-11-15',
    assignedTo: 'Mike Johnson',
    description: 'Complete foreclosure process including NOD filing and sale scheduling.',
    subtasks: [
      {
        id: 101,
        title: 'Property Inspection',
        status: 'completed',
        dueDate: '2024-09-25',
        assignedTo: 'Tom Brown',
        notes: 'Property in good condition, occupied',
        completedDate: '2024-09-23'
      },
      {
        id: 102,
        title: 'Notice of Default Filed',
        status: 'in_progress',
        dueDate: '2024-10-15',
        assignedTo: 'Mike Johnson',
        notes: 'NOD filed with county recorder. 30-day response period active.'
      }
    ]
  }
])

// Resolve AM asset hub id to hit backend endpoints
const amId = computed<number | null>(() => {
  if (props.assetHubId != null && props.assetHubId !== '') return Number(props.assetHubId)
  const rid = props.row && (props.row as any).id
  return rid != null ? Number(rid) : null
})

function syncAssetId(next: number | null | undefined) {
  if (typeof next !== 'number' || Number.isNaN(next)) return
  const exists = assets.value.some((asset: Asset) => asset.id === next)
  if (exists) {
    currentAssetId.value = next
  }
}

watch(amId, (id) => {
  syncAssetId(id)
})

watch(() => props.row, (row) => {
  const nextId = row && (row as any).id
  syncAssetId(nextId != null ? Number(nextId) : null)
})

// Computed properties
const currentAsset = computed<Asset | undefined>(() => {
  // Identify which mock asset matches the currently selected id so we can pull mock data
  return assets.value.find((asset: Asset) => asset.id === currentAssetId.value)
})

const currentAssetIndex = computed<number>(() => {
  // Track the array index for navigation statistics even if the header runs in template mode
  return assets.value.findIndex((asset: Asset) => asset.id === currentAssetId.value)
})

const headerAsset = computed<HeaderAssetView>(() => {
  // Capture the incoming row payload (may be null depending on upstream selection state)
  const rowData = props.row as Record<string, any> | null

  // Reuse mock asset data as a fallback when the parent row does not provide a specific field
  const fallback = currentAsset.value ?? null

  // Build a display address by stitching street, city, state, and zip together
  const addressParts: string[] = []
  if (rowData?.street_address) addressParts.push(String(rowData.street_address).trim())
  if (rowData?.city) addressParts.push(String(rowData.city).trim())
  if (rowData?.state) addressParts.push(String(rowData.state).trim())
  if (rowData?.zip) addressParts.push(String(rowData.zip).trim())
  const propertyAddress = addressParts.length > 0
    ? addressParts.join(', ')
    : fallback?.propertyAddress ?? 'No address selected'

  // Normalize the loan number field across potential snake_case / camelCase keys
  const loanNumber = (
    rowData?.loan_number ??
    rowData?.loanNumber ??
    fallback?.loanNumber ??
    '—'
  )

  // Resolve property type (snake_case or camelCase) with safe fallback text
  const propertyTypeRaw = (
    rowData?.property_type ??
    rowData?.propertyType ??
    fallback?.propertyType ??
    null
  )
  const propertyType = propertyTypeRaw ? String(propertyTypeRaw) : null

  // Identify an asset status label from the upstream row and keep a clear fallback for design mode
  const assetStatus = (
    rowData?.asset_status ??
    rowData?.assetStatus ??
    fallback?.assetStatus ??
    'Status pending'
  )

  // Resolve delinquency status bucket (e.g., "30", "60", "90", "120_plus", "current")
  const delinquencyStatus = (
    rowData?.delinquency_status ??
    rowData?.delinquencyStatus ??
    fallback?.delinquencyStatus ??
    null
  ) as string | null

  // Map bucket to a short label and badge styling for the header pill
  const delinquencyStatusLabel = delinquencyStatus
    ? (({
        current: 'Current',
        '30': '30D',
        '60': '60D',
        '90': '90D',
        '120_plus': '120+D',
      } as Record<string, string>)[delinquencyStatus] ?? delinquencyStatus.toUpperCase()) + ' DLQ'
    : null
  const delinquencyTone = getDelinquencyBadgeTone(delinquencyStatus ?? undefined)

  // Determine property type badge tone + label
  const propertyTypeLabel = propertyType ?? null
  const propertyTypeTone = getPropertyTypeBadgeTone(propertyTypeLabel ?? undefined)

  // Determine delinquency months and format a user-friendly label
  const monthsDelinquentRaw = (
    rowData?.months_dlq ??
    rowData?.monthsDelinquent ??
    fallback?.monthsDelinquent ??
    null
  )
  const monthsDelinquentNumber = typeof monthsDelinquentRaw === 'string'
    ? Number.parseFloat(monthsDelinquentRaw)
    : monthsDelinquentRaw
  const monthsDelinquentLabel = Number.isFinite(monthsDelinquentNumber)
    ? `${monthsDelinquentNumber} months delinquent`
    : 'Delinquency unknown'

  // Borrower name fallback chain supports both naming conventions
  const borrowerName = (
    rowData?.borrower_name ??
    rowData?.borrowerName ??
    fallback?.borrowerName ??
    'Borrower pending'
  )

  // --- Servicer data alignment guard ---
  // Only trust nested servicer data when its hub id matches the row's hub id
  const hubId = (rowData as any)?.asset_hub_id ?? null
  const servicer = (rowData as any)?.servicer_loan_data ?? null
  const servicerHubId = servicer?.asset_hub_id ?? null
  const servicerAligned = hubId != null && servicerHubId != null && Number(hubId) === Number(servicerHubId)

  // Total debt prefers aligned servicer payload; fallback to mocked asset or row totals
  const totalDebt = normalizeNumeric(
    (servicerAligned ? servicer?.total_debt : null) ??
    rowData?.total_debt ??
    rowData?.servicer_total_debt ??
    fallback?.totalDebt ??
    null
  )

  // Original balance can arrive as string/number; normalize to number when possible
  const originalAmount = normalizeNumeric(
    rowData?.original_balance ??
    rowData?.originalAmount ??
    fallback?.loanAmount ??
    null
  )

  // Current balance: prefer aligned servicer current_balance, then row fallback
  const currentBalance = normalizeNumeric(
    (servicerAligned ? servicer?.current_balance : null) ??
    rowData?.current_balance ??
    rowData?.currentBalance ??
    fallback?.currentBalance ??
    null
  )

  // Return the unified object consumed by the header template bindings
  return {
    propertyAddress,
    loanNumber,
    propertyType,
    assetStatus,
    delinquencyStatus,
    delinquencyStatusLabel,
    delinquencyTone,
    propertyTypeLabel,
    propertyTypeTone,
    monthsDelinquentLabel,
    borrowerName,
    totalDebt: totalDebt ?? undefined,
    originalAmount: Number.isFinite(originalAmount as number) ? (originalAmount as number) : undefined,
    currentBalance: Number.isFinite(currentBalance as number) ? (currentBalance as number) : undefined,
    // Map UW values coming from the row payload (flat serializer fields)
    // Use internal_asis_value and internal_arv_value per AssetInventoryRowSerializer
    uwAsIsValue: normalizeNumeric((rowData as any)?.internal_asis_value),
    uwArvValue: normalizeNumeric((rowData as any)?.internal_arv_value),
  }
})

const assetOutcomes = computed<Outcome[]>(() => {
  return outcomes.value.filter((outcome: Outcome) => outcome.assetId === currentAssetId.value)
})

// (legacy filteredOutcomes removed)

const outcomeStats = computed(() => {
  return {
    pending: assetOutcomes.value.filter(o => o.overallStatus === 'pending').length,
    in_progress: assetOutcomes.value.filter(o => o.overallStatus === 'in_progress').length,
    completed: assetOutcomes.value.filter(o => o.overallStatus === 'completed').length
  }
})

// ------- AM Outcomes (Track) integration -------
const outcomesStore = useAmOutcomesStore()
const ensureBusy = ref(false)
const selectedOutcome = ref<OutcomeType | ''>('')
const showTrackMenu = ref(false)
const trackMenuRef = ref<HTMLElement | null>(null)
const visibleOutcomes = ref<Record<OutcomeType, boolean>>({ dil: false, fc: false, reo: false, short_sale: false, modification: false, note_sale: false })
const anyVisibleOutcome = computed(() => Object.values(visibleOutcomes.value).some(Boolean))
// WHAT: Track whether outcome cards are collapsed or expanded
// WHY: Allow users to hide/show all outcome cards at once
const tracksCollapsed = ref(false)

// Resolve hub id from the incoming row props
const hubId = computed<number | null>(() => {
  const raw = (props.row as any)?.asset_hub_id
  return raw != null ? Number(raw) : null
})

type FollowupReason = 'nod_noi' | 'fc_counsel' | 'escrow' | 'reo'
type FollowupEvent = {
  id: number
  title: string
  date: string
  is_public: boolean
  reason: FollowupReason | null
  editable: boolean
}

const followupReasonOptions = [
  { value: 'nod_noi', label: 'NOD/NOI' },
  { value: 'fc_counsel', label: 'FC Counsel' },
  { value: 'escrow', label: 'Escrow' },
  { value: 'reo', label: 'REO' },
] as const

const followups = ref<FollowupEvent[]>([])
const followupsLoading = ref(false)
const followupsError = ref('')
const followupCreateBusy = ref(false)
const followupDeleteBusyId = ref<number | null>(null)
const followupModalOpen = ref(false)

const newFollowup = ref<{ reason: FollowupReason | ''; date: string; title: string; is_public: boolean }>({
  reason: '',
  date: '',
  title: '',
  is_public: false,
})

function todayIso(): string {
  const d = new Date()
  const yyyy = d.getFullYear()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${yyyy}-${mm}-${dd}`
}

function addDaysIso(baseIso: string, days: number): string {
  const base = baseIso ? new Date(`${baseIso}T00:00:00`) : new Date()
  base.setDate(base.getDate() + days)
  const yyyy = base.getFullYear()
  const mm = String(base.getMonth() + 1).padStart(2, '0')
  const dd = String(base.getDate()).padStart(2, '0')
  return `${yyyy}-${mm}-${dd}`
}

function setFollowupDateOffset(days: number) {
  newFollowup.value.date = addDaysIso(todayIso(), days)
}

function reasonLabel(reason: FollowupReason): string {
  const found = followupReasonOptions.find((o) => o.value === reason)
  return found ? found.label : reason
}

async function fetchFollowups() {
  // WHAT: Fetch follow-ups for the current asset only
  // WHY: Create Follow-up button should show follow-ups for the asset being viewed
  const id = hubId.value
  if (!id) {
    followups.value = []
    return
  }
  followupsLoading.value = true
  followupsError.value = ''
  try {
    const resp = await http.get('/core/calendar/events/custom/', {
      params: {
        asset_hub_id: id,
        is_reminder: true,
        start_date: todayIso(),
      },
    })

    const rows = Array.isArray(resp.data) ? resp.data : []
    followups.value = rows.map((r: any) => ({
      id: Number(r.id),
      title: String(r.title ?? ''),
      date: String(r.date ?? ''),
      is_public: Boolean(r.is_public),
      reason: (r.reason as FollowupReason | null) ?? null,
      editable: Boolean(r.editable),
    }))
  } catch (e: any) {
    followupsError.value = 'Failed to load follow-ups.'
    console.error('[Followups] fetch failed', e)
  } finally {
    followupsLoading.value = false
  }
}

async function openFollowupModal() {
  // WHAT: Pre-fetch data before opening modal to prevent size flash
  // WHY: Bootstrap modal calculates size on open, so content should be ready
  await fetchFollowups()
  followupModalOpen.value = true
}

function closeFollowupModal() {
  followupModalOpen.value = false
}

function openTaskModal() {
  // TODO: Implement task creation modal
  alert('Task creation functionality coming soon!')
}

async function createFollowup() {
  const id = hubId.value
  if (!id) return
  if (!newFollowup.value.date) return

  followupCreateBusy.value = true
  try {
    const reason = newFollowup.value.reason ? newFollowup.value.reason : null
    const title = newFollowup.value.title?.trim()
      ? newFollowup.value.title.trim()
      : (reason ? `Follow-up: ${reasonLabel(reason)}` : 'Follow-up')

    await http.post('/core/calendar/events/custom/', {
      title,
      date: newFollowup.value.date,
      time: 'All Day',
      description: '',
      category: 'bg-warning',
      asset_hub: id,
      is_reminder: true,
      is_public: newFollowup.value.is_public,
      reason,
    })

    newFollowup.value.title = ''
    await fetchFollowups()
  } catch (e: any) {
    console.error('[Followups] create failed', e)
    alert('Failed to create follow-up. Please try again.')
  } finally {
    followupCreateBusy.value = false
  }
}

async function deleteFollowup(eventId: number) {
  followupDeleteBusyId.value = eventId
  try {
    await http.delete(`/core/calendar/events/custom/${eventId}/`)
    await fetchFollowups()
  } catch (e: any) {
    console.error('[Followups] delete failed', e)
    alert('Failed to delete follow-up. Please try again.')
  } finally {
    followupDeleteBusyId.value = null
  }
}

// Active outcome types for KPI header badges
const activeTypes = computed<OutcomeType[]>(() => {
  return (Object.keys(visibleOutcomes.value) as OutcomeType[]).filter(
    (k) => visibleOutcomes.value[k]
  )
})

// Map an outcome type to a human-readable label for UiBadge
function trackLabel(t: OutcomeType): string {
  switch (t) {
    case 'modification': return 'Modification'
    case 'short_sale': return 'Short Sale'
    case 'dil': return 'Deed-in-Lieu'
    case 'fc': return 'Foreclosure'
    case 'reo': return 'REO'
    case 'note_sale': return 'Note Sale'
    default: return t
  }
}

// Map an outcome type to a UiBadge tone defined in badgeTokens
function trackTone(t: OutcomeType): import('@/config/badgeTokens').BadgeToneKey {
  switch (t) {
    case 'modification': return 'modification-green'
    case 'short_sale': return 'warning'
    case 'dil': return 'primary'
    case 'fc': return 'danger'
    case 'reo': return 'info'
    case 'note_sale': return 'secondary'
    default: return 'secondary'
  }
}

// -------- Active Tasks KPI helpers --------
// Per-outcome task label maps (kept local to avoid importing component files)
const fcTaskLabel: Record<import('@/stores/outcomes').FcTaskType, string> = {
  nod_noi: 'NOD/NOI',
  fc_filing: 'FC Filing',
  mediation: 'Mediation',
  judgement: 'Judgement',
  redemption: 'Redemption',
  sale_scheduled: 'Sale Scheduled',
  sold: 'Sold',
}
const reoTaskLabel: Record<import('@/stores/outcomes').ReoTaskType, string> = {
  eviction: 'Eviction',
  trashout: 'Trashout',
  renovation: 'Renovation',
  marketing: 'Marketing',
  under_contract: 'Under Contract',
  sold: 'Sold',
}
// Tone maps aligned with outcome components' badgeClass definitions
const fcToneMap: Record<import('@/stores/outcomes').FcTaskType, BadgeToneKey> = {
  nod_noi: 'warning',
  fc_filing: 'primary',
  mediation: 'info',
  judgement: 'secondary',
  redemption: 'success',
  sale_scheduled: 'dark',
  sold: 'danger',
}
const reoToneMap: Record<import('@/stores/outcomes').ReoTaskType, BadgeToneKey> = {
  eviction: 'danger',
  trashout: 'warning',
  renovation: 'info',
  marketing: 'primary',
  under_contract: 'success',
  sold: 'secondary',
}
const shortSaleTaskLabel: Record<import('@/stores/outcomes').ShortSaleTaskType, string> = {
  list_price_accepted: 'List Price Accepted',
  listed: 'Listed',
  under_contract: 'Under Contract',
  sold: 'Sold',
}
const shortSaleToneMap: Record<import('@/stores/outcomes').ShortSaleTaskType, BadgeToneKey> = {
  list_price_accepted: 'warning',
  listed: 'info',
  under_contract: 'primary',
  sold: 'success',
}
// WHAT: Align DIL labels with subtask labels used in DilCard.vue (consistency across UI)
// WHY: Provide human-readable labels and badge colors for all DIL task types
// HOW: Complete mappings for all valid DilTaskType values: pursuing_dil, owner_contacted, dil_failed, dil_drafted, dil_executed
const dilTaskLabel: Record<import('@/stores/outcomes').DilTaskType, string> = {
  pursuing_dil: 'Pursuing DIL',
  owner_contacted: 'Borrowers/Heirs contacted',
  dil_failed: 'DIL Failed',
  dil_drafted: 'DIL Drafted',
  dil_executed: 'DIL Executed',
}
const dilToneMap: Record<import('@/stores/outcomes').DilTaskType, BadgeToneKey> = {
  pursuing_dil: 'info',
  owner_contacted: 'primary',
  dil_failed: 'danger',
  dil_drafted: 'warning',
  dil_executed: 'success',
}
const modificationTaskLabel: Record<import('@/stores/outcomes').ModificationTaskType, string> = {
  mod_drafted: 'Drafted',
  mod_executed: 'Executed',
  mod_rpl: 'Re-Performing',
  mod_failed: 'Failed',
}
const modificationToneMap: Record<import('@/stores/outcomes').ModificationTaskType, BadgeToneKey> = {
  mod_drafted: 'info',
  mod_executed: 'success',
  mod_rpl: 'primary',
  mod_failed: 'danger',
}
const noteSaleTaskLabel: Record<import('@/stores/outcomes').NoteSaleTaskType, string> = {
  potential_note_sale: 'Potential Note Sale',
  out_to_market: 'Out to Market',
  pending_sale: 'Pending Sale',
  sold: 'Sold',
}
const noteSaleToneMap: Record<import('@/stores/outcomes').NoteSaleTaskType, BadgeToneKey> = {
  potential_note_sale: 'secondary',
  out_to_market: 'info',
  pending_sale: 'warning',
  sold: 'success',
}

type BadgeToneKey = import('@/config/badgeTokens').BadgeToneKey
type PillItem = { key: string; label: string; tone: BadgeToneKey }

// Pick only the most recent subtask per outcome for Active Tasks
const activeTaskItems = computed<PillItem[]>(() => {
  const id = hubId.value
  if (!id) return []
  const items: PillItem[] = []

  // Helper: get latest by created_at (fallback to highest id)
  const pickLatest = <T extends { created_at?: string; id: number; task_type: string }>(list: T[]) => {
    if (!list?.length) return null
    const sorted = [...list].sort((a, b) => {
      const ad = a.created_at ? Date.parse(a.created_at) : 0
      const bd = b.created_at ? Date.parse(b.created_at) : 0
      if (ad === bd) return a.id - b.id
      return ad - bd
    })
    return sorted[sorted.length - 1]
  }

  // FC
  if (visibleOutcomes.value.fc) {
    const list = outcomesStore.fcTasksByHub[id] ?? []
    const latest = pickLatest(list)
    if (latest) {
      const tp = latest.task_type as import('@/stores/outcomes').FcTaskType
      items.push({ key: `fc-${latest.id}`, label: `FC: ${fcTaskLabel[tp] ?? latest.task_type}`, tone: fcToneMap[tp] })
    }
  }
  // REO
  if (visibleOutcomes.value.reo) {
    const list = outcomesStore.reoTasksByHub[id] ?? []
    const latest = pickLatest(list)
    if (latest) {
      const tp = latest.task_type as import('@/stores/outcomes').ReoTaskType
      items.push({ key: `reo-${latest.id}`, label: `REO: ${reoTaskLabel[tp] ?? latest.task_type}`, tone: reoToneMap[tp] })
    }
  }
  // Short Sale
  if (visibleOutcomes.value.short_sale) {
    const list = outcomesStore.shortSaleTasksByHub[id] ?? []
    const latest = pickLatest(list)
    if (latest) {
      const tp = latest.task_type as import('@/stores/outcomes').ShortSaleTaskType
      items.push({ key: `ss-${latest.id}`, label: `Short Sale: ${shortSaleTaskLabel[tp] ?? latest.task_type}`, tone: shortSaleToneMap[tp] })
    }
  }
  // DIL
  if (visibleOutcomes.value.dil) {
    const list = outcomesStore.dilTasksByHub[id] ?? []
    const latest = pickLatest(list)
    if (latest) {
      const tp = latest.task_type as import('@/stores/outcomes').DilTaskType
      items.push({ key: `dil-${latest.id}`, label: `DIL: ${dilTaskLabel[tp] ?? latest.task_type}`, tone: dilToneMap[tp] })
    }
  }
  // Modification
  if (visibleOutcomes.value.modification) {
    const list = outcomesStore.modificationTasksByHub[id] ?? []
    const latest = pickLatest(list)
    if (latest) {
      const tp = latest.task_type as import('@/stores/outcomes').ModificationTaskType
      items.push({ key: `mod-${latest.id}`, label: `Mod: ${modificationTaskLabel[tp] ?? latest.task_type}`, tone: modificationToneMap[tp] })
    }
  }
  // Note Sale
  if (visibleOutcomes.value.note_sale) {
    const list = outcomesStore.noteSaleTasksByHub[id] ?? []
    const latest = pickLatest(list)
    if (latest) {
      const tp = latest.task_type as import('@/stores/outcomes').NoteSaleTaskType
      items.push({ key: `note-sale-${latest.id}`, label: `Note Sale: ${noteSaleTaskLabel[tp] ?? latest.task_type}`, tone: noteSaleToneMap[tp] })
    }
  }
  return items
})

// WHAT: Task metrics from backend API
// WHY: Backend determines completion based on task_type (e.g., "sold", "executed")
// WHERE: API endpoint at /api/am/outcomes/task-metrics/
const taskMetrics = ref<{
  active_count: number
  completed_count: number
  active_items: Array<{ key: string; label: string; tone: BadgeToneKey }>
  completed_items: Array<{ key: string; label: string; tone: BadgeToneKey }>
  active_tracks: string[]
  completed_tracks: string[]
  active_track_badges: Array<{ key: string; label: string; tone: BadgeToneKey }>
  active_track_count: number
  completed_track_count: number
}>({ 
  active_count: 0, 
  completed_count: 0, 
  active_items: [], 
  completed_items: [],
  active_tracks: [],
  completed_tracks: [],
  active_track_badges: [],
  active_track_count: 0,
  completed_track_count: 0,
})

// WHAT: Fetch task metrics from backend
// WHY: Get accurate active/completed counts based on task_type completion logic
// HOW: Call API with asset_hub_id query param
async function fetchTaskMetrics() {
  const id = hubId.value
  if (!id) return
  
  try {
    const response = await http.get('/am/outcomes/task-metrics/', {
      params: { asset_hub_id: id }
    })
    taskMetrics.value = response.data
  } catch (error) {
    console.error('Failed to fetch task metrics:', error)
  }
}

// WHAT: Computed properties for template binding
// WHY: Provide reactive counts for KPI cards
const completedTaskCount = computed<number>(() => taskMetrics.value.completed_count)
const activeTaskCount = computed<number>(() => taskMetrics.value.active_count)

// WHAT: Watch hubId and fetch metrics when it changes
// WHY: Update metrics when user navigates to different asset
watch(hubId, () => {
  if (hubId.value) {
    fetchTaskMetrics()
  }
}, { immediate: true })

function toggleTrackMenu() {
  showTrackMenu.value = !showTrackMenu.value
}
// WHAT: Toggle collapsed/expanded state of all outcome cards
// WHY: Allow users to quickly hide/show all tracks and tasks
function toggleTracksCollapsed() {
  tracksCollapsed.value = !tracksCollapsed.value
}
async function selectTrack(type: OutcomeType) {
  if (!hubId.value) return
  try {
    ensureBusy.value = true
    selectedOutcome.value = type
    await outcomesStore.ensureOutcome(hubId.value, type)
    visibleOutcomes.value[type] = true
    
    // WHAT: Emit track added event for auto-refresh
    // WHY: Notify other components that new track was created
    eventBus.emit('track:added', { trackType: type, hubId: hubId.value })
    refreshHubData(hubId.value)
  } finally {
    ensureBusy.value = false
    showTrackMenu.value = false
  }
}
// Close menu on outside click
function handleTrackOutside(e: MouseEvent) {
  const root = trackMenuRef.value
  if (!root) return
  if (showTrackMenu.value && !root.contains(e.target as Node)) showTrackMenu.value = false
}
// NOTE: Lifecycle hooks consolidated at end of script section for clarity

// Confirm deletion modal
const confirm = ref<{ open: boolean; type: OutcomeType | null; busy: boolean }>({ open: false, type: null, busy: false })
function requestDelete(type: OutcomeType) {
  confirm.value = { open: true, type, busy: false }
}
function closeConfirm() { confirm.value.open = false }
async function confirmDelete() {
  if (!hubId.value || !confirm.value.type) return
  try {
    confirm.value.busy = true
    const deletedType = confirm.value.type
    
    // WHAT: Delete outcome from backend
    await outcomesStore.deleteOutcome(hubId.value, deletedType)
    
    // WHAT: Hide the outcome card immediately
    // WHY: Prevent component update errors during deletion
    visibleOutcomes.value[deletedType] = false
    
    // WHAT: Wait for DOM update before emitting events
    // WHY: Ensure component is properly removed before notifying others
    await nextTick()
    
    // WHAT: Emit track deleted event for auto-refresh
    // WHY: Notify other components that track was removed
    eventBus.emit('track:deleted', { trackType: deletedType, hubId: hubId.value })
    refreshHubData(hubId.value)
    
    closeConfirm()
  } catch (err: any) {
    console.error('Failed to delete outcome:', err)
    alert(`Failed to delete ${confirm.value.type}. Please try again.`)
  } finally {
    confirm.value.busy = false
  }
}

// Hydrate visible cards when hub changes
// WHAT: Checks which outcome tracks exist in backend and shows their cards
// WHY: On page load/refresh, we need to restore the visible track cards
// HOW: Fetches all outcome types in PARALLEL for better performance
async function refreshVisible() {
  visibleOutcomes.value = { dil: false, fc: false, reo: false, short_sale: false, modification: false, note_sale: false }
  const id = hubId.value
  if (!id) return
  
  const types: OutcomeType[] = ['dil', 'fc', 'reo', 'short_sale', 'modification', 'note_sale']
  
  // WHAT: Fetch all outcomes in parallel instead of sequentially
  // WHY: Reduces load time from 6 sequential calls to 1 parallel batch
  // HOW: Use Promise.allSettled to handle individual failures gracefully
  const outcomeResults = await Promise.allSettled(
    types.map(t => outcomesStore.fetchOutcome(id, t).then(exists => ({ type: t, exists })))
  )
  
  // WHAT: Process results and set visibility flags
  const existingTypes: OutcomeType[] = []
  for (const result of outcomeResults) {
    if (result.status === 'fulfilled' && result.value.exists) {
      visibleOutcomes.value[result.value.type] = true
      existingTypes.push(result.value.type)
    } else if (result.status === 'rejected') {
      console.error('[AM Tasking] Error fetching outcome:', result.reason)
    }
  }
  
  // WHAT: Preload task lists in parallel for existing outcomes
  // WHY: KPI widget needs task data; parallel fetch is faster
  const taskFetchers: Promise<any>[] = []
  for (const t of existingTypes) {
    if (t === 'fc') taskFetchers.push(outcomesStore.listFcTasks(id))
    else if (t === 'reo') taskFetchers.push(outcomesStore.listReoTasks(id))
    else if (t === 'short_sale') taskFetchers.push(outcomesStore.listShortSaleTasks(id))
    else if (t === 'dil') taskFetchers.push(outcomesStore.listDilTasks(id))
    else if (t === 'note_sale') taskFetchers.push(outcomesStore.listNoteSaleTasks(id))
    else if (t === 'modification') taskFetchers.push(outcomesStore.listModificationTasks(id))
  }
  
  if (taskFetchers.length) {
    await Promise.allSettled(taskFetchers)
  }
}
watch(hubId, refreshVisible)

watch(hubId, () => {
  fetchFollowups()
}, { immediate: true })

// Utility functions
const formatCurrency = (amount?: number | null) => {
  const numeric = typeof amount === 'string' ? Number.parseFloat(amount) : amount
  if (!Number.isFinite(numeric as number)) return '$0'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0
  }).format(numeric as number)
}

// Format a currency range like "$120,000 - $180,000".
// If one side is missing, show the available value only.
// If both are missing, show an em dash.
function formatCurrencyRange(asis?: number | null, arv?: number | null): string {
  const hasAsIs = Number.isFinite(asis as number)
  const hasArv = Number.isFinite(arv as number)
  if (hasAsIs && hasArv) return `${formatCurrency(asis)} - ${formatCurrency(arv)}`
  if (hasAsIs) return formatCurrency(asis)
  if (hasArv) return formatCurrency(arv)
  return '—'
}

const normalizeNumeric = (value: unknown): number | null => {
  if (value == null) return null
  if (typeof value === 'number' && Number.isFinite(value)) return value
  if (typeof value === 'string') {
    const parsed = Number.parseFloat(value)
    return Number.isFinite(parsed) ? parsed : null
  }
  return null
}
// (legacy helper functions removed)

// WHAT: Event handler for refreshing metrics
// WHY: Reusable handler for track/task change events
const handleMetricsRefresh = () => {
  if (hubId.value) fetchTaskMetrics()
}

// WHAT: Consolidated lifecycle hooks
// WHY: Single onMounted/onBeforeUnmount for all initialization and cleanup
// HOW: Combine all event listeners, data fetching, and DOM handlers
onMounted(() => {
  if (amId.value) {
    currentAssetId.value = amId.value
  }
  
  // WHAT: Initialize track menu outside click handler
  // WHY: Close menu when clicking outside
  document.addEventListener('click', handleTrackOutside)
  
  // WHAT: Load visible outcome cards on mount
  // WHY: Restore track cards when page loads
  refreshVisible()
  
  // WHAT: Listen for track and task change events
  // WHY: Update KPI cards when data changes
  eventBus.on('track:added', handleMetricsRefresh)
  eventBus.on('track:deleted', handleMetricsRefresh)
  eventBus.on('task:added', handleMetricsRefresh)
  eventBus.on('task:deleted', handleMetricsRefresh)
  eventBus.on('task:updated', handleMetricsRefresh)
})

// WHAT: Clean up all event listeners on unmount
// WHY: Prevent memory leaks
onBeforeUnmount(() => {
  document.removeEventListener('click', handleTrackOutside)
  eventBus.off('track:added', handleMetricsRefresh)
  eventBus.off('track:deleted', handleMetricsRefresh)
  eventBus.off('task:added', handleMetricsRefresh)
  eventBus.off('task:deleted', handleMetricsRefresh)
  eventBus.off('task:updated', handleMetricsRefresh)
})
</script>

<style scoped>
/* Container */
.tasking-container {
  width: 100%;
  max-width: 100%;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Header Card */
.header-card {
  background: #FDFBF7;
  border-radius: 0.375rem;
  padding: 1.25rem;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2rem;
  position: relative;
}

/* Follow-up and Task buttons container - positioned on the right */
.header-card > .d-flex.gap-2 {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
}

.followup-trigger {
  position: static;
}

.followup-item {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.75rem;
  border-top: 1px solid #f1f3f5;
  border-radius: 0.375rem;
  transition: background-color 0.2s ease;
}

.followup-item:hover {
  background-color: #f8f9fa;
}

.followup-item:first-child {
  border-top: none;
}

.followup-line {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.followup-date {
  font-weight: 600;
  color: #212529;
}

.followup-title {
  font-size: 0.95rem;
  color: #212529;
  margin-top: 0.1rem;
}

.header-badges {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.badge-placeholder {
  font-size: 0.875rem;
  color: #6c757d;
}

/* Details Fields */
.details-fields {
  display: flex;
  align-items: center;
  gap: 2rem;
  flex: 1;
}

.detail-field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  text-align: center;
}

/* KPI Cards Row */
.kpi-cards-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  background-color: transparent;
  align-items: stretch; /* Make all cards same height */
}

.kpi-card {
  background: #FDFBF7;
  border-radius: 0.375rem;
  padding: 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  min-height: 110px;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  height: 100%; /* Fill grid cell height */
  min-width: 0; /* Allow grid items to shrink below content width */
}

.kpi-main {
  flex: 1;
  min-width: 0;
}

.kpi-number {
  font-size: 2rem;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 0.375rem;
  color: #212529;
}

.kpi-title {
  font-size: 0.875rem;
  color: #6c757d;
  margin-bottom: 0.5rem;
}

.kpi-badges-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
  max-height: 3rem;
  overflow-y: auto;
}

.kpi-icon {
  font-size: 2rem;
  flex-shrink: 0;
  opacity: 0.7;
}

.no-data {
  font-size: 0.875rem;
  color: #6c757d;
  font-style: italic;
}

/* Activity Widgets Row */
.activity-widgets-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  background-color: transparent;
  align-items: stretch; /* Make all cards same height */
}

.activity-widget {
  min-height: 280px;
  height: 100%; /* Fill grid cell height */
  display: flex;
  flex-direction: column; /* Allow content to flow vertically */
  min-width: 0; /* Allow grid items to shrink below content width */
  overflow: hidden; /* Prevent content from breaking layout */
}

/* Ensure child components can also shrink */
.activity-widget > * {
  min-width: 0;
  width: 100%;
}

/* Track Card */
.track-card {
  background: #FDFBF7;
  border-radius: 0.375rem;
  overflow: hidden;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.track-header {
  padding: 1rem 1.25rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.track-title {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #212529;
}

/* WHAT: Collapse/expand toggle button styling */
/* WHY: Clean icon button to toggle track outcomes visibility */
.collapse-toggle-btn {
  background: transparent;
  border: 1px solid #6c757d;
  color: #6c757d;
  width: 2rem;
  height: 2rem;
  border-radius: 0.25rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.15s ease;
  padding: 0;
  flex-shrink: 0;
}

.collapse-toggle-btn:hover {
  background: #6c757d;
  color: white;
  border-color: #6c757d;
}

.collapse-toggle-btn svg {
  display: block;
}

.track-menu-wrapper {
  position: relative;
}

.track-button {
  background: #FDFBF7;
  border: 1px solid #0d6efd;
  color: #0d6efd;
  padding: 0.375rem 0.75rem; /* Symmetric padding */
  border-radius: 0.25rem;
  font-size: 0.875rem;
  cursor: pointer;
  position: relative;
  transition: all 0.15s ease;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
}

.track-button:hover:not(:disabled) {
  background: #0d6efd;
  color: white;
}

.track-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.track-button i {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.75rem;
}

.track-dropdown {
  position: absolute;
  right: 0;
  top: calc(100% + 0.25rem);
  background: #FDFBF7;
  border: 1px solid #dee2e6;
  border-radius: 0.375rem;
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
  padding: 0.75rem;
  min-width: 680px;
  z-index: 1060;
  display: flex;
  gap: 0.5rem;
  justify-content: center;
}

.track-option {
  background: transparent;
  border: none;
  padding: 0;
  cursor: pointer;
  transition: transform 0.15s ease;
}

.track-option:hover:not(:disabled) {
  transform: translateY(-2px);
}

.track-option:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.track-outcomes {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.no-tracks {
  text-align: center;
  padding: 3rem 1rem;
  color: #6c757d;
  font-size: 0.95rem;
}

.no-tracks i {
  margin-right: 0.5rem;
}

/* Responsive */
@media (max-width: 992px) {
  .header-card {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .details-fields {
    flex-wrap: wrap;
    gap: 1.5rem;
  }
  
  .kpi-cards-row {
    grid-template-columns: 1fr;
  }
  
  .activity-widgets-row {
    grid-template-columns: 1fr;
  }
  
  .track-dropdown {
    min-width: 100%;
    flex-wrap: wrap;
  }
}

@media (max-width: 768px) {
  .details-fields {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .kpi-number {
    font-size: 1.5rem;
  }
}
</style>

<style>
/* Global utility sizes for pill badges (Bootstrap badge compatible) */
.size_small {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
}
.kpi-badges .badge.size_small {
  font-size: 0.75rem; /* ensure override of earlier .kpi-badges .badge */
  padding: 0.25rem 0.5rem;
}
.size_med {
  font-size: 0.875rem;
  padding: 0.4rem 0.75rem;
}
</style>
