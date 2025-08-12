<template>
  <Layout>
    <Breadcrumb :title="title" :items="items"/>
    <b-row>
      <b-col xxl="8" lg="6">
        <Design/>

        <Comments/>
      </b-col> <!-- end col -->

      <b-col xxl="4" lg="6">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title mb-3">Progress</h5>
            <div dir="ltr">
              <div class="mt-3 chartjs-chart" style="height: 320px;">
                <LineChart/>
              </div>
            </div>
          </div>
        </div>
        <!-- end card-->

        <Files/>
      </b-col>
    </b-row>
    <!-- end row -->
  </Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";
import Design from "@/views/apps/projects/details/design.vue";
import Comments from "@/views/apps/projects/details/comments.vue";
import Files from "@/views/apps/projects/details/files.vue";
import LineChart from "@/views/apps/projects/details/line-chart.vue";

export default {
  components: {
    LineChart,
    Files,
    Comments,
    Design,
    Layout,
    Breadcrumb
  },
  data() {
    return {
      title: 'Project Details',
      items: [
        {
          text: 'Hyper',
          href: '/',
        },
        {
          text: 'Projects',
          href: '/',
        },
        {
          text: 'Project Details',
          active: true,
        },
      ],
    }
  },
}
</script>
