<template>
  <Layout>
    <Breadcrumb :title="title" :items="items"/>
    <b-row>
      <b-col cols="12">
        <div class="card">
          <div class="card-body">
            <b-row>
              <b-col xl="6">
                <div class="mb-3">
                  <label for="projectname" class="form-label">Name</label>
                  <input
                      id="projectname"
                      type="text"
                      class="form-control"
                      placeholder="Enter project name"
                  />
                </div>

                <div class="mb-3">
                  <label for="project-overview" class="form-label">Overview</label>
                  <textarea
                      id="project-overview"
                      class="form-control"
                      rows="5"
                      placeholder="Enter some brief about project.."
                  ></textarea>
                </div>

                <!-- Date View -->
                <div class="mb-3 position-relative">
                  <label class="form-label">Start Date</label>
                  <date-picker
                      class="form-control"
                      v-model="startDate"
                      :first-day-of-week="1"
                      lang="en"
                      format="DD-MMM-YYYY"
                  ></date-picker>
                </div>

                <div class="mb-3">
                  <label for="project-budget" class="form-label">Budget</label>
                  <input
                      id="project-budget"
                      type="text"
                      class="form-control"
                      placeholder="Enter project budget"
                  />
                </div>

                <div class=" mb-0">
                  <label for="project-overview" class="form-label">Team Members</label>

                  <select class="form-control select2" data-toggle="select2">
                    <option>Select</option>
                    <option value="AZ">Mary Scott</option>
                    <option value="CO">Holly Campbell</option>
                    <option value="ID">Beatrice Mills</option>
                    <option value="MT">Melinda Gills</option>
                    <option value="NE">Linda Garza</option>
                    <option value="NM">Randy Ortez</option>
                    <option value="ND">Lorene Block</option>
                    <option value="UT">Mike Baker</option>
                  </select>

                  <div class="mt-2">
                    <a
                        v-b-tooltip.hover
                        href="javascript:void(0);"
                        title="Mat Helme"
                        class="d-inline-block"
                    >
                      <img
                          src="@/assets/images/users/avatar-6.jpg"
                          class="rounded-circle avatar-xs"
                          alt="friend"
                      />
                    </a>

                    <a
                        v-b-tooltip.hover
                        href="javascript:void(0);"
                        title="Michael Zenaty"
                        class="d-inline-block ms-1"
                    >
                      <img
                          src="@/assets/images/users/avatar-7.jpg"
                          class="rounded-circle avatar-xs"
                          alt="friend"
                      />
                    </a>

                    <a
                        v-b-tooltip.hover
                        href="javascript:void(0);"
                        title="James Anderson"
                        class="d-inline-block ms-1"
                    >
                      <img
                          src="@/assets/images/users/avatar-8.jpg"
                          class="rounded-circle avatar-xs"
                          alt="friend"
                      />
                    </a>

                    <a
                        v-b-tooltip.hover
                        href="javascript:void(0);"
                        title="Lorene Block"
                        class="d-inline-block ms-1"
                    >
                      <img
                          src="@/assets/images/users/avatar-4.jpg"
                          class="rounded-circle avatar-xs"
                          alt="friend"
                      />
                    </a>

                    <a
                        v-b-tooltip.hover
                        href="javascript:void(0);"
                        title="Mike Baker"
                        class="d-inline-block ms-1"
                    >
                      <img
                          src="@/assets/images/users/avatar-5.jpg"
                          class="rounded-circle avatar-xs"
                          alt="friend"
                      />
                    </a>
                  </div>
                </div>
              </b-col>
              <!-- end col-->

              <b-col xl="6">
                <div class="mb-3 mt-3 mt-xl-0">
                  <label for="projectname" class="mb-0">Avatar</label>
                  <p class="text-muted font-14">Recommended thumbnail size 800x400 (px).</p>

                  <Dropzone/>
                  <div id="file-previews" class="dropzone-previews mt-3"></div>
                </div>

                <!-- Date View -->
                <div class="mb-3 position-relative">
                  <label class="form-label">Due Date</label>
                  <DatePicker
                      class="form-control"
                      v-model="dueDate"
                      :first-day-of-week="1"
                      lang="en"
                      format="DD-MMM-YYYY"
                  ></DatePicker>
                </div>
              </b-col>
              <!-- end col-->
            </b-row>
            <!-- end row -->
          </div>
          <!-- end card-body -->
        </div>
        <!-- end card-->
      </b-col>
      <!-- end col-->
    </b-row>
    <!-- end row-->
  </Layout>
</template>

<script lang="ts">
import DatePicker from 'vue3-datepicker'
import {useDropzone} from 'vue3-dropzone'

import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";
import Dropzone from "@/components/dropzone.vue";

export default {

  components: {Dropzone, DatePicker, Layout, Breadcrumb},
  data() {
    return {
      title: 'Create Project',
      items: [
        {
          text: 'Hyper',
          href: '/',
        },
        {
          text: 'Projects',
          href: '/',
        },
        {
          text: 'Create Project',
          active: true,
        },
      ],
      startDate: '' as unknown as Date,
      dueDate: '' as unknown as Date,
      dropzoneOptions: {
        url: 'https://httpbin.org/post',
        previewTemplate: this.template(),
        previewsContainer: '.dropzone-previews',
      },
    }
  },
  methods: {
    template: function () {
      return `
      <div class="card mt-1 mb-0 shadow-none border">
          <div class="p-2">
              <div class="row align-items-center">
                  <div class="col-auto">
                      <img data-dz-thumbnail-bg src="#" class="avatar-sm rounded bg-light" alt="">
                  </div>
                  <div class="col pl-0">
                      <a href="javascript:void(0);" class="text-muted font-weight-bold" data-dz-name></a>
                      <p class="mb-0" data-dz-size></p>
                  </div>
                  <div class="col-auto">
                      <!-- Button -->
                      <a href="" class="btn btn-link btn-lg text-muted" data-dz-remove>
                          <i class="dripicons-cross"></i>
                      </a>
                  </div>
              </div>
          </div>
      </div>
      `
    },
  },
}
</script>

