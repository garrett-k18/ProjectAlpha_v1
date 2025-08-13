<template>
  <Layout>
    <Breadcrumb :title="title" :items="items"/>
    <b-row>
      <b-col xxl="6">
        <RevenueStatistics/>
      </b-col> <!-- End col -->

      <b-col xxl="6">
        <div class="row">
          <Stats/>
        </div> <!-- end row -->
      </b-col>
    </b-row> <!-- End row -->

    <h4 class="page-title mb-3">Recently Updated Clients</h4>

    <b-row class="row-cols-1 row-cols-sm-2 row-cols-lg-3 row-cols-xxl-5">

      <b-col v-for="(client,index) in updatedClientsData" :key="index">
        <div class="card">
          <div class="card-body">
            <div class="d-flex">
              <div class="flex-shrink-0">
                <img class="rounded-circle avatar-sm" :src="client.img" alt="Avtar image">
              </div>
              <div class="flex-grow-1 ms-2">
                <a href="javascript:void(0);" class="text-secondary"><h5 class="my-1">{{ client.name }}</h5></a>
                <p class="text-muted mb-0">{{ client.company }}</p>
              </div>

              <b-dropdown class="float-end" variant="white" right toggle-tag="a"
                          toggle-class="card-drop arrow-none p-0">
                <template v-slot:button-content>
                  <i class="mdi mdi-dots-horizontal"></i>
                </template>
                <b-dropdown-item href="javascript: void(0);"><i class="mdi mdi-account me-1"></i>Visite Profilo
                </b-dropdown-item>
                <b-dropdown-item href="javascript: void(0);"><i class="mdi mdi-block-helper me-1"></i>Block
                </b-dropdown-item>
                <b-dropdown-divider/>
                <b-dropdown-item href="javascript: void(0);" class="text-danger"><i
                    class="mdi mdi-trash-can-outline me-1"></i>Remov
                </b-dropdown-item>
              </b-dropdown>


            </div>
          </div>
          <div class="d-flex justify-content-between align-items-center card-body py-2 border-top border-light">
            <h5 class="my-0 font-13 fw-semibold text-muted"><i class="mdi mdi-calendar me-1"></i> {{ client.date }}</h5>
            <a href="javascript:void(0);" class="text-muted" @click="showModal = !showModal"><i
                class="uil uil-comment-alt-lines font-18" v-b-tooltip.hover
                title="Chat"></i></a>
          </div>
        </div>
      </b-col> <!-- end col -->

    </b-row> <!-- end row -->

    <b-row>
      <b-col xxl="6">
       <MonthlyProgress />
      </b-col> <!-- end col -->

      <b-col md="6" xxl="3">
        <TaskStatus />
      </b-col> <!-- end col -->

      <b-col md="6" xxl="3">
        <Calendar />
      </b-col> <!-- end col -->
    </b-row>


    <!-- Modal -->
    <b-modal v-model="showModal"
             hide-header
             hide-footer
             centered
             body-class="p-0"
    >

      <div class="modal-header">
        <h5 class="modal-title" id="exampleModalLabel">
          <div class="d-flex align-items-center">
            <div class="flex-shrink-0">
              <img class="rounded-circle" src="@/assets/images/users/avatar-4.jpg" height="40" alt="Avtar image">
            </div>
            <div class="flex-grow-1 ms-2">
              <a href="javascript:void(0);" class="text-secondary">Kevin Snowden</a>
              <p class="text-muted fw-normal font-14 mb-0"><i class="mdi mdi-circle text-success font-12 me-1"></i>Online
              </p>
            </div>
          </div>
        </h5>
        <button type="button" class="btn-close" @click="showModal=!showModal"></button>
      </div>
      <div class="modal-body">
        <div class="chat-conversation">
          <div data-simplebar style="height: 350px;">
            <ul class="conversation-list">

              <li v-for="(item,index) in chatData" :key="index" :class="(index%2) == 0?'clearfix':'clearfix odd'">
                <div class="chat-avatar">
                  <img :src="item.img" alt="male">
                  <i>{{ item.time }}</i>
                </div>
                <div class="conversation-text">
                  <div class="ctext-wrap">
                    <i>{{ item.name }}</i>
                    <p>
                      {{ item.message }}
                    </p>
                  </div>
                </div>
              </li>

            </ul>
          </div>
          <b-form class="needs-validation" novalidate name="chat-form" id="chat-form">
            <b-row class="align-items-start">
              <b-col>
                <input type="text" class="form-control chat-input" placeholder="Enter your text" required>
                <div class="invalid-feedback">
                  Please enter your message
                </div>
              </b-col>
              <b-col class="col-auto d-grid">
                <b-button variant="danger" type="submit" class="chat-send waves-effect waves-light">Send</b-button>
              </b-col>
            </b-row>
          </b-form>
        </div>
      </div>
    </b-modal>


  </Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";
import RevenueStatistics from "@/views/apps/crm/management/revenue-statistics.vue";
import Stats from "@/views/apps/crm/management/stats.vue";
import MonthlyProgress from "@/views/apps/crm/management/monthly-progress.vue";
import TaskStatus from "@/views/apps/crm/management/task-status.vue";
import Calendar from "@/views/apps/crm/management/calendar.vue";

import avatar1 from '@/assets/images/users/avatar-1.jpg'
import avatar2 from '@/assets/images/users/avatar-2.jpg'
import avatar3 from '@/assets/images/users/avatar-3.jpg'
import avatar5 from '@/assets/images/users/avatar-5.jpg'
import avatar6 from '@/assets/images/users/avatar-6.jpg'

export default {
  components: {Calendar, TaskStatus, MonthlyProgress, Stats, RevenueStatistics, Breadcrumb, Layout},
  data() {
    return {
      title: 'Management',
      items: [
        {
          text: 'Hyper',
          href: '/',
        },
        {
          text: 'CRM',
          href: '/',
        },
        {
          text: 'Management',
          active: true,
        },
      ],
      showModal: false,

      updatedClientsData: [
        {
          img: avatar1,
          name: 'Kevin Snowden',
          company: 'Simple Solutions LLC',
          date: 'Jan 05 2022'
        },
        {
          img: avatar2,
          name: 'Steven Embry',
          company: 'Flipside Records LLC',
          date: 'Jan 10 2022'
        },
        {
          img: avatar3,
          name: 'James McDonald',
          company: 'Vision Clinics LLC',
          date: 'Jan 12 2022'
        },
        {
          img: avatar5,
          name: 'Ralph Wolford',
          company: 'Merry-Go-Round LLC',
          date: 'Jan 18 2022'
        },
        {
          img: avatar6,
          name: 'Tomas Cooper',
          company: 'Museum LLC',
          date: 'Feb 02 2022'
        },
      ],
      chatData: [
        {
          img: avatar5,
          name: 'Geneva',
          message: 'Hello!',
          time: '10:00'
        },
        {
          img: avatar1,
          name: 'Dominic',
          message: 'Hi, How are you? What about our next meeting?',
          time: '10:01'
        },
        {
          img: avatar5,
          name: 'Geneva',
          message: 'Yeah everything is fine',
          time: '10:01'
        },
        {
          img: avatar1,
          name: 'Dominic',
          message: 'Wow that\'s great',
          time: '10:02'
        },
      ]
    }
  }

}
</script>
