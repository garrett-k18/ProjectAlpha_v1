<template>
  <Layout>
    <Breadcrumb :title="title" :items="items"/>
    <b-row>
      <b-col cols="12" >
        <div class="card">
          <div class="card-body">
            <b-row class="mb-2">
              <b-col xl="8">
                <b-form class="row gy-2 gx-2 align-items-center justify-content-xl-start justify-content-between">
                  <b-col class="col-auto">
                    <label for="inputPassword2" class="visually-hidden">Search</label>
                    <input type="search" class="form-control" id="inputPassword2" placeholder="Search...">
                  </b-col>
                  <b-col class="col-auto">
                    <div class="d-flex align-items-center">
                      <label for="state-select" class="me-2">State</label>
                      <select class="form-select" id="state-select" v-model="store.stateFilter" @change="onChangeState">
                        <option value="">All</option>
                        <option v-for="s in uniqueStates" :key="s" :value="s">{{ s }}</option>
                      </select>
                    </div>
                  </b-col>
                </b-form>
              </b-col>
              <b-col xl="4">
                <div class="text-xl-end mt-xl-0 mt-2">
                  <button type="button" class="btn btn-danger mb-2 me-2" @click="showAddBroker = true">
                    <i class="mdi mdi-account-plus-outline me-1"></i>
                    Add Broker
                  </button>
                  <button type="button" class="btn btn-light mb-2">Export</button>
                </div>
              </b-col><!-- end col-->
            </b-row>

            <!-- Add/Edit Broker Modal -->
            <b-modal v-model="showAddBroker" :title="isEditing ? 'Edit Broker' : 'Add Broker'" hide-footer>
              <b-form @submit.prevent="onCreateBroker">
                <b-row class="g-2">
                  <b-col cols="12" md="6">
                    <label class="form-label">Broker Name</label>
                    <b-form-input v-model="form.broker_name" placeholder="Jane Doe"></b-form-input>
                  </b-col>
                  <b-col cols="12" md="6">
                    <label class="form-label">Contact (Email)</label>
                    <b-form-input v-model="form.broker_email" type="email" placeholder="jane@example.com"></b-form-input>
                  </b-col>
                  <b-col cols="12" md="6">
                    <label class="form-label">Phone</label>
                    <b-form-input v-model="form.broker_phone" placeholder="(555) 123-4567"></b-form-input>
                  </b-col>
                  <b-col cols="12" md="6">
                    <label class="form-label">Brokerage (Firm)</label>
                    <b-form-input v-model="form.broker_firm" placeholder="ABC Realty"></b-form-input>
                  </b-col>
                  <b-col cols="8" md="6">
                    <label class="form-label">City</label>
                    <b-form-input v-model="form.broker_city" placeholder="Austin"></b-form-input>
                  </b-col>
                  <b-col cols="4" md="3">
                    <label class="form-label">State</label>
                    <b-form-input
                      v-model="form.broker_state"
                      placeholder="TX"
                      maxlength="2"
                      @input="form.broker_state = (form.broker_state || '').toUpperCase().slice(0,2)"
                    ></b-form-input>
                  </b-col>
                </b-row>

                <div class="d-flex justify-content-end mt-3">
                  <button type="button" class="btn btn-light me-2" @click="onCancelAdd">Cancel</button>
                  <button type="submit" class="btn btn-primary" :disabled="submitting">
                    <span v-if="submitting" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
                    {{ isEditing ? 'Update Broker' : 'Save Broker' }}
                  </button>
                </div>
              </b-form>
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
                  <th>Broker Name</th>
                  <th>Brokerage</th>
                  <th>Locale</th>
                  <th>Contact</th>
                  <th style="width: 125px;">Actions</th>
                </tr>
                </thead>
                <tbody>
                <tr v-if="store.loading">
                  <td colspan="6">
                    <div class="text-center py-3">Loading brokers…</div>
                  </td>
                </tr>
                <tr v-else-if="store.error">
                  <td colspan="6">
                    <div class="text-danger">{{ store.error }}</div>
                  </td>
                </tr>
                <tr v-else-if="!store.results.length">
                  <td colspan="6">
                    <div class="text-muted">No brokers found.</div>
                  </td>
                </tr>
                <tr v-else v-for="broker in store.results" :key="broker.id">
                  <td>
                    <div class="form-check">
                      <input type="checkbox" class="form-check-input" :id="`row-${broker.id}`">
                      <label class="form-check-label" :for="`row-${broker.id}`">&nbsp;</label>
                    </div>
                  </td>
                  <td>
                    <router-link :to="`/acq/brokers/${broker.id}`" class="text-body fw-bold">
                      {{ broker.broker_name || '—' }}
                    </router-link>
                  </td>
                  <td>{{ broker.broker_firm || '—' }}</td>
                  <td>
                    <span>{{ broker.broker_city || '' }}</span>
                    <span v-if="broker.broker_city && broker.broker_state">, </span>
                    <span>{{ broker.broker_state || '' }}</span>
                  </td>
                  <td>
                    <div class="crm-contact">
                      <a v-if="broker.broker_email" :href="`mailto:${broker.broker_email}`">{{ broker.broker_email }}</a>
                      <span v-else>—</span>
                    </div>
                    <div v-if="broker.broker_phone">
                      <a :href="`tel:${(broker.broker_phone || '').replace(/\D/g, '')}`">{{ formatPhone(broker.broker_phone) }}</a>
                    </div>
                  </td>
                  <td>
                    <a href="javascript:void(0);" class="action-icon" title="Edit" @click="onEdit(broker)">
                      <i class="mdi mdi-square-edit-outline"></i>
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
import { useBrokersCrmStore } from '@/stores/brokerscrm'

export default {
  components: {Breadcrumb, Layout},
  data() {
    return {
      title: 'Brokers',
      items: [
        { text: 'Hyper', href: '/' },
        { text: 'CRM', href: '/' },
        { text: 'Brokers', active: true },
      ],
      store: useBrokersCrmStore(),
      // Modal visibility flag for Add Broker
      showAddBroker: false,
      // Editing mode state
      isEditing: false,
      editId: null as number | null,
      // Local form model for new broker (aligned to Brokercrm fields)
      form: {
        broker_name: '',
        broker_email: '',
        broker_phone: '',
        broker_firm: '',
        broker_city: '',
        broker_state: '',
      },
      submitting: false,
    }
  },
  mounted() {
    // Fetch first page on mount
    this.store.fetchBrokers({ page: 1 })
  },
  computed: {
    // Build a sorted unique set of states from current results for quick filtering
    uniqueStates(): string[] {
      const set = new Set<string>()
      for (const r of this.store.results) {
        if (r.broker_state) set.add(r.broker_state)
      }
      return Array.from(set).sort()
    },
  },
  methods: {
    // Trigger backend filter by state and reload first page
    async onChangeState() {
      await this.store.fetchBrokers({ page: 1, state: this.store.stateFilter })
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
      this.form = { broker_name: '', broker_email: '', broker_phone: '', broker_firm: '', broker_city: '', broker_state: '' }
    },
    // Handle cancel from the modal
    onCancelAdd() {
      this.resetForm()
      this.showAddBroker = false
      this.isEditing = false
      this.editId = null
    },
    // Submit new broker to backend via Pinia store
    async onCreateBroker() {
      this.submitting = true
      let ok = false
      const payload = {
        broker_name: this.form.broker_name || null,
        broker_email: this.form.broker_email || null,
        broker_phone: this.form.broker_phone || null,
        broker_firm: this.form.broker_firm || null,
        broker_city: this.form.broker_city || null,
        broker_state: this.form.broker_state || null,
      }
      if (this.isEditing && this.editId != null) {
        ok = await this.store.updateBroker(this.editId, payload)
      } else {
        ok = await this.store.createBroker(payload)
      }
      this.submitting = false
      if (ok) {
        this.showAddBroker = false
        this.resetForm()
        this.isEditing = false
        this.editId = null
      }
    },
    // Populate form and open modal in editing mode
    onEdit(broker: any) {
      this.isEditing = true
      this.editId = broker.id
      this.form = {
        broker_name: broker.broker_name || '',
        broker_email: broker.broker_email || '',
        broker_phone: broker.broker_phone || '',
        broker_firm: broker.broker_firm || '',
        broker_city: broker.broker_city || '',
        broker_state: broker.broker_state || '',
      }
      this.showAddBroker = true
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
