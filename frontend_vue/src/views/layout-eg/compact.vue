<template>
  <Acquisitions/>
</template>

<script lang="ts">
// Replaced missing ecommerce dashboard with acquisitions for Railway build
// @ts-ignore - Type inference issue with Vue component exports
import Acquisitions from "@/views/dashboards/acquisitions/index.vue";
import {useLayoutStore} from "@/stores/layout";

export default {
  components: {Acquisitions},
  data() {
    return{
      useLayout:useLayoutStore()
    }
  },
  mounted() {
    if(this.useLayout.config.layoutType == 'horizontal'){
      this.useLayout.config.layoutType = 'vertical'
    }
    document.getElementsByTagName('html')[0].setAttribute('data-sidenav-size', 'compact')
  },
  unmounted() {
    document.getElementsByTagName('html')[0].setAttribute('data-sidenav-size', 'fixed')
  }
}
</script>
