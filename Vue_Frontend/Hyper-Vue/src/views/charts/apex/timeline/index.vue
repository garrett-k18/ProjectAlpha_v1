<template>
<Layout>
    <Breadcrumb :items="items" :title="title" />

    <b-row>
        <b-col xl="6">
            <b-card>
                <h4 class="header-title mb-3">Basic Timeline</h4>
                <div dir="ltr">
                    <BasicTimelineChart class="apex-charts" />
                </div>
            </b-card>
            <!-- end card -->
        </b-col>
        <!-- end col-->

        <b-col xl="6">
            <b-card>
                <h4 class="header-title mb-3">Distributed Timeline </h4>
                <div dir="ltr">
                    <DistributedColumnChart class="apex-charts" />
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
                <h4 class="header-title mb-3">Multi Series Timeline</h4>

                <div dir="ltr">
                    <MultiSeriesTimelineChart class="apex-charts" />
                </div>
            </b-card>
            <!-- end card -->
        </b-col>
        <!-- end col-->

        <b-col xl="6">
            <b-card>
                <h4 class="header-title mb-3">Advanced Timeline</h4>
                <div dir="ltr">
                    <AdvancedTimelineChart class="apex-charts" />
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
                <h4 class="header-title mb-3">Multiple Series - Group Rows</h4>
                <div dir="ltr">
                    <GroupRowsTimelineChart class="apex-charts" />
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
import BasicTimelineChart from './BasicTimelineChart.vue'
import DistributedColumnChart from './DistributedTimelineChart.vue'
import MultiSeriesTimelineChart from './MultiSeriesTimelineChart.vue'
import AdvancedTimelineChart from './AdvancedTimelineChart.vue'
import GroupRowsTimelineChart from './GroupRowsTimelineChart.vue'
export default {
    components: { Layout, Breadcrumb, BasicTimelineChart, DistributedColumnChart, MultiSeriesTimelineChart, AdvancedTimelineChart, GroupRowsTimelineChart },
    data() {
        return {
            title: 'Timeline Charts',
            items: [{
                    text: 'Hyper',
                    href: '/'
                },
                {
                    text: 'Apex',
                    href: '/'
                },
                {
                    text: 'Timeline Charts',
                    active: true
                }
            ]
        }
    },
}
</script>
