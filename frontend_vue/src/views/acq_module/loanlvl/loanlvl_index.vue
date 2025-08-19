<template>
  <!--
    Master wrapper for Loan-Level UI.
    - Provides Hyper UI Layout/Breadcrumb shell for full-page usage
    - Hosts loan-level tabs (Snapshot, Property Details, Loan Details, Acquisition Analysis)
    - Central place for modal-related global styles (dialog/content sizing), so other
      components (e.g., data grid) remain clean and grid-only.
  -->
  <component :is="standalone ? Layout : 'div'">
    <Breadcrumb v-if="standalone" :title="displayTitle" :items="items" />

    <!--
      Tabs are implemented with BootstrapVue Next (Vue 3 compatible).
      Docs: https://bootstrap-vue-next.github.io/bootstrap-vue-next/docs/components/tabs
    -->
    <BTabs content-class="mt-3">
      <!-- Snapshot Tab: summary content and photo carousel -->
      <BTab title="Snapshot" active>
        <div class="card">
          <div class="card-body">
            <b-row>
              <b-col lg="5">
                <!-- Global PhotoCarousel (replace sample images with real data when wiring backend) -->
                <PhotoCarousel
                  :images="computedImages"
                  :controls="false"
                  :indicators="false"
                  :loop="true"
                  :show-thumbnails="true"
                  :interval="0"
                  img-class="d-block mx-auto"
                  :img-max-width="520"
                  :img-max-height="420"
                  :container-max-width="520"
                />
              </b-col>
              <b-col lg="7">
                <!-- Sample/static fields; bind to real props/row once backend is connected -->
                <b-form class="ps-lg-4">
                  <h3 class="mt-0">
                    Amazing Modern Chair (Orange)
                    <a href="javascript: void(0);" class="text-muted"
                      ><i class="mdi mdi-square-edit-outline ms-2"></i
                    ></a>
                  </h3>
                  <p class="mb-1">Added Date: 09/12/2018</p>
                  <p class="font-16">
                    <span class="text-warning mdi mdi-star"></span>
                    <span class="text-warning mdi mdi-star"></span>
                    <span class="text-warning mdi mdi-star"></span>
                    <span class="text-warning mdi mdi-star"></span>
                    <span class="text-warning mdi mdi-star"></span>
                  </p>

                  <div class="mt-3">
                    <h4><span class="badge badge-success-lighten">Instock</span></h4>
                  </div>

                  <div class="mt-4">
                    <h6 class="font-14">Retail Price:</h6>
                    <h3> $139.58</h3>
                  </div>

                  <div class="mt-4">
                    <h6 class="font-14">Quantity</h6>
                    <div class="d-flex">
                      <input
                        type="number"
                        min="1"
                        value="1"
                        class="form-control"
                        placeholder="Qty"
                        style="width: 90px"
                      />
                      <b-button variant="danger" class="ms-2"
                        ><i class="mdi mdi-cart me-1"></i> Add to cart</b-button
                      >
                    </div>
                  </div>

                  <div class="mt-4">
                    <h6 class="font-14">Description:</h6>
                    <p>
                      It is a long established fact that a reader will be distracted by the readable content of a page
                      when looking at its layout. The point of using Lorem Ipsum is that it has a more-or-less normal
                      distribution of letters, as opposed to using 'Content here, content here', making it look like readable
                      English.
                    </p>
                  </div>

                  <div class="mt-4">
                    <b-row>
                      <b-col md="4">
                        <h6 class="font-14">Available Stock:</h6>
                        <p class="text-sm lh-150">1784</p>
                      </b-col>
                      <b-col md="4">
                        <h6 class="font-14">Number of Orders:</h6>
                        <p class="text-sm lh-150">5,458</p>
                      </b-col>
                      <b-col md="4">
                        <h6 class="font-14">Revenue:</h6>
                        <p class="text-sm lh-150">$8,57,014</p>
                      </b-col>
                    </b-row>
                  </div>
                </b-form>
              </b-col>
            </b-row>

            <div class="table-responsive mt-4">
              <table class="table table-bordered table-centered mb-0">
                <thead class="table-light">
                  <tr>
                    <th>Outlets</th>
                    <th>Price</th>
                    <th>Stock</th>
                    <th>Revenue</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>ASOS Ridley Outlet - NYC</td>
                    <td>$139.58</td>
                    <td>
                      <div class="progress-w-percent mb-0">
                        <span class="progress-value">478 </span>
                        <div class="progress progress-sm">
                          <div
                            class="progress-bar bg-success"
                            role="progressbar"
                            style="width: 56%"
                            aria-valuenow="56"
                            aria-valuemin="0"
                            aria-valuemax="100"
                          ></div>
                        </div>
                      </div>
                    </td>
                    <td>$1,89,547</td>
                  </tr>
                  <tr>
                    <td>Marco Outlet - SRT</td>
                    <td>$149.99</td>
                    <td>
                      <div class="progress-w-percent mb-0">
                        <span class="progress-value">73 </span>
                        <div class="progress progress-sm">
                          <div
                            class="progress-bar bg-danger"
                            role="progressbar"
                            style="width: 16%"
                            aria-valuenow="16"
                            aria-valuemin="0"
                            aria-valuemax="100"
                          ></div>
                        </div>
                      </div>
                    </td>
                    <td>$87,245</td>
                  </tr>
                  <tr>
                    <td>Chairtest Outlet - HY</td>
                    <td>$135.87</td>
                    <td>
                      <div class="progress-w-percent mb-0">
                        <span class="progress-value">781 </span>
                        <div class="progress progress-sm">
                          <div
                            class="progress-bar bg-success"
                            role="progressbar"
                            style="width: 72%"
                            aria-valuenow="72"
                            aria-valuemin="0"
                            aria-valuemax="100"
                          ></div>
                        </div>
                      </div>
                    </td>
                    <td>$5,87,478</td>
                  </tr>
                  <tr>
                    <td>Nworld Group - India</td>
                    <td>$159.89</td>
                    <td>
                      <div class="progress-w-percent mb-0">
                        <span class="progress-value">815 </span>
                        <div class="progress progress-sm">
                          <div
                            class="progress-bar bg-success"
                            role="progressbar"
                            style="width: 89%"
                            aria-valuenow="89"
                            aria-valuemin="0"
                            aria-valuemax="100"
                          ></div>
                        </div>
                      </div>
                    </td>
                    <td>$55,781</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </BTab>

      <!-- Property Details Tab: modular component -->
      <BTab title="Property Details">
        <PropertyDetailsTab :row="row" :productId="productId" />
      </BTab>

      <!-- Loan Details Tab: modular component -->
      <BTab title="Loan Details">
        <LoanDetailsTab :row="row" :productId="productId" />
      </BTab>

      <!-- Acquisition Analysis Tab: modular component -->
      <BTab title="Acquisition Analysis">
        <AcquisitionAnalysisTab :row="row" :productId="productId" />
      </BTab>
    </BTabs>
  </component>
</template>

<script setup lang="ts">
// Layout + shared UI from Hyper UI template
import Layout from '@/components/layouts/layout.vue'
import Breadcrumb from '@/components/breadcrumb.vue'

// BootstrapVue Next tabs (Vue 3 compatible fork)
// Docs: https://bootstrap-vue-next.github.io/bootstrap-vue-next/docs/components/tabs
import { BTabs, BTab } from 'bootstrap-vue-next'

// Global carousel
import PhotoCarousel from '@/1_global/components/PhotoCarousel.vue'
import type { PhotoItem } from '@/1_global/components/PhotoCarousel.vue'

// Tabs (modular loan-level feature areas)
import PropertyDetailsTab from '@/views/acq_module/loanlvl/tabs/PropertyDetailsTab.vue'
import LoanDetailsTab from '@/views/acq_module/loanlvl/tabs/LoanDetailsTab.vue'
import AcquisitionAnalysisTab from '@/views/acq_module/loanlvl/tabs/AcquisitionAnalysisTab.vue'

// Demo images (replace with real photos)
import product5 from '@/assets/images/products/product-5.jpg'
import product1 from '@/assets/images/products/product-1.jpg'
import product6 from '@/assets/images/products/product-6.jpg'
import product3 from '@/assets/images/products/product-3.jpg'

// Vue reactivity utilities
import { ref, computed, toRef, withDefaults, defineProps } from 'vue'

// Strongly-typed props forwarded from router or parent (e.g., when used in a modal)
const props = withDefaults(defineProps<{
  row?: Record<string, any> | null
  productId?: string | number | null
  address?: string | null
  standalone?: boolean
}>(), {
  row: null,
  productId: null,
  address: null,
  standalone: true,
})

// Breadcrumb items beneath the main layout header
const items = ref<Array<{ text: string; href?: string; to?: string; active?: boolean }>>([
  { text: 'Hyper', href: '/' },
  { text: 'Acquisitions Dashboard', to: '/acquisitions' },
  { text: 'Asset Details', active: true },
])

// Create reactive references to incoming props
const productId = toRef(props, 'productId')
const row = toRef(props, 'row')
const addressProp = toRef(props, 'address')
const standalone = toRef(props, 'standalone')

// Page title matches the previous modal header format: `{id} — {address}`
const displayTitle = computed<string>(() => {
  const rawId = productId.value
  const id = typeof rawId === 'string' || typeof rawId === 'number' ? String(rawId) : ''

  const r = row.value || {}
  const street = String((r as any)['street_address'] ?? '').trim()
  const city = String((r as any)['city'] ?? '').trim()
  const state = String((r as any)['state'] ?? '').trim()
  const zip = String((r as any)['zip'] ?? '').trim()
  const locality = [city, state].filter(Boolean).join(', ')
  const tail = [locality, zip].filter(Boolean).join(' ')
  const built = [street, tail].filter(Boolean).join(', ')
  const propAddr = String(addressProp?.value ?? '').trim()
  const address = built || propAddr

  if (id && address) return `${id} — ${address}`
  if (id) return id
  if (address) return address
  return ''
})

// Demo images for the embedded PhotoCarousel
const computedImages = computed<PhotoItem[]>(() => [
  { src: product5, alt: 'Primary product image', thumb: product5 },
  { src: product1, alt: 'Variant image 1', thumb: product1 },
  { src: product6, alt: 'Variant image 2', thumb: product6 },
  { src: product3, alt: 'Variant image 3', thumb: product3 },
])
</script>

<style>
/*
  Global modal sizing & layout-aware centering for loan-level dialog.
  These classes are referenced by modal wrappers via dialog/content classes.
  Keeping them here ensures the grid stays clean and the styles are centralized.
*/
.product-details-dialog {
  width: 93.1vw; /* 5% smaller than 98vw */
  max-width: 93.1vw !important;
  margin-left: auto;
  margin-right: auto;
  position: relative;
  left: 0;
}

@media (min-width: 1200px) {
  .product-details-dialog {
    width: 81.7vw; /* 5% smaller than 86vw */
    max-width: 81.7vw !important;
  }
}

/* Layout-aware horizontal centering over content area (excluding sidebar) */
html[data-sidenav-size='default'] .product-details-dialog {
  left: calc(var(--bs-leftbar-width) / 2);
}
html[data-sidenav-size='compact'] .product-details-dialog {
  left: calc(var(--bs-leftbar-width-md) / 2);
}
html[data-sidenav-size='condensed'] .product-details-dialog,
html[data-sidenav-size='sm-hover'] .product-details-dialog,
html[data-sidenav-size='sm-hover-active'] .product-details-dialog {
  left: calc(var(--bs-leftbar-width-sm) / 2);
}
html[data-sidenav-size='full'] .product-details-dialog,
html[data-sidenav-size='fullscreen'] .product-details-dialog {
  left: 0;
}

.product-details-content {
  height: 89.3vh; /* 5% smaller than 94vh; body still scrolls */
  display: flex;
  flex-direction: column;
}
.product-details-content .modal-body {
  flex: 1 1 auto;
  overflow: auto;
}
</style>
