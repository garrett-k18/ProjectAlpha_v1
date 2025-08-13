<template>
  <div :id="id">
    <slot/>
  </div>
</template>

<script lang="ts">
import 'jstree'

export default {
  props: {id: {type: String}, option: {type: Object}},
  mounted() {
    $(`#${this.id}`).jstree(this.option);
  }
}
</script>
