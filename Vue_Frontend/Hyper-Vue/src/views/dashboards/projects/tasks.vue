<template>
  <div class="card">
    <div class="card-header d-flex justify-content-between align-items-center">
      <h4 class="header-title">Tasks</h4>
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
    <div class="card-header bg-light-lighten border-top border-bottom border-light py-1 text-center">
      <p class="m-0"><b>107</b> Tasks completed out of 195</p>
    </div>

    <div class="card-body pt-2">
      <div class="table-responsive mb-0">
        <table class="table table-centered table-nowrap table-hover mb-0">
          <tbody>
          <tr v-for="task of tasksData" :key="task.name">
            <td>
              <h5 class="font-14 my-1">
                <a href="javascript:void(0);" class="text-body">{{ task.name }}</a>
              </h5>
              <span class="text-muted font-13">Due in {{ task.day }} days</span>
            </td>
            <td>
              <span class="text-muted font-13">Status</span>
              <br/>
              <span
                  class="badge"
                  :class=" { 'badge-success-lighten': `${task.status}` === 'Completed',
                  'badge-danger-lighten': `${task.status}` === 'Outdated',
                  'badge-warning-lighten': `${task.status}` === 'In-progress' } "
              >{{ task.status }}</span>
            </td>
            <td>
              <span class="text-muted font-13">Assigned to</span>
              <h5 class="font-14 mt-1 font-weight-normal">{{ task.assigned }}</h5>
            </td>
            <td>
              <span class="text-muted font-13">Total time spend</span>
              <h5 class="font-14 mt-1 font-weight-normal">{{ task.time }}</h5>
            </td>
            <td class="table-action" style="width: 90px;">
              <a href="javascript: void(0);" class="action-icon">
                <i class="mdi mdi-pencil"></i>
              </a>
              <a href="javascript: void(0);" class="action-icon">
                <i class="mdi mdi-delete"></i>
              </a>
            </td>
          </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
export default {
  data() {
    return {
      tasksData: [
        {
          name: 'Coffee detail page - Main Page',
          day: 3,
          status: 'In-progress',
          assigned: 'Logan R. Cohn',
          time: '3h 20min',
        },
        {
          name: 'Drinking bottle graphics',
          day: 27,
          status: 'Outdated',
          assigned: 'Jerry F. Powell',
          time: '12h 21min',
        },
        {
          name: 'App design and development',
          day: 7,
          status: 'Completed',
          assigned: 'Scot M. Smith',
          time: '78h 05min',
        },
        {
          name: 'Poster illustation design',
          day: 5,
          status: 'In-progress',
          assigned: 'John P. Ritter',
          time: '26h 58min',
        },
      ],
    }
  },
}
</script>