<template>
  <b-col sm="6" xl="3" v-for="(item,index) in statData" :key="index" class="mb-3">
    <div class="card mb-0 h-100">
      <div class="card-body">

        <b-dropdown class="card-drop float-end" variant="white" toggle-tag="a" toggle-class="arrow-none p-0">
          <template v-slot:button-content>
            <i class="mdi mdi-dots-horizontal"></i>
          </template>
          <b-dropdown-item href="javascript: void(0);"><i class="mdi mdi-plus-circle me-1"></i> Add Card
          </b-dropdown-item>
          <b-dropdown-item href="javascript: void(0);"><i class="mdi mdi-content-copy me-1"></i> Copy List
          </b-dropdown-item>
          <b-dropdown-item href="javascript: void(0);"><i class="mdi mdi-square-edit-outline me-1"></i> Edit
          </b-dropdown-item>
          <b-dropdown-divider/>
          <b-dropdown-item href="javascript: void(0);" class="text-danger"><i
              class="mdi mdi-trash-can-outline me-1"></i> Detele
          </b-dropdown-item>
        </b-dropdown>

        <h4 class="header-title">{{ item.title }}</h4>
        <h5 class="text-muted fw-normal mt-0 text-truncate" :title="item.title">{{ item.subtxt }}</h5>

        <div class="d-flex align-items-center mt-4">
          <div class="flex-shrink-0">
            <h5 class="font-13 text-muted my-0"><i class="mdi mdi-clock-outline"></i> {{ item.time }} ago</h5>
          </div>
          <div class="flex-grow-1 ms-2"></div>
          <div class="text-end multi-user">
            <a v-for="img in item.assignees" href="javascript:void(0);" class="d-inline-block">
              <img :src="img" class="rounded-circle avatar-xs" alt="friend">
            </a>
          </div>
        </div>
      </div> <!-- end card-body -->
    </div> <!-- end card -->
  </b-col> <!-- end col -->
</template>

<script lang="ts">
import avatar1 from '@/assets/images/users/avatar-1.jpg'
import avatar2 from '@/assets/images/users/avatar-2.jpg'
import avatar4 from '@/assets/images/users/avatar-4.jpg'
import avatar5 from '@/assets/images/users/avatar-5.jpg'
import avatar6 from '@/assets/images/users/avatar-6.jpg'
import avatar7 from '@/assets/images/users/avatar-7.jpg'

export default {
  data() {
    return {
      statData: [
        {
          title: 'PROJECT DASHBOARD',
          subtxt: 'New Task Assign',
          time: '4 Hrs',
          assignees: [avatar1, avatar2]
        },
        {
          title: 'ADMIN TEMPLATE',
          subtxt: 'New Task Assign',
          time: '7 Hrs',
          assignees: [avatar4, avatar5]
        },
        {
          title: 'CLIENT PROJECT',
          subtxt: 'New Task Assign',
          time: '1 Day',
          assignees: [avatar6, avatar7]
        },
      ]
    }
  }
}
</script>
