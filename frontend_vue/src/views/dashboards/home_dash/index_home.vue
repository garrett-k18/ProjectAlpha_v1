<template>
  <!--
    Root dashboard wrapper uses the shared Hyper UI Layout so we inherit the
    topbar, sidebar, and global styles. All content below is the internal
    dashboard page content specific to the homepage.
  -->
  <Layout>
    <!--
      Page Title Row
      - Uses BootstrapVue3 grid components (<b-row>/<b-col>) already used project-wide
      - Class "page-title-box" matches Hyper UI template styling
    -->
    <b-row>
      <b-col class="col-12">
        <div class="page-title-box text-center">
          <h1 class="page-title m-5" style="font-size: 3rem;">{{ greeting }}!</h1>
        </div>
      </b-col>
    </b-row>

    <!-- Stats Row - Key metrics tiles -->
    <StatsWidget />

    <!-- Pipeline Widget - Asset pipeline stages by outcome track -->
    <b-row class="mt-3">
      <b-col cols="12">
        <PipelineWidget />
      </b-col>
    </b-row>

    <!-- 
      Note: Macro Rates Widget removed - Financial Ticker Banner shown at bottom of home page only
      The ticker provides auto-scrolling market indicators (SOFR, Fed Funds, 30-Year Mortgage, etc.)
    -->
    
    <!-- Calendar Widget (full width now that Macro Rates is removed) -->
    <b-row class="mt-1">
      <b-col cols="12">
        <HomeCalendarWidget />
      </b-col>
    </b-row>

    <!--
      Secondary Row (placeholders)
      - Left: Recent Activity list
      - Right: Getting Started / Documentation pointers
      - Replace with real components or data once APIs/stores are ready
    -->
    <b-row class="mt-1">
      <!-- Recent Activity -->
      <b-col cols="12" xl="6" class="mb-3">
        <div class="card h-100">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Recent Activity</h5>
            <button type="button" class="btn btn-sm btn-outline-primary" @click="goToActivity">View All</button>
          </div>
          <div class="card-body" style="max-height: 360px; overflow-y: auto;">
            <div v-if="isLoadingRecentActivity" class="text-center py-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            <div v-else>
              <ul v-if="recentActivity.length" class="list-unstyled mb-0">
                <li v-for="(evt, idx) in recentActivity" :key="`evt-${idx}`" class="d-flex align-items-start mb-3">
                  <i class="mdi mdi-checkbox-blank-circle-outline text-primary me-2 mt-1"></i>
                  <div>
                    <div class="fw-semibold">{{ evt.title }}</div>
                    <div v-if="evt.message" class="text-muted small">{{ evt.message }}</div>
                    <small class="text-muted">{{ evt.when }}</small>
                  </div>
                </li>
              </ul>
              <div v-else class="text-muted small">No recent activity</div>
            </div>
          </div>
        </div>
      </b-col>

      <!-- Getting Started / Docs -->
      <b-col cols="12" xl="6" class="mb-3">
        <div class="card h-100">
          <div class="card-header">
            <h5 class="mb-0">Getting Started</h5>
          </div>
          <div class="card-body">
            <p class="text-muted">
              This homepage follows Vue Router best practices and Hyper UI patterns used across the app.
              Hook up real data from Pinia stores or backend APIs when ready.
            </p>
            <ol class="mb-0 ps-3">
              <li class="mb-2">Wire stats to Pinia stores (e.g., acquisitions counts, assets under mgmt).</li>
              <li class="mb-2">Replace Recent Activity with real events (audits, assignments, uploads).</li>
              <li class="mb-2">Add role-aware tiles if needed using your `displayRole` helpers.</li>
            </ol>
          </div>
        </div>
      </b-col>
    </b-row>
  </Layout>
  <!-- End Layout wrapper -->
  
  <!-- Financial Ticker - Only shown on home page -->
  <FinancialTicker />
</template>

<script lang="ts">
// Import the shared Layout at the top-level per code standards
import Layout from "@/components/layouts/layout.vue";
// Financial ticker tape - auto-scrolling market indicators (home page only)
import FinancialTicker from '@/components/FinancialTicker.vue'
// Condensed calendar widget for homepage (modular, reusable)
import HomeCalendarWidget from '@/components/widgets/HomeCalendarWidget.vue'
// Stats widget - key metrics tiles (Assets, Tasks, Brokers, Docs)
import StatsWidget from './components/StatsWidget.vue'
// Pipeline widget - asset pipeline stages by outcome track (FC, REO, etc.)
import PipelineWidget from './components/PipelineWidget.vue'
// Django auth store for user data
import { useDjangoAuthStore } from '@/stores/djangoAuth'
import http from '@/lib/http'

type ActivityRow = {
  id: string
  source: string
  created_at: string
  title: string
  message: string
}

type RecentActivityItem = {
  title: string
  message?: string
  when: string
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
  // Explicit component name for devtools and tracing
  name: "HomePage",
  // Register child components locally
  components: {
    Layout,
    FinancialTicker,
    HomeCalendarWidget,
    StatsWidget,
    PipelineWidget,
  },
  // Options API state for simplicity and broad compatibility across the app
  data() {
    return {
      recentActivity: [] as RecentActivityItem[],
      isLoadingRecentActivity: false,
    };
  },
  async mounted() {
    await this.loadRecentActivity()
  },
  computed: {
    /**
     * greeting: Personalized time-based greeting with user's first name
     * Returns "Good Morning/Afternoon/Evening [FirstName]"
     * Morning: 5am-11:59am, Afternoon: 12pm-4:59pm, Evening: 5pm-4:59am
     */
    greeting(): string {
      const authStore = useDjangoAuthStore();
      const firstName = authStore.user?.first_name || 'User';
      
      // Get current hour (0-23)
      const hour = new Date().getHours();
      
      // Determine time of day
      let timeOfDay = 'Evening';
      if (hour >= 5 && hour < 12) {
        timeOfDay = 'Morning';
      } else if (hour >= 12 && hour < 17) {
        timeOfDay = 'Afternoon';
      }
      
      return `Good ${timeOfDay}, ${firstName}`;
    }
  },
  methods: {
    async loadRecentActivity() {
      this.isLoadingRecentActivity = true
      try {
        const res = await http.get('/core/activity/?limit=8')
        const rows: ActivityRow[] = (res as any)?.data || []

        this.recentActivity = (rows || []).map((row: ActivityRow) => {
          const msg = (row.message || '').trim()
          return {
            title: row.title || 'Activity',
            message: msg ? msg : undefined,
            when: formatRelativeTime(row.created_at),
          }
        })
      } catch (e) {
        console.error('Failed to load recent activity:', e)
        this.recentActivity = []
      } finally {
        this.isLoadingRecentActivity = false
      }
    },
    goToActivity() {
      this.$router.push('/pages/activity')
    },
  },
};
</script>

