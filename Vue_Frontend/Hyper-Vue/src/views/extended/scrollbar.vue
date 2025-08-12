<template>
  <Layout>
    <Breadcrumb :title="title" :items="items"/>

    <b-row>
      <b-col xl="6">
        <CustomSyntax title="Default Scroll">
          <template v-slot:sub-text>
            Just use data attribute <code>data-simplebar</code> and add
            <code>max-height: **px</code> oh fix height
          </template>
          <template v-slot:preview>
            <simplebar style="max-height: 250px">
              <div class="mb-3">
                SimpleBar does only one thing: replace the browser's default
                scrollbar with a custom CSS-styled one without losing
                performances. Unlike some popular plugins, SimpleBar doesn't mimic
                scroll with Javascript, causing janks and strange scrolling
                behaviours... You keep the awesomeness of native scrolling...with
                a custom scrollbar!
                <p>
                  SimpleBar
                  <strong>does NOT implement a custom scroll behaviour</strong>.
                  It keeps the <strong>native</strong>
                  <code>overflow: auto</code> scroll and
                  <strong>only</strong> replace the scrollbar visual appearance.
                </p>
                <h5>Design it as you want</h5>
                <p>
                  SimpleBar uses pure CSS to style the scrollbar. You can easily
                  customize it as you want! Or even have multiple style on the
                  same page...or just keep the default style ("Mac OS" scrollbar
                  style).
                </p>
                <h5>Lightweight and performant</h5>
                <p>
                  Only 6kb minified. SimpleBar doesn't use Javascript to handle
                  scrolling. You keep the performances/behaviours of the native
                  scroll.
                </p>
                <h5>Supported everywhere</h5>
                <p class="mb-0">
                  SimpleBar has been tested on the following browsers: Chrome,
                  Firefox, Safari, Edge, IE11.
                </p>
              </div>
            </simplebar>
          </template>
        </CustomSyntax>
      </b-col>

      <b-col xl="6">

        <CustomSyntax title="RTL Position">
          <template v-slot:sub-text>
            Just use data attribute
            <code>data-simplebar data-simplebar-direction='rtl'</code>
            and add <code>max-height: **px</code> oh fix height
          </template>
          <template v-slot:preview>
            <simplebar data-simplebar-direction="rtl" style="max-height: 250px">
              <div class="mb-3">
                SimpleBar does only one thing: replace the browser's default
                scrollbar with a custom CSS-styled one without losing
                performances. Unlike some popular plugins, SimpleBar doesn't mimic
                scroll with Javascript, causing janks and strange scrolling
                behaviours... You keep the awesomeness of native scrolling...with
                a custom scrollbar!
                <p>
                  SimpleBar
                  <strong>does NOT implement a custom scroll behaviour</strong>.
                  It keeps the <strong>native</strong>
                  <code>overflow: auto</code> scroll and
                  <strong>only</strong> replace the scrollbar visual appearance.
                </p>
                <h5>Design it as you want</h5>
                <p>
                  SimpleBar uses pure CSS to style the scrollbar. You can easily
                  customize it as you want! Or even have multiple style on the
                  same page...or just keep the default style ("Mac OS" scrollbar
                  style).
                </p>
                <h5>Lightweight and performant</h5>
                <p>
                  Only 6kb minified. SimpleBar doesn't use Javascript to handle
                  scrolling. You keep the performances/behaviours of the native
                  scroll.
                </p>
                <h5>Supported everywhere</h5>
                <p class="mb-0">
                  SimpleBar has been tested on the following browsers: Chrome,
                  Firefox, Safari, Edge, IE11.
                </p>
              </div>
            </simplebar>
          </template>
        </CustomSyntax>

      </b-col>
    </b-row>

    <b-row>
      <b-col xl="6">

        <CustomSyntax title="Scroll Size">
          <template v-slot:sub-text>
            Just use data attribute <code>data-simplebar</code> and add
            <code>max-height: **px</code> oh fix height
          </template>
          <template v-slot:preview>
            <simplebar
                id="data-simplebar-lg"
                data-simplebar
                data-simplebar-lg
                style="max-height: 250px"
            >
              <div class="py-0 mb-3">
                SimpleBar does only one thing: replace the browser's default
                scrollbar with a custom CSS-styled one without losing
                performances. Unlike some popular plugins, SimpleBar doesn't mimic
                scroll with Javascript, causing janks and strange scrolling
                behaviours... You keep the awesomeness of native scrolling...with
                a custom scrollbar!
                <p>
                  SimpleBar
                  <strong>does NOT implement a custom scroll behaviour</strong>.
                  It keeps the <strong>native</strong>
                  <code>overflow: auto</code> scroll and
                  <strong>only</strong> replace the scrollbar visual appearance.
                </p>
                <h5>Design it as you want</h5>
                <p>
                  SimpleBar uses pure CSS to style the scrollbar. You can easily
                  customize it as you want! Or even have multiple style on the
                  same page...or just keep the default style ("Mac OS" scrollbar
                  style).
                </p>
                <h5>Lightweight and performant</h5>
                <p>
                  Only 6kb minified. SimpleBar doesn't use Javascript to handle
                  scrolling. You keep the performances/behaviours of the native
                  scroll.
                </p>
                <h5>Supported everywhere</h5>
                <p class="mb-0">
                  SimpleBar has been tested on the following browsers: Chrome,
                  Firefox, Safari, Edge, IE11.
                </p>
              </div>
            </simplebar>
          </template>
        </CustomSyntax>

      </b-col>

      <b-col xl="6">

        <CustomSyntax title="Scroll Color">
          <template v-slot:sub-text>
            Just use data attribute
            <code>data-simplebar data-simplebar-primary</code>
            and add <code>max-height: **px</code> oh fix height
          </template>
          <template v-slot:preview>
            <simplebar
                id="data-simplebar-primary"
                data-simplebar
                data-simplebar-primary
                style="max-height: 250px"
            >
              <div class="py-0 mb-3">
                SimpleBar does only one thing: replace the browser's default
                scrollbar with a custom CSS-styled one without losing
                performances. Unlike some popular plugins, SimpleBar doesn't mimic
                scroll with Javascript, causing janks and strange scrolling
                behaviours... You keep the awesomeness of native scrolling...with
                a custom scrollbar!
                <p>
                  SimpleBar
                  <strong>does NOT implement a custom scroll behaviour</strong>.
                  It keeps the <strong>native</strong>
                  <code>overflow: auto</code> scroll and
                  <strong>only</strong> replace the scrollbar visual appearance.
                </p>
                <h5>Design it as you want</h5>
                <p>
                  SimpleBar uses pure CSS to style the scrollbar. You can easily
                  customize it as you want! Or even have multiple style on the
                  same page...or just keep the default style ("Mac OS" scrollbar
                  style).
                </p>
                <h5>Lightweight and performant</h5>
                <p>
                  Only 6kb minified. SimpleBar doesn't use Javascript to handle
                  scrolling. You keep the performances/behaviours of the native
                  scroll.
                </p>
                <h5>Supported everywhere</h5>
                <p class="mb-0">
                  SimpleBar has been tested on the following browsers: Chrome,
                  Firefox, Safari, Edge, IE11.
                </p>
              </div>
            </simplebar>
          </template>
        </CustomSyntax>

      </b-col>
    </b-row>
  </Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";

import simplebar from "simplebar-vue";
import CustomSyntax from "@/components/custom/custom-syntax.vue";

export default {
  components: {
    CustomSyntax,
    Breadcrumb,
    Layout,
    simplebar
  },
  data() {
    return {
      title: 'Scrollbar',
      items: [
        {
          text: 'Hyper',
          href: '/',
        },
        {
          text: 'Extended UI',
          href: '/',
        },
        {
          text: 'Scrollbar',
          active: true,
        },
      ],
    }
  },
};
</script>
