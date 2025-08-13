<template>
  <Layout>
    <Breadcrumb :title="title" :items="items"/>

    <b-row>
      <b-col cols="12">
        <div class="card">
          <div class="card-body">
            <h4 class="header-title mb-4">New Icons <span class="badge badge-danger-lighten">6.5.95</span></h4>
            <b-row class="icons-list-demo" id="newIcons">
              <b-col xl="3" lg="4" sm="6" v-for="(icon,index) in newIcons" :key="index">
                <i :class="`mdi mdi-${icon.name}`"></i> mdi-{{ icon.name }}
              </b-col>
            </b-row>
          </div>
        </div>
        <div class="card">
          <div class="card-body">
            <h4 class="header-title mb-4">All Icons</h4>
            <b-row class="icons-list-demo" id="icons">
              <b-col xl="3" lg="4" sm="6" v-for="(icon,index) in materialDesignIcons" :key="index">
                <i :class="`mdi mdi-${icon.name}`"></i> mdi-{{ icon.name }}
              </b-col>
            </b-row>
          </div> <!-- end card-body -->
        </div> <!-- end card -->
      </b-col>
    </b-row>

    <b-row>
      <b-col cols="12">
        <div class="card">

          <div class="card-body">
            <h4 class="header-title mb-4">Size</h4>

            <b-row class="icons-list-demo">
              <b-col xl="3" lg="4" sm="6">
                <i class="mdi mdi-18px mdi-account"></i> mdi-18px
              </b-col>

              <b-col xl="3" lg="4" sm="6">
                <i class="mdi mdi-24px mdi-account"></i> mdi-24px
              </b-col>

              <b-col xl="3" lg="4" sm="6">
                <i class="mdi mdi-36px mdi-account"></i> mdi-36px
              </b-col>

              <b-col xl="3" lg="4" sm="6">
                <i class="mdi mdi-48px mdi-account"></i> mdi-48px
              </b-col>
            </b-row>
          </div>
        </div>
      </b-col>
    </b-row>
    <!-- end row -->

    <b-row>
      <b-col cols="12">
        <div class="card">

          <div class="card-body">
            <h4 class="header-title mb-4">Rotate</h4>

            <b-row class="icons-list-demo">
              <b-col xl="3" lg="4" sm="6">
                <i class="mdi mdi-rotate-45 mdi-account"></i> mdi-rotate-45
              </b-col>
              <b-col xl="3" lg="4" sm="6">
                <i class="mdi mdi-rotate-90 mdi-account"></i> mdi-rotate-90
              </b-col>
              <b-col xl="3" lg="4" sm="6">
                <i class="mdi mdi-rotate-135 mdi-account"></i> mdi-rotate-135
              </b-col>
              <b-col xl="3" lg="4" sm="6">
                <i class="mdi mdi-rotate-180 mdi-account"></i> mdi-rotate-180
              </b-col>
              <b-col xl="3" lg="4" sm="6">
                <i class="mdi mdi-rotate-225 mdi-account"></i> mdi-rotate-225
              </b-col>
              <b-col xl="3" lg="4" sm="6">
                <i class="mdi mdi-rotate-270 mdi-account"></i> mdi-rotate-270
              </b-col>
              <b-col xl="3" lg="4" sm="6">
                <i class="mdi mdi-rotate-315 mdi-account"></i> mdi-rotate-315
              </b-col>
            </b-row>
          </div>
        </div>
      </b-col>
    </b-row>
    <!-- end row -->

    <b-row>
      <b-col cols="12">
        <div class="card">

          <div class="card-body">
            <h4 class="header-title mb-4">Spin</h4>

            <b-row class="icons-list-demo">
              <b-col xl="3" lg="4" sm="6">
                <i class="mdi mdi-spin mdi-loading"></i> mdi-spin
              </b-col>
              <b-col xl="3" lg="4" sm="6">
                <i class="mdi mdi-spin mdi-star"></i> mdi-spin
              </b-col>
            </b-row>
          </div>
        </div>
      </b-col>
    </b-row>
    <!-- end row -->

  </Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";

import {materialDesignIcons} from "@/views/icons/data";

export default {
  components: {Breadcrumb, Layout},
  data() {
    let newIcons:{name:string,hex:string,version:string}[] = []
    let deprecatedIcons:{name:string,hex:string,version:string,deprecated:string}[] = []
    return {
      title: 'Mdi Icons',
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
          text: 'Mdi Icons',
          active: true,
        },
      ],
      materialDesignIcons,
      newIcons,
      deprecatedIcons
    }
  },
  mounted() {
    this.getNewIcons()
  },
  methods: {
    isNew(icon:{name:string,hex:string,version:string}) {
      return icon.version === '6.5.95';
    },
    // isDeprecated(icon:{name:string,hex:string,version:string,deprecated:string}) {
    //   return typeof icon.deprecated == 'undefined'
    //       ? false
    //       : icon.deprecated;
    // },
    getNewIcons() {
      for (let i in this.materialDesignIcons) {
        if (this.isNew(materialDesignIcons[i])) {
          this.newIcons.push(materialDesignIcons[i])
        }

        // if (this.isDeprecated(materialDesignIcons[i])) {
        //   this.deprecatedIcons.push(materialDesignIcons[i])
        // }
      }
    }
  }

}
</script>

