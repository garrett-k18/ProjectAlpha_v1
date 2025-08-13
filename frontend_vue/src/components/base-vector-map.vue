<template>
  <div :id="id" :style="`height: ${mapHeight}px`"></div>
</template>

<script lang="ts">
import "admin-resources/jquery.vectormap/jquery-jvectormap-1.2.2.min.js";
import "admin-resources/jquery.vectormap/maps/jquery-jvectormap-world-mill-en.js";
import "admin-resources/jquery.vectormap/maps/jquery-jvectormap-us-merc-en.js";
import "admin-resources/jquery.vectormap/maps/jquery-jvectormap-in-mill-en.js";
import "admin-resources/jquery.vectormap/maps/jquery-jvectormap-au-mill-en.js";
import "admin-resources/jquery.vectormap/maps/jquery-jvectormap-uk-mill-en.js";
import "admin-resources/jquery.vectormap/maps/jquery-jvectormap-us-il-chicago-mill-en.js";
import "admin-resources/jquery.vectormap/maps/jquery-jvectormap-ca-lcc-en.js";
import "admin-resources/jquery.vectormap/maps/jquery-jvectormap-europe-mill-en.js";
import "admin-resources/jquery.vectormap/maps/jquery-jvectormap-fr-merc-en.js";
import "admin-resources/jquery.vectormap/maps/jquery-jvectormap-es-merc.js";
import "admin-resources/jquery.vectormap/maps/jquery-jvectormap-es-mill.js";

export default {
  props: {
    id: {
      type: String,
      require: true
    },
    mapHeight: {
      type: Number,
      default: 217,
    },
    options: {
      type: Object,
      require: true
    }
  },
  mounted() {
    if (this.id) {
      $(`#${this.id}`).vectorMap(this.options);
    }
  }
}
</script>