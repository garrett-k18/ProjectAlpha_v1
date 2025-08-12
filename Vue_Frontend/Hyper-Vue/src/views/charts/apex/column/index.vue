<template>
<Layout>
    <Breadcrumb :items="items" :title="title" />

    <div class="row">
        <div class="col-xl-6">
            <div class="card">
                <div class="card-body">
                    <h4 class="header-title">Basic Column Chart</h4>
                    <div dir="ltr">
                        <BasicColumnChart class="apex-charts" />
                    </div>
                </div>
                <!-- end card body-->
            </div>
            <!-- end card -->
        </div>
        <!-- end col-->

        <div class="col-xl-6">
            <div class="card">
                <div class="card-body">
                    <h4 class="header-title mb-3">Column Chart with Datalabels</h4>
                    <div dir="ltr">
                        <DatatablesChart class="apex-charts" />
                    </div>
                </div>
                <!-- end card body-->
            </div>
            <!-- end card -->
        </div>
        <!-- end col-->
    </div>
    <!-- end row-->

    <div class="row">
        <div class="col-xl-6">
            <div class="card">
                <div class="card-body">
                    <h4 class="header-title">Stacked Column Chart</h4>
                    <div dir="ltr">
                        <StackedColumnChart class="apex-charts" />
                    </div>
                </div>
                <!-- end card body-->
            </div>
            <!-- end card -->
        </div>
        <!-- end col-->

        <div class="col-xl-6">
            <div class="card">
                <div class="card-body">
                    <h4 class="header-title">100% Stacked Column Chart</h4>
                    <div dir="ltr">
                        <Stacked100ColumnChart class="apex-charts" />
                    </div>
                </div>
                <!-- end card body-->
            </div>
            <!-- end card -->
        </div>
        <!-- end col-->
    </div>
    <!-- end row-->

    <div class="row">
        <div class="col-xl-6">
            <div class="card">
                <div class="card-body">
                    <h4 class="header-title">Column with Markers</h4>
                    <div dir="ltr">
                        <ColumnwithMarkersChart class="apex-charts" />
                    </div>
                </div>
                <!-- end card body-->
            </div>
            <!-- end card -->
        </div>
        <!-- end col-->

        <div class="col-xl-6">
            <div class="card">
                <div class="card-body">
                    <h4 class="header-title">Column with Group Label</h4>
                    <div dir="ltr">
                        <ColumnwithGrouplabelChart class="apex-charts" />
                    </div>
                </div>
                <!-- end card body-->
            </div>
            <!-- end card -->
        </div>
        <!-- end col-->
    </div>
    <!-- end row-->

    <div class="row">
        <div class="col-xl-6">
            <div class="card">
                <div class="card-body">
                    <h4 class="header-title">Column Chart with rotated labels & Annotations</h4>
                    <div dir="ltr">
                        <RoatedLabelsChart class="apex-charts" />
                    </div>
                </div>
                <!-- end card body-->
            </div>
            <!-- end card -->
        </div>
        <!-- end col-->

        <div class="col-xl-6">
            <div class="card">
                <div class="card-body">
                    <h4 class="header-title">Column Chart with negative values</h4>
                    <div dir="ltr">
                        <NegativeValueChart class="apex-charts" />
                    </div>
                </div>
                <!-- end card body-->
            </div>
            <!-- end card -->
        </div>
        <!-- end col-->
    </div>
    <!-- end row-->

    <div class="row">
        <div class="col-xl-6">
            <div class="card">
                <div class="card-body">
                    <h4 class="header-title">Distributed Column Chart</h4>
                    <div dir="ltr">
                        <DistributedColumnChart class="apex-charts" />
                    </div>
                </div>
                <!-- end card body-->
            </div>
            <!-- end card -->
        </div>
        <!-- end col-->

        <div class="col-xl-6">
            <div class="card">
                <div class="card-body">
                    <h4 class="header-title">Range Column Chart</h4>
                    <div dir="ltr">
                        <RangeColumnChart class="apex-charts" />
                    </div>
                </div>
                <!-- end card body-->
            </div>
            <!-- end card -->
        </div>
        <!-- end col-->
    </div>
    <!-- end row-->

    <b-row>
        <b-col cols="12">
            <div class="card">
                <div class="d-flex card-header justify-content-between align-items-center">
                    <h4 class="header-title">Dynamic Loaded Chart</h4>
                    <div class="flex-shrink-0">
                        <b-form-select v-model="selected" :options="options" id="model" class="form-select-sm">
                        </b-form-select>
                    </div>
                </div>

                <div class="card-body pt-0">
                    <h4 class="header-title"></h4>
                    <DynamicLoadedChart />
                </div>
                <!-- end card body-->
            </div>
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
import BasicColumnChart from './BasicColumnChart.vue'
import DatatablesChart from './DatatablesChart.vue'
import StackedColumnChart from './StackedColumnChart.vue'
import Stacked100ColumnChart from './Stacked100ColumnChart.vue'
import ColumnwithMarkersChart from './ColumnwithMarkersChart.vue'
import ColumnwithGrouplabelChart from './ColumnwithGrouplabelChart.vue'
import RoatedLabelsChart from './RoatedLabelsChart.vue'
import NegativeValueChart from './NegativeValueChart.vue'
import DistributedColumnChart from './DistributedColumnChart.vue'
import RangeColumnChart from './RangeColumnChart.vue'
import DynamicLoadedChart from './dynamic-loaded-chart/DynamicLoadedChart.vue'
export default {
    components: { Layout, Breadcrumb, BasicColumnChart, DatatablesChart, StackedColumnChart, Stacked100ColumnChart, ColumnwithMarkersChart, ColumnwithGrouplabelChart, RoatedLabelsChart, NegativeValueChart, DistributedColumnChart, RangeColumnChart, DynamicLoadedChart   },
    data() {
        return {

            title: 'Column',
            items: [{
                    text: 'Hyper',
                    href: '/'
                },
                {
                    text: 'Apex',
                    href: '/'
                },
                {
                    text: 'Column',
                    active: true
                }
            ],
            selected: 'iphone5',
            options: [
                { value: 'iphone5', text: 'iPhone 5' },
                { value: 'iphone6', text: 'iPhone 6' },
                { value: 'iphone7', text: 'iPhone 7' },
            ]
        }
    },
}
</script>
