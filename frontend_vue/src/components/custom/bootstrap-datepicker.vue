<template>
  <b-form-input
      data-provide="datepicker"
  />
</template>

<script lang="ts">
import "bootstrap-datepicker";

export default {
  props: {id: {type: String}}
}
</script>
