<template>
  <b-form
      action="/"
      method="post"
      class="dropzone"
      id="myAwesomeDropzone"
      v-bind="getRootProps()"
  >
    <div class="fallback">
      <input
          name="file"
          v-bind="getInputProps()"
          @change="onChange"
      />
    </div>

    <div class="dz-message needsclick">
      <i class="h3 text-muted ri-upload-cloud-2-line"></i>
      <h4>Drop files here or click to upload.</h4>
    </div>
  </b-form>

  <div class="dropzone-previews mt-3" id="file-previews"></div>

  <div
      v-if="state.files.length >= 1"
      class=""
      id="uploadPreviewTemplate"
  >
    <div class="card mb-1 mb-0 shadow-none border">
      <div class="p-2">
        <b-row class="align-items-center">
          <b-col class="col-auto">
            <img
                data-dz-thumbnail
                url=""
                class="avatar-sm rounded bg-light"
                alt=""
            />
          </b-col>
          <b-col class="ps-0">
            <a
                class="text-muted fw-bold"
                data-dz-name
                v-if="state.files"
            >{{ state.files[0]?.name }}</a
            >
            <p class="mb-0" data-dz-size>
              {{ getSize(state.files[0]) }}
            </p>
          </b-col>
          <b-col class="col-auto">
            <a
                @click="handleClickDeleteFile(0)"
                class="btn btn-link btn-lg text-muted"
                data-dz-remove
            >
              <i class="ri-close-line"></i>
            </a>
          </b-col>
        </b-row>
      </div>
    </div>
  </div>

</template>

<script lang="ts">
import {useDropzone} from "vue3-dropzone";
import {reactive, ref, watch} from "vue";

export default {
  setup() {
    const selected = "recent";
    let url = null;
    let size;

    const state = reactive<any>({
      files: [],
    });

    const {getRootProps, getInputProps, isDragActive, ...rest} = useDropzone({
      onDrop,
    });

    watch(state, () => {
      getSize(state.files[0]);
      if (state.files[0]) {
        url = URL.createObjectURL(state.files[0]);
      }
    });

    watch(isDragActive, () => {
    });

    function onDrop(acceptFiles: any, rejectReasons: any) {
      state.files = acceptFiles;
    }

    function handleClickDeleteFile(index: number) {
      state.files.splice(index, 1);
    }

    function onChange() {
      getSize(state.files[0]);
    }

    function getSize(file: File) {
      if (file) {
        if (Math.round(file.size / (1024 * 1024)) > 0) {
          return (size =
              Math.round(file.size / (1024 * 1024)).toFixed(2) + " MB");
        }
        return (size = Math.round(file.size / 1024).toFixed(2) + " KB");
      }
    }

    return {
      selected,
      state,
      size,
      getRootProps,
      getInputProps,
      isDragActive,
      ...rest,
      handleClickDeleteFile,
      onChange,
      getSize,
    };
  },
}
</script>
