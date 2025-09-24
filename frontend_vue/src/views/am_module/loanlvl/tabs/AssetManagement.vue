<template>
  <!-- Asset Management: Tasking & Outcome Management -->
  <div class="px-3 px-lg-4">
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
import { withDefaults, defineProps, ref, computed } from 'vue'
import Notes from '@/components/Notes.vue'
import AmLlTasking from '@/views/am_module/loanlvl/am_tasking/am_ll_tasking.vue'

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
