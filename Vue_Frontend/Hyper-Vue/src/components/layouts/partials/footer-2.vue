<template>
  <!-- Footer-->
  <footer class="footer footer-alt">
    <p class="text-muted">2018 - {{ year }} © Hyper - Coderthemes.com
    </p>
  </footer>
</template>

<script lang="ts">
export default {
  computed: {
    year() {
      return new Date().getFullYear()
    }
  },
}
</script>
