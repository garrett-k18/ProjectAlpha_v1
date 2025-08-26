<template>
  <!-- Single broker view: render without site chrome (no header/sidebar) using DefaultLayout.
       Token validation gates content (error/loading/valid), and we only expose broker-assigned data. -->
  <DefaultLayout>
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

    <!-- Main content only when token is valid -->
    <div v-else-if="tokenStatus === 'valid'">
      <!-- Profile centered at top. Add top padding for breathing room (uses Bootstrap utilities). -->
      <b-row class="justify-content-center pt-4 pt-md-5">
        <b-col cols="12" md="8" lg="6" xl="5">
          <Profile :broker="portalMode ? portalMeta?.broker : null" />
        </b-col>
      </b-row>
      <!-- Form card below, full width -->
      <b-row class="mt-3">
        <!-- Add horizontal padding so the card doesn't touch viewport edges on small screens. -->
        <b-col cols="12" class="px-3 px-md-4">
          <b-card>
            <!-- Simple form table: shows basic fields without tabs or expiry info -->
            <h4 class="mb-3">Assigned Valuations</h4>
            <BrokerFormTable
              v-model="form"
              :address="assignedAddress"
              :inviteToken="selectedInviteToken || undefined"
              :sellerRawDataId="sellerRawDataId ?? undefined"
              :prefillValues="prefillValues || undefined"
            />
          </b-card>
        </b-col>
      </b-row>
    </div>
  </DefaultLayout>
</template>

<script lang="ts">
import DefaultLayout from '@/components/layouts/default-layout.vue'
import Profile from './profile.vue'
import BrokerFormTable from './broker-form-table.vue'

/*
  Quick access URL (Vite dev default origin http://localhost:5173):
  - Public token route (no login): http://localhost:5173/brokerview/<token>
    Defined in `src/router/routes.ts` under `externalPublicRoutes` (path '/brokerview/:token', meta.authRequired=false).
  - Backend validation endpoints:
    • Portal token: GET /api/acq/broker-portal/<token>/
    • Single-invite token: GET /api/acq/broker-invites/<token>/

  For preview/prod, only the origin changes; the paths stay the same.
*/
export default {
  components: { DefaultLayout, Profile, BrokerFormTable },
  props: {
    // Token passed from the route: /brokerview/:token
    token: { type: String, default: null },
  },
  data() {
    return {
      // Token validation state for public access
      tokenStatus: 'loading', // 'loading' | 'valid' | 'invalid' | 'expired' | 'used'
      tokenError: null as any,
      sellerRawDataId: null as number | null,
      // When true, the provided token is a portal token tied to a broker (multi-use)
      portalMode: false as boolean,
      // Raw portal metadata returned from backend (includes broker info and expiry)
      portalMeta: null as any,
      // Simple form model for the basic table fields
      form: {
        name: '',
        email: '',
        firm: '',
      } as { name: string; email: string; firm: string },
      // Placeholder for static assigned record address shown in the table header row
      assignedAddress: '',
      // Active invite token for submit endpoint (portal first invite or single-invite token)
      selectedInviteToken: null as string | null,
      // Prefill values from backend BrokerValues (if present in portal payload)
      prefillValues: null as null | {
        broker_asis_value?: string | number | null
        broker_arv_value?: string | number | null
        broker_rehab_est?: string | number | null
        broker_value_date?: string | null
        broker_notes?: string | null
      },
    }
  },
    mounted() {
        // Always validate the token for this single broker view
        this.validateToken()
    },
    methods: {
        async validateToken() {
            // Guard if token missing
            if (!this.token) {
                this.tokenStatus = 'invalid'
                return
            }
            // First try broker portal endpoint; if not found or invalid, fall back to single-invite
            try {
                const portalRes = await fetch(`/api/acq/broker-portal/${encodeURIComponent(this.token)}/`, {
                    method: 'GET',
                    headers: { 'Accept': 'application/json' },
                    credentials: 'same-origin',
                })
                if (portalRes.ok) {
                    const data = await portalRes.json()
                    if (data.valid) {
                        // Enter portal mode and seed form from broker data
                        this.portalMode = true
                        this.portalMeta = { broker: data.broker, expires_at: data.expires_at }
                        this.form.name = data?.broker?.broker_name || ''
                        this.form.email = data?.broker?.broker_email || ''
                        this.form.firm = data?.broker?.broker_firm || ''
                        // Choose an entry: prefer ?srd= match from assigned_entries, else first active invite, else first assigned entry
                        const assigned = Array.isArray(data.assigned_entries) ? data.assigned_entries : []
                        const active = Array.isArray(data.active_invites) ? data.active_invites : []
                        const s = new URLSearchParams(window.location.search)
                        const srdParam = s.get('srd')
                        const srdNum = srdParam && /^\d+$/.test(srdParam) ? Number(srdParam) : null
                        let chosen: any = null
                        if (srdNum != null) {
                          chosen = assigned.find((e: any) => e?.seller_raw_data === srdNum) || active.find((e: any) => e?.seller_raw_data === srdNum) || null
                        }
                        if (!chosen) chosen = active.length ? active[0] : (assigned.length ? assigned[0] : null)

                        // Address from chosen entry (structured)
                        if (chosen?.address) {
                          const a = chosen.address
                          const composed = [a.street_address, a.city, a.state].filter(Boolean).join(', ') + (a.zip ? ` ${a.zip}` : '')
                          this.assignedAddress = (composed || '').trim()
                        } else {
                          // Fallback extractor (legacy shapes)
                          this.assignedAddress = this.extractAddressFromPortalPayload(data) || ''
                        }

                        // SRD id
                        this.sellerRawDataId = chosen?.seller_raw_data ?? null

                        // Only allow saving if the chosen token is active
                        const tokenMeta = chosen?.token
                        const isActive = tokenMeta && !tokenMeta.is_expired && (!tokenMeta.single_use || !tokenMeta.is_used)
                        this.selectedInviteToken = isActive ? (tokenMeta?.value || null) : null

                        // Prefill from any saved values on the chosen entry
                        this.prefillValues = chosen?.values || null
                        this.tokenStatus = 'valid'
                        return
                    }
                } else if (portalRes.status === 400) {
                    const err = await portalRes.json().catch(() => ({}))
                    const reason = err?.reason || err?.detail
                    if (reason === 'expired') {
                        this.tokenStatus = 'expired'
                        this.tokenError = err
                        return
                    }
                }
            } catch (e: any) {
                // Ignore portal network errors and try single-invite
            }

            // Fallback: single-invite validation
            try {
                const res = await fetch(`/api/acq/broker-invites/${encodeURIComponent(this.token)}/`, {
                    method: 'GET',
                    headers: { 'Accept': 'application/json' },
                    credentials: 'same-origin',
                })
                if (res.ok) {
                    const data = await res.json()
                    this.tokenStatus = data.valid ? 'valid' : 'invalid'
                    this.sellerRawDataId = data.seller_raw_data ?? null
                    // In single-invite flow, the route token is the submission token
                    this.selectedInviteToken = this.token
                    // Attempt to extract the assigned subject address from single-invite payload
                    this.assignedAddress = this.extractAddressFromInvitePayload(data) || ''
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

        // Attempt to extract a human-readable address from the broker-portal payload.
        // Because backend payloads can evolve, this method checks several common shapes
        // defensively and returns the first non-empty string it finds.
        // Update these selectors as the backend adds a canonical address field.
        extractAddressFromPortalPayload(data: any): string | null {
            try {
                // Preferred: active_invites[0].address as provided by backend service
                const invites = Array.isArray(data?.active_invites) ? data.active_invites : []
                if (invites.length) {
                    const addr = invites[0]?.address
                    if (addr && (addr.street_address || addr.city || addr.state || addr.zip)) {
                        const a1 = addr.street_address
                        const city = addr.city
                        const st = addr.state
                        const zip = addr.zip
                        const composed = [a1, city, st].filter(Boolean).join(', ') + (zip ? ` ${zip}` : '')
                        if (composed.trim()) return composed.trim()
                    }
                }

                // Fallbacks: Common single-field candidates
                const direct = (
                    data?.subject_address ||
                    data?.address ||
                    data?.loan?.address ||
                    data?.property?.address ||
                    data?.broker?.subject_address
                )
                if (typeof direct === 'string' && direct.trim()) return direct.trim()

                // Fallbacks: Structured object candidates (address1/city/state/zip)
                const structuredCandidates = [
                    data?.loan?.subject_property,
                    data?.subject_property,
                    data?.property,
                ]
                for (const obj of structuredCandidates) {
                    if (obj && (obj.address1 || obj.street || obj.line1)) {
                        const a1 = obj.address1 || obj.street || obj.line1
                        const city = obj.city
                        const st = obj.state || obj.st
                        const zip = obj.zip || obj.postal_code
                        const composed = [a1, city, st].filter(Boolean).join(', ') + (zip ? ` ${zip}` : '')
                        if (composed.trim()) return composed.trim()
                    }
                }
            } catch (_) { /* ignore */ }
            return null
        },

        // Attempt to extract an address from the single-invite payload.
        // Some invite payloads may only include an ID (e.g., seller_raw_data). If there is no
        // address materialized in the payload, this returns null and the UI will show '—'.
        extractAddressFromInvitePayload(data: any): string | null {
            try {
                const direct = (
                    data?.subject_address ||
                    data?.address ||
                    data?.invite?.address
                )
                if (typeof direct === 'string' && direct.trim()) return direct.trim()

                const obj = data?.subject_property || data?.property
                if (obj) {
                    const a1 = obj.address1 || obj.street || obj.line1
                    const city = obj.city
                    const st = obj.state || obj.st
                    const zip = obj.zip || obj.postal_code
                    const composed = [a1, city, st].filter(Boolean).join(', ') + (zip ? ` ${zip}` : '')
                    if (composed.trim()) return composed.trim()
                }
            } catch (_) { /* ignore */ }
            return null
        },
    },
}
</script>
