<template>
  <Layout>
    <Breadcrumb :title="title" :items="items" />
    <b-row>
      <b-col cols="12">
        <div class="card">
          <div class="card-body">
            <b-tabs pills fill content-class="mt-3">
              <b-tab active>
                <template #title>
                  <i class="mdi mdi-account-circle font-18"></i>
                  <span class="d-none d-lg-block">Billing Info</span>
                </template>
                <b-row>
                  <b-col lg="8">
                    <h4 class="mt-2">Billing information</h4>

                    <p class="text-muted mb-4">
                      Fill the form below in order to send you the order's
                      invoice.
                    </p>

                    <b-form>
                      <b-row>
                        <b-col md="6">
                          <div class="mb-3">
                            <label for="billing-first-name" class="form-label"
                              >First Name</label
                            >
                            <input
                              class="form-control"
                              type="text"
                              placeholder="Enter your first name"
                              id="billing-first-name"
                            />
                          </div>
                        </b-col>
                        <b-col md="6">
                          <div class="mb-3">
                            <label for="billing-last-name" class="form-label"
                              >Last Name</label
                            >
                            <input
                              class="form-control"
                              type="text"
                              placeholder="Enter your last name"
                              id="billing-last-name"
                            />
                          </div>
                        </b-col>
                      </b-row>
                      <!-- end row -->
                      <b-row>
                        <b-col md="6">
                          <div class="mb-3">
                            <label
                              for="billing-email-address"
                              class="form-label"
                              >Email Address
                              <span class="text-danger">*</span></label
                            >
                            <input
                              class="form-control"
                              type="email"
                              placeholder="Enter your email"
                              id="billing-email-address"
                            />
                          </div>
                        </b-col>
                        <b-col md="6">
                          <div class="mb-3">
                            <label for="billing-phone" class="form-label"
                              >Phone <span class="text-danger">*</span></label
                            >
                            <input
                              class="form-control"
                              type="text"
                              placeholder="(xx) xxx xxxx xxx"
                              id="billing-phone"
                            />
                          </div>
                        </b-col>
                      </b-row>
                      <!-- end row -->
                      <b-row>
                        <b-col cols="12">
                          <div class="mb-3">
                            <label for="billing-address" class="form-label"
                              >Address</label
                            >
                            <input
                              class="form-control"
                              type="text"
                              placeholder="Enter full address"
                              id="billing-address"
                            />
                          </div>
                        </b-col>
                      </b-row>
                      <!-- end row -->
                      <b-row>
                        <b-col md="4">
                          <div class="mb-3">
                            <label for="billing-town-city" class="form-label"
                              >Town / City</label
                            >
                            <input
                              class="form-control"
                              type="text"
                              placeholder="Enter your city name"
                              id="billing-town-city"
                            />
                          </div>
                        </b-col>
                        <b-col md="4">
                          <div class="mb-3">
                            <label for="billing-state" class="form-label"
                              >State</label
                            >
                            <input
                              class="form-control"
                              type="text"
                              placeholder="Enter your state"
                              id="billing-state"
                            />
                          </div>
                        </b-col>
                        <b-col md="4">
                          <div class="mb-3">
                            <label for="billing-zip-postal" class="form-label"
                              >Zip / Postal Code</label
                            >
                            <input
                              class="form-control"
                              type="text"
                              placeholder="Enter your zip code"
                              id="billing-zip-postal"
                            />
                          </div>
                        </b-col>
                      </b-row>
                      <!-- end row -->
                      <b-row>
                        <b-col cols="12">
                          <div class="mb-3">
                            <label class="form-label">Country</label>
                            <VueMultiselect
                              v-model="value"
                              :options="options"
                              :searchable="true"
                            />
                          </div>
                        </b-col>
                      </b-row>
                      <!-- end row -->

                      <b-row>
                        <b-col cols="12">
                          <div class="mb-3">
                            <div class="form-check">
                              <input
                                type="checkbox"
                                class="form-check-input"
                                id="customCheck2"
                              />
                              <label class="form-check-label" for="customCheck2"
                                >Ship to different address ?</label
                              >
                            </div>
                          </div>

                          <div class="mb-3 mt-3">
                            <label for="example-textarea" class="form-label"
                              >Order Notes:</label
                            >
                            <textarea
                              class="form-control"
                              id="example-textarea"
                              rows="3"
                              placeholder="Write some note.."
                            ></textarea>
                          </div>
                        </b-col>
                      </b-row>
                      <!-- end row -->

                      <b-row class="mt-4">
                        <b-col sm="6">
                          <router-link
                            to="/apps/ecommerce/shopping-cart"
                            class="btn text-muted d-none d-sm-inline-block btn-link fw-semibold"
                          >
                            <i class="mdi mdi-arrow-left"></i> Back to Shopping
                            Cart
                          </router-link>
                        </b-col>
                        <!-- end col -->
                        <b-col sm="6">
                          <div class="text-sm-end">
                            <router-link
                              to="/apps/ecommerce/checkout"
                              class="btn btn-danger"
                            >
                              <i class="mdi mdi-truck-fast me-1"></i> Proceed to
                              Shipping
                            </router-link>
                          </div>
                        </b-col>
                        <!-- end col -->
                      </b-row>
                      <!-- end row -->
                    </b-form>
                  </b-col>
                  <b-col lg="4">
                    <div class="border p-3 mt-4 mt-lg-0 rounded">
                      <h4 class="header-title mb-3">Order Summary</h4>

                      <div class="table-responsive">
                        <table class="table table-nowrap table-centered mb-0">
                          <tbody>
                            <tr>
                              <td>
                                <img
                                  src="@/assets/images/products/product-1.jpg"
                                  alt="contact-img"
                                  title="contact-img"
                                  class="rounded me-2"
                                  height="48"
                                />
                                <p class="m-0 d-inline-block align-middle">
                                  <router-link
                                    to="/apps/ecommerce/products-details"
                                    class="text-body fw-semibold"
                                    >Amazing Modern Chair
                                  </router-link>
                                  <br />
                                  <small>5 x $148.66</small>
                                </p>
                              </td>
                              <td class="text-end">$743.30</td>
                            </tr>
                            <tr>
                              <td>
                                <img
                                  src="@/assets/images/products/product-2.jpg"
                                  alt="contact-img"
                                  title="contact-img"
                                  class="rounded me-2"
                                  height="48"
                                />
                                <p class="m-0 d-inline-block align-middle">
                                  <router-link
                                    to="/apps/ecommerce/products-details"
                                    class="text-body fw-semibold"
                                  >
                                    Designer Awesome Chair
                                  </router-link>
                                  <br />
                                  <small>2 x $99.00</small>
                                </p>
                              </td>
                              <td class="text-end">$198.00</td>
                            </tr>
                            <tr>
                              <td>
                                <img
                                  src="@/assets/images/products/product-3.jpg"
                                  alt="contact-img"
                                  title="contact-img"
                                  class="rounded me-2"
                                  height="48"
                                />
                                <p class="m-0 d-inline-block align-middle">
                                  <router-link
                                    to="/apps/ecommerce/products-details"
                                    class="text-body fw-semibold"
                                    >Biblio Plastic Armchair
                                  </router-link>
                                  <br />
                                  <small>1 x $129.99</small>
                                </p>
                              </td>
                              <td class="text-end">$129.99</td>
                            </tr>
                            <tr class="text-end">
                              <td>
                                <h6 class="m-0">Sub Total:</h6>
                              </td>
                              <td class="text-end">$1071.29</td>
                            </tr>
                            <tr class="text-end">
                              <td>
                                <h6 class="m-0">Shipping:</h6>
                              </td>
                              <td class="text-end">FREE</td>
                            </tr>
                            <tr class="text-end">
                              <td>
                                <h5 class="m-0">Total:</h5>
                              </td>
                              <td class="text-end fw-semibold">$1071.29</td>
                            </tr>
                          </tbody>
                        </table>
                      </div>
                      <!-- end table-responsive -->
                    </div>
                    <!-- end .border-->
                  </b-col>
                  <!-- end col -->
                </b-row>
                <!-- end row-->
              </b-tab>

              <b-tab>
                <template #title>
                  <i class="mdi mdi-truck-fast font-18"></i>
                  <span class="d-none d-lg-block">Shipping Info</span>
                </template>
                <b-row>
                  <b-col lg="8">
                    <h4 class="mt-2">Saved Address</h4>

                    <p class="text-muted mb-3">
                      Fill the form below in order to send you the order's
                      invoice.
                    </p>

                    <b-row>
                      <b-col md="6">
                        <div class="border p-3 rounded mb-3 mb-md-0">
                          <address class="mb-0 address-lg">
                            <div class="form-check">
                              <input
                                type="radio"
                                id="customRadio1"
                                name="customRadio"
                                class="form-check-input"
                                checked
                              />
                              <label
                                class="form-check-label font-16 fw-bold"
                                for="customRadio1"
                                >Home</label
                              >
                            </div>
                            <br />
                            <span class="fw-semibold">Stanley Jones</span>
                            <br />
                            795 Folsom Ave, Suite 600<br />
                            San Francisco, CA 94107<br />
                            <abbr title="Phone">P:</abbr> (123) 456-7890 <br />
                          </address>
                        </div>
                      </b-col>
                      <b-col md="6">
                        <div class="border p-3 rounded">
                          <address class="mb-0 address-lg">
                            <div class="form-check">
                              <input
                                type="radio"
                                id="customRadio2"
                                name="customRadio"
                                class="form-check-input"
                              />
                              <label
                                class="form-check-label font-16 fw-bold"
                                for="customRadio2"
                                >Office</label
                              >
                            </div>
                            <br />
                            <span class="fw-semibold">Stanley Jones</span>
                            <br />
                            795 Folsom Ave, Suite 600<br />
                            San Francisco, CA 94107<br />
                            <abbr title="Phone">P:</abbr> (123) 456-7890 <br />
                          </address>
                        </div>
                      </b-col>
                    </b-row>
                    <!-- end row-->

                    <h4 class="mt-4">Add New Address</h4>

                    <p class="text-muted mb-4">
                      Fill the form below so we can send you the order's
                      invoice.
                    </p>

                    <b-form>
                      <b-row>
                        <b-col md="6">
                          <div class="mb-3">
                            <label for="new-adr-first-name" class="form-label"
                              >First Name</label
                            >
                            <input
                              class="form-control"
                              type="text"
                              placeholder="Enter your first name"
                              id="new-adr-first-name"
                            />
                          </div>
                        </b-col>
                        <b-col md="6">
                          <div class="mb-3">
                            <label for="new-adr-last-name" class="form-label"
                              >Last Name</label
                            >
                            <input
                              class="form-control"
                              type="text"
                              placeholder="Enter your last name"
                              id="new-adr-last-name"
                            />
                          </div>
                        </b-col>
                      </b-row>
                      <!-- end row -->
                      <b-row>
                        <b-col md="6">
                          <div class="mb-3">
                            <label
                              for="new-adr-email-address"
                              class="form-label"
                              >Email Address
                              <span class="text-danger">*</span></label
                            >
                            <input
                              class="form-control"
                              type="email"
                              placeholder="Enter your email"
                              id="new-adr-email-address"
                            />
                          </div>
                        </b-col>
                        <b-col md="6">
                          <div class="mb-3">
                            <label for="new-adr-phone" class="form-label"
                              >Phone <span class="text-danger">*</span></label
                            >
                            <input
                              class="form-control"
                              type="text"
                              placeholder="(xx) xxx xxxx xxx"
                              id="new-adr-phone"
                            />
                          </div>
                        </b-col>
                      </b-row>
                      <!-- end row -->
                      <b-row>
                        <b-col cols="12">
                          <div class="mb-3">
                            <label for="new-adr-address" class="form-label"
                              >Address</label
                            >
                            <input
                              class="form-control"
                              type="text"
                              placeholder="Enter full address"
                              id="new-adr-address"
                            />
                          </div>
                        </b-col>
                      </b-row>
                      <!-- end row -->
                      <b-row>
                        <b-cols md="4">
                          <div class="mb-3">
                            <label for="new-adr-town-city" class="form-label"
                              >Town / City</label
                            >
                            <input
                              class="form-control"
                              type="text"
                              placeholder="Enter your city name"
                              id="new-adr-town-city"
                            />
                          </div>
                        </b-cols>
                        <b-cols md="4">
                          <div class="mb-3">
                            <label for="new-adr-state" class="form-label"
                              >State</label
                            >
                            <input
                              class="form-control"
                              type="text"
                              placeholder="Enter your state"
                              id="new-adr-state"
                            />
                          </div>
                        </b-cols>
                        <b-cols md="4">
                          <div class="mb-3">
                            <label for="new-adr-zip-postal" class="form-label"
                              >Zip / Postal Code</label
                            >
                            <input
                              class="form-control"
                              type="text"
                              placeholder="Enter your zip code"
                              id="new-adr-zip-postal"
                            />
                          </div>
                        </b-cols>
                      </b-row>
                      <!-- end row -->
                      <b-row>
                        <b-col cols="12">
                          <div class="mb-3">
                            <label class="form-label">Country</label>
                            <VueMultiselect
                              v-model="value"
                              :options="options"
                              :searchable="true"
                            />
                          </div>
                        </b-col>
                      </b-row>
                      <!-- end row -->

                      <h4 class="mt-4">Shipping Method</h4>

                      <p class="text-muted mb-3">
                        Fill the form below in order to send you the order's
                        invoice.
                      </p>

                      <b-row>
                        <b-col md="6">
                          <div class="border p-3 rounded mb-3 mb-md-0">
                            <div class="form-check">
                              <input
                                type="radio"
                                id="shippingMethodRadio1"
                                name="shippingOptions"
                                class="form-check-input"
                                checked
                              />
                              <label
                                class="form-check-label font-16 fw-bold"
                                for="shippingMethodRadio1"
                                >Standard Delivery - FREE</label
                              >
                            </div>
                            <p class="mb-0 ps-3 pt-1">
                              Estimated 5-7 days shipping (Duties and tax may be
                              due upon delivery)
                            </p>
                          </div>
                        </b-col>
                        <b-col md="6">
                          <div class="border p-3 rounded">
                            <div class="form-check">
                              <input
                                type="radio"
                                id="shippingMethodRadio2"
                                name="shippingOptions"
                                class="form-check-input"
                              />
                              <label
                                class="form-check-label font-16 fw-bold"
                                for="shippingMethodRadio2"
                                >Fast Delivery - $25</label
                              >
                            </div>
                            <p class="mb-0 ps-3 pt-1">
                              Estimated 1-2 days shipping (Duties and tax may be
                              due upon delivery)
                            </p>
                          </div>
                        </b-col>
                      </b-row>
                      <!-- end row-->

                      <b-row class="mt-4">
                        <b-col sm="6">
                          <router-link
                            to="/apps/ecommerce/shopping-cart"
                            class="btn text-muted d-none d-sm-inline-block btn-link fw-semibold"
                          >
                            <i class="mdi mdi-arrow-left"></i> Back to Shopping
                            Cart
                          </router-link>
                        </b-col>
                        <!-- end col -->
                        <b-col sm="6">
                          <div class="text-sm-end">
                            <router-link
                              to="/apps/ecommerce/checkout"
                              class="btn btn-danger"
                            >
                              <i class="mdi mdi-cash-multiple me-1"></i>
                              Continue to Payment
                            </router-link>
                          </div>
                        </b-col>
                        <!-- end col -->
                      </b-row>
                      <!-- end row -->
                    </b-form>
                  </b-col>
                  <b-col lg="4">
                    <div class="border p-3 mt-4 mt-lg-0 rounded">
                      <h4 class="header-title mb-3">Order Summary</h4>

                      <div class="table-responsive">
                        <table class="table table-nowrap table-centered mb-0">
                          <tbody>
                            <tr>
                              <td>
                                <img
                                  src="@/assets/images/products/product-1.jpg"
                                  alt="contact-img"
                                  title="contact-img"
                                  class="rounded me-2"
                                  height="48"
                                />
                                <p class="m-0 d-inline-block align-middle">
                                  <router-link
                                    to="/apps/ecommerce/products-details"
                                    class="text-body fw-semibold"
                                    >Amazing Modern Chair
                                  </router-link>
                                  <br />
                                  <small>5 x $148.66</small>
                                </p>
                              </td>
                              <td class="text-end">$743.30</td>
                            </tr>
                            <tr>
                              <td>
                                <img
                                  src="@/assets/images/products/product-2.jpg"
                                  alt="contact-img"
                                  title="contact-img"
                                  class="rounded me-2"
                                  height="48"
                                />
                                <p class="m-0 d-inline-block align-middle">
                                  <router-link
                                    to="/apps/ecommerce/products-details"
                                    class="text-body fw-semibold"
                                    >Designer Awesome Chair
                                  </router-link>
                                  <br />
                                  <small>2 x $99.00</small>
                                </p>
                              </td>
                              <td class="text-end">$198.00</td>
                            </tr>
                            <tr>
                              <td>
                                <img
                                  src="@/assets/images/products/product-3.jpg"
                                  alt="contact-img"
                                  title="contact-img"
                                  class="rounded me-2"
                                  height="48"
                                />
                                <p class="m-0 d-inline-block align-middle">
                                  <router-link
                                    to="/apps/ecommerce/products-details"
                                    class="text-body fw-semibold"
                                    >Biblio Plastic Armchair
                                  </router-link>
                                  <br />
                                  <small>1 x $129.99</small>
                                </p>
                              </td>
                              <td class="text-end">$129.99</td>
                            </tr>
                            <tr class="text-end">
                              <td>
                                <h6 class="m-0">Sub Total:</h6>
                              </td>
                              <td class="text-end">$1071.29</td>
                            </tr>
                            <tr class="text-end">
                              <td>
                                <h6 class="m-0">Shipping:</h6>
                              </td>
                              <td class="text-end">FREE</td>
                            </tr>
                            <tr class="text-end">
                              <td>
                                <h5 class="m-0">Total:</h5>
                              </td>
                              <td class="text-end fw-semibold">$1071.29</td>
                            </tr>
                          </tbody>
                        </table>
                      </div>
                      <!-- end table-responsive -->
                    </div>
                    <!-- end .border-->
                  </b-col>
                  <!-- end col -->
                </b-row>
                <!-- end row-->
              </b-tab>

              <b-tab>
                <template #title>
                  <i class="mdi mdi-cash-multiple font-18"></i>
                  <span class="d-none d-lg-block">Payment Info</span>
                </template>
                <div class="row">
                  <div class="col-lg-8">
                    <h4 class="mt-2">Payment Selection</h4>

                    <p class="text-muted mb-4">
                      Fill the form below in order to send you the order's
                      invoice.
                    </p>

                    <!-- Pay with Paypal box-->
                    <div class="border p-3 mb-3 rounded">
                      <b-row>
                        <b-col sm="8">
                          <div class="form-check">
                            <input
                              type="radio"
                              id="BillingOptRadio2"
                              name="billingOptions"
                              class="form-check-input"
                            />
                            <label
                              class="form-check-label font-16 fw-bold"
                              for="BillingOptRadio2"
                              >Pay with Paypal</label
                            >
                          </div>
                          <p class="mb-0 ps-3 pt-1">
                            You will be redirected to PayPal website to complete
                            your purchase securely.
                          </p>
                        </b-col>
                        <b-col sm="4" class="text-sm-end mt-3 mt-sm-0">
                          <img
                            src="@/assets/images/payments/paypal.png"
                            height="25"
                            alt="paypal-img"
                          />
                        </b-col>
                      </b-row>
                    </div>
                    <!-- end Pay with Paypal box-->

                    <!-- Credit/Debit Card box-->
                    <div class="border p-3 mb-3 rounded">
                      <b-row>
                        <b-col sm="8">
                          <div class="form-check">
                            <input
                              type="radio"
                              id="BillingOptRadio1"
                              name="billingOptions"
                              class="form-check-input"
                              checked
                            />
                            <label
                              class="form-check-label font-16 fw-bold"
                              for="BillingOptRadio1"
                              >Credit / Debit Card</label
                            >
                          </div>
                          <p class="mb-0 ps-3 pt-1">
                            Safe money transfer using your bank account. We
                            support Mastercard, Visa, Discover and Stripe.
                          </p>
                        </b-col>
                        <b-col sm="4" class="text-sm-end mt-3 mt-sm-0">
                          <img
                            src="@/assets/images/payments/master.png"
                            height="24"
                            alt="master-card-img"
                          />
                          <img
                            src="@/assets/images/payments/discover.png"
                            height="24"
                            alt="discover-card-img"
                          />
                          <img
                            src="@/assets/images/payments/visa.png"
                            height="24"
                            alt="visa-card-img"
                          />
                          <img
                            src="@/assets/images/payments/stripe.png"
                            height="24"
                            alt="stripe-card-img"
                          />
                        </b-col>
                      </b-row>
                      <!-- end row -->
                      <b-row class="mt-4">
                        <b-col md="12">
                          <div class="mb-3">
                            <label for="card-number" class="form-label"
                              >Card Number</label
                            >
                            <input
                              type="text"
                              id="card-number"
                              class="form-control"
                              data-toggle="input-mask"
                              data-mask-format="0000 0000 0000 0000"
                              placeholder="4242 4242 4242 4242"
                            />
                          </div>
                        </b-col>
                      </b-row>
                      <!-- end row -->
                      <b-row>
                        <b-col md="6">
                          <div class="mb-3">
                            <label for="card-name-on" class="form-label"
                              >Name on card</label
                            >
                            <input
                              type="text"
                              id="card-name-on"
                              class="form-control"
                              placeholder="Master Shreyu"
                            />
                          </div>
                        </b-col>
                        <b-col md="3">
                          <div class="mb-3">
                            <label for="card-expiry-date" class="form-label"
                              >Expiry date</label
                            >
                            <input
                              type="text"
                              id="card-expiry-date"
                              class="form-control"
                              data-toggle="input-mask"
                              data-mask-format="00/00"
                              placeholder="MM/YY"
                            />
                          </div>
                        </b-col>
                        <b-col md="3">
                          <div class="mb-3">
                            <label for="card-cvv" class="form-label"
                              >CVV code</label
                            >
                            <input
                              type="text"
                              id="card-cvv"
                              class="form-control"
                              data-toggle="input-mask"
                              data-mask-format="000"
                              placeholder="012"
                            />
                          </div>
                        </b-col>
                      </b-row>
                      <!-- end row -->
                    </div>
                    <!-- end Credit/Debit Card box-->

                    <!-- Pay with Payoneer box-->
                    <div class="border p-3 mb-3 rounded">
                      <b-row>
                        <b-col sm="8">
                          <div class="form-check">
                            <input
                              type="radio"
                              id="BillingOptRadio3"
                              name="billingOptions"
                              class="form-check-input"
                            />
                            <label
                              class="form-check-label font-16 fw-bold"
                              for="BillingOptRadio3"
                              >Pay with Payoneer</label
                            >
                          </div>
                          <p class="mb-0 ps-3 pt-1">
                            You will be redirected to Payoneer website to
                            complete your purchase securely.
                          </p>
                        </b-col>
                        <b-col sm="4" class="text-sm-end mt-3 mt-sm-0">
                          <img
                            src="@/assets/images/payments/payoneer.png"
                            height="30"
                            alt="paypal-img"
                          />
                        </b-col>
                      </b-row>
                    </div>
                    <!-- end Pay with Payoneer box-->

                    <!-- Cash on Delivery box-->
                    <div class="border p-3 mb-3 rounded">
                      <b-row>
                        <b-col sm="8">
                          <div class="form-check">
                            <input
                              type="radio"
                              id="BillingOptRadio4"
                              name="billingOptions"
                              class="form-check-input"
                            />
                            <label
                              class="form-check-label font-16 fw-bold"
                              for="BillingOptRadio4"
                              >Cash on Delivery</label
                            >
                          </div>
                          <p class="mb-0 ps-3 pt-1">
                            Pay with cash when your order is delivered.
                          </p>
                        </b-col>
                        <b-col sm="4" class="text-sm-end mt-3 mt-sm-0">
                          <img
                            src="@/assets/images/payments/cod.png"
                            height="22"
                            alt="paypal-img"
                          />
                        </b-col>
                      </b-row>
                    </div>
                    <!-- end Cash on Delivery box-->

                    <b-row class="mt-4">
                      <b-col sm="6">
                        <router-link
                          to="/apps/ecommerce/shopping-cart"
                          class="btn text-muted d-none d-sm-inline-block btn-link fw-semibold"
                        >
                          <i class="mdi mdi-arrow-left"></i> Back to Shopping
                          Cart
                        </router-link>
                      </b-col>
                      <!-- end col -->
                      <b-col sm="6">
                        <div class="text-sm-end">
                          <router-link
                            to="/apps/ecommerce/checkout"
                            class="btn btn-danger"
                          >
                            <i class="mdi mdi-cash-multiple me-1"></i> Complete
                            Order
                          </router-link>
                        </div>
                      </b-col>
                      <!-- end col -->
                    </b-row>
                    <!-- end row-->
                  </div>
                  <!-- end col -->

                  <b-col lg="4">
                    <div class="border p-3 mt-4 mt-lg-0 rounded">
                      <h4 class="header-title mb-3">Order Summary</h4>

                      <div class="table-responsive">
                        <table class="table table-nowrap table-centered mb-0">
                          <tbody>
                            <tr>
                              <td>
                                <img
                                  src="@/assets/images/products/product-1.jpg"
                                  alt="contact-img"
                                  title="contact-img"
                                  class="rounded me-2"
                                  height="48"
                                />
                                <p class="m-0 d-inline-block align-middle">
                                  <router-link
                                    to="/apps/ecommerce/products-details"
                                    class="text-body fw-semibold"
                                    >Amazing Modern Chair
                                  </router-link>
                                  <br />
                                  <small>5 x $148.66</small>
                                </p>
                              </td>
                              <td class="text-end">$743.30</td>
                            </tr>
                            <tr>
                              <td>
                                <img
                                  src="@/assets/images/products/product-2.jpg"
                                  alt="contact-img"
                                  title="contact-img"
                                  class="rounded me-2"
                                  height="48"
                                />
                                <p class="m-0 d-inline-block align-middle">
                                  <router-link
                                    to="/apps/ecommerce/products-details"
                                    class="text-body fw-semibold"
                                    >Designer Awesome Chair
                                  </router-link>
                                  <br />
                                  <small>2 x $99.00</small>
                                </p>
                              </td>
                              <td class="text-end">$198.00</td>
                            </tr>
                            <tr>
                              <td>
                                <img
                                  src="@/assets/images/products/product-3.jpg"
                                  alt="contact-img"
                                  title="contact-img"
                                  class="rounded me-2"
                                  height="48"
                                />
                                <p class="m-0 d-inline-block align-middle">
                                  <router-link
                                    to="/apps/ecommerce/products-details"
                                    class="text-body fw-semibold"
                                    >Biblio Plastic Armchair
                                  </router-link>
                                  <br />
                                  <small>1 x $129.99</small>
                                </p>
                              </td>
                              <td class="text-end">$129.99</td>
                            </tr>
                            <tr class="text-end">
                              <td>
                                <h6 class="m-0">Sub Total:</h6>
                              </td>
                              <td class="text-end">$1071.29</td>
                            </tr>
                            <tr class="text-end">
                              <td>
                                <h6 class="m-0">Shipping:</h6>
                              </td>
                              <td class="text-end">FREE</td>
                            </tr>
                            <tr class="text-end">
                              <td>
                                <h5 class="m-0">Total:</h5>
                              </td>
                              <td class="text-end fw-semibold">$1071.29</td>
                            </tr>
                          </tbody>
                        </table>
                      </div>
                      <!-- end table-responsive -->
                    </div>
                    <!-- end .border-->
                  </b-col>
                  <!-- end col -->
                </div>
                <!-- end row-->
              </b-tab>
            </b-tabs>
          </div>
          <!-- end card-body-->
        </div>
        <!-- end card-->
      </b-col>
      <!-- end col -->
    </b-row>
  </Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";

import VueMultiselect from "vue-multiselect";

export default {
  components: { Breadcrumb, Layout, VueMultiselect },
  data() {
    return {
      title: 'Checkout',
      items: [
        {
          text: 'Hyper',
          href: '/',
        },
        {
          text: 'eCommerce',
          href: '/',
        },
        {
          text: 'Checkout',
          active: true,
        },
      ],
      value: null,
      select: null,
      cardCvv: "",
      cardExpiryDate: "",
      cardNumber: "",
      options: [
        "Afghanistan",
        "Albania",
        "Algeria",
        "American Samoa",
        "Andorra",
        "Angola",
        "Anguilla",
        "Antarctica",
        "Argentina",
        "Armenia",
        "Aruba",
        "Australia",
        "Austria",
        "Azerbaijan",
        "Bahamas",
        "Bahrain",
        "Bangladesh",
        "Barbados",
        "Belarus",
        "Belgium",
        "Belize",
        "Benin",
        "Bermuda",
        "Bhutan",
        "Bolivia",
        "Botswana",
        "Bouvet Island",
        "Brazil",
        "Brunei Darussalam",
        "Bulgaria",
        "Burkina Faso",
        "Burundi",
        "Cambodia",
        "Cameroon",
        "Canada",
        "Cape Verde",
        "Cayman Islands",
        "Central African Republic",
        "Chad",
        "Chile",
        "China",
        "Christmas Island",
        "Cocos (Keeling) Islands",
        "Colombia",
        "Comoros",
        "Congo",
        "Cook Islands",
        "Costa Rica",
        `Cote d'Ivoire`,
        "Croatia (Hrvatska)",
        "Cuba",
        "Cyprus",
        "Czech Republic",
        "Denmark",
        "Djibouti",
        "Dominica",
        "Dominican Republic",
        "Ecuador",
        "Egypt",
        "El Salvador",
        "Equatorial Guinea",
        "Eritrea",
        "Estonia",
        "Ethiopia",
        "Falkland Islands (Malvinas)",
        "Faroe Islands",
        "Fiji",
        "Finland",
        "France",
        "French Guiana",
        "French Polynesia",
        "Gabon",
        "Gambia",
        "Georgia",
        "Germany",
        "Ghana",
        "Gibraltar",
        "Greece",
        "Greenland",
        "Grenada",
        "Guadeloupe",
        "Guam",
        "Guatemala",
        "Guinea",
        "Guinea-Bissau",
        "Guyana",
        "Haiti",
        "Honduras",
        "Hong Kong",
        "Hungary",
        "Iceland",
        "India",
        "Indonesia",
        "Iraq",
        "Ireland",
        "Israel",
        "Italy",
        "Jamaica",
        "Japan",
        "Jordan",
        "Kazakhstan",
        "Kenya",
        "Kiribati",
        "Korea",
        "Kuwait",
        "Kyrgyzstan",
        "Latvia",
        "Lebanon",
        "Lesotho",
        "Liberia",
        "Libyan Arab Jamahiriya",
        "Liechtenstein",
        "Lithuania",
        "Luxembourg",
        "Macau",
        "Madagascar",
        "Malawi",
        "Malaysia",
        "Maldives",
        "Mali",
        "Malta",
        "Marshall Islands",
        "Martinique",
        "Mauritania",
        "Mauritius",
        "Mayotte",
        "Mexico",
        "Moldova",
        "Monaco",
        "Mongolia",
        "Montserrat",
        "Morocco",
        "Mozambique",
        "Myanmar",
        "Namibia",
        "Nauru",
        "Nepal",
        "Netherlands",
        "Netherlands Antilles",
        "New Caledonia",
        "New Zealand",
        "Nicaragua",
        "Niger",
        "Nigeria",
        "Niue",
        "Norfolk Island",
        "Northern Mariana Islands",
        "Norway",
        "Oman",
        "Palau",
        "Panama",
        "Papua New Guinea",
        "Paraguay",
        "Peru",
        "Philippines",
        "Pitcairn",
        "Poland",
        "Portugal",
        "Puerto Rico",
        "Qatar",
        "Reunion",
        "Romania",
        "Russian Federation",
        "Rwanda",
        "Saint Kitts and Nevis",
        "Saint LUCIA",
        "Samoa",
        "San Marino",
        "Sao Tome and Principe",
        "Saudi Arabia",
        "Senegal",
        "Seychelles",
        "Sierra Leone",
        "Singapore",
        "Slovakia (Slovak Republic)",
        "Slovenia",
        "Solomon Islands",
        "Somalia",
        "South Africa",
        "Spain",
        "Sri Lanka",
        "St. Helena",
        "St. Pierre and Miquelon",
        "Sudan",
        "Suriname",
        "Swaziland",
        "Sweden",
        "Switzerland",
        "Syrian Arab Republic",
        "Taiwan, Province of China",
        "Tajikistan",
        "Tanzania",
        "Thailand",
        "Togo",
        "Tokelau",
        "Tonga",
        "Trinidad and Tobago",
        "Tunisia",
        "Turkey",
        "Turkmenistan",
        "Turks and Caicos Islands",
        "Tuvalu",
        "Uganda",
        "Ukraine",
        "United Arab Emirates",
        "United Kingdom",
        "United States",
        "Uruguay",
        "Uzbekistan",
        "Vanuatu",
        "Venezuela",
        "Viet Nam",
        "Virgin Islands (British)",
        "Virgin Islands (U.S.)",
        "Wallis and Futuna Islands",
        "Western Sahara",
        "Yemen",
        "Zambia",
        "Zimbabwe",
      ],
    };
  },
};
</script>
