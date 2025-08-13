<template>
  <Layout>
    <Breadcrumb :title="title" :items="items"/>

    <b-row>
      <b-col xl="6">
        <CustomSyntax title="Default Accordions">
          <template v-slot:sub-text>
            Click the accordions below to expand/collapse the accordion content.
          </template>
          <template v-slot:preview>
            <b-accordion v-model="openAccordion1Id" id="accordionExample">
              <b-accordion-item id="1" title="Accordion Item #1">
                <div>
                  <strong>This is the first item's accordion body.</strong> It is
                  shown by default, until the collapse plugin adds the appropriate
                  classes that we use to style each element. These classes control
                  the overall appearance, as well as the showing and hiding via
                  CSS transitions. You can modify any of this with custom CSS or
                  overriding our default variables. It's also worth noting that
                  just about any HTML can go within the
                  <code>.accordion-body</code>, though the transition does limit
                  overflow.
                </div>
              </b-accordion-item>
              <b-accordion-item id="2" title="Accordion Item #2">
                <div>
                  <strong>This is the second item's accordion body.</strong> It is
                  hidden by default, until the collapse plugin adds the
                  appropriate classes that we use to style each element. These
                  classes control the overall appearance, as well as the showing
                  and hiding via CSS transitions. You can modify any of this with
                  custom CSS or overriding our default variables. It's also worth
                  noting that just about any HTML can go within the
                  <code>.accordion-body</code>, though the transition does limit
                  overflow.
                </div>
              </b-accordion-item>
              <b-accordion-item id="3" title="Accordion Item #3">
                <div>
                  <strong>This is the third item's accordion body.</strong> It is
                  hidden by default, until the collapse plugin adds the
                  appropriate classes that we use to style each element. These
                  classes control the overall appearance, as well as the showing
                  and hiding via CSS transitions. You can modify any of this with
                  custom CSS or overriding our default variables. It's also worth
                  noting that just about any HTML can go within the
                  <code>.accordion-body</code>, though the transition does limit
                  overflow.
                </div>
              </b-accordion-item>
            </b-accordion>
          </template>
        </CustomSyntax>
      </b-col>

      <b-col xl="6">
        <CustomSyntax title="Flush Accordions">
          <template v-slot:sub-text>
            Add <code>.accordion-flush</code> to remove the default <code>background-color</code>, some borders, and
            some rounded corners to render accordions edge-to-edge with their parent container.
          </template>
          <template v-slot:preview>
            <b-accordion :flush="true" id="accordionFlushExample">
              <b-accordion-item id="1" title="Accordion Item #1">
                <div>
                  Placeholder content for this accordion, which is intended to
                  demonstrate the <code>.accordion-flush</code> class. This is the
                  first item's accordion body.
                </div>
              </b-accordion-item>

              <b-accordion-item id="2" title="Accordion Item #2">
                <div>
                  Placeholder content for this accordion, which is intended to
                  demonstrate the <code>.accordion-flush</code> class. This is the
                  second item's accordion body. Let's imagine this being filled
                  with some actual content.
                </div>
              </b-accordion-item>

              <b-accordion-item id="3" title="Accordion Item #3">
                <div>
                  Placeholder content for this accordion, which is intended to
                  demonstrate the <code>.accordion-flush</code> class. This is the
                  third item's accordion body. Nothing more exciting happening
                  here in terms of content, but just filling up the space to make
                  it look, at least at first glance, a bit more representative of
                  how this would look in a real-world application.
                </div>
              </b-accordion-item>
            </b-accordion>
          </template>
        </CustomSyntax>
      </b-col>

    </b-row>
    <!-- end row-->

    <b-row>

      <b-col xl="6">
        <CustomSyntax title="Simple Card Accordions">
          <template v-slot:sub-text>
            Using the card component, you can extend the default collapse behavior to create an accordion. To properly
            achieve
            the accordion style, be sure to use <code>.accordion</code> as a wrapper.
          </template>
          <template v-slot:preview>
            <b-accordion v-model="openAccordion3Id" id="CardaccordionExample">
              <div id="1" class="card mb-0">
                <div class="card-header" id="CardheadingOne">
                  <h5 class="m-0">
                    <a class="text-reset d-block" v-b-toggle.CardcollapseOne>
                      Collapsible Group Item #1
                    </a>
                  </h5>
                </div>

                <b-collapse id="CardcollapseOne" visible>
                  <div class="card-body pt-0">
                    Anim pariatur cliche reprehenderit, enim eiusmod high life
                    accusamus terry richardson ad squid. 3 wolf moon officia aute,
                    non cupidatat skateboard dolor brunch. Food truck quinoa
                    nesciunt laborum eiusmod. Brunch 3 wolf moon tempor, sunt
                    aliqua put a bird on it squid single-origin coffee nulla
                    assumenda shoreditch et. Nihil anim keffiyeh helvetica, craft
                    beer labore wes anderson cred nesciunt sapiente ea proident.
                    Ad vegan excepteur butcher vice lomo. Leggings occaecat craft
                    beer farm-to-table, raw denim aesthetic synth nesciunt you
                    probably haven't heard of them accusamus labore susta inable
                    VHS.
                  </div>
                </b-collapse>
              </div>
              <div id="2" class="card mb-0">
                <div class="card-header" id="CardheadingTwo">
                  <h5 class="m-0">
                    <a class="text-reset d-block collapsed" v-b-toggle.CardcollapseTwo>
                      Collapsible Group Item #2
                    </a>
                  </h5>
                </div>
                <b-collapse id="CardcollapseTwo">
                  <div class="card-body pt-0">
                    Anim pariatur cliche reprehenderit, enim eiusmod high life
                    accusamus terry richardson ad squid. 3 wolf moon officia aute,
                    non cupidatat skateboard dolor brunch. Food truck quinoa
                    nesciunt laborum eiusmod. Brunch 3 wolf moon tempor, sunt
                    aliqua put a bird on it squid single-origin coffee nulla
                    assumenda shoreditch et. Nihil anim keffiyeh helvetica, craft
                    beer labore wes anderson cred nesciunt sapiente ea proident.
                    Ad vegan excepteur butcher vice lomo. Leggings occaecat craft
                    beer farm-to-table, raw denim aesthetic synth nesciunt you
                    probably haven't heard of them accusamus labore sustainable
                    VHS.
                  </div>
                </b-collapse>
              </div>
              <div id="3" class="card mb-0">
                <div class="card-header" id="CardheadingThree">
                  <h5 class="m-0">
                    <a class="text-reset d-block collapsed" v-b-toggle.CardcollapseThree>
                      Collapsible Group Item #3
                    </a>
                  </h5>
                </div>
                <b-collapse id="CardcollapseThree">
                  <div class="card-body pt-0">
                    Anim pariatur cliche reprehenderit, enim eiusmod high life
                    accusamus terry richardson ad squid. 3 wolf moon officia aute,
                    non cupidatat skateboard dolor brunch. Food truck quinoa
                    nesciunt laborum eiusmod. Brunch 3 wolf moon tempor, sunt
                    aliqua put a bird on it squid single-origin coffee nulla
                    assumenda shoreditch et. Nihil anim keffiyeh helvetica, craft
                    beer labore wes anderson cred nesciunt sapiente ea proident.
                    Ad vegan excepteur butcher vice lomo. Leggings occaecat craft
                    beer farm-to-table, raw denim aesthetic synth nesciunt you
                    probably haven't heard of them accusamus labore sustainable
                    VHS.
                  </div>
                </b-collapse>
              </div>
            </b-accordion>
          </template>
        </CustomSyntax>
      </b-col> <!-- end col-->

      <b-col xl="6">
        <CustomSyntax title="Always Open Accordions">
          <template v-slot:sub-text>
            Omit the <code>data-bs-parent</code> attribute on each <code>.accordion-collapse</code>
            to make accordion items stay open when another item is opened.
          </template>
          <template v-slot:preview>
            <b-accordion v-model="openAccordion3Id" :free="true" id="accordionPanelsStayOpenExample">
              <b-accordion-item id="1" title="Accordion Item #1">
                <div>
                  <strong>This is the first item's accordion body.</strong> It is
                  shown by default, until the collapse plugin adds the appropriate
                  classes that we use to style each element. These classes control
                  the overall appearance, as well as the showing and hiding via
                  CSS transitions. You can modify any of this with custom CSS or
                  overriding our default variables. It's also worth noting that
                  just about any HTML can go within the
                  <code>.accordion-body</code>, though the transition does limit
                  overflow.
                </div>
              </b-accordion-item>
              <b-accordion-item id="2" title="Accordion Item #2">
                <div>
                  <strong>This is the second item's accordion body.</strong> It is
                  hidden by default, until the collapse plugin adds the
                  appropriate classes that we use to style each element. These
                  classes control the overall appearance, as well as the showing
                  and hiding via CSS transitions. You can modify any of this with
                  custom CSS or overriding our default variables. It's also worth
                  noting that just about any HTML can go within the
                  <code>.accordion-body</code>, though the transition does limit
                  overflow.
                </div>
              </b-accordion-item>
              <b-accordion-item id="3" title="Accordion Item #3">
                <div>
                  <strong>This is the third item's accordion body.</strong> It is
                  hidden by default, until the collapse plugin adds the
                  appropriate classes that we use to style each element. These
                  classes control the overall appearance, as well as the showing
                  and hiding via CSS transitions. You can modify any of this with
                  custom CSS or overriding our default variables. It's also worth
                  noting that just about any HTML can go within the
                  <code>.accordion-body</code>, though the transition does limit
                  overflow.
                </div>
              </b-accordion-item>
            </b-accordion>
          </template>
        </CustomSyntax>
      </b-col> <!-- end col-->

    </b-row>
    <!-- end row-->

    <b-row>

      <b-col xl="6">
        <CustomSyntax title="Custom Accordions">
          <template v-slot:sub-text>
            You can have custom look and feel for accorion as well. Just use class <code>.custom-accordion</code>
            along with
            <code>.accordion</code> as a wrapper.
          </template>
          <template v-slot:preview>
            <b-accordion v-model="openAccordion4Id" :free="true" id="accordionPanelsStayOpenExample">
              <b-accordion-item id="1" title="Q. Can I use this template for my client?">
                <div>
                  Yup, the marketplace license allows you to use this theme
                  in any end products.
                  For more information on licenses, please refere <a href="https://themes.getbootstrap.com/licenses/">here</a>.
                </div>
              </b-accordion-item>
              <b-accordion-item id="2" title=" Q. Can this theme work with WordPress?">
                <div>
                  No. This is a HTML template. It won't directly with
                  WordPress, though you can convert this into WordPress
                  compatible theme
                </div>
              </b-accordion-item>
              <b-accordion-item id="3" title="Q. How do I get help with the theme?">
                <div>
                  Use our dedicated support email (support@coderthemes.com) to
                  send your issues or feedback. We are here to help anytime
                </div>
              </b-accordion-item>
            </b-accordion>
            <!-- <b-accordion>
                <div class="card mb-0">
                    <div class="card-header" id="headingFour">
                        <h5 class="m-0">
                            <a class="custom-accordion-title d-block" data-bs-toggle="collapse" href="#collapseFour" aria-expanded="true" aria-controls="collapseFour">
                                <i class="mdi mdi-chevron-down accordion-arrow"></i>
                            </a>
                        </h5>
                    </div>

                    <div id="collapseFour" class="collapse show" aria-labelledby="headingFour" data-bs-parent="#custom-accordion-one">
                        <div class="card-body">

                        </div>
                    </div>
                </div>
                <div class="card mb-0">
                    <div class="card-header" id="headingFive">
                        <h5 class="m-0">
                            <a class="custom-accordion-title collapsed d-block" data-bs-toggle="collapse" href="#collapseFive" aria-expanded="false" aria-controls="collapseFive">
                                <i class="mdi mdi-chevron-down accordion-arrow"></i>
                            </a>
                        </h5>
                    </div>
                    <div id="collapseFive" class="collapse" aria-labelledby="headingFive" data-bs-parent="#custom-accordion-one">
                        <div class="card-body">

                        </div>
                    </div>
                </div>
                <div class="card mb-0">
                    <div class="card-header" id="headingSix">
                        <h5 class="m-0">
                            <a class="custom-accordion-title collapsed d-block" data-bs-toggle="collapse" href="#collapseSix" aria-expanded="false" aria-controls="collapseSix">
                                <i class="mdi mdi-chevron-down accordion-arrow"></i>
                            </a>
                        </h5>
                    </div>
                    <div id="collapseSix" class="collapse" aria-labelledby="headingSix" data-bs-parent="#custom-accordion-one">
                        <div class="card-body">

                        </div>
                    </div>
                </div>
                <div class="card mb-0">
                    <div class="card-header" id="headingSeven">
                        <h5 class="m-0">
                            <a class="custom-accordion-title collapsed d-block" data-bs-toggle="collapse" href="#collapseSeven" aria-expanded="false" aria-controls="collapseSeven">
                                Q. Will you regularly give updates of Hyper ? <i class="mdi mdi-chevron-down accordion-arrow"></i>
                            </a>
                        </h5>
                    </div>
                    <div id="collapseSeven" class="collapse" aria-labelledby="headingSeven" data-bs-parent="#custom-accordion-one">
                        <div class="card-body">
                            Yes, We will update the Hyper regularly. All the
                            future updates would be available without any cost
                        </div>
                    </div>
                </div>
            </b-accordion> -->
          </template>
        </CustomSyntax>
      </b-col> <!-- end col-->

      <b-col xl="6">
        <CustomSyntax title="Collapse">
          <template v-slot:sub-text>
            Bootstrap's collapse provides the way to toggle the visibility of any content or element.
            Please read the official <a href="https://getbootstrap.com/docs/5.2/components/collapse/" target="_blank">Bootstrap</a>
            documentation for a full list of options.
          </template>
          <template v-slot:preview>
            <p>
              <a class="btn btn-primary" v-b-toggle.collapseExample>
                Link with href
              </a>
              <b-button class="ms-1" variant="primary" v-b-toggle="'collapseExample'">
                Button with data-bs-target
              </b-button>
            </p>
            <b-collapse visible id="collapseExample">
              <div class="card card-body mb-0">
                Anim pariatur cliche reprehenderit, enim eiusmod high life
                accusamus terry
                richardson ad squid. Nihil anim keffiyeh helvetica, craft beer
                labore wes
                anderson cred nesciunt sapiente ea proident.
              </div>
            </b-collapse>
          </template>
        </CustomSyntax>
      </b-col> <!-- end col-->

    </b-row>
    <!-- end row-->

    <b-row>

      <b-col xl="6">
        <CustomSyntax title="Collapse Horizontal">
          <template v-slot:sub-text>
            The collapse plugin also supports horizontal collapsing. Add the <code>.collapse-horizontal</code>
            modifier class to transition the <code>width</code> instead of <code>height</code> and set a
            <code>width</code> on the immediate child element.
          </template>
          <template v-slot:preview>
            <p>
              <b-button variant="primary" v-b-toggle.collapseWidthExample>
                Toggle width collapse
              </b-button>
            </p>
            <div style="min-height: 120px;">
              <b-collapse horizontal id="collapseWidthExample">
                <div class="card card-body mb-0" style="width: 300px;">
                  This is some placeholder content for a horizontal collapse. It's hidden by default and shown when
                  triggered.
                </div>
              </b-collapse>
            </div>
          </template>
        </CustomSyntax>
      </b-col> <!-- end col-->

      <b-col xl="6">
        <CustomSyntax title="Multiple Targets">
          <template v-slot:sub-text>
            Multiple <code>&lt;button&gt;</code> or <code>&lt;a&gt;</code> can show and hide an element if
            they each reference it with their <code>href</code> or <code>data-bs-target</code> attribute.
          </template>
          <template v-slot:preview>
            <p>
              <a class="btn btn-primary" v-b-toggle.multiCollapseExample1>Toggle first element</a>
              <b-button variant="primary" v-b-toggle.multiCollapseExample2>Toggle second element
              </b-button>
              <b-button variant="primary" v-b-toggle="'multiCollapseExample1 multiCollapseExample2'">Toggle both
                elements
              </b-button>
            </p>
            <b-row>
              <b-col>
                <b-collapse multi-collapse id="multiCollapseExample1">
                  <div class="card card-body mb-0">
                    Anim pariatur cliche reprehenderit, enim eiusmod high life accusamus terry richardson ad squid.
                    Nihil anim keffiyeh helvetica, craft beer labore wes anderson cred nesciunt sapiente ea
                    proident.
                  </div>
                </b-collapse>
              </b-col>
              <b-col>
                <b-collapse multi-collapse id="multiCollapseExample2">
                  <div class="card card-body mb-0">
                    Anim pariatur cliche reprehenderit, enim eiusmod high life accusamus terry richardson ad squid.
                    Nihil anim keffiyeh helvetica, craft beer labore wes anderson cred nesciunt sapiente ea
                    proident.
                  </div>
                </b-collapse>
              </b-col> <!-- end col -->
            </b-row>
          </template>
        </CustomSyntax>
      </b-col> <!-- end col-->

    </b-row> <!-- end row-->
  </Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";
import CustomSyntax from "@/components/custom/custom-syntax.vue";

export default {
  components: {CustomSyntax, Breadcrumb, Layout},

  data() {
    return {
      title: 'Accordions',
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
          text: 'Accordions',
          active: true,
        },
      ],

      openAccordion1Id: "1",
      openAccordion2Id: "1",
      openAccordion3Id: "1",
      openAccordion4Id: "1"
    };
  },
}
</script>
