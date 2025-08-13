<template>
  <Layout>
    <Breadcrumb :title="title" :items="items"/>

    <b-row>
      <b-col cols="12">
        <CustomSyntax title="Simple Drag and Drop Example">
          <template v-slot:sub-text>
            Just specify the data attribute
            <code>data-plugin='dragula'</code> to have drag and drop support in
            your container.
          </template>
          <template v-slot:preview>
            <Draggable
                class="row"
                id="simple-dragula"
                group="cards"
                :list="cardItem"
            >
              <b-col md="4" v-for="(item, index) of cardItem" :key="index">
                <b-card
                    class="mb-0 mt-3 text-white"
                    :class="'bg-' + item.color"
                >
                  <blockquote class="card-bodyquote mb-0">
                    <p>
                      Lorem ipsum dolor sit amet, consectetur adipiscing elit.
                      Integer posuere erat a ante.
                    </p>
                    <footer>
                      Someone famous in
                      <cite title="Source Title">Source Title</cite>
                    </footer>
                  </blockquote>
                </b-card>
              </b-col>
            </Draggable>
          </template>
        </CustomSyntax>
      </b-col>
    </b-row>

    <b-row>
      <b-col cols="12">

        <CustomSyntax title="Move stuff between containers">
          <template v-slot:sub-text>
            Just specify the data attribute <code>data-plugin='dragula'</code> and
            <code>data-containers='["first-container-id", "second-container-id"]'</code>.
          </template>
          <template v-slot:preview>
            <b-row>
              <b-col md="6">
                <div class="bg-dragula p-2 p-lg-4">
                  <h5 class="mt-0">Part 1</h5>
                  <div id="company-list-left" class="py-2">
                    <Draggable group="tasks" :list="list1">
                      <b-card
                          class="mb-0 mt-2"
                          v-for="(item, index) of list1"
                          :key="index"
                      >
                        <div class="d-flex align-items-start">
                          <img
                              :src="item.img"
                              alt="image"
                              class="me-3 d-none d-sm-block avatar-sm rounded-circle"
                          />
                          <div class="w-100 overflow-hidden">
                            <h5 class="mb-1 mt-0">{{ item.name }}</h5>
                            <p>{{ item.role }}</p>
                            <p class="mb-0 text-muted">
                            <span class="fst-italic"
                            ><b>"</b>Disrupt pork belly poutine, asymmetrical
                              tousled succulents selfies. You probably haven't
                              heard of them tattooed master cleanse live-edge
                              keffiyeh.</span
                            >
                            </p>
                          </div>
                        </div>
                      </b-card>
                    </Draggable>
                  </div>
                </div>
              </b-col>

              <b-col md="6">
                <div class="bg-dragula p-2 p-lg-4">
                  <h5 class="mt-0">Part 2</h5>
                  <div id="company-list-right" class="py-2">
                    <Draggable group="tasks" :list="list2">
                      <b-card
                          class="mb-0 mt-2"
                          v-for="(item, index) of list2"
                          :key="index"
                      >
                        <div class="d-flex align-items-start">
                          <img
                              :src="item.img"
                              alt="image"
                              class="me-3 d-none d-sm-block avatar-sm rounded-circle"
                          />
                          <div class="w-100 overflow-hidden">
                            <h5 class="mb-1 mt-0">{{ item.name }}</h5>
                            <p>{{ item.role }}</p>
                            <p class="mb-0 text-muted">
                            <span class="fst-italic"
                            ><b>"</b>Disrupt pork belly poutine, asymmetrical
                              tousled succulents selfies. You probably haven't
                              heard of them tattooed master cleanse live-edge
                              keffiyeh
                            </span>
                            </p>
                          </div>
                        </div>
                      </b-card>
                    </Draggable>
                  </div>
                </div>
              </b-col>
            </b-row>
          </template>
        </CustomSyntax>
      </b-col>
    </b-row>

    <b-row>
      <b-col cols="12">
        <CustomSyntax title="Move stuff between containers using handle">
          <template v-slot:sub-text>
            Just specify the data attribute
            <code>data-plugin='dragula'</code>,
            <code
            >data-containers='["first-container-id",
              "second-container-id"]'</code
            >
            and <code>data-handle-class='dragula-handle'</code>.
          </template>
          <template v-slot:preview>
            <b-row
                data-plugin="dragula"
                data-containers='["handle-dragula-left", "handle-dragula-right"]'
                data-handleClass="dragula-handle"
            >
              <b-col md="6">
                <div class="bg-dragula p-2 p-lg-4">
                  <h5 class="mt-0">Part 1</h5>
                  <div id="handle-dragula-left" class="py-2">
                    <Draggable class="list-group" group="tasks1" :list="list3">
                      <b-card
                          class="mb-0 mt-2"
                          v-for="item of list3"
                          :key="item.image"
                      >
                        <div class="d-flex align-items-start">
                          <img
                              :src="`${item.image}`"
                              alt="image"
                              class="me-3 d-none d-sm-block avatar-sm rounded-circle"
                          />
                          <div class="w-100 overflow-hidden">
                            <h5 class="mb-1 mt-1">{{ item.name }}</h5>
                            <p class="mb-0">{{ item.role }}</p>
                          </div>
                          <span class="dragula-handle"></span>
                        </div>
                      </b-card>
                    </Draggable>
                  </div>
                </div>
              </b-col>

              <b-col md="6">
                <div class="bg-dragula p-2 p-lg-4">
                  <h5 class="mt-0">Part 2</h5>
                  <div id="handle-dragula-right" class="py-2">
                    <Draggable class="list-group" group="tasks1" :list="list4">
                      <b-card
                          class="mb-0 mt-2"
                          v-for="item of list4"
                          :key="item.image"
                      >
                        <div class="d-flex align-items-start">
                          <img
                              :src="`${item.image}`"
                              alt="image"
                              class="me-3 d-none d-sm-block avatar-sm rounded-circle"
                          />
                          <div class="w-100 overflow-hidden">
                            <h5 class="mb-1 mt-1">{{ item.name }}</h5>
                            <p class="mb-0">{{ item.role }}</p>
                          </div>
                          <span class="dragula-handle"></span>
                        </div>
                      </b-card>
                    </Draggable>
                  </div>
                </div>
              </b-col>
            </b-row>
          </template>
        </CustomSyntax>
      </b-col>
    </b-row>
  </Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";
import CustomSyntax from "@/components/custom/custom-syntax.vue";

import {VueDraggableNext} from "vue-draggable-next";

import avatar1 from "@/assets/images/users/avatar-1.jpg";
import avatar2 from "@/assets/images/users/avatar-2.jpg";
import avatar3 from "@/assets/images/users/avatar-3.jpg";
import avatar4 from "@/assets/images/users/avatar-4.jpg";
import avatar5 from "@/assets/images/users/avatar-5.jpg";
import avatar6 from "@/assets/images/users/avatar-6.jpg";
import avatar7 from "@/assets/images/users/avatar-7.jpg";
import avatar8 from "@/assets/images/users/avatar-8.jpg";
import avatar9 from "@/assets/images/users/avatar-9.jpg";
import avatar10 from "@/assets/images/users/avatar-10.jpg";

export default {
  components: {CustomSyntax, Breadcrumb, Layout, Draggable: VueDraggableNext,},
  data() {
    return {
      title: 'Dragula',
      items: [
        {
          text: 'Hyper',
          href: '/',
        },
        {
          text: 'Extended UI',
          href: '/',
        },
        {
          text: 'Dragula',
          active: true,
        },
      ],

      enabled: true,
      dragging: false,
      cardItem: [
        {
          color: "primary",
        },
        {
          color: "secondary",
        },
        {
          color: "success",
        },
        {
          color: "info",
        },
        {
          color: "warning",
        },
        {
          color: "danger",
        },
      ],
      list1: [
        {
          img: avatar1,
          name: "Louis K. Bond",
          role: "Founder & CEO",
        },
        {
          img: avatar2,
          name: "Dennis N. Cloutier",
          role: "Software Engineer",
        },
        {
          img: avatar3,
          name: "Susan J. Sander",
          role: "Web Designer",
        },
      ],
      list2: [
        {
          img: avatar4,
          name: "James M. Short",
          role: "Web Developer",
        },
        {
          img: avatar5,
          name: "Gabriel J. Snyder",
          role: "Business Analyst",
        },
        {
          img: avatar6,
          name: "Louie C. Mason",
          role: "Human Resources",
        },
      ],
      list3: [
        {
          image: avatar7,
          name: "Louis K. Bond",
          role: "Founder & CEO",
        },
        {
          image: avatar8,
          name: "Dennis N. Cloutier",
          role: "Software Engineer",
        },
        {
          image: avatar9,
          name: "Susan J. Sander",
          role: "Web Designer",
        },
      ],
      list4: [
        {
          image: avatar10,
          name: "James M. Short",
          role: "Web Developer",
        },
        {
          image: avatar5,
          name: "Gabriel J. Snyder",
          role: "Business Analyst",
        },
        {
          image: avatar3,
          name: "Louie C. Mason",
          role: "Human Resources",
        },
      ],
    }
  }

}
</script>
