<template>
  <Layout>
    <Breadcrumb :title="title" :items="items" />

    <div class="card">
      <div class="card-body">
        <b-row>
          <!-- start projects-->

          <b-col xxl="3" lg="4">
            <div class="pe-xl-3">
              <h5 class="mt-0 mb-3">Projects</h5>

              <!-- start search box -->
              <div class="app-search">
                <form>
                  <div class="mb-2 position-relative w-100">
                    <input
                      type="text"
                      class="form-control"
                      placeholder="search by name..."
                      @keyup="onSearch"
                    />

                    <span class="mdi mdi-magnify search-icon"></span>
                  </div>
                </form>
              </div>

              <!-- end search box -->

              <b-row>
                <b-col>
                  <simplebar class="pe-xl-3" style="max-height: 535px">
                    <a
                      v-for="project in projects"
                      :key="project.id"
                      href="javascript:void(0);"
                      class="text-body"
                    >
                      <div class="d-flex mt-2 p-2">
                        <div class="avatar-sm d-table">
                          <span
                            :class="{
                              'bg-success-lighten text-success':
                                project.status === 'On-Track',
                              'bg-warning-lighten text-warning':
                                project.status === 'Locked',
                              'bg-danger-lighten text-danger':
                                project.status === 'Delayed',
                            }"
                            class="avatar-title rounded-circle"
                          >
                            <i :class="project.icon" class="font-24"></i>
                          </span>
                        </div>

                        <div class="ms-2">
                          <h5 class="mt-0 mb-0">
                            {{ project.name }}
                            <span
                              :class="{
                                'badge-success-lighten':
                                  project.status === 'On-Track',
                                'badge-warning-lighten':
                                  project.status === 'Locked',
                                'badge-danger-lighten':
                                  project.status === 'Delayed',
                              }"
                              class="badge ms-1"
                              >{{ project.status }}</span
                            >
                          </h5>

                          <p class="mt-1 mb-0 text-muted">
                            ID: {{ project.id }}
                          </p>
                        </div>
                      </div>
                    </a>
                  </simplebar>
                </b-col>
              </b-row>
            </div>
          </b-col>
          <!-- end projects -->

          <!-- gantt view -->
          <b-col xxl="9" lg="8" class="mt-4 mt-xl-0">
            <div class="ps-xl-3">
              <b-row>
                <b-col class="col-auto">
                  <a
                    href="javascript: void(0);"
                    class="btn btn-success btn-sm mb-2"
                    >Add New Task</a
                  >
                </b-col>
                <b-col class="text-sm-end">
                  <div
                    id="modes-filter"
                    class="btn-group btn-group-sm mb-2"
                    data-toggle="buttons"
                  >
                    <b-form-group label="">
                      <b-form-radio-group
                        id="mode-selection"
                        v-model="selectedMode"
                        :options="modes"
                        buttons
                        button-variant="primary"
                        name="radios-btn-default"
                        @change="onModeChange"
                      ></b-form-radio-group>
                    </b-form-group>
                  </div>
                </b-col>
              </b-row>
              <b-row>
                <b-col class="mt-3">
                  <div class="gantt-target"></div>
                </b-col>
              </b-row>
            </div>
          </b-col>
          <!-- end gantt view -->
        </b-row>
      </div>
    </div>
  </Layout>
</template>

<script lang="ts">
import Gantt from "frappe-gantt";
import simplebar from "simplebar-vue";

import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";


const projects = [
  {
    id: "proj101",
    name: "Lunar",
    status: "On-Track",
    icon: "uil uil-moonset",
  },
  {
    id: "proj102",
    name: "Dark Moon",
    status: "On-Track",
    icon: "uil uil-moon-eclipse",
  },
  {
    id: "proj103",
    name: "Aurora",
    status: "Locked",
    icon: "uil uil-mountains",
  },
  {
    id: "proj104",
    name: "Blue Moon",
    status: "Locked",
    icon: "uil uil-moon",
  },
  {
    id: "proj105",
    name: "Casanova",
    status: "Delayed",
    icon: "uil uil-ship",
  },
  {
    id: "proj106",
    name: "Darwin",
    status: "On-Track",
    icon: "uil uil-subway-alt",
  },
  {
    id: "proj107",
    name: "Eagle",
    status: "Delayed",
    icon: "uil uil-gold",
  },
];

export default {
  components: { simplebar, Layout, Breadcrumb },
  data() {
    return {
      title: "Gantt",
      selectedMode: "Week",
      modes: ["Quarter Day", "Half Day", "Day", "Week", "Month"],
      items: [
        {
          text: "Hyper",
          href: "/",
        },
        {
          text: "Projects",
          href: "/",
        },
        {
          text: "Gantt",
          active: true,
        },
      ],
      projects: [...projects],
      tasks: [
        {
          id: "1",
          name: "Draft the new contract document for sales team",
          start: "2019-07-16",
          end: "2019-07-20",
          progress: 55,
        },
        {
          id: "2",
          name: "Find out the old contract documents",
          start: "2019-07-19",
          end: "2019-07-21",
          progress: 85,
          dependencies: "1",
        },
        {
          id: "3",
          name: "Organize meeting with sales associates to understand need in detail",
          start: "2019-07-21",
          end: "2019-07-22",
          progress: 80,
          dependencies: "2",
        },
        {
          id: "4",
          name: "iOS App home page",
          start: "2019-07-15",
          end: "2019-07-17",
          progress: 80,
        },
        {
          id: "5",
          name: "Write a release note",
          start: "2019-07-18",
          end: "2019-07-22",
          progress: 65,
          dependencies: "4",
        },
        {
          id: "6",
          name: "Setup new sales project",
          start: "2019-07-20",
          end: "2019-07-31",
          progress: 15,
        },
        {
          id: "7",
          name: "Invite user to a project",
          start: "2019-07-25",
          end: "2019-07-26",
          progress: 99,
          dependencies: "6",
        },
        {
          id: "8",
          name: "Coordinate with business development",
          start: "2019-07-28",
          end: "2019-07-30",
          progress: 35,
          dependencies: "7",
        },
        {
          id: "9",
          name: "Kanban board design",
          start: "2019-08-01",
          end: "2019-08-03",
          progress: 25,
          dependencies: "8",
        },
        {
          id: "10",
          name: "Enable analytics tracking",
          start: "2019-08-05",
          end: "2019-08-07",
          progress: 60,
          dependencies: "9",
        },
      ],
      ganttRef: '',
    };
  },
  mounted() {
    // eslint-disable-next-line camelcase
    this.ganttRef = new Gantt(".gantt-target", this.tasks, {
      custom_popup_html: (task:any) => {
        // the task object will contain the updated
        // dates and progress value
        // eslint-disable-next-line
        var endDate = task.end;
        // eslint-disable-next-line
        var progressCls =
          task.progress >= 60
            ? "bg-success"
            : task.progress >= 30 && task.progress < 60
            ? "bg-primary"
            : "bg-warning";
        return (
          '<div class="popover fade show bs-popover-right gantt-task-details" role="tooltip">' +
          '<div class="arrow"></div><div class="popover-body">' +
          // eslint-disable-next-line no-template-curly-in-string
          `<h5>${task.name}</h5><p class="mb-2">Expected to finish by ${endDate}</p>` +
          '<div class="progress mb-2" style="height: 10px;">' +
          // eslint-disable-next-line no-template-curly-in-string
          `<div class="progress-bar ${progressCls}" role="progressbar" style="width: ${task.progress}%;" aria-valuenow="${task.progress}"` +
          // eslint-disable-next-line no-template-curly-in-string
          ` aria-valuemin="0" aria-valuemax="100">${task.progress}%</div>` +
          "</div></div></div>"
        );
      },
      view_modes: this.modes,
      view_mode: "Week",
      bar_height: 20,
      padding: 18,
    });
  },
  methods: {
    onModeChange(val:any) {
      if (this.ganttRef) this.ganttRef.change_view_mode(val);
    },
    onSearch(e:any) {
      const val = e.target.value;
      if (val) {
        this.projects = projects.filter(
          (p) => p.name.toLowerCase().indexOf(val.toLowerCase()) !== -1
        );
      } else this.projects = [...projects];
    },
  },
};
</script>
