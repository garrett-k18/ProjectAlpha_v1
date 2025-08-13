<template>
  <Layout>
    <Breadcrumb :items="items" :title="title"/>

    <b-row>
      <b-col xl="6">
        <b-card>
          <h4 class="header-title">Basic Polar Area Chart</h4>
          <div dir="ltr">
            <BasicPolarAreaChart class="apex-charts"/>
          </div>
        </b-card>
        <!-- end card -->
      </b-col>
      <!-- end col-->

      <b-col xl="6">
        <b-card>
          <h4 class="header-title">Monochrome Polar Area</h4>
          <div dir="ltr">
            <MonochromePolarArea class="apex-charts"/>
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
import BasicPolarAreaChart from './BasicPolarAreaChart.vue'
import MonochromePolarArea from './MonochromePolarArea.vue'

export default {
  components: {
    Layout,
    Breadcrumb,
    BasicPolarAreaChart,
    MonochromePolarArea
  },
  data() {
    return {
      title: 'Polar Area Charts',
      items: [{
        text: 'Hyper',
        href: '/'
      },
        {
          text: 'Apex',
          href: '/'
        },
        {
          text: 'Polar Area Charts',
          active: true
        }
      ]
    }
  },
}
</script>
