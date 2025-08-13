<template>
  <Layout>
    <Breadcrumb :title="title" :items="items"/>
    <b-row>
      <b-col xxl="9">
        <b-row>
          <Stats/>

          <b-col sm="6" xl="3" class="mb-3">
            <div class="card mb-0 h-100">
              <div class="card-body">
                <div
                    class="border-dashed border-2 border h-100 w-100 rounded d-flex align-items-center justify-content-center">
                  <a href="javascript:void(0);" class="text-center text-muted p-2" @click="showModal = !showModal">
                    <i class="mdi mdi-plus h3 my-0"></i> <h4 class="font-16 mt-1 mb-0 d-block">Add New Project</h4>
                  </a>
                </div>
              </div> <!-- end card-body -->
            </div> <!-- end card -->
          </b-col> <!-- end col -->
        </b-row>

        <b-row>
          <b-col xl="4">
            <MonthlyTarget/>
          </b-col>
          <b-col xl="8">
            <ProjectStatistics/>
          </b-col>
        </b-row>
      </b-col>
      <b-col xxl="3">
        <ProjectSummary/>

        <div class="card">
          <div class="card-body">
            <h4 class="fw-semibold mt-0 mb-3">On Time Completed Rate <span
                class="badge bg-success-lighten text-success fw ms-sm-1"><i
                class="mdi mdi-trending-up me-1"></i>59%</span></h4>
            <h5 class="float-end mt-0">65%</h5>
            <h5 class="fw-normal mt-0 mb-2">Completed Projects</h5>

            <b-progress :max="100" height="4px">
              <b-progress-bar :value="65"/>
            </b-progress>

          </div>
        </div>
      </b-col>
    </b-row>

    <b-row>
      <b-col sm="6" xl="3" v-for="(item,index) in otherData" :key="index">
        <div class="card">
          <div class="card-body">
            <div class="d-flex align-items-center">
              <div class="flex-shrink-0 me-3">
                <div class="avatar-sm">
                  <span class="avatar-title rounded" :class="`bg-${item.color}-lighten text-${item.color}`">
                    <i class="mdi font-24" :class="item.icon"></i>
                  </span>
                </div>
              </div>
              <div class="flex-grow-1">
                <h5 class="mt-0 mb-1">{{ item.title }}</h5>
                <p class="mb-0">{{ item.number }}</p>
              </div>

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
          </div>
        </div>
      </b-col>

    </b-row>

    <b-row>
      <b-col xxl="6">
        <Overview/>
      </b-col>

      <b-col md="6" xxl="3">
        <DailyTasks/>
      </b-col>

      <b-col md="6" xxl="3">
        <TeamMembers/>
      </b-col>
    </b-row> <!-- end row -->


    <!-- Modal -->
    <b-modal
        v-model="showModal"
        title="Add New Project"
        title-class="h5"
        hide-footer
    >
      <div class="p-1 pb-2">
        <div class="mb-3">
          <label for="projectName" class="form-label">Project Name</label>
          <input type="text" class="form-control" id="projectName" placeholder="Add project name...">
        </div>
        <div class="mb-3">
          <label for="formGroupExampleInput" class="form-label">Add Task</label>
          <VueMultiselect
              v-model="taskValue"
              :options="taskOptions"
              :searchable="true"
          />


        </div>

        <div class="mb-3">
          <label for="AssignTask" class="form-label">Assign Task</label>
          <VueMultiselect
              v-model="assignTaskValue"
              :options="assignTaskOptions"
              multiple="true"
          />
        </div>

        <div>
          <label for="description" class="form-label">Description</label>
          <textarea class="form-control" id="description" rows="4"></textarea>
        </div>
      </div>
      <div class="float-end">
        <button type="button" class="btn btn-light" data-bs-dismiss="modal">Close</button>
        <button type="button" class="ms-1 btn btn-primary">Create Project</button>
      </div>
    </b-modal>

  </Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";
import Stats from "@/views/apps/crm/projects/stats.vue"
import VueMultiselect from "vue-multiselect";
import MonthlyTarget from "@/views/apps/crm/projects/monthly-target.vue";
import ProjectStatistics from "@/views/apps/crm/projects/project-statistics.vue";
import ProjectSummary from "@/views/apps/crm/projects/project-summary.vue";
import Overview from "@/views/apps/crm/projects/overview.vue";
import DailyTasks from "@/views/apps/crm/projects/daily-tasks.vue";
import TeamMembers from "@/views/apps/crm/projects/team-members.vue";

export default {
  components: {
    TeamMembers,
    DailyTasks,
    Overview, ProjectSummary, ProjectStatistics, MonthlyTarget, Stats, Breadcrumb, Layout, VueMultiselect
  },
  data() {
    return {
      title: 'Projects',
      items: [
        {
          text: 'Hyper',
          href: '/',
        },
        {
          text: 'CRM',
          href: '/',
        },
        {
          text: 'Projects',
          active: true,
        },
      ],

      showModal: false,
      taskValue: 'Add a task...',
      assignTaskValue: null,
      taskOptions: [
        'Add a task...',
        'Landing Page',
        'Admin Dashboards',
        'Admin Pages',
        'UX/UI Design',
        'Client Work',
        'Other Work'
      ],
      assignTaskOptions: [
        'Andrea',
        'Danielle',
        'John',
        'Steven',
        'Michael',
        'Sharon',
        'Timothy',
        'Frederick',
        'Henry',
      ],
      otherData: [
        {
          title: 'Active Projects',
          number: 85,
          icon: 'mdi-file-document-edit',
          color: 'primary'
        },
        {
          title: 'Total Employees',
          number: 32,
          icon: 'mdi-account-group',
          color: 'success'
        },
        {
          title: 'Project Reviews',
          number: 40,
          icon: 'mdi-account-star',
          color: 'info'
        },
        {
          title: 'New Projects',
          number: 25,
          icon: 'mdi-folder-plus',
          color: 'warning'
        },
      ]
    }
  }
}
</script>



