<template>
  <Layout>
    <Breadcrumb :items="items" :title="title"/>

    <b-row>
      <b-col sm="12">
        <!-- Profile -->
        <div class="card bg-primary">
          <div class="card-body profile-user-box">
            <b-row>
              <div class="col-sm-8">
                <Profile  :image="profileData.img" :name="profileData.name" :role="profileData.role"
                         :revenue="profileData.revenue" :orders="profileData.orders"/>
              </div>

              <b-col sm="4">
                <div class="text-center mt-sm-0 mt-3 text-sm-end">
                  <b-button variant="light">
                    <i class="mdi mdi-account-edit me-1"></i> Edit Profile
                  </b-button>
                </div>
              </b-col> <!-- end col-->
            </b-row> <!-- end row -->

          </div> <!-- end card-body/ profile-user-box-->
        </div>
        <!--end profile/ card -->
      </b-col> <!-- end col-->
    </b-row>
    <!-- end row -->

    <b-row>
      <b-col xl="4">
        <!-- Personal-Information -->
        <SellerInfo/>
        <!-- Personal-Information -->

        <!-- Toll free number box-->
        <b-card class="text-bg-info overflow-hidden">
          <div class="toll-free-box text-center">
            <h4 class="text-reset"><i class="mdi mdi-deskphone"></i> Toll Free : 1-234-567-8901</h4>
          </div>
        </b-card> <!-- end card-->
        <!-- End Toll free number box-->

        <!-- Messages-->
        <Message :messages="messages"/>

      </b-col> <!-- end col-->

      <b-col xl="8">
        <Orders/>
        <Stats/>
        <Product/>
      </b-col>
      <!-- end col -->

    </b-row>
  </Layout>
</template>

<script lang="ts">
import Layout from '@/components/layouts/layout.vue'
import Breadcrumb from '@/components/breadcrumb.vue'
import Profile from '@/components/widgets/profile.vue'
import Message from '@/components/widgets/message.vue';

import SellerInfo from '@/views/pages/profile/seller-info.vue';
import Orders from '@/views/pages/profile/orders.vue'
import Product from '@/views/pages/profile/product.vue'
import Stats from '@/views/pages/profile/stats.vue'

import avatar2 from '@/assets/images/users/avatar-2.jpg'
import avatar3 from '@/assets/images/users/avatar-3.jpg'
import avatar4 from '@/assets/images/users/avatar-4.jpg'
import avatar5 from '@/assets/images/users/avatar-5.jpg'
import avatar6 from '@/assets/images/users/avatar-6.jpg'

export default {
  components: {Layout, Breadcrumb, Profile, SellerInfo, Message, Product, Orders, Stats},
  data() {
    return {
      title: "Profile",
      items: [{
        text: 'Hyper',
        href: '/',
      },
        {
          text: 'Pages',
          href: '/',
        },
        {
          text: 'Profile',
          active: true,
        },
      ],

      profileData: {
        img: avatar2,
        name: 'Michael Franklin',
        role: 'Authorised Brand Seller',
        revenue: '25,184',
        orders: 5482
      },
      messages: [{
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
    }
  },

}
</script>
