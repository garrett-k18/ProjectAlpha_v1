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
            <div class="kpi-badges d-flex gap-2 align-items-center">
              <template v-if="activeTypes.length">
                <span
                  v-for="t in activeTypes"
                  :key="t"
                  class="badge rounded-pill"
                  :class="trackBadge(t).cls"
                >
                  {{ trackBadge(t).label }}
                </span>
              </template>
              <span v-else class="text-muted">None</span>
            </div>
          </div>
        </b-col>
      </b-row>
    </b-card>

    <!-- Outcome Summary Cards (moved above Track) -->
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

    <!-- Track: Start/ensure outcomes and render cards -->
    <b-row class="g-3 align-items-stretch mb-4">
      <b-col cols="12">
        <b-card class="w-100">
          <template #header>
            <div class="d-flex align-items-center justify-content-between w-100">
              <h5 class="mb-0 d-flex align-items-center">
                <i class="fas fa-stream me-2"></i>
                Current Track(s)
              </h5>
              <div class="position-relative" ref="trackMenuRef">
                <button type="button" class="btn btn-sm btn-outline-primary px-3 d-inline-flex align-items-center justify-content-center position-relative" :disabled="!hubId || ensureBusy" @click.stop="toggleTrackMenu">
                  <span class="w-100 text-center">Choose Track</span>
                  <i class="fas fa-chevron-down small position-absolute end-0 me-2 top-50 translate-middle-y" aria-hidden="true"></i>
                </button>
                <!-- Custom dropdown menu with pill badges -->
                <div v-if="showTrackMenu" class="card shadow-sm mt-1" style="position: absolute; right: 0; min-width: 680px; z-index: 1060;" @click.stop>
                  <div class="card-body py-2">
                    <div class="d-flex flex-row flex-nowrap align-items-center justify-content-center gap-2 text-center">
                      <button class="btn p-0 bg-transparent border-0" @click="selectTrack('modification')" :disabled="ensureBusy">
                        <span class="badge rounded-pill text-bg-secondary px-3 py-2">Modification</span>
                      </button>
                      <button class="btn p-0 bg-transparent border-0" @click="selectTrack('short_sale')" :disabled="ensureBusy">
                        <span class="badge rounded-pill text-bg-warning px-3 py-2">Short Sale</span>
                      </button>
                      <button class="btn p-0 bg-transparent border-0" @click="selectTrack('dil')" :disabled="ensureBusy">
                        <span class="badge rounded-pill text-bg-primary px-3 py-2">Deed-in-Lieu</span>
                      </button>
                      <button class="btn p-0 bg-transparent border-0" @click="selectTrack('fc')" :disabled="ensureBusy">
                        <span class="badge rounded-pill text-bg-danger px-3 py-2">Foreclosure</span>
                      </button>
                      <button class="btn p-0 bg-transparent border-0" @click="selectTrack('reo')" :disabled="ensureBusy">
                        <span class="badge rounded-pill text-bg-info px-3 py-2">REO</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </template>

          <div class="row g-3">
            <div class="col-12 col-lg-6" v-if="visibleOutcomes.dil">
              <DilCard :hubId="hubId!" @delete="() => requestDelete('dil')" />
            </div>
            <div class="col-12 col-lg-6" v-if="visibleOutcomes.fc">
              <FcCard :hubId="hubId!" @delete="() => requestDelete('fc')" />
            </div>
            <div class="col-12 col-lg-6" v-if="visibleOutcomes.reo">
              <ReoCard :hubId="hubId!" @delete="() => requestDelete('reo')" />
            </div>
            <div class="col-12 col-lg-6" v-if="visibleOutcomes.short_sale">
              <ShortSaleCard :hubId="hubId!" @delete="() => requestDelete('short_sale')" />
            </div>
            <div class="col-12 col-lg-6" v-if="visibleOutcomes.modification">
              <ModificationCard :hubId="hubId!" @delete="() => requestDelete('modification')" />
            </div>
            <div v-if="!anyVisibleOutcome" class="col-12 small text-muted">
              Pick a track above to create its card for this asset.
            </div>
          </div>
        </b-card>
      </b-col>
    </b-row>

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

    
    <!-- Filters and legacy outcome list removed -->
  </div>
</template>

<script setup lang="ts">
import { withDefaults, defineProps, ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
defineOptions({
  name: 'AmLlTasking',
})
// (legacy imports removed)
import UiBadge from '@/components/ui/UiBadge.vue'
import { getDelinquencyBadgeTone, getPropertyTypeBadgeTone } from '@/config/badgeTokens'
// Outcome cards + store
import DilCard from '@/views/am_module/outcomes/DilCard.vue'
import FcCard from '@/views/am_module/outcomes/FcCard.vue'
import ReoCard from '@/views/am_module/outcomes/ReoCard.vue'
import ShortSaleCard from '@/views/am_module/outcomes/ShortSaleCard.vue'
import ModificationCard from '@/views/am_module/outcomes/ModificationCard.vue'
import { useAmOutcomesStore, type OutcomeType } from '@/stores/outcomes'

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
const visibleOutcomes = ref<Record<OutcomeType, boolean>>({ dil: false, fc: false, reo: false, short_sale: false, modification: false })
const anyVisibleOutcome = computed(() => Object.values(visibleOutcomes.value).some(Boolean))

// Resolve hub id from the incoming row props
const hubId = computed<number | null>(() => {
  const raw = (props.row as any)?.asset_hub_id
  return raw != null ? Number(raw) : null
})

// Active outcome types for KPI header badges
const activeTypes = computed<OutcomeType[]>(() => {
  return (Object.keys(visibleOutcomes.value) as OutcomeType[]).filter(
    (k) => visibleOutcomes.value[k]
  )
})

function trackBadge(t: OutcomeType): { label: string; cls: string } {
  switch (t) {
    case 'modification':
      return { label: 'Modification', cls: 'text-bg-secondary' }
    case 'short_sale':
      return { label: 'Short Sale', cls: 'text-bg-warning' }
    case 'dil':
      return { label: 'Deed-in-Lieu', cls: 'text-bg-primary' }
    case 'fc':
      return { label: 'Foreclosure', cls: 'text-bg-danger' }
    case 'reo':
      return { label: 'REO', cls: 'text-bg-info' }
    default:
      return { label: t, cls: 'text-bg-secondary' }
  }
}

function toggleTrackMenu() {
  showTrackMenu.value = !showTrackMenu.value
}
async function selectTrack(type: OutcomeType) {
  if (!hubId.value) return
  try {
    ensureBusy.value = true
    selectedOutcome.value = type
    await outcomesStore.ensureOutcome(hubId.value, type)
    visibleOutcomes.value[type] = true
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
onMounted(() => document.addEventListener('click', handleTrackOutside))
onBeforeUnmount(() => document.removeEventListener('click', handleTrackOutside))

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
    await outcomesStore.deleteOutcome(hubId.value, confirm.value.type)
    visibleOutcomes.value[confirm.value.type] = false
    closeConfirm()
  } finally {
    confirm.value.busy = false
  }
}

// Hydrate visible cards when hub changes
async function refreshVisible() {
  visibleOutcomes.value = { dil: false, fc: false, reo: false, short_sale: false, modification: false }
  const id = hubId.value
  if (!id) return
  const types: OutcomeType[] = ['dil', 'fc', 'reo', 'short_sale', 'modification']
  for (const t of types) {
    const exists = await outcomesStore.fetchOutcome(id, t)
    if (exists) visibleOutcomes.value[t] = true
  }
}
onMounted(refreshVisible)
watch(hubId, refreshVisible)

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
// (legacy helper functions removed)

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

/* Keep KPI card height stable when showing multiple active outcome pills */
.kpi-badges {
  flex-wrap: nowrap;
  overflow: hidden;           /* prevent growing the card */
  text-overflow: ellipsis;    /* gracefully truncate if too many */
  white-space: nowrap;        /* keep on one line */
  min-height: 1.5rem;         /* stable line box */
}
.kpi-badges .badge {
  padding: 0.15rem 0.5rem;    /* smaller pill without changing font size */
  line-height: 1;             /* compact height */
  font-weight: 500;           /* readable weight */
}
</style>
