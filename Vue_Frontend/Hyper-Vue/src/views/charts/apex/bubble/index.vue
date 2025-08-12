<template>
<Layout>
    <Breadcrumb :items="items" :title="title" />

    <b-row>
        <b-col xl="6">
            <b-card>
                <h4 class="header-title">Simple Bubble Chart</h4>
                <div dir="ltr">
                    <SimplebubbleChart class="apex-charts" />
                </div>
            </b-card>
            <!-- end card -->
        </b-col>
        <!-- end col-->

        <b-col xl="6">
            <b-card>
                <h4 class="header-title">3D Bubble Chart</h4>
                <div dir="ltr">
                    <Bubble3DChart id="second-bubble" class="apex-charts" />
                </div>
            </b-card>
            <!-- end card -->
        </b-col>
        <!-- end col-->
    </b-row>
    <!-- end row-->

</Layout>
</template>

<script>
import Layout from '@/components/layouts/layout.vue'
import Breadcrumb from '@/components/breadcrumb.vue'
import SimplebubbleChart from './SimplebubbleChart.vue'
import Bubble3DChart from './Bubble3DChart.vue'
export default {
    components: { Layout, Breadcrumb, SimplebubbleChart, Bubble3DChart },
    data() {
        return {
            title: 'Bubble',
            items: [{
                    text: "Hyper",
                    href: "/",
                },
                {
                    text: "Apex",
                    href: "/",
                },
                {
                    text: "Bubble",
                    active: true,
                },
            ]
        }
    },

}
</script>
