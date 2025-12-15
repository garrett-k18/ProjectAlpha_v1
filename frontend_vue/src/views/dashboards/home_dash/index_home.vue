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
      <b-col cols="12" xl="8" class="mb-3">
        <div class="card h-100">
          <div class="card-header">
            <h5 class="mb-0">Recent Activity</h5>
          </div>
          <div class="card-body">
            <ul class="list-unstyled mb-0">
              <li v-for="(evt, idx) in recentActivity" :key="`evt-${idx}`" class="d-flex align-items-start mb-3">
                <i class="mdi mdi-checkbox-blank-circle-outline text-primary me-2 mt-1"></i>
                <div>
                  <div class="fw-semibold">{{ evt.title }}</div>
                  <small class="text-muted">{{ evt.when }}</small>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </b-col>

      <!-- Getting Started / Docs -->
      <b-col cols="12" xl="4" class="mb-3">
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
      // recentActivity: placeholder list of recent events; replace with real data later
      recentActivity: [
        { title: "Uploaded new Seller Data Tape (Q4)", when: "2 hours ago" },
        { title: "Assigned 12 loans to Broker CRM", when: "Yesterday" },
        { title: "Updated assumptions: state reference table", when: "2 days ago" },
      ],
    };
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
};
</script>

