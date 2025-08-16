<template>
  <Layout>
    <Breadcrumb :title="displayTitle" :items="items"/>
    <ProductDetailsContent :row="row" :product-id="productId" />

  </Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";
import { PropType } from 'vue'
import ProductDetailsContent from '@/views/loanlvl/components/ProductDetailsContent.vue'

export default {
  components: {Breadcrumb, Layout, ProductDetailsContent},
  // Optional props allow embedding this view inside a modal with context from a grid row
  props: {
    row: {
      type: Object as PropType<Record<string, any> | null>,
      default: null,
    },
    productId: {
      type: [String, Number] as PropType<string | number | null>,
      default: null,
    },
  },
  data() {
    return {
      title: 'Product Details',
      items: [
        {
          text: 'Hyper',
          href: '/',
        },
        {
          text: 'Acquisitions Dashboard',
          to: '/acquisitions',
        },
        {
          text: 'Product Details',
          active: true,
        },
      ],
    }
  },
  computed: {
    // Prefer explicit productId when provided; fallback to default title
    displayTitle(): string {
      // Note: using an em dash for stylistic consistency in Hyper UI headings
      return this.productId != null && this.productId !== ''
        ? `Product Details — ${this.productId}`
        : this.title
    },
  },
}
</script>
