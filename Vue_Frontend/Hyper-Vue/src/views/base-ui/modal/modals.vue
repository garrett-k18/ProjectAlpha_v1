<template>
  <Layout>
    <Breadcrumb :title="title" :items="items"/>

    <b-row>
      <b-col xl="6">
        <CustomSyntax title="Bootstrap Modals">
          <template v-slot:sub-text>
            A rendered modal with header, body, and set of actions in the footer.
          </template>
          <template v-slot:preview>
            <!-- Standard modal content -->
            <b-modal id="standard-modal" v-model="standardModal" title="Modal Heading" title-class="h4" hide-footer>
              <div class="">
                <h5>Text in a modal</h5>
                <p>
                  Duis mollis, est non commodo luctus, nisi erat porttitor ligula.
                </p>
                <hr/>
                <h5>Overflowing text to show scroll behavior</h5>
                <p>
                  Cras mattis consectetur purus sit amet fermentum. Cras justo
                  odio, dapibus ac facilisis in, egestas eget quam. Morbi leo
                  risus, porta ac consectetur ac, vestibulum at eros.
                </p>
                <p>
                  Praesent commodo cursus magna, vel scelerisque nisl consectetur
                  et. Vivamus sagittis lacus vel augue laoreet rutrum faucibus
                  dolor auctor.
                </p>
                <p class="mb-0">
                  Aenean lacinia bibendum nulla sed consectetur. Praesent commodo
                  cursus magna, vel scelerisque nisl consectetur et. Donec sed
                  odio dui. Donec ullamcorper nulla non metus auctor fringilla.
                </p>
              </div>
              <div class="modal-footer">
                <b-button variant="light" @click="standardModal = !standardModal">Close</b-button>
                <b-button variant="primary">Save changes</b-button>
              </div>
            </b-modal>

            <b-modal id="bs-example-modal-lg" v-model="modalLg" title="Large modal" title-class="h4" hide-footer size="lg">
              <div class="">...</div>
            </b-modal>

            <b-modal id="bs-example-modal-sm" v-model="modalSm" title="Small modal" title-class="h4" hide-footer size="sm">
              <div class="">...</div>
            </b-modal>

            <!-- Full width modal content -->
            <b-modal id="full-width-modal" v-model="modalXl" title="Modal Heading" title-class="h4" hide-footer size="xl">

              <div class="">
                <h5>Text in a modal</h5>
                <p>
                  Duis mollis, est non commodo luctus, nisi erat porttitor ligula.
                </p>
                <hr/>
                <h5>Overflowing text to show scroll behavior</h5>
                <p>
                  Cras mattis consectetur purus sit amet fermentum. Cras justo
                  odio, dapibus ac facilisis in, egestas eget quam. Morbi leo
                  risus, porta ac consectetur ac, vestibulum at eros.
                </p>
                <p>
                  Praesent commodo cursus magna, vel scelerisque nisl consectetur
                  et. Vivamus sagittis lacus vel augue laoreet rutrum faucibus
                  dolor auctor.
                </p>
                <p class="mb-0">
                  Aenean lacinia bibendum nulla sed consectetur. Praesent commodo
                  cursus magna, vel scelerisque nisl consectetur et. Donec sed
                  odio dui. Donec ullamcorper nulla non metus auctor fringilla.
                </p>
              </div>
              <div class="modal-footer">
                <b-button variant="light" @click="modalXl = !modalXl">
                  Close
                </b-button>
                <button type="button" class="btn btn-primary">
                  Save changes
                </button>
              </div>
            </b-modal>

            <!-- Long Content Scroll Modal -->
            <b-modal id="scrollable-modal" v-model="scrollableModal" title="Modal title" title-class="h4" scrollable>
              <div class="modal-body">
                <div v-for="i in 5" :key="i">
                  <p>
                    Cras mattis consectetur purus sit amet fermentum. Cras justo
                    odio, dapibus ac facilisis in, egestas eget quam. Morbi leo
                    risus, porta ac consectetur ac, vestibulum at eros.
                  </p>
                  <p>
                    Praesent commodo cursus magna, vel scelerisque nisl
                    consectetur et. Vivamus sagittis lacus vel augue laoreet
                    rutrum faucibus dolor auctor.
                  </p>
                  <p>
                    Aenean lacinia bibendum nulla sed consectetur. Praesent
                    commodo cursus magna, vel scelerisque nisl consectetur et.
                    Donec sed odio dui. Donec ullamcorper nulla non metus auctor
                    fringilla.
                  </p>
                </div>
              </div>
              <template #modal-footer>
                <div>
                  <b-button variant="secondary" @click="scrollableModal = !scrollableModal">
                    Close
                  </b-button>
                  <b-button variant="primary"> Save changes</b-button>
                </div>
              </template>
            </b-modal>

            <div class="d-flex flex-wrap gap-2">
              <b-button variant="primary" @click="standardModal = !standardModal">Standard Modal</b-button>

              <b-button variant="info" @click="modalLg = !modalLg">Large Modal</b-button>

              <b-button variant="success" @click="modalSm = !modalSm">Small Modal</b-button>

              <b-button variant="primary" @click="modalXl = !modalXl">Full Width Modal</b-button>

              <b-button variant="secondary" @click="scrollableModal = !scrollableModal">Scrollable Modal</b-button>
            </div>

          </template>
        </CustomSyntax>

      </b-col> <!-- end col -->

      <b-col xl="6">
        <CustomSyntax title="Modal with Pages">
          <template v-slot:sub-text>
            Examples of custom modals.
          </template>
          <template v-slot:preview>

            <b-modal id="signup-modal" v-model="signupModal" hide-header hide-footer>
              <div class="auth-brand text-center mt-2 mb-4 position-relative top-0">
                <a href="/dashboard" class="logo-dark">
                  <span><img src="@/assets/images/logo-dark.png" alt="dark logo" height="22"/></span>
                </a>
                <a href="/dashboard" class="logo-light">
                  <span><img src="@/assets/images/logo.png" alt="logo" height="22"/></span>
                </a>
              </div>

              <b-form class="ps-3 pe-3" action="#">
                <b-form-group label="Name" label-for="username" class="mb-3">
                  <b-form-input type="email" id="username" required placeholder="Michael Zenaty"/>
                </b-form-group>

                <b-form-group label="Email address" label-for="emailaddress" class="mb-3">
                  <b-form-input type="email" id="emailaddress" required placeholder="john@deo.com"/>
                </b-form-group>

                <b-form-group label="Password" label-for="password" class="mb-3">
                  <b-form-input type="password" required id="password" placeholder="Enter your password"/>
                </b-form-group>

                <div class="mb-3">
                  <b-form-checkbox id="customCheck1">I accept
                    <a href="#">Terms and Conditions</a></b-form-checkbox>
                </div>

                <div class="mb-3 text-center">
                  <b-button variant="primary" type="submit">
                    Sign Up Free
                  </b-button>
                </div>
              </b-form>
            </b-modal>

            <!-- SignIn modal content -->
            <b-modal id="login-modal" v-model="loginModal" hide-header hide-footer>
              <div class="auth-brand text-center mt-2 mb-4 position-relative top-0">
                <a href="/dashboard" class="logo-dark">
                  <span><img src="@/assets/images/logo-dark.png" alt="dark logo" height="22"/></span>
                </a>
                <a href="/dashboard" class="logo-light">
                  <span><img src="@/assets/images/logo.png" alt="logo" height="22"/></span>
                </a>
              </div>

              <b-form action="#" class="ps-3 pe-3">
                <b-form-group label="Email address" label-for="emailaddress1" class="mb-3">
                  <b-form-input type="email" id="emailaddress1" required placeholder="john@deo.com"/>
                </b-form-group>

                <b-form-group label="Password" label-for="password1" class="mb-3">
                  <b-form-input type="password" required id="password1" placeholder="Enter your password"/>
                </b-form-group>

                <div class="mb-3">
                  <b-form-checkbox id="customCheck2">Remember me</b-form-checkbox>
                </div>

                <div class="mb-3 text-center">
                  <b-button variant="primary" pill class="btn rounded-pill btn-primary" type="submit">
                    Sign In
                  </b-button>
                </div>
              </b-form>
            </b-modal>

            <div class="d-flex flex-wrap gap-2">
              <b-button variant="primary" @click="signupModal = !signupModal">
                Sign Up Modal
              </b-button>

              <b-button variant="info" @click="loginModal = !loginModal">
                Log In Modal
              </b-button>
            </div>
          </template>
        </CustomSyntax>

      </b-col> <!-- end col -->
    </b-row>
    <!-- end row -->

    <b-row>
      <b-col xl="6">
        <CustomSyntax title="Modal based Alerts">
          <template v-slot:sub-text>
            Show different contexual alert messages using modal component
          </template>
          <template v-slot:preview>
            <b-modal id="success-alert-modal" v-model="successAlertModal" content-class="bg-success" hide-footer hide-header size="sm">

              <div class="modal-filled bg-success p-4">
                <div class="text-center">
                  <i class="ri-check-line h1"></i>
                  <h4 class="mt-2">Well Done!</h4>
                  <p class="mt-3">
                    Cras mattis consectetur purus sit amet fermentum. Cras justo
                    odio, dapibus ac facilisis in, egestas eget quam.
                  </p>
                  <b-button variant="light" class="my-2" @click="successAlertModal = !successAlertModal">
                    Continue
                  </b-button>
                </div>
              </div>

            </b-modal>

            <!-- Info Alert Modal -->
            <b-modal id="info-alert-modal" v-model="infoAlertModal" hide-footer hide-header size="sm">
              <div class="p-4">
                <div class="text-center">
                  <i class="ri-information-line h1 text-info"></i>
                  <h4 class="mt-2">Heads up!</h4>
                  <p class="mt-3">
                    Cras mattis consectetur purus sit amet fermentum. Cras justo
                    odio, dapibus ac facilisis in, egestas eget quam.
                  </p>
                  <b-button variant="info" class="my-2" @click="infoAlertModal = !infoAlertModal">
                    Continue
                  </b-button>
                </div>
              </div>
            </b-modal>

            <!-- Warning Alert Modal -->
            <b-modal id="warning-alert-modal" v-model="warningAlertModal" hide-footer hide-header size="sm">
              <div class="p-4">
                <div class="text-center">
                  <i class="ri-alert-line h1 text-warning"></i>
                  <h4 class="mt-2">Incorrect Information</h4>
                  <p class="mt-3">
                    Cras mattis consectetur purus sit amet fermentum. Cras justo
                    odio, dapibus ac facilisis in, egestas eget quam.
                  </p>
                  <b-button variant="warning" class="my-2" @click="warningAlertModal = !warningAlertModal">
                    Continue
                  </b-button>
                </div>
              </div>
            </b-modal>

            <!-- Danger Alert Modal -->
            <b-modal id="danger-alert-modal" v-model="dangerAlertModal" content-class="bg-danger" hide-footer hide-header size="sm">

              <div class="modal-filled bg-danger p-4">
                <div class="text-center">
                  <i class="ri-close-circle-line h1"></i>
                  <h4 class="mt-2">Oh snap!</h4>
                  <p class="mt-3">
                    Cras mattis consectetur purus sit amet fermentum. Cras justo
                    odio, dapibus ac facilisis in, egestas eget quam.
                  </p>
                  <b-button variant="light" class="my-2" @click="dangerAlertModal = !dangerAlertModal">
                    Continue
                  </b-button>
                </div>
              </div>
            </b-modal>

            <div class="d-flex flex-wrap gap-2">
              <b-button variant="success" @click="successAlertModal = !successAlertModal">
                Success Alert
              </b-button>

              <b-button variant="info" @click="infoAlertModal = !infoAlertModal">
                Info Alert
              </b-button>

              <b-button variant="warning" @click="warningAlertModal = !warningAlertModal">
                Warning Alert
              </b-button>

              <b-button variant="danger" @click="dangerAlertModal = !dangerAlertModal">
                Danger Alert
              </b-button>
            </div>
          </template>
        </CustomSyntax>

      </b-col> <!-- end col -->

      <b-col xl="6">
        <CustomSyntax title="Modal Position">
          <template v-slot:sub-text>
            Specify the position for the modal. You can display modal at top, bottom, center or right of page by
            specifying
            classes <code>modal-top</code>, <code>modal-bottom</code>, <code>modal-dialog-centered</code> and <code>modal-right</code>
            respectively.
          </template>
          <template v-slot:preview>
            <b-modal id="top-modal" v-model="topModal" hide-footer title="Modal Heading" title-class="h4">
              <div class="modal-body">
                <h5>Text in a modal</h5>
                <p>
                  Duis mollis, est non commodo luctus, nisi erat porttitor ligula.
                </p>
              </div>
              <div class="modal-footer">
                <b-button variant="light" @click="topModal = !topModal">
                  Close
                </b-button>
                <b-button variant="primary"> Save changes</b-button>
              </div>
            </b-modal>

            <!-- Right modal content -->
            <b-modal id="right-modal" v-model="rightModal" hide-footer title="Modal Heading" title-class="h4">
              <div class="modal-body">
                <div class="text-center">
                  <h4 class="mt-0">Text in a modal</h4>
                  <p>
                    Duis mollis, est non commodo luctus, nisi erat porttitor
                    ligula.
                  </p>
                  <b-button variant="danger" size="sm" @click="rightModal = !rightModal">
                    Close
                  </b-button>
                </div>
              </div>
            </b-modal>

            <!-- Bottom modal content -->
            <b-modal id="bottom-modal" v-model="bottomModal" hide-footer title="Modal Heading" title-class="h4"
                     size="sm">
              <div class="modal-body">
                <h5>Text in a modal</h5>
                <p>
                  Duis mollis, est non commodo luctus, nisi erat porttitor ligula.
                </p>
              </div>
              <div class="modal-footer">
                <b-button variant="light" @click="bottomModal = !bottomModal">
                  Close
                </b-button>
                <b-button variant="primary"> Save changes</b-button>
              </div>
            </b-modal>

            <!-- Center modal content -->
            <b-modal id="centermodal" v-model="centerModal" centered hide-footer title="Center modal" title-class="h4">
              <div class="modal-body">
                <h5>Overflowing text to show scroll behavior</h5>
                <p>
                  Cras mattis consectetur purus sit amet fermentum. Cras justo
                  odio, dapibus ac facilisis in, egestas eget quam. Morbi leo
                  risus, porta ac consectetur ac, vestibulum at eros.
                </p>
                <p>
                  Praesent commodo cursus magna, vel scelerisque nisl consectetur
                  et. Vivamus sagittis lacus vel augue laoreet rutrum faucibus
                  dolor auctor.
                </p>
              </div>
            </b-modal>

            <div class="d-flex flex-wrap gap-2">
              <b-button variant="secondary" @click="topModal = !topModal">
                Top Modal
              </b-button>

              <b-button variant="secondary" @click="bottomModal = !bottomModal">
                Bottom Modal
              </b-button>

              <b-button variant="secondary" @click="centerModal = !centerModal">
                Center modal
              </b-button>

              <b-button variant="secondary" @click="rightModal = !rightModal">
                Rightbar Modal
              </b-button>
            </div>
          </template>
        </CustomSyntax>

      </b-col> <!-- end col -->
    </b-row>
    <!-- end row -->

    <b-row>
      <b-col xl="6">
        <FillColor/>
      </b-col> <!-- end col -->

      <b-col xl="6">
        <FillClass/>
      </b-col> <!-- end col -->
    </b-row>
    <!-- end row -->

    <b-row>
      <b-col xl="6">
        <CustomSyntax title="Multiple Modal">
          <template v-slot:sub-text>
            Display a series of modals one by one to guide your users on multiple aspects or take step wise input.
          </template>
          <template v-slot:preview>
            <!-- Modal -->
            <b-modal id="multiple-one" v-model="multipleModalOne" title-class="h4" title="Modal Heading" hide-footer>
              <h5 class="mt-0">Text in a modal</h5>
              <p>
                Duis mollis, est non commodo luctus, nisi erat porttitor ligula.
              </p>
              <div class="modal-footer">
                <b-button variant="primary"
                          @click="() => {multipleModalTwo = !multipleModalTwo;multipleModalOne = !multipleModalOne; }">
                  Next
                </b-button>
              </div>
            </b-modal>

            <!-- Modal -->
            <b-modal id="multiple-two" v-model="multipleModalTwo" title-class="h4" title="Modal Heading" hide-footer>
              <h5 class="mt-0">Text in a modal</h5>
              <p>
                Duis mollis, est non commodo luctus, nisi erat porttitor ligula.
              </p>
              <div class="modal-footer">
                <b-button variant="primary" @click="multipleModalTwo = !multipleModalTwo">
                  Close
                </b-button>
              </div>
            </b-modal>

            <div class="d-flex flex-wrap gap-2">
              <!-- Multiple modal -->
              <b-button variant="primary" @click="multipleModalOne = !multipleModalOne">
                Multiple Modal
              </b-button>
            </div>
          </template>
        </CustomSyntax>

      </b-col> <!-- end col -->

      <b-col xl="6">
        <CustomSyntax title="Toggle Between Modals">
          <template v-slot:sub-text>
            Toggle between multiple modals with some clever placement of the <code>data-bs-target</code> and <code>data-bs-toggle</code>
            attributes.
          </template>
          <template v-slot:preview>
            <b-modal id="exampleModalToggle1" v-model="modalToggleOne" title-class="h5" title="Modal 1" hide-footer
                     centered>
              <div class="modal-body">
                Show a second modal and hide this one with the button below.
              </div>
              <div class="modal-footer">
                <b-button variant="primary"
                          @click=" () => { modalToggleTwo = !modalToggleTwo; modalToggleOne = !modalToggleOne; }">
                  Open second modal
                </b-button>
              </div>
            </b-modal>

            <!-- Modal -->
            <b-modal id="exampleModalToggle2" v-model="modalToggleTwo" title-class="h5" title="Modal 2" hide-footer
                     centered>
              <div class="modal-body">Hide this modal and show the first with the button below.</div>
              <div class="modal-footer">
                <b-button variant="primary"
                          @click=" () => {modalToggleTwo = !modalToggleTwo; modalToggleOne = !modalToggleOne;}">
                  Back to first
                </b-button>
              </div>
            </b-modal>

            <a class="btn btn-secondary" role="button" @click="modalToggleOne = !modalToggleOne">Open first modal</a>
          </template>
        </CustomSyntax>

      </b-col> <!-- end col -->
    </b-row>
    <!-- end row -->

    <b-row>
      <b-col xl="6">
        <CustomSyntax title="Fullscreen Modal">
          <template v-slot:sub-text>
            Another override is the option to pop up a modal that covers the user viewport, available via modifier
            classes that are placed on a <code>.modal-dialog</code>
          </template>
          <template v-slot:preview>
            <div class="hstack gap-2 flex-wrap">
              <b-button variant="primary" @click="fullScreenModal = !fullScreenModal"> Fullscreen Modal</b-button>
              <b-button variant="primary" @click="fullScreenSmModal = !fullScreenSmModal">Full Screen Below sm
              </b-button>
              <b-button variant="primary" @click="fullScreenMdModal = !fullScreenMdModal">Full Screen Below md
              </b-button>
              <b-button variant="primary" @click="fullScreenLgModal = !fullScreenLgModal">Full Screen Below lg
              </b-button>
              <b-button variant="primary" @click="fullScreenXlModal = !fullScreenXlModal">Full Screen Below xl
              </b-button>
              <b-button variant="primary" @click="fullScreenXxlModal = !fullScreenXxlModal">Full Screen Below xxl
              </b-button>
            </div>

            <b-modal id="fullscreeexampleModal" v-model="fullScreenModal" fullscreen title="Full Screen Modal"
                     title-class="h5" hide-footer>
              <div class="modal-body"> ...</div>
              <div class="modal-footer">
                <a href="javascript:void(0);" class="btn btn-light"
                   @click="fullScreenModal = !fullScreenModal">Close</a>
                <b-button variant="primary">Save Changes</b-button>
              </div>
            </b-modal>

            <!-- Modal -->
            <b-modal id="exampleModalFullscreenSm" v-model="fullScreenSmModal" title="Full screen below sm"
                     title-class="h5" hide-footer size="sm">
              <div class=""> ...</div>
              <div class="modal-footer">
                <a href="javascript:void(0);" class="btn btn-light"
                   @click="fullScreenSmModal= !fullScreenSmModal">Close</a>
                <b-button variant="primary">Save Changes</b-button>
              </div>
            </b-modal>

            <!-- Modal -->
            <b-modal id="exampleModalFullscreenMd" v-model="fullScreenMdModal" title="Full screen below md"
                     title-class="h5" hide-footer size="md">
              <div class="">...</div>
              <div class="modal-footer">
                <a href="javascript:void(0);" class="btn btn-light" @click="fullScreenMdModal = !fullScreenMdModal">Close</a>
                <b-button variant="primary">Save Changes</b-button>
              </div>
            </b-modal>

            <!-- Modal -->
            <b-modal id="exampleModalFullscreenLg" v-model="fullScreenLgModal" hide-footer size="lg"
                     title="Full screen below lg" title-class="h5">
              <div class="modal-body"> ...</div>
              <div class="modal-footer">
                <a href="javascript:void(0);" class="btn btn-light" @click="fullScreenLgModal = ! fullScreenLgModal">Close</a>
                <b-button variant="primary">Save Changes</b-button>
              </div>
            </b-modal>

            <!-- Modal -->
            <b-modal id="exampleModalFullscreenXl" v-model="fullScreenXlModal" size="xl" title="Full screen below xl"
                     tile-class="h5" hide-footer>
              <div class="modal-body">...</div>
              <div class="modal-footer">
                <a href="javascript:void(0);" variant="light" @click="fullScreenXlModal = !fullScreenXlModal">Close</a>
                <b-button class="btn btn-primary">Save Changes</b-button>
              </div>
            </b-modal>

            <!-- Modal -->
            <b-modal id="exampleModalFullscreenXxl" v-model="fullScreenXxlModal" title="Full screen below xxl"
                     title-class="h5" size="xxl" hide-footer>
              <div class="">
                ...
              </div>
              <div class="modal-footer">
                <a href="javascript:void(0);" class="btn btn-light" @click="fullScreenXxlModal = !fullScreenXxlModal">Close</a>
                <b-button variant="primary">Save Changes</b-button>
              </div>
            </b-modal>

          </template>
        </CustomSyntax>

      </b-col> <!-- end col -->

      <b-col xl="6">
        <CustomSyntax title="Static Backdrop">
          <template v-slot:sub-text>
            When backdrop is set to static, the modal will not close when clicking outside it. Click the button below to
            try it.
          </template>
          <template v-slot:preview>
            <div class="d-flex flex-wrap gap-2">
              <!-- Static Backdrop modal -->
              <b-button variant="info" @click="staticBackdropModal = !staticBackdropModal">
                Static Backdrop
              </b-button>
            </div> <!-- btn list -->

            <!-- Modal -->
            <b-modal id="staticBackdrop" v-model="staticBackdropModal" title="Modal title" title-class="h5" hide-footer>
              <div class="">
                <p class="m-0">I will not close if you click outside me. Don't even try to press escape key.</p>
              </div>
              <div class="modal-footer">
                <b-button variant="secondary" @click="staticBackdropModal = !staticBackdropModal">Close</b-button>
                <b-button variant="primary">Understood</b-button>
              </div> <!-- end modal footer -->
            </b-modal> <!-- end modal-->
          </template>
        </CustomSyntax>

      </b-col> <!-- end col -->

    </b-row>
    <!-- end row -->

    <b-row>
      <b-col xl="6">
        <CustomSyntax title="Varying Modal Content">
          <template v-slot:sub-text>
            Have a bunch of buttons that all trigger the same modal with slightly different contents? Use
            <code>event.relatedTarget</code> and <a
              href="https://developer.mozilla.org/en-US/docs/Learn/HTML/Howto/Use_data_attributes" target="_blank">HTML
            <code>data-bs-*</code>
            attributes</a> to vary the contents of the modal depending on which button was clicked.
          </template>
          <template v-slot:preview>
            <div class="hstack gap-2 flex-wrap">
              <b-button variant="primary" @click="openVaryingModal('@mdo')">Open modal for @mdo</b-button>
              <b-button variant="primary" @click="openVaryingModal('@fat')">Open modal for @fat</b-button>
              <b-button variant="primary" @click="openVaryingModal('@getbootstrap')">Open modal for @getbootstrap
              </b-button>
            </div>

            <b-modal id="exampleModal" v-model="varyingModal" title="New message" title-class="h5" hide-footer>
              <div class="modal-body">
                <b-form>
                  <b-form-group label="Recipient:" label-for="recipient-name" class="mb-3">
                    <b-form-input type="text" id="recipient-name" v-model="recipient"/>
                  </b-form-group>
                  <b-form-group label="Message:" label-for="message-text" class="mb-3">
                    <b-form-textarea class="form-control" id="message-text"></b-form-textarea>
                  </b-form-group>
                </b-form>
              </div>
              <div class="modal-footer">
                <b-button variant="secondary" @click="varyingModal = !varyingModal">Close</b-button>
                <b-button variant="primary">Send message</b-button>
              </div>
            </b-modal>
          </template>
        </CustomSyntax>

      </b-col> <!-- end col -->
    </b-row>
    <!-- end row -->

  </Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";
import CustomSyntax from "@/components/custom/custom-syntax.vue";
import FillClass from "@/views/base-ui/modal/fill-class.vue";
import FillColor from "@/views/base-ui/modal/fill-color.vue";

export default {
  props: ['coloredHeaderModal'],
  components: {Layout, CustomSyntax, Breadcrumb, FillClass, FillColor},
  data() {
    return {
      title: 'Modals',
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
          text: 'Modals',
          active: true,
        },
      ],

      standardModal: false,
      modalLg: false,
      modalSm: false,
      modalXl: false,
      scrollableModal: false,
      signupModal: false,
      loginModal: false,
      successAlertModal: false,
      infoAlertModal: false,
      warningAlertModal: false,
      dangerAlertModal: false,
      topModal: false,
      rightModal: false,
      bottomModal: false,
      centerModal: false,

      multipleModalOne: false,
      multipleModalTwo: false,

      modalToggleOne: false,
      modalToggleTwo: false,

      fullScreenModal: false,
      fullScreenSmModal: false,
      fullScreenMdModal: false,
      fullScreenLgModal: false,
      fullScreenXlModal: false,
      fullScreenXxlModal: false,

      staticBackdropModal: false,
      varyingModal: false,
      recipient: "",

    };
  },
  methods: {
    openVaryingModal(recipient: string) {
      this.varyingModal = true;
      this.recipient = recipient;
    }
  },
}
</script>
