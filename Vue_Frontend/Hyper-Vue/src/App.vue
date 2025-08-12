<template>
  <RouterView/>
</template>

<script lang="ts">
import {RouterLink, RouterView} from 'vue-router'
import {useLayoutStore} from "@/stores/layout";

export default {
  data() {
    return {
      useLayout: useLayoutStore(),
    }
  },
  mounted() {
    this.useLayout.init()
    this.useLayout.initConfig()

    this.initPortletCard()
  },
  methods: {
    initPortletCard() {
      let portletIdentifier = ".card"
      let portletCloser = '.card a[data-bs-toggle="remove"]'
      let portletRefresher = '.card a[data-bs-toggle="reload"]'

      // Panel closest
      $(document).on("click", portletCloser, function (ev) {
        ev.preventDefault();
        let $portlet = $(this).closest(portletIdentifier);
        let $portlet_parent = $portlet.parent();
        $portlet.remove();
        if ($portlet_parent.children().length == 0) {
          $portlet_parent.remove();
        }
      });

      // Panel Reload
      $(document).on("click", portletRefresher, function (ev) {
        ev.preventDefault();
        let $portlet = $(this).closest(portletIdentifier);
        // This is just a simulation, nothing is going to be reloaded
        $portlet.append('<div class="card-disabled"><div class="card-portlets-loader"></div></div>');
        let $pd = $portlet.find('.card-disabled');
        setTimeout(function () {
          $pd.fadeOut('fast', function () {
            $pd.remove();
          });
        }, 500 + 300 * (Math.random() * 5));
      });
    },
  }
}
</script>