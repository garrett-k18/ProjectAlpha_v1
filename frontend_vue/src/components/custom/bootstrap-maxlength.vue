<template>
  <b-form-input type="text" data-toggle="maxlength"/>
</template>

<script lang="ts">
import "bootstrap-maxlength/dist/bootstrap-maxlength.min.js";

export default {
  mounted() {
    $('[data-toggle="maxlength"]').each(function (idx, obj) {
      var objOptions = $.extend({}, {}, $(obj).data());
      $(obj).maxlength(objOptions);
    });
  },
};
</script>
