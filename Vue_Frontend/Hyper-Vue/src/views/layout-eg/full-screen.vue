<template>
  <Ecommerce/>
</template>

<script lang="ts">
import Ecommerce from "@/views/dashboards/ecommerce/index.vue";
import {useLayoutStore} from "@/stores/layout";

export default {
  components: {Ecommerce},
  data(){
    return{
      useLayout:useLayoutStore()
    }
  },
  mounted() {
    if(this.useLayout.config.layoutType == 'horizontal'){
      this.useLayout.config.layoutType = 'vertical'
    }
    document.getElementsByTagName('html')[0].setAttribute('data-sidenav-size','fullscreen')
  },
  unmounted() {
    document.getElementsByTagName('html')[0].setAttribute('data-sidenav-size','fixed')
  }
}
</script>
