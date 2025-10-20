<template>
  <Layout>
    <b-row>
      <b-col class="col-12">
        <div class="page-title-box">
          <h4 class="page-title">Asset Managment Module</h4>
        </div>
      </b-col>
    </b-row>

    <b-row>
      <b-col xl="5" lg="6">
        <Stats/>
      </b-col>

      <b-col xl="7" lg="6">
        <Projection/>
      </b-col>
    </b-row>

    <!-- Asset Management Data Grid placed directly below widgets -->
    <b-row>
      <b-col cols="12">
        <AssetGrid />
      </b-col>
    </b-row>

    <b-row>
      <b-col lg="8">
        <Revenue/>
      </b-col>

      <b-col lg="4">
        <AssetDispersion/>
      </b-col>
    </b-row>

    <b-row>
      <b-col xl="6" lg="12" class="order-lg-2 order-xl-1">
        <Products/>
      </b-col>

      <b-col xl="3" lg="6" class="order-lg-1">
        <Sales/>
      </b-col>

      <b-col xl="3" lg="6" class="order-lg-1">
        <Activity/>
      </b-col>
    </b-row>

  </Layout>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import Layout from "@/components/layouts/layout.vue";
import Activity from "@/views/dashboards/asset_mgmt/activity.vue";
import Products from "@/views/dashboards/asset_mgmt/products.vue";
import Sales from "@/views/dashboards/asset_mgmt/sales.vue";
import Revenue from "@/views/dashboards/asset_mgmt/revenue.vue";
import Projection from "@/views/dashboards/asset_mgmt/projection.vue";
import Stats from "@/views/dashboards/asset_mgmt/stats.vue";
import AssetDispersion from "@/views/dashboards/asset_mgmt/assetdispersion/assetdispersion.vue";
import AssetGrid from "@/views/dashboards/asset_mgmt/asset-grid.vue";
import DateRangePicker from "@/components/custom/date-range-picker.vue";

export default defineComponent({
  name: 'AssetMgmtDashboard',
  components: {
    Layout,
    Activity,
    Products,
    Sales,
    Revenue,
    Projection,
    Stats,
    AssetDispersion,
    AssetGrid,
    DateRangePicker
  },
  methods: {
    useMeta(meta: { title: string }): void {
      document.title = meta.title;
    }
  },
  mounted() {
    this.useMeta({
      title: "Asset Managment Module",
    });
  }
});
</script>
