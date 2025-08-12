<template>
  <div class="wrapper">

    <Topbar/>
    <LeftSidebar/>
<!--    <Sidebar :is-condensed="isMenuCondensed"-->
<!--             :theme="useLayout.config.theme"-->
<!--             :type="useLayout.config.sidenav.size"/>-->

    <div class="content-page">
      <div class="content">
        <b-container fluid>

          <slot></slot>

        </b-container>
      </div>

      <Footer/>

    </div>
  </div>

  <RightSidebar/>
</template>

<script lang="ts">
import Topbar from "@/components/layouts/partials/topbar.vue";
import LeftSidebar from "@/components/layouts/partials/left-sidebar.vue";
import Footer from "@/components/layouts/partials/footer.vue";
import RightSidebar from "@/components/layouts/partials/right-sidebar.vue";
import Sidebar from "@/components/layouts/partials/sidebar.vue";
import router from "@/router";

import {useLayoutStore} from "@/stores/layout";

export default {
  components: {Sidebar, RightSidebar, Footer, LeftSidebar, Topbar},
  data() {
    return {
      isMenuCondensed: false,
      user: {},
      useLayout: useLayoutStore()
    }
  },

  watch: {
    layoutWidth: function (newVal, oldVal) {
      if (newVal !== oldVal) {
        this.activateWidth(newVal)
      }
    },
  },
  created: function () {
    document.getElementsByTagName('html')[0].removeAttribute('data-layout')
    if (window.screen.width >= 767 && window.screen.width <= 1028) {
      this.useLayout.changeLeftbarSize('condensed')
      this.isMenuCondensed = true
    } else if (window.screen.width > 1028) {
      this.useLayout.changeLeftbarSize('fixed')
      this.isMenuCondensed = false
    }
    this.activateWidth(this.layoutWidth)
  },
  mounted: () => {
    if (
        /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini|Mobile|mobile|CriOS/i.test(
            navigator.userAgent
        )
    ) {
      if (window.screen.width >= 728 && window.screen.width <= 1028) {
        document.body.setAttribute('data-sidenav-size', 'condensed')
      }
    }
    if (
        /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini|Mobile|mobile|CriOS/i.test(
            navigator.userAgent
        )
    ) {
      router.afterEach((routeTo, routeFrom) => {
        document.body.classList.remove('sidebar-enable')
      })
    }
  },
  methods: {

    toggleMenu() {
      document.body.classList.toggle('sidebar-enable')
    },
    hideMenu() {
      document.body.classList.remove('sidebar-enable')
    },
    toggleRightSidebar() {
      document.body.classList.toggle('right-bar-enabled')
    },
    hideRightSidebar() {
      document.body.classList.remove('right-bar-enabled')
    },
    activateWidth(width) {
      switch (width) {
        case 'boxed':
          document.body.setAttribute('data-layout-mode', 'boxed')
          this.useLayout.changeLeftbarSize('condensed')
          this.isMenuCondensed = true
          break
        default:
          document.body.removeAttribute('data-layout-mode')
          this.useLayout.changeLeftbarSize('fixed')
          this.isMenuCondensed = false
          break
      }
    },
  },
}
</script>
