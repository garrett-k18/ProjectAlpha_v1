<template>
  <!--
    Asset Management Quickview card rendered on the Snapshot tab.
    WHAT: Shows a compact summary of AM tasking state (tracks + latest tasks)
    WHY: Gives AM users a heads-up before diving into the full Tasking tab
    HOW: Pulls data from the shared Pinia outcomes store using the asset hub id
  -->
  <div class="card h-100 w-100">
    <!-- Header matches Hyper UI card conventions for consistency -->
    <div class="card-header d-flex align-items-center justify-content-between">
      <h4 class="header-title mb-0">Asset Management Quickview</h4>
      <!-- Future enhancement: link into full AM Tasking view -->
    </div>

    <div class="card-body">
      <!-- Guard: the snapshot row might be missing a hub id until the modal loads -->
      <div v-if="!hasHubId" class="text-muted small">
        Select an asset to load tasking context.
      </div>

      <!-- Loading indicator follows Bootstrap spinner guidance -->
      <div v-else-if="isLoading" class="d-flex align-items-center gap-2 text-muted small">
        <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
        Loading asset management data...
      </div>

      <!-- Display backend or fetch errors without breaking the snapshot page -->
      <div v-else-if="loadError" class="alert alert-warning py-2 px-3 small mb-0">
        {{ loadError }}
      </div>

      <!-- Main quickview content once data is ready - Track sub-cards layout -->
      <div v-else class="d-flex flex-column gap-3">
        <!-- Show each active track as a sub-card with clearer hierarchy -->
        <div v-if="trackSummaries.length" class="d-flex flex-column gap-3">
          <div
            v-for="summary in trackSummaries"
            :key="summary.key"
            class="card mb-0 shadow-sm border"
          >
            <!-- Track Header -->
            <div class="card-header bg-light py-2 px-3 d-flex align-items-center justify-content-between">
              <div class="d-flex align-items-center gap-2">
                <UiBadge :tone="summary.tone" size="sm" :label="summary.title" />
              </div>
            </div>
            
            <!-- Track Body -->
            <div class="card-body p-3">
              <!-- Latest task details -->
              <div v-if="getLatestTaskForTrack(summary.key)" class="d-flex align-items-start gap-2">
                <i class="ri-time-line text-primary mt-1"></i>
                <div class="flex-fill">
                  <div class="small">
                    <span class="fw-semibold">{{ getLatestTaskForTrack(summary.key) }}</span>
                  </div>
                </div>
              </div>
              
              <!-- No tasks message -->
              <div v-else class="text-muted small fst-italic">
                No recent activity
              </div>
            </div>
          </div>
        </div>

        <!-- Empty state when no tracks exist -->
        <div v-else class="text-center text-muted py-4">
          <i class="ri-inbox-line fs-2 d-block mb-2 opacity-50"></i>
          <p class="mb-0">No active tracks or tasks</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import UiBadge from '@/components/ui/UiBadge.vue'
import { useAmOutcomesStore, type OutcomeType, type DilTask, type FcTask, type ReoTask, type ShortSaleTask, type ModificationTask, type NoteSaleTask, type PerformingTask, type DelinquentTask } from '@/stores/outcomes'
import type { BadgeToneKey } from '@/GlobalStandardizations/badges'

/**
 * WHAT: Strict list of outcome types we support in AM tasking.
 * WHY: Drives loops so each type gets consistent fetch + presentation logic.
 * HOW: Matches the OutcomeType union exported by the Pinia store.
 */
const outcomeTypes: OutcomeType[] = ['dil', 'fc', 'reo', 'short_sale', 'modification', 'note_sale', 'performing', 'delinquent']

/**
 * WHAT: Typed union for the various task payloads returned by the backend.
 * WHY: Allows us to store tasks in a single map without losing TS safety.
 * HOW: Union of each task interface defined in `@/stores/outcomes`.
 */
type OutcomeTask = DilTask | FcTask | ReoTask | ShortSaleTask | ModificationTask | NoteSaleTask | PerformingTask | DelinquentTask

/**
 * WHAT: Quickview props passed by the Snapshot tab parent.
 * WHY: Provides the asset row payload plus resolved hub id for lookups.
 * HOW: Both props are optional to keep component reusable in other contexts.
 */
const props = defineProps<{
  row?: Record<string, any> | null
  assetHubId?: string | number | null
}>()

/**
 * WHAT: Shared Pinia outcomes store for fetching tasking data.
 * WHY: Reuses existing ensure/list endpoints used by the Tasking tab.
 * HOW: Store docs: https://pinia.vuejs.org/core-concepts/
 */
const outcomesStore = useAmOutcomesStore()

/**
 * WHAT: Reactive map of outcome presence keyed by outcome type.
 * WHY: Drives "Active Tracks" badges and decides which task lists to fetch.
 * HOW: Updated after each API roundtrip in `loadQuickview`.
 */
const activeOutcomeMap = ref<Record<OutcomeType, boolean>>({
  dil: false,
  fc: false,
  reo: false,
  short_sale: false,
  modification: false,
  note_sale: false,
  performing: false,
  delinquent: false,
})

/**
 * WHAT: Reactive map of task lists per outcome type.
 * WHY: Allows quick aggregation for counts and latest updates in computed blocks.
 * HOW: Populated by `fetchTasksForType` inside `loadQuickview`.
 */
const tasksByType = ref<Record<OutcomeType, OutcomeTask[]>>({
  dil: [],
  fc: [],
  reo: [],
  short_sale: [],
  modification: [],
  note_sale: [],
  performing: [],
  delinquent: [],
})

/**
 * WHAT: Loading flag toggled while we query Pinia/store endpoints.
 * WHY: Drives the spinner to avoid jarring empty state flicker.
 * HOW: Set inside `loadQuickview` following Vue docs on reactive refs (https://vuejs.org/guide/essentials/reactivity-fundamentals.html).
 */
const isLoading = ref<boolean>(false)

/**
 * WHAT: Human-readable error message for fetch failures.
 * WHY: Snapshot tab should show a warning instead of breaking the modal.
 * HOW: Updated within `loadQuickview` catch blocks.
 */
const loadError = ref<string | null>(null)

/**
 * WHAT: Computed hub id resolved from props.row or assetHubId prop.
 * WHY: Snapshot rows sometimes provide ids as strings; we normalize to number.
 * HOW: Prefers explicit prop, then row.asset_hub_id, then row.id.
 */
const normalizedHubId = computed<number | null>(() => {
  const explicit = props.assetHubId
  const fromRow = props.row && (props.row as any).asset_hub_id
  const fallbackId = props.row && (props.row as any).id
  const candidate = explicit ?? fromRow ?? fallbackId
  const numeric = candidate != null ? Number(candidate) : NaN
  return Number.isFinite(numeric) ? numeric : null
})

/**
 * WHAT: Boolean flag indicating whether we have a valid hub id to query with.
 * WHY: Controls initial empty state messaging in the template.
 * HOW: True when normalizedHubId returns a concrete number.
 */
const hasHubId = computed<boolean>(() => normalizedHubId.value != null)

/**
 * WHAT: Mapping from outcome type to user-facing badge label.
 * WHY: Keeps label text consistent between Tasking tab and Quickview snapshot.
 * HOW: Mirrors helper in `am_tasking/index_amLLTasking.vue` to stay in sync.
 */
function trackLabel(type: OutcomeType): string {
  switch (type) {
    case 'modification':
      return 'Modification'
    case 'short_sale':
      return 'Short Sale'
    case 'dil':
      return 'Deed-in-Lieu'
    case 'fc':
      return 'Foreclosure'
    case 'reo':
      return 'REO'
    case 'note_sale':
      return 'Note Sale'
    case 'performing':
      return 'Performing'
    case 'delinquent':
      return 'Delinquent'
    default:
      return type
  }
}

/**
 * WHAT: Mapping from outcome type to badge tone key.
 * WHY: Reuses the color palette established across AM tasking surfaces.
 * HOW: Color choices mirror those configured in Tasking’s track menu.
 */
function trackTone(type: OutcomeType): BadgeToneKey {
  switch (type) {
    case 'modification':
      return 'secondary'
    case 'short_sale':
      return 'warning'
    case 'dil':
      return 'primary'
    case 'fc':
      return 'danger'
    case 'reo':
      return 'info'
    case 'note_sale':
      return 'secondary'
    case 'performing':
      return 'success'
    case 'delinquent':
      return 'warning'
    default:
      return 'secondary'
  }
}

/**
 * WHAT: Helper to derive a concise task label per outcome type.
 * WHY: Converts backend `task_type` codes into user-friendly copy.
 * HOW: Mirrors label maps used by outcome cards in AM tasking.
 */
function taskLabelFor(type: OutcomeType, rawTask: OutcomeTask): string {
  switch (type) {
    case 'fc': {
      const map: Record<string, string> = {
        nod_noi: 'NOD/NOI',
        fc_filing: 'FC Filing',
        mediation: 'Mediation',
        judgement: 'Judgement',
        redemption: 'Redemption',
        sale_scheduled: 'Sale Scheduled',
        sold: 'Sold',
      }
      return map[(rawTask as FcTask).task_type] ?? (rawTask as FcTask).task_type
    }
    case 'reo': {
      const map: Record<string, string> = {
        eviction: 'Eviction',
        trashout: 'Trashout',
        renovation: 'Renovation',
        pre_marketing: 'Pre-Marketing',
        listed: 'Listed',
        under_contract: 'Under Contract',
        sold: 'Sold',
      }
      return map[(rawTask as ReoTask).task_type] ?? (rawTask as ReoTask).task_type
    }
    case 'short_sale': {
      const map: Record<string, string> = {
        list_price_accepted: 'List Price Accepted',
        listed: 'Listed',
        under_contract: 'Under Contract',
        sold: 'Sold',
      }
      return map[(rawTask as ShortSaleTask).task_type] ?? (rawTask as ShortSaleTask).task_type
    }
    case 'dil': {
      const map: Record<string, string> = {
        owner_contacted: 'Borrowers Contacted',
        no_cooperation: 'No Cooperation',
        dil_drafted: 'DIL Drafted',
        dil_successful: 'DIL Executed',
      }
      return map[(rawTask as DilTask).task_type] ?? (rawTask as DilTask).task_type
    }
    case 'modification': {
      const map: Record<string, string> = {
        mod_negotiations: 'Negotiations',
        mod_accepted: 'Accepted',
        mod_started: 'Started',
        mod_failed: 'Failed',
      }
      return map[(rawTask as ModificationTask).task_type] ?? (rawTask as ModificationTask).task_type
    }
    default:
      return rawTask.task_type ?? 'Task'
  }
}

/**
 * WHAT: Helper mapping outcome tasks to Hyper UI badge tones.
 * WHY: Provides quick visual cues for task urgency/status.
 * HOW: Uses the same tone selections as AM tasking outcome cards.
 */
function taskToneFor(type: OutcomeType, rawTask: OutcomeTask): BadgeToneKey {
  switch (type) {
    case 'fc': {
      const map: Record<string, BadgeToneKey> = {
        nod_noi: 'warning',
        fc_filing: 'primary',
        mediation: 'info',
        judgement: 'secondary',
        redemption: 'success',
        sale_scheduled: 'dark',
        sold: 'danger',
      }
      return map[(rawTask as FcTask).task_type] ?? 'secondary'
    }
    case 'reo': {
      const map: Record<string, BadgeToneKey> = {
        eviction: 'danger',
        trashout: 'warning',
        renovation: 'info',
        pre_marketing: 'primary',
        listed: 'primary',
        under_contract: 'success',
        sold: 'secondary',
      }
      return map[(rawTask as ReoTask).task_type] ?? 'secondary'
    }
    case 'short_sale': {
      const map: Record<string, BadgeToneKey> = {
        list_price_accepted: 'warning',
        listed: 'info',
        under_contract: 'primary',
        sold: 'success',
      }
      return map[(rawTask as ShortSaleTask).task_type] ?? 'secondary'
    }
    case 'dil': {
      const map: Record<string, BadgeToneKey> = {
        owner_contacted: 'primary',
        no_cooperation: 'secondary',
        dil_drafted: 'warning',
        dil_successful: 'success',
      }
      return map[(rawTask as DilTask).task_type] ?? 'secondary'
    }
    case 'modification': {
      const map: Record<string, BadgeToneKey> = {
        mod_negotiations: 'info',
        mod_accepted: 'success',
        mod_started: 'primary',
        mod_failed: 'danger',
      }
      return map[(rawTask as ModificationTask).task_type] ?? 'secondary'
    }
    default:
      return 'secondary'
  }
}

/**
 * WHAT: Format helper for timestamps so Snapshot cards stay compact.
 * WHY: Backend returns ISO strings; we present locale date per product guidance.
 * HOW: Uses Intl.DateTimeFormat per MDN docs (https://developer.mozilla.org/docs/Web/JavaScript/Reference/Global_Objects/Intl/DateTimeFormat).
 */
function formatTimestamp(value: string | null | undefined): string {
  if (!value) return 'Date pending'
  const parsed = Date.parse(value)
  if (Number.isNaN(parsed)) return 'Date pending'
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(new Date(parsed))
}

/**
 * WHAT: Reset helper that clears reactive maps when hub id disappears.
 * WHY: Prevents stale data from previous asset lingering in the UI.
 * HOW: Resets outcome and task maps and clears status flags.
 */
function resetQuickviewState(): void {
  activeOutcomeMap.value = {
    dil: false,
    fc: false,
    reo: false,
    short_sale: false,
    modification: false,
    note_sale: false,
    performing: false,
    delinquent: false,
  }
  tasksByType.value = {
    dil: [],
    fc: [],
    reo: [],
    short_sale: [],
    modification: [],
    note_sale: [],
    performing: [],
    delinquent: [],
  }
  loadError.value = null
}

/**
 * WHAT: Fetch tasks for a specific outcome type.
 * WHY: Centralizes the switch logic so `loadQuickview` stays readable.
 * HOW: Calls the corresponding list helper from the Pinia store with force=true to refresh caches.
 */
async function fetchTasksForType(hubId: number, type: OutcomeType): Promise<OutcomeTask[]> {
  switch (type) {
    case 'dil':
      return await outcomesStore.listDilTasks(hubId, true)
    case 'fc':
      return await outcomesStore.listFcTasks(hubId, true)
    case 'reo':
      return await outcomesStore.listReoTasks(hubId, true)
    case 'short_sale':
      return await outcomesStore.listShortSaleTasks(hubId, true)
    case 'modification':
      return await outcomesStore.listModificationTasks(hubId, true)
    case 'note_sale':
      return await outcomesStore.listNoteSaleTasks(hubId, true)
    case 'performing':
      return await outcomesStore.listPerformingTasks(hubId, true)
    case 'delinquent':
      return await outcomesStore.listDelinquentTasks(hubId, true)
    default:
      return []
  }
}

/**
 * WHAT: Core loader that fetches active outcomes + tasks for the selected asset hub.
 * WHY: Powers all quickview sections.
 * HOW: Sequentially queries outcomes, then tasks, handling per-type errors gracefully.
 */
async function loadQuickview(): Promise<void> {
  const hubId = normalizedHubId.value
  if (!hubId) {
    resetQuickviewState()
    return
  }

  isLoading.value = true
  loadError.value = null
  resetQuickviewState()

  try {
    for (const type of outcomeTypes) {
      try {
        const outcome = await outcomesStore.fetchOutcome(hubId, type)
        const isActive = !!outcome
        activeOutcomeMap.value[type] = isActive
        tasksByType.value[type] = isActive ? await fetchTasksForType(hubId, type) : []
      } catch (innerError: any) {
        // Capture per-type issues while letting other types continue loading.
        loadError.value = innerError?.response?.data?.detail || innerError?.message || 'Failed to load one or more tracks.'
      }
    }
  } finally {
    isLoading.value = false
  }
}

/**
 * WHAT: Computed list of badge descriptors for currently active tracks.
 * WHY: Keeps template markup simple and expressive.
 * HOW: Filters outcomeTypes using activeOutcomeMap.
 */
const activeTrackBadges = computed(() => {
  return outcomeTypes
    .filter((type) => activeOutcomeMap.value[type])
    .map((type) => ({
      key: `track-${type}`,
      label: trackLabel(type),
      tone: trackTone(type),
    }))
})

/**
 * WHAT: Count of active tracks for display in badge summary.
 * WHY: Offers a quick at-a-glance number next to the section title.
 * HOW: Derived from activeTrackBadges length.
 */
const activeTracksCount = computed(() => activeTrackBadges.value.length)

/**
 * WHAT: Aggregated task summaries per outcome type.
 * WHY: Drives the "Task Totals" section with consistent formatting.
 * HOW: Builds an array of descriptor objects for template iteration.
 */
const trackSummaries = computed(() => {
  return outcomeTypes
    .filter((type) => activeOutcomeMap.value[type])
    .map((type) => {
      const tasks = tasksByType.value[type] ?? []
      return {
        key: `summary-${type}`,
        title: trackLabel(type),
        subtitle: tasks.length ? `${tasks.length} recorded task${tasks.length === 1 ? '' : 's'}` : 'No tasks recorded',
        countLabel: tasks.length ? `${tasks.length}` : '0',
        tone: trackTone(type),
      }
    })
})

/**
 * WHAT: Total task count across all active outcomes.
 * WHY: Displayed in the section header badge.
 * HOW: Sum the lengths from `trackSummaries` data.
 */
const totalTaskCount = computed(() => trackSummaries.value.reduce((sum, summary) => sum + Number(summary.countLabel), 0))

/**
 * WHAT: Helper function to get the latest task description for a given track.
 * WHY: Shows the most recent activity for each track inline within the track card.
 * HOW: Extracts the outcome type from the summary key, finds the latest task by created_at timestamp.
 * @param summaryKey - The key from trackSummaries (format: "summary-{type}")
 * @returns Formatted string with task label and timestamp, or null if no tasks exist.
 */
function getLatestTaskForTrack(summaryKey: string): string | null {
  // Extract outcome type from the summary key (e.g., "summary-dil" -> "dil")
  const type = summaryKey.replace('summary-', '') as OutcomeType
  const tasks = tasksByType.value[type] ?? []
  
  if (!tasks.length) return null
  
  // Sort tasks by created_at timestamp (most recent first)
  const sorted = [...tasks].sort((a, b) => {
    const aTime = a.created_at ? Date.parse(a.created_at) : 0
    const bTime = b.created_at ? Date.parse(b.created_at) : 0
    return bTime - aTime
  })
  
  const latest = sorted[0]
  const label = taskLabelFor(type, latest)
  const timestamp = formatTimestamp(latest.created_at ?? latest.updated_at ?? null)
  
  return `Latest: ${label} (${timestamp})`
}

/**
 * WHAT: Watcher to reload quickview whenever the selected hub id changes.
 * WHY: Snapshot modal can switch assets without remounting the component.
 * HOW: Vue watch API per docs (https://vuejs.org/api/reactivity-core.html#watch).
 */
watch(normalizedHubId, () => {
  loadQuickview()
})

/**
 * WHAT: Initial load when the component mounts.
 * WHY: Ensures data fetch runs on first render.
 * HOW: Vue lifecycle hook per docs (https://vuejs.org/api/composition-api-lifecycle.html#onmounted).
 */
onMounted(() => {
  loadQuickview()
})
</script>
