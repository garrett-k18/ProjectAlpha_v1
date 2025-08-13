<template>
  <Layout>
    <Breadcrumb :items="items" :title="title"/>

    <b-row>
      <b-col xl="6">
        <b-card>
          <h4 class="header-title mb-4">Basic Boxplot</h4>
          <div dir="ltr">
            <BasicBoxplotChart class="apex-charts"/>
          </div>
        </b-card>
        <!-- end card -->
      </b-col>
      <!-- end col-->

      <b-col xl="6">
        <b-card>
          <h4 class="header-title mb-4">Scatter Boxplot </h4>
          <div dir="ltr">
            <ScatterBoxplotChart class="apex-charts"/>
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
          <h4 class="header-title mb-4">Horizontal BoxPlot</h4>
          <div dir="ltr">
            <HorizontalBoxplotChart class="apex-charts"/>
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
import BasicBoxplotChart from './BasicBoxplotChart.vue'
import ScatterBoxplotChart from './ScatterBoxplotChart.vue'
import HorizontalBoxplotChart from './HorizontalBoxplotChart.vue'

export default {
  components: {
    Layout, Breadcrumb,
    BasicBoxplotChart,
    ScatterBoxplotChart,
    HorizontalBoxplotChart
  },
  data() {
    return {
      title: 'Boxplot Charts',
      items: [{
        text: 'Hyper',
        href: '/'
      },
        {
          text: 'Apex',
          href: '/'
        },
        {
          text: 'Boxplot Charts',
          active: true
        }
      ]
    }
  },
}
</script>
