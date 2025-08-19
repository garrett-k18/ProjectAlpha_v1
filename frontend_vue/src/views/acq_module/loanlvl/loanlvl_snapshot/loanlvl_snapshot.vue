<template>
  <Layout>
    <Breadcrumb :title="displayTitle" :items="items"/>
    <div>
      <!--
        Master tabs wrapper for loan-level UI. We use BootstrapVue Next's
        <BTabs>/<BTab> components (Vue 3 compatible fork) to host separate
        feature areas. This keeps loan UI concerns out of the grid.
        Docs: https://bootstrap-vue-next.github.io/bootstrap-vue-next/docs/components/tabs
      -->
      <BTabs content-class="mt-3">
        <!-- Snapshot tab wraps the existing summary/layout content -->
        <BTab title="Snapshot" active>
          <div class="card">
            <div class="card-body">
              <b-row>
                <b-col lg="5">
                  <!-- Reusable global PhotoCarousel component replaces static images -->
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
                  <!--
                    The following UI is sample/static. When integrated with real data, use the
                    provided props (row, productId) to bind values appropriately.
                  -->
                  <b-form class="ps-lg-4">
                    <!-- Product title -->
                    <h3 class="mt-0">
                      Amazing Modern Chair (Orange)
                      <a href="javascript: void(0);" class="text-muted"><i class="mdi mdi-square-edit-outline ms-2"></i></a>
                    </h3>
                    <p class="mb-1">Added Date: 09/12/2018</p>
                    <p class="font-16">
                      <span class="text-warning mdi mdi-star"></span>
                      <span class="text-warning mdi mdi-star"></span>
                      <span class="text-warning mdi mdi-star"></span>
                      <span class="text-warning mdi mdi-star"></span>
                      <span class="text-warning mdi mdi-star"></span>
                    </p>

                    <!-- Product stock -->
                    <div class="mt-3">
                      <h4><span class="badge badge-success-lighten">Instock</span></h4>
                    </div>

                    <!-- Product description -->
                    <div class="mt-4">
                      <h6 class="font-14">Retail Price:</h6>
                      <h3> $139.58</h3>
                    </div>

                    <!-- Quantity -->
                    <div class="mt-4">
                      <h6 class="font-14">Quantity</h6>
                      <div class="d-flex">
                        <input type="number" min="1" value="1" class="form-control" placeholder="Qty"
                               style="width: 90px;">
                        <b-button variant="danger" class="ms-2"><i class="mdi mdi-cart me-1"></i> Add to cart
                        </b-button>
                      </div>
                    </div>

                    <!-- Product description -->
                    <div class="mt-4">
                      <h6 class="font-14">Description:</h6>
                      <p>It is a long established fact that a reader will be distracted by the readable content of a page
                        when looking at its layout. The point of using Lorem Ipsum is that it has a more-or-less normal
                        distribution of letters, as opposed to using 'Content here, content here', making it look like
                        readable English. </p>
                    </div>

                    <!-- Product information -->
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
                          <div class="progress-bar bg-success" role="progressbar" style="width: 56%;" aria-valuenow="56"
                               aria-valuemin="0" aria-valuemax="100"></div>
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
                          <div class="progress-bar bg-danger" role="progressbar" style="width: 16%;" aria-valuenow="16"
                               aria-valuemin="0" aria-valuemax="100"></div>
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
                          <div class="progress-bar bg-success" role="progressbar" style="width: 72%;" aria-valuenow="72"
                               aria-valuemin="0" aria-valuemax="100"></div>
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
                          <div class="progress-bar bg-success" role="progressbar" style="width: 89%;" aria-valuenow="89"
                               aria-valuemin="0" aria-valuemax="100"></div>
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

        <!-- Property Details tab -->
        <BTab title="Property Details">
          <PropertyDetailsTab :row="row" :productId="productId" />
        </BTab>

        <!-- Acquisition Analysis tab -->
        <BTab title="Acquisition Analysis">
          <AcquisitionAnalysisTab :row="row" :productId="productId" />
        </BTab>
      </BTabs>
    </div>

  </Layout>
</template>

<script setup lang="ts">
// Import layout and shared components used in this view
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";
import PhotoCarousel from '@/1_global/components/PhotoCarousel.vue'
import type { PhotoItem } from '@/1_global/components/PhotoCarousel.vue'
// Import BootstrapVue Next tabs per docs (Vue 3 fork of BootstrapVue)
// Docs: https://bootstrap-vue-next.github.io/bootstrap-vue-next/docs/components/tabs
import { BTabs, BTab } from 'bootstrap-vue-next'
// Import loan-level tab components (kept modular under tabs/)
import PropertyDetailsTab from '@/views/acq_module/loanlvl/tabs/PropertyDetailsTab.vue'
import AcquisitionAnalysisTab from '@/views/acq_module/loanlvl/tabs/AcquisitionAnalysisTab.vue'
// Sample images used as fallback demo content (Vite resolves asset URLs)
import product5 from '@/assets/images/products/product-5.jpg'
import product1 from '@/assets/images/products/product-1.jpg'
import product6 from '@/assets/images/products/product-6.jpg'
import product3 from '@/assets/images/products/product-3.jpg'

// Import Vue Composition API utilities
import { ref, computed, toRef } from 'vue'

// Type describing a breadcrumb item consumed by `Breadcrumb`
type BreadcrumbItem = {
  text: string
  href?: string
  to?: string
  active?: boolean
}

// Define strongly-typed props for this view
const props = withDefaults(defineProps<{
  // Optional row object passed from a parent grid/list
  row?: Record<string, any> | null
  // Explicit product/asset identifier to show in the header
  productId?: string | number | null
  // Optional best-effort address forwarded via route (query param)
  address?: string | null
}>(), {
  row: null,
  productId: null,
  address: null,
})

// Reactive page title text
const title = ref<string>('Asset Details')

// Reactive breadcrumb items shown beneath the main layout header
const items = ref<BreadcrumbItem[]>([
  { text: 'Hyper', href: '/' },
  { text: 'Acquisitions Dashboard', to: '/acquisitions' },
  { text: 'Asset Details', active: true },
])

// Create reactive references to incoming props for template usage
const productId = toRef(props, 'productId')
const row = toRef(props, 'row')
const addressProp = toRef(props, 'address')

// Address for header is composed inline in displayTitle using
// SellerRawData fields: street_address, city, state, zip.

// Compute the display title to match the modal formatting
const displayTitle = computed<string>(() => {
  const rawId = productId.value
  const id = (typeof rawId === 'string' || typeof rawId === 'number') ? String(rawId) : ''
  // Build address directly from known backend fields; fallback to address prop (router)
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

// Demo images for the embedded PhotoCarousel. Replace with real photos when wiring backend data.
const computedImages = computed<PhotoItem[]>(() => [
  { src: product5, alt: 'Primary product image', thumb: product5 },
  { src: product1, alt: 'Variant image 1', thumb: product1 },
  { src: product6, alt: 'Variant image 2', thumb: product6 },
  { src: product3, alt: 'Variant image 3', thumb: product3 },
])
</script>
