<template>
<Layout>
    <Breadcrumb :title="title" :items="items" />

    <b-row>
        <b-col xl="6">
            <CustomSyntax title="Default Pagination">
                <template v-slot:sub-text>
                    Simple pagination inspired by Rdio, great for apps and search results.
                </template>
                <template v-slot:preview>
                    <nav>

                        <b-pagination v-model="currentPage1" :total-rows="20" :per-page="4"></b-pagination>
                    </nav>
                </template>
            </CustomSyntax>

            <CustomSyntax title="Disabled and active states">
                <template v-slot:sub-text>
                    Pagination links are customizable for different circumstances. Use <code>.disabled</code> for links that appear un-clickable and <code>.active</code> to indicate the current page.
                </template>
                <template v-slot:preview>
                    <nav aria-label="...">
                        <b-pagination v-model="currentPage" :total-rows="15" :per-page="5" hide-goto-end-buttons prev-text="Previous" next-text="Next"></b-pagination>
                    </nav>
                </template>
            </CustomSyntax>

            <CustomSyntax title="Alignment">
                <template v-slot:sub-text>
                    Change the alignment of pagination components with flexbox utilities.
                </template>
                <template v-slot:preview>

                    <nav aria-label="Page navigation example">
                        <b-pagination v-model="currentPage1" :total-rows="15" :per-page="5" hide-goto-end-buttons prev-text="Previous" next-text="Next" align="center"></b-pagination>
                    </nav>

                    <nav aria-label="Page navigation example">

                        <b-pagination v-model="currentPage1" :total-rows="15" :per-page="5" hide-goto-end-buttons prev-text="Previous" next-text="Next" align="end"></b-pagination>
                    </nav>

                </template>
            </CustomSyntax>

        </b-col> <!-- end col -->

        <b-col xl="6">
            <CustomSyntax title="Rounded Pagination">
                <template v-slot:sub-text>
                    Add <code> .pagination-rounded</code> for rounded pagination.
                </template>
                <template v-slot:preview>
                    <nav>
                        <ul class="pagination pagination-rounded mb-0">
                            <b-pagination v-model="currentPage2" :total-rows="20" :per-page="4"></b-pagination>
                        </ul>
                    </nav>
                </template>
            </CustomSyntax>

            <CustomSyntax title="Sizing">
                <template v-slot:sub-text>
                    Add <code> .pagination-lg</code> or <code> .pagination-sm</code> for additional sizes.
                </template>
                <template v-slot:preview>
                    <nav>
                        <b-pagination v-model="currentPage1" :total-rows="15" :per-page="5" size="lg"></b-pagination>
                    </nav>

                    <nav>
                        <ul class="mb-0">
                            <b-pagination v-model="currentPage1" :total-rows="15" :per-page="5" size="sm"></b-pagination>
                        </ul>
                    </nav>
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
          title: 'Pagination',
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
              text: 'Pagination',
              active: true,
            },
          ],
            currentPage: 2,
            currentPage1: 0,
            currentPage2: 3
        };
    },
}
</script>
