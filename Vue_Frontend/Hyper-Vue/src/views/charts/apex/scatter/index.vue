<template>
<Layout>
    <Breadcrumb :items="items" :title="title" />

    <b-row>
        <b-col xl="6">
            <b-card>
                <h4 class="header-title">Scatter (XY) Chart</h4>
                <div dir="ltr">
                    <ScatterChart class="apex-charts" />
                </div>
            </b-card>
            <!-- end card -->
        </b-col>
        <!-- end col-->

        <b-col xl="6">
            <b-card>
                <h4 class="header-title">Scatter Chart - Datetime</h4>
                <div dir="ltr">
                    <DatetimeScatterChart class="apex-charts" />
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
                <h4 class="header-title">Scatter - Images</h4>
                <div dir="ltr">
                    <ImagesScatterChart class="apex-charts scatter-images-chart" />
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
import ScatterChart from './ScatterChart.vue'
import DatetimeScatterChart from './DatetimeScatterChart.vue'
import ImagesScatterChart from './ImagesScatterChart.vue'
export default {
    components: {
        Layout,
        Breadcrumb,
        ScatterChart,
        DatetimeScatterChart,
        ImagesScatterChart
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
