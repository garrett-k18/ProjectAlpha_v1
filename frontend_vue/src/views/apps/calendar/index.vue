<template>
  <Layout>
    <Breadcrumb :title="title" :items="items" />

    <b-row>
      <b-col cols="12">
        <div class="card">
          <div class="card-body">
            <b-row>
              <b-col lg="3">
                <div class="d-grid">
                  <b-button
                    variant="danger"
                    size="lg"
                    class="font-16"
                    @click="dateClicked({ date: new Date(), allDay: true })"
                  >
                    <i class="mdi mdi-plus-circle-outline"></i> Create New Event
                  </b-button>
                </div>
                <div id="external-events" class="mt-3">
                  <p class="text-muted">
                    Drag and drop your event or click in the calendar
                  </p>
                  <div
                    class="external-event bg-success-lighten text-success"
                    data-class="bg-success"
                  >
                    <i
                      class="mdi mdi-checkbox-blank-circle me-2 vertical-middle"
                    ></i
                    >New Theme Release
                  </div>
                  <div
                    class="external-event bg-info-lighten text-info"
                    data-class="bg-info"
                  >
                    <i
                      class="mdi mdi-checkbox-blank-circle me-2 vertical-middle"
                    ></i
                    >My Event
                  </div>
                  <div
                    class="external-event bg-warning-lighten text-warning"
                    data-class="bg-warning"
                  >
                    <i
                      class="mdi mdi-checkbox-blank-circle me-2 vertical-middle"
                    ></i
                    >Meet manager
                  </div>
                  <div
                    class="external-event bg-danger-lighten text-danger"
                    data-class="bg-danger"
                  >
                    <i
                      class="mdi mdi-checkbox-blank-circle me-2 vertical-middle"
                    ></i
                    >Create New theme
                  </div>
                </div>

                <div class="mt-5 d-none d-xl-block">
                  <h5 class="text-center">How It Works ?</h5>

                  <ul class="ps-3">
                    <li class="text-muted mb-3">
                      It has survived not only five centuries, but also the leap
                      into electronic typesetting, remaining essentially
                      unchanged.
                    </li>
                    <li class="text-muted mb-3">
                      Richard McClintock, a Latin professor at Hampden-Sydney
                      College in Virginia, looked up one of the more obscure
                      Latin words, consectetur, from a Lorem Ipsum passage.
                    </li>
                    <li class="text-muted mb-3">
                      It has survived not only five centuries, but also the leap
                      into electronic typesetting, remaining essentially
                      unchanged.
                    </li>
                  </ul>
                </div>
              </b-col>
              <!-- end col-->

              <b-col lg="9">
                <div class="mt-4 mt-lg-0">
                  <FullCalendar
                    ref="fullCalendar"
                    :bootstrap-font-awesome="false"
                    :options="calendarOptions"
                  />
                </div>
              </b-col>
              <!-- end col -->
            </b-row>
            <!-- end row -->
          </div>
          <!-- end card body-->
        </div>
        <!-- end card -->
      </b-col>
      <!-- end col-12 -->
    </b-row>
    <!-- end row -->

    <!-- Add New Event MODAL -->
    <b-modal
      v-model="showModal"
      hide-footer
      title-class="h5"
      title="Add New Event"
      header-class="px-4 pb-0 border-bottom-0"
      body-class="px-4 pb-4 pt-3"
    >
      <b-form
        id="form-event"
        class="needs-validation"
        name="event-form"
        novalidate
        @submit.prevent="handleSubmit"
      >
        <b-row>
          <b-col cols="12">
            <b-form-group label="Event Name" class="mb-3">
              <b-form-input
                id="event-title"
                v-model="event.title"
                class="form-control"
                name="title"
                placeholder="Insert Event Name"
                required
                type="text"
              />
              <div class="invalid-feedback">
                Please provide a valid event name
              </div>
            </b-form-group>
          </b-col>
          <b-col cols="12">
            <b-form-group label="Category" class="mb-3">
              <b-form-select
                id="event-category"
                v-model="event.category"
                name="category"
                required
              >
                <b-form-select-option
                  v-for="option in categories"
                  :key="option.value"
                  :value="`${option.value}`"
                >
                  {{ option.name }}
                </b-form-select-option>
              </b-form-select>

              <div class="invalid-feedback">
                Please select a valid event category
              </div>
            </b-form-group>
          </b-col>
        </b-row>
        <b-row>
          <b-col cols="6"></b-col>
          <b-col cols="6" class="text-end">
            <b-button variant="light" class="me-1" @click="hideModal">
              Close
            </b-button>
            <b-button variant="success" id="btn-save-event" type="submit">
              Save
            </b-button>
          </b-col>
        </b-row>
      </b-form>
    </b-modal>

    <!-- Edit Event MODAL -->
    <b-modal
      v-model="eventModal"
      hide-footer
      title-class="h5"
      title="Edit Event"
      header-class="px-4 pb-0 border-bottom-0"
      body-class="px-4 pb-4 pt-3"
    >
      <b-form
        id="form-event"
        class="needs-validation"
        name="event-form"
        novalidate
        @submit.prevent="editSubmit"
      >
        <b-row>
          <b-col cols="12">
            <b-form-group label="Event Name" class="mb-3">
              <b-form-input
                id="event-title"
                v-model="editevent.editTitle"
                class="form-control"
                name="title"
                placeholder="Insert Event Name"
                required
                type="text"
              />
            </b-form-group>
          </b-col>
          <b-col cols="12">
            <b-form-group label="Category" class="mb-3">
              <b-form-select
                id="event-category"
                v-model="editevent.editCategory"
                name="category"
                :value="editevent.editCategory"
                required
              >
                <b-form-select-option
                  v-for="option in categories"
                  :key="option.value"
                  :value="`${option.value}`"
                >
                  {{ option.name }}
                </b-form-select-option>
              </b-form-select>

              <div class="invalid-feedback">
                Please select a valid event category
              </div>
            </b-form-group>
          </b-col>
        </b-row>
        <b-row>
          <b-col cols="6">
            <b-button
              variant="danger"
              id="btn-delete-event"
              @click="deleteEvent"
            >
              Delete
            </b-button>
          </b-col>
          <b-col cols="6" class="text-end">
            <b-button variant="light" class="me-1" @click="closeModal">
              Close
            </b-button>
            <b-button variant="success" id="btn-save-event" type="submit">
              Save
            </b-button>
          </b-col>
        </b-row>
      </b-form>
    </b-modal>
  </Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";

import FullCalendar from "@fullcalendar/vue3";
import dayGridPlugin from "@fullcalendar/daygrid";
import timeGridPlugin from "@fullcalendar/timegrid";
import interactionPlugin, { Draggable } from "@fullcalendar/interaction";
import bootstrapPlugin from "@fullcalendar/bootstrap5";
import listPlugin from "@fullcalendar/list";

import { calendarEvents, categories } from "./data";
import { type CalendarOptions } from "@fullcalendar/core";

export default {
  components: { Breadcrumb, Layout, FullCalendar },
  data() {
    return {
      title: "Calendar",
      items: [
        {
          text: "Hyper",
          href: "/",
        },
        {
          text: "Apps",
          href: "/",
        },
        {
          text: "Calendar",
          active: true,
        },
      ],

      showModal: false,
      eventModal: false,
      categories: categories,
      calendarEvents: calendarEvents,
      submitted: false,
      submit: false,
      newEventData: {} as any,
      edit: {} as any,
      deleteId: {},
      event: {
        title: "Add new event",
        category: "bg-success",
      },
      editevent: {
        editTitle: "",
        editCategory: {},
      },
      calendarOptions: {
        plugins: [
          dayGridPlugin,
          timeGridPlugin,
          interactionPlugin,
          bootstrapPlugin,
          listPlugin,
        ],
        headerToolbar: {
          left: "prev,next today",
          center: "title",
          right: "dayGridMonth,timeGridWeek,timeGridDay,listWeek",
        },

        buttonText: {
          today: "Today",
          month: "Month",
          week: "Week",
          day: "Day",
          list: "List",
          prev: "Prev",
          next: "Next",
        },
        slotDuration: "00:15:00",
        slotMinTime: "08:00:00",
        slotMaxTime: "19:00:00",
        themeSystem: "bootstrap",
        initialView: "dayGridMonth",
        handleWindowResize: true,
        height: window.innerHeight - 200,
        weekends: true,
        droppable: true,
        editable: true,
        selectable: true,
        events: calendarEvents,
        eventClick: (arg) => {
          this.editEvent(arg);
        },
        dateClick: (arg) => {
          this.dateClicked(arg);
        },
      } as CalendarOptions,
    };
  },
  methods: {
    handleSubmit(e) {
      this.submitted = true;
      const title = this.event.title;
      const category = this.event.category;
      if (title == null || category == null) {
        return;
      } else {
        this.calendarEvents.push({
          id: this.calendarEvents.length + 1,
          title: title,
          start: this.newEventData.date,
          allDay: this.newEventData.allDay,
          classNames: [category],
        });
        this.calendarOptions.events = this.calendarEvents;
        this.showModal = false;
        this.newEventData = {} as any;
      }
      this.submitted = false;
      this.event = {};
    },

    hideModal(e) {
      this.submitted = false;
      this.showModal = false;
      this.event = {};
    },

    editSubmit(e) {
      this.submit = true;
      const editTitle = this.editevent.editTitle;
      const editCategory = this.editevent.editCategory;
      this.edit.setProp("title", editTitle);
      this.edit.setProp("classNames", editCategory);
      this.eventModal = false;
    },

    deleteEvent() {
      var deleteId = this.edit.id;

      this.calendarOptions.events = (this.calendarOptions.events as any).filter(
        (x) => "" + x.id !== "" + deleteId
      );
      this.eventModal = false;
    },

    dateClicked(info) {
      this.newEventData = info;
      this.showModal = true;
    },

    editEvent(info: { event: any }) {
      this.edit = info.event;
      this.editevent.editTitle = this.edit.title;
      this.editevent.editCategory = this.edit.category;
      this.eventModal = true;
    },

    closeModal() {
      this.eventModal = false;
    },
  },
  mounted() {
    new Draggable(document.getElementById("external-events")!, {
      itemSelector: ".external-event",
      eventData: function (eventEl) {
        return {
          title: eventEl.innerText,
          start: new Date(),
          className: eventEl.getAttribute("data-class"),
        };
      },
    });
  },
};
</script>
