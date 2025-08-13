<template>
  <div class="wrapper">

    <Topbar/>
    <HorizontalNav/>

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
import AppMenu from "@/components/layouts/partials/app-menu.vue";
import RightSidebar from "@/components/layouts/partials/right-sidebar.vue";
import Footer from "@/components/layouts/partials/footer.vue";
import HorizontalNav from "@/components/layouts/partials/horizontal-nav.vue";

export default {
  components: {HorizontalNav, Topbar, AppMenu, RightSidebar, Footer},
  data() {
    let html = document.getElementsByTagName('html')[0]
    return {
      user: {},
      showMenu: window.screen.width > 768,
      layoutWidth: 'fluid',
      html
    }
  },

  watch: {
    layoutWidth: function (newVal, oldVal) {
      if (newVal !== oldVal) {
        this.activateWidth(newVal)
      }
    },
  },
  mounted() {
    this.html.setAttribute('data-layout', 'topnav')
    document.body.classList.remove('authentication-bg')
    document.body.classList.remove('authentication-bg-pattern')
    this.activateWidth(this.layoutWidth)
  },
  unmounted() {
    this.html.removeAttribute('data-layout')
  },
  methods: {

    toggleMenu() {
      this.showMenu = !this.showMenu
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
          break
        default:
          document.body.removeAttribute('data-layout-mode')
          break
      }
    },
  },
}
</script>