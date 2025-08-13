<template>
<Layout>
    <Breadcrumb :items="items" :title="title" />

    <b-row>
        <b-col xl="6">
            <b-card>
                <h4 class="header-title mb-3">Basic Radar Chart</h4>
                <div dir="ltr">
                    <BasicRadarChart class="apex-charts" />
                </div>
            </b-card>
            <!-- end card -->
        </b-col>
        <!-- end col-->
        <b-col xl="6">
            <b-card>
                <h4 class="header-title mb-3">Radar with Polygon-fill</h4>
                <div dir="ltr">
                    <PollygonFillRadarChart class="apex-charts" />
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
                <h4 class="header-title mb-3">Radar – Multiple Series</h4>
                <div dir="ltr">
                    <MultipleSeriesRadarChart class="apex-charts" />
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
import BasicRadarChart from './BasicRadarChart.vue'
import PollygonFillRadarChart from './PollygonFillRadarChart.vue'
import MultipleSeriesRadarChart from './MultipleSeriesRadarChart.vue'
export default {
    components: { Layout, Breadcrumb, BasicRadarChart, PollygonFillRadarChart, MultipleSeriesRadarChart },
    data() {
        return {
            title: 'Radar Charts',
            items: [{
                    text: 'Hyper',
                    href: '/'
                },
                {
                    text: 'Apex',
                    href: '/'
                },
                {
                    text: 'Radar Charts',
                    active: true
                }
            ]
        }
    },
}
</script>
