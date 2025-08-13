<template>
<Layout>
    <Breadcrumb :title="title" :items="items" />

    <b-row>
        <b-col cols="12">
            <b-card>
                <h4 class="header-title">Grid Options</h4>
                <p class="text-muted font-13">
                    See how aspects of the Bootstrap grid system work across multiple devices with a handy table.
                </p>

                <div class="table-responsive">
                    <table class="table table-bordered table-striped mb-0">
                        <thead>
                            <tr>
                                <th></th>
                                <th class="text-center">
                                    Extra small<br>
                                    <small>&lt;576px</small>
                                </th>
                                <th class="text-center">
                                    Small<br>
                                    <small>≥576px</small>
                                </th>
                                <th class="text-center">
                                    Medium<br>
                                    <small>≥768px</small>
                                </th>
                                <th class="text-center">
                                    Large<br>
                                    <small>≥992px</small>
                                </th>
                                <th class="text-center">
                                    Extra large<br>
                                    <small>≥1200px</small>
                                </th>
                                <th class="text-center">
                                    Extra large<br>
                                    <small>≥1400px</small>
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <th class="text-nowrap" scope="row">Container <code class="fw-normal">max-width</code></th>
                                <td>None (auto)</td>
                                <td>540px</td>
                                <td>720px</td>
                                <td>960px</td>
                                <td>1140px</td>
                                <td>1320px</td>
                            </tr>
                            <tr>
                                <th class="text-nowrap" scope="row">Class prefix</th>
                                <td><code>.col-</code></td>
                                <td><code>.col-sm-</code></td>
                                <td><code>.col-md-</code></td>
                                <td><code>.col-lg-</code></td>
                                <td><code>.col-xl-</code></td>
                                <td><code>.col-xxl-</code></td>
                            </tr>
                            <tr>
                                <th class="text-nowrap" scope="row"># of columns</th>
                                <td colspan="6">12</td>
                            </tr>
                            <tr>
                                <th class="text-nowrap" scope="row">Gutter width</th>
                                <td colspan="6">1.5rem (.75rem on left and right)</td>
                            </tr>
                            <tr>
                                <th class="text-nowrap" scope="row">Custom gutters</th>
                                <td colspan="6"><a href="/docs/5.3/layout/gutters/">Yes</a></td>
                            </tr>
                            <tr>
                                <th class="text-nowrap" scope="row">Nestable</th>
                                <td colspan="6"><a href="#nesting">Yes</a></td>
                            </tr>
                            <tr>
                                <th class="text-nowrap" scope="row">Column ordering</th>
                                <td colspan="6"><a href="/docs/5.3/layout/columns/#reordering">Yes</a></td>
                            </tr>
                        </tbody>
                    </table>
                </div> <!-- end table-responsive-->

            </b-card> <!-- end card-->
        </b-col> <!-- end col-->
    </b-row>
    <!-- end row -->

    <b-row>
        <b-col cols="12">
            <b-card>
                <h4 class="header-title mb-3">Grid Example</h4>

                <div class="grid-structure">
                    <b-row>
                        <b-col lg="12">
                            <div class="grid-container">
                                col-lg-12
                            </div>
                        </b-col>
                    </b-row>
                    <b-row>
                        <b-col lg="11">
                            <div class="grid-container">
                                col-lg-11
                            </div>
                        </b-col>
                        <b-col lg="1">
                            <div class="grid-container">
                                col-lg-1
                            </div>
                        </b-col>
                    </b-row>
                    <b-row>
                        <b-col lg="10">
                            <div class="grid-container">
                                col-lg-10
                            </div>
                        </b-col>
                        <b-col lg="2">
                            <div class="grid-container">
                                col-lg-2
                            </div>
                        </b-col>
                    </b-row>
                    <b-row>
                        <b-col lg="9">
                            <div class="grid-container">
                                col-lg-9
                            </div>
                        </b-col>
                        <b-col lg="3">
                            <div class="grid-container">
                                col-lg-3
                            </div>
                        </b-col>
                    </b-row>
                    <b-row>
                        <b-col lg="8">
                            <div class="grid-container">
                                col-lg-8
                            </div>
                        </b-col>
                        <b-col lg="4">
                            <div class="grid-container">
                                col-lg-4
                            </div>
                        </b-col>
                    </b-row>
                    <b-row>
                        <b-col lg="7">
                            <div class="grid-container">
                                col-lg-7
                            </div>
                        </b-col>
                        <b-col lg="5">
                            <div class="grid-container">
                                col-lg-5
                            </div>
                        </b-col>
                    </b-row>
                    <b-row>
                        <b-col lg="6">
                            <div class="grid-container">
                                col-lg-6
                            </div>
                        </b-col>
                        <b-col lg="6">
                            <div class="grid-container">
                                col-lg-6
                            </div>
                        </b-col>
                    </b-row>
                    <b-row>
                        <b-col lg="5">
                            <div class="grid-container">
                                col-lg-5
                            </div>
                        </b-col>
                        <b-col lg="7">
                            <div class="grid-container">
                                col-lg-7
                            </div>
                        </b-col>
                    </b-row>
                    <b-row>
                        <b-col lg="4">
                            <div class="grid-container">
                                col-lg-4
                            </div>
                        </b-col>
                        <b-col lg="8">
                            <div class="grid-container">
                                col-lg-8
                            </div>
                        </b-col>
                    </b-row>
                    <b-row>
                        <b-col lg="3">
                            <div class="grid-container">
                                col-lg-3
                            </div>
                        </b-col>
                        <b-col lg="9">
                            <div class="grid-container">
                                col-lg-9
                            </div>
                        </b-col>
                    </b-row>
                    <b-row>
                        <b-col lg="2">
                            <div class="grid-container">
                                col-lg-2
                            </div>
                        </b-col>
                        <b-col lg="10">
                            <div class="grid-container">
                                col-lg-10
                            </div>
                        </b-col>
                    </b-row>
                    <b-row>
                        <b-col lg="1">
                            <div class="grid-container">
                                col-lg-1
                            </div>
                        </b-col>
                        <b-col lg="11">
                            <div class="grid-container">
                                col-lg-11
                            </div>
                        </b-col>
                    </b-row>
                    <b-row>
                        <b-col lg="2">
                            <div class="grid-container">
                                col-lg-2
                            </div>
                        </b-col>
                        <b-col lg="3">
                            <div class="grid-container">
                                col-lg-3
                            </div>
                        </b-col>
                        <b-col lg="4">
                            <div class="grid-container">
                                col-lg-4
                            </div>
                        </b-col>
                        <b-col lg="2">
                            <div class="grid-container">
                                col-lg-2
                            </div>
                        </b-col>
                        <b-col lg="1">
                            <div class="grid-container">
                                col-lg-1
                            </div>
                        </b-col>
                    </b-row> <!-- end row -->
                </div> <!-- grid-structure -->

            </b-card> <!-- end card-->
        </b-col> <!-- end col-->
    </b-row>
    <!-- end row-->

</Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";
export default {
    components: { Layout, Breadcrumb },
  data() {
    return {
      title: 'Grid System',
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
          text: 'Grid System',
          active: true,
        },
      ],
    }
  },
}
</script>
