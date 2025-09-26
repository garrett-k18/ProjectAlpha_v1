<template>
  <Layout>
    <Breadcrumb
        :title="title"
        :items="items"
    />

    <b-row>
      <b-col xl="4" lg="12">
        <div class="card">
          <div class="card-body">
            <Profile :image="profileData.img" :name="profileData.name" :role="profileData.role" :revenue="profileData.revenue" :orders="profileData.orders" text-color="secondary" />
          </div>
          <!-- end card-body-->
        </div>
      </b-col>

      <b-col xl="4" sm="6"
          v-for="data of statData"
          :key="data.chartType"
      >
        <Stat
            :title="data.title"
            :subtitle="data.subtitle"
            :chart-color="data.chartColor"
            :chart-data="data.chartData"
            :chart-type="data.chartType"
        />
      </b-col>
      <!-- end col -->
    </b-row>
    <!-- end row -->

    <b-row>
      <b-col xxl="3" sm="6"
          v-for="stat of statIcon"
          :key="stat.icon"
      >
        <StatIcon
            :icon="stat.icon"
            :icon-color="stat.iconColor"
            :title="stat.title"
            :number="stat.number"
            :subtext="stat.subtext"
            :color="stat.color"

        />
      </b-col>
      <!-- end col -->
    </b-row>
    <!-- end row -->

    <b-row>
      <b-col xxl="3" sm="6"
          v-for="chart of statChart"
          :key="chart.title"
    
      >
        <div class="card">
          <div class="card-body">
            <StatChart
                :title="chart.title"
                :number="chart.number"
                :chart-data="chart.chartData"
                :chart-color="chart.chartColor"
                :chart-type="chart.chartType"
                :subtext="chart.subtext"
            />
          </div>
        </div>
      </b-col>
      <!-- end col -->
    </b-row>
    <!-- end row -->

    <b-row>
      <b-col xl="4">
        <!-- chat -->
        <Chat
            :chat-messages="chatMessages"
            :chat-window-height="chatWindowHeight"
        />
      </b-col>
      <!-- end col -->
      <b-col xl="4">
        <div class="card cta-box text-bg-danger">
          <div class="card-body">
            <div class="d-flex align-items-center">
              <div class="w-100 overflow-hidden">
                <h2 class="mt-0 text-reset">
                  <i class="mdi mdi-bullhorn-outline"></i>
                </h2>
                <h3 class="m-0 fw-normal cta-box-title text-reset">
                  Enhance your
                  <b>Campaign</b> for better outreach
                  <i class="mdi mdi-arrow-right-bold-outline"></i>
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
        <!-- end card-->

        <div class="card cta-box text-bg-primary">
          <div class="card-body">
            <div class="text-center">
              <h3 class="m-0 fw-normal cta-box-title text-reset">
                Enhance your
                <b>Campaign</b> for better outreach
              </h3>

              <img
                  class="my-3"
                  src="@/assets/images/svg/report.svg"
                  width="180"
                  alt="Generic placeholder image"
              />

              <br />

              <a
                  href="javascript:void(0);"
                  class="btn btn-sm btn-light btn-rounded"
              >
                Know More
                <i class="mdi mdi-arrow-right"></i>
              </a>
            </div>
          </div>
          <!-- end card-body -->
        </div>
        <!-- end card-->
      </b-col>
      <b-col xl="4">
        <!-- Todo -->
        <ToDoList
            :items="todoItems"
            :todo-window-height="todoWindowHeight"
        />
      </b-col>
    </b-row>
    <!-- end row -->

    <b-row>
      <b-col xl="4">
        <!-- Messages -->
        <Message :messages="messages" />
      </b-col>
      <b-col xl="4">
        <!-- Recent-activity -->
        <RecentActivity
            :activity-data="activityData"
            :activity-window-height="activityWindowHeight"
        />
      </b-col>
      <b-col xl="4">
        <!-- Transactions -->
        <Transactions :transactions="transactions" :transaction-window-height="transactionWindowHeight" />
      </b-col>
    </b-row>
    <!-- end row -->

    <b-row>
      <b-col xxl="3" md="6"
          v-for="item of chartData"
          :key="item.title"
      >
        <StatChart3
            :title="item.title"
            :number="item.number"
            :chart-color="item.chartColor"
            :chart-data="item.chartData"
            :chart-type="item.chartType"
            :last-month="item.lastMonth"
            :current-month="item.currentMonth"
        />
      </b-col>
      <!-- end col -->
    </b-row>
    <!-- end row -->

    <b-row>
      <b-col lg="4">
        <div class="card text-bg-info overflow-hidden">
          <div class="card-body">
            <div class="toll-free-box text-center">
              <h4 class="text-reset">
                <i class="mdi mdi-deskphone"></i> Toll Free : 1-234-567-8901
              </h4>
            </div>
          </div>
          <!-- end card-body-->
        </div>
        <!-- end card -->
      </b-col>
      <!-- end col-->

      <b-col lg="4">
        <div class="card text-bg-danger overflow-hidden">
          <div class="card-body">
            <div class="toll-free-box text-center">
              <h4 class="text-reset">
                <i class="mdi mdi-headset"></i> Need help ? Just contact us
              </h4>
            </div>
          </div>
          <!-- end card-body-->
        </div>
        <!-- end card -->
      </b-col>
      <!-- end col-->

      <b-col lg="4">
        <div class="card text-bg-success">
          <div class="card-body">
            <div class="text-center">
              <h4 class="text-reset">
                <i class="mdi mdi-deskphone"></i> Toll Free : 1-234-567-8901
              </h4>
            </div>
          </div>
          <!-- end card-body-->
        </div>
        <!-- end card -->
      </b-col>
      <!-- end col-->
    </b-row>
    <!-- end row -->
  </Layout>
</template>
<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";

import Profile from '@/components/widgets/profile.vue'
import Stat from '@/components/widgets/widget-stat.vue'
import StatIcon from '@/components/widgets/widget-stat-icon.vue'
import StatChart from '@/components/widgets/widget-stat-chart-1.vue'
import Chat from '@/components/widgets/chat.vue'
import ToDoList from '@/components/widgets/todo-list.vue'
import Message from '@/components/widgets/message.vue'
import RecentActivity from '@/views/am_module/loanlvl/am_tasking/recent-activity.vue'
import Transactions from '@/components/widgets/transactions.vue'
import StatChart3 from '@/components/widgets/widget-stat-chart-3.vue'

import avatar1 from '@/assets/images/users/avatar-1.jpg'
import avatar2 from '@/assets/images/users/avatar-2.jpg'
import avatar3 from '@/assets/images/users/avatar-3.jpg'
import avatar4 from '@/assets/images/users/avatar-4.jpg'
import avatar5 from '@/assets/images/users/avatar-5.jpg'
import avatar6 from '@/assets/images/users/avatar-6.jpg'

export default {

  components: {
    Layout,
    Breadcrumb,
    Profile,
    Stat,
    StatIcon,
    StatChart,
    Chat,
    ToDoList,
    Message,
    RecentActivity,
    Transactions,
    StatChart3,
  },
  data() {
    return {
      title: 'Widgets',
      items: [
        {
          text: 'Hyper',
          href: '/',
        },
        {
          text: 'Components',
          href: '/',
        },
        {
          text: 'Widgets',
          active: true,
        },
      ],
      profileData:{
        img:avatar2,
        name:'Michael Franklin',
        role:'Authorised Brand Seller',
        revenue:'25,184',
        orders:5482
      },
      statData: [
        {
          title: '$424,652',
          subtitle: 'Sales',
          chartColor: '#3688fc',
          chartData: [
            47,
            45,
            54,
            38,
            56,
            24,
            65,
            31,
            37,
            39,
            62,
            51,
            35,
            41,
            35,
            27,
            93,
            53,
            61,
            27,
            54,
            43,
            19,
            46,
          ],
          chartType: 'area',
        },
        {
          title: '$135,965',
          subtitle: 'Profits',
          chartColor: '#0acf97',
          chartData: [
            47,
            45,
            54,
            38,
            56,
            24,
            65,
            31,
            37,
            39,
            62,
            51,
            35,
            41,
            35,
            27,
            93,
            53,
            61,
            27,
            54,
            43,
            19,
            46,
          ],
          chartType: 'bar',
        },
      ],
      statIcon: [
        {
          icon: 'mdi-currency-btc',
          iconColor:'danger',
          number: '$6,254',
          title: 'Revenue',
          color: 'danger',
          subtext: '7.00%',
        },
        {
          icon: 'mdi-pulse widget-icon',
          iconColor:'primary',
          number: '+ 30.56%',
          title: 'Growth',
          color: 'success',
          subtext: '4.87%',
        },
        {
          icon: 'mdi-account-multiple',
          iconColor:'warning',
          number: '36,254',
          title: 'Customers',
          color: 'success',
          subtext: '5.27%',
        },
        {
          icon: 'mdi-currency-usd',
          iconColor:'success',
          number: '$10,245',
          title: 'Revenue',
          color: 'danger',
          subtext: '1.08%',
        },
      ],
      statChart: [
        {
          title: 'Campaign Sent',
          number: '9,184',
          subtext: '3.27%',
          chartData: [25, 66, 41, 89, 63, 25, 44, 12, 36, 9, 54],
          chartColor: '#727cf5',
          chartType: 'bar',
        },
        {
          title: 'New Leads',
          number: '3,254',
          subtext: '5.38%',
          chartData: [25, 66, 41, 89, 63, 25, 44, 12, 36, 9, 54],
          chartColor: '#727cf5',
          chartType: 'line',
        },
        {
          title: 'Deals',
          number: '861',
          subtext: '4.87%',
          chartData: [12, 14, 2, 47, 42, 15, 47, 75, 65, 19, 14],
          chartColor: '#727cf5',
          chartType: 'bar',
        },
        {
          title: 'Booked Revenue',
          number: '$253k',
          subtext: '11.7%',
          chartData: [47, 45, 74, 14, 56, 74, 14, 11, 7, 39, 82],
          chartColor: '#727cf5',
          chartType: 'bar',
        },
      ],
      chatMessages: [
        {
          id: 1,
          image: avatar5,
          name: 'Geneva',
          message: 'Hello!',
          time: '10:00',
        },
        {
          id: 2,
          image: avatar1,
          name: 'Dominic',
          message: 'Hi, How are you? What about our next meeting?',
          time: '10:01',
        },
        {
          id: 3,
          image: avatar5,
          name: 'Geneva',
          message: 'Yeah everything is fine',
          time: '10:01',
        },
        {
          id: 4,
          image: avatar1,
          name: 'Dominic',
          message: "Wow that's great",
          time: '10:02',
        },
        {
          id: 5,
          image: avatar5,
          name: 'Geneva',
          message: 'Yup!',
          time: '10:03',
        },
      ],
      todoItems: [
        {
          id: 1,
          task: 'Build an angular app',
          isCompleted: true,
        },
        {
          id: 2,
          task: 'Create new version 3.0',
          isCompleted: false,
        },
        {
          id: 3,
          task: 'Hehe!! This is looks cool!',
          isCompleted: false,
        },
        {
          id: 4,
          task: 'Testing??',
          isCompleted: true,
        },
        {
          id: 5,
          task: 'Creating component page',
          isCompleted: true,
        },
        {
          id: 6,
          task: 'Build a js based app',
          isCompleted: true,
        },
        {
          id: 7,
          task: 'Design One page theme',
          isCompleted: false,
        },
        {
          id: 8,
          task: "That's Brilliant",
          isCompleted: true,
        },
      ],
      messages: [
        {
          image: avatar2,
          name: 'Tomaslau',
          message: "I've finished it! See you so...",
        },
        {
          image: avatar3,
          name: 'Stillnotdavid',
          message: 'This theme is awesome!',
        },
        {
          image: avatar4,
          name: 'Kurafire',
          message: 'Nice to meet you',
        },
        {
          image: avatar5,
          name: 'Shahedk',
          message: "Hey! there I'm available...",
        },
        {
          image: avatar6,
          name: 'Adhamdannaway',
          message: 'This theme is awesome!',
        },
      ],
      activityData: [
        {
          id: 1,
          icon: 'mdi-upload',
          title: 'You sold an item',
          text: 'Paul Burgess just purchased “Hyper - Admin Dashboard”!',
          subtext: '5 minutes ago',
          color: 'info',
        },
        {
          id: 2,
          icon: 'mdi-airplane',
          title: 'Product on the Bootstrap Market',
          text: 'Dave Gamache added',
          subtext: '30 minutes ago',
          boldText: 'Admin Dashboard',
          color: 'primary',
        },
        {
          id: 3,
          icon: 'mdi-microphone',
          title: 'Robert Delaney',
          text: 'Send you message',
          boldText: '"Are you there?"',
          subtext: '2 hours ago',
          color: 'info',
        },
        {
          id: 4,
          icon: 'mdi-airplane',
          title: 'Audrey Tobey',
          text: 'Uploaded a photo',
          subtext: '14 hours ago',
          boldText: '"Error.jpg"',
          color: 'primary',
        },
      ],
      transactions: [
        {
          title: 'Purchased Hyper Admin Template',
          icon: 'mdi-arrow-collapse-up',
          date: 'Today',
          amount: '-$489.30',
          color: 'danger',
        },
        {
          title: 'Payment received Bootstrap Marketplace',
          icon: 'mdi-arrow-collapse-down',
          date: 'Yesterday',
          amount: '+$1578.54',
          color: 'success',
        },
        {
          title: 'Freelance work - Shane',
          icon: 'mdi-arrow-collapse-down',
          date: '16 Sep 2018',
          amount: '+$247.5',
          color: 'success',
        },
        {
          title: 'Hire new developer for work',
          icon: 'mdi-arrow-collapse-up',
          date: '09 Sep 2018',
          amount: '-$185.14',
          color: 'danger',
        },
        {
          title: 'Money received from paypal',
          icon: 'mdi-arrow-collapse-down',
          date: '28 Aug 2018',
          amount: '+$684.45',
          color: 'success',
        },
        {
          title: 'Zairo landing purchased',
          icon: 'mdi-arrow-collapse-up',
          date: '17 Aug 2018',
          amount: '-$21.00',
          color: 'danger',
        },
        {
          title: 'Interest received',
          icon: 'mdi-arrow-collapse-down',
          date: '09 Sep 2018',
          amount: '+$784.55',
          color: 'success',
        },
      ],
      chartData: [
        {
          title: 'Sales Summary',
          number: '259',
          chartColor: '#734CEA',
          chartData: [25, 66, 41, 59, 25, 44, 12, 36, 9, 21],
          chartType: 'line',
          lastMonth:'358',
          currentMonth:'194'
        },
        {
          title: 'Revenue',
          number: '$6,254',
          chartColor: '#34bfa3',
          chartData: [12, 14, 2, 47, 32, 44, 14, 55, 41, 69],
          chartType: 'bar',
          lastMonth:'$781.12',
          currentMonth:'$128.2'
        },
        {
          title: 'Active Users',
          number: '324',
          chartColor: '#f4516c',
          chartData: [47, 45, 74, 32, 56, 31, 44, 33, 45, 19],
          chartType: 'line',
          lastMonth:'+15%',
          currentMonth:'-6.87%'
        },
        {
          title: 'Expense Summary',
          number: '$4,745.2',
          chartColor: '#00c5dc',
          chartData: [15, 75, 47, 65, 14, 32, 19, 54, 44, 61],
          chartType: 'bar',
          lastMonth:'$7814',
          currentMonth:'$4782.8'
        },
      ],
      chatWindowHeight: '316px',
      todoWindowHeight: '298px',
      activityWindowHeight: '325px',
      transactionWindowHeight:'325px',
      textColor: 'black',
    }
  },
}
</script>