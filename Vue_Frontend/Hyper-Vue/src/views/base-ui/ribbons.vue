<template>
  <Layout>
    <Breadcrumb :title="title" :items="items"/>

    <b-row>
      <b-col cols="12">
        <CustomSyntax title="">
          <template v-slot:sub-text>
          </template>
          <template v-slot:preview>
            <b-row>
              <b-col xxl="4" md="6">
                <b-card class="ribbon-box">
                  <div class="ribbon ribbon-primary float-start"><i class="mdi mdi-access-point me-1"></i> Primary</div>
                  <h5 class="text-primary float-end mt-0">Primary Header</h5>
                  <div class="ribbon-content">
                    <p class="mb-0">Quisque nec turpis at urna dictum luctus.
                      Suspendisse convallis dignissim eros at volutpat. In egestas
                      mattis dui. Aliquam mattis dictum aliquet. Nulla sapien
                      mauris, eleifend et sem ac, commodo dapibus odio.</p>
                  </div>
                </b-card> <!-- end card-->
              </b-col> <!-- end col -->

              <b-col xxl="4" md="6">
                <b-card class="ribbon-box">
                  <div class="ribbon ribbon-success float-end"><i class="mdi mdi-access-point me-1"></i> Success</div>
                  <h5 class="text-success float-start mt-0">Success Header</h5>
                  <div class="ribbon-content">
                    <p class="mb-0">Quisque nec turpis at urna dictum luctus.
                      Suspendisse convallis dignissim eros at volutpat. In egestas
                      mattis dui. Aliquam mattis dictum aliquet. Nulla sapien
                      mauris, eleifend et sem ac, commodo dapibus odio.</p>
                  </div>
                </b-card> <!-- end card-->
              </b-col> <!-- end col -->

              <b-col xxl="4" md="6">
                <b-card class="ribbon-box">
                  <div class="ribbon ribbon-info float-end"><i class="mdi mdi-access-point me-1"></i> Info</div>
                  <h5 class="text-info float-start mt-0">Info Header</h5>
                  <div class="ribbon-content">
                    <p class="mb-0">Quisque nec turpis at urna dictum luctus.
                      Suspendisse convallis dignissim eros at volutpat. In egestas
                      mattis dui. Aliquam mattis dictum aliquet. Nulla sapien
                      mauris, eleifend et sem ac, commodo dapibus odio.</p>
                  </div>
                </b-card> <!-- end card-->
              </b-col> <!-- end col -->

              <b-col xxl="4" md="6">
                <b-card class="ribbon-box">
                  <div class="ribbon ribbon-warning float-start"><i class="mdi mdi-access-point me-1"></i> Warning</div>
                  <h5 class="text-warning float-end mt-0">Warning Header</h5>
                  <div class="ribbon-content">
                    <p class="mb-0">Quisque nec turpis at urna dictum luctus.
                      Suspendisse convallis dignissim eros at volutpat. In egestas
                      mattis dui. Aliquam mattis dictum aliquet. Nulla sapien
                      mauris, eleifend et sem ac, commodo dapibus odio.</p>
                  </div>
                </b-card> <!-- end card-->
              </b-col> <!-- end col -->

              <b-col xxl="4" md="6">
                <b-card class="ribbon-box">
                  <div class="ribbon ribbon-danger float-end"><i class="mdi mdi-access-point me-1"></i> Danger</div>
                  <h5 class="text-danger float-start mt-0">Danger Header</h5>
                  <div class="ribbon-content">
                    <p class="mb-0">Quisque nec turpis at urna dictum luctus.
                      Suspendisse convallis dignissim eros at volutpat. In egestas
                      mattis dui. Aliquam mattis dictum aliquet. Nulla sapien
                      mauris, eleifend et sem ac, commodo dapibus odio.</p>
                  </div>
                </b-card> <!-- end card-->
              </b-col> <!-- end col -->

              <b-col xxl="4" md="6">
                <b-card class="ribbon-box">
                  <div class="ribbon ribbon-dark bg-dark text-light float-end"><i class="mdi mdi-access-point me-1"></i>
                    Dark
                  </div>
                  <h5 class="text-dark float-start mt-0">Dark Header</h5>
                  <div class="ribbon-content">
                    <p class="mb-0">Quisque nec turpis at urna dictum luctus.
                      Suspendisse convallis dignissim eros at volutpat. In egestas
                      mattis dui. Aliquam mattis dictum aliquet. Nulla sapien
                      mauris, eleifend et sem ac, commodo dapibus odio.</p>
                  </div>
                </b-card> <!-- end card-->
              </b-col> <!-- end col -->

              <b-col xxl="4" md="6">
                <b-card class="ribbon-box">
                  <div class="ribbon ribbon-secondary bg-secondary text-light float-start"><i
                      class="mdi mdi-access-point me-1"></i> Secondary
                  </div>
                  <h5 class="text-secondary float-end mt-0">Secondary Header</h5>
                  <div class="ribbon-content">
                    <p class="mb-0">Quisque nec turpis at urna dictum luctus.
                      Suspendisse convallis dignissim eros at volutpat. In egestas
                      mattis dui. Aliquam mattis dictum aliquet. Nulla sapien
                      mauris, eleifend et sem ac, commodo dapibus odio.</p>
                  </div>
                </b-card> <!-- end card-->
              </b-col> <!-- end col -->

              <b-col xxl="4" md="6">
                <b-card class="ribbon-box">
                  <div class="ribbon-two ribbon-two-primary"><span>Primary</span></div>
                  <p class="mb-0">Quisque nec turpis at urna dictum luctus. Suspendisse
                    convallis dignissim eros at volutpat. In egestas mattis dui. Aliquam
                    mattis dictum aliquet. Nulla sapien mauris, eleifend et sem ac,
                    commodo dapibus odio. Vivamus pretium nec odio cursus elementum.
                    Suspendisse molestie ullamcorper ornare.</p>
                </b-card> <!-- end card-->
              </b-col> <!-- end col -->

              <b-col xxl="4" md="6">
                <b-card class="ribbon-box">
                  <div class="ribbon-two ribbon-two-success"><span>Success</span></div>
                  <p class="mb-0">Quisque nec turpis at urna dictum luctus. Suspendisse
                    convallis dignissim eros at volutpat. In egestas mattis dui. Aliquam
                    mattis dictum aliquet. Nulla sapien mauris, eleifend et sem ac,
                    commodo dapibus odio. Vivamus pretium nec odio cursus elementum.
                    Suspendisse molestie ullamcorper ornare.</p>
                </b-card> <!-- end card-->
              </b-col> <!-- end col -->

              <b-col xxl="4" md="6">
                <b-card class="ribbon-box">
                  <div class="ribbon-two ribbon-two-info"><span>Info</span></div>
                  <p class="mb-0">Quisque nec turpis at urna dictum luctus. Suspendisse
                    convallis dignissim eros at volutpat. In egestas mattis dui. Aliquam
                    mattis dictum aliquet. Nulla sapien mauris, eleifend et sem ac,
                    commodo dapibus odio. Vivamus pretium nec odio cursus elementum.
                    Suspendisse molestie ullamcorper ornare.</p>
                </b-card> <!-- end card-->
              </b-col> <!-- end col -->

              <b-col xxl="4" md="6">
                <b-card class="ribbon-box">
                  <div class="ribbon-two ribbon-two-warning"><span>Warning</span></div>
                  <p class="mb-0">Quisque nec turpis at urna dictum luctus. Suspendisse
                    convallis dignissim eros at volutpat. In egestas mattis dui. Aliquam
                    mattis dictum aliquet. Nulla sapien mauris, eleifend et sem ac,
                    commodo dapibus odio. Vivamus pretium nec odio cursus elementum.
                    Suspendisse molestie ullamcorper ornare.</p>
                </b-card> <!-- end card-->
              </b-col> <!-- end col -->

              <b-col xxl="4" md="6">
                <b-card class="ribbon-box">
                  <div class="ribbon-two ribbon-two-dark"><span>Dark</span></div>
                  <p class="mb-0">Quisque nec turpis at urna dictum luctus. Suspendisse
                    convallis dignissim eros at volutpat. In egestas mattis dui. Aliquam
                    mattis dictum aliquet. Nulla sapien mauris, eleifend et sem ac,
                    commodo dapibus odio. Vivamus pretium nec odio cursus elementum.
                    Suspendisse molestie ullamcorper ornare.</p>
                </b-card> <!-- end card-->
              </b-col> <!-- end col -->

              <b-col xxl="4" md="6">
                <b-card class="ribbon-box">
                  <div class="ribbon-two ribbon-two-danger"><span>Danger</span></div>
                  <p class="mb-0">Quisque nec turpis at urna dictum luctus. Suspendisse
                    convallis dignissim eros at volutpat. In egestas mattis dui. Aliquam
                    mattis dictum aliquet. Nulla sapien mauris, eleifend et sem ac,
                    commodo dapibus odio. Vivamus pretium nec odio cursus elementum.
                    Suspendisse molestie ullamcorper ornare.</p>
                </b-card> <!-- end card-->
              </b-col> <!-- end col -->

              <b-col xxl="4" md="6">
                <b-card class="ribbon-box">
                  <div class="ribbon-two ribbon-two-secondary"><span class="bg-secondary text-light">Secondary</span>
                  </div>
                  <p class="mb-0">Quisque nec turpis at urna dictum luctus. Suspendisse
                    convallis dignissim eros at volutpat. In egestas mattis dui. Aliquam
                    mattis dictum aliquet. Nulla sapien mauris, eleifend et sem ac,
                    commodo dapibus odio. Vivamus pretium nec odio cursus elementum.
                    Suspendisse molestie ullamcorper ornare.</p>
                </b-card> <!-- end card-->
              </b-col> <!-- end col -->
            </b-row>
            <!-- end row -->
          </template>
        </CustomSyntax>

      </b-col>
    </b-row>
    <!-- end row-->

  </Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";
import CustomSyntax from "@/components/custom/custom-syntax.vue";

export default {
  components: {Layout, CustomSyntax, Breadcrumb},
  data() {
    return {
      title: 'Ribbons',
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
          text: 'Ribbons',
          active: true,
        },
      ],
    }
  }
}
</script>
