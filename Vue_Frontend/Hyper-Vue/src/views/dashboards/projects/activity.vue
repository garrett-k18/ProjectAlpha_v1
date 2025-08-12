<template>
  <div class="card">
    <div class="card-header d-flex justify-content-between align-items-center">
      <h4 class="header-title">Recent Activities</h4>

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
      <div class="table-responsive mb-0">
        <table class="table table-centered table-nowrap table-hover mb-0">
          <tbody>
          <tr v-for="activity of activities" :key="activity.name">
            <td>
              <div class="d-flex align-items-start">
                <img
                    class="me-2 rounded-circle"
                    :src="`${activity.image}`"
                    width="40"
                    alt=""
                />
                <div>
                  <h5 class="mt-0 mb-1">
                    {{ activity.name }}
                    <small class="fw-normal ms-3">{{ activity.date }}</small>
                  </h5>
                  <span class="font-13">{{ activity.text }}</span>
                </div>
              </div>
            </td>
            <td>
              <span class="text-muted font-13">Project</span>
              <br/>
              <p class="mb-0">{{ activity.project }}</p>
            </td>
            <td class="table-action" style="width: 50px;">
              <b-dropdown toggle-class="arrow-none card-drop p-0" variant="black" right>
                <template v-slot:button-content>
                  <i class="mdi mdi-dots-horizontal"></i>
                </template>
                <b-dropdown-item href="javascript:void(0);">Settings</b-dropdown-item>
                <b-dropdown-item href="javascript:void(0);">Action</b-dropdown-item>
              </b-dropdown>
            </td>
          </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import avatar2 from '@/assets/images/users/avatar-2.jpg'
import avatar3 from '@/assets/images/users/avatar-3.jpg'
import avatar4 from '@/assets/images/users/avatar-4.jpg'
import avatar5 from '@/assets/images/users/avatar-5.jpg'
import avatar6 from '@/assets/images/users/avatar-6.jpg'

export default {
  data() {
    return {
      activities: [
        {
          image: avatar2,
          name: 'Soren Drouin',
          date: '18 Jan 2019 11:28 pm',
          text: 'Completed "Design new idea"...',
          project: 'Hyper Mockup',
        },
        {
          image: avatar6,
          name: 'Anne Simard',
          date: '18 Jan 2019 11:09 pm',
          text: 'Assigned task "Poster illustation design"...',
          project: 'Hyper Mockup',
        },
        {
          image: avatar3,
          name: 'Nicolas Chartier',
          date: '15 Jan 2019 09:29 pm',
          text: 'Completed "Drinking bottle graphics"...',
          project: 'Web UI Design',
        },
        {
          image: avatar4,
          name: 'Gano Cloutier',
          date: '10 Jan 2019 08:36 pm',
          text: 'Completed "Design new idea"...',
          project: 'UBold Admin',
        },
        {
          image: avatar5,
          name: 'Francis Achin',
          date: '08 Jan 2019 12:28 pm',
          text: 'Assigned task "Hyper app design"...',
          project: 'Website Mockup',
        },
      ],
    }
  },
}
</script>
