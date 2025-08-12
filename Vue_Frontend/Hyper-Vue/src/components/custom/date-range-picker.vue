<template>
  <b-form-input :id="id!" type="text" class="date"/>
</template>
<script lang="ts">

import 'daterangepicker/moment.min.js';
import 'daterangepicker/daterangepicker.js';

export default {
  props: {
    id: {type: String}
  },
  mounted() {

    $(`#${this.id}`).daterangepicker({
      singleDatePicker: true
    });

    $('[data-toggle="date-picker"]').each(function (idx, obj) {
      var objOptions = $.extend({}, {}, $(obj).data());
      $(obj).daterangepicker(objOptions);
    });

    $('[data-toggle="date-picker-range"]').each(function (idx, obj) {
      var objOptions = $.extend({}, {}, $(obj).data());
      var target = objOptions["targetDisplay"];
      //rendering
      $(obj).daterangepicker(objOptions, function (start: any, end: any) {
        if (target)
          $(target).html(
              start.format("MMMM D, YYYY") + " - " + end.format("MMMM D, YYYY")
          );
      });
    });
  },
}
</script>

