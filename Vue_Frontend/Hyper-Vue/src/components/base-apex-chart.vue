<template>
  <apexchart :height="height" :type="type!" :series="series!" :options="options"></apexchart>
</template>

<script lang="ts">
export default {
  props: {
    height: {
      type: Number,
      require: true
    },
    type:{
      type:String
    },
    series: {
      type: Array,
      require: true
    },
    options: {
      type: Object,
      require: true
    }
  },
}
</script>
