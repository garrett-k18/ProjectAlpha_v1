<template>
  <div :id="id" class="text-center"></div>
</template>

<script lang="ts">
import 'jquery-sparkline'

export default {
  props: {
    id: {
      type: String,
      require: true
    },
    series: {
      type: Array,
      require: true
    },
    option: {
      type: Object,
      require: true
    }
  },
  mounted() {
    $(`#${this.id}`).sparkline(this.series, this.option);
  }
}
</script>
