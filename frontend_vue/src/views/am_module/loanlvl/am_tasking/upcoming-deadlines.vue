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
      <h4 class="header-title mb-0">{{ title }}</h4>
      <i class="mdi mdi-calendar-clock text-muted"></i>
    </div>
    <div class="card-body py-2">
      <div v-if="!items || items.length === 0" class="text-muted small">No upcoming deadlines.</div>
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

<script lang="ts">
// WHAT: Upcoming deadlines list UI for AM Tasking.
// WHY: Make urgent dates visible and scannable.
// WHERE: Feature-local component under am_tasking.
// HOW: Import and pass `items` with id/label/dueDate/tone.
import type { PropType } from 'vue'

export type DeadlineTone = 'danger' | 'warning' | 'info' | 'secondary'
export interface DeadlineItem {
  id: number
  label: string
  dueDate: string // ISO or display string; we format compactly
  tone?: DeadlineTone
}

export default {
  name: 'UpcomingDeadlines',
  props: {
    title: { type: String, default: 'Upcoming Deadlines' },
    items: { type: Array as PropType<DeadlineItem[]>, default: () => [] },
  },
  methods: {
    fmtDate(iso: string): string {
      try {
        const d = new Date(iso)
        return d.toLocaleDateString(undefined, { year: '2-digit', month: 'numeric', day: 'numeric' })
      } catch { return iso }
    },
    badgeClass(tone?: DeadlineTone): string {
      if (!tone) return 'badge bg-secondary-subtle text-secondary'
      const map: Record<DeadlineTone, string> = {
        danger: 'badge bg-danger-subtle text-danger',
        warning: 'badge bg-warning-subtle text-warning',
        info: 'badge bg-info-subtle text-info',
        secondary: 'badge bg-secondary-subtle text-secondary',
      }
      return map[tone] ?? map.secondary
    },
    toneLabel(tone?: DeadlineTone): string {
      const map: Record<DeadlineTone, string> = {
        danger: 'Urgent',
        warning: 'Soon',
        info: 'Info',
        secondary: 'Other',
      }
      return tone ? map[tone] : 'Other'
    },
  },
}
</script>

<style scoped>
/* Keep styling minimal; leverage Bootstrap/Hyper UI */
</style>
