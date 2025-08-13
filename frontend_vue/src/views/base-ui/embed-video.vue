<template>
<Layout>
    <Breadcrumb :title="title" :items="items" />

    <b-row>
        <b-col xl="6">
            <CustomSyntax title="Responsive embed video 21:9">
                <template v-slot:sub-text>
                    Use class <code>.ratio-21x9</code>
                </template>
                <template v-slot:preview>
                    <div class="ratio ratio-21x9">
                        <iframe src="https://www.youtube.com/embed/PrUxWZiQfy4?autohide=0&showinfo=0&controls=0"></iframe>
                    </div>
                </template>
            </CustomSyntax>

            <CustomSyntax title="Responsive embed video 1:1">
                <template v-slot:sub-text>
                    Use class <code>.ratio-1x1</code>
                </template>
                <template v-slot:preview>
                    <div class="ratio ratio-1x1">
                        <iframe src="https://www.youtube.com/embed/PrUxWZiQfy4?ecver=1"></iframe>
                    </div>
                </template>
            </CustomSyntax>

        </b-col> <!-- end col -->

        <b-col xl="6">
            <CustomSyntax title="Responsive embed video 16:9">
                <template v-slot:sub-text>
                    Use class <code>.ratio-16x9</code>
                </template>
                <template v-slot:preview>
                    <div class="ratio ratio-16x9">
                        <iframe src="https://www.youtube.com/embed/PrUxWZiQfy4?autohide=0&showinfo=0&controls=0"></iframe>
                    </div>
                </template>
            </CustomSyntax>

            <CustomSyntax title="Responsive embed video 4:3">
                <template v-slot:sub-text>
                    Use class <code>.ratio-4x3</code>
                </template>
                <template v-slot:preview>
                    <div class="ratio ratio-4x3">
                        <iframe src="https://www.youtube.com/embed/PrUxWZiQfy4?ecver=1"></iframe>
                    </div>
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
    components: { Layout, CustomSyntax, Breadcrumb },
  data() {
    return {
      title: 'Embed Video',
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
          text: 'Embed Video',
          active: true,
        },
      ],
    }
  },
}
</script>
