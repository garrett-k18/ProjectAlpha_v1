<template>
  <b-form-input
      :id="id"
      type="range"
      data-plugin="range-slider"
  />
</template>

<script lang="ts">
import "ion-rangeslider/js/ion.rangeSlider.min.js";

export default {
  props: {id: {type: String}},
  mounted() {
    $('[data-plugin="range-slider"]').each(function () {
      var opts = $(this).data();
      $(this).ionRangeSlider(opts);
    });
  },
}
</script>
