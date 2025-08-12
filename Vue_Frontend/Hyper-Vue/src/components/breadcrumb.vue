<template>
  <!-- start page title -->
  <b-row>
    <b-col cols="12">
      <div class="page-title-box">
        <div class="page-title-right" id="title-right">
          <b-breadcrumb
              :items="items"
              class="m-0"
          ></b-breadcrumb>
        </div>
        <h4 class="page-title">{{ title }}</h4>
      </div>
    </b-col>
  </b-row>
  <!-- end page title -->
</template>

<script lang="ts">
export default {
  components: {},
  props: {
    title: {
      type: String,
      default: '',
    },
    items: {
      type: Array,
      default: () => {
        return []
      },
    },
  },
  mounted() {
    this.useMeta({
      title: this.title,
    });
  }
}
</script>

<style>
#title-right ol{
  padding-bottom: 0 !important;
}
</style>
