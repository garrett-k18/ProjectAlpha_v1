<template>
  <div class="card">
    <div class="card-header d-flex justify-content-between align-items-center">
      <h4 class="header-title">Your Calendar</h4>
      <div class="float-end">
        <b-dropdown toggle-class="arrow-none card-drop p-0" variant="black" right>
          <template v-slot:button-content>
            <i class="mdi mdi-dots-vertical"></i>
          </template>
          <b-dropdown-item href="javascript:void(0);">Weekly Report</b-dropdown-item>
          <b-dropdown-item href="javascript:void(0);">Monthly Report</b-dropdown-item>
          <b-dropdown-item href="javascript:void(0);">Action</b-dropdown-item>
          <b-dropdown-item href="javascript:void(0);">Settings</b-dropdown-item>
        </b-dropdown>
      </div>
    </div>

    <div class="card-body pt-0">
      <b-row class=" calendar-widget calendar-widget-inline">
        <b-col md="7">
          <!--Calendar-->
          <div data-provide="datepicker-inline" data-date-today-highlight="true" class="calendar-widget">
          </div>
        </b-col>

        <b-col md="5">
          <ul class="list-unstyled mt-1">
            <li class="mb-4">
              <p class="text-muted mb-1 font-13">
                <i class="mdi mdi-calendar"></i> 7:30 AM - 10:00 AM
              </p>
              <h5>Meeting with BD Team</h5>
            </li>
            <li class="mb-4">
              <p class="text-muted mb-1 font-13">
                <i class="mdi mdi-calendar"></i> 10:30 AM - 11:45 AM
              </p>
              <h5>Design Review - Hyper Admin</h5>
            </li>
            <li class="mb-4">
              <p class="text-muted mb-1 font-13">
                <i class="mdi mdi-calendar"></i> 12:15 PM - 02:00 PM
              </p>
              <h5>Setup Github Repository</h5>
            </li>
            <li>
              <p class="text-muted mb-1 font-13">
                <i class="mdi mdi-calendar"></i> 5:30 PM - 07:00 PM
              </p>
              <h5>Meeting with Design Studio</h5>
            </li>
          </ul>
        </b-col>
      </b-row>
    </div>
  </div>
</template>

<script lang="ts">
import "bootstrap-datepicker";

export default {}
</script>
