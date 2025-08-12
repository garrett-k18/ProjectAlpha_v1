<template>
  <div
    class="card bg-primary card-bg-img"
    style="background-image: url('/src/assets/images/bg-pattern.png')"
  >
    <div class="card-body">
      <span class="float-end text-white-50 display-5 mt-n1"
        ><i class="mdi mdi-contactless-payment"></i
      ></span>
      <h4 class="text-white">Dominic Keller</h4>

      <b-row class="align-items-center mt-4">
        <b-col cols="3" class="text-white font-12">
          <i class="mdi mdi-circle"></i>
          <i class="mdi mdi-circle"></i>
          <i class="mdi mdi-circle"></i>
          <i class="mdi mdi-circle"></i>
        </b-col>
        <b-col cols="3" class="text-white font-12">
          <i class="mdi mdi-circle"></i>
          <i class="mdi mdi-circle"></i>
          <i class="mdi mdi-circle"></i>
          <i class="mdi mdi-circle"></i>
        </b-col>
        <b-col cols="3" class="text-white font-12">
          <i class="mdi mdi-circle"></i>
          <i class="mdi mdi-circle"></i>
          <i class="mdi mdi-circle"></i>
          <i class="mdi mdi-circle"></i>
        </b-col>
        <b-col cols="3" class="text-white font-16 fw-bold">
          <span>1</span>
          <span>2</span>
          <span>3</span>
          <span>4</span>
        </b-col>
      </b-row>

      <b-row class="mt-4">
        <b-col cols="4">
          <p class="text-white-50 font-16 mb-1">Expiry Date</p>
          <h4 class="text-white my-0">10/26</h4>
        </b-col>

        <b-col cols="4">
          <p class="text-white-50 font-16 mb-1">CCV</p>
          <h4 class="text-white my-0">000</h4>
        </b-col>
        <b-col cols="4">
          <div class="text-end">
            <span
              class="avatar-sm bg-white opacity-25 rounded-circle d-inline-block"
            ></span>
            <span
              class="avatar-sm bg-white opacity-25 rounded-circle d-inline-block ms-n3"
            ></span>
          </div>
        </b-col>
      </b-row>
    </div>
  </div>
</template>

<script lang="ts">
export default {};
</script>
