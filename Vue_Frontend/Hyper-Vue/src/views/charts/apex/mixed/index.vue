<template>
<Layout>
    <Breadcrumb :items="items" :title="title" />

    <b-row>
        <b-col xl="6">
            <b-card>
                <h4 class="header-title">Line & Column Chart</h4>
                <div dir="ltr">
                    <LineAndColumnChart class="apex-charts" />
                </div>
            </b-card>
            <!-- end card -->
        </b-col>
        <!-- end col-->

        <b-col xl="6">
            <b-card>
                <h4 class="header-title">Multiple Y-Axis Chart</h4>
                <div dir="ltr">
                    <MultipleYaxisChart class="apex-charts" />
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
                <h4 class="header-title">Line & Area Chart</h4>
                <div dir="ltr">
                    <LineAndAreaChart class="apex-charts" />
                </div>
            </b-card>
            <!-- end card -->
        </b-col>
        <!-- end col-->

        <b-col xl="6">
            <b-card>
                <h4 class="header-title">Line, Column & Area Chart</h4>
                <div dir="ltr">
                    <LineColumnAreaChart class="apex-charts" />
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
import LineAndColumnChart from './LineAndColumnChart.vue'
import MultipleYaxisChart from './MultipleYaxisChart.vue'
import LineAndAreaChart from './LineAndAreaChart.vue'
import LineColumnAreaChart from '../line/LineColumnAreaChart.vue'
export default {
    components: { Layout, Breadcrumb, LineAndColumnChart, MultipleYaxisChart, LineAndAreaChart, LineColumnAreaChart },
    data() {
        return {
            title: 'Mixed Charts',
            items: [{
                    text: 'Hyper',
                    href: '/'
                },
                {
                    text: 'Apex',
                    href: '/'
                },
                {
                    text: 'Mixed Charts',
                    active: true
                }
            ]
        }
    },
}
</script>
