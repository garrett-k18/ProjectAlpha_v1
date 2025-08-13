<template>
<Layout>
    <Breadcrumb :title="title" :items="items" />

    <b-row>
        <b-col xl="6">
            <CustomSyntax title="Offcanvas">
                <template v-slot:sub-text>
                    You can use a link with the <code>href</code> attribute, or a button with the <code>data-bs-target</code> attribute. In both cases, the <code>data-bs-toggle="offcanvas"</code> is required.
                </template>
                <template v-slot:preview>
                    <div class="d-flex flex-wrap gap-2">
                        <a class="btn btn-primary" @click="offcanvas = !offcanvas">
                            Link with href
                        </a>
                        <b-button variant="primary" @click="offcanvas = !offcanvas">
                            Button with data-bs-target
                        </b-button>
                    </div>

                    <b-offcanvas v-model="offcanvas" placement="start" title="Offcanvas" id="offcanvasExample">
                        <div>
                            <div>
                                Some text as placeholder. In real life you can have the elements
                                you have chosen. Like, text, images, lists, etc.
                            </div>
                            <h5 class="mt-3">List</h5>
                            <ul class="ps-3">
                                <li class="">Nemo enim ipsam voluptatem quia aspernatur</li>
                                <li class="">Neque porro quisquam est, qui dolorem</li>
                                <li class="">Quis autem vel eum iure qui in ea</li>
                            </ul>

                            <ul class="ps-3">
                                <li class="">
                                    At vero eos et accusamus et iusto odio dignissimos
                                </li>
                                <li class="">Et harum quidem rerum facilis</li>
                                <li class="">Temporibus autem quibusdam et aut officiis</li>
                            </ul>
                        </div>
                    </b-offcanvas>
                </template>
            </CustomSyntax>

            <CustomSyntax title="Offcanvas Backdrop">
                <template v-slot:sub-text>
                    Scrolling the <code>&lt;body&gt;</code> element is disabled when an offcanvas and its backdrop are visible. Use the <code>data-bs-scroll</code> attribute to toggle <code>&lt;body&gt;</code> scrolling and <code>data-bs-backdrop</code> to toggle the backdrop.
                </template>
                <template v-slot:preview>
                    <div class="d-flex flex-wrap gap-2">
                        <b-button variant="primary" class="mt-2 mt-md-0" @click="offcanvas1 = !offcanvas1">
                            Enable body scrolling
                        </b-button>
                        <b-button variant="primary" class="mt-2 mt-md-0" @click="offcanvas2 = !offcanvas2">
                            Enable backdrop (default)
                        </b-button>
                        <b-button variant="primary" class="mt-2 mt-md-0" @click="offcanvas3 = !offcanvas3">
                            Enable both scrolling & backdrop
                        </b-button>
                    </div>
                    <!-- end d-flex flex-wrap gap-2-->

                    <b-offcanvas v-model="offcanvas1" placement="start" title="Colored with scrolling" :body-scrolling="true" :backdrop="false" id="offcanvasScrolling">
                        <div>
                            <div>
                                Some text as placeholder. In real life you can have the elements
                                you have chosen. Like, text, images, lists, etc.
                            </div>
                            <h5 class="mt-3">List</h5>
                            <ul class="ps-3">
                                <li class="">Nemo enim ipsam voluptatem quia aspernatur</li>
                                <li class="">Neque porro quisquam est, qui dolorem</li>
                                <li class="">Quis autem vel eum iure qui in ea</li>
                            </ul>

                            <ul class="ps-3">
                                <li class="">
                                    At vero eos et accusamus et iusto odio dignissimos
                                </li>
                                <li class="">Et harum quidem rerum facilis</li>
                                <li class="">Temporibus autem quibusdam et aut officiis</li>
                            </ul>
                        </div>
                    </b-offcanvas>

                    <b-offcanvas v-model="offcanvas2" placement="start" title="Offcanvas with backdrop" id="offcanvasWithBackdrop">
                        <div>
                            <div>
                                Some text as placeholder. In real life you can have the elements
                                you have chosen. Like, text, images, lists, etc.
                            </div>
                            <h5 class="mt-3">List</h5>
                            <ul class="ps-3">
                                <li class="">Nemo enim ipsam voluptatem quia aspernatur</li>
                                <li class="">Neque porro quisquam est, qui dolorem</li>
                                <li class="">Quis autem vel eum iure qui in ea</li>
                            </ul>

                            <ul class="ps-3">
                                <li class="">
                                    At vero eos et accusamus et iusto odio dignissimos
                                </li>
                                <li class="">Et harum quidem rerum facilis</li>
                                <li class="">Temporibus autem quibusdam et aut officiis</li>
                            </ul>
                        </div>
                    </b-offcanvas>

                    <b-offcanvas v-model="offcanvas3" placement="start" title="Backdroped with scrolling" :body-scrolling="true" id="offcanvasWithBothOptions">
                        <div>
                            <div>
                                Some text as placeholder. In real life you can have the elements
                                you have chosen. Like, text, images, lists, etc.
                            </div>
                            <h5 class="mt-3">List</h5>
                            <ul class="ps-3">
                                <li class="">Nemo enim ipsam voluptatem quia aspernatur</li>
                                <li class="">Neque porro quisquam est, qui dolorem</li>
                                <li class="">Quis autem vel eum iure qui in ea</li>
                            </ul>

                            <ul class="ps-3">
                                <li class="">
                                    At vero eos et accusamus et iusto odio dignissimos
                                </li>
                                <li class="">Et harum quidem rerum facilis</li>
                                <li class="">Temporibus autem quibusdam et aut officiis</li>
                            </ul>
                        </div>
                    </b-offcanvas>
                </template>
            </CustomSyntax>

        </b-col> <!-- end col-->

        <b-col xl="6">
            <CustomSyntax title="Offcanvas Placement">
                <template v-slot:sub-text>
                    Try the right and bottom examples out below.

                </template>
                <template v-slot:preview>
                    <ul class="text-muted font-13">
                        <li><code>.offcanvas-start</code> places offcanvas on the left of the viewport (shown above)</li>
                        <li><code>.offcanvas-end</code> places offcanvas on the right of the viewport</li>
                        <li><code>.offcanvas-top</code> places offcanvas on the top of the viewport</li>
                        <li><code>.offcanvas-bottom</code> places offcanvas on the bottom of the viewport</li>
                    </ul>

                    <div>
                        <div class="d-flex flex-wrap gap-2">
                            <b-button variant="primary" class="mt-2 mt-md-0" @click="offcanvasTop = !offcanvasTop">
                                Toggle Top offcanvas
                            </b-button>
                            <b-button variant="primary" class="mt-2 mt-md-0" @click="offcanvasRight = !offcanvasRight">
                                Toggle right offcanvas
                            </b-button>
                            <b-button variant="primary" class="mt-2 mt-md-0" @click="offcanvasBottom = !offcanvasBottom">
                                Toggle bottom offcanvas
                            </b-button>
                            <b-button variant="primary" class="mt-2 mt-lg-0" @click="offcanvasLeft = !offcanvasLeft">
                                Toggle Left offcanvas
                            </b-button>
                        </div>

                        <b-offcanvas v-model="offcanvasTop" placement="top" title="Offcanvas Top" id="offcanvasTop">
                            <div>
                                <div>
                                    Some text as placeholder. In real life you can have the
                                    elements you have chosen. Like, text, images, lists, etc.
                                </div>
                                <h5 class="mt-3">List</h5>
                                <ul class="ps-3">
                                    <li class="">Nemo enim ipsam voluptatem quia aspernatur</li>
                                    <li class="">Neque porro quisquam est, qui dolorem</li>
                                    <li class="">Quis autem vel eum iure qui in ea</li>
                                </ul>
                            </div>
                        </b-offcanvas>

                        <b-offcanvas v-model="offcanvasRight" placement="end" title="Offcanvas Right" id="offcanvasRight">
                            <div>
                                <div>
                                    Some text as placeholder. In real life you can have the
                                    elements you have chosen. Like, text, images, lists, etc.
                                </div>
                                <h5 class="mt-3">List</h5>
                                <ul class="ps-3">
                                    <li class="">Nemo enim ipsam voluptatem quia aspernatur</li>
                                    <li class="">Neque porro quisquam est, qui dolorem</li>
                                    <li class="">Quis autem vel eum iure qui in ea</li>
                                </ul>
                            </div>
                        </b-offcanvas>

                        <b-offcanvas v-model="offcanvasBottom" placement="bottom" title="Offcanvas Bottom" id="offcanvasBottom">
                            <div>
                                <div>
                                    Some text as placeholder. In real life you can have the
                                    elements you have chosen. Like, text, images, lists, etc.
                                </div>
                                <h5 class="mt-3">List</h5>
                                <ul class="ps-3">
                                    <li class="">Nemo enim ipsam voluptatem quia aspernatur</li>
                                    <li class="">Neque porro quisquam est, qui dolorem</li>
                                    <li class="">Quis autem vel eum iure qui in ea</li>
                                </ul>
                            </div>
                        </b-offcanvas>

                        <b-offcanvas v-model="offcanvasLeft" placement="start" title="Offcanvas Left" id="offcanvasLeft">
                            <div>
                                <div>
                                    Some text as placeholder. In real life you can have the
                                    elements you have chosen. Like, text, images, lists, etc.
                                </div>
                                <h5 class="mt-3">List</h5>
                                <ul class="ps-3">
                                    <li class="">Nemo enim ipsam voluptatem quia aspernatur</li>
                                    <li class="">Neque porro quisquam est, qui dolorem</li>
                                    <li class="">Quis autem vel eum iure qui in ea</li>
                                </ul>
                            </div>
                        </b-offcanvas>
                    </div> <!-- end tab-pan-->
                </template>
            </CustomSyntax>

            <CustomSyntax title="Dark Offcanvas">
                <template v-slot:sub-text>
                    Change the appearance of offcanvases with utilities to better match them to different contexts like dark navbars.
                    Here we add <code>.text-bg-dark</code> to the <code>.offcanvas</code> and <code>.btn-close-white</code> to
                    <code>.btn-close</code> for proper styling with a dark offcanvas. If you have dropdowns within, consider also adding
                    <code>.dropdown-menu-dark</code> to <code>.dropdown-menu</code>.
                </template>
                <template v-slot:preview>
                    <div>
                        <b-button variant="primary" class="mt-2 mt-md-0" @click="offcanvasDark = !offcanvasDark">
                            Dark offcanvas
                        </b-button>

                        <b-offcanvas v-model="offcanvasDark" placement="start" title="Dark Offcanvas" class="text-bg-dark" id="offcanvasDark">
                            <div>
                                <div>
                                    Some text as placeholder. In real life you can have the elements
                                    you have chosen. Like, text, images, lists, etc.
                                </div>
                                <h5 class="mt-3">List</h5>
                                <ul class="ps-3">
                                    <li class="">Nemo enim ipsam voluptatem quia aspernatur</li>
                                    <li class="">Neque porro quisquam est, qui dolorem</li>
                                    <li class="">Quis autem vel eum iure qui in ea</li>
                                </ul>
                            </div>
                        </b-offcanvas>
                    </div> <!-- end tab-pan-->
                </template>
            </CustomSyntax>

        </b-col> <!-- end col-->
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
          title: 'Offcanvas',
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
              text: 'Offcanvas',
              active: true,
            },
          ],

            offcanvas: false,
            offcanvas1: false,
            offcanvas2: false,
            offcanvas3: false,
            offcanvasTop: false,
            offcanvasRight: false,
            offcanvasBottom: false,
            offcanvasLeft: false,
            offcanvasDark: false,
        };
    },

}
</script>
