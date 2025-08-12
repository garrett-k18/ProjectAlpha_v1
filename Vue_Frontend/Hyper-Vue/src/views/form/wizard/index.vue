<template>
  <Layout>
    <Breadcrumb :title="title" :items="items" />

    <b-row>
      <b-col xl="6">
        <CustomSyntax title="Basic Wizard">
          <template v-slot:sub-text>
          </template>
          <template v-slot:preview>
            <b-form>
              <FormWizard1 />
            </b-form>
          </template>
        </CustomSyntax>
      </b-col>

      <b-col xl="6">
        <CustomSyntax title="Button Wizard">
          <template v-slot:sub-text>
          </template>
          <template v-slot:preview>
            <b-form>
              <FormWizard2 />
            </b-form>
          </template>
        </CustomSyntax>
      </b-col>
    </b-row>

    <b-row>
      <b-col xl="6">
        <CustomSyntax title="Wizard With Progress Bar">
          <template v-slot:sub-text>
          </template>
          <template v-slot:preview>
            <b-form>
              <FormWizard1 :bar="true" />
            </b-form>
          </template>
        </CustomSyntax>
      </b-col>

      <b-col xl="6">
        <CustomSyntax title="Wizard With Form Validation">
          <template v-slot:sub-text>
          </template>
          <template v-slot:preview>
            <b-form>
              <FormWizard3 />
            </b-form>
          </template>
        </CustomSyntax>
      </b-col>
    </b-row>
  </Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";

import FormWizard1 from "./form-wizard-1.vue";
import FormWizard2 from "./form-wizard-2.vue";
import FormWizard3 from "./form-wizard-3.vue";
import CustomSyntax from "@/components/custom/custom-syntax.vue";

export default {
  components: {CustomSyntax, Layout, Breadcrumb, FormWizard1, FormWizard2, FormWizard3 },
  data() {
    return {
      title: 'Form Wizard',
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
          text: 'Form Wizard',
          active: true,
        },
      ],
    };
  },
};
</script>
