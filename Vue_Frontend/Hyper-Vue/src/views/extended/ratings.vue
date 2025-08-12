<template>
  <Layout>
    <Breadcrumb :title="title" :items="items"/>

    <b-row>
      <b-col xl="6">

        <CustomSyntax title="Default Ratings">
          <template v-slot:sub-text>
          </template>
          <template v-slot:preview>
            <CustomRating data-rateit-mode="font"/>
          </template>
        </CustomSyntax>

        <CustomSyntax title="Icon Font - Change icon">
          <template v-slot:sub-text>
          </template>
          <template v-slot:preview>
            <CustomRating data-rateit-icon="@" data-rateit-mode="font"/>
          </template>
        </CustomSyntax>

        <CustomSyntax title="Progressive enhancement (using select)">
          <template v-slot:sub-text>
          </template>
          <template v-slot:preview>
            <select id="backing3b">
              <option value="0">Bad</option>
              <option value="1" selected="selected">OK</option>
              <option value="2">Good</option>
              <option value="3">Great</option>
              <option value="4">Excellent</option>
            </select>
            <CustomRating class="rateit-mdi" data-rateit-backingfld="#backing3b" data-rateit-mode="font"
                          data-rateit-icon="󰓒"/>
          </template>
        </CustomSyntax>

        <CustomSyntax title="Javascript interaction">
          <template v-slot:sub-text>
          </template>
          <template v-slot:preview>
            <CustomRating class="rateit-mdi" id="js-interaction" data-rateit-min="2" data-rateit-mode="font"
                          data-rateit-icon="󰓒"/>
            <div>
              <span id="jsvalue"></span>
              <span id="jshover"></span>
            </div>
          </template>
        </CustomSyntax>

        <CustomSyntax title="RTL support">
          <template v-slot:sub-text>
            Now we are in RTL mode. No changes needed to make this work
          </template>
          <template v-slot:preview>
            <div style="direction: rtl">
              <CustomRating class="rateit-mdi" data-rateit-mode="font" data-rateit-icon="󰓒"/>
            </div>
          </template>
        </CustomSyntax>

      </b-col>

      <b-col xl="6">

        <CustomSyntax title="MATERIAL DESIGN ICONS">
          <template v-slot:sub-text>
          </template>
          <template v-slot:preview>
            <CustomRating class="rateit-mdi" data-rateit-mode="font" data-rateit-icon="󰓒"/>
            <br/>
            <CustomRating class="rateit-mdi mt-3" data-rateit-mode="font" data-rateit-icon="󰋕"/>
          </template>
        </CustomSyntax>

        <CustomSyntax title="Icon Font - Sizing">
          <template v-slot:sub-text>
          </template>
          <template v-slot:preview>
            <CustomRating class="rateit-mdi" data-rateit-mode="font" data-rateit-icon="󰓒" style="font-size: 36px;"/>
          </template>
        </CustomSyntax>

        <CustomSyntax title="Readonly and preset value">
          <template v-slot:sub-text>
          </template>
          <template v-slot:preview>
            <CustomRating class="rateit-mdi" data-rateit-mode="font" data-rateit-icon="󰓒"  data-rateit-value="2.5" data-rateit-ispreset="true" data-rateit-readonly="true"/>
          </template>
        </CustomSyntax>

        <CustomSyntax title="Setting and Getting values">
          <template v-slot:sub-text>
            All properties can also be set on the fly. Here are a few examples:
          </template>
          <template v-slot:preview>
            <CustomRating class="rateit-mdi" data-rateit-mode="font" data-rateit-icon="󰓒" id="getting-values"/>
            <div class="d-flex flex-wrap gap-2 mt-3">
              <b-button
                  size="sm"
                  variant="primary"
                  onclick="alert($('#getting-values').rateit('value'))"
              >Get value
              </b-button
              >
              <b-button
                  size="sm"
                  variant="primary"
                  onclick="$('#getting-values').rateit('value', prompt('Input numerical value'))"
              >Set value
              </b-button
              >
              <b-button
                  size="sm"
                  variant="primary"
                  onclick="alert($('#getting-values').rateit('max'))"
              >Get max value
              </b-button
              >
              <b-button
                  size="sm"
                  variant="primary"
                  onclick="$('#getting-values').rateit('max', prompt('Input numerical value'))"
              >Set max value
              </b-button
              >
              <b-button
                  size="sm"
                  variant="primary"
                  onclick="alert($('#getting-values').rateit('step'))"
              >Get step size
              </b-button
              >
              <b-button
                  size="sm"
                  variant="primary"
                  onclick="$('#getting-values').rateit('step', prompt('Input numerical value'))"
              >Set step size
              </b-button
              >
              <b-button
                  size="sm"
                  variant="primary"
                  onclick="alert($('#getting-values').rateit('readonly'))"
              >Get readonly value
              </b-button
              >
              <b-button
                  size="sm"
                  variant="primary"
                  onclick="$('#getting-values').rateit('readonly',!$('#getting-values').rateit('readonly'))"
              >Toggle readonly
              </b-button
              >
              <b-button
                  size="sm"
                  variant="primary"
                  onclick="alert($('#getting-values').rateit('ispreset'))"
              >Get ispreset value
              </b-button
              >
              <b-button
                  size="sm"
                  variant="primary"
                  onclick="$('#getting-values').rateit('ispreset',!$('#getting-values').rateit('ispreset'))"
              >Toggle ispreset
              </b-button
              >
              <b-button
                  size="sm"
                  variant="primary"
                  onclick="$('#getting-values').rateit('reset')"
              >Reset
              </b-button
              >
            </div>
          </template>
        </CustomSyntax>

      </b-col>
    </b-row>
  </Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";

import "jquery.rateit";
import CustomRating from "@/components/custom/custom-rating.vue";
import CustomSyntax from "@/components/custom/custom-syntax.vue";

export default {
  components: {
    CustomSyntax,
    CustomRating,
    Layout,
    Breadcrumb,
  },
  data() {
    return {
      title: 'Ratings',
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
          text: 'Ratings',
          active: true,
        },
      ],

      rating: 0,
    };
  },
  mounted() {

    // Rated
    $("#js-interaction").bind("rated", function (event, value) {
      $("#jsvalue").text("You've rated it: " + value);
    });

    // Reset
    $("#js-interaction").bind("reset", function () {
      $("#jsvalue").text("Rating reset");
    });

    // Over
    $("#js-interaction").bind("over", function (event, value) {
      $("#jshover").text("Hovering over: " + value);
    });
  },
};
</script>
