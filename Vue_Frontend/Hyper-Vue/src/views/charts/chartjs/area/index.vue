<template>
<Layout>
    <Breadcrumb :title="title" :items="items" />
    <b-row>
        <b-col xl="6">
            <b-card>
                <h4 class="header-title mb-4">Boundaries</h4>

                <div dir="ltr">
                    <div class="mt-3 chartjs-chart" style="height: 320px">
                        <BoundariesChart />
                    </div>
                </div>
            </b-card>
        </b-col>

        <b-col xl="6">
            <b-card>
                <h4 class="header-title mb-4">Different Dataset</h4>

                <div dir="ltr">
                    <div class="mt-3 chartjs-chart" style="height: 320px">
                        <DifferentDatasetChart />
                    </div>
                </div>
            </b-card>
        </b-col>
    </b-row>

    <b-row>
        <b-col xl="6">
            <b-card>
                <h4 class="header-title mb-4">Draw Time</h4>

                <div dir="ltr">
                    <div class="mt-3 chartjs-chart" style="height: 320px">
                        <DrawTimeChart />
                    </div>
                </div>
            </b-card>
        </b-col>

        <b-col xl="6">
            <b-card>
                <h4 class="header-title mb-4">Stacked</h4>

                <div dir="ltr">
                    <div class="mt-3 chartjs-chart" style="height: 320px">
                        <StackedChart />
                    </div>
                </div>
            </b-card>
        </b-col>
    </b-row>

    <b-row>
        <b-col xl="6">
            <b-card>
                <h4 class="header-title mb-4">Radar</h4>

                <div dir="ltr">
                    <div class="mt-3 chartjs-chart" style="height: 320px">
                        <RadarChart />
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

import BoundariesChart from "./BoundariesChart.vue";
import DifferentDatasetChart from "./DifferentDatasetChart.vue";
import DrawTimeChart from "./DrawTimeChart.vue";
import StackedChart from "./StackedChart.vue";
import RadarChart from "./RadarChart.vue";
export default {
    components: {
        Layout,
        Breadcrumb,
        BoundariesChart,
        DifferentDatasetChart,
        DrawTimeChart,
        StackedChart,
        RadarChart,
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
