<template>
<Layout>
    <Breadcrumb :items="items" :title="title" />

    <b-row>
        <b-col xl="6">
            <b-card>
                <h4 class="header-title">Simple Pie Chart</h4>
                <div dir="ltr">
                    <SimplePieChart class="apex-charts" />
                </div>
            </b-card>
            <!-- end card -->
        </b-col>
        <!-- end col-->

        <b-col xl="6">
            <b-card>
                <h4 class="header-title">Simple Donut Chart</h4>
                <div dir="ltr">
                    <SimpleDonutChart class="apex-charts" />
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
                <h4 class="header-title mb-4">Monochrome Pie Chart</h4>
                <div dir="ltr">
                    <MonochromePieChart class="apex-charts" />
                </div>
            </b-card>
            <!-- end card -->
        </b-col>
        <!-- end col-->

        <b-col xl="6">
            <b-card>
                <h4 class="header-title mb-4">Gradient Donut Chart</h4>
                <div dir="ltr">
                    <GradientDonutChart class="apex-charts" />
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
                <h4 class="header-title mb-4">Patterned Donut Chart</h4>
                <div dir="ltr">
                    <PatternedDonutChart class="apex-charts" />
                </div>
            </b-card>
            <!-- end card -->
        </b-col>
        <!-- end col-->

        <b-col xl="6">
            <b-card>
                <h4 class="header-title mb-4">Pie Chart with Image fill</h4>
                <div dir="ltr">
                    <ImagePieChart class="apex-charts" />
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
                <h4 class="header-title mb-4">Donut Update</h4>
                <div dir="ltr">
                    <DonutUpadteChart class="apex-charts" />
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
import SimplePieChart from './SimplePieChart.vue'
import SimpleDonutChart from './SimpleDonutChart.vue'
import MonochromePieChart from './MonochromePieChart.vue'
import GradientDonutChart from './GradientDonutChart.vue'
import PatternedDonutChart from './PatternedDonutChart.vue'
import ImagePieChart from './ImagePieChart.vue'
import DonutUpadteChart from './DonutUpadteChart.vue'
export default {
    components: { Layout, Breadcrumb, SimplePieChart, SimpleDonutChart, MonochromePieChart, GradientDonutChart, PatternedDonutChart, ImagePieChart, DonutUpadteChart },
    data() {
        return {
            title: 'Pie Charts',
            items: [{
                    text: 'Hyper',
                    href: '/'
                },
                {
                    text: 'Apex',
                    href: '/'
                },
                {
                    text: 'Pie Charts',
                    active: true
                }
            ]
        }
    },
}
</script>
