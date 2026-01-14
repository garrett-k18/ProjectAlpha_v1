<template>
  <Layout>
    <b-row>
      <b-col class="col-12">
        <div class="page-title-box">
          <h4 class="page-title">Asset Managment Module</h4>
        </div>
      </b-col>
    </b-row>

    <!-- Asset Management Data Grid placed at the top -->
    <b-row>
      <b-col cols="12">
        <AssetGrid ref="assetGridRef" />
      </b-col>
    </b-row>

    <b-row class="mt-3 g-3">
      <b-col lg="7" class="d-flex">
        <AssetDispersion @marker-click="onMarkerClickFromMap" />
      </b-col>

      <b-col lg="5" class="d-flex">
        <AssetAllocation/>
      </b-col>
    </b-row>

    <b-row class="mt-3">
      <b-col xl="6" lg="12" class="order-lg-2 order-xl-1">
        <Products/>
      </b-col>

      <b-col xl="3" lg="6" class="order-lg-1">
        <Projection/>
      </b-col>

      <b-col xl="3" lg="6" class="order-lg-1">
        <Activity/>
      </b-col>
    </b-row>

    <b-row class="mt-3">
      <b-col cols="12">
        <Revenue/>
      </b-col>
    </b-row>

  </Layout>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import Layout from "@/components/layouts/layout.vue";
import Activity from "@/views/dashboards/asset_mgmt/activity.vue";
import Products from "@/views/dashboards/asset_mgmt/products.vue";
import AssetAllocation from "@/views/dashboards/asset_mgmt/assetAllocation.vue";
import Revenue from "@/views/dashboards/asset_mgmt/revenue.vue";
import Projection from "@/views/dashboards/asset_mgmt/projection.vue";
import AssetDispersion from "@/views/dashboards/asset_mgmt/assetdispersion/assetdispersion.vue";
import AssetGrid from "@/views/dashboards/asset_mgmt/asset-grid.vue";
import DateRangePicker from "@/components/custom/date-range-picker.vue";

export default defineComponent({
  name: 'AssetMgmtDashboard',
  components: {
    Layout,
    Activity,
    Products,
    AssetAllocation,
    Revenue,
    Projection,
    AssetDispersion,
    AssetGrid,
    DateRangePicker
  },
  methods: {
    useMeta(meta: { title: string }): void {
      document.title = meta.title;
    },

    // Forward map marker clicks into the existing AM asset modal exposed by AssetGrid.
    onMarkerClickFromMap(payload: { assetHubId: string | number; address?: string | null }): void {
      const grid: any = (this.$refs as any)?.assetGridRef
      if (grid && typeof grid.openAssetModalFromMarker === 'function') {
        grid.openAssetModalFromMarker(payload)
      }
    },
  },
  mounted() {
    this.useMeta({
      title: "Asset Managment Module",
    });
  }
});
</script>
