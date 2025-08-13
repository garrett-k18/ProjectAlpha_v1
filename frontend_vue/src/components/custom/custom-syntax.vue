<template>
  <div class="card">
    <div class="card-body">
      <h4 class="header-title">{{ title }}</h4>
      <p class="text-muted font-14 mb-3">
        <sub-text>
          <slot name="sub-text"></slot>
        </sub-text>
      </p>

      <!--      <b-tabs content-class="mt-3" class="nav-tabs nav-bordered mb-3">-->
      <!--        <b-tab title="Preview" active class="tab-pane">-->
      <preview>
        <slot name="preview"></slot>
      </preview>
      <!--        </b-tab>-->
      <!--        <b-tab title="Code" class="tab-pane">-->
      <!--          <button class="btn-copy-clipboard" @click="doCopy"><span class="">{{ copied ? 'Copied' : 'Copy' }}</span>-->
      <!--          </button>-->
      <!--          <pre class="mb-0">-->
      <!--            <span class="html escape">-->
      <!--              <Prism language="html" class="" v-show="showCode">-->
      <!--                {{ code }}-->
      <!--              </Prism>-->
      <!--            </span>-->
      <!--          </pre>-->
      <!--        </b-tab>-->
      <!--      </b-tabs>-->
    </div>
  </div>
</template>

<script lang="ts">
import 'prismjs';
import Prism from 'vue-prism-component'
import {copyText} from 'vue3-clipboard'

export default {
  components: {Prism},
  props: {
    title: {type: String},
    code: {type: String},
  },
  data() {
    return {
      showCode: true,
      copied: false
    }
  },
  methods: {
    doCopy() {
      copyText(this.code, undefined, (error, event) => {
        if (error) {
          console.log(error)
        } else {
          this.copied = true
          setTimeout(() => {
            this.copied = false
          }, 2000)
          console.log(event)
        }
      })
    }
  }
};
</script>
