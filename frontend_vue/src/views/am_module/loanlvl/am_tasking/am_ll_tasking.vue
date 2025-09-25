<template>
  <!-- Asset Management: Outcome Manager -->
  <div class="am-tasking-wrapper">
    <!-- Asset Navigation Header (dynamic to selected asset) -->
    <b-card class="mb-4">
      <div class="d-flex align-items-center justify-content-between mb-3">
        <div>
          <h3 class="mb-1">{{ headerAsset?.propertyAddress || 'No address selected' }}</h3>
          <div class="d-flex align-items-center flex-wrap gap-3 text-muted">
            <div class="d-flex align-items-center gap-2">
              <UiBadge
                v-if="headerAsset?.delinquencyStatusLabel"
                :tone="headerAsset.delinquencyTone"
                size="sm"
                :label="headerAsset.delinquencyStatusLabel"
              />
              <span v-else class="text-body">Delinquency unknown</span>
            </div>
            <div class="d-flex align-items-center gap-2">
              <UiBadge
                v-if="headerAsset?.propertyTypeLabel"
                :tone="headerAsset.propertyTypeTone"
                size="sm"
                :label="headerAsset.propertyTypeLabel"
              />
              <span v-else class="text-body">Property type unavailable</span>
            </div>
          </div>
        </div>
        
      </div>
      
      <!-- Asset Details Row (static placeholders) -->
      <b-row class="g-3">
        <b-col md="3">
          <div class="bg-light rounded p-3">
            <div class="small text-muted">Current Balance</div>
            <div class="fw-semibold">{{ formatCurrency(headerAsset?.currentBalance) }}</div>
          </div>
        </b-col>
        <b-col md="3">
          <div class="bg-light rounded p-3">
            <div class="small text-muted">Total Debt</div>
            <div class="fw-semibold">{{ formatCurrency(headerAsset?.totalDebt) }}</div>
          </div>
        </b-col>
        <b-col md="3">
          <div class="bg-light rounded p-3">
            <div class="small text-muted">Borrower</div>
            <div class="fw-semibold">{{ headerAsset?.borrowerName || 'Borrower pending' }}</div>
          </div>
        </b-col>
        <b-col md="3">
          <div class="bg-light rounded p-3">
            <div class="small text-muted">Active Outcomes</div>
            <div class="fw-semibold">{{ outcomeStats.pending + outcomeStats.in_progress }}</div>
          </div>
        </b-col>
      </b-row>
    </b-card>

    <!-- Outcome Summary Cards -->
    <b-row class="g-3 mb-4">
      <b-col md="4">
        <b-card class="text-center h-100">
          <div class="d-flex align-items-center justify-content-between">
            <div>
              <div class="h2 text-warning mb-0">{{ outcomeStats.pending }}</div>
              <div class="small text-muted">Pending Outcomes</div>
            </div>
            <i class="fas fa-clock fa-2x text-warning"></i>
          </div>
        </b-card>
      </b-col>
      <b-col md="4">
        <b-card class="text-center h-100">
          <div class="d-flex align-items-center justify-content-between">
            <div>
              <div class="h2 text-primary mb-0">{{ outcomeStats.in_progress }}</div>
              <div class="small text-muted">In Progress</div>
            </div>
            <i class="fas fa-spinner fa-2x text-primary"></i>
          </div>
        </b-card>
      </b-col>
      <b-col md="4">
        <b-card class="text-center h-100">
          <div class="d-flex align-items-center justify-content-between">
            <div>
              <div class="h2 text-success mb-0">{{ outcomeStats.completed }}</div>
              <div class="small text-muted">Completed</div>
            </div>
            <i class="fas fa-check-circle fa-2x text-success"></i>
          </div>
        </b-card>
      </b-col>
    </b-row>

    <!-- Filters -->
    <b-card class="mb-4">
      <div class="d-flex align-items-center justify-content-between">
        <div class="d-flex align-items-center">
          <i class="fas fa-filter text-muted me-3"></i>
          
          <b-form-select v-model="outcomeFilter" size="sm" class="me-3" style="width: auto;">
            <option value="all">All Outcome Types</option>
            <option value="foreclosure">Foreclosure</option>
            <option value="modification">Modification</option>
            <option value="deed_in_lieu">Deed in Lieu</option>
            <option value="short_sale">Short Sale</option>
          </b-form-select>
          
          <b-form-select v-model="statusFilter" size="sm" style="width: auto;">
            <option value="all">All Statuses</option>
            <option value="pending">Pending</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
          </b-form-select>
        </div>
        
        <b-button variant="primary" size="sm" @click="createNewOutcome">
          <i class="fas fa-plus me-2"></i>
          New Outcome
        </b-button>
      </div>
    </b-card>

    <!-- Outcome Cards -->
    <div v-if="filteredOutcomes.length > 0" class="mb-4">
      <b-card 
        v-for="outcome in filteredOutcomes" 
        :key="outcome.id" 
        :class="['mb-3 border-start border-4', getPriorityBorderClass(outcome.priority)]"
      >
        <!-- Main Outcome Header -->
        <div class="d-flex align-items-start justify-content-between mb-3">
          <div class="d-flex align-items-center">
            <i :class="['me-3 fa-lg', getOutcomeIcon(outcome.outcomeType)]"></i>
            <div>
              <b-badge :variant="getOutcomeTypeVariant(outcome.outcomeType)" class="me-2">
                {{ getOutcomeTypeLabel(outcome.outcomeType) }}
              </b-badge>
              <b-badge :variant="getStatusVariant(outcome.overallStatus)" class="me-2">
                <i :class="['me-1', getStatusIcon(outcome.overallStatus)]"></i>
                {{ getStatusLabel(outcome.overallStatus) }}
              </b-badge>
            </div>
          </div>
          <div class="d-flex align-items-center">
            <b-badge :variant="getPriorityVariant(outcome.priority)" class="me-2">
              {{ outcome.priority.charAt(0).toUpperCase() + outcome.priority.slice(1) }} Priority
            </b-badge>
            <b-button 
              variant="outline-secondary" 
              size="sm" 
              @click="toggleOutcomeExpansion(outcome.outcomeType, outcome.id)"
            >
              <i :class="isExpanded(outcome.outcomeType, outcome.id) ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
            </b-button>
          </div>
        </div>
        
        <h5 class="mb-2">{{ outcome.title }}</h5>
        <p class="text-muted small mb-3">{{ outcome.description }}</p>
        
        <!-- Progress Bar -->
        <div class="mb-3">
          <div class="d-flex justify-content-between small text-muted mb-1">
            <span>Progress: {{ getSubtaskProgress(outcome.subtasks) }} subtasks</span>
            <span>{{ Math.round(getProgressPercentage(outcome.subtasks)) }}% complete</span>
          </div>
          <b-progress :value="getProgressPercentage(outcome.subtasks)" variant="primary" height="8px"></b-progress>
        </div>
        
        <div class="d-flex align-items-center justify-content-between small text-muted">
          <div class="d-flex align-items-center">
            <div class="d-flex align-items-center me-4">
              <i class="fas fa-user me-1"></i>
              {{ outcome.assignedTo }}
            </div>
            <div class="d-flex align-items-center">
              <i class="fas fa-calendar me-1"></i>
              Target: {{ formatDate(outcome.targetDate) }}
            </div>
          </div>
          <span>Started: {{ formatDate(outcome.startDate) }}</span>
        </div>

        <!-- Subtasks (Expandable) -->
        <b-collapse :visible="isExpanded(outcome.outcomeType, outcome.id)">
          <hr>
          <h6 class="mb-3">Subtasks</h6>
          <div class="row g-2">
            <div v-for="subtask in outcome.subtasks" :key="subtask.id" class="col-12">
              <b-card class="border">
                <div class="d-flex align-items-start justify-content-between mb-2">
                  <div class="d-flex align-items-center">
                    <b-badge :variant="getStatusVariant(subtask.status)" class="me-2">
                      <i :class="['me-1', getStatusIcon(subtask.status)]"></i>
                      {{ getStatusLabel(subtask.status) }}
                    </b-badge>
                    <span class="fw-medium">{{ subtask.title }}</span>
                  </div>
                  <span class="small text-muted">
                    Due: {{ formatDate(subtask.dueDate) }}
                  </span>
                </div>
                
                <div class="d-flex align-items-center justify-content-between small text-muted">
                  <div class="d-flex align-items-center">
                    <i class="fas fa-user me-1"></i>
                    {{ subtask.assignedTo }}
                  </div>
                  <span v-if="subtask.completedDate" class="text-success">
                    Completed: {{ formatDate(subtask.completedDate) }}
                  </span>
                </div>
                
                <div v-if="subtask.notes" class="mt-2 small text-muted bg-light rounded p-2">
                  <strong>Notes:</strong> {{ subtask.notes }}
                </div>
              </b-card>
            </div>
          </div>
        </b-collapse>
      </b-card>
    </div>

    <!-- No outcomes found -->
    <b-card v-else class="text-center py-5">
      <i class="fas fa-file-alt fa-3x text-muted mb-3"></i>
      <h5 class="mb-2">No outcomes found</h5>
      <p class="text-muted mb-3">
        No outcomes match your current filters for this asset.
      </p>
      <b-button variant="primary" @click="createNewOutcome">
        Create New Outcome
      </b-button>
    </b-card>
  </div>
</template>

<script setup lang="ts">
import { withDefaults, defineProps, ref, computed, watch, onMounted } from 'vue'
defineOptions({
  name: 'AmLlTasking',
})
import http from '@/lib/http'
import PropertyMap from '@/components/PropertyMap.vue'
import PhotoCarousel from '@/components/PhotoCarousel.vue'
import DocumentsQuickView from '@/components/DocumentsQuickView.vue'
import UiBadge from '@/components/ui/UiBadge.vue'
import { getDelinquencyBadgeTone, getPropertyTypeBadgeTone } from '@/config/badgeTokens'

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
  productId?: string | number | null 
}>(), {
  row: null,
  productId: null,
})

// Reactive state
const currentAssetId = ref<number>(1)
const outcomeFilter = ref<string>('all')
const statusFilter = ref<string>('all')
const expandedOutcomes = ref<Set<string>>(new Set(['foreclosure1', 'modification2']))

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

// Resolve AM asset id to hit backend endpoints
const amId = computed<number | null>(() => {
  if (props.productId != null && props.productId !== '') return Number(props.productId)
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
  }
})

const assetOutcomes = computed<Outcome[]>(() => {
  return outcomes.value.filter((outcome: Outcome) => outcome.assetId === currentAssetId.value)
})

const filteredOutcomes = computed(() => {
  return assetOutcomes.value.filter(outcome => {
    const matchesOutcomeType = outcomeFilter.value === 'all' || outcome.outcomeType === outcomeFilter.value
    const matchesStatus = statusFilter.value === 'all' || outcome.overallStatus === statusFilter.value
    return matchesOutcomeType && matchesStatus
  })
})

const outcomeStats = computed(() => {
  return {
    pending: assetOutcomes.value.filter(o => o.overallStatus === 'pending').length,
    in_progress: assetOutcomes.value.filter(o => o.overallStatus === 'in_progress').length,
    completed: assetOutcomes.value.filter(o => o.overallStatus === 'completed').length
  }
})

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

const normalizeNumeric = (value: unknown): number | null => {
  if (value == null) return null
  if (typeof value === 'number' && Number.isFinite(value)) return value
  if (typeof value === 'string') {
    const parsed = Number.parseFloat(value)
    return Number.isFinite(parsed) ? parsed : null
  }
  return null
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}

const getSubtaskProgress = (subtasks: Subtask[]) => {
  const completed = subtasks.filter(s => s.status === 'completed').length
  return `${completed}/${subtasks.length}`
}

const getProgressPercentage = (subtasks: Subtask[]) => {
  const completed = subtasks.filter(s => s.status === 'completed').length
  return (completed / subtasks.length) * 100
}

// Methods
const navigateAsset = (direction: 'prev' | 'next') => {
  const currentIndex = assets.value.findIndex(asset => asset.id === currentAssetId.value)
  let newIndex: number
  
  if (direction === 'prev') {
    newIndex = currentIndex > 0 ? currentIndex - 1 : assets.value.length - 1
  } else {
    newIndex = currentIndex < assets.value.length - 1 ? currentIndex + 1 : 0
  }
  
  currentAssetId.value = assets.value[newIndex].id
}

const toggleOutcomeExpansion = (outcomeType: string, outcomeId: number) => {
  const key = outcomeType + outcomeId
  const newExpanded = new Set(expandedOutcomes.value)
  if (newExpanded.has(key)) {
    newExpanded.delete(key)
  } else {
    newExpanded.add(key)
  }
  expandedOutcomes.value = newExpanded
}

const isExpanded = (outcomeType: string, outcomeId: number) => {
  return expandedOutcomes.value.has(outcomeType + outcomeId)
}

const createNewOutcome = () => {
  // TODO: Implement create new outcome modal/form
  console.log('Create new outcome for asset:', currentAssetId.value)
}

// Style helper functions
const getOutcomeTypeLabel = (type: string) => {
  const types: Record<string, string> = {
    foreclosure: 'Foreclosure',
    modification: 'Modification',
    deed_in_lieu: 'Deed in Lieu',
    short_sale: 'Short Sale'
  }
  return types[type] || 'Unknown'
}

const getOutcomeTypeVariant = (type: string) => {
  const variants: Record<string, any> = {
    foreclosure: 'danger',
    modification: 'primary',
    deed_in_lieu: 'success',
    short_sale: 'warning'
  }
  return variants[type] || 'secondary'
}

const getOutcomeIcon = (type: string) => {
  const icons: Record<string, string> = {
    foreclosure: 'fas fa-home text-danger',
    modification: 'fas fa-file-contract text-primary',
    deed_in_lieu: 'fas fa-handshake text-success',
    short_sale: 'fas fa-dollar-sign text-warning'
  }
  return icons[type] || 'fas fa-question text-secondary'
}

const getStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    pending: 'Pending',
    in_progress: 'In Progress',
    completed: 'Completed'
  }
  return labels[status] || 'Unknown'
}

const getStatusVariant = (status: string) => {
  const variants: Record<string, any> = {
    pending: 'warning',
    in_progress: 'primary',
    completed: 'success'
  }
  return variants[status] || 'secondary'
}

const getStatusIcon = (status: string) => {
  const icons: Record<string, string> = {
    pending: 'fas fa-clock',
    in_progress: 'fas fa-spinner',
    completed: 'fas fa-check-circle'
  }
  return icons[status] || 'fas fa-question'
}

const getPriorityVariant = (priority: string) => {
  const variants: Record<string, any> = {
    high: 'danger',
    medium: 'warning',
    low: 'secondary'
  }
  return variants[priority] || 'secondary'
}

const getPriorityBorderClass = (priority: string) => {
  const classes: Record<string, string> = {
    high: 'border-danger',
    medium: 'border-warning',
    low: 'border-secondary'
  }
  return classes[priority] || 'border-secondary'
}

// Initialize with current asset if available
onMounted(() => {
  if (amId.value) {
    currentAssetId.value = amId.value
  }
})
</script>

<style scoped>
/* Custom styles for the Asset Management Tasking component */
.am-tasking-wrapper {
  /* Full-width wrapper so cards align with the surrounding layout */
  width: 100%;
  /* Remove duplicate horizontal padding because parent container already applies spacing */
  padding: 0;
}

.border-start {
  border-left-width: 4px !important;
}

.bg-light {
  background-color: #f8f9fa !important;
}

.text-warning {
  color: #ffc107 !important;
}

.text-primary {
  color: #0d6efd !important;
}

.text-success {
  color: #198754 !important;
}

.text-danger {
  color: #dc3545 !important;
}

.border-danger {
  border-color: #dc3545 !important;
}

.border-warning {
  border-color: #ffc107 !important;
}

.border-secondary {
  border-color: #6c757d !important;
}
</style>
