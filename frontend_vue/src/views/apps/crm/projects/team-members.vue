<template>
  <div class="card card-h-100">
    <div class="card-header d-flex justify-content-between align-items-center">
      <h4 class="header-title mb-0">Team Members</h4>
      <div>
        <select class="form-select form-select-sm" aria-label=".form-select-sm example">
          <option selected>Active</option>
          <option value="1">Offline</option>
        </select>
      </div>
    </div>

    <div class="card-body py-0 mb-3" data-simplebar style="max-height: 304px;">

      <div v-for="(member,index) in membersData" :key="index" class="d-flex align-items-start"
           :class="index!=0?'mt-3':''">
        <img class="me-3 rounded-circle" :src="member.img" width="40"
             alt="Generic placeholder image">
        <div class="w-100 overflow-hidden">
          <h5 class="mt-0 mb-1 fw-semibold"><a href="javascript:void(0);" class="text-reset">{{ member.name }}</a></h5>
          <ul class="list-inline mb-0 font-13">
            <li class="list-inline-item">{{ member.role }}</li>
            <li class="list-inline-item text-muted"><i class="mdi mdi-circle-small"></i></li>
            <li class="list-inline-item text-muted">{{ member.experience }} Year Experience</li>
          </ul>
        </div>
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
import avatar6 from '@/assets/images/users/avatar-6.jpg'

export default {
  data() {
    return {
      membersData: [
        {
          img: avatar2,
          name: 'Risa Pearson',
          role: 'UI/UX Designer',
          experience: 2.5
        },
        {
          img: avatar3,
          name: 'Margaret D. Evans',
          role: 'PHP Developer',
          experience: 2
        },
        {
          img: avatar4,
          name: 'Bryan J. Luellen',
          role: 'Front end Developer',
          experience: 1
        },
        {
          img: avatar5,
          name: 'Kathryn S. Collier',
          role: 'UI/UX Designer',
          experience: 3
        },
        {
          img: avatar1,
          name: 'Timothy Kauper',
          role: 'Backend Developer',
          experience: 2
        },
        {
          img: avatar6,
          name: 'Zara Raws',
          role: 'Python Developer',
          experience: 1
        },
      ]
    }
  }

}
</script>
