<template>
  <Layout>
    <Breadcrumb :items="items" :title="title"/>

    <b-row>

      <b-col xl="6">
        <b-card>
          <h4 class="header-title mb-4">Syncing charts</h4>
          <SyncingLineChart/>
        </b-card>
        <!-- end card -->
      </b-col>
      <!-- end col-->

      <b-col xl="6">
        <b-card>
          <h4 class="header-title mb-3">Stepline Chart</h4>
          <div dir="ltr">
            <StepLineChart class="apex-charts"/>
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
          <h4 class="header-title mb-4">Missing / Null values</h4>
          <div dir="ltr">
            <MissingLineChart class="apex-charts"/>
          </div>
        </b-card>
        <!-- end card -->
      </b-col>
      <!-- end col-->

      <b-col xl="6">
        <b-card>
          <h4 class="header-title mb-4">Dashed Line Chart</h4>
          <div dir="ltr">
            <DashedLineChart class="apex-charts"/>
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
          <h4 class="header-title">Brush Chart</h4>
          <div dir="ltr">
            <BrushLineChart/>
          </div>
        </b-card>
        <!-- end card -->
      </b-col>
      <!-- end col-->

      <b-col xl="6">
        <b-card>
          <h4 class="header-title">Realtime Chart</h4>
          <div dir="ltr">
            <RealTimeLineChart class="apex-charts"/>
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
import SyncingLineChart from './SyncingLineChart.vue'
import MissingLineChart from './MissingLineChart.vue'
import DashedLineChart from './DashedLineChart.vue'
import StepLineChart from './StepLineChart.vue'
import BrushLineChart from './BrushLineChart.vue'
import RealTimeLineChart from './RealTimeLineChart.vue'

export default {
  components: {
    Layout,
    Breadcrumb,
    SyncingLineChart,
    MissingLineChart,
    DashedLineChart,
    StepLineChart,
    BrushLineChart,
    RealTimeLineChart
  },
  data() {
    return {
      title: 'Line Charts',
      items: [{
        text: 'Hyper',
        href: '/'
      },
        {
          text: 'Apex',
          href: '/'
        },
        {
          text: 'Line Charts',
          active: true
        }
      ]
    }
  },

}
</script>
