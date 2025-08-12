<template>
  <Vertical v-if="useLayout.config.layoutType === 'vertical'">
    <slot/>
  </Vertical>
  <Horizontal v-if="useLayout.config.layoutType === 'horizontal'">
    <slot/>
  </Horizontal>
  <Detached v-if="useLayout.config.layoutType === 'detached'">
    <slot/>
  </Detached>
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
}
</script>
