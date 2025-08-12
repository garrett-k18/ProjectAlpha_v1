<template>
  <div class="card">
    <div class="card-body">
      <h5 class="card-title mb-3">Attachments</h5>

      <Dropzone/>

      <div class="card my-1 shadow-none border">
        <div class="p-2">
          <b-row class="align-items-center">
            <b-col class="col-auto">
              <div class="avatar-sm">
                <span class="avatar-title rounded">.ZIP</span>
              </div>
            </b-col>
            <b-col class="ps-0">
              <a
                  href="javascript:void(0);"
                  class="text-muted fw-bold"
              >Hyper-admin-design.zip</a>
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
              <img
                  src="@/assets/images/projects/project-1.jpg"
                  class="avatar-sm rounded"
                  alt="file-image"
              />
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
                <span class="avatar-title bg-secondary rounded">.MP4</span>
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
    </div>
  </div>
</template>

<script lang="ts">
import Dropzone from "@/components/dropzone.vue";

export default {
  components: {Dropzone},
}
</script>