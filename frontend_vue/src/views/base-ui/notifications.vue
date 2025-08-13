<template>
<Layout>
    <Breadcrumb :title="title" :items="items" />

    <b-row>
        <b-col cols="12">
            <CustomSyntax title="Bootstrap Toasts">
                <template v-slot:sub-text>
                    Push notifications to your visitors with a toast, a
                    lightweight and easily customizable alert message.
                </template>
                <template v-slot:preview>
                    <b-row>
                        <b-col md="6">
                            <h5 class="mb-2">Basic</h5>
                            <p class="text-muted font-14">Toasts are as flexible as you need and
                                have very little required markup. At a minimum, we
                                require a single element to contain your “toasted” content and
                                strongly encourage a dismiss button.</p>
                            <div class="p-3">

                                <div class="toast fade show" role="alert" id="basic-toast">
                                    <div class="toast-header">
                                        <img src="@/assets/images/logo-dark-sm.png" alt="brand-logo" height="16" class="me-1" />
                                        <strong class="me-auto">Hyper</strong>
                                        <small>11 mins ago</small>
                                        <button type="button" class="ms-2 btn-close" @click="closeToast('basic-toast')"></button>
                                    </div>
                                    <div class="toast-body">
                                        Hello, world! This is a toast message.
                                    </div>
                                </div>
                                <!--end toast-->

                            </div>
                        </b-col> <!-- end col-->
                        <b-col md="6">
                            <h5 class="mb-2">Translucent</h5>
                            <p class="text-muted font-14">Toasts are slightly translucent, too,
                                so they blend over whatever they might appear over.
                                For browsers that support the backdrop-filter CSS property,
                                we’ll also attempt to blur the elements under a toast.</p>

                            <div class="p-3 bg-light">
                                <div class="toast fade show" role="alert" id="translucent-toast">
                                    <div class="toast-header">
                                        <img src="@/assets/images/logo-dark-sm.png" alt="brand-logo" height="16" class="me-1" />
                                        <strong class="me-auto">Hyper</strong>
                                        <small>11 mins ago</small>
                                        <button type="button" class="ms-2 btn-close"   @click="closeToast('translucent-toast')"></button>
                                    </div>
                                    <div class="toast-body">
                                        Hello, world! This is a toast message.
                                    </div>
                                </div>
                                <!--end toast-->
                            </div>
                        </b-col> <!-- end col-->
                    </b-row>
                    <!-- end row-->

                    <b-row>
                        <b-col md="6" class="mt-4">
                            <h5 class="mb-2">Stacking</h5>
                            <p class="text-muted font-14">When you have multiple toasts, we
                                default to vertiaclly stacking them in a readable manner.</p>
                            <div class="p-3">
                                <div aria-live="polite" aria-atomic="true" style="position: relative; min-height: 200px;">
                                    <!-- Position it -->
                                    <div class="toast-container" style="position: absolute; top: 0; right: 0;">

                                        <!-- Then put toasts within -->
                                        <div class="toast fade show" role="alert"    id="stacking-toast-1">
                                            <div class="toast-header">
                                                <img src="@/assets/images/logo-dark-sm.png" alt="brand-logo" height="16" class="me-1" />
                                                <strong class="me-auto">Hyper</strong>
                                                <small class="text-muted">just now</small>
                                                <button type="button" class="ms-2 btn-close"    @click="closeToast('stacking-toast-1')"></button>
                                            </div>
                                            <div class="toast-body">
                                                See? Just like this.
                                            </div>
                                        </div>
                                        <!--end toast-->

                                        <div class="toast fade show" role="alert"   id="stacking-toast-2">
                                            <div class="toast-header">
                                                <img src="@/assets/images/logo-dark-sm.png" alt="brand-logo" height="16" class="me-1" />
                                                <strong class="me-auto">Hyper</strong>
                                                <small class="text-muted">2 seconds ago</small>
                                                <button type="button" class="ms-2 btn-close"  @click="closeToast('stacking-toast-2')"></button>
                                            </div>
                                            <div class="toast-body">
                                                Heads up, toasts will stack automatically
                                            </div>
                                        </div>
                                        <!--end toast-->
                                    </div>
                                </div>
                            </div>
                        </b-col> <!-- end col-->
                        <b-col md="6" class="mt-4">
                            <h5 class="mb-2">Placement</h5>
                            <p class="text-muted font-14">Place toasts with custom CSS as you
                                need them. The top right is often used for
                                notifications, as is the top middle. If you’re only ever going
                                to show one toast at a time, put the positioning
                                styles right on the <code>.toast</code>.</p>
                            <div class="p-3">
                                <div aria-live="polite" aria-atomic="true" class="d-flex justify-content-center align-items-center" style="min-height: 200px;">

                                    <!-- Then put toasts within -->
                                    <div class="toast fade show" role="alert"  id="placement-toast">
                                        <div class="toast-header">
                                            <img src="@/assets/images/logo-dark-sm.png" alt="brand-logo" height="16" class="me-1" />
                                            <strong class="me-auto">Hyper</strong>
                                            <small>11 mins ago</small>
                                            <button type="button" class="ms-2 btn-close"  @click="closeToast('placement-toast')"></button>
                                        </div>
                                        <div class="toast-body">
                                            Hello, world! This is a toast message.
                                        </div>
                                    </div>
                                    <!--end toast-->
                                </div>
                            </div>
                        </b-col> <!-- end col-->
                    </b-row>
                    <!-- end row-->
                </template>
            </CustomSyntax>

        </b-col> <!-- end col-->
    </b-row><!-- end row-->

    <b-row>
        <b-col lg="6">
            <CustomSyntax title="Custom content">
                <template v-slot:sub-text>
                    Alternatively, you can also add additional controls
                    and components to toasts.
                </template>
                <template v-slot:preview>
                    <div class="toast show align-items-center mb-4" role="alert"   id="custom-1">
                        <div class="d-flex">
                            <div class="toast-body">
                                Hello, world! This is a toast message.
                            </div>
                            <button type="button" class="btn-close me-2 m-auto"   @click="closeToast('custom-1')"></button>
                        </div>
                    </div>

                    <div class="toast show align-items-center text-white bg-primary border-0 mb-4" role="alert"   id="custom-2">
                        <div class="d-flex">
                            <div class="toast-body">
                                Hello, world! This is a toast message.
                            </div>
                            <button type="button" class="btn-close btn-close-white me-2 m-auto" @click="closeToast('custom-2')"></button>
                        </div>
                    </div>

                    <div class="toast show mb-4" role="alert" id="custom-3">
                        <div class="toast-body">
                            Hello, world! This is a toast message.
                            <div class="mt-2 pt-2 border-top">
                                <button type="button" class="btn btn-primary btn-sm">Take
                                    action</button>
                                <button type="button" class="btn btn-secondary btn-sm"  @click="closeToast('custom-3')">Close</button>
                            </div>
                        </div>
                    </div>

                    <div class="toast bg-primary show" role="alert" id="custom-4">
                        <div class="toast-body text-white">
                            Hello, world! This is a toast message.
                            <div class="mt-2 pt-2 border-top">
                                <button type="button" class="btn btn-light btn-sm">Take
                                    action</button>
                                <button type="button" class="btn btn-secondary btn-sm"  @click="closeToast('custom-4')">Close</button>
                            </div>
                        </div>
                    </div>
                </template>
            </CustomSyntax>

        </b-col> <!-- end col-->

        <b-col lg="6">
            <CustomSyntax title="Placement">
                <template v-slot:sub-text>
                    Place toasts with custom CSS as you need them. The top
                    right is often used for notifications, as is the top middle. If you’re only ever
                    going to show one toast at a time, put the positioning styles right on the
                    <code>.toast</code>.
                </template>
                <template v-slot:preview>
                    <form>
                        <div class="mb-3">
                            <label for="selectToastPlacement">Toast placement</label>
                          <b-form-select
                              v-model="selected"
                              :options="options"
                              class="form-select mt-2"
                              id="selectToastPlacement"
                          >
                          </b-form-select>
                        </div>
                    </form>
                    <div aria-live="polite" aria-atomic="true" class="bg-light position-relative bd-example-toasts" style="min-height:294px">
                        <div class="toast-container position-absolute p-3" id="toastPlacement"   :class="selected">
                            <div class="toast show">
                                <div class="toast-header">
                                    <img src="@/assets/images/logo-dark-sm.png" alt="brand-logo" height="16" class="me-1" />
                                    <strong class="me-auto">Hyper</strong>
                                    <small>11 mins ago</small>
                                </div>
                                <div class="toast-body">
                                    Hello, world! This is a toast message.
                                </div>
                            </div>
                        </div>
                    </div>
                </template>
            </CustomSyntax>

        </b-col> <!-- end col-->
    </b-row><!-- end row-->

    <b-row>
        <b-col cols="12">
            <CustomSyntax title="Jquery Toast">
                <template v-slot:sub-text>
                    Toasts based notifications can be used to to show
                    important alerts or information to users.
                </template>
                <template v-slot:preview>
                    <b-row>
                        <b-col md="3" sm="6">
                            <div class="text-center p-1 pb-3 p-sm-3">
                                <p>Info Example</p>
                                <b-button variant="info" size="sm" id="toastr-one" >Click me</b-button>
                            </div>
                        </b-col> <!-- end col-->
                        <b-col md="3" sm="6">
                            <div class="text-center p-1 pb-3 p-sm-3">
                                <p>Warning Example</p>
                              <b-button variant="warning" size="sm" id="toastr-two">
                                Click me
                              </b-button>
                            </div>
                        </b-col> <!-- end col-->
                        <b-col md="3" sm="6">
                            <div class="text-center p-1 pb-3 p-sm-3">
                                <p>Success Example</p>
                              <b-button variant="success" size="sm" id="toastr-three">
                                Click me
                              </b-button>
                            </div>
                        </b-col> <!-- end col-->
                        <b-col md="3" sm="6">
                            <div class="text-center p-1 pb-3 p-sm-3">
                                <p>Danger Example</p>
                              <b-button variant="danger" size="sm" id="toastr-four">
                                Click me
                              </b-button>
                            </div>
                        </b-col> <!-- end col-->
                    </b-row>
                    <!-- end row-->

                    <b-row>
                        <b-col md="3" sm="6">
                            <div class="text-center p-1 pb-3 p-sm-3">
                                <p>The text can be an array</p>
                              <b-button variant="light" size="sm" id="toastr-five">
                                Click me
                              </b-button>
                            </div>
                        </b-col> <!-- end col-->
                        <b-col md="3" sm="6">
                            <div class="text-center p-1 pb-3 p-sm-3">
                                <p>Put some HTML in the text</p>
                              <b-button variant="light" size="sm" id="toastr-six">
                                Click me
                              </b-button>
                            </div>
                        </b-col> <!-- end col-->
                        <b-col md="3" sm="6">
                            <div class="text-center p-1 pb-3 p-sm-3">
                                <p>Making them sticky</p>
                              <b-button variant="light" size="sm" id="toastr-seven">
                                Click me
                              </b-button>
                            </div>
                        </b-col> <!-- end col-->
                        <b-col md="3" sm="6">
                            <div class="text-center p-1 pb-3 p-sm-3">
                                <p>Fade transitions</p>
                              <b-button variant="light" size="sm" id="toastr-eight">
                                Click me
                              </b-button>
                            </div>
                        </b-col> <!-- end col-->
                    </b-row>
                    <!-- end row-->

                </template>
            </CustomSyntax>

        </b-col> <!-- end col-->
    </b-row>
    <!-- end row-->

</Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";
import CustomSyntax from "@/components/custom/custom-syntax.vue";

import 'jquery-toast-plugin'
export default {
    components: { Layout, CustomSyntax, Breadcrumb },
  data(){
      return{
        title: 'Notifications',
        items: [
          {
            text: 'Hyper',
            href: '/',
          },
          {
            text: 'Base UI',
            href: '/',
          },
          {
            text: 'Notifications',
            active: true,
          },
        ],

        selected: null,
        options: [
          { value: null, text: "Select a position..." },
          { value: "top-0 start-0", text: "Top left" },
          { value: "top-0 start-50 translate-middle-x", text: "Top center" },
          { value: "top-0 end-0", text: "Top right" },
          { value: "top-50 start-0 translate-middle-y", text: "Middle left" },
          { value: "top-50 start-50 translate-middle", text: "Middle center" },
          { value: "top-50 end-0 translate-middle-y", text: "Middle right" },
          { value: "bottom-0 start-0", text: "Bottom left" },
          {
            value: "bottom-0 start-50 translate-middle-x",
            text: "Bottom center",
          },
          { value: "bottom-0 end-0", text: "Bottom right" },
        ],
      }
  },
  mounted() {

    setInterval(() => {
      document.getElementById("basic-toast")?.classList.remove("show");
    }, 6000);
    setInterval(() => {
      document.getElementById("translucent-toast")?.classList.remove("show");
    }, 10000);

    let NotificationApp = function () {};

    NotificationApp.prototype.send = function (
        heading: any,
        body: any,
        position: any,
        loaderBgColor: any,
        icon: any,
        hideAfter: any,
        stack: any,
        showHideTransition: any
    ) {
      // default
      if (!hideAfter) hideAfter = 30000;
      if (!stack) stack = 1;

      let options = {
        heading: heading,
        text: body,
        position: position,
        loaderBg: loaderBgColor,
        icon: icon,
        hideAfter: hideAfter,
        stack: stack,
        showHideTransition: ''
      };

      if (showHideTransition) options.showHideTransition = showHideTransition;
      else options.showHideTransition = "fade";

      $.toast().reset("all");
      $.toast(options);
    };

    ($.NotificationApp = new NotificationApp()),
        ($.NotificationApp.Constructor = NotificationApp);

    $("#toastr-one").on('click', function (e) {
      $.NotificationApp.send("Heads up!", "This alert needs your attention, but it is not super important.", 'top-right', 'rgba(0,0,0,0.2)', 'info');
    });

    $("#toastr-two").on('click', function (e) {
      $.NotificationApp.send("Heads up!", "Check below fields please.", 'top-center', 'rgba(0,0,0,0.2)', 'warning');
    });

    $("#toastr-three").on('click', function (e) {
      $.NotificationApp.send("Well Done!", "You successfully read this important alert message", 'bottom-right', 'rgba(0,0,0,0.2)', 'success');
    });

    $("#toastr-four").on('click', function (e) {
      $.NotificationApp.send("Oh snap!", "Change a few things up and try submitting again.", 'bottom-left', 'rgba(0,0,0,0.2)', 'error');
    });

    $("#toastr-five").on('click', function (e) {
      $.NotificationApp.send("How to contribute?", ['Fork the repository', 'Improve/extend the functionality', 'Create a pull request'], 'top-right', 'rgba(0,0,0,0.2)', 'info');
    });

    $("#toastr-six").on('click', function (e) {
      $.NotificationApp.send("Can I add <em>icons</em>?", "Yes! check this <a href='https://github.com/kamranahmedse/jquery-toast-plugin/commits/master'>update</a>.", 'top-right', 'rgba(0,0,0,0.2)', 'info', false);
    });

    $("#toastr-seven").on('click', function (e) {
      $.NotificationApp.send("", "Set the `hideAfter` property to false and the toast will become sticky.", 'top-right', 'rgba(0,0,0,0.2)', 'success');
    });

    $("#toastr-eight").on('click', function (e) {
      $.NotificationApp.send("", "Set the `showHideTransition` property to fade|plain|slide to achieve different transitions.", 'top-right', 'rgba(0,0,0,0.2)', 'info', 3000, 1, 'fade');
    });
  },
  methods: {
    closeToast(id: string) {
      document.getElementById(id)?.classList.remove("show");
    },
  },
}
</script>
