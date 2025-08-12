<template>
  <div class="card">
    <div class="card-header d-flex justify-content-between align-items-center">
      <h4 class="header-title pb-2">Calendar</h4>

      <b-dropdown class="float-end" variant="white" right toggle-tag="a" toggle-class="arrow-none p-0">
        <template v-slot:button-content>
          <i class="mdi mdi-dots-vertical"></i>
        </template>
        <b-dropdown-item href="javascript: void(0);">Today</b-dropdown-item>
        <b-dropdown-item href="javascript: void(0);">Yesterday</b-dropdown-item>
        <b-dropdown-item href="javascript: void(0);">Last Week</b-dropdown-item>
        <b-dropdown-item href="javascript: void(0);">Last Month</b-dropdown-item>
      </b-dropdown>

    </div>
    <div class="card-body px-2 pb-1 pt-0 mt-n2">
      <!--Calendar-->
      <div data-provide="datepicker-inline" data-date-today-highlight="true" class="calendar-widget"></div>
    </div>
  </div>
</template>

<script lang="ts">
import "bootstrap-datepicker";

export default {}
</script>
