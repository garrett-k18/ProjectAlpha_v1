<template>
  <div class="card">
    <div class="card-body">
      <b-dropdown
          class="card-widgets"
          variant="black"
          toggle-tag="a"
          toggle-class="arrow-none p-0"
          right
      >
        <template v-slot:button-content>
          <i class="uil uil-ellipsis-h"></i>
        </template>

        <b-dropdown-item href="javascript:void(0);">
          <i class="uil uil-file-upload me-1"></i>Attachment
        </b-dropdown-item>
        <b-dropdown-item href="javascript:void(0);">
          <i class="uil uil-edit me-1"></i>Edit
        </b-dropdown-item>
        <b-dropdown-item href="javascript:void(0);">
          <i class="uil uil-file-copy-alt me-1"></i>Mark as Duplicate
        </b-dropdown-item>
        <div class="dropdown-divider"></div>
        <b-dropdown-item href="javascript:void(0);" class="text-danger">
          <i class="uil uil-trash-alt me-1"></i>Delete
        </b-dropdown-item>
      </b-dropdown>

      <div class="form-check float-start">
        <input type="checkbox" class="form-check-input" id="completedCheck">
        <label class="form-check-label" for="completedCheck">
          Mark as completed
        </label>
      </div>

      <hr class="mt-4 mb-2" />
      <b-row>
        <b-col>
          <h4>Draft the new contract document for sales team</h4>

          <b-row>
            <b-col cols="6">
              <!-- assignee -->
              <p class="mt-2 mb-1 text-muted">Assigned To</p>
              <div class="d-flex">
                <img
                    src="@/assets/images/users/avatar-9.jpg"
                    alt="Arya S"
                    class="rounded-circle me-2"
                    height="24"
                />
                <div>
                  <h5 class="mt-1 font-14">Arya Stark</h5>
                </div>
              </div>
              <!-- end assignee -->
            </b-col>
            <!-- end col -->

            <b-col cols="6">
              <!-- start due date -->
              <p class="mt-2 mb-1 text-muted">Due Date</p>
              <div class="d-flex">
                <i class="uil uil-schedule font-18 text-success me-1"></i>
                <div class="w-100">
                  <h5 class="mt-1 font-14">Today 10am</h5>
                </div>
              </div>
              <!-- end due date -->
            </b-col>
            <!-- end col -->
          </b-row>
          <!-- end row -->

          <!-- task description -->
          <b-row class="mt-3">
            <b-col>

              <div class="border rounded">
                <QuillEditor
                    :content="taskDetail"
                    :toolbar="toolbar"
                    content-type="html"
                    style="height: 130px"
                    theme="bubble"
                />
              </div>
            </b-col>
            <!-- end col -->
          </b-row>
          <!-- end task description -->

          <!-- start sub tasks/checklists -->
          <h5 class="mt-4 mb-2 font-16">Checklists/Sub-tasks</h5>
          <div class="form-check mt-1">
            <input id="checklist1" type="checkbox" class="form-check-input" />
            <label
                class="form-check-label strikethrough"
                for="checklist1"
            >Find out the old contract documents</label>
          </div>

             <div class="form-check mt-1">
            <input id="checklist2" type="checkbox" class="form-check-input" />
            <label
                class="form-check-label strikethrough"
                for="checklist2"
            >Organize meeting sales associates to understand need in detail</label>
          </div>

             <div class="form-check mt-1">
            <input id="checklist3" type="checkbox" class="form-check-input" />
            <label
                class="form-check-label strikethrough"
                for="checklist3"
            >Make sure to cover every small details</label>
          </div>
          <!-- end sub tasks/checklists -->

          <!-- start attachments -->
          <h5 class="mt-4 mb-2 font-16">Attachments</h5>
          <div class="card mb-2 shadow-none border">
            <div class="p-1">
              <b-row class="align-items-center">
                <b-col class="col-auto">
                  <div class="avatar-sm">
                    <span class="avatar-title rounded">.ZIP</span>
                  </div>
                </b-col>
                <b-col class="ps-0">
                  <a href="javascript:void(0);" class="text-muted font-weight-bold">sales-assets.zip</a>
                  <p class="mb-0">2.3 MB</p>
                </b-col>
                <b-col class="col-auto">
                  <!-- Button -->
                  <a
                      v-b-tooltip.hover.bottom
                      href="javascript:void(0);"
                      title="Download"
                      class="btn btn-link text-muted btn-lg p-0"
                  >
                    <i class="uil uil-cloud-download"></i>
                  </a>
                  <a
                      v-b-tooltip.hover.bottom
                      href="javascript:void(0);"
                      title="Delete"
                      class="btn btn-link text-danger btn-lg p-0"
                  >
                    <i class="uil uil-multiply"></i>
                  </a>
                </b-col>
              </b-row>
            </div>
          </div>
          <div class="card mb-2 shadow-none border">
            <div class="p-1">
              <b-row class="align-items-center">
                <b-col class="col-auto">
                  <img
                      src="@/assets/images/projects/project-1.jpg"
                      class="avatar-sm rounded"
                      alt="file-image"
                  />
                </b-col>
                <b-col class="ps-0">
                  <a
                      href="javascript:void(0);"
                      class="text-muted font-weight-bold"
                  >new-contarcts.docx</a>
                  <p class="mb-0">1.25 MB</p>
                </b-col>
                <b-col class="col-auto">
                  <!-- Button -->
                  <a
                      v-b-tooltip.hover.bottom
                      href="javascript:void(0);"
                      title="Download"
                      class="btn btn-link text-muted btn-lg p-0"
                  >
                    <i class="uil uil-cloud-download"></i>
                  </a>
                  <a
                      v-b-tooltip.hover.bottom
                      href="javascript:void(0);"
                      title="Delete"
                      class="btn btn-link text-danger btn-lg p-0"
                  >
                    <i class="uil uil-multiply"></i>
                  </a>
                </b-col>
              </b-row>
            </div>
          </div>
          <!-- end attachments -->

          <!-- comments -->
          <b-row class="mt-3">
            <b-col>
              <h5 class="mb-2 font-16">Comments</h5>

              <div class="d-flex mt-3 p-1">
                <img
                    src="@/assets/images/users/avatar-9.jpg"
                    class="me-2 rounded-circle"
                    height="36"
                    alt="Arya Stark"
                />
                <div class="w-100">
                  <h5 class="mt-0 mb-0">
                    <span class="float-end text-muted font-12">4:30am</span>
                    Arya Stark
                  </h5>
                  <p
                      class="mt-1 mb-0 text-muted"
                  >Should I review the last 3 years legal documents as well?</p>
                </div>
              </div>
              <!-- end comment -->

              <hr />

              <div class="d-flex mt-2 p-1">
                <img
                    src="@/assets/images/users/avatar-5.jpg"
                    class="me-2 rounded-circle"
                    height="36"
                    alt="Dominc B"
                />
                <div class="w-100">
                  <h5 class="mt-0 mb-0">
                    <span class="float-end text-muted font-12">3:30am</span>
                    Gary Somya
                  </h5>
                  <p
                      class="mt-1 mb-0 text-muted"
                  >@Arya FYI..I have created some general guidelines last year.</p>
                </div>
              </div>
              <!-- end comment-->

              <hr />
            </b-col>
            <!-- end col -->
          </b-row>
          <!-- end row -->

          <b-row class="mt-2">
            <b-col>
              <div class="border rounded">
                <b-form action="#" class="comment-area-box">
                  <textarea
                      rows="3"
                      class="form-control border-0 resize-none"
                      placeholder="Your comment..."
                  ></textarea>
                  <div class="p-2 bg-light">
                    <div class="float-end">
                      <button type="submit" class="btn btn-sm btn-success">
                        <i class="uil uil-message me-1"></i>Submit
                      </button>
                    </div>
                    <div>
                      <a href="#" class="btn btn-sm px-1 btn-light">
                        <i class="uil uil-cloud-upload"></i>
                      </a>
                      <a href="#" class="btn btn-sm px-1 btn-light">
                        <i class="uil uil-at"></i>
                      </a>
                    </div>
                  </div>
                </b-form>
              </div>
              <!-- end .border-->
            </b-col>
            <!-- end col-->
          </b-row>
          <!-- end row-->
          <!-- end comments -->
        </b-col>
        <!-- end col -->
      </b-row>
    </div>
  </div>
  <!-- end row-->
</template>
<script lang="ts">
import { QuillEditor } from "@vueup/vue-quill";
import "@vueup/vue-quill/dist/vue-quill.bubble.css";

export default {
  components: {
    QuillEditor,
  },
  data() {
    return {
      taskDetail: `<h3>This is an simple editable area.</h3>
  - Select a text to reveal the toolbar.
  - Edit rich document on-the-fly, so elastic!
    <span ><b>End of simple area</b></span>`,
      toolbar: [
        ["bold", "italic", "link"],
        [{header: "1"}, {header: "2"}, "blockquote"],
      ],
    };
  },
}
</script>