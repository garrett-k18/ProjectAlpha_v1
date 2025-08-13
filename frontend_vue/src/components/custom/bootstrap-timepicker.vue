<template>
  <b-form-input
      :id="id!"
      type="text"
      data-provide="timepicker"
  />
</template>

<script lang="ts">
import "bootstrap-timepicker/js/bootstrap-timepicker.min.js"

export default {
  props: {id: {type: String}}
}
</script>
