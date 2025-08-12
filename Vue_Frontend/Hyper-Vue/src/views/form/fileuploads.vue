<template>
  <Layout>
    <Breadcrumb :title="title" :items="items"/>
    <b-row>
      <b-col cols="12">

        <CustomSyntax title="Dropzone File Upload">
          <template v-slot:sub-text>
            DropzoneJS is an open source library that provides drag’n’drop
            file uploads with image previews.
          </template>
          <template v-slot:preview>
            <b-form
                action="/"
                method="post"
                class="dropzone"
                id="myAwesomeDropzone"
                data-plugin="dropzone"
                data-previews-container="#file-previews"
                data-upload-preview-template="#uploadPreviewTemplate"
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
                <i class="h1 text-muted ri-upload-cloud-2-line"></i>
                <h3>Drop files here or click to upload.</h3>
                <span class="text-muted fs-13"
                >(This is just a demo dropzone. Selected files are
                  <strong>not</strong> actually uploaded.)</span
                >
              </div>
            </b-form>

            <!-- Preview -->
            <div
                v-if="state.files.length >= 1"
                class="dropzone-previews mt-3"
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
                          class="btn btn-link btn-lg text-danger"
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
        </CustomSyntax>
      </b-col>
    </b-row>
  </Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";

import {useDropzone} from "vue3-dropzone";
import {reactive, ref, watch} from "vue";
import CustomSyntax from "@/components/custom/custom-syntax.vue";

export default {
  components: {
    CustomSyntax,
    Layout,
    Breadcrumb,
  },
  setup() {
    const selected = "recent";
    let url = null;

    const state = reactive<any>({
      files: [],
    });

    const {getRootProps, getInputProps, isDragActive, ...rest} = useDropzone({
      onDrop,
    });

    watch(state, () => {
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
          return Math.round(file.size / (1024 * 1024)).toFixed(2) + " MB";
        }
        return Math.round(file.size / 1024).toFixed(2) + " KB";
      }
    }

    return {
      title: 'File Uploads',
      items: [
        {
          text: 'Hyper',
          href: '/',
        },
        {
          text: 'Forms',
          href: '/',
        },
        {
          text: 'File Uploads',
          active: true,
        },
      ],
      selected,
      state,
      getRootProps,
      getInputProps,
      isDragActive,
      getSize,
      ...rest,
      handleClickDeleteFile,
      onChange,
    };
  },
};
</script>
