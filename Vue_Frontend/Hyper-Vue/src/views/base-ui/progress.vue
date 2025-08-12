<template>
  <Layout>
    <Breadcrumb :title="title" :items="items"/>

    <b-row>
      <b-col xl="6">
        <CustomSyntax title="Examples">
          <template v-slot:sub-text>
            A progress bar can be used to show a user how far along he/she is in a process.
          </template>
          <template v-slot:preview>
            <b-progress class="mb-2">
              <b-progress-bar></b-progress-bar>
            </b-progress>
            <b-progress class="mb-2">
              <b-progress-bar :value="25"></b-progress-bar>
            </b-progress>
            <b-progress class="mb-2">
              <b-progress-bar :value="50"></b-progress-bar>
            </b-progress>
            <b-progress class="mb-2">
              <b-progress-bar :value="75"></b-progress-bar>
            </b-progress>
            <b-progress>
              <b-progress-bar :value="100"></b-progress-bar>
            </b-progress>
          </template>
        </CustomSyntax>

        <CustomSyntax title="Height">
          <template v-slot:sub-text>
            We only set a <code>height</code> value on the <code>.progress</code>, so if you change that value the inner
            <code>.progress-bar</code> will automatically resize accordingly.
            Use <code>.progress-sm</code>,<code>.progress-md</code>,<code>.progress-lg</code>,<code>.progress-xl</code>
            classes.
          </template>
          <template v-slot:preview>
            <b-progress class="mb-2" style="height: 1px;">
              <b-progress-bar variant="danger" :value="25"></b-progress-bar>
            </b-progress>
            <b-progress class="mb-2" style="height: 3px;">
              <b-progress-bar :value="25" height="20px"></b-progress-bar>
            </b-progress>
            <b-progress class="mb-2 progress-sm">
              <b-progress-bar variant="success" :value="25"></b-progress-bar>
            </b-progress>
            <b-progress class="mb-2 progress-md">
              <b-progress-bar variant="info" :value="50"></b-progress-bar>
            </b-progress>
            <b-progress class="progress-lg mb-2">
              <b-progress-bar variant="warning" :value="75"></b-progress-bar>
            </b-progress>
            <b-progress class="progress-xl">
              <b-progress-bar variant="success" :value="38"></b-progress-bar>
            </b-progress>
          </template>
        </CustomSyntax>

        <CustomSyntax title="Multiple bars">
          <template v-slot:sub-text>
            Include multiple progress bars in a progress component if you need.
          </template>
          <template v-slot:preview>
            <b-progress>
              <b-progress-bar :value="15"></b-progress-bar>
              <b-progress-bar variant="success" :value="30"></b-progress-bar>
              <b-progress-bar variant="info" :value="20"></b-progress-bar>
            </b-progress>
          </template>
        </CustomSyntax>

        <CustomSyntax title="Animated stripes">
          <template v-slot:sub-text>
            The striped gradient can also be animated. Add <code>.progress-bar-animated</code> to
            <code>.progress-bar</code> to animate the stripes right to left via CSS3 animations.
          </template>
          <template v-slot:preview>
            <b-progress>
              <b-progress-bar striped animated style="width: 75%"></b-progress-bar>
            </b-progress>
          </template>
        </CustomSyntax>

      </b-col> <!-- end col -->

      <b-col xl="6">
        <CustomSyntax title="Labels">
          <template v-slot:sub-text>
            Add labels to your progress bars by placing text within the <code>.progress-bar</code>.
          </template>
          <template v-slot:preview>
            <b-progress class="mb-3">
              <b-progress-bar style="width: 25%;">25%</b-progress-bar>
            </b-progress>
            <b-progress>
              <b-progress-bar visible class="text-dark" style="width: 10%">Long label text for the progress bar, set to
                a dark color
              </b-progress-bar>
            </b-progress>
          </template>
        </CustomSyntax>

        <CustomSyntax title="Backgrounds">
          <template v-slot:sub-text>
            Use background utility classes to change the appearance of individual progress bars.
          </template>
          <template v-slot:preview>
            <b-progress class="mb-2">
              <b-progress-bar variant="success" style="width: 25%"></b-progress-bar>
            </b-progress>
            <b-progress class="mb-2">
              <b-progress-bar variant="info" style="width: 50%"></b-progress-bar>
            </b-progress>
            <b-progress class="mb-2">
              <b-progress-bar variant="warning" style="width: 75%"></b-progress-bar>
            </b-progress>
            <b-progress class="mb-2">
              <b-progress-bar variant="danger" style="width: 100%"></b-progress-bar>
            </b-progress>
            <b-progress class="mb-2">
              <b-progress-bar variant="dark" style="width: 65%"></b-progress-bar>
            </b-progress>
            <b-progress>
              <b-progress-bar variant="secondary" style="width: 50%"></b-progress-bar>
            </b-progress>
          </template>
        </CustomSyntax>

        <CustomSyntax title="Striped">
          <template v-slot:sub-text>
            Add <code>.progress-bar-striped</code> to any <code>.progress-bar</code> to apply a stripe via CSS gradient
            over the progress bar’s background color.
          </template>
          <template v-slot:preview>
            <b-progress class="mb-2">
              <b-progress-bar striped style="width: 10%"></b-progress-bar>
            </b-progress>
            <b-progress class="mb-2">
              <b-progress-bar striped variant="success" style="width: 25%"></b-progress-bar>
            </b-progress>
            <b-progress class="mb-2">
              <b-progress-bar striped variant="info" style="width: 50%"></b-progress-bar>
            </b-progress>
            <b-progress class="mb-2">
              <b-progress-bar striped variant="warning" style="width: 75%"></b-progress-bar>
            </b-progress>
            <b-progress>
              <b-progress-bar striped variant="danger" style="width: 100%"></b-progress-bar>
            </b-progress>
          </template>
        </CustomSyntax>

      </b-col> <!-- end col -->
    </b-row>
    <!-- end row -->

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
      title: 'Progress',
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
          text: 'Progress',
          active: true,
        },
      ],
    }
  }
}
</script>
