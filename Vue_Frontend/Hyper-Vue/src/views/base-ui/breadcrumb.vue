<template>
  <Layout>

    <Breadcrumb :title="title" :items="items"/>

    <b-row>
      <b-col xl="6">
        <CustomSyntax title="Example">
          <template v-slot:sub-text>
            Indicate the current page’s location within a navigational hierarchy that automatically adds separators via
            CSS.
            Please read the official <a target="_blank" href="https://getbootstrap.com/docs/5.3/components/breadcrumb/">Bootstrap</a>
            documentation for more options.
          </template>
          <template v-slot:preview>
            <nav aria-label="breadcrumb">
              <ol class="breadcrumb mb-0 py-1">
                <b-breadcrumb-item active>Home</b-breadcrumb-item>
              </ol>
            </nav>

            <nav aria-label="breadcrumb">
              <ol class="breadcrumb mb-0 py-2">
                <b-breadcrumb-item><a href="#">Home</a></b-breadcrumb-item>
                <b-breadcrumb-item active>Library</b-breadcrumb-item>
              </ol>
            </nav>

            <nav aria-label="breadcrumb">
              <ol class="breadcrumb mb-0 py-2">
                <b-breadcrumb-item><a href="#">Home</a></b-breadcrumb-item>
                <b-breadcrumb-item><a href="#">Library</a></b-breadcrumb-item>
                <b-breadcrumb-item active>Data</b-breadcrumb-item>
              </ol>
            </nav>
          </template>
        </CustomSyntax>
      </b-col> <!-- end col -->

      <b-col xl="6">
        <CustomSyntax title="With Icons">
          <template v-slot:sub-text>
            Optionally you can also specify the icon with your breadcrumb item.
          </template>
          <template v-slot:preview>
            <nav aria-label="breadcrumb">
              <ol class="breadcrumb mb-1 p-2 bg-light-subtle">
                <b-breadcrumb-item active><i class="ri-home-4-line me-1"></i>Home
                </b-breadcrumb-item>
              </ol>
            </nav>

            <nav aria-label="breadcrumb">
              <ol class="breadcrumb mb-1 p-2 bg-light-subtle">
                <b-breadcrumb-item><a href="#"><i class="ri-home-4-line"></i> Home</a></b-breadcrumb-item>
                <b-breadcrumb-item active>Library</b-breadcrumb-item>
              </ol>
            </nav>

            <nav aria-label="breadcrumb">
              <ol class="breadcrumb mb-0 p-2 bg-light-subtle">
                <b-breadcrumb-item><a href="#"><i class="ri-home-4-line"></i> Home</a></b-breadcrumb-item>
                <b-breadcrumb-item><a href="#">Library</a></b-breadcrumb-item>
                <b-breadcrumb-item active>Data</b-breadcrumb-item>
              </ol>
            </nav>
          </template>
        </CustomSyntax>

      </b-col> <!-- end col -->

    </b-row> <!-- end row -->
  </Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";
import CustomSyntax from "@/components/custom/custom-syntax.vue";

export default {
  components: {Layout, CustomSyntax, Breadcrumb},
  data() {
    return {
      title: 'Breadcrumb',
      items: [
        {
          text: 'Hyper',
          href: '/',
        },
        {
          text: 'Base UI',
          href: '/',
        },
        {
          text: 'Breadcrumb',
          active: true,
        },
      ],
    }
  },
}
</script>
