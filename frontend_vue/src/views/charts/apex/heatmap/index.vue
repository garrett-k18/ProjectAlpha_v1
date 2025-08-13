<template>
<Layout>
    <Breadcrumb :items="items" :title="title" />

    <b-row>
        <b-col xl="6">
            <b-card>
                <h4 class="header-title">Basic Heatmap - Single Series</h4>
                <div dir="ltr">
                    <BasicHeatmapChart class="apex-charts" />
                </div>
            </b-card>
            <!-- end card -->
        </b-col>
        <!-- end col-->

        <b-col xl="6">
            <b-card>
                <h4 class="header-title">Heatmap - Multiple Series</h4>
                <div dir="ltr">
                    <MultipleSeriesChart class="apex-charts" />
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
                <h4 class="header-title mb-3">Heatmap - Color Range</h4>
                <div dir="ltr">
                    <ColorRangeChart class="apex-charts" />
                </div>
            </b-card>
            <!-- end card -->
        </b-col>
        <!-- end col-->

        <b-col xl="6">
            <b-card>
                <h4 class="header-title mb-3">Heatmap - Range without Shades</h4>
                <div dir="ltr">
                    <RangewithoutShadeChart class="apex-charts" />
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
import BasicHeatmapChart from './BasicHeatmapChart.vue'
import MultipleSeriesChart from './MultipleSeriesChart.vue'
import ColorRangeChart from './ColorRangeChart.vue'
import RangewithoutShadeChart from './RangewithoutShadeChart.vue'

export default {
    components: { Layout, Breadcrumb, BasicHeatmapChart, MultipleSeriesChart, ColorRangeChart, RangewithoutShadeChart },
    data() {
        return {
            title: 'Heatmap Charts',
            items: [{
                    text: 'Hyper',
                    href: '/'
                },
                {
                    text: 'Apex',
                    href: '/'
                },
                {
                    text: 'Heatmap Charts',
                    active: true
                }
            ]
        }
    },
}
</script>
