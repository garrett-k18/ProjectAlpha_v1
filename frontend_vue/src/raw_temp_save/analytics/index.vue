<template>
  <Layout>
    <b-row>
      <b-col class="col-12">
        <div class="page-title-box">
          <div class="page-title-right">
            <form class="d-flex">
              <div class="input-group">
                <DateRangePicker id="dash-daterange" class="form-control form-control-light"  />
                <span
                  class="input-group-text bg-primary border-primary text-white"
                >
                  <i class="mdi mdi-calendar-range font-13"></i>
                </span>
              </div>
              <a href="javascript: void(0);" class="btn btn-primary ms-2">
                <i class="mdi mdi-autorenew"></i>
              </a>
            </form>
          </div>
          <h4 class="page-title">Acquisitions</h4>
        </div>
      </b-col>
    </b-row>

    <b-row>
      <b-col xl="3" lg="4">
        <div class="card tilebox-one">
          <div class="card-body">
            <i class="uil uil-users-alt float-end"></i>
            <h6 class="text-uppercase mt-0">Active Users</h6>
            <h2 class="my-2" id="active-users-count">121</h2>
            <p class="mb-0 text-muted">
              <span class="text-success me-2"
                ><span class="mdi mdi-arrow-up-bold"></span> 5.27%</span
              >
              <span class="text-nowrap">Since last month</span>
            </p>
          </div>
        </div>

        <div class="card tilebox-one">
          <div class="card-body">
            <i class="uil uil-window-restore float-end"></i>
            <h6 class="text-uppercase mt-0">Views per minute</h6>
            <h2 class="my-2" id="active-views-count">560</h2>
            <p class="mb-0 text-muted">
              <span class="text-danger me-2"
                ><span class="mdi mdi-arrow-down-bold"></span> 1.08%</span
              >
              <span class="text-nowrap">Since previous week</span>
            </p>
          </div>
        </div>

        <div class="card cta-box overflow-hidden">
          <div class="card-body">
            <div class="d-flex align-items-center">
              <div>
                <h3 class="m-0 fw-normal cta-box-title">
                  Enhance your <b>Campaign</b> for better outreach
                  <i class="mdi mdi-arrow-right"></i>
                </h3>
              </div>
              <img
                class="ms-3"
                src="@/assets/images/svg/email-campaign.svg"
                width="92"
                alt="Generic placeholder image"
              />
            </div>
          </div>
        </div>
      </b-col>

      <b-col xl="9" lg="8">
        <Overview />
      </b-col>
    </b-row>

    <b-row>
      <b-col class="col-12">
        <Country />
      </b-col>
    </b-row>

    <b-row>
      <b-col xl="4" lg="12">
        <Views />
      </b-col>

      <b-col xl="4" lg="6">
        <Browser />
      </b-col>

      <b-col xl="4" lg="6">
        <System />
      </b-col>
    </b-row>

    <b-row>
      <b-col xl="4" lg="6">
        <Channel />
      </b-col>

      <b-col xl="4" lg="6">
        <Media />
      </b-col>

      <b-col xl="4" lg="12">
        <EngagementOverview />
      </b-col>
    </b-row>
  </Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import DateRangePicker from "@/components/custom/date-range-picker.vue";
import Overview from "@/views/dashboards/acquisitions/overview.vue";
import Views from "@/views/dashboards/acquisitions/views.vue";
import Browser from "@/views/dashboards/acquisitions/browser.vue";
import System from "@/views/dashboards/acquisitions/system.vue";
import Channel from "@/views/dashboards/acquisitions/channel.vue";
import Media from "@/views/dashboards/acquisitions/media.vue";
import EngagementOverview from "@/views/dashboards/acquisitions/engagement-overview.vue";
import Country from "@/views/dashboards/acquisitions/country.vue";

export default {
  components: {
    Country,
    EngagementOverview,
    Media,
    Channel,
    System,
    Browser,
    Views,
    Overview,
    DateRangePicker,
    Layout,
  },
  mounted() {
    // this.useMeta({
    //   title: "Acquisitions Dashboard",
    // });
  }
};
</script>
