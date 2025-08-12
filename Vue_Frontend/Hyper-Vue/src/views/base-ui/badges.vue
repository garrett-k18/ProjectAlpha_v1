<template>
<Layout>
    <Breadcrumb :title="title" :items="items" />

    <b-row>
        <b-col xl="6">
            <CustomSyntax title="Default">
                <template v-slot:sub-text>
                    A simple labeling component. Badges scale to match the size of the immediate parent element by using relative font sizing and <code>em</code> units.
                </template>
                <template v-slot:preview>
                    <h1>h1.Example heading <b-badge variant="secondary">New</b-badge>
                    </h1>
                    <h2>h2.Example heading <b-badge class="bg-success-subtle text-success">New</b-badge>
                    </h2>
                    <h3>h2.Example heading <b-badge variant="primary">New</b-badge>
                    </h3>
                    <h4>h4.Example heading <b-badge href="#" class="bg-info-subtle text-info">Info Link</b-badge>
                    </h4>
                    <h5>h5.Example heading <b-badge variant="text-warning" class="badge-outline-warning">New</b-badge>
                    </h5>
                    <h6>h6.Example heading <b-badge class="bg-danger">New</b-badge>
                    </h6>
                </template>
            </CustomSyntax>

            <CustomSyntax title="Pill Badges">
                <template v-slot:sub-text>
                    Use the <code>.rounded-pill</code> modifier class to make badges more rounded.
                </template>
                <template v-slot:preview>
                    <b-badge pill variant="primary">Primary</b-badge>
                    <b-badge pill class="text-light ms-1" variant="secondary">Secondary</b-badge>
                    <b-badge pill variant="success" class="ms-1">Success</b-badge>
                    <b-badge pill class="bg-danger ms-1">Danger</b-badge>
                    <b-badge pill class="bg-warning ms-1">Warning</b-badge>
                    <b-badge pill class="bg-info ms-1">Info</b-badge>
                    <b-badge pill variant="light" class="ms-1">Light</b-badge>
                    <b-badge pill variant="dark" class="ms-1">Dark</b-badge>

                    <h5 class="mt-4">Lighten Badges</h5>
                    <p class="text-muted font-14 mb-3">
                        Use the <code>.badge-*-lighten</code> modifier class to make badges lighten.
                    </p>

                    <b-badge pill class="bg-primary-subtle text-primary">Primary</b-badge>
                    <b-badge pill class="bg-secondary-subtle text-secondary ms-1">Secondary</b-badge>
                    <b-badge pill class="bg-success-subtle text-success ms-1">Success</b-badge>
                    <b-badge pill class="bg-danger-subtle text-danger ms-1">Danger</b-badge>
                    <b-badge pill class="bg-warning-subtle text-warning ms-1">Warning</b-badge>
                    <b-badge pill class="bg-info-subtle text-info ms-1">Info</b-badge>
                    <b-badge pill class="bg-dark-subtle text-dark ms-1">Dark</b-badge>

                    <h5 class="mt-4">Outline Badges</h5>
                    <p class="text-muted font-14 mb-3">
                        Using the <code>.badge-outline-*</code> to quickly create a bordered badges.
                    </p>

                    <b-badge pill class="badge-outline-primary" variant="text-primary">Primary</b-badge>
                    <b-badge pill class="badge-outline-secondary ms-1" variant="text-secondary">Secondary</b-badge>
                    <b-badge pill class="badge-outline-success ms-1" variant="text-success">Success</b-badge>
                    <b-badge pill class="badge-outline-danger ms-1" variant="text-danger">Danger</b-badge>
                    <b-badge pill class="badge-outline-warning ms-1" variant="text-warning">Warning</b-badge>
                    <b-badge pill class="badge-outline-info ms-1" variant="text-info">Info</b-badge>
                    <b-badge pill class="badge-outline-dark ms-1" variant="text-dark">Dark</b-badge>
                </template>
            </CustomSyntax>
        </b-col> <!-- end col-->
        <b-col xl="6">
            <CustomSyntax title="Contextual variations">
                <template v-slot:sub-text>
                    Add any of the below mentioned modifier classes to change the appearance of a badge.
                    Badge can be more contextual as well. Just use regular convention e.g. <code>badge-*color</code>, <code>bg-primary</code>
                    to have badge with different background.
                </template>
                <template v-slot:preview>
                    <b-badge variant="primary">Primary</b-badge>
                    <b-badge class="bg-secondary ms-1">Secondary</b-badge>
                    <b-badge class="bg-success ms-1">Success</b-badge>
                    <b-badge class="bg-danger ms-1">Danger</b-badge>
                    <b-badge class="bg-warning ms-1">Warning</b-badge>
                    <b-badge class="bg-info ms-1">Info</b-badge>
                    <b-badge variant="light" class="text-dark ms-1">Light</b-badge>
                    <b-badge variant="dark" class="text-light ms-1">Dark</b-badge>
                    <h5 class="mt-4">Lighten Badges</h5>
                    <p class="text-muted font-14 mb-3">
                        Using the <code>.badge-*-lighten</code> modifier class, you can have more soften variation.
                    </p>

                    <b-badge class="bg-primary-subtle text-primary">Primary</b-badge>
                    <b-badge class="bg-secondary-subtle text-secondary ms-1">Secondary</b-badge>
                    <b-badge class="bg-success-subtle text-success ms-1">Success</b-badge>
                    <b-badge class="bg-danger-subtle text-danger ms-1">Danger</b-badge>
                    <b-badge class="bg-warning-subtle text-warning ms-1">Warning</b-badge>
                    <b-badge class="bg-info-subtle text-info ms-1">Info</b-badge>
                    <b-badge class="bg-dark-subtle text-dark ms-1">Dark</b-badge>

                    <h5 class="mt-4">Outline Badges</h5>
                    <p class="text-muted font-14 mb-3">
                        Using the <code>.badge-outline-*</code> to quickly create a bordered badges.
                    </p>

                    <b-badge class="badge-outline-primary" variant="text-primary">Primary</b-badge>
                    <b-badge class="badge-outline-secondary ms-1" variant="text-secondary">Secondary</b-badge>
                    <b-badge class="badge-outline-success ms-1" variant="text-success">Success</b-badge>
                    <b-badge class="badge-outline-danger ms-1" variant="text-danger">Danger</b-badge>
                    <b-badge class="badge-outline-warning ms-1" variant="text-warning">Warning</b-badge>
                    <b-badge class="badge-outline-info ms-1" variant="text-info">Info</b-badge>
                    <b-badge class="badge-outline-dark ms-1" variant="text-dark">Dark</b-badge>
                </template>
            </CustomSyntax>

            <CustomSyntax title="Badge Positioned">
                <template v-slot:sub-text>
                    Use utilities to modify a <code>.badge</code> and position it in the corner of a
                    link or button.
                </template>
                <template v-slot:preview>
                    <b-row>
                        <b-col cols="6">
                            <b-button class="position-relative" variant="primary">
                                Inbox
                                <b-badge pill class="position-absolute top-0 start-100 translate-middle bg-danger">
                                    99+
                                    <span class="visually-hidden">unread messages</span>
                                </b-badge>
                            </b-button>
                        </b-col>
                        <b-col cols="6">
                            <b-button class="position-relative" variant="primary">
                                Profile
                                <b-badge class="position-absolute top-0 start-100 translate-middle p-1 bg-danger border border-light rounded-circle">
                                    <span class="visually-hidden">New alerts</span>
                                </b-badge>
                            </b-button>
                        </b-col>
                        <b-col cols="6">
                            <b-button class="mt-4" variant="success">
                                Notifications <b-badge class="bg-light text-dark ms-1">4</b-badge>
                            </b-button>
                        </b-col>
                    </b-row>
                </template>
            </CustomSyntax>

        </b-col> <!-- end col -->
    </b-row>
    <!-- end row -->
</Layout>
</template>

<script lang="ts">
import Layout from '@/components/layouts/layout.vue';
import Breadcrumb from '@/components/breadcrumb.vue';
import CustomSyntax from "@/components/custom/custom-syntax.vue";
export default {
    components: { Layout, Breadcrumb, CustomSyntax },
  data() {
    return {
      title: 'Badges',
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
          text: 'Badges',
          active: true,
        },
      ],
    }
  },
}
</script>
