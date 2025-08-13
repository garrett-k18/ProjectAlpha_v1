<template>
  <div :id="id" class="rateit"></div>
</template>

<script lang="ts">
import "jquery.rateit";

export default {
  props: {id: {type: String}}
}
</script>
