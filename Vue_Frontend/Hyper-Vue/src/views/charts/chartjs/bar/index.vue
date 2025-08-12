<template>
<Layout>
    <Breadcrumb :title="title" :items="items" />
    <b-row>
        <b-col xl="6">
            <b-card>
                <h4 class="header-title mb-4">Border Radius</h4>

                <div dir="ltr">
                    <div class="mt-3 chartjs-chart" style="height: 320px">
                        <BorderRadiusChart />
                    </div>
                </div>
            </b-card>
        </b-col>

        <b-col xl="6">
            <b-card>
                <h4 class="header-title mb-4">Floating</h4>

                <div dir="ltr">
                    <div class="mt-3 chartjs-chart" style="height: 320px">
                        <FloatingChart />
                    </div>
                </div>
            </b-card>
        </b-col>
    </b-row>

    <b-row>
        <b-col xl="6">
            <b-card>
                <h4 class="header-title mb-4">Horizontal</h4>

                <div dir="ltr">
                    <div class="mt-3 chartjs-chart" style="height: 320px">
                        <HorizontalChart />
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
                <h4 class="header-title mb-4">Stacked with Groups</h4>

                <div dir="ltr">
                    <div class="mt-3 chartjs-chart" style="height: 320px">
                        <StackedwithGroupsChart />
                    </div>
                </div>
            </b-card>
        </b-col>

        <b-col xl="6">
            <b-card>
                <h4 class="header-title mb-4">Vertical</h4>

                <div dir="ltr">
                    <div class="mt-3 chartjs-chart" style="height: 320px">
                        <VerticalChart />
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

import BorderRadiusChart from "./BorderRadiusChart.vue";
import FloatingChart from "./FloatingChart.vue";
import HorizontalChart from "./HorizontalChart.vue";
import StackedChart from "./StackedChart.vue";
import StackedwithGroupsChart from "./StackedwithGroupsChart.vue";
import VerticalChart from "./VerticalChart.vue";
export default {
    components: {
        Layout,
        Breadcrumb,
        BorderRadiusChart,
        FloatingChart,
        HorizontalChart,
        StackedChart,
        StackedwithGroupsChart,
        VerticalChart,
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
