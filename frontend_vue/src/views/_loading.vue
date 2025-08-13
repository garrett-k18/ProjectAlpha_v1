<template>
  <Layout>
    <!-- Pre-loader -->
    <div class="preloader">
      <div id="status">
        <b-spinner style="width: 3rem; height: 3rem;" label="Large Spinner" variant="primary"></b-spinner>
      </div>
    </div>
    <!-- End Preloader -->
  </Layout>

</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";

export default {
  components: {Layout}
}

</script>
