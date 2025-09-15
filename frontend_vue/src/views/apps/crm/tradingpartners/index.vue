<template>
  <Layout>
    <Breadcrumb :title="title" :items="items"/>
    <b-row>
      <b-col cols="12" >
        <div class="card">
          <div class="card-body">
            <b-row class="mb-2">
              <b-col xl="8">
                <!-- Simple search form for trading partners (filters by firm/name/email/phone fields) -->
                <b-form class="row gy-2 gx-2 align-items-center justify-content-xl-start justify-content-between" @submit.prevent="onSearch">
                  <b-col class="col-auto">
                    <label for="search-input" class="visually-hidden">Search</label>
                    <input
                      type="search"
                      class="form-control"
                      id="search-input"
                      v-model="store.q"
                      placeholder="Search firms, names, emails, phones..."
                    >
                  </b-col>
                  <b-col class="col-auto">
                    <button type="submit" class="btn btn-primary">Search</button>
                  </b-col>
                </b-form>
              </b-col>
              <b-col xl="4">
                <div class="text-xl-end mt-xl-0 mt-2">
                  <button type="button" class="btn btn-danger mb-2 me-2" @click="showAddPartner = true">
                    <i class="mdi mdi-account-plus-outline me-1"></i>
                    Add Partner
                  </button>
                  <button type="button" class="btn btn-light mb-2">Export</button>
                </div>
              </b-col><!-- end col-->
            </b-row>

            <!-- Add/Edit Trading Partner Modal -->
            <b-modal v-model="showAddPartner" :title="isEditing ? 'Edit Partner' : 'Add Partner'" hide-footer>
              <b-form @submit.prevent="onSubmitPartner">
                <b-row class="g-2">
                  <!-- Firm (required) -->
                  <b-col cols="12" md="6">
                    <label class="form-label">Firm<span class="text-danger">*</span></label>
                    <b-form-input v-model="form.firm" placeholder="Example Capital" required></b-form-input>
                  </b-col>
                  <!-- Primary contact name -->
                  <b-col cols="12" md="6">
                    <label class="form-label">Primary Contact</label>
                    <b-form-input v-model="form.name" placeholder="Jane Doe"></b-form-input>
                  </b-col>
                  <!-- Primary contact email -->
                  <b-col cols="12" md="6">
                    <label class="form-label">Email</label>
                    <b-form-input v-model="form.email" type="email" placeholder="jane@example.com"></b-form-input>
                  </b-col>
                  <!-- Primary contact phone -->
                  <b-col cols="12" md="6">
                    <label class="form-label">Phone</label>
                    <b-form-input v-model="form.phone" placeholder="(555) 123-4567"></b-form-input>
                  </b-col>
                  <!-- Alternate contact info -->
                  <b-col cols="12" md="6">
                    <label class="form-label">Alt Contact Name</label>
                    <b-form-input v-model="form.altname" placeholder="John Smith"></b-form-input>
                  </b-col>
                  <b-col cols="12" md="6">
                    <label class="form-label">Alt Contact Email</label>
                    <b-form-input v-model="form.altemail" type="email" placeholder="john@example.com"></b-form-input>
                  </b-col>
                  <b-col cols="12" md="6">
                    <label class="form-label">Alt Contact Phone</label>
                    <b-form-input v-model="form.alt_phone" placeholder="(555) 222-3333"></b-form-input>
                  </b-col>
                  <!-- NDA fields -->
                  <b-col cols="12" md="3" class="d-flex align-items-center">
                    <div class="form-check mt-3 mt-md-0">
                      <input class="form-check-input" type="checkbox" id="nda-flag" v-model="form.nda_flag">
                      <label class="form-check-label" for="nda-flag">NDA Required</label>
                    </div>
                  </b-col>
                  <b-col cols="12" md="3">
                    <label class="form-label">NDA Signed (YYYY-MM-DD)</label>
                    <b-form-input v-model="form.nda_signed" type="date"></b-form-input>
                  </b-col>
                </b-row>

                <div class="d-flex justify-content-end mt-3">
                  <button type="button" class="btn btn-light me-2" @click="onCancelAdd">Cancel</button>
                  <button type="submit" class="btn btn-primary" :disabled="submitting">
                    <span v-if="submitting" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
                    {{ isEditing ? 'Update Partner' : 'Save Partner' }}
                  </button>
                </div>
              </b-form>
            </b-modal>

            <!-- NDA Viewer Modal -->
            <b-modal v-model="showNdaModal" title="NDA Document" hide-footer>
              <!--
                Plan (backend):
                - Create a read-only endpoint like GET /api/acq/trading-partners/:id/nda/
                  which returns { url?: string, filename?: string, content_type?: string } OR streams the file.
                - Alternatively, a generic documents endpoint: GET /api/acq/trading-partners/:id/documents?type=nda
                - This frontend will either:
                  a) render the URL in an <iframe>/<object> if it's a web-safe MIME (e.g., application/pdf), or
                  b) show a download button for non-embeddable types.
                - Auth: per current dev standard, public for now; reintroduce auth later.
              -->
              <div v-if="ndaLoading" class="text-center py-3">
                <span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
                Loading NDA…
              </div>
              <div v-else-if="ndaError" class="text-danger py-2">
                {{ ndaError }}
              </div>
              <div v-else-if="ndaDocUrl" class="ratio ratio-4x3">
                <!-- Try to embed the NDA document if it's a PDF or browser-viewable type -->
                <iframe :src="ndaDocUrl" style="border:0" title="NDA Document"></iframe>
              </div>
              <div v-else class="text-muted py-2">
                No NDA document available for this partner yet.
              </div>
            </b-modal>

            <div class="table-responsive">
              <table class="table table-sm table-centered table-nowrap mb-0 crm-brokers-table">
                <thead class="table-light">
                <tr>
                  <th style="width: 20px;">
                    <div class="form-check">
                      <input type="checkbox" class="form-check-input" id="selectAll">
                      <label class="form-check-label" for="selectAll">&nbsp;</label>
                    </div>
                  </th>
                  <th>Partner</th>
                  <th>Firm</th>
                  <th>NDA</th>
                  <th>Contact</th>
                  <th style="width: 125px;">Actions</th>
                </tr>
                </thead>
                <tbody>
                <tr v-if="store.loading">
                  <td colspan="6">
                    <div class="text-center py-3">Loading partners…</div>
                  </td>
                </tr>
                <tr v-else-if="store.error">
                  <td colspan="6">
                    <div class="text-danger">{{ store.error }}</div>
                  </td>
                </tr>
                <tr v-else-if="!store.results.length">
                  <td colspan="6">
                    <div class="text-muted">No partners found.</div>
                  </td>
                </tr>
                <tr v-else v-for="partner in store.results" :key="partner.id">
                  <td>
                    <div class="form-check">
                      <input type="checkbox" class="form-check-input" :id="`row-${partner.id}`">
                      <label class="form-check-label" :for="`row-${partner.id}`">&nbsp;</label>
                    </div>
                  </td>
                  <td>
                    <span class="text-body fw-bold">{{ partner.name || '—' }}</span>
                  </td>
                  <td>{{ partner.firm }}</td>
                  <td>
                    <span v-if="partner.nda_flag" class="badge bg-success">Required</span>
                    <span v-else class="badge bg-secondary">No NDA</span>
                    <div v-if="partner.nda_signed" class="text-muted small">Signed: {{ partner.nda_signed }}</div>
                  </td>
                  <td>
                    <div class="crm-contact">
                      <a v-if="partner.email" :href="`mailto:${partner.email}`">{{ partner.email }}</a>
                      <span v-else>—</span>
                    </div>
                    <div v-if="partner.phone">
                      <a :href="`tel:${(partner.phone || '').replace(/\D/g, '')}`">{{ formatPhone(partner.phone) }}</a>
                    </div>
                  </td>
                  <td>
                    <!-- Edit partner action -->
                    <a href="javascript:void(0);" class="action-icon me-1" title="Edit" @click="onEdit(partner)">
                      <i class="mdi mdi-square-edit-outline"></i>
                    </a>
                    <!-- View NDA action (opens modal). Future: if no NDA on file, we could disable or show tooltip. -->
                    <a href="javascript:void(0);" class="action-icon" title="View NDA" @click="onViewNda(partner)">
                      <i class="mdi mdi-file-document-outline"></i>
                    </a>
                  </td>
                </tr>
                </tbody>
              </table>
            </div>
          </div> <!-- end card-body-->
        </div> <!-- end card-->
      </b-col> <!-- end col -->
    </b-row> <!-- end row -->
  </Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";
import { useTradingPartnersStore } from '@/stores/tradingPartners'

export default {
  components: {Breadcrumb, Layout},
  data() {
    return {
      title: 'Trading Partners',
      items: [
        { text: 'Hyper', href: '/' },
        { text: 'CRM', href: '/' },
        { text: 'Trading Partners', active: true },
      ],
      store: useTradingPartnersStore(),
      // Modal visibility flag for Add Partner
      showAddPartner: false,
      // Editing mode state
      isEditing: false,
      editId: null as number | null,
      // Local form model for new trading partner (aligned to TradingPartnerCRM fields)
      form: {
        firm: '',
        name: '',
        email: '',
        phone: '',
        altname: '',
        altemail: '',
        alt_phone: '',
        nda_flag: false,
        nda_signed: '' as string,
      },
      submitting: false,
      // NDA viewer modal state
      showNdaModal: false, // controls visibility of NDA modal
      ndaLoading: false,   // shows spinner while fetching NDA metadata/file URL
      ndaError: null as string | null, // holds any fetch error to display
      ndaDocUrl: '' as string,         // embeddable URL to the NDA (e.g., signed PDF)
    }
  },
  mounted() {
    // Fetch first page of trading partners on mount
    this.store.fetchPartners({ page: 1 })
  },
  methods: {
    // Trigger backend search by q and reload first page
    async onSearch() {
      await this.store.fetchPartners({ page: 1, q: this.store.q })
    },
    // Format a phone number to (xxx) xxx-xxxx; falls back to raw if not 10 digits
    formatPhone(phone: string | null): string {
      const digits = (phone || '').replace(/\D/g, '')
      if (digits.length === 10) {
        const area = digits.slice(0, 3)
        const mid = digits.slice(3, 6)
        const last = digits.slice(6)
        return `(${area}) ${mid}-${last}`
      }
      return phone || ''
    },
    // Reset form to initial state
    resetForm() {
      this.form = { firm: '', name: '', email: '', phone: '', altname: '', altemail: '', alt_phone: '', nda_flag: false, nda_signed: '' }
    },
    // Handle cancel from the modal
    onCancelAdd() {
      this.resetForm()
      this.showAddPartner = false
      this.isEditing = false
      this.editId = null
    },
    // Submit create/update partner to backend via Pinia store
    async onSubmitPartner() {
      this.submitting = true
      let ok = false
      const payload = {
        firm: this.form.firm,
        name: this.form.name || null,
        email: this.form.email || null,
        phone: this.form.phone || null,
        altname: this.form.altname || null,
        altemail: this.form.altemail || null,
        alt_phone: this.form.alt_phone || null,
        nda_flag: !!this.form.nda_flag,
        nda_signed: this.form.nda_signed || null,
      }
      if (this.isEditing && this.editId != null) {
        ok = await this.store.updatePartner(this.editId, payload)
      } else {
        ok = await this.store.createPartner(payload)
      }
      this.submitting = false
      if (ok) {
        this.showAddPartner = false
        this.resetForm()
        this.isEditing = false
        this.editId = null
      }
    },
    // Populate form and open modal in editing mode
    onEdit(partner: any) {
      this.isEditing = true
      this.editId = partner.id
      this.form = {
        firm: partner.firm || '',
        name: partner.name || '',
        email: partner.email || '',
        phone: partner.phone || '',
        altname: partner.altname || '',
        altemail: partner.altemail || '',
        alt_phone: partner.alt_phone || '',
        nda_flag: !!partner.nda_flag,
        nda_signed: partner.nda_signed || '',
      }
      this.showAddPartner = true
    },
    // Open the NDA viewer modal for the selected partner
    // Notes:
    // - Backend is not implemented yet. Planned endpoint options:
    //   a) GET /api/acq/trading-partners/:id/nda/ -> { url, filename, content_type }
    //   b) GET /api/acq/trading-partners/:id/documents?type=nda -> latest NDA doc
    // - When implemented, perform an http.get to retrieve a signed URL or stream.
    // - If content_type is application/pdf, we can embed via <iframe>. Otherwise show a download link.
    onViewNda(partner: any) {
      // Reset NDA modal state
      this.ndaLoading = true
      this.ndaError = null
      this.ndaDocUrl = ''
      this.showNdaModal = true

      // TODO: Replace this placeholder with a real API call once backend exists.
      // Example:
      // const resp = await http.get(`/acq/trading-partners/${partner.id}/nda/`)
      // this.ndaDocUrl = resp.data.url
      // this.ndaLoading = false
      // Handle errors by setting this.ndaError

      // Placeholder behavior for now
      this.ndaLoading = false
      this.ndaError = 'NDA endpoint not implemented yet. TODO: wire to /api/acq/trading-partners/:id/nda/ and return a signed PDF URL.'
    },
  }
}
</script>

<style scoped>
/* Keep row height compact so email + phone fits without increasing row size */
.crm-brokers-table td,
.crm-brokers-table th {
  padding-top: 0.35rem;
  padding-bottom: 0.35rem;
  vertical-align: middle;
}

/* Compact stacking of email and phone */
.crm-brokers-table td .crm-contact,
.crm-brokers-table td .crm-contact + div {
  line-height: 1.1;
  margin: 0;
}
</style>
