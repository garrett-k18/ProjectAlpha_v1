<template>
<Layout>
    <Breadcrumb :title="title" :items="items" />

    <b-row>
        <b-col xl="6">
            <CustomSyntax title="Placeholders">
                <template v-slot:sub-text>
                    In the example below, we take a typical card component and recreate it with placeholders applied to create a “loading card”. Size and proportions are the same between the two.
                </template>
                <template v-slot:preview>
                    <b-row>
                        <b-col md="6">
                            <div class="card border shadow-none mb-md-0">
                                <img src="@/assets/images/small/small-1.jpg" class="card-img-top" alt="...">

                                <div class="card-body">
                                    <h5 class="card-title">Card title</h5>
                                    <p class="card-text">Some quick example text to build on the card title and make up the bulk of the card's
                                        content.</p>
                                    <a href="#" class="btn btn-primary">Go somewhere</a>
                                </div> <!-- end card-body-->
                            </div> <!-- end card-->
                        </b-col> <!-- end col-->

                        <b-col md="6">
                            <div class="card border shadow-none mb-0" aria-hidden="true">
                                <img src="@/assets/images/small/small-2.jpg" class="card-img-top" alt="...">
                                <div class="card-body">
                                    <h5 class="card-title placeholder-glow">
                                        <span class="placeholder col-6"></span>
                                    </h5>
                                    <p class="card-text placeholder-glow">
                                        <span class="placeholder col-7"></span>
                                        <span class="placeholder col-4"></span>
                                        <span class="placeholder col-4"></span>
                                        <span class="placeholder col-6"></span>
                                        <span class="placeholder col-8"></span>
                                    </p>
                                    <a href="#" tabindex="-1" class="btn btn-primary disabled placeholder col-6"></a>
                                </div> <!-- end card-body-->
                            </div> <!-- end card-->
                        </b-col> <!-- end col-->
                    </b-row> <!-- end row-->
                </template>
            </CustomSyntax>
        </b-col> <!-- end col-->

        <b-col xl="6">
            <CustomSyntax title="Color">
                <template v-slot:sub-text>
                    By default, the <code>placeholder</code> uses <code>currentColor</code>. This can be overriden with a custom color or utility class.
                </template>
                <template v-slot:preview>
                    <span class="placeholder col-12"></span>
                    <span class="placeholder col-12 bg-primary"></span>
                    <span class="placeholder col-12 bg-secondary"></span>
                    <span class="placeholder col-12 bg-success"></span>
                    <span class="placeholder col-12 bg-danger"></span>
                    <span class="placeholder col-12 bg-warning"></span>
                    <span class="placeholder col-12 bg-info"></span>
                    <span class="placeholder col-12 bg-light"></span>
                    <span class="placeholder col-12 bg-dark"></span>
                </template>
            </CustomSyntax>

            <CustomSyntax title="Width">
                <template v-slot:sub-text>
                    You can change the <code>width</code> through grid column classes, width utilities, or inline styles.
                </template>
                <template v-slot:preview>
                    <span class="placeholder col-6"></span>
                    <span class="placeholder w-75"></span>
                    <span class="placeholder" style="width: 25%;"></span>
                </template>
            </CustomSyntax>

        </b-col> <!-- end col-->

        <b-col xl="6">
            <CustomSyntax title="Sizing">
                <template v-slot:sub-text>
                    The size of <code>.placeholder</code>s are based on the typographic style of the parent element. Customize them with sizing modifiers: <code>.placeholder-lg</code>, <code>.placeholder-sm</code>, or <code>.placeholder-xs</code>.
                </template>
                <template v-slot:preview>
                    <span class="placeholder col-12 placeholder-lg"></span>
                    <span class="placeholder col-12"></span>
                    <span class="placeholder col-12 placeholder-sm"></span>
                    <span class="placeholder col-12 placeholder-xs"></span>
                </template>
            </CustomSyntax>

        </b-col> <!-- end col-->

        <b-col xl="6">
            <CustomSyntax title="How it works">
                <template v-slot:sub-text>
                    Create placeholders with the <code>.placeholder</code> class and a grid column class (e.g., <code>.col-6</code>) to set the <code>width</code>. They can replace the text inside an element or as be added as a modifier class to an existing component.
                </template>
                <template v-slot:preview>
                    <p aria-hidden="true">
                        <span class="placeholder col-6"></span>
                    </p>

                    <a href="#" class="btn btn-primary disabled placeholder col-4" aria-hidden="true"></a>
                </template>
            </CustomSyntax>

        </b-col> <!-- end col-->

        <b-col xl="6">
            <CustomSyntax title="Animation">
                <template v-slot:sub-text>
                    Animate placehodlers with <code>.placeholder-glow</code> or <code>.placeholder-wave</code> to better convey the perception of something being <em>actively</em> loaded.
                </template>
                <template v-slot:preview>
                    <p class="placeholder-glow">
                        <span class="placeholder col-12"></span>
                    </p>

                    <p class="placeholder-wave mb-0">
                        <span class="placeholder col-12"></span>
                    </p>
                </template>
            </CustomSyntax>

        </b-col> <!-- end col-->
    </b-row> <!-- end row -->

</Layout>
</template>

<script>
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";
import CustomSyntax from "@/components/custom/custom-syntax.vue";
export default {
    components: { Layout, Breadcrumb, CustomSyntax },
  data(){
      return{
        title: 'Placeholders',
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
            text: 'Placeholders',
            active: true,
          },
        ],
      }
  }
}
</script>
