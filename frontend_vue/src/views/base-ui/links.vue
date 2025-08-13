<template>
<Layout>
    <Breadcrumb :title="title" :items="items" />

    <b-row>
        <b-col xl="6">
            <CustomSyntax title="Colored links">
                <template v-slot:sub-text>
                    You can use the <code>.link-*</code> classes to colorize links. Unlike the <a href="ui-utilities.html"><code>.text-*</code> classes</a>, these classes have a <code>:hover</code> and <code>:focus</code> state. Some of the link styles use a relatively light foreground color, and should only be used on a dark background in order to have sufficient contrast.
                </template>
                <template v-slot:preview>
                    <p>
                        <b-link href="#" variant="primary">Primary link</b-link>
                    </p>
                    <p>
                        <b-link href="#" variant="secondary">Secondary link</b-link>
                    </p>
                    <p>
                        <b-link variant="success">Success link</b-link>
                    </p>
                    <p>
                        <b-link variant="danger">Danger link</b-link>
                    </p>
                    <p>
                        <b-link variant="warning">Warning link</b-link>
                    </p>
                    <p>
                        <b-link variant="info">Info link</b-link>
                    </p>
                    <p>
                        <b-link variant="light">Light link</b-link>
                    </p>
                    <p>
                        <b-link variant="dark">Dark link</b-link>
                    </p>
                    <p class="mb-0"><a href="#" class="link-body-emphasis">Emphasis link</a></p>
                </template>
            </CustomSyntax>

        </b-col> <!-- end col -->

        <b-col xl="6">
            <CustomSyntax title="Link utilities">
                <template v-slot:sub-text>
                    <a href="ui-utilities.html">Colored link helpers</a> have been updated to pair with our link utilities. Use the new utilities to modify the link opacity, underline opacity, and underline offset.
                </template>
                <template v-slot:preview>
                    <p>
                        <b-link href="#" variant="primary" linkOffset="2" class="text-decoration-underline link-underline-opacity-25 link-underline-opacity-100-hover">Primary link</b-link>
                    </p>
                    <p>
                        <b-link href="#" variant="secondary" linkOffset="2" class="text-decoration-underline link-underline-opacity-25 link-underline-opacity-100-hover">Secondary link</b-link>
                    </p>
                    <p>
                        <b-link href="#" variant="success" linkOffset="2" class="text-decoration-underline link-underline-opacity-25 link-underline-opacity-100-hover">Success link</b-link>
                    </p>
                    <p>
                        <b-link href="#" variant="danger" linkOffset="2" class="text-decoration-underline link-underline-opacity-25 link-underline-opacity-100-hover">Danger link</b-link>
                    </p>
                    <p>
                        <b-link href="#" variant="warning" linkOffset="2" class="text-decoration-underline link-underline-opacity-25 link-underline-opacity-100-hover">Warning link</b-link>
                    </p>
                    <p>
                        <b-link href="#" variant="info" linkOffset="2" class="text-decoration-underline link-underline-opacity-25 link-underline-opacity-100-hover">Info link</b-link>
                    </p>
                    <p>
                        <b-link href="#" variant="light" linkOffset="2" class="text-decoration-underline link-underline-opacity-25 link-underline-opacity-100-hover">Light link</b-link>
                    </p>
                    <p>
                        <b-link href="#" variant="dark" linkOffset="2" class="text-decoration-underline link-underline-opacity-25 link-underline-opacity-100-hover">Dark link</b-link>
                    </p>
                    <p>
                        <b-link href="#" variant="body-emphasis" linkOffset="2" class="text-decoration-underline link-underline-opacity-25 link-underline-opacity-75-hover">Emphasis link</b-link>
                    </p>
                </template>
            </CustomSyntax>

        </b-col> <!-- end col -->
    </b-row>
    <!--end row-->

    <b-row>
        <b-col xl="6">
            <CustomSyntax title="Link opacity">
                <template v-slot:sub-text>
                    Change the alpha opacity of the link <code>rgba()</code> color value with utilities. Please be aware that changes to a color’s opacity can lead to links with <em>insufficient</em> contrast.
                </template>
                <template v-slot:preview>
                    <p>
                        <b-link class="link-opacity-10" href="#">Link opacity 10</b-link>
                    </p>
                    <p>
                        <b-link class="link-opacity-25" href="#">Link opacity 25</b-link>
                    </p>
                    <p>
                        <b-link class="link-opacity-50" href="#">Link opacity 50</b-link>
                    </p>
                    <p>
                        <b-link class="link-opacity-75" href="#">Link opacity 75</b-link>
                    </p>
                    <p class="mb-0">
                        <a class="link-opacity-100" href="#">Link opacity 100</a>
                    </p>
                </template>
            </CustomSyntax>

        </b-col> <!-- end col -->
        <b-col xl="6">
            <CustomSyntax title="Link hover opacity">
                <template v-slot:sub-text>
                    You can even change the opacity level on hover.
                </template>
                <template v-slot:preview>
                    <p>
                        <b-link class="link-opacity-10-hover" href="#">Link hover opacity 10</b-link>
                    </p>
                    <p>
                        <b-link class="link-opacity-25-hover" href="#">Link hover opacity 25</b-link>
                    </p>
                    <p>
                        <b-link class="link-opacity-50-hover" href="#">Link hover opacity 50</b-link>
                    </p>
                    <p>
                        <b-link class="link-opacity-75-hover" href="#">Link hover opacity 75</b-link>
                    </p>
                    <p class="mb-0">
                        <a class="link-opacity-100-hover" href="#">Link hover opacity 100</a>
                    </p>
                </template>
            </CustomSyntax>

        </b-col> <!-- end col -->
    </b-row>
    <!--end row-->

    <b-row>
        <b-col xl="6">
            <CustomSyntax title="Underline color">
                <template v-slot:sub-text>
                    Change the underline’s color independent of the link text color.
                </template>
                <template v-slot:preview>
                    <p>
                        <b-link href="#" class="text-decoration-underline link-underline-primary">Primary underline</b-link>
                    </p>
                    <p>
                        <b-link href="#" class="text-decoration-underline link-underline-secondary">Secondary underline</b-link>
                    </p>
                    <p>
                        <b-link href="#" class="text-decoration-underline link-underline-success">Success underline</b-link>
                    </p>
                    <p>
                        <b-link href="#" class="text-decoration-underline link-underline-danger">Danger underline</b-link>
                    </p>
                    <p>
                        <b-link href="#" class="text-decoration-underline link-underline-warning">Warning underline</b-link>
                    </p>
                    <p>
                        <b-link href="#" class="text-decoration-underline link-underline-info">Info underline</b-link>
                    </p>
                    <p>
                        <b-link href="#" class="text-decoration-underline link-underline-light">Light underline</b-link>
                    </p>
                    <p class="mb-0">
                        <b-link href="#" class="text-decoration-underline link-underline-dark">Dark underline</b-link>
                    </p>
                </template>
            </CustomSyntax>

        </b-col> <!-- end col -->
        <b-col xl="6">
            <CustomSyntax title="Underline opacity">
                <template v-slot:sub-text>
                    Change the underline’s opacity. Requires adding <code>.link-underline</code> to first set an <code>rgba()</code> color we use to then modify the alpha opacity.
                </template>
                <template v-slot:preview>
                    <p>
                        <b-link linkOffset="2" class="text-decoration-underline link-underline link-underline-opacity-0" href="#">Underline opacity 0</b-link>
                    </p>
                    <p>
                        <b-link linkOffset="2" class="text-decoration-underline link-underline link-underline-opacity-10" href="#">Underline opacity 10</b-link>
                    </p>
                    <p>
                        <b-link linkOffset="2" class="text-decoration-underline link-underline link-underline-opacity-25" href="#">Underline opacity 25</b-link>
                    </p>
                    <p>
                        <b-link linkOffset="2" class="text-decoration-underline link-underline link-underline-opacity-50" href="#">Underline opacity 50</b-link>
                    </p>
                    <p>
                        <b-link linkOffset="2" class="text-decoration-underline link-underline link-underline-opacity-75" href="#">Underline opacity 75</b-link>
                    </p>
                    <p class="mb-0">
                        <b-link linkOffset="2" class="text-decoration-underline link-underline link-underline-opacity-100" href="#">Underline opacity 100</b-link>
                    </p>
                </template>
            </CustomSyntax>

        </b-col> <!-- end col -->
    </b-row>
    <!--end row-->

    <b-row>
        <b-col xl="6">
            <CustomSyntax title="Underline offset">
                <template v-slot:sub-text>
                    Change the underline’s opacity. Requires adding <code>.link-underline</code> to first set an <code>rgba()</code> color we use to then modify the alpha opacity.
                </template>
                <template v-slot:preview>
                    <p>
                        <b-link href="#">Default link</b-link>
                    </p>
                    <p>
                        <b-link linkOffset="1" class="text-decoration-underline" href="#">Offset 1 link</b-link>
                    </p>
                    <p>
                        <b-link linkOffset="2" class="text-decoration-underline" href="#">Offset 2 link</b-link>
                    </p>
                    <p class="mb-0">
                        <b-link linkOffset="3" class="text-decoration-underline" href="#">Offset 3 link</b-link>
                    </p>
                </template>
            </CustomSyntax>

        </b-col> <!-- end col -->
        <b-col xl="6">
            <CustomSyntax title="Hover variants">
                <template v-slot:sub-text>
                    Just like the <code>.link-opacity-*-hover</code> utilities, <code>.link-offset</code> and <code>.link-underline-opacity</code> utilities include <code>:hover</code> variants by default. Mix and match to create unique link styles.
                </template>
                <template v-slot:preview>
                    <b-link linkOffset="2" class="linkOffset-3-hover text-decoration-underline link-underline link-underline-opacity-0 link-underline-opacity-75-hover" href="#">
                        Underline opacity 0
                    </b-link>
                </template>
            </CustomSyntax>

        </b-col> <!-- end col -->
    </b-row>
    <!--end row-->

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
      title: 'Links',
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
          text: 'Links',
          active: true,
        },
      ],
    }
  },
}
</script>s
