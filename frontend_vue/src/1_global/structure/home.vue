<template>
  <Layout>
    <b-row>
      <b-col class="col-12">
        <div class="page-title-box">
          <h4 class="page-title">Home Page</h4>
        </div>
      </b-col>
    </b-row>

    <b-row>
      <b-col>
        <div class="card">
          <div class="card-body">
            <p>Welcome to the home page! We will build this out using the SAAS layout.</p>
          </div>
        </div>
      </b-col>
    </b-row>
  </Layout>
</template>

<script lang="ts">
// Importing the main layout component
import Layout from "@/components/layouts/layout.vue";

/**
 * Home component
 */
export default {
  // Component name
  name: "HomePage",
  // Child components
  components: {
    Layout,
  },
};
</script>
