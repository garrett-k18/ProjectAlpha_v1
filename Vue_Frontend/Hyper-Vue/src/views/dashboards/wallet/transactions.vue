<template>
  <div class="card">
    <div class="card-header d-flex justify-content-between align-items-center">
      <h4 class="header-title mb-0">Transaction List</h4>
      <div>
        <select class="form-select form-select-sm" aria-label=".form-select-sm example">
          <option selected>Today</option>
          <option value="1">Yesterday</option>
          <option value="2">Tomorrow</option>
        </select>
      </div>
    </div>

    <div class="card-body pt-0">
      <div class="table-responsive mb-0">
        <table class="table table-centered table-nowrap table-hover mb-0">
          <thead>
          <tr>
            <th scope="col">Name</th>
            <th scope="col">Date</th>
            <th scope="col">Status</th>
            <th scope="col">Amount</th>
            <th scope="col" class="text-end">Action</th>
          </tr>
          </thead>
          <tbody>

          <tr v-for="(record,index) in transactionList">
            <td>
              <div class="d-flex align-items-center">
                <div class="flex-shrink-0">
                  <img class="rounded-circle" :src="record.img" alt="Avtar image"
                       width="33">
                </div>
                <div class="flex-grow-1 ms-2">
                  {{ record.name }}
                </div>
              </div>
            </td>
            <td><i class="uil uil-calender me-1"></i>{{ record.date }}</td>
            <td>
              <span class="badge" :class="record.status == 'Incoming' ? 'bg-success-lighten text-success' :'' || record.status == 'Outgoing' ? 'bg-danger-lighten text-danger' :'' || record.status == 'In Progress' ? 'bg-warning-lighten text-warning' :''">{{ record.status }}</span>
            </td>
            <td>
              <span class="fw-semibold" :class="record.status == 'Incoming' ? 'text-success ' :'' || record.status == 'Outgoing' ? 'text-danger' :'' || record.status == 'In Progress' ? 'text-warning' :''">{{ record.amount }}</span>
            </td>
            <td class="text-end">
              <a href="javascript:void(0);" class="font-18 text-info me-2" data-bs-toggle="tooltip"
                 data-bs-placement="top" title="Edit"><i class="uil uil-pen"></i></a>
              <a href="javascript:void(0);" class="font-18 text-danger" data-bs-toggle="tooltip"
                 data-bs-placement="top" title="Delete"><i class="uil uil-trash"></i></a>
            </td>
          </tr>

          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import avatar1 from "@/assets/images/users/avatar-1.jpg"
import avatar2 from "@/assets/images/users/avatar-2.jpg"
import avatar3 from "@/assets/images/users/avatar-3.jpg"
import avatar4 from "@/assets/images/users/avatar-4.jpg"
import avatar5 from "@/assets/images/users/avatar-5.jpg"

export default {
  data() {
    return {
      transactionList: [
        {
          img: avatar1,
          name: 'Adam Baldwin',
          date: 'Jan 01, 2022',
          status: 'Incoming',
          amount: '+ $2,586.60',
        },
        {
          img: avatar2,
          name: 'Peter Wallace',
          date: 'Jan 18, 2022',
          status: 'Outgoing',
          amount: '- $1,250.48',
        },
        {
          img: avatar3,
          name: 'Jacob Dunn',
          date: 'Feb 05, 2022',
          status: 'Incoming',
          amount: '+ $18,400.00',
        },
        {
          img: avatar4,
          name: 'Terry Adams',
          date: 'Feb 13, 2022',
          status: 'In Progress',
          amount: '+ $9,646.20',
        },
        {
          img: avatar5,
          name: 'Jason Stovall',
          date: 'Mar 02, 2022',
          status: 'Outgoing',
          amount: '+ $10,285.80',
        },
      ]
    }
  }
}
</script>