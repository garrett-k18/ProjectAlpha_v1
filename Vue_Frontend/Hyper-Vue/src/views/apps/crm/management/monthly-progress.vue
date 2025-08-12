<template>
  <div class="card">
    <div class="card-header d-flex justify-content-between align-items-center">
      <h4 class="header-title">Monthly Progress</h4>

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

    <div class="card-body pt-0">
      <div class="table-responsive mt-n2 mb-0">
        <table class="table table-centered table-hover table-nowrap mb-0">
          <thead>
          <tr>
            <th scope="col">Employees Name</th>
            <th scope="col">Eamil Address</th>
            <th scope="col">Project Name</th>
            <th scope="col">Status</th>
            <th scope="col">Action</th>
          </tr>
          </thead>
          <tbody>

          <tr v-for="(item,index) in progressData" :key="index">
            <td>
              <div class="d-flex align-items-center">
                <div class="flex-shrink-0">
                  <img class="rounded-circle" :src="item.img" alt="Avtar image" width="31">
                </div>
                <div class="flex-grow-1 ms-2">
                  {{ item.name }}
                </div>
              </div>
            </td>
            <td>{{ item.email }}</td>
            <td>{{ item.project }}</td>
            <td>
              <span class="badge"
                    :class="item.status=='In Progress'?'bg-primary-lighten text-primary':'' || item.status=='Completed'?'bg-success-lighten text-success':'' || item.status=='Pending'?'bg-warning-lighten text-warning':''">{{
                  item.status
                }}</span>
            </td>
            <td>
              <a href="javascript:void(0);" class="font-18 text-info me-2" v-b-tooltip.hover title="Edit"><i
                  class="uil uil-pen"></i></a>
              <a href="javascript:void(0);" class="font-18 text-danger" v-b-tooltip.hover title="Delete"><i
                  class="uil uil-trash"></i></a>
            </td>
          </tr> <!-- end tr -->

          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import avatar1 from '@/assets/images/users/avatar-1.jpg'
import avatar2 from '@/assets/images/users/avatar-2.jpg'
import avatar3 from '@/assets/images/users/avatar-3.jpg'
import avatar4 from '@/assets/images/users/avatar-4.jpg'
import avatar5 from '@/assets/images/users/avatar-5.jpg'

export default {
  data() {
    return {
      progressData: [
        {
          img: avatar1,
          name: 'Adam Baldwin',
          email: 'AdamNBaldwin@dayrep.com',
          project: 'Admin Dashboard',
          status: 'In Progress'
        },
        {
          img: avatar2,
          name: 'Peter Wallace',
          email: 'PeterGWallace@dayrep.com',
          project: 'Landing Page',
          status: 'Completed'
        },
        {
          img: avatar3,
          name: 'Jacob Dunn',
          email: 'JacobEDunn@dayrep.com',
          project: 'Logo Design',
          status: 'Pending'
        },
        {
          img: avatar4,
          name: 'Terry Adams',
          email: 'TerryCAdams@dayrep.com',
          project: 'Client Project',
          status: 'In Progress'
        },
        {
          img: avatar5,
          name: 'Jason Stovall',
          email: 'JasonJStovall@armyspy.com',
          project: 'Figma Work',
          status: 'Pending'
        },
      ]
    }
  }
}
</script>
