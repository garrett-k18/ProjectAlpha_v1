<template>
  <Layout>
    <Breadcrumb :title="title" :items="items"/>

    <b-row>
      <b-col cols="12">
        <CustomSyntax title="Quill Editor">
          <template v-slot:sub-text>
            Snow is a clean, flat toolbar theme.
          </template>
          <template v-slot:preview>
            <QuillEditor
                theme="snow"
                :toolbar="toolbar1"
                style="height: 300px"
                :content="taskDetail"
                content-type="html"
            />
          </template>
        </CustomSyntax>
      </b-col>
    </b-row>

    <b-row class="row">
      <b-col cols="12">
        <CustomSyntax title="Bubble Editor">
          <template v-slot:sub-text>
            Bubble is a simple tooltip based theme.
          </template>
          <template v-slot:preview>
            <QuillEditor
                theme="bubble"
                style="height: 300px"
                :toolbar="toolbar2"
                :content="taskDetail"
                content-type="html"
            />
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
import {QuillEditor} from "@vueup/vue-quill";


export default {
  components: {CustomSyntax, Layout, Breadcrumb, QuillEditor},
  data() {
    return {
      title: 'Editors',
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
          text: 'Editors',
          active: true,
        },
      ],

      taskDetail: `<h3><span class="ql-size-large">Hello World!</span></h3>
      <h3>This is a simple editable area.</h3>
      - Select a text to reveal the toolbar.
      - Edit rich document on-the-fly, so elastic!
      <span ><b>End of simple area</b></span>`,
      toolbar1: [
        [{font: []}, {size: []}],
        ["bold", "italic", "underline", "strike"],
        [{color: []}, {background: []}],
        [{script: "super"}, {script: "sub"}],
        [{header: [false, 1, 2, 3, 4, 5, 6]}, "blockquote", "code-block"],
        [
          {list: "ordered"},
          {list: "bullet"},
          {indent: "-1"},
          {indent: "+1"},
        ],
        ["direction", {align: []}],
        ["link", "image", "video"],
        ["clean"],
      ],

      toolbar2: [
        ["bold", "italic", "link"],
        [{header: "1"}, {header: "2"}, "blockquote"],
      ],

      content: '',
      configs: {
        spellChecker: false,
        autosave: {
          enabled: true,
          unique_id: 'simplemde1',
        },
      },
    };
  },

};
</script>
