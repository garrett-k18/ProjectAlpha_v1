<template>
  <!--
    BrokerFormTable
    Renders the Assigned Valuations table.
    Columns:
      - Address
      - As-Is Value
      - After Repair Value
      - Estimated Rehab
      - Notes (opens modal)
      - Uploads (photos/documents)
      - Links (data rooms / Dropbox, etc.)

    Notes on implementation:
      - We keep the v-model (modelValue) API intact to avoid breaking parent usage.
      - Internal reactive state `row` represents a single valuation input row.
      - Future: can be extended to multiple rows by turning `row` into an array and rendering v-for.
  -->
  <b-form @submit.prevent>
    <table class="table table-bordered table-sm align-middle mb-0">
      <thead class="table-light">
        <tr>
          <th class="text-nowrap">Address</th>
          <th class="text-nowrap">As-Is Value</th>
          <th class="text-nowrap">After Repair Value</th>
          <th class="text-nowrap">Estimated Rehab</th>
          <th class="text-nowrap">Notes</th>
          <th class="text-nowrap">Uploads</th>
          <th class="text-nowrap">Links</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <!-- Address: static display from prop (read-only) -->
          <td style="min-width: 220px;">
            <span class="d-inline-block text-truncate" style="max-width: 360px;" :title="address || 'Address'">
              {{ address || '—' }}
            </span>
          </td>

          <!-- As-Is Value: currency-like numeric (commas, no decimals) -->
          <td style="min-width: 160px;">
            <div class="input-group">
              <span class="input-group-text">$</span>
              <b-form-input
                type="text"
                inputmode="numeric"
                pattern="[0-9,]*"
                v-currency
                :value="asIsInput"
                @input="onCurrencyInput('asIs', $event)"
                placeholder="0"
              />
            </div>
          </td>

          <!-- After Repair Value (ARV): currency-like numeric (commas, no decimals) -->
          <td style="min-width: 160px;">
            <div class="input-group">
              <span class="input-group-text">$</span>
              <b-form-input
                type="text"
                inputmode="numeric"
                pattern="[0-9,]*"
                v-currency
                :value="arvInput"
                @input="onCurrencyInput('arv', $event)"
                placeholder="0"
              />
            </div>
          </td>

          <!-- Estimated Rehab: currency-like numeric (commas, no decimals) -->
          <td style="min-width: 160px;">
            <div class="input-group">
              <span class="input-group-text">$</span>
              <b-form-input
                type="text"
                inputmode="numeric"
                pattern="[0-9,]*"
                v-currency
                :value="rehabInput"
                @input="onCurrencyInput('rehab', $event)"
                placeholder="0"
              />
            </div>
          </td>

          <!-- Notes: opens a modal to enter a free-form note -->
          <td style="min-width: 140px;">
            <b-button size="sm" variant="primary" @click="notesOpen = true">
              <i class="mdi mdi-note-text-outline me-1"></i>
              Add Note
            </b-button>
            <!-- Modal for notes. Uses BootstrapVueNext modal which inherits Hyper theme styles. -->
            <b-modal v-model="notesOpen" title="Valuation Note" ok-title="Save" cancel-title="Cancel" @ok="onSaveNotes">
              <b-form-textarea
                v-model="row.notes"
                rows="6"
                placeholder="Enter detailed notes here..."
              />
            </b-modal>
          </td>

          <!-- Uploads: basic multi-file input; future enhancement could show previews/list -->
          <td style="min-width: 180px;">
            <input
              class="form-control form-control-sm"
              type="file"
              multiple
              @change="onFilesSelected"
            />
            <small class="text-muted d-block mt-1" v-if="row.files.length">
              {{ row.files.length }} file(s) selected
            </small>
          </td>

          <!-- Links: add one or more URLs (data rooms, Dropbox, etc.) -->
          <td style="min-width: 220px;">
            <div class="d-flex gap-2">
              <b-form-input
                v-model="linkInput"
                placeholder="https://..."
              />
              <b-button size="sm" variant="outline-secondary" @click="addLink">
                Add
              </b-button>
            </div>
            <ul class="list-unstyled small mt-2 mb-0" v-if="row.links.length">
              <li v-for="(lnk, idx) in row.links" :key="idx" class="text-truncate">
                <a :href="lnk" target="_blank" rel="noopener">{{ lnk }}</a>
              </li>
            </ul>
          </td>
        </tr>
      </tbody>
    </table>
    <!-- Action bar: Save button to persist values to backend (BrokerValues) -->
    <div class="d-flex justify-content-end mt-3">
      <b-button :disabled="!inviteToken || isSaving" variant="primary" size="sm" @click="handleSave">
        <span v-if="!isSaving">Save</span>
        <span v-else>Saving…</span>
      </b-button>
    </div>
    <div v-if="saveMessage" class="mt-2 small" :class="saveSuccess ? 'text-success' : 'text-danger'">
      {{ saveMessage }}
    </div>
  </b-form>
</template>

<script lang="ts">
import { defineComponent, reactive, ref, watch } from 'vue'

export default defineComponent({
  name: 'BrokerFormTable',
  props: {
    // v-model binding from parent; historically carried { name, email, firm }.
    // We keep the API to prevent breaking changes even if the new table uses
    // its own internal state for valuation inputs.
    modelValue: {
      type: Object as () => { [key: string]: any },
      required: true,
    },
    // Read-only assigned address to display in the first column
    address: {
      type: String,
      default: '',
    },
    // Invite token used to authorize public submission (required to save)
    inviteToken: {
      type: String,
      default: null,
    },
    // Linked SellerRawData id (informational; not required for submit since token binds it)
    sellerRawDataId: {
      type: [Number, String],
      default: null,
    },
    // Prefill values from backend (BrokerValues) so fields persist even if invite is used/expired
    prefillValues: {
      type: Object as () => {
        broker_asis_value?: string | number | null
        broker_arv_value?: string | number | null
        broker_rehab_est?: string | number | null
        broker_value_date?: string | null
        broker_notes?: string | null
      } | null,
      default: null,
    },
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    // row: reactive single-row state for the valuation inputs.
    const row = reactive({
      // Numeric currency-like values (store as numbers)
      asIs: undefined as number | undefined,
      arv: undefined as number | undefined,
      rehab: undefined as number | undefined,
      // Free-form note text
      notes: '' as string,
      // Selected files for upload (kept client-side for now)
      files: [] as File[],
      // List of user-provided links
      links: [] as string[],
    })

    // Controls visibility of the Notes modal
    const notesOpen = ref(false)

    // Temporary input for adding a link before pushing to row.links
    const linkInput = ref('')

    // Input display strings for currency fields (formatted with commas, no decimals)
    const asIsInput = ref('')
    const arvInput = ref('')
    const rehabInput = ref('')

    // Saving state and feedback
    const isSaving = ref(false)
    const saveMessage = ref('')
    const saveSuccess = ref<boolean | null>(null)

    // Formatter using Intl for commas; configured for no decimals
    const nf = new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 })

    // Utility: sanitize a string to digits only; returns string of digits
    const sanitizeDigits = (val: string): string => (val || '').replace(/[^0-9]/g, '')

    // Utility: format a digits-only string with commas; returns formatted string
    const formatWithCommas = (digits: string): string => {
      if (!digits) return ''
      try {
        return nf.format(Number(digits))
      } catch {
        return digits
      }
    }

    // Sync helper: set row numeric based on field and digits string
    const setRowFromDigits = (field: 'asIs' | 'arv' | 'rehab', digits: string) => {
      const num = digits ? Number(digits) : undefined
      row[field] = Number.isFinite(num as number) ? (num as number) : undefined
      emit('update:modelValue', { ...props.modelValue, valuationRow: { ...row } })
    }

    // Hydrate from backend prefill values (if provided by portal payload)
    const applyPrefill = () => {
      const v = props.prefillValues
      if (!v) return
      // As-Is
      if (v.broker_asis_value !== undefined && v.broker_asis_value !== null) {
        const d = sanitizeDigits(String(v.broker_asis_value))
        asIsInput.value = formatWithCommas(d)
        setRowFromDigits('asIs', d)
      }
      // ARV
      if (v.broker_arv_value !== undefined && v.broker_arv_value !== null) {
        const d = sanitizeDigits(String(v.broker_arv_value))
        arvInput.value = formatWithCommas(d)
        setRowFromDigits('arv', d)
      }
      // Rehab
      if (v.broker_rehab_est !== undefined && v.broker_rehab_est !== null) {
        const d = sanitizeDigits(String(v.broker_rehab_est))
        rehabInput.value = formatWithCommas(d)
        setRowFromDigits('rehab', d)
      }
      // Notes
      if (typeof v.broker_notes === 'string') {
        row.notes = v.broker_notes || ''
        emit('update:modelValue', { ...props.modelValue, valuationRow: { ...row } })
      }
    }

    // React to prefill changes (initial + subsequent)
    watch(
      () => props.prefillValues,
      () => applyPrefill(),
      { deep: true, immediate: true }
    )

    // Input handler: live-format while typing (commas). We still store numeric digits in row.
    const onCurrencyInput = (field: 'asIs' | 'arv' | 'rehab', evt: Event) => {
      const target = evt.target as HTMLInputElement
      const digits = sanitizeDigits(target.value)
      const formatted = formatWithCommas(digits)
      if (field === 'asIs') asIsInput.value = formatted
      if (field === 'arv') arvInput.value = formatted
      if (field === 'rehab') rehabInput.value = formatted
      setRowFromDigits(field, digits)
    }

    // Handler: invoked when user confirms modal (OK button)
    const onSaveNotes = () => {
      // Emit the updated form outward, merging current row state under a key
      // without mutating the incoming modelValue object (readonly).
      emit('update:modelValue', { ...props.modelValue, valuationRow: { ...row } })
    }

    // Handler: when files are selected, capture FileList into `row.files`
    const onFilesSelected = (evt: Event) => {
      const input = evt.target as HTMLInputElement
      const files = input?.files ? Array.from(input.files) : []
      row.files = files
      // Persist outward
      emit('update:modelValue', { ...props.modelValue, valuationRow: { ...row } })
    }

    // Handler: add the current linkInput to the list if valid-ish
    const addLink = () => {
      const val = (linkInput.value || '').trim()
      if (!val) return
      row.links.push(val)
      linkInput.value = ''
      // Persist outward
      emit('update:modelValue', { ...props.modelValue, valuationRow: { ...row } })
    }

    // Deep watch to persist any change in the row (address/value fields etc.)
    watch(
      () => row,
      () => {
        emit('update:modelValue', { ...props.modelValue, valuationRow: { ...row } })
      },
      { deep: true }
    )

    // Save to backend (public token submit) to persist BrokerValues
    const handleSave = async () => {
      saveMessage.value = ''
      saveSuccess.value = null
      if (!props.inviteToken) {
        saveMessage.value = 'Missing invite token; cannot save.'
        saveSuccess.value = false
        return
      }
      isSaving.value = true
      try {
        // Prepare payload: send integers (no decimals). Backend accepts Decimal and will coerce.
        const payload: Record<string, any> = {
          broker_asis_value: row.asIs ?? null,
          broker_arv_value: row.arv ?? null,
          broker_rehab_est: row.rehab ?? null,
          broker_notes: row.notes || null,
        }
        const res = await fetch(`/api/acq/broker-invites/${encodeURIComponent(props.inviteToken)}/submit/`, {
          method: 'POST',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
          },
          credentials: 'same-origin',
          body: JSON.stringify(payload),
        })
        if (!res.ok) {
          const err = await res.json().catch(() => ({}))
          throw new Error(err?.detail || 'Failed to save')
        }
        saveMessage.value = 'Saved'
        saveSuccess.value = true
      } catch (e: any) {
        saveMessage.value = e?.message || 'Save failed'
        saveSuccess.value = false
      } finally {
        isSaving.value = false
      }
    }

    return {
      row,
      notesOpen,
      linkInput,
      asIsInput,
      arvInput,
      rehabInput,
      isSaving,
      saveMessage,
      saveSuccess,
      onSaveNotes,
      onFilesSelected,
      addLink,
      onCurrencyInput,
      handleSave,
    }
  },
})
</script>

<style scoped>
/* Hide spinner arrows in number inputs within this component */
/* Chrome, Safari, Edge, Opera */
.table input[type='number']::-webkit-outer-spin-button,
.table input[type='number']::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

/* Firefox */
.table input[type='number'] {
  -moz-appearance: textfield;
  appearance: textfield; /* modern standardized property */
}
</style>
