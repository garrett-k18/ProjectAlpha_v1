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
        <div class="page-title-box d-flex justify-content-between align-items-center">
          <!-- Left: Page Title -->
          <h4 class="page-title mb-0">Dashboard</h4>
          <!-- Right: Optional actions (placeholders for now) -->
          <div class="d-none d-md-flex gap-2">
            <!-- These buttons are placeholders to demonstrate layout; wire to real actions later -->
            <button class="btn btn-sm btn-outline-secondary" type="button">
              <i class="mdi mdi-refresh"></i>
              Refresh
            </button>
            <button class="btn btn-sm btn-primary" type="button">
              <i class="mdi mdi-plus"></i>
              New
            </button>
          </div>
        </div>
      </b-col>
    </b-row>

    <!-- Condensed Calendar & External Events Widget (reuses FullCalendar stack) -->
    <b-row class="mt-1">
      <b-col cols="12">
        <HomeCalendarWidget />
      </b-col>
    </b-row>

    <!--
      Stats Row
      - Four lightweight tiles with key metrics
      - Data currently placeholder; replace with real store-driven values later
      - Using bg-light cards to match Hyper's tile style (low chrome)
    -->
    <b-row class="mt-2">
      <b-col v-for="(stat, idx) in stats" :key="`stat-${idx}`" cols="12" md="6" xl="3" class="mb-3">
        <div class="card bg-light border-0 h-100">
          <div class="card-body d-flex align-items-center">
            <!-- Icon circle -->
            <div class="me-3 flex-shrink-0">
              <div class="avatar-sm">
                <span class="avatar-title rounded bg-primary text-white">
                  <i :class="stat.icon"></i>
                </span>
              </div>
            </div>
            <!-- Metric content -->
            <div class="flex-grow-1">
              <h6 class="text-muted text-uppercase fs-12 mb-1">{{ stat.label }}</h6>
              <h4 class="mb-0">{{ stat.value }}</h4>
              <small class="text-muted">{{ stat.subtext }}</small>
            </div>
          </div>
        </div>
      </b-col>
    </b-row>

    <!--
      Quick Links Row
      - Cards that link to primary app areas (Acquisitions, Asset Mgmt, CRM, Calendar)
      - Uses <router-link> to internal routes defined in src/router/routes.ts
    -->
    <b-row class="mt-1">
      <b-col cols="12">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Quick Links</h5>
            <!-- Optional "View All" could go to a site map; hidden for now -->
          </div>
          <div class="card-body">
            <div class="row g-3">
              <!-- Each quick link tile -->
              <div v-for="(item, idx) in quickLinks" :key="`ql-${idx}`" class="col-12 col-md-6 col-xl-3">
                <router-link :to="item.to" class="text-decoration-none">
                  <div class="card h-100 border shadow-none hover-shadow">
                    <div class="card-body d-flex align-items-start gap-3">
                      <div class="avatar-sm flex-shrink-0">
                        <span class="avatar-title rounded-circle bg-secondary text-white">
                          <i :class="item.icon"></i>
                        </span>
                      </div>
                      <div class="flex-grow-1">
                        <h6 class="mb-1">{{ item.title }}</h6>
                        <p class="text-muted mb-0">{{ item.desc }}</p>
                      </div>
                    </div>
                  </div>
                </router-link>
              </div>
            </div>
          </div>
        </div>
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

export default {
  // Explicit component name for devtools and tracing
  name: "HomePage",
  // Register child components locally
  components: {
    Layout,
    HomeCalendarWidget,
  },
  // Options API state for simplicity and broad compatibility across the app
  data() {
    return {
      // stats: array of metric tiles shown at the top of the dashboard
      // Each object includes: label (string), value (string/number), subtext (string), icon (mdi class)
      stats: [
        { label: "Assets", value: "1,248", subtext: "Across all modules", icon: "mdi mdi-home-city" },
        { label: "Open Tasks", value: "32", subtext: "Due this week", icon: "mdi mdi-clipboard-text" },
        { label: "Brokers", value: "87", subtext: "Active contacts", icon: "mdi mdi-account-tie" },
        { label: "Docs", value: "542", subtext: "Uploaded this quarter", icon: "mdi mdi-file-document" },
      ],

      // quickLinks: primary navigation tiles for the most-used app areas
      // "to" values map to absolute paths defined in src/router/routes.ts
      quickLinks: [
        { title: "Acquisitions", to: "/acquisitions", icon: "mdi mdi-finance", desc: "Seller data tape, stratifications, loan-level" },
        { title: "Asset Mgmt", to: "/asset-mgmt", icon: "mdi mdi-domain", desc: "Active portfolio and monitoring" },
        { title: "CRM", to: "/crm", icon: "mdi mdi-account-group", desc: "Brokers, clients, trading partners" },
        { title: "Calendar", to: "/apps/calendar", icon: "mdi mdi-calendar-month", desc: "Events & reminders" },
      ],

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

