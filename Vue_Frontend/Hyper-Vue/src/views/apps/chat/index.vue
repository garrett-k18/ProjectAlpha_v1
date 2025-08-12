<template>
  <Layout>
    <Breadcrumb :title="title" :items="items"/>
    <b-row>

      <b-col xxl="3" xl="6" class="order-xl-1">
        <ChatUser/>
      </b-col>

      <b-col xxl="6" xl="12" class="order-xl-2">
        <ChatArea/>
      </b-col>

      <b-col xxl="3" xl="6" class="order-xl-1 order-xxl-2">
        <ChatProfile/>
      </b-col>

    </b-row>
  </Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";
import ChatUser from "@/views/apps/chat/chat-user.vue";
import ChatProfile from "@/views/apps/chat/chat-profile.vue";
import ChatArea from "@/views/apps/chat/chat-area.vue";

export default {
  components: {ChatArea, ChatProfile, ChatUser, Breadcrumb, Layout},
  data() {
    return {
      title: 'Chat',
      items: [
        {
          text: 'Hyper',
          href: '/',
        },
        {
          text: 'Apps',
          href: '/',
        },
        {
          text: 'Chat',
          active: true,
        },
      ],
    }
  },
}
</script>