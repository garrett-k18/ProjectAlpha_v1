<template>
  <!--
    Render the appropriate layout based on the current layoutType.
    If an unexpected layoutType is persisted in storage, fall back to Vertical
    to avoid rendering a blank page.
  -->
  <Vertical v-if="layoutType === 'vertical'">
    <slot/>
  </Vertical>
  <Horizontal v-else-if="layoutType === 'horizontal'">
    <slot/>
  </Horizontal>
  <Detached v-else-if="layoutType === 'detached'">
    <slot/>
  </Detached>
  <!-- Safe fallback: default to Vertical -->
  <Vertical v-else>
    <slot/>
  </Vertical>
  
</template>

<script lang="ts">
import Vertical from "@/components/layouts/vertical.vue";
import Horizontal from "@/components/layouts/horizontal.vue";
import Detached from "@/components/layouts/detached.vue";

import {useLayoutStore} from "@/stores/layout";

export default {
  components: {Detached, Horizontal, Vertical},
  data() {
    return {
      useLayout: useLayoutStore()
    }
  },
  computed: {
    // Normalize layoutType to one of the supported values
    layoutType(): string {
      const t: any = this.useLayout?.config?.layoutType
      return ['vertical', 'horizontal', 'detached'].includes(t) ? t : 'vertical'
    }
  },
}
</script>
