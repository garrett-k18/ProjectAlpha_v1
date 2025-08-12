<template>
<Layout>
    <Breadcrumb :items="items" :title="title" />

    <b-row>
        <b-col xl="6">
            <b-card>
                <h4 class="header-title">Basic Treemap</h4>
                <div dir="ltr">
                    <BasicTreemapChart class="apex-charts" />
                </div>
            </b-card>
            <!-- end card -->
        </b-col>
        <!-- end col-->

        <b-col xl="6">
            <b-card>
                <h4 class="header-title">Treemap Multiple Series</h4>
                <div dir="ltr">
                    <MultipleTreemapChart class="apex-charts" />
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
                <h4 class="header-title">Distributed Treemap</h4>
                <div dir="ltr">
                    <DistributedTreemapChart class="apex-charts" />
                </div>
            </b-card>
            <!-- end card -->
        </b-col>
        <!-- end col-->

        <b-col xl="6">
            <b-card>
                <h4 class="header-title">Color Range Treemap</h4>
                <div dir="ltr">
                    <ColorRangeTreemapChart class="apex-charts" />
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
import BasicTreemapChart from './BasicTreemapChart.vue'
import MultipleTreemapChart from './MultipleTreemapChart.vue'
import DistributedTreemapChart from './DistributedTreemapChart.vue'
import ColorRangeTreemapChart from './ColorRangeTreemapChart.vue'
export default {
    components: { Layout, Breadcrumb, BasicTreemapChart, MultipleTreemapChart, DistributedTreemapChart, ColorRangeTreemapChart },
    data() {
        return {

            title: 'Treemap Charts',
            items: [{
                    text: 'Hyper',
                    href: '/'
                },
                {
                    text: 'Apex',
                    href: '/'
                },
                {
                    text: 'Treemap Charts',
                    active: true
                }
            ]
        }
    },
}
</script>
