<template>
  <!-- Asset Management: Tasking & Outcome Management -->
  <div class="px-3 px-lg-4">
    <!-- Outcomes Row: Start/ensure outcomes and render cards -->
    <b-row class="g-3 align-items-stretch mb-4">
      <b-col cols="12">
        <b-card class="w-100">
          <template #header>
            <div class="d-flex align-items-center justify-content-between w-100">
              <h5 class="mb-0 d-flex align-items-center">
                <i class="fas fa-stream me-2"></i>
                Track
              </h5>
              <div class="position-relative" ref="trackMenuRef">
                <button type="button" class="btn btn-sm btn-outline-primary px-3 d-inline-flex align-items-center justify-content-center" :disabled="!hubId || ensureBusy" @click.stop="toggleTrackMenu">
                  <span class="me-2">Select Track</span>
                  <i class="fas fa-chevron-down small"></i>
                </button>
                <!-- Custom dropdown menu with pill badges -->
                <div v-if="showTrackMenu" class="card shadow-sm mt-1" style="position: absolute; right: 0; min-width: 680px; z-index: 1060;" @click.stop>
                  <div class="card-body py-2">
                    <div class="d-flex flex-row flex-nowrap align-items-center justify-content-center gap-2 text-center">
                      <button class="btn p-0 bg-transparent border-0" @click="selectTrack('modification')" :disabled="ensureBusy">
                        <span class="badge rounded-pill text-bg-secondary px-3 py-2">Modification</span>
                      </button>
                      <button class="btn p-0 bg-transparent border-0" @click="selectTrack('short_sale')" :disabled="ensureBusy">
                        <span class="badge rounded-pill text-bg-warning px-3 py-2">Short Sale</span>
                      </button>
                      <button class="btn p-0 bg-transparent border-0" @click="selectTrack('dil')" :disabled="ensureBusy">
                        <span class="badge rounded-pill text-bg-primary px-3 py-2">Deed-in-Lieu</span>
                      </button>
                      <button class="btn p-0 bg-transparent border-0" @click="selectTrack('fc')" :disabled="ensureBusy">
                        <span class="badge rounded-pill text-bg-danger px-3 py-2">Foreclosure</span>
                      </button>
                      <button class="btn p-0 bg-transparent border-0" @click="selectTrack('reo')" :disabled="ensureBusy">
                        <span class="badge rounded-pill text-bg-info px-3 py-2">REO</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </template>

          <div class="row g-3">
            <div class="col-12 col-lg-6" v-if="visibleOutcomes.dil">
              <DilCard :hubId="hubId!" @delete="() => requestDelete('dil')" />
            </div>
            <div class="col-12 col-lg-6" v-if="visibleOutcomes.fc">
              <FcCard :hubId="hubId!" @delete="() => requestDelete('fc')" />
            </div>
            <div class="col-12 col-lg-6" v-if="visibleOutcomes.reo">
              <ReoCard :hubId="hubId!" @delete="() => requestDelete('reo')" />
            </div>
            <div class="col-12 col-lg-6" v-if="visibleOutcomes.short_sale">
              <ShortSaleCard :hubId="hubId!" @delete="() => requestDelete('short_sale')" />
            </div>
            <div class="col-12 col-lg-6" v-if="visibleOutcomes.modification">
              <ModificationCard :hubId="hubId!" @delete="() => requestDelete('modification')" />
            </div>
            <div v-if="!anyVisibleOutcome" class="col-12 small text-muted">
              Pick an outcome above and click "Start Outcome" to create its tracking card for this asset.
            </div>
          </div>
        </b-card>
      </b-col>
    </b-row>

    <!-- Confirm Delete Modal (Hyper UI style) -->
    <template v-if="confirm.open">
      <!-- Backdrop behind modal -->
      <div class="modal-backdrop fade show" style="z-index: 1050;"></div>
      <!-- Modal above backdrop -->
      <div class="modal fade show" tabindex="-1" role="dialog" aria-modal="true"
           style="display: block; position: fixed; inset: 0; z-index: 1055;">
        <div class="modal-dialog modal-dialog-centered" role="document">
          <div class="modal-content">
            <div class="modal-header bg-danger-subtle">
              <h5 class="modal-title d-flex align-items-center">
                <i class="fas fa-triangle-exclamation text-danger me-2"></i>
                Confirm Deletion
              </h5>
              <button type="button" class="btn-close" aria-label="Close" @click="closeConfirm"></button>
            </div>
            <div class="modal-body">
              <p class="mb-0">Are you sure you want to delete this outcome record? This action cannot be undone.</p>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-light" @click="closeConfirm">Cancel</button>
              <button type="button" class="btn btn-danger" @click="confirmDelete" :disabled="confirm.busy">
                <span v-if="confirm.busy" class="spinner-border spinner-border-sm me-2"></span>
                Delete
              </button>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Include the full tasking interface -->
    <AmLlTasking :assetId="amId" :row="props.row" />
    
    <!-- Servicing Notes Section -->
    <b-row class="g-3 align-items-stretch mt-4">
      <b-col lg="12" class="d-flex">
        <b-card class="w-100">
          <template #header>
            <h5 class="mb-0">
              <i class="fas fa-sticky-note me-2"></i>
              Servicing Notes
            </h5>
          </template>
          <Notes :assetId="amId || undefined" class="w-100" />
        </b-card>
      </b-col>
    </b-row>
  </div>
  
</template>

<script setup lang="ts">
import { withDefaults, defineProps, ref, computed, onMounted, watch, onBeforeUnmount } from 'vue'
import Notes from '@/components/Notes.vue'
import AmLlTasking from '@/views/am_module/loanlvl/am_tasking/am_ll_tasking.vue'
import DilCard from '@/views/am_module/outcomes/DilCard.vue'
import FcCard from '@/views/am_module/outcomes/FcCard.vue'
import ReoCard from '@/views/am_module/outcomes/ReoCard.vue'
import ShortSaleCard from '@/views/am_module/outcomes/ShortSaleCard.vue'
import ModificationCard from '@/views/am_module/outcomes/ModificationCard.vue'
import { useAmOutcomesStore, type OutcomeType } from '@/stores/outcomes'

const props = withDefaults(defineProps<{ row?: Record<string, any> | null; productId?: string | number | null }>(), {
  row: null,
  productId: null,
})

// Resolve AM asset id to hit backend endpoints
const amId = computed<number | null>(() => {
  if (props.productId != null && props.productId !== '') return Number(props.productId)
  const rid = props.row && (props.row as any).id
  return rid != null ? Number(rid) : null
})

// Resolve hub id for outcome APIs from the row payload (AssetDetailSerializer exposes asset_hub_id)
const hubId = computed<number | null>(() => {
  const raw = props.row && (props.row as any).asset_hub_id
  return raw != null ? Number(raw) : null
})

// Outcomes store helpers
const outcomes = useAmOutcomesStore()
const ensureBusy = ref(false)
const selectedOutcome = ref<OutcomeType | ''>('')
const showTrackMenu = ref(false)
const trackMenuRef = ref<HTMLElement | null>(null)
const visibleOutcomes = ref<Record<OutcomeType, boolean>>({ dil: false, fc: false, reo: false, short_sale: false, modification: false })
const anyVisibleOutcome = computed(() => Object.values(visibleOutcomes.value).some(Boolean))

function toggleTrackMenu() {
  showTrackMenu.value = !showTrackMenu.value
}
async function selectTrack(type: OutcomeType) {
  if (!hubId.value) return
  try {
    ensureBusy.value = true
    selectedOutcome.value = type
    await outcomes.ensureOutcome(hubId.value, type)
    visibleOutcomes.value[type] = true
  } finally {
    ensureBusy.value = false
    showTrackMenu.value = false
  }
}

// Close menu on outside click
function handleDocClick(e: MouseEvent) {
  const target = e.target as Node
  const root = trackMenuRef.value
  if (!root) return
  if (showTrackMenu.value && !root.contains(target)) {
    showTrackMenu.value = false
  }
}
onMounted(() => document.addEventListener('click', handleDocClick))
onBeforeUnmount(() => document.removeEventListener('click', handleDocClick))

// Confirm delete modal state
const confirm = ref<{ open: boolean; type: OutcomeType | null; busy: boolean }>({ open: false, type: null, busy: false })

function requestDelete(type: OutcomeType) {
  confirm.value = { open: true, type, busy: false }
}
function closeConfirm() {
  confirm.value.open = false
}
async function confirmDelete() {
  if (!hubId.value || !confirm.value.type) return
  try {
    confirm.value.busy = true
    await outcomes.deleteOutcome(hubId.value, confirm.value.type)
    visibleOutcomes.value[confirm.value.type] = false
    closeConfirm()
  } finally {
    confirm.value.busy = false
  }
}

onMounted(async () => {
  await refreshVisible()
})

// When hub changes (navigating to another asset), rehydrate visible cards
watch(hubId, async () => {
  await refreshVisible()
})

async function refreshVisible() {
  // Reset visibility
  visibleOutcomes.value = { dil: false, fc: false, reo: false, short_sale: false, modification: false }
  const id = hubId.value
  if (!id) return
  // Check each outcome existence via backend
  const types: OutcomeType[] = ['dil', 'fc', 'reo', 'short_sale', 'modification']
  for (const t of types) {
    const exists = await outcomes.fetchOutcome(id, t)
    if (exists) visibleOutcomes.value[t] = true
  }
}

</script>

<style scoped>
.note-body :deep(p) { margin-bottom: 0.5rem; }
.note-body :deep(h1), .note-body :deep(h2) { margin: 0.25rem 0; font-size: 1.1rem; }
.notes-list { font-size: 0.875rem; }
.note-item { padding: 0.5rem 0.75rem; }
.note-item .meta { font-size: 0.78rem; }
.note-body { line-height: 1.2; }
.note-body :deep(p:last-child) { margin-bottom: 0; }
.note-body :deep(img),
.note-body :deep(video),
.note-body :deep(iframe) { max-width: 100%; height: auto; display: block; }
</style>
