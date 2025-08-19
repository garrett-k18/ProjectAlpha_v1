<template>
  <Layout>
    <Breadcrumb :title="title" :items="items"/>

    <b-row>
      <b-col lg="6">
        <CustomSyntax title="Slides only">
          <template v-slot:sub-text>
          </template>
          <template v-slot:preview>
            <b-carousel v-model="slide" id="carouselExampleSlidesOnly" @sliding-start="onSlideStart">
              <b-carousel-slide img-src="@/assets/images/small/small-1.jpg">
                <template #img>
                  <img class="d-block img-fluid" src="@/assets/images/small/small-1.jpg" alt=""/></template>
              </b-carousel-slide>
              <b-carousel-slide>
                <template #img>
                  <img class="d-block img-fluid" src="@/assets/images/small/small-2.jpg" alt=""/></template>
              </b-carousel-slide>
              <b-carousel-slide>
                <template #img>
                  <img class="d-block img-fluid" src="@/assets/images/small/small-3.jpg" alt=""/></template>
              </b-carousel-slide>
            </b-carousel>
          </template>
        </CustomSyntax>
      </b-col>

      <b-col lg="6">
        <CustomSyntax title="With controls">
          <template v-slot:sub-text>

          </template>
          <template v-slot:preview>
            <b-carousel v-model="slide1" controls id="carouselExampleControls">
              <b-carousel-slide>
                <template #img>
                  <img class="d-block img-fluid" src="@/assets/images/small/small-4.jpg" alt="First slide"/>
                </template>
              </b-carousel-slide>
              <b-carousel-slide>
                <template #img>
                  <img class="d-block img-fluid" src="@/assets/images/small/small-1.jpg" alt="Second slide"/>
                </template>
              </b-carousel-slide>
              <b-carousel-slide>
                <template #img>
                  <img class="d-block img-fluid" src="@/assets/images/small/small-2.jpg" alt="Third slide"/>
                </template>
              </b-carousel-slide>
            </b-carousel>
          </template>
        </CustomSyntax>
      </b-col>
    </b-row>
    <!-- end row -->

    <b-row>
      <b-col lg="6">
        <CustomSyntax title="With indicators">
          <template v-slot:sub-text>
          </template>
          <template v-slot:preview>
            <b-carousel
                v-model="slide2"
                :interval="4000"
                controls
                indicators
                id="carouselExampleIndicators"
            >
              <b-carousel-slide>
                <template #img>
                  <img
                      class="d-block img-fluid"
                      src="@/assets/images/small/small-3.jpg"
                      alt="First slide"
                  /></template>
              </b-carousel-slide>
              <b-carousel-slide>
                <template #img>
                  <img
                      class="d-block img-fluid"
                      src="@/assets/images/small/small-2.jpg"
                      alt="Second slide"
                  /></template>
              </b-carousel-slide>
              <b-carousel-slide>
                <template #img>
                  <img
                      class="d-block img-fluid"
                      src="@/assets/images/small/small-1.jpg"
                      alt="Third slide"
                  /></template>
              </b-carousel-slide>
            </b-carousel>
          </template>
        </CustomSyntax>
      </b-col> <!-- end col -->

      <b-col lg="6">
        <CustomSyntax title="With captions">
          <template v-slot:sub-text>
          </template>
          <template v-slot:preview>
            <b-carousel
                v-model="slide3"
                :interval="4000"
                controls
                id="carouselExampleCaption"
            >
              <b-carousel-slide
                  caption="First slide label"
                  text="Lorem ipsum dolor sit amet, consectetur adipiscing elit."
              >
                <template #img>
                  <img
                      src="@/assets/images/small/small-1.jpg"
                      alt="..."
                      class="d-block img-fluid"
                  />
                </template>
              </b-carousel-slide>
              <b-carousel-slide
                  caption="Second slide label"
                  text="Lorem ipsum dolor sit amet, consectetur adipiscing elit."
              >
                <template #img>
                  <img
                      src="@/assets/images/small/small-3.jpg"
                      alt="..."
                      class="d-block img-fluid"
                  />
                </template>
              </b-carousel-slide>
              <b-carousel-slide
                  caption="Third slide label"
                  text="Lorem ipsum dolor sit amet, consectetur adipiscing elit."
              >
                <template #img>
                  <img
                      src="@/assets/images/small/small-2.jpg"
                      alt="..."
                      class="d-block img-fluid"
                  /></template>
              </b-carousel-slide>
            </b-carousel>
          </template>
        </CustomSyntax>
      </b-col> <!-- end col -->

    </b-row>
    <!-- end row -->

    <b-row>
      <b-col lg="6">
        <CustomSyntax title="Crossfade">
          <template v-slot:sub-text>

          </template>
          <template v-slot:preview>
            <b-carousel
                v-model="slide4"
                :interval="4000"
                controls
                id="carouselExampleFade"
                fade
            >
              <b-carousel-slide>
                <template #img>
                  <img
                      class="d-block img-fluid"
                      src="@/assets/images/small/small-1.jpg"
                      alt="First slide"
                  /></template>
              </b-carousel-slide>
              <b-carousel-slide>
                <template #img>
                  <img
                      class="d-block img-fluid"
                      src="@/assets/images/small/small-2.jpg"
                      alt="Second slide"
                  /></template>
              </b-carousel-slide>
              <b-carousel-slide>
                <template #img>
                  <img
                      class="d-block img-fluid"
                      src="@/assets/images/small/small-3.jpg"
                      alt="Third slide"
                  /></template>
              </b-carousel-slide>
            </b-carousel>
          </template>
        </CustomSyntax>
      </b-col> <!-- end col -->

      <b-col lg="6">
        <CustomSyntax title="Individual interval">
          <template v-slot:sub-text>

          </template>
          <template v-slot:preview>
            <b-carousel
                v-model="intervalSlide"
                controls
                id="carouselExampleInterval"
            >
              <b-carousel-slide>
                <template #img>
                  <img
                      src="@/assets/images/small/small-4.jpg"
                      class="img-fluid d-block w-100"
                      alt="First slide"
                  /></template>
              </b-carousel-slide>
              <b-carousel-slide>
                <template #img>
                  <img
                      src="@/assets/images/small/small-2.jpg"
                      class="img-fluid d-block w-100"
                      alt="Second slide"
                  /></template>
              </b-carousel-slide>
              <b-carousel-slide>
                <template #img>
                  <img
                      src="@/assets/images/small/small-1.jpg"
                      class="img-fluid d-block w-100"
                      alt="Third slide"
                  /></template>
              </b-carousel-slide>
            </b-carousel>
          </template>
        </CustomSyntax>
      </b-col> <!-- end col -->

      <b-col lg="6">
        <CustomSyntax title="Dark variant">
          <template v-slot:sub-text>
          </template>
          <template v-slot:preview>
            <b-carousel
                v-model="slide6"
                controls
                indicators
                id="carouselExampleDark"
                class="carousel-dark"
            >
              <b-carousel-slide
                  caption="First slide label"
                  text="Some representative placeholder content for the first slide."
                  :interval="10000"
              >
                <template #img>
                  <img
                      src="@/assets/images/small/small-5.jpg"
                      class="img-fluid"
                      alt="Images"
                  /></template>
              </b-carousel-slide>
              <b-carousel-slide
                  caption="Second slide label"
                  text="Some representative placeholder content for the first slide."
                  :interval="2000"
              >
                <template #img>
                  <img
                      src="@/assets/images/small/small-6.jpg"
                      class="img-fluid"
                      alt="Images"
                  /></template>
              </b-carousel-slide>
              <b-carousel-slide
                  caption="Third slide label"
                  text="Some representative placeholder content for the first slide."
              >
                <template #img>
                  <img
                      src="@/assets/images/small/small-7.jpg"
                      class="img-fluid"
                      alt="Images"
                  /></template>
              </b-carousel-slide>
            </b-carousel>
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
  components: {Layout, Breadcrumb, CustomSyntax},
  data() {
    return {
      title: 'Carousel',
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
          text: 'Carousel',
          active: true,
        },
      ],
      slide: 0,
      slide1: 0,
      slide2: 0,
      slide3: 0,
      slide4: 0,
      slide6: 0,
      intervalSlide: 0,
    }
  },
  methods: {
    // Handle BootstrapVue 3 <b-carousel> 'sliding-start' event.
    // The event payload is the target slide index (number).
    // We mirror it into this.slide to keep v-model in sync when needed.
    onSlideStart(newIndex: number) {
      this.slide = newIndex
    },
  },
  mounted() {
    setInterval(() => {
      if (this.slide < 2) {
        this.slide += 1
      } else {
        this.slide = 0
      }
    }, 3000)

    setInterval(() => {
      if (this.intervalSlide < 2) {
        this.intervalSlide += 1
      } else {
        this.intervalSlide = 0
      }
    }, 3000)
  }
}
</script>
