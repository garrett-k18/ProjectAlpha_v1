<template>
  <!-- Standalone: render with Hyper Layout/Breadcrumb -->
  <Layout v-if="standalone">
    <Breadcrumb :items="items" :title="title" />
    <b-row>
      <b-col xl="4" lg="5">
        <Profile />
      </b-col>
      <b-col xl="8" lg="7">
        <b-card>
          <b-tabs content-class="mt-3" pills justified nav-class="bg-nav-pills">
            <b-tab active title="Settings" title-link-class="rounded-0">
              <Settings />
            </b-tab>
          </b-tabs>
        </b-card>
      </b-col>
    </b-row>
  </Layout>

  <!-- Public token route: render without site chrome and WITHOUT profile/sidebar
       Only show the broker form fields to keep this page isolated from the rest of the app. -->
  <div v-else>
    <!-- Error banner for invalid/expired/used tokens -->
    <b-alert
      v-if="tokenStatus !== 'loading' && tokenStatus !== 'valid'"
      show
      variant="danger"
      class="mb-3"
    >
      <strong>Access error:</strong>
      <span v-if="tokenStatus === 'expired'">This link has expired. Please contact your Project Alpha contact for a new link.</span>
      <span v-else-if="tokenStatus === 'used'">This single-use link has already been used.</span>
      <span v-else>Invalid link. Please check that the full URL was copied.</span>
    </b-alert>

    <!-- Lightweight loading state while validating token -->
    <div v-if="tokenStatus === 'loading'" class="text-center my-4">
      Validating access…
    </div>

    <!-- Main content only when token is valid in public mode -->
    <div v-else-if="tokenStatus === 'valid'">
      <b-row>
        <b-col cols="12">
          <b-card>
            <Settings />
          </b-card>
        </b-col>
      </b-row>
    </div>
  </div>
</template>

<script lang="ts">
import Layout from '@/components/layouts/layout.vue'
import Breadcrumb from '@/components/breadcrumb.vue'
import Profile from './profile.vue'
import Settings from './setting.vue'

/*
  Quick access URLs (Vite dev default origin http://localhost:5173):
  - Authenticated internal route (requires login): http://localhost:5173/acq/brokerview
    Defined in `src/router/routes.ts` under `acqModuleRoutes` (path '/acq/brokerview', meta.authRequired=true).
  - Public token route (no login): http://localhost:5173/brokerview/<token>
    Defined in `src/router/routes.ts` under `externalPublicRoutes` (path '/brokerview/:token', meta.authRequired=false).
  - Backend token validation endpoint: GET /api/acq/broker-invites/:token/ (proxied to Django http://localhost:8000 via Vite `server.proxy`).

  For preview/prod, only the origin changes; the paths stay the same.
*/
export default {
  components: { Layout, Breadcrumb, Profile, Settings },
  props: {
    // When false, render without the Hyper Layout/Breadcrumb for public token links
    standalone: { type: Boolean, default: true },
    // Token passed from the public route: /brokerview/:token
    token: { type: String, default: null },
  },
  data() {
    return {
      title: 'Brokerview',
      items: [
        {
          text: 'Hyper',
          href: '/',
        },
        {
          text: 'Pages',
          href: '/',
        },
        {
          text: 'Brokerview',
          active: true,
        },
      ],
      // Token validation state for public access
      tokenStatus: this.standalone ? 'valid' : 'loading', // 'loading' | 'valid' | 'invalid' | 'expired' | 'used'
      tokenError: null as any,
      sellerRawDataId: null as number | null,
    }
  },
    mounted() {
        // Validate token when rendered in public mode
        if (!this.standalone) {
            this.validateToken()
        }
    },
    methods: {
        async validateToken() {
            // Guard if token missing
            if (!this.token) {
                this.tokenStatus = 'invalid'
                return
            }
            try {
                // Use relative URL so it works in all envs; DRF route registered at /api/acq/broker-invites/<token>/
                const res = await fetch(`/api/acq/broker-invites/${encodeURIComponent(this.token)}/`, {
                    method: 'GET',
                    headers: { 'Accept': 'application/json' },
                    credentials: 'same-origin',
                })
                if (res.ok) {
                    const data = await res.json()
                    this.tokenStatus = data.valid ? 'valid' : 'invalid'
                    this.sellerRawDataId = data.seller_raw_data ?? null
                } else {
                    const err = await res.json().catch(() => ({}))
                    // Map backend reasons to local states
                    const reason = err?.reason || err?.detail
                    if (reason === 'expired' || reason === 'token_expired') this.tokenStatus = 'expired'
                    else if (reason === 'used' || reason === 'token_used') this.tokenStatus = 'used'
                    else this.tokenStatus = 'invalid'
                    this.sellerRawDataId = err?.seller_raw_data ?? null
                    this.tokenError = err
                }
            } catch (e) {
                this.tokenStatus = 'invalid'
                this.tokenError = e
            }
        },
    },
}
</script>
