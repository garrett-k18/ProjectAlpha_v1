<template>
<Layout>
    <Breadcrumb :items="items" :title="title" />

    <b-row>
        <b-col xl="6">
            <b-card>
                <h4 class="header-title">Basic Bar Chart</h4>
                <div dir="ltr">
                    <BasicbarChart class="apex-charts" />
                </div>
            </b-card>
            <!-- end card -->
        </b-col>
        <!-- end col-->

        <b-col xl="6">
            <b-card>
                <h4 class="header-title">Grouped Bar Chart</h4>
                <div dir="ltr">
                    <GroupbarChart class="apex-charts" />
                </div>
            </b-card>
            <!-- end card -->
        </b-col>
        <!-- end col-->
    </b-row>
    <!-- end row-->

    <b-row>
        <b-col xl="6">
            <b-card>
                <h4 class="header-title">Stacked Bar Chart</h4>
                <div dir="ltr">
                    <StackbarChart class="apex-charts" />
                </div>
            </b-card>
            <!-- end card -->
        </b-col>
        <!-- end col-->

        <b-col xl="6">
            <b-card>
                <h4 class="header-title">100% Stacked Bar Chart</h4>
                <div dir="ltr">
                    <FullstackbarChart class="apex-charts" />
                </div>
            </b-card>
            <!-- end card -->
        </b-col>
        <!-- end col-->
    </b-row>
    <!-- end row-->

    <b-row>
        <b-col xl="6">
            <b-card>
                <h4 class="header-title">Bar with Negative Values</h4>
                <div dir="ltr">
                    <NegativebarChart class="apex-charts" />
                </div>
            </b-card>
            <!-- end card -->
        </b-col>
        <!-- end col-->

        <b-col xl="6">
            <b-card>
                <h4 class="header-title">Reversed Bar Chart</h4>
                <div dir="ltr">
                    <ReversedbarChart class="apex-charts" />
                </div>
            </b-card>
            <!-- end card -->
        </b-col>
        <!-- end col-->
    </b-row>
    <!-- end row-->

    <b-row>
        <b-col xl="6">
            <b-card>
                <h4 class="header-title">Bar with Image Fill</h4>
                <div dir="ltr">
                    <ImagebarChart class="apex-charts" />
                </div>
            </b-card>
            <!-- end card -->
        </b-col>
        <!-- end col-->

        <b-col xl="6">
            <b-card>
                <h4 class="header-title">Custom DataLabels Bar</h4>
                <div dir="ltr">
                    <CustombarChart class="apex-charts" />
                </div>
            </b-card>
            <!-- end card -->
        </b-col>
        <!-- end col-->
    </b-row>
    <!-- end row-->

    <b-row>
        <b-col xl="6">
            <b-card>
                <h4 class="header-title">Patterned Bar Chart</h4>
                <div dir="ltr">
                    <PatternbarChart class="apex-charts" />
                </div>
            </b-card>
            <!-- end card -->
        </b-col>
        <!-- end col-->

        <b-col xl="6">
            <b-card>
                <h4 class="header-title">Bar with Markers</h4>
                <div dir="ltr">
                    <MarkersbarChart class="apex-charts" />
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
import BasicbarChart from './BasicbarChart.vue'
import GroupbarChart from './GroupbarChart.vue'
import StackbarChart from './StackbarChart.vue'
import FullstackbarChart from './FullstackbarChart.vue'
import NegativebarChart from './NegativebarChart.vue'
import ReversedbarChart from './ReversedbarChart.vue'
import ImagebarChart from './ImagebarChart.vue'
import CustombarChart from './CustombarChart.vue'
import PatternbarChart from './PatternbarChart.vue'
import MarkersbarChart from './MarkersbarChart.vue'
export default {
    components: { Layout, Breadcrumb, BasicbarChart, GroupbarChart, StackbarChart, FullstackbarChart, NegativebarChart, ReversedbarChart, ImagebarChart, CustombarChart, PatternbarChart, MarkersbarChart },
    data() {
        return {
            title: 'Bar Charts',
            items: [{
                    text: "Hyper",
                    href: "/",
                },
                {
                    text: "Apex",
                    href: "/",
                },
                {
                    text: "Bar Charts",
                    active: true,
                },
            ]
        }
    },

}
</script>
