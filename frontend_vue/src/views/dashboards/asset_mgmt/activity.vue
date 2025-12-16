<template>
  <RecentActivity :activity-data="activityData" :activity-window-height="activityWindowHeight"/>
</template>

<script lang="ts">
import RecentActivity, { type ActivityItem } from "@/views/am_module/loanlvl/am_tasking/components/recent-activity.vue";
import http from '@/lib/http'

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
        const rows = (res as any)?.data || []

        this.activityData = (rows || []).map((row: any, idx: number) => {
          const isNotif = row.source === 'notification'
          return {
            id: idx + 1,
            icon: isNotif ? 'mdi-bell-outline' : 'mdi-history',
            title: row.title || 'Activity',
            text: row.message || '',
            subtext: formatRelativeTime(row.created_at),
            color: isNotif ? 'info' : 'secondary',
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

