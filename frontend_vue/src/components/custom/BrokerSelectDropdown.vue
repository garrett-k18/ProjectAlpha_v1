<template>
  <!-- WHAT: Custom dropdown for selecting a broker with rich two-line display -->
  <!-- WHY: Native <select> cannot render multi-line labels or MSA badges -->
  <div class="broker-select-dropdown position-relative" ref="rootEl">
    <!-- Control button styled like a form-select -->
    <button
      type="button"
      class="form-select form-select-sm text-start broker-select-control"
      :class="{ 'broker-select-disabled': disabled }"
      :disabled="disabled"
      @click="toggleOpen"
    >
      <div class="d-flex flex-column">
        <div class="fw-semibold text-truncate">
          {{ selectedBroker ? formatNameFirm(selectedBroker) : placeholder }}
        </div>
        <div
          v-if="selectedBroker && getBrokerMsas(selectedBroker).length"
          class="small text-muted mt-1 broker-select-msas"
        >
          <span
            v-for="msa in getVisibleMsas(selectedBroker)"
            :key="msa"
            class="badge bg-light text-dark border me-1"
          >
            {{ msa }}
          </span>
          <span
            v-if="getExtraCount(selectedBroker) > 0"
            class="badge bg-light text-dark border"
          >
            +{{ getExtraCount(selectedBroker) }} more
          </span>
        </div>
      </div>
    </button>

    <!-- Dropdown menu -->
    <div
      v-if="open && !disabled"
      class="dropdown-menu show w-100 shadow-sm broker-select-menu"
    >
      <button
        type="button"
        class="dropdown-item small text-muted"
        @click.stop="selectBroker(null)"
      >
        {{ placeholder }}
      </button>

      <div
        v-if="!brokers || !brokers.length"
        class="dropdown-item text-muted small"
      >
        No brokers available
      </div>

      <button
        v-for="broker in brokers"
        :key="broker.id"
        type="button"
        class="dropdown-item py-2 broker-option"
        @click.stop="selectBroker(broker.id)"
      >
        <div class="fw-semibold text-truncate">
          {{ formatNameFirm(broker) }}
        </div>
        <div
          v-if="getBrokerMsas(broker).length"
          class="small text-muted mt-1"
        >
          <span
            v-for="msa in getVisibleMsas(broker)"
            :key="msa"
            class="badge bg-light text-dark border me-1"
          >
            {{ msa }}
          </span>
          <span
            v-if="getExtraCount(broker) > 0"
            class="badge bg-light text-dark border"
          >
            +{{ getExtraCount(broker) }} more
          </span>
        </div>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onBeforeUnmount } from 'vue'
import type { BrokerCrmItem } from '@/stores/brokerscrm'

const props = defineProps<{
  modelValue: number | null
  brokers: BrokerCrmItem[]
  disabled?: boolean
  placeholder?: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: number | null): void
}>()

const open = ref(false)
const rootEl = ref<HTMLElement | null>(null)

const placeholder = computed(() => props.placeholder ?? 'Assign broker...')

const selectedBroker = computed<BrokerCrmItem | null>(() => {
  if (!props.brokers || props.modelValue == null) return null
  return props.brokers.find((b) => b.id === props.modelValue) || null
})

function toggleOpen() {
  if (props.disabled) return
  open.value = !open.value
}

function selectBroker(id: number | null) {
  if (props.disabled) return
  emit('update:modelValue', id)
  open.value = false
}

function formatNameFirm(broker: BrokerCrmItem): string {
  const name = broker.name || broker.contact_name || null
  const firm = broker.firm || broker.firm_ref?.name || null
  if (name && firm) return `${name} - ${firm}`
  if (name) return name
  if (firm) return firm
  return `Broker ${broker.id}`
}

function getBrokerMsas(broker: BrokerCrmItem): string[] {
  if (Array.isArray(broker.msas) && broker.msas.length) {
    return broker.msas.filter((m) => !!m).map((m) => String(m))
  }
  if (Array.isArray(broker.msa_assignments) && broker.msa_assignments.length) {
    return broker.msa_assignments
      .map((a) => a?.msa_name)
      .filter((m): m is string => !!m)
      .map((m) => String(m))
  }
  return []
}

function getVisibleMsas(broker: BrokerCrmItem): string[] {
  const unique = Array.from(new Set(getBrokerMsas(broker)))
  return unique.slice(0, 3)
}

function getExtraCount(broker: BrokerCrmItem): number {
  const unique = Array.from(new Set(getBrokerMsas(broker)))
  return Math.max(0, unique.length - 3)
}

function handleClickOutside(event: MouseEvent) {
  const root = rootEl.value
  if (!root) return
  if (!root.contains(event.target as Node)) {
    open.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.broker-select-control {
  cursor: pointer;
}

.broker-select-disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.broker-select-menu {
  max-height: 320px;
  overflow-y: auto;
  z-index: 1050;
}

.broker-option {
  white-space: normal;
}

.broker-select-msas .badge {
  font-size: 0.7rem;
}
</style>
