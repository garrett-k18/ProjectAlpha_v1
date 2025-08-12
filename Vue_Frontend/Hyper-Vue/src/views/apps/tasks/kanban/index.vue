<template>
  <Layout>
    <!-- start page title -->
    <b-row>
      <b-col cols="12">
        <div class="page-title-box">
          <div class="page-title-right">
            <ol class="breadcrumb m-0">
              <li class="breadcrumb-item">
                <a href="javascript: void(0);">Hyper</a>
              </li>
              <li class="breadcrumb-item">
                <a href="javascript: void(0);">Tasks</a>
              </li>
              <li class="breadcrumb-item active">Kanban Board</li>
            </ol>
          </div>
          <h4 class="page-title">
            Kanban Board
            <a
                class="btn btn-success btn-sm ms-3"
                href="javascript: void(0);"
                @click="showModal = true"
            >Add New</a>
          </h4>
        </div>
      </b-col>
    </b-row>
    <!-- end page title -->

    <b-row>
      <b-col cols="12">
        <div class="board">
          <!-- Toda task -->
          <div class="tasks">
            <h5 class="mt-0 task-header">TODO (3)</h5>

            <div id="task-list-one" class="task-list-items">
              <Draggable class="list-group" group="tasks" :list="todoData">
                <!-- Task Item -->
                <div v-for="todo of todoData" :key="todo.id" class="card mb-0">
                  <div class="card-body p-3">
                    <small
                        class="float-end text-muted"
                    >{{ moment(new Date(todo.date)).format('DD-MMM-YYYY') }}</small>
                    <span
                        class="badge"
                        :class="{ 'bg-success': todo.priority === 'Low',
                    'bg-secondary': todo.priority === 'Medium',
                    'bg-danger': todo.priority === 'High' }"
                    >{{ todo.priority }}</span>

                    <h5 class="mt-2 mb-2">
                      <a href="#" class="text-body" @click="showTaskModal = !showTaskModal">{{ todo.title }}</a>
                    </h5>

                    <p class="mb-0">
                      <span class="pe-2 text-nowrap mb-2 d-inline-block">
                        <i class="mdi mdi-briefcase-outline text-muted"></i>
                        {{ todo.project }}
                      </span>
                      <span class="text-nowrap mb-2 d-inline-block">
                        <i class="mdi mdi-comment-multiple-outline text-muted"></i>
                        <b> {{ todo.comments }}</b> Comments
                      </span>
                    </p>

                    <b-dropdown
                        right
                        variant="white"
                        class="float-end"
                        toggle-class="text-muted arrow-none p-0"
                    >
                      <template v-slot:button-content>
                        <i class="mdi mdi-dots-vertical font-18"></i>
                      </template>
                      <b-dropdown-item href="javascript: void(0);">
                        <i class="mdi mdi-pencil me-1"></i>Edit
                      </b-dropdown-item>
                      <b-dropdown-item href="javascript: void(0);">
                        <i class="mdi mdi-delete me-1"></i>Delete
                      </b-dropdown-item>
                      <b-dropdown-item href="javascript: void(0);">
                        <i class="mdi mdi-plus-circle-outline me-1"></i>Add People
                      </b-dropdown-item>
                      <b-dropdown-item href="javascript: void(0);">
                        <i class="mdi mdi-exit-to-app me-1"></i>Leave
                      </b-dropdown-item>
                    </b-dropdown>

                    <p class="mb-0">
                      <img
                          :src="`${todo.image}`"
                          alt="user-img"
                          class="avatar-xs rounded-circle me-1"
                      />
                      <span class="align-middle">{{ todo.assign }}</span>
                    </p>
                  </div>
                  <!-- end card-body -->
                </div>
                <!-- Task Item End -->
              </Draggable>
            </div>
          </div>

          <!-- progress task -->
          <div class="tasks">
            <h5 class="mt-0 task-header text-uppercase">In Progress (2)</h5>

            <div id="task-list-one" class="task-list-items">
              <draggable class="list-group" group="tasks" :list="progressData">
                <!-- Task Item -->
                <div v-for="progress of progressData" :key="progress.id" class="card mb-0">
                  <div class="card-body p-3">
                    <small class="float-end text-muted">{{
                        moment(new Date(progress.date)).format('DD-MMM-YYYY')
                      }}</small>
                    <span
                        class="badge"
                        :class="{ 'text-bg-success': progress.priority === 'Low',
                    'text-bg-secondary': progress.priority === 'Medium',
                    'text-bg-danger': progress.priority === 'High' }"
                    >{{ progress.priority }}</span>

                    <h5 class="mt-2 mb-2">
                      <a href="#" class="text-body" @click="showTaskModal = !showTaskModal">{{ progress.title }}</a>
                    </h5>

                    <p class="mb-0">
                      <span class="pe-2 text-nowrap mb-2 d-inline-block">
                        <i class="mdi mdi-briefcase-outline text-muted"></i>
                        {{ progress.project }}
                      </span>
                      <span class="text-nowrap mb-2 d-inline-block">
                        <i class="mdi mdi-comment-multiple-outline text-muted"></i>
                        <b> {{ progress.comments }}</b> Comments
                      </span>
                    </p>

                    <b-dropdown
                        right
                        variant="white"
                        class="float-end"
                        toggle-class="text-muted arrow-none p-0"
                    >
                      <template v-slot:button-content>
                        <i class="mdi mdi-dots-vertical font-18"></i>
                      </template>
                      <b-dropdown-item href="javascript: void(0);">
                        <i class="mdi mdi-pencil me-1"></i>Edit
                      </b-dropdown-item>
                      <b-dropdown-item href="javascript: void(0);">
                        <i class="mdi mdi-delete me-1"></i>Delete
                      </b-dropdown-item>
                      <b-dropdown-item href="javascript: void(0);">
                        <i class="mdi mdi-plus-circle-outline me-1"></i>Add People
                      </b-dropdown-item>
                      <b-dropdown-item href="javascript: void(0);">
                        <i class="mdi mdi-exit-to-app me-1"></i>Leave
                      </b-dropdown-item>
                    </b-dropdown>

                    <p class="mb-0">
                      <img
                          :src="`${progress.image}`"
                          alt="user-img"
                          class="avatar-xs rounded-circle me-1"
                      />
                      <span class="align-middle">{{ progress.assign }}</span>
                    </p>
                  </div>
                  <!-- end card-body -->
                </div>
                <!-- Task Item End -->
              </draggable>
            </div>
          </div>

          <!-- Review task -->
          <div class="tasks">
            <h5 class="mt-0 task-header text-uppercase">Review (4)</h5>

            <div id="task-list-one" class="task-list-items">
              <draggable class="list-group" group="tasks" :list="reviewData">
                <!-- Task Item -->
                <div v-for="review of reviewData" :key="review.id" class="card mb-0">
                  <div class="card-body p-3">
                    <small class="float-end text-muted">{{
                        moment(new Date(review.date)).format('DD-MMM-YYYY')
                      }}</small>
                    <span
                        class="badge"
                        :class="{ 'bg-danger': review.priority === 'High',
                    'bg-secondary': review.priority === 'Medium',
                    'bg-success': review.priority === 'Low' }"
                    >{{ review.priority }}</span>

                    <h5 class="mt-2 mb-2">
                      <a href="#" class="text-body" @click="showTaskModal = !showTaskModal">{{ review.title }}</a>
                    </h5>

                    <p class="mb-0">
                      <span class="pe-2 text-nowrap mb-2 d-inline-block">
                        <i class="mdi mdi-briefcase-outline text-muted"></i>
                        {{ review.project }}
                      </span>
                      <span class="text-nowrap mb-2 d-inline-block">
                        <i class="mdi mdi-comment-multiple-outline text-muted"></i>
                        <b> {{ review.comments }}</b> Comments
                      </span>
                    </p>

                    <b-dropdown
                        right
                        variant="white"
                        class="float-end"
                        toggle-class="text-muted arrow-none p-0"
                    >
                      <template v-slot:button-content>
                        <i class="mdi mdi-dots-vertical font-18"></i>
                      </template>
                      <b-dropdown-item href="javascript: void(0);">
                        <i class="mdi mdi-pencil me-1"></i>Edit
                      </b-dropdown-item>
                      <b-dropdown-item href="javascript: void(0);">
                        <i class="mdi mdi-delete me-1"></i>Delete
                      </b-dropdown-item>
                      <b-dropdown-item href="javascript: void(0);">
                        <i class="mdi mdi-plus-circle-outline me-1"></i>Add People
                      </b-dropdown-item>
                      <b-dropdown-item href="javascript: void(0);">
                        <i class="mdi mdi-exit-to-app me-1"></i>Leave
                      </b-dropdown-item>
                    </b-dropdown>

                    <p class="mb-0">
                      <img
                          :src="`${review.image}`"
                          alt="user-img"
                          class="avatar-xs rounded-circle me-1"
                      />
                      <span class="align-middle">{{ review.assign }}</span>
                    </p>
                  </div>
                  <!-- end card-body -->
                </div>
                <!-- Task Item End -->
              </draggable>
            </div>
          </div>

          <!-- Done task -->
          <div class="tasks">
            <h5 class="mt-0 task-header text-uppercase">Done (1)</h5>

            <div id="task-list-one" class="task-list-items">
              <draggable class="list-group" group="tasks" :list="doneData">
                <!-- Task Item -->
                <div v-for="donetask of doneData" :key="donetask.id" class="card mb-0">
                  <div class="card-body p-3">
                    <small class="float-end text-muted">{{
                        moment(new Date(donetask.date)).format('DD-MMM-YYYY')
                      }}</small>
                    <span
                        class="badge"
                        :class="{ 'bg-danger': donetask.priority === 'High',
                    'bg-secondary': donetask.priority === 'Medium',
                    'bg-success': donetask.priority === 'Low' }"
                    >{{ donetask.priority }}</span>

                    <h5 class="mt-2 mb-2">
                      <a href="#" class="text-body" @click="showTaskModal = !showTaskModal">{{ donetask.title }}</a>
                    </h5>

                    <p class="mb-0">
                      <span class="pe-2 text-nowrap mb-2 d-inline-block">
                        <i class="mdi mdi-briefcase-outline text-muted"></i>
                        {{ donetask.project }}
                      </span>
                      <span class="text-nowrap mb-2 d-inline-block">
                        <i class="mdi mdi-comment-multiple-outline text-muted"></i>
                        <b> {{ donetask.comments }}</b> Comments
                      </span>
                    </p>

                    <b-dropdown
                        right
                        variant="white"
                        class="float-end"
                        toggle-class="text-muted arrow-none p-0"
                    >
                      <template v-slot:button-content>
                        <i class="mdi mdi-dots-vertical font-18"></i>
                      </template>
                      <b-dropdown-item href="javascript: void(0);">
                        <i class="mdi mdi-pencil me-1"></i>Edit
                      </b-dropdown-item>
                      <b-dropdown-item href="javascript: void(0);">
                        <i class="mdi mdi-delete me-1"></i>Delete
                      </b-dropdown-item>
                      <b-dropdown-item href="javascript: void(0);">
                        <i class="mdi mdi-plus-circle-outline me-1"></i>Add People
                      </b-dropdown-item>
                      <b-dropdown-item href="javascript: void(0);">
                        <i class="mdi mdi-exit-to-app me-1"></i>Leave
                      </b-dropdown-item>
                    </b-dropdown>

                    <p class="mb-0">
                      <img
                          :src="`${donetask.image}`"
                          alt="user-img"
                          class="avatar-xs rounded-circle me-1"
                      />
                      <span class="align-middle">{{ donetask.assign }}</span>
                    </p>
                  </div>
                  <!-- end card-body -->
                </div>
                <!-- Task Item End -->
              </draggable>
            </div>
          </div>
        </div>
      </b-col>
      <!-- end col -->
    </b-row>
    <!-- end row -->

    <!-- New task add modal -->
    <b-modal
        id="modal-1"
        v-model="showModal"
        centered
        size="lg"
        class="task-modal-content"
        title="Create New Task"
        title-tag="h4"
        title-class="modal-title"
        hide-footer
    >
      <b-form class="p-2" @submit.prevent="taskformsubmit">
        <div class="mb-3">
          <label class="form-label">Project</label>
          <select
              v-model="form.project"
              class="form-select form-control-light"
          >
            <option>Select</option>
            <option>Hyper</option>
            <option>CRM</option>
            <option>iOS</option>
          </select>
        </div>

        <b-row>
          <b-col md="8">
            <div class="mb-3">
              <label for="task-title" class="form-label">Title</label>
              <input
                  id="task-title"
                  v-model="form.title"
                  type="text"
                  class="form-control form-control-light"
                  placeholder="Enter title"

              />
            </div>
          </b-col>

          <b-col md="4">
            <div class="mb-3">
              <label for="task-priority2" class="form-label">Priority</label>
              <select
                  id="task-priority2"
                  v-model="form.priority"
                  class="form-select form-control-light"
              >
                <option>Low</option>
                <option>Medium</option>
                <option>High</option>
              </select>
            </div>
          </b-col>
        </b-row>

        <div class="mb-3">
          <label for="task-description" class="form-label">Description</label>
          <textarea id="task-description" class="form-control form-control-light" rows="3"></textarea>
        </div>

        <b-row>
          <b-col md="6">
            <div class="mb-3">
              <label for="task-title" class="form-label">Assign To</label>
              <select
                  id="task-priority"
                  v-model="form.assign"
                  class="form-select form-control-light"

              >
                <option>Coderthemes</option>
                <option>Robert Carlile</option>
                <option>Louis Allen</option>
                <option>Sean White</option>
                <option>Riley Steele</option>
                <option>Zak Turnbull</option>
              </select>
            </div>
          </b-col>

          <b-col md="6">
            <div class="mb-3">
              <label for="task-priority" class="form-label">Due Date</label>
              <DatePicker
                  v-model="form.date"
                  :first-day-of-week="1"
                  lang="en"
                  confirm
                  class="form-control form-control-light"
              ></DatePicker>
            </div>
          </b-col>
        </b-row>

        <div class="text-end">
          <b-button variant="light" @click="hideModal">Cancel</b-button>
          <b-button type="submit" variant="primary" class="ml-1">Create</b-button>
        </div>
      </b-form>
    </b-modal>
    <!-- end Modal  -->


    <!--  Task details modal -->
    <b-modal class="task-modal-content"
             v-model="showTaskModal"
             modal-class=""
             centered
             body-class="p-0"
             size="lg"
             hide-header
             hide-footer
    >
      <div class="modal-header">
        <h4 class="modal-title" id="TaskDetailModalLabel">iOS App home page <span
            class="badge bg-danger ms-2">High</span></h4>
        <button type="button" class="btn-close" @click="showTaskModal= !showTaskModal"></button>
      </div>


      <div class="modal-body">

        <div class="p-2">
          <h5 class="mt-0">Description:</h5>

          <p class="text-muted mb-4">
            Voluptates, illo, iste itaque voluptas corrupti ratione reprehenderit magni similique? Tempore, quos
            delectus asperiores
            libero voluptas quod perferendis! Voluptate, quod illo rerum? Lorem ipsum dolor sit amet. With supporting
            text below
            as a natural lead-in to additional contenposuere erat a ante.
          </p>

          <b-row>
            <b-col md="4">
              <div class="mb-4">
                <h5>Create Date</h5>
                <p>17 March 2018 <small class="text-muted">1:00 PM</small></p>
              </div>
            </b-col>
            <b-col md="4">
              <div class="mb-4">
                <h5>Due Date</h5>
                <p>22 December 2018 <small class="text-muted">1:00 PM</small></p>
              </div>
            </b-col>
            <b-col md="4">
              <div class="mb-4" id="tooltip-container">
                <h5>Asignee:</h5>
                <a href="javascript:void(0);" data-bs-container="#tooltip-container" data-bs-toggle="tooltip"
                   data-bs-placement="top" title="Mat Helme" class="d-inline-block">
                  <img src="@/assets/images/users/avatar-6.jpg" class="rounded-circle avatar-xs" alt="friend">
                </a>
              </div>
            </b-col>
          </b-row>
          <!-- end row-->

          <b-tabs content-class="mt-3">
            <b-tab title="Comments" active class="nav-link" id="home-b1">
   <textarea class="form-control form-control-light mb-2" placeholder="Write message" id="example-textarea"
             rows="3"></textarea>
              <div class="text-end">
                <div class="btn-group mb-2 d-none d-sm-inline-block">
                  <button type="button" class="btn btn-link btn-sm text-muted font-18"><i class="ri-attachment-2"></i>
                  </button>
                </div>
                <div class="btn-group mb-2 ms-2 d-none d-sm-inline-block">
                  <button type="button" class="btn btn-primary btn-sm">Submit</button>
                </div>
              </div>

              <div class="d-flex mt-2">
                <img class="me-3 avatar-sm rounded-circle" src="@/assets/images/users/avatar-3.jpg"
                     alt="Generic placeholder image">
                <div class="w-100">
                  <h5 class="mt-0">Jeremy Tomlinson</h5>
                  Cras sit amet nibh libero, in gravida nulla. Nulla vel metus scelerisque ante sollicitudin. Cras purus
                  odio, vestibulum in
                  vulputate at, tempus viverra turpis.

                  <div class="d-flex mt-3">
                    <a class="pe-3" href="#">
                      <img src="@/assets/images/users/avatar-4.jpg" class="avatar-sm rounded-circle"
                           alt="Generic placeholder image">
                    </a>
                    <div class="w-100">
                      <h5 class="mt-0">Kathleen Thomas</h5>
                      Cras sit amet nibh libero, in gravida nulla. Nulla vel metus scelerisque ante sollicitudin. Cras
                      purus odio, vestibulum in
                      vulputate at, tempus viverra turpis.
                    </div>
                  </div>
                </div>
              </div>

              <div class="text-center mt-2">
                <a href="javascript:void(0);" class="text-danger">Load more </a>
              </div>
            </b-tab>
            <b-tab title="Files" class="nav-link" id="profile-b1">
              <div class="card mb-1 shadow-none border">
                <div class="p-2">
                  <b-row class="align-items-center">
                    <b-col class="col-auto">
                      <div class="avatar-sm">
                                                        <span class="avatar-title rounded">
                                                            .ZIP
                                                        </span>
                      </div>
                    </b-col>
                    <b-col class="ps-0">
                      <a href="javascript:void(0);" class="text-muted fw-bold">Hyper-admin-design.zip</a>
                      <p class="mb-0">2.3 MB</p>
                    </b-col>
                    <b-col class="col-auto">
                      <!-- Button -->
                      <a href="javascript:void(0);" class="btn btn-link btn-lg text-muted">
                        <i class="ri-download-2-line"></i>
                      </a>
                    </b-col>
                  </b-row>
                </div>
              </div>

              <div class="card mb-1 shadow-none border">
                <div class="p-2">
                  <b-row class="align-items-center">
                    <b-col class="col-auto">
                      <img src="@/assets/images/projects/project-1.jpg" class="avatar-sm rounded" alt="file-image"/>
                    </b-col>
                    <b-col class="ps-0">
                      <a href="javascript:void(0);" class="text-muted fw-bold">Dashboard-design.jpg</a>
                      <p class="mb-0">3.25 MB</p>
                    </b-col>
                    <b-col class="col-auto">
                      <!-- Button -->
                      <a href="javascript:void(0);" class="btn btn-link btn-lg text-muted">
                        <i class="ri-download-2-line"></i>
                      </a>
                    </b-col>
                  </b-row>
                </div>
              </div>

              <div class="card mb-0 shadow-none border">
                <div class="p-2">
                  <b-row class="align-items-center">
                    <b-col class="col-auto">
                      <div class="avatar-sm">
                                                        <span class="avatar-title bg-secondary rounded">
                                                            .MP4
                                                        </span>
                      </div>
                    </b-col>
                    <b-col class="ps-0">
                      <a href="javascript:void(0);" class="text-muted fw-bold">Admin-bug-report.mp4</a>
                      <p class="mb-0">7.05 MB</p>
                    </b-col>
                    <b-col class="col-auto">
                      <!-- Button -->
                      <a href="javascript:void(0);" class="btn btn-link btn-lg text-muted">
                        <i class="ri-download-2-line"></i>
                      </a>
                    </b-col>
                  </b-row>
                </div>
              </div>
            </b-tab>
          </b-tabs>

        </div> <!-- .p-2 -->
      </div>
    </b-modal><!-- /.modal -->


  </Layout>
</template>

<script lang="ts">
import moment from 'moment';
import {VueDraggableNext} from "vue-draggable-next";
import DatePicker from 'vue3-datepicker'

import avatar1 from '@/assets/images/users/avatar-1.jpg'
import Layout from "@/components/layouts/layout.vue";

import {todoData, progressData, reviewData, doneData} from './data'

export default {
  components: {DatePicker, Draggable: VueDraggableNext, Layout},
  data() {
    return {
      moment,
      todoData: todoData,
      progressData: progressData,
      reviewData: reviewData,
      doneData: doneData,
      showModal: false,
      showTaskModal: false,
      defaultdate: '',
      form: {
        project: 'Select',
        title: '',
        priority: 'Low',
        assign: 'Coderthemes',
        date: '',
      },
      submitted: false,
    }
  },
  mounted() {
    this.useMeta({
      title: "Kanban",
    });
  },

  methods: {

    taskformsubmit(e:any) {
      this.submitted = true

      if (this.form.project == '' || this.form.title == '') {
        return
      } else {
        const project = this.form.project
        const title = this.form.title
        const priority = this.form.priority
        const assign = this.form.assign
        const date = this.form.date
        this.todoData.push({
          image: avatar1,
          id: Math.floor(Math.random() * (100 - 1) + 1),
          project,
          title,
          priority,
          comments: 68,
          assign,
          date
        })
        this.showModal = false
      }
      this.submitted = false
      this.form = {  
        project: 'Select',
        title: '',
        priority: 'Low',
        assign: 'Coderthemes',
        date: '',}
    },

    /**
     * Hide modal on close
     */
    hideModal(e:any) {
      this.submitted = false
      this.showModal = false
      this.form = {  
        project: 'Select',
        title: '',
        priority: 'Low',
        assign: 'Coderthemes',
        date: '',}
    },
  },
}
</script>