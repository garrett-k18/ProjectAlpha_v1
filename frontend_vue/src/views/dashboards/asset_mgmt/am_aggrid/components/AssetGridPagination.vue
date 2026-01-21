<template>
  <div class="d-flex justify-content-end align-items-center gap-2 mt-2">
    <label for="pageSizeSelect" class="small mb-0">Rows</label>
    <select
      id="pageSizeSelect"
      class="form-select form-select-sm"
      v-model="pageSizeModel"
      @change="handlePageSizeChange"
      autocomplete="off"
      style="width: auto;"
    >
      <option :value="50">50</option>
      <option :value="100">100</option>
      <option :value="200">200</option>
      <option :value="500">500</option>
      <option value="ALL">All</option>
    </select>

    <div class="d-flex align-items-center gap-1" v-if="!viewAll">
      <button
        class="btn btn-sm btn-light"
        :disabled="!canGoToPrev || loading"
        @click="handlePrevPage"
        title="Prev"
      >
        ‹
      </button>
      <span class="small">Page {{ page }} / {{ totalPages || 1 }}</span>
      <button
        class="btn btn-sm btn-light"
        :disabled="!canGoToNext || loading"
        @click="handleNextPage"
        title="Next"
      >
        ›
      </button>
    </div>

    <div class="small" v-if="totalCount !== null">
      Total: <strong>{{ totalCount }}</strong>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  page: number
  pageSize: number
  pageSizeSelection: number | 'ALL'
  viewAll: boolean
  totalCount: number | null
  totalPages: number | null
  loading: boolean
  canGoToPrev: boolean
  canGoToNext: boolean
}>()

const emit = defineEmits<{
  'update:pageSizeSelection': [value: number | 'ALL']
  'pageSizeChange': []
  'prevPage': []
  'nextPage': []
}>()

const pageSizeModel = computed({
  get: () => props.pageSizeSelection,
  set: (val) => emit('update:pageSizeSelection', val),
})

function handlePageSizeChange(): void {
  emit('pageSizeChange')
}

function handlePrevPage(): void {
  emit('prevPage')
}

function handleNextPage(): void {
  emit('nextPage')
}
</script>

<style scoped>
/* Inherits parent styles */
</style>
