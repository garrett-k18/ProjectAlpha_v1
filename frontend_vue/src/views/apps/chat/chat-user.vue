

<template>
  <div class="card">
    <div class="card-body p-0">
      <b-tabs fill nav-class="nav-tabs nav-bordered" content-class="p-3 pb-0">
        <b-tab title="All">
          <!-- start search box -->
          <div class="app-search">
            <form>
              <div class="mb-2 w-100 position-relative">
                <input type="search" class="form-control" placeholder="People, groups & messages..."/>
                <span class="mdi mdi-magnify search-icon"></span>
              </div>
            </form>
          </div>
          <!-- end search box -->
          <b-row>
            <b-col>
          <simplebar class="card-body p-0 mb-3" style="max-height: 545px">
            <a
                v-for="chat of chatData"
                :key="chat.name"
                href="javascript:void(0);"
                class="text-body"
            >
              <div class="d-flex align-items-start mt-1 p-2">
                <img
                    :src="`${chat.image}`"
                    class="me-2 rounded-circle"
                    height="48"
                    alt=""
                />
                <div class="w-100 overflow-hidden">
                  <h5 class="mt-0 mb-0 font-14">
                    <span class="float-end text-muted font-12">{{ chat.time }}</span>
                    {{ chat.name }}
                  </h5>
                  <p class="mt-1 mb-0 text-muted font-14">
                    <span class="w-25 float-end text-end">
                      <span class="badge badge-danger-lighten">{{ chat.text }}</span>
                    </span>
                    <span class="w-75">{{ chat.message }}</span>
                  </p>
                </div>
              </div>
            </a>
          </simplebar>
            </b-col>
          </b-row>
        </b-tab>
        <b-tab title="Favourites">
          <!-- start search box -->
          <div class="app-search">
            <form>
              <div class="mb-2 w-100 position-relative">
                <input type="search" class="form-control" placeholder="People, groups & messages..."/>
                <span class="mdi mdi-magnify search-icon"></span>
              </div>
            </form>
          </div>
          <!-- end search box -->
          <b-row>
            <b-col>
              <simplebar class="card-body p-0 mb-3" style="max-height: 545px">
                <a
                    v-for="chat of chatData"
                    :key="chat.name"
                    href="javascript:void(0);"
                    class="text-body"
                >
                  <div class="d-flex align-items-start mt-1 p-2">
                    <img
                        :src="`${chat.image}`"
                        class="me-2 rounded-circle"
                        height="48"
                        alt=""
                    />
                    <div class="w-100 overflow-hidden">
                      <h5 class="mt-0 mb-0 font-14">
                        <span class="float-end text-muted font-12">{{ chat.time }}</span>
                        {{ chat.name }}
                      </h5>
                      <p class="mt-1 mb-0 text-muted font-14">
                    <span class="w-25 float-end text-end">
                      <span class="badge badge-danger-lighten">{{ chat.text }}</span>
                    </span>
                        <span class="w-75">{{ chat.message }}</span>
                      </p>
                    </div>
                  </div>
                </a>
              </simplebar>
            </b-col>
          </b-row>
        </b-tab>
        <b-tab title="Friends">
          <!-- start search box -->
          <div class="app-search">
            <form>
              <div class="mb-2 w-100 position-relative">
                <input type="search" class="form-control" placeholder="People, groups & messages..."/>
                <span class="mdi mdi-magnify search-icon"></span>
              </div>
            </form>
          </div>
          <!-- end search box -->
          <b-row>
            <b-col>
              <simplebar class="card-body p-0 mb-3" style="max-height: 545px">
                <a
                    v-for="chat of chatData"
                    :key="chat.name"
                    href="javascript:void(0);"
                    class="text-body"
                >
                  <div class="d-flex align-items-start mt-1 p-2">
                    <img
                        :src="`${chat.image}`"
                        class="me-2 rounded-circle"
                        height="48"
                        alt=""
                    />
                    <div class="w-100 overflow-hidden">
                      <h5 class="mt-0 mb-0 font-14">
                        <span class="float-end text-muted font-12">{{ chat.time }}</span>
                        {{ chat.name }}
                      </h5>
                      <p class="mt-1 mb-0 text-muted font-14">
                    <span class="w-25 float-end text-end">
                      <span class="badge badge-danger-lighten">{{ chat.text }}</span>
                    </span>
                        <span class="w-75">{{ chat.message }}</span>
                      </p>
                    </div>
                  </div>
                </a>
              </simplebar>
            </b-col>
          </b-row>
        </b-tab>
      </b-tabs>
    </div>
  </div>
</template>

<script lang="ts">
import simplebar from 'simplebar-vue'

import avatar1 from '@/assets/images/users/avatar-1.jpg'
import avatar2 from '@/assets/images/users/avatar-2.jpg'
import avatar3 from '@/assets/images/users/avatar-3.jpg'
import avatar5 from '@/assets/images/users/avatar-5.jpg'
import avatar6 from '@/assets/images/users/avatar-6.jpg'
import avatar7 from '@/assets/images/users/avatar-7.jpg'
import avatar8 from '@/assets/images/users/avatar-8.jpg'
import avatar10 from '@/assets/images/users/avatar-10.jpg'

export default {
  components: {simplebar},
  data() {
    return {
      chatData: [
        {
          image: avatar2,
          name: 'Brandon Smith',
          message: 'How are you today?',
          time: '4:30am',
          text: 3,
        },
        {
          image: avatar5,
          name: 'Shreyu N',
          message: "Hey! a reminder for tomorrow's meeting...",
          time: '5:30am',
        },
        {
          image: avatar7,
          name: 'Maria C',
          message: "Are we going to have this week's planning meeting today?",
          time: 'Thu',
          text: 2,
        },
        {
          image: avatar10,
          name: 'Rhonda D',
          message: 'Please check these design assets...',
          time: 'Wed',
        },
        {
          image: avatar3,
          name: 'Michael H',
          message:
              'Are you free for 15 min? I would like to discuss something...',
          time: 'Tue',
          text: 6,
        },
        {
          image: avatar6,
          name: 'Thomas R',
          message: "Let's have meeting today between me, you and Tony...",
          time: 'Tue',
        },
        {
          image: avatar8,
          name: 'Thomas J',
          message: 'Howdy?',
          time: 'Tue',
        },
        {
          image: avatar1,
          name: 'Ricky J',
          message: 'Are you interested in learning?',
          time: 'Tue',
          text: 28,
        },
      ],
    }
  },
}
</script>