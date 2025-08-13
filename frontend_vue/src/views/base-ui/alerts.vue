<template>
<Layout>
    <breadcrumb :title="title" :items="items" />

    <b-row>
        <b-col xl="6">
            <CustomSyntax title="Default Alert">
                <template v-slot:sub-text>
                    Provide contextual feedback messages for typical user actions with the handful of available and flexible alert messages.
                    Alerts are available for any length of text, as well as an optional dismiss
                    button.
                </template>
                <template v-slot:preview>
                    <b-alert show variant="primary" v-model="show">
                        <strong>Primary - </strong> A simple primary alert—check it out!
                    </b-alert>
                    <b-alert show variant="secondary" v-model="show">
                        <strong>Secondary - </strong> A simple secondary alert—check it out!
                    </b-alert>
                    <b-alert show variant="success" v-model="show">
                        <strong>Success - </strong> A simple success alert—check it out!
                    </b-alert>
                    <b-alert show variant="danger" v-model="show">
                        <strong>Error - </strong> A simple danger alert—check it out!
                    </b-alert>
                    <b-alert show variant="warning" v-model="show" class="text-bg-warning border-0">
                        <strong>Warning - </strong> A simple warning alert—check it out!
                    </b-alert>
                    <b-alert show variant="info" v-model="show" class="text-bg-info border-0">
                        <strong>Info - </strong> A simple info alert—check it out!
                    </b-alert>
                    <b-alert show variant="light" v-model="show" class="text-bg-light border-0">
                        <strong>Light - </strong> A simple light alert—check it out!
                    </b-alert>
                    <b-alert show variant="dark" v-model="show" class="text-bg-dark border-0 mb-0">
                        <strong>Dark - </strong> A simple dark alert—check it out!
                    </b-alert>
                </template>
            </CustomSyntax>

        </b-col> <!-- end col-->

        <b-col xl="6">
            <CustomSyntax title="Dismissing Alerts">
                <template v-slot:sub-text>
                    Add a dismiss button and the <code>.alert-dismissible</code> class, which adds
                    extra padding to the right of the alert
                    and positions the <code>.btn-close</code> button.
                </template>
                <template v-slot:preview>
                    <b-alert show dismissible variant="primary" v-model="dismissibleAlert1" class="text-bg-primary border-0">
                        <b-button class="btn-close btn-close-white" @click="dismissibleAlert1 = !dismissibleAlert1"></b-button>
                        <strong>Primary - </strong> A simple primary alert—check it out!
                    </b-alert>
                    <b-alert show dismissible variant="secondary" v-model="dismissibleAlert2" class="text-bg-secondary border-0">
                        <b-button class="btn-close btn-close-white" @click="dismissibleAlert2 = !dismissibleAlert2"></b-button>
                        <strong>Secondary - </strong> A simple secondary alert—check it out!
                    </b-alert>
                    <b-alert show dismissible variant="success" v-model="dismissibleAlert3" class="text-bg-success border-0">
                        <b-button class="btn-close btn-close-white" @click="dismissibleAlert3 = !dismissibleAlert3"></b-button>
                        <strong>Success - </strong> A simple success alert—check it out!
                    </b-alert>
                    <b-alert show dismissible variant="danger" v-model="dismissibleAlert4" class="text-bg-danger border-0">
                        <b-button class="btn-close btn-close-white" @click="dismissibleAlert4 = !dismissibleAlert4"></b-button>
                        <strong>Error - </strong> A simple danger alert—check it out!
                    </b-alert>
                    <b-alert show dismissible variant="warning" v-model="dismissibleAlert5">
                        <b-button class="btn-close btn-close-white" @click="dismissibleAlert5 = !dismissibleAlert5"></b-button>
                        <strong>Warning - </strong> A simple warning alert—check it out!
                    </b-alert>
                    <b-alert show dismissible variant="info" v-model="dismissibleAlert6">
                        <b-button class="btn-close btn-close-white" @click="dismissibleAlert6 = !dismissibleAlert6"></b-button>
                        <strong>Info - </strong> A simple info alert—check it out!
                    </b-alert>
                    <b-alert show dismissible variant="light" v-model="dismissibleAlert7">
                        <b-button class="btn-close btn-close-white" @click="dismissibleAlert7 = !dismissibleAlert7"></b-button>
                        <strong>Light - </strong> A simple light alert—check it out!
                    </b-alert>
                    <b-alert show dismissible variant="dark" v-model="dismissibleAlert8">
                        <b-button class="btn-close btn-close-white" @click="dismissibleAlert8 = !dismissibleAlert8"></b-button>
                        <strong>Dark - </strong> A simple dark alert—check it out!
                    </b-alert>
                </template>
            </CustomSyntax>

        </b-col> <!-- end col-->
    </b-row>
    <!-- end row -->

    <b-row>
        <b-col xl="6">
            <CustomSyntax title="Custom Alerts">
                <template v-slot:sub-text>
                    Display alert with transparent background and with contextual text color. Use
                    classes
                    <code>.bg-white</code>, and <code>.text-*</code>. E.g. <code>bg-white
                        text-primary</code>.
                </template>
                <template v-slot:preview>
                    <b-alert show variant="primary" v-model="show" class="bg-transparent text-primary">
                        This is a <strong>primary</strong> alert—check it out!
                    </b-alert>
                    <b-alert show variant="secondary" v-model="show" class="bg-transparent text-secondary">
                        This is a <strong>secondary</strong> alert—check it out!
                    </b-alert>
                    <b-alert show variant="success" v-model="show" class="bg-transparent text-success">
                        This is a <strong>success</strong> alert—check it out!
                    </b-alert>
                    <b-alert show variant="info" v-model="show" class="bg-transparent text-info">
                        This is a <strong>info</strong> alert—check it out!
                    </b-alert>
                    <b-alert show variant="warning" v-model="show" class="bg-transparent text-warning">
                        This is a <strong>warning</strong> alert—check it out!
                    </b-alert>
                    <b-alert show variant="danger" v-model="show" class="bg-transparent text-danger">
                        This is a <strong>danger</strong> alert—check it out!
                    </b-alert>
                    <b-alert show variant="light" v-model="show" class="bg-transparent text-light">
                        This is a <strong>light</strong> alert—check it out!
                    </b-alert>
                    <b-alert show variant="dark" v-model="show" class="bg-transparent text-dark mb-0">
                        This is a <strong>dark</strong> alert—check it out!
                    </b-alert>
                </template>
            </CustomSyntax>
        </b-col> <!-- end col-->

        <b-col xl="6">
            <CustomSyntax title="Link Color">
                <template v-slot:sub-text>
                    Use the <code>.alert-link</code> utility class to quickly provide matching
                    colored links within any alert.
                </template>
                <template v-slot:preview>
                    <b-alert show variant="primary" v-model="show">
                        A simple primary alert with
                        <a href="#" class="alert-link">an example link</a>. Give it a click
                        if you like.
                    </b-alert>
                    <b-alert show variant="secondary" v-model="show">
                        A simple secondary alert with
                        <a href="#" class="alert-link">an example link</a>. Give it a click
                        if you like.
                    </b-alert>
                    <b-alert show variant="success" v-model="show">
                        A simple success alert with
                        <a href="#" class="alert-link">an example link</a>. Give it a click
                        if you like.
                    </b-alert>
                    <b-alert show variant="danger" v-model="show">
                        A simple danger alert with
                        <a href="#" class="alert-link">an example link</a>. Give it a click
                        if you like.
                    </b-alert>
                    <b-alert show variant="warning" v-model="show">
                        A simple warning alert with
                        <a href="#" class="alert-link">an example link</a>. Give it a click
                        if you like.
                    </b-alert>
                    <b-alert show variant="info" v-model="show">
                        A simple info alert with
                        <a href="#" class="alert-link">an example link</a>. Give it a click
                        if you like.
                    </b-alert>
                    <b-alert show variant="light" v-model="show">
                        A simple light alert with
                        <a href="#" class="alert-link">an example link</a>. Give it a click
                        if you like.
                    </b-alert>
                    <b-alert show variant="dark" v-model="show">
                        A simple dark alert with
                        <a href="#" class="alert-link">an example link</a>. Give it a click
                        if you like.
                    </b-alert>
                </template>
            </CustomSyntax>

        </b-col> <!-- end col-->
    </b-row>
    <!-- end row -->

    <b-row>
        <b-col xl="6">
            <CustomSyntax title="Icons with Alerts">
                <template v-slot:sub-text>
                    You can also include additional elements like icons, heading, etc along side the actual message.
                </template>
                <template v-slot:preview>
                    <b-alert show variant="success" v-model="show">
                        <i class="ri-check-line me-1 align-middle fs-16"></i> This is a
                        <strong>success</strong> alert - check it out!
                    </b-alert>
                    <b-alert show variant="danger" v-model="show">
                        <i class="ri-close-circle-line me-1 align-middle fs-16"></i> This is
                        a <strong>danger</strong>
                        alert - check it out!
                    </b-alert>
                    <b-alert show variant="warning" v-model="show">
                        <i class="ri-alert-line me-1 align-middle fs-16"></i> This is a
                        <strong>warning</strong> alert - check it out!
                    </b-alert>
                    <b-alert show variant="info" v-model="show" class="mb-0">
                        <i class="ri-information-line me-1 align-middle fs-16"></i> This is
                        a <strong>info</strong> alert - check it out!
                    </b-alert>
                </template>
            </CustomSyntax>
        </b-col> <!-- end col-->

        <b-col xl="6">
            <CustomSyntax title="Additional content">
                <template v-slot:sub-text>
                    Alerts can also contain additional HTML elements like headings, paragraphs and
                    dividers.
                </template>
                <template v-slot:preview>
                    <b-alert show variant="info" v-model="show" class="text-center mb-0">
                        <h4 class="alert-heading">Well done!</h4>
                        <p>
                            Aww yeah, you successfully read this important alert message.
                            This example text is going to run a bit longer so that you can
                            see how spacing within an alert works with this kind of content.
                        </p>
                        <hr class="border-info border-opacity-25" />
                        <p class="mb-0">
                            Whenever you need to, be sure to use margin utilities to keep
                            things nice and tidy.
                        </p>
                    </b-alert>
                </template>
            </CustomSyntax>
        </b-col> <!-- end col-->
    </b-row> <!-- end row-->

    <b-row>
        <b-col xl="6">
            <CustomSyntax title="Live Alert">
                <template v-slot:sub-text>
                    Click the button below to show an alert (hidden with inline styles to start), then dismiss (and destroy) it with the built-in close button.
                </template>
                <template v-slot:preview>
                    <b-alert show dismissible variant="success" v-model="dismissibleAlert9">
                        <div>Nice, you triggered this alert message!</div>
                        <button class="btn-close" @click="dismissibleAlert9 = !dismissibleAlert9"></button>
                    </b-alert>
                    <b-button variant="primary" @click="dismissibleAlert9 = !dismissibleAlert9">Show live alert</b-button>
                </template>
            </CustomSyntax>
        </b-col>
    </b-row> <!-- end row-->
</Layout>
</template>

<script lang="ts">
import Layout from '@/components/layouts/layout.vue';
import Breadcrumb from '@/components/breadcrumb.vue';
import CustomSyntax from "@/components/custom/custom-syntax.vue";

export default {
    components: { Layout, Breadcrumb, CustomSyntax },
    data() {
        const alertPlaceholder = document.getElementById("liveAlertPlaceholder");

        return {
          title: 'Alerts',
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
              text: 'Alerts',
              active: true,
            },
          ],

            show: true,
            dismissibleAlert1: true,
            dismissibleAlert2: true,
            dismissibleAlert3: true,
            dismissibleAlert4: true,
            dismissibleAlert5: true,
            dismissibleAlert6: true,
            dismissibleAlert7: true,
            dismissibleAlert8: true,
            dismissibleAlert9: false,
            alertPlaceholder,
        }
    },
    methods: {
        alert(message: string, type: string = "primary") {
            const wrapper = document.createElement("div");
            wrapper.innerHTML = [
                `<b-alert show dismissible variant="${type}" v-model="dismissibleAlert9">`,
                `   <div>${message}</div>`,
                '   <b-button class="btn-close" @click="dismissibleAlert9 = !dismissibleAlert9"></b-button>',
                "</b-alert>",
            ].join("");
            if (this.alertPlaceholder) this.alertPlaceholder.append(wrapper);
        },
    },

}
</script>
