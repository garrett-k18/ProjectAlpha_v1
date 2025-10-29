<template>
  <!-- Per-row invite checkbox. Disabled until an agent is selected for the row. -->
  <div class="invite-cell d-flex w-100 h-100 align-items-center justify-content-center gap-1">
    <input
      class="form-check-input m-0 border-2 border-dark"
      type="checkbox"
      :checked="isChecked"
      :disabled="!canAssign || loading || isChecked"
      @change="onToggle"
      :aria-label="`Create invite for row ${rowKey}`"
      :title="isChecked ? 'Invite created' : 'Create invite'"
    />

    <!-- Tiny spinner while creating -->
    <b-spinner v-if="loading" small variant="primary" label="Saving..."></b-spinner>

    <!-- Success check icon -->
    <i v-if="isChecked" class="mdi mdi-check-circle text-success" title="Invite created"></i>
  </div>
  
</template>

<script setup lang="ts">
import type { ICellRendererParams } from 'ag-grid-community'
import { computed, ref } from 'vue'
import { BSpinner } from 'bootstrap-vue-next'

const props = defineProps<{
  params: ICellRendererParams & {
    onAssign?: (row: any) => Promise<boolean>
    canAssign?: (row: any) => boolean
    isInvited?: (row: any) => boolean
  }
}>()

const loading = ref(false)
const done = ref(false)

const rowKey = computed(() => props.params?.node?.id)

const canAssign = computed<boolean>(() => {
  try {
    return typeof props.params?.canAssign === 'function'
      ? !!props.params.canAssign(props.params.data)
      : true
  } catch {
    return true
  }
})

// Whether parent indicates this row is already invited
const alreadyInvited = computed<boolean>(() => {
  try {
    return typeof props.params?.isInvited === 'function'
      ? !!props.params.isInvited(props.params.data)
      : false
  } catch {
    return false
  }
})

// The visual checked state: true if either we just completed or parent says invited
const isChecked = computed<boolean>(() => done.value || alreadyInvited.value)

async function onToggle(e: Event) {
  const input = e.target as HTMLInputElement
  if (!input?.checked) return // ignore uncheck
  if (isChecked.value || loading.value) return
  loading.value = true
  try {
    const ok = typeof props.params?.onAssign === 'function'
      ? await props.params.onAssign(props.params.data)
      : false
    if (ok) {
      done.value = true
    } else {
      input.checked = false
    }
  } catch (err) {
    input.checked = false
    console.error('[AssignInviteCell] failed to assign invite', err)
    alert('Failed to create invite for this row.')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* Ensure the cell wrapper fills the AG Grid cell for proper centering */
.invite-cell {
  width: 100%;
  height: 100%;
}

/* Center the inner form-check wrapper if present (BFormCheckbox case) */
.invite-cell :deep(.form-check) {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Make checkbox border bolder and darker (covers both raw input and form-check input) */
.invite-cell :deep(.form-check-input),
.invite-cell input[type="checkbox"] {
  border-width: 2px !important;
  border-color: var(--bs-dark, #212529) !important;
}
</style>
