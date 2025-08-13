<template>
<Layout>
    <Breadcrumb :title="title" :items="items" />

    <b-row>
        <b-col xl="4">
            <CustomSyntax title="Basic example">
                <template v-slot:sub-text>
                    The most basic list group is an unordered list with list items and the proper classes.
                    Build upon it with the options that follow, or with your own CSS as needed.
                </template>
                <template v-slot:preview>
                    <b-list-group>
                        <b-list-group-item><i class="uil-google-drive-alt me-1"></i> Google Drive</b-list-group-item>
                        <b-list-group-item><i class="uil-facebook-messenger me-1"></i> Facebook Messenger</b-list-group-item>
                        <b-list-group-item><i class="uil-apple me-1"></i> Apple Technology Company</b-list-group-item>
                        <b-list-group-item><i class="uil-intercom me-1"></i> Intercom Support System</b-list-group-item>
                        <b-list-group-item><i class="uil-paypal me-1"></i> Paypal Payment Gateway</b-list-group-item>
                    </b-list-group>
                </template>
            </CustomSyntax>
        </b-col> <!-- end col -->

        <b-col xl="4">
            <CustomSyntax title="Active items">
                <template v-slot:sub-text>
                    Add <code>.active</code> to a <code>.list-group-item</code> to indicate the current active selection.
                </template>
                <template v-slot:preview>
                    <b-list-group>
                        <b-list-group-item active><i class="uil-google-drive-alt me-1"></i> Google Drive</b-list-group-item>
                        <b-list-group-item><i class="uil-facebook-messenger me-1"></i> Facebook Messenger</b-list-group-item>
                        <b-list-group-item><i class="uil-apple me-1"></i> Apple Technology Company</b-list-group-item>
                        <b-list-group-item><i class="uil-intercom me-1"></i> Intercom Support System</b-list-group-item>
                        <b-list-group-item><i class="uil-paypal me-1"></i> Paypal Payment Gateway</b-list-group-item>
                    </b-list-group>
                </template>
            </CustomSyntax>
        </b-col>

        <b-col xl="4">
            <CustomSyntax title="Disabled items">
                <template v-slot:sub-text>
                    Add <code>.disabled</code> to a <code>.list-group-item</code> to make it <em>appear</em> disabled.
                </template>
                <template v-slot:preview>
                    <b-list-group>
                        <b-list-group-item disabled><i class="uil-google-drive-alt me-1"></i> Google Drive</b-list-group-item>
                        <b-list-group-item><i class="uil-facebook-messenger me-1"></i> Facebook Messenger</b-list-group-item>
                        <b-list-group-item><i class="uil-apple me-1"></i> Apple Technology Company</b-list-group-item>
                        <b-list-group-item><i class="uil-intercom me-1"></i> Intercom Support System</b-list-group-item>
                        <b-list-group-item><i class="uil-paypal me-1"></i> Paypal Payment Gateway</b-list-group-item>
                    </b-list-group>
                </template>
            </CustomSyntax>

        </b-col> <!-- end col -->

    </b-row>
    <!-- end row -->

    <b-row>
        <b-col xl="4">
            <CustomSyntax title="Links and Buttons">
                <template v-slot:sub-text>
                    Use <code>&lt;a&gt;</code>s or <code>&lt;button&gt;</code>s to create <em>actionable</em> list group items with hover, disabled, and active states by adding <code>.list-group-item-action</code>.
                </template>
                <template v-slot:preview>
                    <b-list-group>
                        <b-list-group-item href="#" active>
                            Paypal Payment Gateway
                        </b-list-group-item>
                        <b-list-group-item action href="#">Google Drive</b-list-group-item>
                        <b-list-group-item action type="button">Facebook Messenger</b-list-group-item>
                        <b-list-group-item action type="button">Apple Technology Company</b-list-group-item>
                        <b-list-group-item href="#" disabled>Intercom Support System</b-list-group-item>
                    </b-list-group>
                </template>
            </CustomSyntax>

        </b-col> <!-- end col -->

        <b-col xl="4">
            <CustomSyntax title="Flush">
                <template v-slot:sub-text>
                    Add <code>.list-group-flush</code> to remove some borders and rounded corners to render list group items edge-to-edge in a parent container (e.g., cards).
                </template>
                <template v-slot:preview>
                    <b-list-group flush>
                        <b-list-group-item>Google Drive</b-list-group-item>
                        <b-list-group-item>Facebook Messenger</b-list-group-item>
                        <b-list-group-item>Apple Technology Company</b-list-group-item>
                        <b-list-group-item>Intercom Support System</b-list-group-item>
                        <b-list-group-item>Paypal Payment Gateway</b-list-group-item>
                    </b-list-group>
                </template>
            </CustomSyntax>

        </b-col> <!-- end col -->

        <b-col xl="4">
            <CustomSyntax title="Horizontal">
                <template v-slot:sub-text>
                    Add <code>.list-group-horizontal</code> to change the layout of list group items from vertical to horizontal across all breakpoints. Alternatively, choose a responsive variant <code>.list-group-horizontal-{sm|md|lg|xl}</code> to make a list group horizontal starting at that breakpoint’s <code>min-width</code>.
                </template>
                <template v-slot:preview>
                    <b-list-group horizontal class="mb-3">
                        <b-list-group-item>Google</b-list-group-item>
                        <b-list-group-item>Whatsapp</b-list-group-item>
                        <b-list-group-item>Facebook</b-list-group-item>
                    </b-list-group>

                    <b-list-group horizontal="sm" class="mb-3">
                        <b-list-group-item>Apple</b-list-group-item>
                        <b-list-group-item>PayPal</b-list-group-item>
                        <b-list-group-item>Intercom</b-list-group-item>
                    </b-list-group>

                    <b-list-group horizontal="md">
                        <b-list-group-item>Google</b-list-group-item>
                        <b-list-group-item>Whatsapp</b-list-group-item>
                        <b-list-group-item>Facebook</b-list-group-item>
                    </b-list-group>
                </template>
            </CustomSyntax>

        </b-col> <!-- end col -->
    </b-row>
    <!-- end row -->

    <b-row>
        <b-col xl="4">
            <CustomSyntax title="Contextual classes">
                <template v-slot:sub-text>
                    Use contextual classes to style list items with a stateful background and color.
                </template>
                <template v-slot:preview>
                    <b-list-group>
                        <b-list-group-item>Dapibus ac facilisis in</b-list-group-item>
                        <b-list-group-item variant="primary">A simple primary list group item</b-list-group-item>
                        <b-list-group-item variant="secondary">A simple secondary list group item</b-list-group-item>
                        <b-list-group-item variant="success">A simple success list group item</b-list-group-item>
                        <b-list-group-item variant="danger">A simple danger list group item</b-list-group-item>
                        <b-list-group-item variant="warning">A simple warning list group item</b-list-group-item>
                        <b-list-group-item variant="info">A simple info list group item</b-list-group-item>
                        <b-list-group-item variant="light">A simple light list group item</b-list-group-item>
                        <b-list-group-item variant="dark">A simple dark list group item</b-list-group-item>
                    </b-list-group>
                </template>
            </CustomSyntax>

        </b-col> <!-- end col -->

        <b-col xl="4">
            <CustomSyntax title="Contextual classes with Link">
                <template v-slot:sub-text>
                    Use contextual classes to style list items with a stateful background and color.
                </template>
                <template v-slot:preview>
                    <b-list-group>
                        <b-list-group-item href="#" action>Dapibus ac facilisis in</b-list-group-item>
                        <b-list-group-item href="#" action variant="primary">A simple primary list group item</b-list-group-item>
                        <b-list-group-item href="#" action variant="secondary">A simple secondary list group item</b-list-group-item>
                        <b-list-group-item href="#" action variant="success">A simple success list group item</b-list-group-item>
                        <b-list-group-item href="#" action variant="danger">A simple danger list group item</b-list-group-item>
                        <b-list-group-item href="#" action variant="warning">A simple warning list group item</b-list-group-item>
                        <b-list-group-item href="#" action variant="info">A simple info list group item</b-list-group-item>
                        <b-list-group-item href="#" action variant="light">A simple light list group item</b-list-group-item>
                        <b-list-group-item href="#" action variant="dark">A simple dark list group item</b-list-group-item>
                    </b-list-group>
                </template>
            </CustomSyntax>

        </b-col> <!-- end col -->

        <b-col xl="4">
            <CustomSyntax title="Custom content">
                <template v-slot:sub-text>
                    Add nearly any HTML within, even for linked list groups like the one below, with the help of flexbox utilities.
                </template>
                <template v-slot:preview>
                    <b-list-group>
                        <b-list-group-item href="#" active action>
                            <div class="d-flex w-100 justify-content-between">
                                <h5 class="mb-1">List group item heading</h5>
                                <small>3 days ago</small>
                            </div>
                            <p class="mb-1">Donec id elit non mi porta gravida at eget metus. Maecenas sed diam eget risus varius blandit.</p>
                            <small>Donec id elit non mi porta.</small>
                        </b-list-group-item>
                        <b-list-group-item href="#" action>
                            <div class="d-flex w-100 justify-content-between">
                                <h5 class="mb-1">List group item heading</h5>
                                <small class="text-muted">3 days ago</small>
                            </div>
                            <p class="mb-1">Donec id elit non mi porta gravida at eget metus. Maecenas sed diam eget risus varius blandit.</p>
                            <small class="text-muted">Donec id elit non mi porta.</small>
                        </b-list-group-item>
                        <b-list-group-item href="#" action>
                            <div class="d-flex w-100 justify-content-between">
                                <h5 class="mb-1">List group item heading</h5>
                                <small class="text-muted">3 days ago</small>
                            </div>
                            <p class="mb-1">Donec id elit non mi porta gravida at eget metus. Maecenas sed diam eget risus varius blandit.</p>
                            <small class="text-muted">Donec id elit non mi porta.</small>
                        </b-list-group-item>
                    </b-list-group>
                </template>
            </CustomSyntax>

        </b-col> <!-- end col -->

    </b-row>
    <!-- end row -->

    <b-row>
        <b-col xl="4">
            <CustomSyntax title="With badges">
                <template v-slot:sub-text>
                    Add badges to any list group item to show unread counts, activity, and more with the help of some utilities.
                </template>
                <template v-slot:preview>
                    <b-list-group>
                        <b-list-group-item class="d-flex justify-content-between align-items-center">
                            Gmail Emails
                            <b-badge pill variant="primary">14</b-badge>
                        </b-list-group-item>
                        <b-list-group-item class="d-flex justify-content-between align-items-center">
                            Pending Payments
                            <b-badge pill variant="success">2</b-badge>
                        </b-list-group-item>
                        <b-list-group-item class="d-flex justify-content-between align-items-center">
                            Action Needed
                            <b-badge pill variant="danger">99+</b-badge>
                        </b-list-group-item>
                        <b-list-group-item class="d-flex justify-content-between align-items-center">
                            Payments Done
                            <b-badge pill variant="success">20+</b-badge>
                        </b-list-group-item>
                        <b-list-group-item class="d-flex justify-content-between align-items-center">
                            Pending Payments
                            <b-badge pill variant="warning" class="text-white">12</b-badge>
                        </b-list-group-item>
                    </b-list-group>
                </template>
            </CustomSyntax>

        </b-col> <!-- end col -->

        <b-col xl="4">
            <CustomSyntax title="Checkboxes and radios">
                <template v-slot:sub-text>
                    Place Bootstrap’s checkboxes and radios within list group items and customize as needed. You can use them without <code>&lt;label&gt;</code>s, but please remember to include an <code>aria-label</code> attribute and value for accessibility.
                </template>
                <template v-slot:preview>
                    <b-list-group>
                        <b-list-group-item>
                            <b-form-checkbox class="me-1" value="" id="firstCheckbox">First checkbox</b-form-checkbox>
                        </b-list-group-item>
                        <b-list-group-item>
                            <b-form-checkbox class="me-1" value="" id="secondCheckbox">Second checkbox</b-form-checkbox>
                        </b-list-group-item>
                    </b-list-group>

                    <b-list-group class="mt-2">
                        <b-list-group-item>
                            <b-form-radio class="me-1" v-model="checked" name="listGroupRadio" value="1" id="firstRadio">First radio</b-form-radio>
                        </b-list-group-item>
                        <b-list-group-item>
                            <b-form-radio class="me-1" v-model="checked" name="listGroupRadio" value="2" id="secondRadio">Second radio</b-form-radio>
                        </b-list-group-item>
                    </b-list-group>
                </template>
            </CustomSyntax>

        </b-col> <!-- end col -->

        <b-col xl="4">
            <CustomSyntax title="Numbered">
                <template v-slot:sub-text>
                    Numbers are generated by <code>counter-reset</code> on the <code>&lt;ol&gt;</code>, and then styled and placed with a <code>::before</code> psuedo-element on the <code>&lt;li&gt;</code> with <code>counter-increment</code> and <code>content</code>.
                </template>
                <template v-slot:preview>
                    <b-list-group numbered>
                        <b-list-group-item class="d-flex justify-content-between align-items-start">
                            <div class="ms-2 me-auto">
                                <div class="fw-bold">Attex Admin</div>
                                Attex Admin
                            </div>
                            <b-badge pill variant="primary">865</b-badge>
                        </b-list-group-item>
                        <b-list-group-item class="d-flex justify-content-between align-items-start">
                            <div class="ms-2 me-auto">
                                <div class="fw-bold">Attex React Admin</div>
                                Attex React Admin
                            </div>
                            <b-badge pill variant="primary">140</b-badge>
                        </b-list-group-item>
                        <b-list-group-item class="d-flex justify-content-between align-items-start">
                            <div class="ms-2 me-auto">
                                <div class="fw-bold">Angular Version</div>
                                Angular Version
                            </div>
                            <b-badge pill variant="primary">85</b-badge>
                        </b-list-group-item>
                    </b-list-group>
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
              title: 'List Group',
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
                  text: 'List Group',
                  active: true,
                },
              ],

            checked: "1",
        };
    },
}
</script>
