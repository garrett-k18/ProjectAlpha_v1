<template>
<Layout>
    <Breadcrumb :items="items" :title="title" />

    <b-row>
        <b-col xl="6">
            <b-card>
                <h4 class="header-title mb-4">Basic RadialBar Chart</h4>
                <div dir="ltr">
                    <BasicRadialBarChart class="apex-charts" />
                </div>
            </b-card>
            <!-- end card -->
        </b-col>
        <!-- end col-->

        <b-col xl="6">
            <b-card>
                <h4 class="header-title mb-4">Multiple RadialBars</h4>
                <div dir="ltr">
                    <MultipleRadialBars class="apex-charts" />
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
                <h4 class="header-title mb-4">Circle Chart - Custom Angle</h4>
                <div class="text-center" dir="ltr">
                    <CustomAngleRadialBarChart class="apex-charts" />
                </div>
            </b-card>
            <!-- end card -->
        </b-col>
        <!-- end col-->

        <b-col xl="6">
            <b-card>
                <h4 class="header-title mb-4">Circle Chart with Image</h4>
                <div dir="ltr">
                    <ImageRadialChart class="apex-charts" />
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
                <h4 class="header-title mb-4">Stroked Circular Guage</h4>
                <div dir="ltr">
                    <StrokedCircularGuage class="apex-charts" />
                </div>
            </b-card>
            <!-- end card -->
        </b-col>
        <!-- end col-->

        <b-col xl="6">
            <b-card>
                <h4 class="header-title mb-4">Gradient Circular Chart</h4>
                <div dir="ltr">
                    <GradientCircularChart class="apex-charts" />
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
                <h4 class="header-title mb-4">Semi Circle Gauge</h4>
                <div dir="ltr">
                    <semi-circle-gauge class="apex-charts" />
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
import BasicRadialBarChart from './BasicRadialBarChart.vue'
import MultipleRadialBars from './MultipleRadialBars.vue'
import CustomAngleRadialBarChart from './CustomAngleRadialBarChart.vue'
import ImageRadialChart from './ImageRadialChart.vue'
import StrokedCircularGuage from './StrokedCircularGuage.vue'
import GradientCircularChart from './GradientCircularChart.vue'
import SemiCircleGauge from './SemiCircleGauge.vue'
export default {
    components: {
        Layout,
        Breadcrumb,
        BasicRadialBarChart,
        MultipleRadialBars,
        CustomAngleRadialBarChart,
        ImageRadialChart,
        StrokedCircularGuage,
        GradientCircularChart,
        SemiCircleGauge
    },
    data() {
        return {
            title: 'RadialBar Charts',
            items: [{
                    text: 'Hyper',
                    href: '/'
                },
                {
                    text: 'Apex',
                    href: '/'
                },
                {
                    text: 'RadialBar Charts',
                    active: true
                }
            ]
        }
    },
}
</script>
