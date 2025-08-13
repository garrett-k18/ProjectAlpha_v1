<template>
  <Layout>
    <Breadcrumb :title="title" :items="items" />

    <b-row>
      <b-col lg="6">
        <div class="card">
          <div class="card-body">
            <h4 class="header-title">Custom styles</h4>
            <p class="text-muted fs-14">
              Custom feedback styles apply custom colors, borders, focus styles,
              and background icons to better communicate feedback. Background
              icons for <code>&lt;select&gt;</code>s are only available with
              <code>.form-select</code>, and not <code>.form-control</code>.
            </p>

            <b-form class="needs-validation">
              <b-form-group
                  label="First name"
                  label-for="validationCustom01"
                  class="mb-3"
              >
                <b-form-input
                    type="text"
                    id="validationCustom01"
                    placeholder="First name"
                    v-model="first_name"
                    :state="validateFirstName"
                    required
                />
                <b-form-valid-feedback :state="validateFirstName"
                >Looks good!</b-form-valid-feedback
                >
              </b-form-group>
              <b-form-group
                  label="Last name"
                  label-for="validationCustom02"
                  class="mb-3"
              >
                <b-form-input
                    type="text"
                    id="validationCustom02"
                    placeholder="Last name"
                    v-model="last_name"
                    :state="validateLastName"
                    required
                />
                <b-form-valid-feedback :state="validateLastName"
                >Looks good!</b-form-valid-feedback
                >
              </b-form-group>
              <b-form-group
                  label="Username"
                  label-for="validationCustomUsername"
                  class="mb-3"
              >
                <b-input-group prepend="@">
                  <b-form-input
                      type="text"
                      id="validationCustomUsername"
                      v-model="username"
                      :state="validateUserName"
                      required
                  />
                  <b-form-invalid-feedback :state="validateUserName"
                  >Please choose a username.</b-form-invalid-feedback
                  >
                </b-input-group>
              </b-form-group>
              <b-form-group
                  label="City"
                  label-for="validationCustom03"
                  class="mb-3"
              >
                <b-form-input
                    type="text"
                    id="validationCustom03"
                    placeholder="City"
                    v-model="city"
                    :state="validateCity"
                    required
                />
                <b-form-invalid-feedback :state="validateCity"
                >Please provide a valid city.</b-form-invalid-feedback
                >
              </b-form-group>
              <b-form-group
                  label="State"
                  label-for="validationCustom04"
                  class="mb-3"
              >
                <b-form-input
                    type="text"
                    id="validationCustom04"
                    placeholder="State"
                    v-model="state"
                    :state="validateState"
                    required
                />
                <b-form-invalid-feedback :state="validateState">
                  Please provide a valid state.
                </b-form-invalid-feedback>
              </b-form-group>
              <b-form-group
                  label="Zip"
                  label-for="validationCustom05"
                  class="mb-3"
              >
                <b-form-input
                    type="text"
                    id="validationCustom05"
                    placeholder="Zip"
                    v-model="zip"
                    :state="validateZip"
                    required
                />
                <b-form-invalid-feedback :state="validateZip"
                >Please provide a valid zip.</b-form-invalid-feedback
                >
              </b-form-group>
              <div class="mb-3">
                <b-form-checkbox
                    id="invalidCheck"
                    v-model="selected"
                    :state="validateAgree"
                    required
                >Agree to terms and conditions</b-form-checkbox
                >

                <b-form-invalid-feedback :state="validateAgree">
                  You must agree before submitting.
                </b-form-invalid-feedback>
              </div>
              <b-button variant="primary" type="submit">Submit form</b-button>
            </b-form>
          </div>
        </div>
      </b-col>

      <b-col lg="6">
        <div class="card">
          <div class="card-body">
            <h4 class="header-title">Tooltips</h4>
            <p class="text-muted fs-14">
              If your form layout allows it, you can swap the
              <code>.{valid|invalid}-feedback</code> classes for
              <code>.{valid|invalid}-tooltip</code> classes to display
              validation feedback in a styled tooltip. Be sure to have a parent
              with <code>position: relative</code>
              on it for tooltip positioning. In the example below, our column
              classes have this already, but your project may require an
              alternative setup.
            </p>

            <form class="needs-validation" novalidate>
              <b-form-group
                  label="First name"
                  label-for="validationTooltip01"
                  class="position-relative mb-3"
              >
                <b-form-input
                    type="text"
                    id="validationTooltip01"
                    placeholder="First name"
                    v-model="first_name1"
                    :state="validateFirstName1"
                    required
                />
                <b-form-valid-feedback
                    :state="validateFirstName1"
                    class="valid-tooltip"
                >Looks good!</b-form-valid-feedback
                >
                <b-form-invalid-feedback
                    :state="validateFirstName1"
                    class="invalid-tooltip"
                >Please enter first name.</b-form-invalid-feedback
                >
              </b-form-group>
              <b-form-group
                  label="Last name"
                  label-for="validationTooltip02"
                  class="position-relative mb-3"
              >
                <b-form-input
                    type="text"
                    id="validationTooltip02"
                    placeholder="Last name"
                    v-model="last_name1"
                    :state="validateLastName1"
                    required
                />
                <b-form-valid-feedback
                    :state="validateLastName1"
                    class="valid-tooltip"
                >Looks good!</b-form-valid-feedback
                >
                <b-form-invalid-feedback
                    :state="validateLastName1"
                    class="invalid-tooltip"
                >Please enter last name.</b-form-invalid-feedback
                >
              </b-form-group>
              <b-form-group
                  label="Username"
                  label-for="validationTooltipUsername"
                  class="position-relative mb-3"
              >
                <b-input-group prepend="@">
                  <b-form-input
                      type="text"
                      id="validationTooltipUsername"
                      placeholder="Username"
                      aria-describedby="validationTooltipUsernamePrepend"
                      required
                      v-model="username1"
                      :state="validateUserName1"
                  />
                  <b-form-invalid-feedback
                      :state="validateUserName1"
                      class="invalid-tooltip"
                  >
                    Please choose a unique and valid username.
                  </b-form-invalid-feedback>
                </b-input-group>
              </b-form-group>
              <b-form-group
                  label="City"
                  label-for="validationTooltip03"
                  class="position-relative mb-3"
              >
                <b-form-input
                    type="text"
                    id="validationTooltip03"
                    placeholder="City"
                    required
                    v-model="city1"
                    :state="validateCity1"
                />
                <b-form-invalid-feedback
                    :state="validateCity1"
                    class="invalid-tooltip"
                >Please provide a valid city.</b-form-invalid-feedback
                >
              </b-form-group>
              <b-form-group
                  label="State"
                  label-for="validationTooltip04"
                  class="position-relative mb-3"
              >
                <b-form-input
                    type="text"
                    id="validationTooltip04"
                    placeholder="State"
                    required
                    v-model="state1"
                    :state="validateState1"
                />
                <b-form-invalid-feedback
                    :state="validateState1"
                    class="invalid-tooltip"
                >Please provide a valid state.</b-form-invalid-feedback
                >
              </b-form-group>
              <b-form-group
                  label="Zip"
                  label-for="validationTooltip05"
                  class="position-relative mb-3"
              >
                <b-form-input
                    type="text"
                    class="form-control"
                    id="validationTooltip05"
                    placeholder="Zip"
                    required
                    v-model="zip1"
                    :state="validateZip1"
                />
                <b-form-invalid-feedback
                    :state="validateZip1"
                    class="invalid-tooltip"
                >Please provide a valid zip.</b-form-invalid-feedback
                >
              </b-form-group>
              <b-button variant="primary" type="submit">Submit form</b-button>
            </form>
          </div>
        </div>
      </b-col>
    </b-row>
  </Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";
export default {
  components: { Layout, Breadcrumb },
  data() {
    return {
      title: 'Form Validation',
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
          text: 'Form Validation',
          active: true,
        },
      ],

      first_name: "Mark",
      last_name: "Otto",
      username: "",
      city: "",
      state: "",
      zip: "",
      selected: false,
      first_name1: "Mark",
      last_name1: "Otto",
      username1: "",
      city1: "",
      state1: "",
      zip1: "",
      selected1: false,
    };
  },
  computed: {
    validateFirstName() {
      return this.first_name.length >= 2 && this.first_name.length < 15;
    },
    validateLastName() {
      return this.last_name.length >= 2 && this.last_name.length < 15;
    },
    validateUserName() {
      return this.username.length >= 2 && this.username.length < 15;
    },
    validateCity() {
      return this.city.length >= 2 && this.city.length < 15;
    },
    validateState() {
      return this.state.length >= 2 && this.state.length < 15;
    },
    validateZip() {
      return this.zip.length > 0 && this.zip.length <= 6;
    },
    validateAgree() {
      return this.selected == true;
    },
    validateFirstName1() {
      return this.first_name1.length >= 2 && this.first_name1.length < 15;
    },
    validateLastName1() {
      return this.last_name1.length >= 2 && this.last_name1.length < 15;
    },
    validateUserName1() {
      return this.username1.length >= 2 && this.username1.length < 15;
    },
    validateCity1() {
      return this.city1.length >= 2 && this.city1.length < 15;
    },
    validateState1() {
      return this.state1.length >= 2 && this.state1.length < 15;
    },
    validateZip1() {
      return this.zip1.length > 0 && this.zip1.length <= 6;
    },
    validateAgree1() {
      return this.selected1 == true;
    },
  },

};
</script>
