<template>
<Layout>
    <Breadcrumb :title="title" :items="items" />

    <b-row>
        <b-col xl="6">
            <CustomSyntax title="Default Buttons">
                <template v-slot:sub-text>
                    Use the button classes on an <code>&lt;a&gt;</code>, <code>&lt;button&gt;</code>, or <code>&lt;input&gt;</code> element.
                </template>
                <template v-slot:preview>
                    <div class="d-flex flex-wrap gap-2">
                        <b-button variant="primary">Primary</b-button>
                        <b-button variant="secondary">Secondary</b-button>
                        <b-button variant="success">Success</b-button>
                        <b-button variant="danger">Danger</b-button>
                        <b-button variant="warning">Warning</b-button>
                        <b-button variant="info">Info</b-button>
                        <b-button variant="light">Light</b-button>
                        <b-button variant="dark">Dark</b-button>
                        <b-button variant="link">Link</b-button>
                    </div>
                </template>
            </CustomSyntax>
        </b-col> <!-- end col -->

        <b-col xl="6">
            <CustomSyntax title="Button Outline">
                <template v-slot:sub-text>
                    Use a classes <code>.btn-outline-**</code> to quickly create a bordered buttons.
                </template>
                <template v-slot:preview>
                    <div class="d-flex flex-wrap gap-2">
                        <b-button variant="outline-primary">Primary</b-button>
                        <b-button variant="outline-secondary">Secondary</b-button>
                        <b-button variant="outline-success"><i class="uil-cloud-computing"></i> Success</b-button>
                        <b-button variant="outline-danger">Danger</b-button>
                        <b-button variant="outline-warning">Warning</b-button>
                        <b-button variant="outline-info"><i class="uil-circuit"></i> Info</b-button>
                        <b-button variant="outline-light">Light</b-button>
                        <b-button variant="outline-dark">Dark</b-button>
                    </div>
                </template>
            </CustomSyntax>
        </b-col>
    </b-row> <!-- end row -->

    <b-row>
        <b-col xl="6">
            <CustomSyntax title="Button-Rounded">
                <template v-slot:sub-text>
                    Add <code>.rounded-pill</code> to default button to get rounded corners.
                </template>
                <template v-slot:preview>
                    <div class="d-flex flex-wrap gap-2">
                        <b-button pill variant="primary">Primary</b-button>
                        <b-button pill variant="secondary">Secondary</b-button>
                        <b-button pill variant="success">Success</b-button>
                        <b-button pill variant="danger">Danger</b-button>
                        <b-button pill variant="warning">Warning</b-button>
                        <b-button pill variant="info">Info</b-button>
                        <b-button pill variant="light">Light</b-button>
                        <b-button pill variant="dark">Dark</b-button>
                    </div>
                </template>
            </CustomSyntax>

        </b-col> <!-- end col -->

        <b-col xl="6">
            <CustomSyntax title="Button Outline Rounded">
                <template v-slot:sub-text>
                    Use a classes <code>.btn-outline-**</code> to quickly create a bordered buttons.
                </template>
                <template v-slot:preview>
                    <div class="d-flex flex-wrap gap-2">
                        <b-button pill variant="outline-primary">Primary</b-button>
                        <b-button pill variant="outline-secondary">Secondary</b-button>
                        <b-button pill variant="outline-success"><i class="uil-cloud-computing"></i> Success</b-button>
                        <b-button pill variant="outline-danger">Danger</b-button>
                        <b-button pill variant="outline-warning">Warning</b-button>
                        <b-button pill variant="outline-info"><i class="uil-circuit"></i> Info</b-button>
                        <b-button pill variant="outline-light">Light</b-button>
                        <b-button pill variant="outline-dark">Dark</b-button>
                    </div>
                </template>
            </CustomSyntax>
        </b-col> <!-- end col -->
    </b-row> <!-- end row -->

    <b-row>
        <b-col xl="6">
            <CustomSyntax title="Soft Buttons">
                <template v-slot:sub-text>
                    Use a classes <code>.btn-soft-**</code> to quickly create a soft background color buttons.
                </template>
                <template v-slot:preview>
                    <div class="d-flex flex-wrap gap-2">
                        <b-button variant="soft-primary">Primary</b-button>
                        <b-button variant="soft-secondary">Secondary</b-button>
                        <b-button variant="soft-success">Success</b-button>
                        <b-button variant="soft-danger">Danger</b-button>
                        <b-button variant="soft-warning">Warning</b-button>
                        <b-button variant="soft-info">Info</b-button>
                        <b-button variant="soft-dark">Dark</b-button>
                    </div>
                </template>
            </CustomSyntax>
        </b-col> <!-- end col -->

        <b-col xl="6">
            <CustomSyntax title="Soft Rounded Buttons">
                <template v-slot:sub-text>
                    Use a classes <code>.btn-soft-**</code> <code>.rounded-pill</code> to quickly create a soft background color buttons with rounded.
                </template>
                <template v-slot:preview>
                    <div class="d-flex flex-wrap gap-2">
                        <b-button pill variant="primary">Primary</b-button>
                        <b-button pill variant="secondary">Secondary</b-button>
                        <b-button pill variant="success">Success</b-button>
                        <b-button pill variant="danger">Danger</b-button>
                        <b-button pill variant="warning">Warning</b-button>
                        <b-button pill variant="info">Info</b-button>
                        <b-button pill variant="dark">Dark</b-button>
                    </div>
                </template>
            </CustomSyntax>
        </b-col> <!-- end col -->
    </b-row> <!-- end row -->

    <b-row>
        <b-col xl="6">
            <CustomSyntax title="Button-Sizes">
                <template v-slot:sub-text>
                    Add <code>.btn-lg</code>, <code>.btn-sm</code> for additional sizes.
                </template>
                <template v-slot:preview>
                    <div class="d-flex flex-wrap align-items-center gap-2">
                        <b-button variant="primary" size="lg">Large</b-button>
                        <b-button variant="info">Normal</b-button>
                        <b-button variant="success" size="sm">Small</b-button>
                    </div>
                </template>
            </CustomSyntax>
        </b-col> <!-- end col -->

        <b-col xl="6">
            <CustomSyntax title="Button-Disabled">
                <template v-slot:sub-text>
                    Add the <code>disabled</code> attribute to <code>&lt;button&gt;</code> buttons.
                </template>
                <template v-slot:preview>
                    <div class="d-flex flex-wrap gap-2">
                        <b-button variant="info" disabled>Info</b-button>
                        <b-button variant="success" disabled>Success</b-button>
                        <b-button variant="danger" disabled>Danger</b-button>
                        <b-button variant="dark" disabled>Dark</b-button>
                    </div>
                </template>
            </CustomSyntax>
        </b-col> <!-- end col -->
    </b-row> <!-- end row -->

    <b-row>
        <b-col xl="6">
            <CustomSyntax title="Icon Buttons">
                <template v-slot:sub-text>
                    Icon only button.
                </template>
                <template v-slot:preview>
                    <div class="d-flex flex-wrap gap-2">
                        <b-button variant="light"><i class="mdi mdi-heart-outline"></i> </b-button>
                        <b-button variant="danger"><i class="mdi mdi-window-close"></i> </b-button>
                        <b-button variant="dark"><i class="mdi mdi-music"></i> </b-button>
                        <b-button variant="primary"><i class="mdi mdi-star"></i> </b-button>
                        <b-button variant="success"><i class="mdi mdi-thumb-up-outline"></i> </b-button>
                        <b-button variant="info"><i class="mdi mdi-keyboard"></i> </b-button>
                        <b-button variant="warning"><i class="mdi mdi-wrench"></i> </b-button>

                        <b-button variant="light"><i class="mdi mdi-heart me-1"></i> <span>Like</span> </b-button>
                        <b-button variant="warning"><i class="mdi mdi-rocket me-1"></i> <span>Launch</span> </b-button>
                        <b-button variant="info"><i class="mdi mdi-cloud me-1"></i> <span>Cloud Hosting</span> </b-button>

                        <b-button variant="outline-success"><i class="uil-money-withdrawal"></i> Money</b-button>
                        <b-button variant="outline-primary"><i class="uil-paypal"></i> PayPal</b-button>
                        <b-button variant="outline-danger"><i class="uil-cog"></i> Settings</b-button>
                    </div>
                </template>
            </CustomSyntax>
        </b-col> <!-- end col -->

        <b-col xl="6">
            <CustomSyntax title="Block Button">
                <template v-slot:sub-text>
                    Create block level buttons by adding class <code>.d-grid</code> to parent div.
                </template>
                <template v-slot:preview>
                    <div class="d-grid gap-2">
                        <b-button size="sm" variant="primary">Block Button</b-button>
                        <b-button size="lg" variant="success">Block Button</b-button>
                    </div>
                </template>
            </CustomSyntax>
        </b-col> <!-- end col -->
    </b-row> <!-- end row -->

    <b-row>
        <b-col xl="6">
            <CustomSyntax title="Button Group">
                <template v-slot:sub-text>
                    Wrap a series of buttons with <code>.btn</code> in <code>.btn-group</code>.
                </template>
                <template v-slot:preview>
                    <b-button-group class="mb-2">
                        <b-button variant="light">Left</b-button>
                        <b-button variant="light">Middle</b-button>
                        <b-button variant="light">Right</b-button>
                    </b-button-group>

                    <br>

                    <b-button-group class="mb-2">
                        <b-button variant="light">1</b-button>
                        <b-button variant="light">2</b-button>
                        <b-button variant="light">3</b-button>
                        <b-button variant="light">4</b-button>
                    </b-button-group>

                    <b-button-group class="mb-2">
                        <b-button variant="light">5</b-button>
                        <b-button variant="light">6</b-button>
                        <b-button variant="light">7</b-button>
                    </b-button-group>

                    <b-button-group class="mb-2">
                        <b-button variant="light">8</b-button>
                    </b-button-group>

                    <br>

                    <b-button-group class="mb-2">
                        <b-button variant="light">1</b-button>
                        <b-button variant="primary">2</b-button>
                        <b-button variant="light">3</b-button>
                        <b-button-group>
                            <b-dropdown text="Dropdown" variant="light">
                                <b-dropdown-item href="#">Dropdown link</b-dropdown-item>
                                <b-dropdown-item href="#">Dropdown link</b-dropdown-item>
                            </b-dropdown>
                        </b-button-group>
                    </b-button-group>

                    <b-row>
                        <b-col md="3">
                            <b-button-group vertical class="mb-2">
                                <b-button variant="light">Top</b-button>
                                <b-button variant="light">Middle</b-button>
                                <b-button variant="light">Bottom</b-button>
                            </b-button-group>
                        </b-col>
                        <b-col md="3">
                            <b-button-group vertical class="mb-2">
                                <b-button variant="light">Button 1</b-button>
                                <b-button variant="light">Button 2</b-button>
                                <b-dropdown variant="light" text="Button 3">
                                    <b-dropdown-item href="#">Dropdown link</b-dropdown-item>
                                    <b-dropdown-item href="#">Dropdown link</b-dropdown-item>
                                </b-dropdown>
                            </b-button-group>
                        </b-col>
                    </b-row>
                </template>
            </CustomSyntax>
        </b-col> <!-- end col -->

        <b-col xl="6">
            <b-row>
                <b-col xl="12">
                    <CustomSyntax title="Toggle Button">
                        <template v-slot:sub-text>
                            Add <code>data-bs-toggle="button"</code> to toggle a button�s <code>active</code> state. If you�re pre-toggling a button, you must manually add the <code>.active</code> class <strong>and</strong> <code>aria-pressed="true"</code> to ensure that it is conveyed appropriately to assistive technologies.
                        </template>
                        <template v-slot:preview>
                            <b-button variant="primary" data-bs-toggle="button">Toggle button</b-button>
                            <b-button variant="primary" active data-bs-toggle="button" aria-pressed="true">Active toggle button</b-button>
                            <b-button variant="primary" disabled data-bs-toggle="button">Disabled toggle button</b-button>
                        </template>
                    </CustomSyntax>
                </b-col>
                <!--end col-->
                <b-col xl="12">
                    <CustomSyntax title="Button tags">
                        <template v-slot:sub-text>
                            The <code>.btn</code> classes are designed to be used with the <code>&lt;button&gt;</code> element. However, you can also use these classes on <code>&lt;a&gt;</code> or <code>&lt;input&gt;</code> elements (though some browsers may apply a slightly different rendering).
                        </template>
                        <template v-slot:preview>
                            <a class="btn btn-primary" href="#" role="button">Link</a>
                            <b-button variant="primary" type="submit">Button</b-button>
                            <input class="btn btn-primary" type="button" value="Input">
                            <input class="btn btn-primary" type="submit" value="Submit">
                            <input class="btn btn-primary" type="reset" value="Reset">
                        </template>
                    </CustomSyntax>
                </b-col>
            </b-row>
            <!--end row-->
        </b-col> <!-- end col -->

    </b-row> <!-- end row -->

    <b-row>
        <b-col xl="6">
            <CustomSyntax title="Basic Button">
                <template v-slot:sub-text>
                    Bootstrap has a base <code>.btn</code> class that sets up basic styles such as padding and content alignment. By default, <code>.btn</code> controls have a transparent border and background color, and lack any explicit focus and hover styles.
                </template>
                <template v-slot:preview>
                    <b-button class="btn">Base class</b-button>
                </template>
            </CustomSyntax>
        </b-col> <!-- end col -->

        <b-col xl="6">
            <CustomSyntax title="Focus Ring Custom">
                <template v-slot:sub-text>
                    Click directly on the link below to see the focus ring in action, or into the example below and then press <kbd>Tab</kbd>.
                </template>
                <template v-slot:preview>
                    <a href="#" class="d-inline-flex focus-ring py-1 px-2 text-decoration-none border rounded-2">
                        Custom focus ring
                    </a>

                    <a href="#" class="d-inline-flex focus-ring py-1 px-2 text-decoration-none border rounded-2" style="--ct-focus-ring-color: rgba(var(--ct-success-rgb), .25)">
                        Green focus ring
                    </a>

                    <a href="#" class="d-inline-flex focus-ring py-1 px-2 text-decoration-none border rounded-2" style="--ct-focus-ring-x: 10px; --ct-focus-ring-y: 10px; --ct-focus-ring-blur: 4px">
                        Blurry offset focus ring
                    </a>
                </template>
            </CustomSyntax>
        </b-col> <!-- end col -->
    </b-row>
    <!--end row-->

    <b-row>
        <b-col xl="6">
            <CustomSyntax title="Focus Ring Utilities">
                <template v-slot:sub-text>
                    In addition to <code>.focus-ring</code>, we have several <code>.focus-ring-*</code> utilities to modify the helper class defaults. Modify the color with any of our <a href="ui-utilities.html">theme colors</a>. Note that the light and dark variants may not be visible on all background colors given current color mode support.
                </template>
                <template v-slot:preview>
                    <p><a href="#" class="d-inline-flex focus-ring focus-ring-primary py-1 px-2 text-decoration-none border rounded-2">Primary focus</a></p>
                    <p><a href="#" class="d-inline-flex focus-ring focus-ring-secondary py-1 px-2 text-decoration-none border rounded-2">Secondary focus</a></p>
                    <p><a href="#" class="d-inline-flex focus-ring focus-ring-success py-1 px-2 text-decoration-none border rounded-2">Success focus</a></p>
                    <p><a href="#" class="d-inline-flex focus-ring focus-ring-danger py-1 px-2 text-decoration-none border rounded-2">Danger focus</a></p>
                    <p><a href="#" class="d-inline-flex focus-ring focus-ring-warning py-1 px-2 text-decoration-none border rounded-2">Warning focus</a></p>
                    <p><a href="#" class="d-inline-flex focus-ring focus-ring-info py-1 px-2 text-decoration-none border rounded-2">Info focus</a></p>
                    <p><a href="#" class="d-inline-flex focus-ring focus-ring-light py-1 px-2 text-decoration-none border rounded-2">Light focus</a></p>
                    <p class="mb-0"><a href="#" class="d-inline-flex focus-ring focus-ring-dark py-1 px-2 text-decoration-none border rounded-2">Dark focus</a></p>
                </template>
            </CustomSyntax>
        </b-col> <!-- end col -->
    </b-row>

</Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";
import CustomSyntax from "@/components/custom/custom-syntax.vue";
export default {
    components: { CustomSyntax, Breadcrumb, Layout },
  data() {
    return {
      title: 'Buttons',
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
          text: 'Buttons',
          active: true,
        },
      ],
    }
  },
}
</script>
