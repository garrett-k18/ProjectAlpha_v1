<template>
  <Layout>
    <Breadcrumb :title="title" :items="items"/>
    <b-row>
      <b-col xxl="8" lg="7">
        <!-- project card -->
        <Description/>
        <Comments/>
      </b-col>
      <!-- end col -->

      <b-col xxl="4" lg="5">
        <Attachment/>
      </b-col>
      <!-- end col -->
    </b-row>
    <!-- end row -->
  </Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";

import Description from "@/views/apps/tasks/details/description.vue";
import Comments from "@/views/apps/tasks/details/comments.vue";
import Attachment from "@/views/apps/tasks/details/attachment.vue";

export default {

  components: {Layout, Breadcrumb, Description, Comments, Attachment},
  data() {
    return {
      title: 'Task Detail',
      items: [
        {
          text: 'Hyper',
          href: '/',
        },
        {
          text: 'Tasks',
          href: '/',
        },
        {
          text: 'Task Detail',
          active: true,
        },
      ],
    }
  },
}
</script>
