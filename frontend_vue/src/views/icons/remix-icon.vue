<template>
  <Layout>
    <Breadcrumb :title="title" :items="items"/>
    <b-row>
      <b-col cols="12" id="icons">
        <div class="card" v-for="(item, value) in remixIcons">
          <div class="card-body">
            <h4 class="header-title">{{ value }}</h4>
            <p class="card-title-desc mb-2">
              Use <code>&lt;i class="ri-home-line"&gt;&lt;/i&gt;</code> or
              <code>&lt;i class="ri-home-fill"&gt;&lt;/i&gt;</code>
            </p>

            <b-row v-if="value == 'Editor'" class="icons-list-demo">
              <b-col xl="3" lg="4" sm="6" v-for="(key, value) in item">
                <i :class="'ri-' + value"></i>
                <span>ri-{{ value }}</span>
              </b-col>
            </b-row>

            <b-row v-else class="icons-list-demo">
              <b-col xl="3" lg="4" sm="6" v-for="(key, value) in item">
                <i :class="'ri-' + value + '-line'"></i>
                <span>ri-{{ value }}-line</span>
              </b-col>
              <b-col xl="3" lg="4" sm="6" v-for="(key, value) in item">
                <i :class="'ri-' + value + '-fill'"></i>
                <span>ri-{{ value }}-fill</span>
              </b-col>
            </b-row>
          </div>
        </div>
      </b-col>
    </b-row>
  </Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";
import {remixIcons} from "@/views/icons/data";

export default {
  components: {Layout, Breadcrumb},
  data() {
    return {
      title: 'Remix Icons',
      items: [
        {
          text: 'Hyper',
          href: '/',
        },
        {
          text: 'Icons',
          href: '/',
        },
        {
          text: 'Remix Icons',
          active: true,
        },
      ],
      remixIcons
    }
  }
}
</script>
