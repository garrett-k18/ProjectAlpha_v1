<template>
  <Layout>
    <Breadcrumb :title="title" :items="items" />
    <b-row>
      <!-- Right Sidebar -->
      <b-col cols="12">
        <div class="card">
          <div class="card-body">
            <!-- Left sidebar -->
            <div class="page-aside-left">
              <div class="d-grid">
                <button
                  type="button"
                  class="btn btn-danger"
                  @click="showModal = true"
                >
                  Compose
                </button>
              </div>

              <div class="email-menu-list mt-3">
                <a href="javascript: void(0);" class="text-danger fw-bold">
                  <i class="ri-inbox-line me-2"></i>Inbox
                  <span class="badge badge-danger-lighten float-end ms-2"
                    >7</span
                  >
                </a>
                <a href="javascript: void(0);">
                  <i class="ri-star-line me-2"></i>Starred
                </a>
                <a href="javascript: void(0);">
                  <i class="ri-time-line me-2"></i>Snoozed
                </a>
                <a href="javascript: void(0);">
                  <i class="ri-article-line me-2"></i>Draft
                  <span class="badge badge-info-lighten float-end ms-2"
                    >32</span
                  >
                </a>
                <a href="javascript: void(0);">
                  <i class="ri-mail-send-line me-2"></i>Sent Mail
                </a>
                <a href="javascript: void(0);">
                  <i class="ri-delete-bin-line me-2"></i>Trash
                </a>
                <a href="javascript: void(0);">
                  <i class="ri-price-tag-3-line me-2"></i>Important
                </a>
                <a href="javascript: void(0);">
                  <i class="ri-alert-line me-2"></i>Spam
                </a>
              </div>

              <div class="mt-4">
                <h6 class="text-uppercase">Labels</h6>
                <div class="email-menu-list labels-list mt-2">
                  <a href="javascript: void(0);">
                    <i class="mdi mdi-circle font-13 text-info me-2"></i>Updates
                  </a>
                  <a href="javascript: void(0);">
                    <i class="mdi mdi-circle font-13 text-warning me-2"></i
                    >Friends
                  </a>
                  <a href="javascript: void(0);">
                    <i class="mdi mdi-circle font-13 text-success me-2"></i
                    >Family
                  </a>
                  <a href="javascript: void(0);">
                    <i class="mdi mdi-circle font-13 text-primary me-2"></i
                    >Social
                  </a>
                  <a href="javascript: void(0);">
                    <i class="mdi mdi-circle font-13 text-danger me-2"></i
                    >Important
                  </a>
                  <a href="javascript: void(0);">
                    <i class="mdi mdi-circle font-13 text-secondary me-2"></i
                    >Promotions
                  </a>
                </div>
              </div>

              <div class="mt-5">
                <h4>
                  <span
                    class="badge rounded-pill p-1 px-2 badge-secondary-lighten"
                    >FREE</span
                  >
                </h4>
                <h6 class="text-uppercase mt-3">Storage</h6>
                <b-progress
                  height="5px"
                  class="my-2"
                  :value="46"
                  variant="success"
                ></b-progress>

                <p class="text-muted font-13 mb-0">
                  7.02 GB (46%) of 15 GB used
                </p>
              </div>
            </div>
            <!-- end Left sidebar -->

            <div class="page-aside-right">
              <Toolbar />
              <div class="mt-3">
                <ul class="email-list">
                  <li
                    v-for="(email, index) in paginatedEmailData"
                    :key="index"
                    :class="{ unread: `${email.unread}` === 'true' }"
                  >
                    <div class="email-sender-info">
                      <div class="checkbox-wrapper-mail">
                        <div class="form-check">
                          <input
                            :id="`mail${index}`"
                            type="checkbox"
                            class="form-check-input"
                          />
                          <label
                            class="form-check-label"
                            :for="`mail${index}`"
                          ></label>
                        </div>
                      </div>
                      <span
                        :class="`star-toggle mdi mdi-star-outline text-${email.text}`"
                      ></span>
                      <a href="javascript: void(0);" class="email-title">{{
                        email.title
                      }}</a>
                    </div>
                    <div class="email-content">
                      <a href="javascript: void(0);" class="email-subject">{{
                        email.subject
                      }}</a>
                      <div class="email-date">{{ email.date }}</div>
                    </div>
                    <div class="email-action-icons">
                      <ul class="list-inline">
                        <li class="list-inline-item">
                          <a href="javascript: void(0);">
                            <i
                              class="mdi mdi-archive email-action-icons-item"
                            ></i>
                          </a>
                        </li>
                        <li class="list-inline-item">
                          <a href="javascript: void(0);">
                            <i
                              class="mdi mdi-delete email-action-icons-item"
                            ></i>
                          </a>
                        </li>
                        <li class="list-inline-item">
                          <a href="javascript: void(0);">
                            <i
                              class="mdi mdi-email-open email-action-icons-item"
                            ></i>
                          </a>
                        </li>
                        <li class="list-inline-item">
                          <a href="javascript: void(0);">
                            <i
                              class="mdi mdi-clock email-action-icons-item"
                            ></i>
                          </a>
                        </li>
                      </ul>
                    </div>
                  </li>
                </ul>
                <b-row class="justify-content-md-between align-items-md-center">
                  <b-col xl="7"
                    >Showing {{ startIndex }} - {{ endIndex }} of
                    {{ rows }}</b-col
                  >
                  <!-- end col-->
                  <b-col xl="5">
                    <!-- pagination -->
                    <div
                      class="text-md-end float-md-end mt-2 pagination-rounded"
                    >
                      <b-pagination
                        v-model="currentPage"
                        :total-rows="rows"
                        :per-page="perPage"
                        @input="onPageChange"
                      ></b-pagination>
                    </div>
                    <!-- end pagination -->
                  </b-col>
                  <!-- end col-->
                </b-row>
              </div>
            </div>
            <!-- end inbox-rightbar-->
          </div>
        </div>
        <!-- end card -->
      </b-col>
      <!-- end col -->
    </b-row>
    <!-- end row -->

    <!-- Compose modal -->
    <b-modal
      v-model="showModal"
      title="New Message"
      title-tag="h4"
      header-class="modal-colored-header bg-primary"
      hide-footer
    >
      <div>
        <b-form class="p-1">
          <div class="mb-2">
            <label for="msgto" class="form-label">To</label>
            <input
              id="msgto"
              type="text"
              class="form-control"
              placeholder="example@email.com"
            />
          </div>
          <div class="mb-2">
            <label for="mailsubject" class="form-label">Subject</label>
            <input
              id="mailsubject"
              type="text"
              class="form-control"
              placeholder="your subject"
            />
          </div>
          <div class="write-mdg-box mb-3">
            <label class="form-label">Message</label>
            <QuillEditor
              theme="snow"
              :toolbar="toolbar"
              style="height: 150px"
              :placeholder="'Write something...'"
            />
          </div>

          <b-button variant="primary" @click="showModal = false">
            <i class="mdi mdi-send me-1"></i> Send Message
          </b-button>
          <b-button variant="light" class="ms-1" @click="showModal = false"
            >Cancel</b-button
          >
        </b-form>
      </div>
    </b-modal>
    <!-- end modal -->
  </Layout>
</template>

<script lang="ts">

import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";
import Toolbar from "@/views/apps/email/toolbar.vue";
import { QuillEditor } from "@vueup/vue-quill";

import { emailData } from "./data";

export default {
  components: {
    QuillEditor,
    Layout,
    Breadcrumb,
    Toolbar,
  },
  data() {
    return {
      emailData: emailData,
      title: "Inbox",
      items: [
        {
          text: "Hyper",
          href: "/",
        },
        {
          text: "Email",
          href: "/",
        },
        {
          text: "Inbox",
          active: true,
        },
      ],
      showModal: false,
      // page number
      currentPage: 1,
      // default page size
      perPage: 15,

      // start and end index
      startIndex: 1,
      endIndex: 15,

      toolbar: [
        ["bold", "italic", "underline"],
        ["blockquote"],
        [{ list: "ordered" }, { list: "bullet" }],
        ["link", "image", "video"],
        ["clean"],
      ],
    };
  },
  computed: {
    rows() {
      return this.emailData.length;
    },
  },
  created() {
    this.startIndex = 0;
    this.endIndex = this.perPage;

    this.paginatedEmailData = this.emailData.slice(
      this.startIndex,
      this.endIndex
    );
  },
  methods: {
    /**
     * page change
     */
    onPageChange() {
      this.startIndex = (this.currentPage - 1) * this.perPage;
      this.endIndex = (this.currentPage - 1) * this.perPage + this.perPage;

      this.paginatedEmailData = this.emailData.slice(
        this.startIndex,
        this.endIndex
      );
    },
  },
};
</script>
