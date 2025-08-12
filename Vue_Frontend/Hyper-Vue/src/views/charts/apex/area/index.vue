<template>
<Layout>
    <Breadcrumb :title="title" :items="items" />
    <b-row>
        <b-col xl="6">
            <b-card>
                <h4 class="header-title mb-4">Basic Area Chart</h4>
                <div dir="ltr">
                    <BasicAreaChart />
                </div>
            </b-card>
        </b-col>

        <b-col xl="6">
            <b-card>
                <h4 class="header-title mb-4">Spline Area</h4>
                <div dir="ltr">
                    <SplineAreaChart />
                </div>
            </b-card>
        </b-col>
    </b-row>

    <b-row>
        <b-col xl="6">
            <b-card>
                <h4 class="header-title mb-4">Area Chart - Datetime X-axis</h4>
                <AreaDatetimeChart />
            </b-card>
        </b-col>

        <b-col xl="6">
            <b-card>
                <h4 class="header-title mb-4">Area with Negative Values</h4>
                <div dir="ltr">
                    <NegativeAreaChart />
                </div>
            </b-card>
        </b-col>
    </b-row>

    <b-row>
        <b-col xl="6">
            <b-card>
                <h4 class="header-title mb-4">Selection - Github Style</h4>
                <div dir="ltr">
                    <GithubStyleChart />
                </div>
            </b-card>
        </b-col>
    </b-row>

</Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";

import BasicAreaChart from "./BasicAreaChart.vue";
import SplineAreaChart from "./SplineAreaChart.vue";
import AreaDatetimeChart from "./AreaDatetimeChart.vue";
import NegativeAreaChart from "./NegativeAreaChart.vue";
import GithubStyleChart from "./GithubStyleChart.vue";

export default {
    components: {
        Layout,
        Breadcrumb,
        BasicAreaChart,
        SplineAreaChart,
        AreaDatetimeChart,
        NegativeAreaChart,
        GithubStyleChart,
    },
    data() {
        return {
            title: "Area Charts",
            items: [{
                    text: "Hyper",
                    href: "/",
                },
                {
                    text: "Apex",
                    href: "/",
                },
                {
                    text: "Area Charts",
                    active: true,
                },
            ],
        }
    }

};
</script>
