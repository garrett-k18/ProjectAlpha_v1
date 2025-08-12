<template>
  <Layout>
    <Breadcrumb :title="title" :items="items"/>

    <b-row>
      <b-col xl="6">
        <CustomSyntax title="Examples">
          <template v-slot:sub-text>
            Hover over the links below to see tooltips.
          </template>
          <template v-slot:preview>
            <p class="muted mb-0">
              Tight pants next level keffiyeh <a href="#" v-b-tooltip.hover title="Default tooltip">you probably</a>
              haven't heard
              of them. Photo booth beard raw denim letterpress vegan messenger bag
              stumptown. Farm-to-table Photo booth beard seitan, mcsweeney's fixie sustainable quinoa
              8-bit american apparel <a href="#" v-b-tooltip.hover title="Another tooltip">have a</a> terry richardson
              vinyl chambray. Beard stumptown, cardigans banh mi lomo thundercats.
              Tofu biodiesel williamsburg marfa, four loko mcsweeney's cleanse vegan
              chambray. A really ironic artisan <a href="#" v-b-tooltip.hover title="Another one here too">whatever
            </a> keytar, scenester farm-to-table banksy Austin <a href="#" v-b-tooltip.hover title="The last tip!">twitter
              handle</a> freegan cred
              raw denim single-origin coffee viral.
            </p>
          </template>
        </CustomSyntax>

        <CustomSyntax title="Disabled elements">
          <template v-slot:sub-text>
            Elements with the <code>disabled</code> attribute
            aren’t interactive, meaning users cannot focus, hover, or click them to trigger
            a tooltip (or popover). As a workaround, you’ll want to trigger the tooltip from
            a wrapper <code>&lt;div&gt;</code> or <code>&lt;span&gt;</code>, ideally made
            keyboard-focusable using <code>tabindex="0"</code>, and override the
            <code>pointer-events</code> on the disabled element.
          </template>
          <template v-slot:preview>
            <div>
                        <span class="d-inline-block" tabindex="0" v-b-tooltip.hover title="Disabled tooltip">
                            <button class="btn btn-primary pe-none" type="button" disabled>Disabled button</button>
                        </span>
            </div>
          </template>
        </CustomSyntax>

      </b-col> <!-- end col -->

      <b-col xl="6">
        <CustomSyntax title="Four Directions">
          <template v-slot:sub-text>
            Hover over the buttons below to see the four tooltips
            directions: top, right, bottom, and left.
          </template>
          <template v-slot:preview>
            <div class="d-flex flex-wrap gap-2">
              <b-button variant="info" v-b-tooltip.hover.top title="Tooltip on top">Tooltip on top</b-button>
              <b-button id="button-2 " variant="info" v-b-tooltip.hover.bottom title="Tooltip on bottom">Tooltip on
                bottom
              </b-button>
              <b-button variant="info" v-b-tooltip.hover.left title="Tooltip on left">Tooltip on left</b-button>
              <b-button variant="info" v-b-tooltip.hover.right title="Tooltip on right">Tooltip on right</b-button>
            </div>
          </template>
        </CustomSyntax>

        <CustomSyntax title="HTML Tags">
          <template v-slot:sub-text>
            And with custom HTML added:
          </template>
          <template v-slot:preview>
            <button type="button" class="btn btn-secondary" v-b-tooltip.hover
                    title="<em>Tooltip</em> <u>with</u> <b>HTML</b>">
              Tooltip with HTML
            </button>
          </template>
        </CustomSyntax>

        <CustomSyntax title="Color Tooltips">
          <template v-slot:sub-text>
            We set a custom class with ex. <code>data-bs-custom-class="primary-tooltip"</code> to scope our
            background-color primary appearance and use
            it to override a local CSS
            variable.
          </template>
          <template v-slot:preview>
            <div class="d-flex flex-wrap gap-2">
              <b-button variant="primary" id="tooltip1">
                Primary tooltip
              </b-button>
              <b-tooltip target="tooltip1" class="primary-tooltip">This top tooltip is themed via CSS variables.
              </b-tooltip>

              <b-button variant="danger" id="tooltip2"> Danger tooltip</b-button>
              <b-tooltip target="tooltip2" class="danger-tooltip">This top tooltip is themed via CSS variables.
              </b-tooltip>

              <b-button variant="info" id="tooltip3"> Info tooltip</b-button>
              <b-tooltip target="tooltip3" class="info-tooltip">This top tooltip is themed via CSS variables.
              </b-tooltip>

              <b-button variant="success" id="tooltip4">
                Success tooltip
              </b-button>
              <b-tooltip target="tooltip4" class="success-tooltip">This top tooltip is themed via CSS variables.
              </b-tooltip>
            </div>
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

export default {
  components: {Layout, CustomSyntax, Breadcrumb},
  data() {
    return {
      title: 'Tooltips',
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
          text: 'Tooltips',
          active: true,
        },
      ],
    }
  },
}
</script>
