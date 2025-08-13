<template>
  <Layout>
    <Breadcrumb :title="title" :items="items"/>
    <b-row>
      <b-col class="xxl-6">
        <CustomSyntax title="Sizing - Images">
          <template v-slot:sub-text>
            Create and group avatars of different sizes and shapes with the css classes.
            Using Bootstrap's naming convention, you can control size of avatar including standard avatar, or scale it
            up to different sizes.
          </template>
          <template v-slot:preview>
            <b-row>
              <b-col md="3">
                <b-avatar src="/src/assets/images/users/avatar-2.jpg" alt="avatar" size="sm" class="img-fluid"
                          rounded="sm"/>
                <p>
                  <code>.avatar-xs</code>
                </p>
                <b-avatar src="/src/assets/images/users/avatar-3.jpg" alt="avatar" size="sm"
                          class="img-fluid avatar-sm mt-2" rounded="sm"/>
                <p class="mb-2 mb-sm-0">
                  <code>.avatar-sm</code>
                </p>
              </b-col>
              <b-col md="3">
                <b-avatar src="/src/assets/images/users/avatar-4.jpg" alt="avatar" size="md" class="img-fluid avatar-md"
                          rounded="sm"/>
                <p>
                  <code>.avatar-md</code>
                </p>
              </b-col>

              <b-col md="3">
                <b-avatar src="/src/assets/images/users/avatar-5.jpg" alt="avatar" class="img-fluid avatar-lg"
                          rounded="sm"/>
                <p>
                  <code>.avatar-lg</code>
                </p>
              </b-col>

              <b-col md="3">
                <b-avatar src="/src/assets/images/users/avatar-6.jpg" alt="avatar" class="img-fluid avatar-xl"
                          rounded="sm"/>
                <p class="mb-0">
                  <code>.avatar-xl</code>
                </p>
              </b-col>
            </b-row> <!-- end row-->
          </template>
        </CustomSyntax>

      </b-col>
      <b-col xxl="6">
        <CustomSyntax title="Rounded Circle">
          <template v-slot:sub-text>
            Using an additional class <code>.rounded-circle</code> in <code>&lt;img&gt;</code> element creates the
            rounded avatar.
          </template>
          <template v-slot:preview>
            <b-row>
              <b-col md="4">
                <b-avatar src="/src/assets/images/users/avatar-7.jpg" alt="avatar" class="img-fluid avatar-md"
                          rounded="circle"/>
                <p class="mt-1">
                  <code>.avatar-md .rounded-circle</code>
                </p>
              </b-col>

              <b-col md="4">
                <b-avatar src="/src/assets/images/users/avatar-8.jpg" alt="avatar" class="img-fluid avatar-lg"
                          rounded="circle"/>
                <p>
                  <code>.avatar-lg .rounded-circle</code>
                </p>
              </b-col>

              <b-col md="4">
                <b-avatar src="/src/assets/images/users/avatar-9.jpg" alt="avatar" class="img-fluid avatar-xl"
                          rounded="circle"/>
                <p class="mb-0">
                  <code>.avatar-xl .rounded-circle</code>
                </p>
              </b-col>
            </b-row> <!-- end row-->
          </template>
        </CustomSyntax>
      </b-col>
    </b-row>
    <!-- end row -->

    <b-row>
      <b-col xxl="6">
        <CustomSyntax title="Sizing - Background Color">
          <template v-slot:sub-text>
            Using utilities classes of background e.g. <code>bg-*</code> allows you to have any background color as
            well.
          </template>
          <template v-slot:preview>
            <b-row>
              <b-col md="3">
                <div class="avatar-xs">
                                <span class="avatar-title rounded">
                                    xs
                                </span>
                </div>
                <p class="mb-2 font-14 mt-1">
                  Using <code>.avatar-xs</code>
                </p>

                <div class="avatar-sm mt-3">
                                <span class="avatar-title bg-success rounded">
                                    sm
                                </span>
                </div>

                <p class="mb-0 font-14 mt-1">
                  Using <code>.avatar-sm</code>
                </p>
              </b-col>
              <b-col md="3">
                <div class="avatar-md">
                                <span class="avatar-title bg-info-lighten text-info font-20 rounded">
                                    MD
                                </span>
                </div>

                <p class="mb-0 font-14 mt-1">
                  Using <code>.avatar-md</code>
                </p>
              </b-col>

              <b-col md="3">
                <div class="avatar-lg">
                                <span class="avatar-title bg-danger font-22 rounded">
                                    LG
                                </span>
                </div>

                <p class="mb-0 font-14 mt-1">
                  Using <code>.avatar-lg</code>
                </p>
              </b-col>

              <b-col md="3">
                <div class="avatar-xl">
                                <span class="avatar-title bg-warning-lighten text-warning font-24 rounded">
                                    XL
                                </span>
                </div>

                <p class="mb-0 font-14 mt-1">
                  Using <code>.avatar-xl</code>
                </p>
              </b-col>
            </b-row> <!-- end row-->
          </template>
        </CustomSyntax>
      </b-col>
      <b-col xxl="6">
        <CustomSyntax title="Rounded Circle Background">
          <template v-slot:sub-text>
            Using an additional class <code>.rounded-circle</code> in <code>&lt;img&gt;</code> element creates the
            rounded avatar.
          </template>
          <template v-slot:preview>
            <b-row>
              <b-col md="4">
                <div class="avatar-md">
                                <span class="avatar-title bg-secondary-lighten text-secondary font-20 rounded-circle">
                                    MD
                                </span>
                </div>

                <p class="mb-0 font-14 mt-1">
                  Using <code>.avatar-md .rounded-circle</code>
                </p>
              </b-col>

              <b-col md="4">
                <div class="avatar-lg">
                                <span class="avatar-title bg-light text-dark font-22 rounded-circle">
                                    LG
                                </span>
                </div>

                <p class="mb-0 font-14 mt-1">
                  Using <code>.avatar-lg .rounded-circle</code>
                </p>
              </b-col>

              <b-col md="4">
                <div class="avatar-xl">
                                <span class="avatar-title bg-primary-lighten text-primary font-24 rounded-circle">
                                    XL
                                </span>
                </div>

                <p class="mb-0 font-14 mt-1">
                  Using <code>.avatar-xl .rounded-circle</code>
                </p>
              </b-col>
            </b-row> <!-- end row-->
          </template>
        </CustomSyntax>
      </b-col>
    </b-row>
    <!-- end row -->

    <b-row>
      <b-col cols="12">
        <CustomSyntax title="Images shapes">
          <template v-slot:sub-text>
            Avatars with different sizes and shapes.
          </template>
          <template v-slot:preview>
            <b-row>
              <b-col sm="2">
                <b-avatar src="/src/assets/images/small/small-2.jpg" alt="avatar" class="img-fluid" rounded
                          size="150px"/>
                <p class="mb-0">
                  <code>.rounded</code>
                </p>
              </b-col>

              <b-col sm="2" class="text-center">
                <b-avatar src="/src/assets/images/users/avatar-6.jpg" alt="avatar" class="img-fluid" rounded
                          size="120px"/>
                <p class="mb-0">
                  <code>.rounded</code>
                </p>
              </b-col>

              <b-col sm="2" class="text-center">
                <b-avatar src="/src/assets/images/users/avatar-7.jpg" alt="avatar" class="img-fluid rounded-circle"
                          size="120px"/>
                <p class="mb-0">
                  <code>.rounded-circle</code>
                </p>
              </b-col>

              <b-col sm="2">
                <b-avatar src="/src/assets/images/small/small-3.jpg" alt="avatar" variant="light"
                          class="img-fluid img-thumbnail" size="200px"/>
                <p class="mb-0">
                  <code>.img-thumbnail</code>
                </p>
              </b-col>
              <b-col sm="2">
                <b-avatar src="/src/assets/images/users/avatar-8.jpg" alt="avatar" variant="light"
                          class="img-fluid img-thumbnail" rounded="circle" size="120"/>
                <p class="mb-0">
                  <code>.rounded-circle .img-thumbnail</code>
                </p>
              </b-col>
            </b-row> <!-- end row-->
          </template>
        </CustomSyntax>
      </b-col>
    </b-row>
    <!-- end row -->
  </Layout>
</template>

<script lang="ts">
import Layout from '@/components/layouts/layout.vue';
import Breadcrumb from '@/components/breadcrumb.vue';
import CustomSyntax from "@/components/custom/custom-syntax.vue";

export default {
  components: {Layout, Breadcrumb, CustomSyntax},
  data() {
    return {
      title: 'Avatars',
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
          text: 'Avatars',
          active: true,
        },
      ],
    }
  }
}
</script>
