<template>
  <Ecommerce/>
</template>

<script lang="ts">
import Ecommerce from "@/views/dashboards/ecommerce/index.vue";
import {useLayoutStore} from "@/stores/layout";

export default {
  components: {Ecommerce},
  data() {
    return {
      useLayout: useLayoutStore()
    }
  },
  mounted() {
    this.useLayout.config.layoutType = 'detached'
  },
  unmounted() {
    this.useLayout.config.layoutType = 'vertical'
  }
}
</script>
