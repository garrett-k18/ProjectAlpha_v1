<template>
  <form-wizard
      shape="tab"
      color="#727cf5"
      class="pb-0"
      @on-change="(prevIndex:number,currentIndex:number) => onTabShow(prevIndex,currentIndex)"
  >
    <b-progress
        v-if="bar"
        :value="value"
        :max="max"
        variant="success"
        striped
        :animated="true"
        class="progress mb-3"
        style="height: 7px"
    ></b-progress>

    <tab-content
        customIcon='<i class="mdi mdi-account-circle fw-normal align-middle me-1"></i>
                              <span class="d-none d-sm-inline">Account</span>'
        id="basictab1"
    >
      <b-row>
        <b-col cols="12">
          <b-row class="mb-3">
            <label class="col-md-3 col-form-label" for="userName"
            >User name</label
            >
            <b-col md="9">
              <b-form-input
                  type="text"
                  id="userName"
                  name="userName"
                  v-model="wizardData.username"
              />
            </b-col>
          </b-row>
          <b-row class="mb-3">
            <label class="col-md-3 col-form-label" for="password">
              Password</label
            >
            <b-col md="9">
              <b-form-input
                  type="password"
                  id="password"
                  name="password"
                  v-model="wizardData.pass"
              />
            </b-col>
          </b-row>

          <b-row class="mb-3">
            <label class="col-md-3 col-form-label" for="confirm"
            >Re Password</label
            >
            <b-col md="9">
              <b-form-input
                  type="password"
                  id="confirm"
                  name="confirm"
                  v-model="wizardData.confirmPass"
              />
            </b-col>
          </b-row>
        </b-col>
      </b-row>
    </tab-content>

    <tab-content
        customIcon='<i class="mdi mdi-face-man-profile fw-normal align-middle me-1"></i>
                              <span class="d-none d-sm-inline">Profile</span>'
        id="basictab2"
    >
      <b-row>
        <b-col cols="12">
          <b-row class="mb-3">
            <label class="col-md-3 col-form-label" for="name">
              First name</label
            >
            <b-col md="9">
              <b-form-input
                  type="text"
                  id="name"
                  name="name"
                  v-model="wizardData.firstName"
              />
            </b-col>
          </b-row>
          <b-row class="mb-3">
            <label class="col-md-3 col-form-label" for="surname">
              Last name</label
            >
            <b-col md="9">
              <b-form-input
                  type="text"
                  id="surname"
                  name="surname"
                  v-model="wizardData.lastName"
              />
            </b-col>
          </b-row>

          <b-row class="mb-3">
            <label class="col-md-3 col-form-label" for="email">Email</label>
            <b-col md="9">
              <b-form-input
                  type="email"
                  id="email"
                  name="email"
                  v-model="wizardData.email"
              />
            </b-col>
          </b-row>
        </b-col>
      </b-row>
    </tab-content>

    <tab-content
        customIcon='<i class="mdi mdi-checkbox-marked-circle-outline fw-normal align-middle me-1"></i>
                              <span class="d-none d-sm-inline">Finish</span>'
        id="basictab3"
    >
      <b-row>
        <b-col cols="12">
          <div class="text-center">
            <h2 class="mt-0">
              <i class="ri-check-double-line"></i>
            </h2>
            <h3 class="mt-0">Thank you !</h3>

            <p class="w-75 mb-2 mx-auto">
              Quisque nec turpis at urna dictum luctus. Suspendisse convallis
              dignissim eros at volutpat. In egestas mattis dui. Aliquam mattis
              dictum aliquet.
            </p>

            <div class="mb-3">
              <div class="d-inline-block">
                <b-form-checkbox v-model="wizardData.isAgree" id="customCheck1"
                >I agree with the Terms and Conditions
                </b-form-checkbox
                >
              </div>
            </div>
          </div>
        </b-col>
      </b-row>
    </tab-content>

    <!-- Custom button -->
    <template v-slot:footer="props">
      <div class="wizard-footer-left">
        <b-button
            variant="light"
            v-if="props.activeTabIndex > 0 && !props.isLastStep"
            @click.native="props.prevTab()"
            class="wizard-button"
        >
          <i class="ri-arrow-left-line me-1"></i> Back to Account
        </b-button>

        <b-button
            class="wizard-button"
            variant="light"
            v-if="props.isLastStep"
            @click.native="props.prevTab()"
        >
          <i class="ri-arrow-left-line me-1"></i> Back to Profile
        </b-button>
      </div>
      <div class="wizard-footer-right">
        <b-button
            variant="info"
            v-if="!props.isLastStep"
            @click.native="props.nextTab()"
            class="wizard-button"
        >
          Add More Info <i class="ri-arrow-right-line ms-1"></i>
        </b-button>

        <b-button variant="info" v-else>
          {{ props.isLastStep ? "Submit" : "Next" }}
        </b-button>
      </div>
    </template>
  </form-wizard>
</template>

<script lang="ts">
import {FormWizard, TabContent} from "vue3-form-wizard";

export default {
  components: {FormWizard, TabContent},
  props: {
    'bar': {
      type: Boolean,
      default: false
    },
  },
  data() {
    return {
      value: 33.33,
      max: 100,
      wizardData: {
        username: "Admin",
        pass: 123456789,
        confirmPass: 123456789,
        firstName: "Francis",
        lastName: "Brinkman",
        email: "cory1979@hotmail.com",
        isAgree: false,
      },
    };
  },
  methods: {
    onTabShow(prevIndex: number, currentIndex: number) {
      this.value = 33.33 * (currentIndex + 1)
    },
  },
};
</script>
