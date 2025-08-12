<template>
<Layout>
    <Breadcrumb :items="items" :title="title" />

    <b-row>
        <b-col xl="6">
            <b-card>
                <h4 class="header-title">Simple Candlestick Chart</h4>
                <div dir="ltr">
                    <SimpleCandlestickChart class="apex-charts" />
                </div>
            </b-card>
            <!-- end card -->
        </b-col>
        <!-- end col-->

        <b-col xl="6">
            <b-card>
                <h4 class="header-title">Combo Candlestick Chart</h4>
                <div dir="ltr">
                    <ComboCandlestickChart class="apex-charts" />
                    <div id="combo-bar-candlestick" class="apex-charts" />
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
                <h4 class="header-title mb-3">Category X-Axis</h4>
                <div dir="ltr">
                    <CategoryXAxisChart class="apex-charts" />
                </div>
            </b-card>
            <!-- end card -->
        </b-col>
        <!-- end col-->

        <b-col xl="6">
            <b-card>
                <h4 class="header-title mb-3">Candlestick with Line</h4>
                <div dir="ltr">
                    <LineCandlestickChart class="apex-charts" />
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
import SimpleCandlestickChart from './SimpleCandlestickChart.vue'
import ComboCandlestickChart from './ComboCandlestickChart.vue'
import CategoryXAxisChart from './CategoryX-AxisChart.vue'
import LineCandlestickChart from './LineCandlestickChart.vue'
export default {
    components: { Layout, Breadcrumb, SimpleCandlestickChart, ComboCandlestickChart, CategoryXAxisChart, LineCandlestickChart },
    data() {
        return {
            title: 'Candlestick',
            items: [{
                    text: 'Hyper',
                    href: '/'
                },
                {
                    text: 'Apex',
                    href: '/'
                },
                {
                    text: 'Candlestick',
                    active: true
                }
            ]
        }
    },
}
</script>
