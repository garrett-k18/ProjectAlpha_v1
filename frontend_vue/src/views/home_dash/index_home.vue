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
        <div class="page-title-box">
          <h4 class="page-title mb-0">Dashboard</h4>
        </div>
      </b-col>
    </b-row>

    <!-- Quick Links - Compact navigation buttons -->
    <b-row class="mt-2 mb-2">
      <b-col cols="12">
        <QuickLinksWidget />
      </b-col>
    </b-row>

    <!-- Stats Row - Key metrics tiles -->
    <StatsWidget />

    <!-- Condensed Calendar & Macro Rates Row -->
    <b-row class="mt-1">
      <!-- Calendar Widget -->
      <b-col cols="12" lg="8">
        <HomeCalendarWidget />
      </b-col>
      
      <!-- Macro Rates Widget -->
      <b-col cols="12" lg="4">
        <MacroRatesWidget />
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
</template>

<script lang="ts">
// Import the shared Layout at the top-level per code standards
import Layout from "@/components/layouts/layout.vue";
// Condensed calendar widget for homepage (modular, reusable)
import HomeCalendarWidget from '@/components/widgets/HomeCalendarWidget.vue'
// Macro rates widget - displays economic indicators from FRED API
import MacroRatesWidget from './components/MacroRatesWidget.vue'
// Quick links widget - navigation tiles to primary app areas
import QuickLinksWidget from './components/QuickLinksWidget.vue'
// Stats widget - key metrics tiles (Assets, Tasks, Brokers, Docs)
import StatsWidget from './components/StatsWidget.vue'

export default {
  // Explicit component name for devtools and tracing
  name: "HomePage",
  // Register child components locally
  components: {
    Layout,
    HomeCalendarWidget,
    MacroRatesWidget,
    QuickLinksWidget,
    StatsWidget,
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
};
</script>

