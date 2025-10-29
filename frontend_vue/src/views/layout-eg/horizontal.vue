<template>
  <Acquisitions/>
</template>

<script lang="ts">
// Replaced missing ecommerce dashboard with acquisitions for Railway build
// @ts-ignore - Type inference issue with Vue component exports
import Acquisitions from "@/views/acq_module/acq_dash/index_acq_dash.vue";
import {useLayoutStore} from "@/stores/layout";

export default {
  components: {Acquisitions},
  data() {
    return {
      useLayout: useLayoutStore()
    }
  },
  mounted() {
    this.useLayout.config.layoutType = 'horizontal'
  },
  unmounted() {
    this.useLayout.config.layoutType = 'vertical'
  }
}
</script>
