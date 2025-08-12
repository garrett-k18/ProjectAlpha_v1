<template>
  <Layout>
    <Breadcrumb :title="title" :items="items"/>
    <b-row class="mb-2">
      <b-col sm="4">
        <router-link tag="a" to="/apps/projects/create" class="btn btn-danger rounded-pill mb-3">
          <i class="mdi mdi-plus"></i> Create Project
        </router-link>
      </b-col>
      <b-col sm="8">
        <div class="text-sm-end">
          <div class="btn-group mb-3">
            <button type="button" class="btn btn-primary">All</button>
          </div>
          <div class="btn-group mb-3 ms-1">
            <button type="button" class="btn btn-light">Ongoing</button>
            <button type="button" class="btn btn-light">Finished</button>
          </div>
          <div class="btn-group mb-3 ms-2 d-none d-sm-inline-block">
            <button type="button" class="btn btn-secondary"><i class="ri-function-line"></i></button>
          </div>
          <div class="btn-group mb-3 d-none d-sm-inline-block">
            <button type="button" class="btn btn-link text-muted"><i class="ri-list-check-2"></i></button>
          </div>
        </div>
      </b-col>
      <!-- end col-->
    </b-row>
    <b-row>
      <b-col md="6" xxl="3" v-for="data of projects" :key="data.title">
        <div class="card d-block">
          <div class="card-body">
            <b-dropdown
                class="card-widgets"
                right
                variant="white"
                toggle-tag="a"
                toggle-class="arrow-none p-0"
            >
              <template v-slot:button-content>
                <i class="ri-more-fill"></i>
              </template>
              <b-dropdown-item href="javascript:void(0);">
                <i class="mdi mdi-pencil me-1"></i>Edit
              </b-dropdown-item>
              <b-dropdown-item href="javascript:void(0);">
                <i class="mdi mdi-delete me-1"></i>Delete
              </b-dropdown-item>
              <b-dropdown-item href="javascript:void(0);">
                <i class="mdi mdi-email-outline me-1"></i>Invite
              </b-dropdown-item>
              <b-dropdown-item href="javascript:void(0);">
                <i class="mdi mdi-exit-to-app me-1"></i>Leave
              </b-dropdown-item>
            </b-dropdown>
            <!-- project title-->
            <h4 class="mt-0">
              <router-link tag="a" to="/apps/projects/details" class="text-title">{{ data.title }}</router-link>
            </h4>
            <div class="badge" :class="data.status==='Finished' ? 'bg-success': 'bg-secondary'">{{ data.status }}</div>

            <p class="text-muted font-13 my-3">
              {{ data.description }}
              <a
                  href="javascript:void(0);"
                  class="fw-bold text-muted"
              >view more</a>
            </p>

            <!-- project detail-->
            <p class="mb-1">
              <span class="pe-2 text-nowrap mb-2 d-inline-block">
                <i class="mdi mdi-format-list-bulleted-type text-muted"></i>
                <b>{{ data.tasks }}</b> Tasks
              </span>
              <span class="text-nowrap mb-2 d-inline-block">
                <i class="mdi mdi-comment-multiple-outline text-muted"></i>
                <b>{{ data.comments }}</b> Comments
              </span>
            </p>
            <div>
              <a
                  v-b-tooltip.top
                  :title="`${data.name[0]}`"
                  href="javascript:void(0);"
                  class="d-inline-block"
              >
                <img :src="`${data.images[0]}`" class="rounded-circle avatar-xs" alt="friend"/>
              </a>

              <a
                  v-b-tooltip.top
                  :title="`${data.name[1]}`"
                  href="javascript:void(0);"
                  class="d-inline-block"
              >
                <img :src="`${data.images[1]}`" class="rounded-circle avatar-xs ms-1" alt="friend"/>
              </a>

              <a
                  v-if="data.images[2]"
                  v-b-tooltip.top
                  :title="`${data.name[2]}`"
                  href="javascript:void(0);"
                  class="d-inline-block"
              >
                <img :src="`${data.images[2]}`" class="rounded-circle avatar-xs ms-1" alt="friend"/>
              </a>
              <a
                  href="javascript:void(0);"
                  class="d-inline-block text-muted fw-bold ms-2"
              >{{ data.text }}</a>
            </div>
          </div>
          <ul class="list-group list-group-flush">
            <li class="list-group-item p-3">
              <!-- project progress-->
              <p class="mb-2 fw-bold">
                Progress
                <span class="float-end">{{ data.progressValue }}%</span>
              </p>
              <b-progress :value="data.progressValue" height="5px"></b-progress>
            </li>
          </ul>
        </div>
      </b-col>
    </b-row>

    <b-row>
      <b-col md="6" xxl="3" v-for="data of projectImage" :key="data.title">
        <!-- project card -->
        <div class="card d-block">
          <!-- project-thumbnail -->
          <img class="card-img-top" :src="`${data.product}`" alt="project image cap"/>
          <div class="card-img-overlay">
            <div class="badge p-1" :class="data.status==='Finished' ? 'text-bg-success': 'text-bg-secondary'">
              {{ data.status }}
            </div>
          </div>

          <div class="card-body position-relative">
            <!-- project title-->
            <h4 class="mt-0">
              <router-link tag="a" to="/apps/projects/details" class="text-title">{{ data.title }}</router-link>
            </h4>

            <!-- project detail-->
            <p class="mb-3">
              <span class="pe-2 text-nowrap">
                <i class="mdi mdi-format-list-bulleted-type"></i>
                <b>{{ data.tasks }}</b> Tasks
              </span>
              <span class="text-nowrap">
                <i class="mdi mdi-comment-multiple-outline"></i>
                <b>{{ data.comments }}</b> Comments
              </span>
            </p>
            <div class="mb-3">
              <a
                  v-b-tooltip.top
                  :title="`${data.name[0]}`"
                  href="javascript:void(0);"
                  class="d-inline-block"
              >
                <img :src="`${data.images[0]}`" class="rounded-circle avatar-xs" alt="friend"/>
              </a>

              <a
                  v-b-tooltip.top
                  :title="`${data.name[1]}`"
                  href="javascript:void(0);"
                  class="d-inline-block"
              >
                <img :src="`${data.images[1]}`" class="rounded-circle avatar-xs ms-1" alt="friend"/>
              </a>

              <a
                  v-if="data.images[2]"
                  v-b-tooltip.top
                  :title="`${data.name[2]}`"
                  href="javascript:void(0);"
                  class="d-inline-block"
              >
                <img :src="`${data.images[2]}`" class="rounded-circle avatar-xs ms-1" alt="friend"/>
              </a>
            </div>

            <!-- project progress-->
            <p class="mb-2 fw-bold">
              Progress
              <span class="float-end">{{ data.progressValue }}%</span>
            </p>
            <b-progress :value="data.progressValue" height="5px"></b-progress>
          </div>
          <!-- end card-body-->
        </div>
        <!-- end card-->
      </b-col>
      <!-- end col -->
    </b-row>
  </Layout>
</template>
<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";

import {projects, projectImage} from './data'

export default {

  components: {
    Layout,
    Breadcrumb
  },
  data() {
    return {
      projects: projects,
      projectImage: projectImage,
      title: 'Projects List',
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
          text: 'Projects List',
          active: true,
        },
      ],
    }
  },
}
</script>