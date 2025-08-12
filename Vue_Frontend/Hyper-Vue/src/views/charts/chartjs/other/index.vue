<template>
<Layout>
    <Breadcrumb :items="items" :title="title" />

    <b-row>
        <b-col xl="6">
            <b-card>
                <h4 class="header-title mb-4">Bubble</h4>

                <div dir="ltr">
                    <div class="mt-3 chartjs-chart" style="height: 320px;">
                        <BubbleChart />
                    </div>
                </div>
            </b-card> <!-- end card -->
        </b-col><!-- end col-->

        <b-col xl="6">
            <b-card>
                <h4 class="header-title mb-4">DONUT</h4>

                <div dir="ltr">
                    <div class="mt-3 chartjs-chart" style="height: 320px;">
                        <DonutCharts />
                    </div>
                </div>
            </b-card> <!-- end card -->
        </b-col><!-- end col-->
    </b-row>
    <!-- end row-->

    <b-row>
        <b-col xl="6">
            <b-card>
                <h4 class="header-title mb-4">Pie</h4>

                <div dir="ltr">
                    <div class="mt-3 chartjs-chart" style="height: 320px;">
                        <PieChart />
                    </div>
                </div>
            </b-card> <!-- end card -->
        </b-col><!-- end col-->

        <b-col xl="6">
            <b-card>
                <h4 class="header-title mb-4">Polar Area</h4>

                <div dir="ltr">
                    <div class="mt-3 chartjs-chart" style="height: 320px;">
                        <PolarAreaChart />
                    </div>
                </div>
            </b-card> <!-- end card -->
        </b-col><!-- end col-->
    </b-row>
    <!-- end row-->

    <b-row>
        <b-col xl="6">
            <b-card>
                <h4 class="header-title mb-4">Radar</h4>

                <div dir="ltr">
                    <div class="mt-3 chartjs-chart" style="height: 320px;">
                        <RadarChart />
                    </div>
                </div>
            </b-card> <!-- end card -->
        </b-col><!-- end col-->

        <b-col xl="6">
            <b-card>
                <h4 class="header-title mb-4">Scatter</h4>

                <div dir="ltr">
                    <div class="mt-3 chartjs-chart" style="height: 320px;">
                        <scatterChart />
                    </div>
                </div>
            </b-card> <!-- end card -->
        </b-col><!-- end col-->
    </b-row>

    <!-- end row-->
    <b-row>
        <b-col xl="6">
            <b-card>
                <h4 class="header-title mb-4">Stacked Bar/Line</h4>

                <div dir="ltr">
                    <div class="mt-3 chartjs-chart" style="height: 320px;">
                        <StackesLineChart />
                    </div>
                </div>
            </b-card> <!-- end card -->
        </b-col><!-- end col-->

    </b-row>
    <!-- end row-->

</Layout>
</template>

<script>
import Layout from '@/components/layouts/layout.vue'
import Breadcrumb from '@/components/breadcrumb.vue'
import BubbleChart from './BubbleChart.vue'
import DonutCharts from './DonutCharts.vue'
import PieChart from './PieChart.vue'
import PolarAreaChart from './PolarAreaChart.vue'
import RadarChart from './RadarChart.vue'
import scatterChart from './scatterChart.vue'
import StackesLineChart from './StackesLineChart.vue'
export default {
    components: {
        Layout,
        Breadcrumb,
        BubbleChart,
        DonutCharts,
        PieChart,
        PolarAreaChart,
        RadarChart,
        scatterChart,
        StackesLineChart
    },
    data() {
        return {
            title: 'Chartjs',
            items: [{
                    text: 'Hyper',
                    href: '/'
                },
                {
                    text: 'Apex',
                    href: '/'
                },
                {
                    text: 'Chartjs',
                    active: true
                }
            ]
        }
    },
}
</script>
