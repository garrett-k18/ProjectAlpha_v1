<template>
  <!--
    WHAT
    - A small card that lists upcoming deadlines (due dates) across outcomes/tasks.

    WHY
    - Gives a quick glance at what's due soon without opening each card.

    WHERE
    - AM Tasking (loan-level) page, typically near KPIs or Recent Activity.

    HOW
    - Pass an array of DeadlineItem via the `items` prop.
    - Each item shows a label, a due date (compact), and an optional tone badge.
  -->
  <div class="card h-100">
    <div class="card-header d-flex align-items-center justify-content-between">
      <h4 class="header-title mb-0">Milestones</h4>
      <i class="mdi mdi-calendar-clock text-muted"></i>
    </div>
    <div class="card-body py-2">
      <div v-if="!items || items.length === 0" class="text-muted small">No upcoming milestones.</div>
      <ul v-else class="list-group list-group-flush small">
        <li v-for="it in items" :key="it.id" class="list-group-item d-flex align-items-center justify-content-between px-0 py-2">
          <div class="d-flex flex-column">
            <span class="fw-bold">{{ it.label }}</span>
            <span class="text-muted">Due: {{ fmtDate(it.dueDate) }}</span>
          </div>
          <span v-if="it.tone" :class="badgeClass(it.tone)">{{ toneLabel(it.tone) }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
// WHAT: Milestones card - self-contained component for AM Tasking
// WHY: Display upcoming deadlines/milestones for the asset
// WHERE: AM Tasking page, activity widgets row
// HOW: Accepts hubId prop, fetches and displays milestone data
import { ref, onMounted, watch } from 'vue'

export type DeadlineTone = 'danger' | 'warning' | 'info' | 'secondary'
export interface DeadlineItem {
  id: number
  label: string
  dueDate: string // ISO or display string; we format compactly
  tone?: DeadlineTone
}

const props = defineProps<{
  hubId: number
}>()

// WHAT: Milestone items for this asset
// WHY: Store fetched deadline data
// WHERE: Populated by loadMilestones()
const items = ref<DeadlineItem[]>([])

// WHAT: Load milestones for this asset hub
// WHY: Fetch deadline data from backend (currently demo data)
// HOW: Replace with API call when backend endpoint is ready
async function loadMilestones() {
  // TODO: Replace with actual API call
  // const response = await http.get(`/api/am/milestones/?asset_hub_id=${props.hubId}`)
  // items.value = response.data
  
  // Demo data for now
  items.value = [
    { id: 101, label: 'DIL: Borrower Signature', dueDate: new Date(Date.now() + 3*24*3600*1000).toISOString(), tone: 'warning' },
    { id: 102, label: 'FC: Mediation Hearing', dueDate: new Date(Date.now() + 5*24*3600*1000).toISOString(), tone: 'danger' },
  ]
}

// WHAT: Load milestones on mount and when hubId changes
// WHY: Keep data fresh when navigating between assets
watch(() => props.hubId, () => {
  if (props.hubId) loadMilestones()
}, { immediate: true })

// WHAT: Helper functions for formatting and styling
// WHY: Format dates and style badges consistently
function fmtDate(iso: string): string {
  try {
    const d = new Date(iso)
    return d.toLocaleDateString(undefined, { year: '2-digit', month: 'numeric', day: 'numeric' })
  } catch { return iso }
}

function badgeClass(tone?: DeadlineTone): string {
  if (!tone) return 'badge bg-secondary-subtle text-secondary'
  const map: Record<DeadlineTone, string> = {
    danger: 'badge bg-danger-subtle text-danger',
    warning: 'badge bg-warning-subtle text-warning',
    info: 'badge bg-info-subtle text-info',
    secondary: 'badge bg-secondary-subtle text-secondary',
  }
  return map[tone] ?? map.secondary
}

function toneLabel(tone?: DeadlineTone): string {
  const map: Record<DeadlineTone, string> = {
    danger: 'Urgent',
    warning: 'Soon',
    info: 'Info',
    secondary: 'Other',
  }
  return tone ? map[tone] : 'Other'
}
</script>

<style scoped>
/* Keep styling minimal; leverage Bootstrap/Hyper UI */
</style>
