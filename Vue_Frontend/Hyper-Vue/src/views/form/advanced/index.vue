<template>
  <Layout>
    <Breadcrumb :title="title" :items="items"/>

    <b-row>
      <b-col cols="12">
        <CustomSyntax title="Select2">
          <template v-slot:sub-text>
            Select2 gives you a customizable select box with support for searching,
            tagging, remote data sets, infinite scrolling, and many other highly
            used options.
          </template>
          <template v-slot:preview>
            <b-row>
              <b-col lg="6">
                <p class="mb-1 fw-bold text-muted">Single Select</p>
                <p class="text-muted fs-14">
                  Select2 can take a regular select box like this...
                </p>

                <VueMultiselect v-model="selected" :options="multiSelectOptions" :searchable="true">
                </VueMultiselect>
              </b-col>

              <b-col lg="6">
                <p class="mb-1 fw-bold text-muted">Multiple Select</p>
                <p class="text-muted fs-14">
                  Select2 can take a regular select box like this...
                </p>

                <VueMultiselect
                    v-model="selected1"
                    :options="multiSelectOptions"
                    :multiple="true"
                    :searchable="true"
                >
                </VueMultiselect>
              </b-col>
            </b-row>
          </template>
        </CustomSyntax>
      </b-col>
    </b-row>

    <b-row>
      <b-col cols="12">
        <CustomSyntax title="Date Range Picker">
          <template v-slot:sub-text>
            A JavaScript component for choosing date ranges, dates and times.
          </template>
          <template v-slot:preview>
            <b-row>
              <b-col lg="6">
                <b-form-group label="Date Range" class="mb-3">
                  <DateRangePicker id="singledaterange" data-toggle="date-picker" data-cancel-class="btn-warning"/>
                </b-form-group>
              </b-col>

              <b-col lg="6">
                <b-form-group label="Date Range Picker With Times" class="mb-3">
                  <DateRangePicker id="daterangetime" data-toggle="date-picker" data-time-picker="true"
                                   data-locale="{'format': 'DD/MM hh:mm A'}"/>
                </b-form-group>
              </b-col>
            </b-row>

            <b-row>
              <b-col lg="6">
                <b-form-group label="Single Date Picker">
                  <DateRangePicker id="birthdatepicker" data-toggle="date-picker" data-single-date-picker="true"/>
                </b-form-group>
              </b-col>

              <b-col lg="6">
                <div>
                  <label class="form-label">Predefined Date Ranges</label>
                  <div id="reportrange" class="form-control" data-toggle="date-picker-range" data-target-display="#selectedValue"  data-cancel-class="btn-light">
                    <i class="mdi mdi-calendar"></i>&nbsp;
                    <span id="selectedValue"></span> <i class="mdi mdi-menu-down"></i>
                  </div>
                </div>
              </b-col>
            </b-row>
          </template>
        </CustomSyntax>

      </b-col>
    </b-row>

    <b-row>
      <b-col cols="12">

        <CustomSyntax title="Switch">
          <template v-slot:sub-text>
            Here are a few types of switches.
          </template>
          <template v-slot:preview>
            <div class="pt-2">
              <!-- without label-->
              <input type="checkbox" id="switch0" data-switch="none"/>
              <label class="me-1" for="switch0" data-on-label="" data-off-label=""></label>

              <!-- Bool Switch-->
              <input type="checkbox" id="switch1" checked data-switch="bool"/>
              <label class="me-1" for="switch1" data-on-label="On" data-off-label="Off"></label>

              <!-- Primary Switch-->
              <input type="checkbox" id="switch2" checked data-switch="primary"/>
              <label class="me-1" for="switch2" data-on-label="On" data-off-label="Off"></label>

              <!-- Success Switch-->
              <input type="checkbox" id="switch3" checked data-switch="success"/>
              <label class="me-1" for="switch3" data-on-label="Yes" data-off-label="No"></label>

              <!-- Info Switch-->
              <input type="checkbox" id="switch4" checked data-switch="info"/>
              <label class="me-1" for="switch4" data-on-label="On" data-off-label="Off"></label>

              <!-- Warning Switch-->
              <input type="checkbox" id="switch5" checked data-switch="warning"/>
              <label class="me-1" for="switch5" data-on-label="Yes" data-off-label="No"></label>

              <!-- Danger Switch-->
              <input type="checkbox" id="switch6" checked data-switch="danger"/>
              <label class="me-1" for="switch6" data-on-label="On" data-off-label="Off"></label>

              <!-- Dark Switch-->
              <input type="checkbox" id="switch7" checked data-switch="secondary"/>
              <label class="me-1" for="switch7" data-on-label="Yes" data-off-label="No"></label>

              <!-- Disbled Switch-->
              <input type="checkbox" id="switchdis" data-switch="primary" checked disabled/>
              <label class="me-1" for="switchdis" data-on-label="On" data-off-label="Off"></label>
            </div>
          </template>
        </CustomSyntax>

      </b-col>
      <!-- end col -->
    </b-row>
    <!-- end row -->

    <b-row>
      <b-col cols="12">

        <CustomSyntax title="Bootstrap Datepicker">
          <template v-slot:sub-text>
            Bootstrap-datepicker provides a flexible datepicker widget in the
            Bootstrap style.
          </template>
          <template v-slot:preview>
            <b-row>
              <b-col lg="6">
                <b-form-group
                    label="Date Picker"
                    class="mb-3 position-relative"
                    id="datepicker1"
                >
                  <BootstrapDatepicker type="text" placeholder="Select Date" data-provide="datepicker"
                                       data-date-format="d-M-yyyy" data-date-container="#datepicker1"/>
                </b-form-group>
              </b-col>

              <b-col lg="6">
                <b-form-group
                    label="Date View"
                    class="mb-3 position-relative"
                    id="datepicker2"
                >
                  <BootstrapDatepicker type="text" placeholder="Select Date" data-provide="datepicker"
                                       data-date-format="d-M-yyyy" data-date-container="#datepicker2"/>
                </b-form-group>
              </b-col>
            </b-row>

            <b-row>
              <b-col lg="6">
                <b-form-group
                    label="Multi Datepicker"
                    class="mb-3 position-relative"
                    id="datepicker3"

                >
                  <BootstrapDatepicker type="text" placeholder="Select Date" data-provide="datepicker"
                                       data-date-multidate="true" data-date-container="#datepicker3"/>
                </b-form-group>
              </b-col>

              <b-col lg="6">
                <b-form-group
                    label="Autoclose"
                    class="mb-3 position-relative"
                    id="datepicker4"
                >
                  <BootstrapDatepicker type="text" placeholder="Select Date" data-provide="datepicker"
                                       data-date-autoclose="true"
                                       data-date-container="#datepicker4"/>
                </b-form-group>
              </b-col>
            </b-row>

            <b-row>
              <b-col lg="6">
                <b-form-group
                    label="Month View"
                    class="mb-3 position-relative"
                    id="datepicker5"
                >
                  <BootstrapDatepicker type="text" placeholder="Select Month" data-provide="datepicker"
                                       data-date-format="MM yyyy" data-date-min-view-mode="1"
                                       data-date-container="#datepicker5"/>
                </b-form-group>
              </b-col>

              <b-col lg="6">
                <b-form-group
                    label="Year View"
                    class="mb-3 position-relative"
                    id="datepicker6"
                >
                  <BootstrapDatepicker type="text" placeholder="Select Year" data-provide="datepicker"
                                       data-date-min-view-mode="2" data-date-container="#datepicker6"/>
                </b-form-group>
              </b-col>
            </b-row>

            <b-row>
              <b-col lg="6">
                <div>
                  <label class="form-label">Inline Datepicker</label>
                  <div data-provide="datepicker-inline"></div>
                </div>
              </b-col>
            </b-row>
          </template>
        </CustomSyntax>

      </b-col>
    </b-row>

    <b-row>
      <b-col cols="12">

        <CustomSyntax title="Flatpickr - Date picker">
          <template v-slot:sub-text>
            A lightweight and powerful datetimepicker
          </template>
          <template v-slot:preview>
            <b-row>
              <b-col lg="6">
                <b-form-group label="Basic" class="mb-3">
                  <Flatpickr id="basic-datepicker" placeholder="Basic datepicker"/>
                </b-form-group>

                <b-form-group label="Date & Time" class="mb-3">
                  <Flatpickr id="datetime-datepicker" placeholder="Date and Time" :options="flatpickrOptions2"/>
                </b-form-group>

                <b-form-group label="Human-friendly Dates" class="mb-3">
                  <Flatpickr id="humanfd-datepicker" placeholder="October 9, 2018" :options="flatpickrOptions3"/>
                </b-form-group>

                <b-form-group label="MinDate and MaxDate" class="mb-3">
                  <Flatpickr id="minmax-datepicker" placeholder="mindate - maxdate" :options="flatpickrOptions4"/>
                </b-form-group>

                <b-form-group label="Disabling dates" class="mb-3">
                  <Flatpickr id="disable-datepicker" placeholder="Disabling dates" :options="flatpickrOptions5"/>
                </b-form-group>

                <b-form-group label="Selecting multiple dates" class="mb-3">
                  <Flatpickr id="multiple-datepicker" placeholder="Multiple dates" :options="flatpickrOptions6"/>
                </b-form-group>
              </b-col>

              <b-col lg="6" class="mt-3 mt-lg-0">
                <b-form-group
                    label="Selecting multiple dates - Conjunction"
                    class="mb-3"
                >
                  <Flatpickr id="conjunction-datepicker" placeholder="2018-10-10 :: 2018-10-11"
                             :options="flatpickrOptions7"/>
                </b-form-group>

                <b-form-group label="Range Calendar" class="mb-3">
                  <Flatpickr id="range-datepicker" placeholder="2018-10-03 to 2018-10-10"
                             :options="flatpickrOptions8"/>
                </b-form-group>

                <b-form-group label="Inline Calendar">
                  <Flatpickr id="inline-datepicker" placeholder="Inline calendar" :options="flatpickrOptions9"/>
                </b-form-group>
              </b-col>
            </b-row>
          </template>
        </CustomSyntax>

      </b-col>
    </b-row>

    <b-row>
      <b-col cols="12">

        <CustomSyntax title="Flatpickr - Time Picker">
          <template v-slot:sub-text>
            A lightweight and powerful datetimepicker
          </template>
          <template v-slot:preview>
            <b-row>
              <b-col lg="6">
                <b-form-group label="Default Time Picker" class="mb-3">
                  <div class="input-group">
                    <Flatpickr id="basic-timepicker" placeholder="Basic timepicker" :options="flatpickrOptions10"/>
                    <span class="input-group-text"><i class="ri-time-line"></i></span>
                  </div>
                </b-form-group>

                <b-form-group label="24-hour Time Picker" class="mb-0">
                  <div class="input-group">
                    <Flatpickr id="24hours-timepicker" placeholder="16:21" :options="flatpickrOptions11"/>
                    <span class="input-group-text"><i class="ri-time-line"></i></span>
                  </div>
                </b-form-group>
              </b-col>

              <b-col lg="6" class="mt-3 mt-lg-0">
                <b-form-group label="Time Picker w/ Limits" class="mb-3">
                  <div class="input-group">
                    <Flatpickr id="minmax-timepicker" placeholder="Limits" :options="flatpickrOptions12"/>
                    <span class="input-group-text"><i class="ri-time-line"></i></span>
                  </div>
                </b-form-group>

                <b-form-group label="Preloading Time" class="mb-0">
                  <div class="input-group">
                    <Flatpickr id="preloading-timepicker" placeholder="Pick a time" :options="flatpickrOptions13"/>
                    <span class="input-group-text"><i class="ri-time-line"></i></span>
                  </div>
                </b-form-group>
              </b-col>
            </b-row>
          </template>
        </CustomSyntax>

      </b-col>
    </b-row>

    <b-row>
      <b-col cols="12">
        <CustomSyntax title="Input Masks">
          <template v-slot:sub-text>
            A jQuery Plugin to make masks on form fields and HTML elements.
          </template>
          <template v-slot:preview>
            <b-row>
              <b-col md="6">
                <b-form action="#">
                  <b-form-group label="Date" label-class="" class="mb-3">
                    <b-form-input
                        v-model="inputMask.demoDate"
                        v-mask="'##/##/####'"
                        type="text"
                        placeholder="Enter date"
                    />
                    <span class="font-13 text-muted">e.g "DD/MM/YYYY"</span>
                  </b-form-group>
                  <b-form-group label="Hour" label-class="" class="mb-3">
                    <b-form-input
                        v-model="inputMask.hour"
                        v-mask="'##:##:##'"
                        type="text"
                        placeholder="Enter time"
                    />
                    <span class="font-13 text-muted">e.g "HH:MM:SS"</span>
                  </b-form-group>
                  <b-form-group label="Date & Hour" label-class="" class="mb-3">
                    <b-form-input
                        v-model="inputMask.datetime"
                        v-mask="'##/##/#### ##:##:##'"
                        type="text"
                        placeholder="Enter date & time"
                    />
                    <span class="font-13 text-muted">e.g "DD/MM/YYYY HH:MM:SS"</span>
                  </b-form-group>
                  <b-form-group label="ZIP Code" label-class="" class="mb-3">
                    <b-form-input
                        type="text"
                        v-model="inputMask.zipcode"
                        v-mask="'#####-###'"
                        placeholder="Enter zip code"
                    />
                    <span class="font-13 text-muted">e.g "xxxxx-xxx"</span>
                  </b-form-group>
                  <b-form-group label="Crazy Zip Code" label-class="" class="mb-3">
                    <b-form-input
                        v-model="inputMask.crazyzip"
                        v-mask="'#-##-##-##'"
                        type="text"
                        placeholder="Enter zip code"
                    />
                    <span class="font-13 text-muted">e.g "x-xx-xx-xx"</span>
                  </b-form-group>
                  <b-form-group label="Money" label-class="" class="mb-3">
                    <b-form-input
                        v-model="inputMask.money"
                        v-mask="'###.###.###.###.###,##'"
                        type="text"
                        placeholder="Enter money"
                    />
                    <span class="font-13 text-muted">e.g "Your money"</span>
                  </b-form-group>
                  <b-form-group label="Money 2" label-class="">
                    <b-form-input
                        v-model="inputMask.money2"
                        v-mask="'#.##0,00'"
                        type="text"
                        placeholder="Enter money"
                    />
                    <span class="font-13 text-muted">e.g "#.##0,00"</span>
                  </b-form-group>
                </b-form>
              </b-col>

              <b-col md="6">
                <b-form action="#">
                  <b-form-group label="Telephone" label-class="" class="mb-3">
                    <b-form-input
                        v-model="inputMask.telephone"
                        v-mask="'####-####'"
                        type="text"
                        placeholder="Enter telephone"
                    />
                    <span class="font-13 text-muted">e.g "xxxx-xxxx"</span>
                  </b-form-group>
                  <b-form-group
                      label="Telephone with Code Area"
                      label-class=""
                      class="mb-3"
                  >
                    <b-form-input
                        v-model="inputMask.areacode"
                        v-mask="'(##) ####-####'"
                        type="text"
                        placeholder="Enter telephone"
                    />
                    <span class="font-13 text-muted">e.g "(xx) xxxx-xxxx"</span>
                  </b-form-group>
                  <b-form-group label="US Telephone" label-class="" class="mb-3">
                    <b-form-input
                        v-model="inputMask.ustelephone"
                        v-mask="'(###) ###-####'"
                        type="text"
                        placeholder="Enter US telephone"
                    />
                    <span class="font-13 text-muted">e.g "(xxx) xxx-xxxx"</span>
                  </b-form-group>
                  <b-form-group
                      label="São Paulo Celphones"
                      label-class=""
                      class="mb-3"
                  >
                    <b-form-input
                        v-model="inputMask.celphone"
                        v-mask="'(##) #####-####'"
                        type="text"
                        placeholder="Enter telephone"
                    />
                    <span class="font-13 text-muted">e.g "(xx) xxxxx-xxxx"</span>
                  </b-form-group>
                  <b-form-group label="CPF" label-class="" class="mb-3">
                    <b-form-input
                        v-model="inputMask.cpf"
                        v-mask="'###.###.###-##'"
                        type="text"
                        placeholder="Enter CPF"
                    />
                    <span class="font-13 text-muted">e.g "xxx.xxx.xxxx-xx"</span>
                  </b-form-group>
                  <b-form-group label="CNPJ" label-class="" class="mb-3">
                    <b-form-input
                        v-model="inputMask.cnpj"
                        v-mask="'##.###.###/####-##'"
                        type="text"
                        placeholder="Enter CNPJ"
                    />
                    <span class="font-13 text-muted">e.g "xx.xxx.xxx/xxxx-xx"</span>
                  </b-form-group>
                  <b-form-group label="IP Address" label-class="">
                    <b-form-input
                        v-model="inputMask.ipaddress"
                        v-mask="'###.###.###.###'"
                        type="text"
                        placeholder="Enter IP address"
                    />
                    <span class="font-13 text-muted">e.g "xxx.xxx.xxx.xxx"</span>
                  </b-form-group>
                </b-form>
              </b-col>
            </b-row>
          </template>
        </CustomSyntax>

      </b-col>
    </b-row>

    <b-row>
      <b-col cols="12">
        <!--        <BootstrapTouchspin />-->
      </b-col>
    </b-row>

    <b-row>
      <b-col cols="12">

        <CustomSyntax title="Bootstrap Maxlength">
          <template v-slot:sub-text>
            Uses the HTML5 attribute "maxlength" to work. Just specify
            <code>data-toggle="maxlength"</code> attribute to have maxlength
            indication on any input.
          </template>
          <template v-slot:preview>
            <b-row>
              <b-col lg="6">
                <b-form-group label="Default usage" class="mb-3">
                  <p class="text-muted fs-13">
                    The badge will show up by default when the remaining chars are 10
                    or less:
                  </p>
                  <BootstrapMaxlength class="maxlength" placeholder="Max 25" maxlength="25" />
                </b-form-group>

                <b-form-group label="Threshold value" class="mb-3">
                  <p class="text-muted fs-13">
                    Satrt displaying the indication when reached to some threshhold.
                    Specift the data attribute
                    <code>threshold</code>. E.g.
                    <code>data-threshold="12"</code>
                  </p>
                  <BootstrapMaxlength placeholder="Max 25" maxlength="25" data-threshold="12" />
                </b-form-group>
              </b-col>

              <b-col lg="6" class="mt-3 mt-lg-0">
                <b-form-group label="Position" class="mb-3">
                  <p class="text-muted fs-13">
                    All you need to do is specify the data attribute
                    <code>placement</code>. The possible positions are left, top,
                    right, bottom-right, top-right, top-left, bottom, bottom-left and
                    centered-right. If none is specified, the positioning will be
                    defauted to 'bottom'. E.g.
                    <code>data-placement="top"</code>
                  </p>
                  <BootstrapMaxlength placeholder="Max 25" maxlength="25" data-placement="top" />
                </b-form-group>

                <b-form-group label="Textareas">
                  <p class="text-muted fs-13">
                    Bootstrap maxlength supports textarea as well as inputs. Even on
                    old IE.
                  </p>
                  <b-form-textarea
                      data-toggle="maxlength"
                      maxlength="225"
                      rows="3"
                      placeholder="This textarea has a limit of 225 chars."
                  ></b-form-textarea>
                </b-form-group>
              </b-col>
            </b-row>
          </template>
        </CustomSyntax>

      </b-col>
    </b-row>

    <b-row>
      <b-col cols="12">

        <CustomSyntax title="Timepicker">
          <template v-slot:sub-text>
            Easily select a time for a text input using your mouse or keyboards
            arrow keys. Specify attribute
            <code>data-toggle="timepicker"</code>
            and you would have nice timepicker input element.
          </template>
          <template v-slot:preview>
            <b-row>
              <b-col lg="6">
                <div class="mb-3">
                  <label class="form-label">Default Time Picker</label>
                  <div class="input-group" id="timepicker-input-group1">
                    <BootstrapTimepicker id="timepicker"/>
                    <span class="input-group-text"><i class="ri-time-line"></i></span>
                  </div>
                </div>

                <div class="mb-0">
                  <label class="form-label"
                  >24 Hour Mode Time Picker E.g.
                    <code>data-show-meridian="false"</code></label
                  >
                  <div class="input-group" id="timepicker-input-group2">
                    <BootstrapTimepicker id="timepicker2" data-show-meridian="false"/>
                    <span class="input-group-text"><i class="ri-time-line"></i></span>
                  </div>
                </div>
              </b-col>

              <b-col lg="6" class="mt-3 mt-lg-0">
                <div class="mb-0">
                  <label class="form-label"
                  >Specify a step for the minute field E.g.
                    <code>data-minute-step="5"</code></label
                  >
                  <div class="input-group" id="timepicker-input-group3">
                    <BootstrapTimepicker id="timepicker3" data-minute-step="5"/>
                    <span class="input-group-text"><i class="ri-time-line"></i></span>
                  </div>
                </div>
              </b-col>
            </b-row>
          </template>
        </CustomSyntax>
      </b-col>
    </b-row>

    <b-row>
      <b-col cols="12">
        <TypeAhead/>
      </b-col>
    </b-row>
  </Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";
import CustomSyntax from "@/components/custom/custom-syntax.vue";
import DateRangePicker from "@/components/custom/date-range-picker.vue";
import {multiSelectOptions} from "@/views/form/advanced/data";

import VueMultiselect from "vue-multiselect";
import BootstrapDatepicker from "@/components/custom/bootstrap-datepicker.vue";
import Flatpickr from "@/components/custom/custom-flatpickr.vue";
import TypeAhead from "@/views/form/advanced/type-ahead.vue";
import BootstrapTimepicker from "@/components/custom/bootstrap-timepicker.vue";
import BootstrapMaxlength from "@/components/custom/bootstrap-maxlength.vue";
import switches from 'vue-switches';
import 'vue-switches/dist/switches.css'

export default {
  components: {
    BootstrapMaxlength,
    BootstrapTimepicker,
    TypeAhead,
    switches,
    Flatpickr, BootstrapDatepicker, DateRangePicker, CustomSyntax, Breadcrumb, Layout, VueMultiselect
  },
  data() {
    return {
      title: 'Form Advanced',
      enabled: true,
      items: [
        {
          text: 'Hyper',
          href: '/',
        },
        {
          text: 'Forms',
          href: '/',
        },
        {
          text: 'Form Advanced',
          active: true,
        },
      ],


      selected: null,
      selected1: null,
      multiSelectOptions,
      flatpickrOptions2: {
        enableTime: true,
        dateFormat: "Y-m-d H:i",
      },
      flatpickrOptions3: {
        altInput: true,
        altFormat: "F j, Y",
        dateFormat: "Y-m-d",
      },
      flatpickrOptions4: {
        minDate: "2020-01",
        maxDate: "2020-03",
      },
      flatpickrOptions5: {
        onReady: function () {
          this.jumpToDate("2025-01");
        },
        disable: ["2025-01-10", "2025-01-21", "2025-01-30", new Date(2025, 4, 9)],
        dateFormat: "Y-m-d",
      },
      flatpickrOptions6: {
        mode: "multiple",
        dateFormat: "Y-m-d",
      },
      flatpickrOptions7: {
        mode: "multiple",
        dateFormat: "Y-m-d",
        conjunction: " :: ",
      },
      flatpickrOptions8: {
        mode: "range",
      },
      flatpickrOptions9: {
        inline: true,
      },
      flatpickrOptions10: {
        enableTime: true,
        noCalendar: true,
        dateFormat: 'H:i',
      },
      flatpickrOptions11: {
        enableTime: true,
        noCalendar: true,
        dateFormat: "H:i",
        time_24hr: true,
      },
      flatpickrOptions12: {
        enableTime: true,
        noCalendar: true,
        dateFormat: "H:i",
        minDate: "16:00",
        maxDate: "22:30",
      },
      flatpickrOptions13: {
        enableTime: true,
        noCalendar: true,
        dateFormat: "H:i",
        defaultDate: "01:45",
      },

      inputMask: {
        demoDate: "",
        hour: "",
        datetime: "",
        zipcode: "",
        crazyzip: "",
        money: "",
        money2: "",
        telephone: "",
        celphone: "",
        ustelephone: "",
        areacode: "",
        ipaddress: "",
        cnpj: "",
        cpf: "",
        maxlen: "",
        data: "",
        option: "",
        textarea: "",
      }
    }
  }
}
</script>
