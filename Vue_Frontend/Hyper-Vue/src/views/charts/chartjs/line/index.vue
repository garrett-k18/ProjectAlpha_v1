<template>
<Layout>
    <Breadcrumb :title="title" :items="items" />

    <b-row>
        <b-col xl="6">
            <b-card>
                <h4 class="header-title mb-4">Interpolation</h4>

                <div dir="ltr">
                    <div class="mt-3 chartjs-chart" style="height: 320px">
                        <InterpolationChart />
                    </div>
                </div>
            </b-card>
        </b-col>

        <b-col xl="6">
            <b-card>
                <h4 class="header-title mb-4">Line</h4>

                <div dir="ltr">
                    <div class="mt-3 chartjs-chart" style="height: 320px">
                        <LineChart />
                    </div>
                </div>
            </b-card>
        </b-col>
    </b-row>

    <b-row>
        <b-col xl="6">
            <b-card>
                <h4 class="header-title mb-4">Multi-Axes</h4>

                <div dir="ltr">
                    <div class="mt-3 chartjs-chart" style="height: 320px">
                        <MultiAxesChart />
                    </div>
                </div>
            </b-card>
        </b-col>

        <b-col xl="6">
            <b-card>
                <h4 class="header-title mb-4">Point Styling</h4>

                <div dir="ltr">
                    <div class="mt-3 chartjs-chart" style="height: 320px">
                        <PointStylingChart />
                    </div>
                </div>
            </b-card>
        </b-col>
    </b-row>

    <b-row>
        <b-col xl="6">
            <b-card>
                <h4 class="header-title mb-4">Line Segment</h4>

                <div dir="ltr">
                    <div class="mt-3 chartjs-chart" style="height: 320px">
                        <LineSegmentChart />
                    </div>
                </div>
            </b-card>
        </b-col>

        <b-col xl="6">
            <b-card>
                <h4 class="header-title mb-4">Stepped</h4>

                <div dir="ltr">
                    <div class="mt-3 chartjs-chart" style="height: 320px">
                        <SteppedChart />
                    </div>
                </div>
            </b-card>
        </b-col>
    </b-row>
</Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";

import InterpolationChart from "./InterpolationChart.vue";
import LineChart from "./LineChart.vue";
import MultiAxesChart from "./MultiAxesChart.vue";
import PointStylingChart from "./PointStylingChart.vue";
import LineSegmentChart from "./LineSegmentChart.vue";
import SteppedChart from "./SteppedChart.vue";

export default {
    components: {
        Layout,
        Breadcrumb,
        InterpolationChart,
        LineChart,
        MultiAxesChart,
        PointStylingChart,
        LineSegmentChart,
        SteppedChart,
    },
    data() {
        return {
            title: 'Chartjs',
            items: [{
                    text: 'Hyper',
                    href: '/',
                },
                {
                    text: 'Charts',
                    href: '/',
                },
                {
                    text: 'Chartjs',
                    active: true,
                },
            ],
        }
    }
};
</script>
