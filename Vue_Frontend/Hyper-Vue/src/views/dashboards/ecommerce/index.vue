<template>
  <Layout>
    <b-row>
      <b-col class="col-12">
        <div class="page-title-box">
          <div class="page-title-right">
            <form class="d-flex">
              <div class="input-group">
                <DateRangePicker id="dash-daterange" class="form-control form-control-light" />
                <span class="input-group-text bg-primary border-primary text-white">
                                                    <i class="mdi mdi-calendar-range font-13"></i>
                                                </span>
              </div>
              <a href="javascript: void(0);" class="btn btn-primary ms-2">
                <i class="mdi mdi-autorenew"></i>
              </a>
              <a href="javascript: void(0);" class="btn btn-primary ms-1">
                <i class="mdi mdi-filter-variant"></i>
              </a>
            </form>
          </div>
          <h4 class="page-title">Dashboard</h4>
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


    <b-row>
      <b-col lg="8">
        <Revenue/>
      </b-col>

      <b-col lg="4">
        <RevenueByLoc/>
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
import Layout from "@/components/layouts/layout.vue";
import Activity from "@/views/dashboards/ecommerce/activity.vue";
import Products from "@/views/dashboards/ecommerce/products.vue";
import Sales from "@/views/dashboards/ecommerce/sales.vue";
import Revenue from "@/views/dashboards/ecommerce/revenue.vue";
import Projection from "@/views/dashboards/ecommerce/projection.vue";
import Stats from "@/views/dashboards/ecommerce/stats.vue";
import RevenueByLoc from "@/views/dashboards/ecommerce/revenue-by-loc.vue";
import DateRangePicker from "@/components/custom/date-range-picker.vue";

export default {
  components: {DateRangePicker, RevenueByLoc, Stats, Projection, Revenue, Sales, Products, Activity, Layout},
  mounted() {
    this.useMeta({
      title: "Dashboard",
    });
  }
}
</script>
