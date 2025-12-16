<template>
<Layout>

    <Breadcrumb :title="title" :items="items" />

    <b-row>
      <b-col cols="12">
        <RecentActivity :activity-data="activityData" :activity-window-height="activityWindowHeight" />
      </b-col>
    </b-row>

</Layout>
</template>

<script lang="ts">
import Layout from '@/components/layouts/layout.vue'
import Breadcrumb from '@/components/breadcrumb.vue'
import http from '@/lib/http'
import RecentActivity, { type ActivityItem } from '@/views/am_module/loanlvl/am_tasking/components/recent-activity.vue'

type ActivityRow = {
  id: string
  source: string
  created_at: string
  title: string
  message: string
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
  components: { Layout, Breadcrumb, RecentActivity },
  data() {
    return {
      title: 'Recent Activity',
      items: [
        { text: 'Hyper', href: '/' },
        { text: 'Activity', href: '/' },
        { text: 'Recent Activity', active: true },
      ],
      activityData: [] as ActivityItem[],
      activityWindowHeight: '600px',
    }
  },
  async mounted() {
    await this.loadActivity()
  },
  methods: {
    async loadActivity() {
      try {
        const res = await http.get('/core/activity/?limit=50')
        const rows: ActivityRow[] = (res as any)?.data || []

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
