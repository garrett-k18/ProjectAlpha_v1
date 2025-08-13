<template>
  <DataTable
      :id="id"
      :data="data"
      :options="options"
  >
    <thead>
    <tr>
      <th v-for="head in tHead">{{ head }}</th>
    </tr>
    </thead>

  </DataTable>
</template>

<script lang="ts">


declare global {
  interface Window {
    jQuery: any;
    $: any;
    dt: any;
  }
}

import jQuery from "jquery";

window.$ = window.jQuery = jQuery;
import dataTables from "datatables.net";

window.dt = dataTables;

import DataTable from "datatables.net-vue3";
import DataTablesCore from "datatables.net";

// import "datatables.net-responsive-bs5/css/responsive.bootstrap5.min.css"
// import "datatables.net-buttons-bs5/css/buttons.bootstrap5.min.css"
import "datatables.net-bs5/css/dataTables.bootstrap5.min.css";
import "datatables.net-bs5";

// import "datatables.net-buttons-bs5/js/buttons.bootstrap5.min.js"
// import "datatables.net-buttons/js/buttons.html5.min.js"
// import "datatables.net-buttons/js/buttons.flash.min.js"
// import "datatables.net-buttons/js/buttons.print.min.js"
// import "datatables.net-keytable/js/dataTables.keyTable.min.js"

DataTable.use(DataTablesCore);

export default {
  components: {DataTable},
  props: {
    id: {type: String, require: true},
    data: {type: Array, require: true},
    options: {type: Object, require: true},
    tHead: {type: Array}
  }
}
</script>
