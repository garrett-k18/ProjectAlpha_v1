<template>
  <Layout>
    <Breadcrumb :title="displayTitle" :items="items"/>
    <ProductDetailsContent :row="row" :product-id="productId" />

  </Layout>
</template>

<script setup lang="ts">
// Import layout and shared components used in this view
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";
import ProductDetailsContent from '@/views/loanlvl/components/ProductDetailsContent.vue'

// Import Vue Composition API utilities
import { ref, computed, toRef } from 'vue'

// Type describing a breadcrumb item consumed by `Breadcrumb`
type BreadcrumbItem = {
  text: string
  href?: string
  to?: string
  active?: boolean
}

// Define strongly-typed props for this view
const props = defineProps<{
  // Optional row object passed from a parent grid/list
  row: Record<string, any> | null
  // Explicit product/asset identifier to show in the header
  productId: string | number | null
}>()

// Reactive page title text
const title = ref<string>('Asset Details')

// Reactive breadcrumb items shown beneath the main layout header
const items = ref<BreadcrumbItem[]>([
  { text: 'Hyper', href: '/' },
  { text: 'Acquisitions Dashboard', to: '/acquisitions' },
  { text: 'Asset Details', active: true },
])

// Create reactive references to incoming props for template usage
const productId = toRef(props, 'productId')
const row = toRef(props, 'row')

// Compute the display title. If an id is provided, append it; otherwise fallback to the base title
const displayTitle = computed<string>(() => {
  return productId.value != null && productId.value !== ''
    ? `Asset Details — ${productId.value}`
    : title.value
})
</script>
