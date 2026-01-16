<template>
  <RecentActivity :activity-data="activityData" :activity-window-height="activityWindowHeight"/>
</template>

<script lang="ts">
import RecentActivity, { type ActivityItem } from "@/views/am_module/loanlvl/am_tasking/components/recent-activity.vue";
import http from '@/lib/http'

 function toTitleToken(token: string): string {
   const raw = (token || '').trim()
   if (!raw) return ''
   if (/^\d+$/.test(raw)) return raw
   if (raw.toLowerCase() === 'am') return 'AM'
   if (raw.toLowerCase() === 'dq') return 'DQ'
   const lower = raw.toLowerCase()
   return lower.charAt(0).toUpperCase() + lower.slice(1)
 }

 function humanizeLabel(input: string): string {
   if (!input) return ''
   const withSpaces = String(input).replace(/_/g, ' ').replace(/\s+/g, ' ').trim()
   if (!withSpaces) return ''
   return withSpaces
     .split(' ')
     .map(toTitleToken)
     .filter(Boolean)
     .join(' ')
 }

 function humanizeActivityText(input: string): string {
   if (!input) return ''
   const str = String(input)
   return str.replace(/[A-Za-z0-9]+(?:_[A-Za-z0-9]+)+/g, (m) => humanizeLabel(m))
 }

 type ActivityRow = {
   id: string
   source: string
   created_at: string
   title: string
   message: string
   event_type?: string
   field_name?: string
 }

 function getActivityBadge(row: ActivityRow): { badgeText: string; badgeColor: ActivityItem['color'] } {
   if ((row.source || '').toLowerCase() === 'audit') {
     return { badgeText: 'Audit', badgeColor: 'secondary' }
   }

   const et = (row.event_type || '').toLowerCase()
   if (et === 'trade_import') return { badgeText: 'Import', badgeColor: 'success' }
   if (et === 'task_changed') return { badgeText: 'Task', badgeColor: 'info' }
   if (et === 'asset_liquidated') return { badgeText: 'Asset', badgeColor: 'warning' }
   return { badgeText: 'Notification', badgeColor: 'secondary' }
 }

 function formatActivityDetails(row: ActivityRow): string {
   const et = (row.event_type || '').toLowerCase()
   const msg = String(row.message || '')

   if (et === 'task_changed') {
     const m = msg.match(/\bTask\s+([A-Za-z0-9_]+)\b/i)
     if (m && m[1]) return humanizeLabel(m[1])
   }

   return humanizeActivityText(msg)
 }

function formatRelativeTime(dateStr: string): string {
  if (!dateStr) return ''
  try {
    const date = new Date(dateStr)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffSec = Math.floor(diffMs / 1000)
    const diffMin = Math.floor(diffSec / 60)
    const diffHr = Math.floor(diffMin / 60)
    const diffDay = Math.floor(diffHr / 24)

    if (diffSec < 60) return 'Just now'
    if (diffMin < 60) return `${diffMin} min ago`
    if (diffHr < 24) return `${diffHr} hr ago`
    if (diffDay < 7) return `${diffDay} day${diffDay > 1 ? 's' : ''} ago`

    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
    })
  } catch {
    return dateStr
  }
}

export default {
  components: {RecentActivity},

  data() {
    return {
      activityData: [] as ActivityItem[],
      activityWindowHeight: '403px',
    }
  },

  async mounted() {
    await this.loadActivity()
  },

  methods: {
    async loadActivity() {
      try {
        const res = await http.get('/core/activity/?limit=15')
        const rows: ActivityRow[] = (res as any)?.data || []

        this.activityData = (rows || []).map((row: any, idx: number) => {
          const isNotif = row.source === 'notification'
          const badge = getActivityBadge(row)
          return {
            id: idx + 1,
            icon: isNotif ? 'mdi-bell-outline' : 'mdi-history',
            title: humanizeLabel(row.title || 'Activity'),
            text: formatActivityDetails(row),
            subtext: formatRelativeTime(row.created_at),
            color: isNotif ? 'info' : 'secondary',
            badgeText: badge.badgeText,
            badgeColor: badge.badgeColor,
          }
        })
      } catch (e) {
        console.error('Failed to load activity:', e)
        this.activityData = []
      }
    },
  },
}
</script>

