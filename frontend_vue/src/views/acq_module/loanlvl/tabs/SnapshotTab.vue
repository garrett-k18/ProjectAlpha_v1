<template>
  <!-- Snapshot tab content used inside the product details modal.
       This component intentionally excludes page-level wrappers (Layout, Breadcrumb)
       so it can be embedded within a modal body. -->
  <div>
    <!-- Top summary row with photos and quick facts -->
    <b-row>
      <b-col lg="5">
        <!-- Reusable global PhotoCarousel component displays product/asset images -->
        <PhotoCarousel
          :images="images"
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
        <!-- Sample static details. Replace with real bindings to `row` / `productId` as wired. -->
        <b-form class="ps-lg-4">
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
              <input type="number" min="1" value="1" class="form-control" placeholder="Qty" style="width: 90px;" />
              <b-button variant="danger" class="ms-2"><i class="mdi mdi-cart me-1"></i> Add to cart</b-button>
            </div>
          </div>

          <div class="mt-4">
            <h6 class="font-14">Description:</h6>
            <p>
              It is a long established fact that a reader will be distracted by the readable content of a page when
              looking at its layout. The point of using Lorem Ipsum is that it has a more-or-less normal distribution
              of letters, as opposed to using 'Content here, content here', making it look like readable English.
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

    <!-- Pricing/stock by outlet table -->
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
                  <div class="progress-bar bg-success" role="progressbar" style="width: 56%;" aria-valuenow="56" aria-valuemin="0" aria-valuemax="100"></div>
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
                  <div class="progress-bar bg-danger" role="progressbar" style="width: 16%;" aria-valuenow="16" aria-valuemin="0" aria-valuemax="100"></div>
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
                  <div class="progress-bar bg-success" role="progressbar" style="width: 72%;" aria-valuenow="72" aria-valuemin="0" aria-valuemax="100"></div>
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
                  <div class="progress-bar bg-success" role="progressbar" style="width: 89%;" aria-valuenow="89" aria-valuemin="0" aria-valuemax="100"></div>
                </div>
              </div>
            </td>
            <td>$55,781</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
// SnapshotTab.vue
// Purpose: Provide the Snapshot tab content for the acquisitions product details modal.
// Props are designed to be generic so this component remains reusable.

// Import the reusable global PhotoCarousel and its PhotoItem type for strong typing
import PhotoCarousel from '@/1_global/components/PhotoCarousel.vue'
import type { PhotoItem } from '@/1_global/components/PhotoCarousel.vue'

// Vue composition API helpers (no state here, only props)
import { withDefaults, defineProps } from 'vue'

// Strongly-typed props so parent can pass images and optional context
const props = withDefaults(defineProps<{
  // images: array of photo items displayed in the carousel
  images: PhotoItem[]
  // row: optional dataset row for future bindings
  row?: Record<string, any> | null
  // productId: optional identifier for the asset
  productId?: string | number | null
}>(), {
  row: null,
  productId: null,
})
</script>
