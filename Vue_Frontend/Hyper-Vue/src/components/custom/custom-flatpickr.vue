<template>
  <b-form-input
      type="text"
      :id="id!"
  />
</template>

<script lang="ts">
import "flatpickr";
export default {
  props: {id: {type: String}, options: {type: Object}},
  mounted() {
    $(`#${this.id}`).flatpickr(this.options);
  }
}
</script>
