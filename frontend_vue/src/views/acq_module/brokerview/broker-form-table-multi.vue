<template>
  <!--
    BrokerFormTableMulti
    Renders the Assigned Valuations table with one row per active invite (loan).

    Columns:
      - Address
      - As-Is Value
      - After Repair Value
      - Estimated Rehab
      - Notes (opens modal)
      - Uploads (photos/documents)
      - Links (data rooms / Dropbox, etc.)

    Implementation notes:
      - Accepts `rows` prop: an array of normalized entries from the portal payload.
      - Each row tracks its own state and auto-saves independently using its invite token.
      - Emits `saved` after a successful save of any row so parent can refresh portal data.
      - Uses BootstrapVue Next components already present in the app. Can be restyled with Hyper UI.
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
          <th class="text-nowrap">Photos</th>
          <th class="text-nowrap">Documents</th>
          <th class="text-nowrap">Links</th>
          <th class="text-nowrap" style="width:140px">Status</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(entry, idx) in normalizedRows" :key="entry.key">
          <!-- Address: static display from prop (read-only) -->
          <td style="min-width: 220px;">
            <span class="d-inline-block text-truncate" style="max-width: 360px;" :title="entry.address">
              {{ entry.address || '—' }}
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
                v-model="asIsInput[idx]"
                @update:modelValue="onCurrencyModel(idx, 'asIs', $event)"
                placeholder="0"
                :disabled="!entry.inviteToken || photoUploadStatus[idx] === 'uploading'"
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
                v-model="arvInput[idx]"
                @update:modelValue="onCurrencyModel(idx, 'arv', $event)"
                placeholder="0"
                :disabled="!entry.inviteToken || photoUploadStatus[idx] === 'uploading'"
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
                v-model="rehabInput[idx]"
                @update:modelValue="onCurrencyModel(idx, 'rehab', $event)"
                placeholder="0"
                :disabled="!entry.inviteToken || photoUploadStatus[idx] === 'uploading'"
              />
            </div>
          </td>

          <!-- Notes: opens a modal to enter a free-form note -->
          <td style="min-width: 140px;">
            <b-button size="sm" variant="primary" @click="openNotes(idx)" :disabled="!entry.inviteToken || photoUploadStatus[idx] === 'uploading'">
              <i class="mdi mdi-note-text-outline me-1"></i>
              Add Note
            </b-button>
            <!-- Notes modal per row -->
            <b-modal
              v-model="notesOpen[idx]"
              title="Valuation Note"
              ok-title="Save"
              cancel-title="Cancel"
              @ok="onSaveNotes(idx)"
            >
              <b-form-textarea
                v-model="rowsState[idx].notes"
                rows="6"
                placeholder="Enter detailed notes here..."
              />
            </b-modal>
          </td>

          <!-- Photos: multi-file image input (BrokerPhoto model) -->
          <td style="min-width: 180px;">
            <input
              class="form-control form-control-sm"
              type="file"
              accept="image/*"
              multiple
              @change="onPhotoSelected(idx, $event)"
              :disabled="!entry.inviteToken || photoUploadStatus[idx] === 'uploading'"
            />
            <small class="text-muted d-block mt-1" v-if="rowsState[idx].photoFiles.length">
              {{ rowsState[idx].photoFiles.length }} photo(s) selected
            </small>
            <div class="mt-1" v-if="photoUploadStatus[idx] !== 'idle'">
              <b-progress
                v-if="photoUploadStatus[idx] === 'uploading'"
                :value="photoUploadProgress[idx]"
                :max="100"
                height="6px"
              />
              <small v-if="photoUploadStatus[idx] === 'uploading'" class="text-muted">
                Uploading {{ photoUploadProgress[idx] }}%
              </small>
              <small v-else-if="photoUploadStatus[idx] === 'uploaded'" class="text-success">
                {{ photoUploadMessage[idx] || 'Photos uploaded' }}
              </small>
              <small v-else-if="photoUploadStatus[idx] === 'error'" class="text-danger">
                {{ photoUploadMessage[idx] || 'Upload failed' }}
              </small>
            </div>
          </td>

          <!-- Documents: multi-file input for non-image docs -->
          <td style="min-width: 180px;">
            <input
              class="form-control form-control-sm"
              type="file"
              multiple
              @change="onDocsSelected(idx, $event)"
              :disabled="!entry.inviteToken || photoUploadStatus[idx] === 'uploading'"
            />
            <small class="text-muted d-block mt-1" v-if="rowsState[idx].docFiles.length">
              {{ rowsState[idx].docFiles.length }} document(s) selected
            </small>
          </td>

          <!-- Links: add one or more URLs (data rooms, Dropbox, etc.) -->
          <td style="min-width: 220px;">
            <div class="d-flex gap-2">
              <b-form-input
                v-model="linkInput[idx]"
                placeholder="https://..."
                :disabled="!entry.inviteToken || photoUploadStatus[idx] === 'uploading'"
              />
              <b-button size="sm" variant="outline-secondary" @click="addLink(idx)" :disabled="!entry.inviteToken || photoUploadStatus[idx] === 'uploading'">
                Add
              </b-button>
            </div>
            <ul class="list-unstyled small mt-2 mb-0" v-if="rowsState[idx].links.length">
              <li v-for="(lnk, j) in rowsState[idx].links" :key="j" class="text-truncate">
                <a :href="lnk" target="_blank" rel="noopener">{{ lnk }}</a>
              </li>
            </ul>
          </td>

          <!-- Auto-save status per row -->
          <td class="text-end">
            <small v-if="!entry.inviteToken" class="text-muted">No active token</small>
            <small v-else-if="autoSaveStatus[idx] === 'saving'" class="text-muted">Saving…</small>
            <small v-else-if="autoSaveStatus[idx] === 'saved'" class="text-success">Saved</small>
            <small v-else-if="autoSaveStatus[idx] === 'error'" class="text-danger">{{ saveMessage[idx] || 'Save failed' }}</small>
            <small v-else class="text-muted">Idle</small>
          </td>
        </tr>
      </tbody>
    </table>
  </b-form>
</template>

<script lang="ts">
import { defineComponent, ref, watch } from 'vue'
import type { PropType } from 'vue'
import axios from 'axios'
import type { AxiosProgressEvent } from 'axios'

// Row entry provided by parent. Normalized structure used by this component.
export interface BrokerFormEntry {
  key: string // unique key per row (e.g., `${srdId}:${token}`)
  srdId: number | null
  inviteToken: string | null // null when not active; component disables saving
  address: string
  prefillValues: {
    broker_asis_value?: string | number | null
    broker_arv_value?: string | number | null
    broker_rehab_est?: string | number | null
    broker_value_date?: string | null
    broker_notes?: string | null
  } | null
}

export default defineComponent({
  name: 'BrokerFormTableMulti',
  props: {
    // v-model support for parent (kept for compatibility)
    modelValue: {
      type: Object as () => { [key: string]: any },
      required: true,
    },
    // Array of normalized entries to render as rows
    rows: {
      type: Array as PropType<BrokerFormEntry[]>,
      default: () => [],
    },
  },
  emits: ['update:modelValue', 'saved'],
  setup(props, { emit }) {
    // Reactive per-row state for valuation inputs
    const rowsState = ref(
      props.rows.map(() => ({
        asIs: undefined as number | undefined,
        arv: undefined as number | undefined,
        rehab: undefined as number | undefined,
        notes: '' as string,
        photoFiles: [] as File[],
        docFiles: [] as File[],
        links: [] as string[],
      }))
    )

    // UI helpers per row
    const notesOpen = ref<boolean[]>(props.rows.map(() => false))
    const linkInput = ref<string[]>(props.rows.map(() => ''))
    const asIsInput = ref<string[]>(props.rows.map(() => ''))
    const arvInput = ref<string[]>(props.rows.map(() => ''))
    const rehabInput = ref<string[]>(props.rows.map(() => ''))

    // Per-row save state
    const isSaving = ref<boolean[]>(props.rows.map(() => false))
    const saveMessage = ref<string[]>(props.rows.map(() => ''))
    const autoSaveStatus = ref<Array<'idle' | 'saving' | 'saved' | 'error'>>(
      props.rows.map(() => 'idle')
    )

    // Per-row photo upload UI state
    // photoUploadStatus: tracks current upload state for each row
    // photoUploadMessage: captures last success/error message for each row
    // photoUploadProgress: 0-100 integer progress for active upload
    const photoUploadStatus = ref<Array<'idle' | 'uploading' | 'uploaded' | 'error'>>(
      props.rows.map(() => 'idle')
    )
    const photoUploadMessage = ref<string[]>(props.rows.map(() => ''))
    const photoUploadProgress = ref<number[]>(props.rows.map(() => 0))

    // Debounce timers per row index
    const timers: Record<number, any> = {}

    // Number formatter
    const nf = new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 })

    // Normalize incoming rows for template
    const normalizedRows = ref<BrokerFormEntry[]>(props.rows)

    // Helper: sanitize a string to digits only
    const sanitizeDigits = (val: string): string => (val || '').replace(/[^0-9]/g, '')

    // Helper: format digits with commas
    const formatWithCommas = (digits: string): string => {
      if (!digits) return ''
      try { return nf.format(Number(digits)) } catch { return digits }
    }

    // Helper: normalize numeric-ish to whole-dollar number
    const toWhole = (val: string | number | null | undefined): number | null => {
      if (val === null || val === undefined) return null
      const raw = String(val).replace(/,/g, '')
      const num = Number(raw)
      if (!Number.isFinite(num)) return null
      return Math.round(num)
    }

    // Set numeric from digits for a row and emit model update
    const setRowFromDigits = (idx: number, field: 'asIs' | 'arv' | 'rehab', digits: string) => {
      const num = digits ? Number(digits) : undefined
      rowsState.value[idx][field] = Number.isFinite(num as number) ? (num as number) : undefined
      emit('update:modelValue', { ...props.modelValue, valuationRows: [...rowsState.value] })
    }

    // Hydrate from prefill values for each row
    const applyPrefillAll = () => {
      normalizedRows.value.forEach((entry, idx) => {
        const v = entry.prefillValues
        if (!v) return
        // As-Is
        if (v.broker_asis_value !== undefined && v.broker_asis_value !== null) {
          const whole = toWhole(v.broker_asis_value)
          const d = whole !== null ? String(whole) : ''
          asIsInput.value[idx] = formatWithCommas(d)
          setRowFromDigits(idx, 'asIs', d)
        }
        // ARV
        if (v.broker_arv_value !== undefined && v.broker_arv_value !== null) {
          const whole = toWhole(v.broker_arv_value)
          const d = whole !== null ? String(whole) : ''
          arvInput.value[idx] = formatWithCommas(d)
          setRowFromDigits(idx, 'arv', d)
        }
        // Rehab
        if (v.broker_rehab_est !== undefined && v.broker_rehab_est !== null) {
          const whole = toWhole(v.broker_rehab_est)
          const d = whole !== null ? String(whole) : ''
          rehabInput.value[idx] = formatWithCommas(d)
          setRowFromDigits(idx, 'rehab', d)
        }
        // Notes
        if (typeof v.broker_notes === 'string') {
          rowsState.value[idx].notes = v.broker_notes || ''
          emit('update:modelValue', { ...props.modelValue, valuationRows: [...rowsState.value] })
        }
      })
    }

    // Initialize prefill on mount
    applyPrefillAll()

    // React to changes in `rows` length/contents
    watch(
      () => props.rows,
      (newRows) => {
        normalizedRows.value = newRows || []
        // Resize per-row arrays to match new rows
        const n = normalizedRows.value.length
        rowsState.value = Array.from({ length: n }, (_, i) => rowsState.value[i] || {
          asIs: undefined,
          arv: undefined,
          rehab: undefined,
          notes: '',
          photoFiles: [],
          docFiles: [],
          links: [],
        })
        notesOpen.value = Array.from({ length: n }, (_, i) => notesOpen.value[i] || false)
        linkInput.value = Array.from({ length: n }, (_, i) => linkInput.value[i] || '')
        asIsInput.value = Array.from({ length: n }, (_, i) => asIsInput.value[i] || '')
        arvInput.value = Array.from({ length: n }, (_, i) => arvInput.value[i] || '')
        rehabInput.value = Array.from({ length: n }, (_, i) => rehabInput.value[i] || '')
        isSaving.value = Array.from({ length: n }, (_, i) => isSaving.value[i] || false)
        saveMessage.value = Array.from({ length: n }, (_, i) => saveMessage.value[i] || '')
        autoSaveStatus.value = Array.from({ length: n }, (_, i) => autoSaveStatus.value[i] || 'idle')
        photoUploadStatus.value = Array.from({ length: n }, (_, i) => photoUploadStatus.value[i] || 'idle')
        photoUploadMessage.value = Array.from({ length: n }, (_, i) => photoUploadMessage.value[i] || '')
        photoUploadProgress.value = Array.from({ length: n }, (_, i) => photoUploadProgress.value[i] || 0)
        // Re-apply prefill for any new rows
        applyPrefillAll()
      },
      { deep: true }
    )

    // Input formatter handler
    const onCurrencyModel = (idx: number, field: 'asIs' | 'arv' | 'rehab', val: string) => {
      const digits = sanitizeDigits(val || '')
      const formatted = formatWithCommas(digits)
      if (field === 'asIs') asIsInput.value[idx] = formatted
      if (field === 'arv') arvInput.value[idx] = formatted
      if (field === 'rehab') rehabInput.value[idx] = formatted
      setRowFromDigits(idx, field, digits)
      scheduleAutoSave(idx)
    }

    // Notes modal open
    const openNotes = (idx: number) => { notesOpen.value[idx] = true }

    // Save notes on modal OK
    const onSaveNotes = (idx: number) => {
      emit('update:modelValue', { ...props.modelValue, valuationRows: [...rowsState.value] })
      scheduleAutoSave(idx)
    }

    // File selection handlers
    const onPhotoSelected = (idx: number, evt: Event) => {
      const input = evt.target as HTMLInputElement
      const files = input?.files ? Array.from(input.files) : []
      rowsState.value[idx].photoFiles = files
      emit('update:modelValue', { ...props.modelValue, valuationRows: [...rowsState.value] })
      // Immediately upload selected photos for this row using the invite token
      if (files && files.length) {
        uploadPhotosForRow(idx)
      }
    }

    const onDocsSelected = (idx: number, evt: Event) => {
      const input = evt.target as HTMLInputElement
      const files = input?.files ? Array.from(input.files) : []
      rowsState.value[idx].docFiles = files
      emit('update:modelValue', { ...props.modelValue, valuationRows: [...rowsState.value] })
    }

    // Upload selected photos for a row to the backend token-based endpoint
    // Uses axios with onUploadProgress to report progress. Backend expects multipart
    // form field name 'files' (alias 'photos' or 'image' also accepted per backend docs).
    const uploadPhotosForRow = async (idx: number) => {
      const token = normalizedRows.value[idx]?.inviteToken
      const files = rowsState.value[idx].photoFiles || []
      if (!token || !files.length) return

      // Initialize UI state for upload
      photoUploadStatus.value[idx] = 'uploading'
      photoUploadMessage.value[idx] = ''
      photoUploadProgress.value[idx] = 0

      try {
        const form = new FormData()
        for (const f of files) {
          // Append under canonical key 'files' (backend also supports 'photos'/'image')
          form.append('files', f)
        }

        const res = await axios.post(
          `/api/acq/broker-invites/${encodeURIComponent(token)}/photos/`,
          form,
          {
            headers: {
              // Let the browser set Content-Type with boundary; only declare Accept
              'Accept': 'application/json',
            },
            // Report upload progress for user feedback
            onUploadProgress: (evt: AxiosProgressEvent) => {
              if (typeof evt.total === 'number' && typeof evt.loaded === 'number' && evt.total > 0) {
                photoUploadProgress.value[idx] = Math.round((evt.loaded / evt.total) * 100)
              }
            },
            withCredentials: false,
          }
        )

        // Success: clear selected files, show message, and notify parent to refresh data
        const uploaded = Number((res?.data && (res.data.uploaded as any)) || files.length)
        rowsState.value[idx].photoFiles = []
        photoUploadStatus.value[idx] = 'uploaded'
        photoUploadMessage.value[idx] = `${uploaded} photo(s) uploaded`
        photoUploadProgress.value[idx] = 100
        emit('saved')
      } catch (e: any) {
        // Error: capture message and allow retry by re-selecting files
        photoUploadStatus.value[idx] = 'error'
        photoUploadMessage.value[idx] = e?.message || 'Upload failed'
      } finally {
        // No additional cleanup; keep progress bar at 100 on success briefly
        // Caller may trigger another selection to re-upload
      }
    }

    // Add link
    const addLink = (idx: number) => {
      const val = (linkInput.value[idx] || '').trim()
      if (!val) return
      rowsState.value[idx].links.push(val)
      linkInput.value[idx] = ''
      emit('update:modelValue', { ...props.modelValue, valuationRows: [...rowsState.value] })
    }

    // Debounced auto-save per row
    const scheduleAutoSave = (idx: number) => {
      const token = normalizedRows.value[idx]?.inviteToken
      if (!token) return
      autoSaveStatus.value[idx] = 'saving'
      if (timers[idx]) clearTimeout(timers[idx])
      timers[idx] = setTimeout(() => submitNow(idx), 600)
    }

    // Immediate submit for a single row
    const submitNow = async (idx: number) => {
      const token = normalizedRows.value[idx]?.inviteToken
      if (!token) { autoSaveStatus.value[idx] = 'idle'; return }
      saveMessage.value[idx] = ''
      isSaving.value[idx] = true
      autoSaveStatus.value[idx] = 'saving'
      try {
        const payload: Record<string, any> = {
          broker_asis_value: rowsState.value[idx].asIs ?? null,
          broker_arv_value: rowsState.value[idx].arv ?? null,
          broker_rehab_est: rowsState.value[idx].rehab ?? null,
          broker_notes: rowsState.value[idx].notes || null,
        }
        const res = await fetch(`/api/acq/broker-invites/${encodeURIComponent(token)}/submit/`, {
          method: 'POST',
          headers: { 'Accept': 'application/json', 'Content-Type': 'application/json' },
          credentials: 'same-origin',
          body: JSON.stringify(payload),
        })
        if (!res.ok) {
          const err = await res.json().catch(() => ({}))
          throw new Error(err?.detail || 'Failed to save')
        }
        autoSaveStatus.value[idx] = 'saved'
        saveMessage.value[idx] = ''
        // Notify parent so it can refresh portal payload if needed
        emit('saved')
      } catch (e: any) {
        autoSaveStatus.value[idx] = 'error'
        saveMessage.value[idx] = e?.message || 'Save failed'
      } finally {
        isSaving.value[idx] = false
      }
    }

    return {
      normalizedRows,
      rowsState,
      notesOpen,
      linkInput,
      asIsInput,
      arvInput,
      rehabInput,
      isSaving,
      saveMessage,
      autoSaveStatus,
      photoUploadStatus,
      photoUploadMessage,
      photoUploadProgress,
      onCurrencyModel,
      openNotes,
      onSaveNotes,
      onPhotoSelected,
      onDocsSelected,
      uploadPhotosForRow,
      addLink,
      scheduleAutoSave,
      submitNow,
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
