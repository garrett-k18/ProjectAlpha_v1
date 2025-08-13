<template>
  <Layout>
    <Breadcrumb :title="title" :items="items" />

    <div>
      <Stats />
    </div>

    <b-row>
      <b-col lg="5">
        <Campaign />
      </b-col>

      <b-col lg="7">
        <Revenue />
      </b-col>
    </b-row>

    <b-row>
      <b-col xl="4" lg="12">
        <Performing />
      </b-col>

      <b-col xl="4" lg="6">
        <Leads />
      </b-col>

      <b-col xl="4" lg="6">
        <div class="card cta-box bg-primary text-white">
          <div class="card-body">
            <div class="d-flex align-items-start align-items-center">
              <div class="w-100 overflow-hidden">
                <h2 class="mt-0 text-reset">
                  <i class="mdi mdi-bullhorn-outline"></i>&nbsp;
                </h2>
                <h3 class="m-0 fw-normal cta-box-title text-reset">
                  Enhance your <b>Campaign</b> for better outreach
                  <i class="mdi mdi-arrow-right"></i>
                </h3>
              </div>
              <img
                class="ms-3"
                src="@/assets/images/svg/email-campaign.svg"
                width="120"
                alt="Generic placeholder image"
              />
            </div>
          </div>
          <!-- end card-body -->
        </div>
 

        <Todo />
      </b-col>
 
    </b-row>

  </Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";
import Campaign from "@/views/dashboards/crm/campaign.vue";
import Leads from "@/views/dashboards/crm/leads.vue";
import Performing from "@/views/dashboards/crm/performing.vue";
import Revenue from "@/views/dashboards/crm/revenue.vue";
import Status from "@/views/dashboards/projects/status.vue";
import Stats from "@/views/dashboards/crm/stats.vue";
import Todo from "@/views/dashboards/crm/todo.vue";

export default {
  components: {
    Todo,
    Stats,
    Status,
    Revenue,
    Performing,
    Leads,
    Campaign,
    Breadcrumb,
    Layout,
  },
  data(){
    return{
      title: 'CRM',
      items: [
        {
          text: 'Hyper',
          href: '/',
        },
        {
          text: 'Dashboard',
          href: '/',
        },
        {
          text: 'CRM',
          active: true,
        },
      ],
    }
  }
};
</script>
