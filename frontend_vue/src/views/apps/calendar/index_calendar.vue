<template>
  <Layout>
    <!-- Page Title -->
    <b-row>
      <b-col cols="12">
        <div class="page-title-box">
          <h4 class="page-title">Calendar</h4>
        </div>
      </b-col>
    </b-row>

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
                <!-- Event Type Legend -->
                <div class="mt-3">
                  <h5 class="mb-3">Event Types</h5>
                  <div
                    v-for="category in categories"
                    :key="category.value"
                    class="mb-2 d-flex align-items-center"
                  >
                    <span
                      class="badge me-2"
                      :class="category.value"
                      style="width: 20px; height: 20px; display: inline-block;"
                    ></span>
                    <span class="text-muted">{{ category.name }}</span>
                  </div>
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
import interactionPlugin from "@fullcalendar/interaction";
import bootstrapPlugin from "@fullcalendar/bootstrap5";
import listPlugin from "@fullcalendar/list";

import { calendarEvents as demoEvents, categories } from "./data";
import axios from '@/lib/http';  // Centralized axios instance
import { type CalendarOptions, type EventInput } from "@fullcalendar/core";

type EventForm = {
  title: string;
  category: string;
};

type EditEventForm = {
  editTitle: string;
  editCategory: string | string[];
};

export default {
  components: { Breadcrumb, Layout, FullCalendar },
  data() {
    const normalizedDemoEvents: EventInput[] = demoEvents.map((event) => ({
      ...event,
      id: String(event.id),
    }));

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
      demoEventInputs: normalizedDemoEvents,
      calendarEvents: [...normalizedDemoEvents],
      submitted: false,
      submit: false,
      newEventData: {} as any,
      edit: {} as any,
      deleteId: {},
      event: {
        title: "",
        category: "bg-success",
      } as EventForm,
      editevent: {
        editTitle: "",
        editCategory: "bg-success",
      } as EditEventForm,
      // Map backend event types to Bootstrap color classes
      // What: Converts semantic event types from backend to frontend styling
      // Why: Separates backend data concerns from frontend presentation
      // Where: Used in fetchCalendarEvents() to apply colors
      // How: Backend sends event type, frontend applies matching color
      eventColorMap: {
        'actual_liquidation': 'bg-success',     // Green - actual FC sales
        'projected_liquidation': 'bg-warning',  // Yellow - projected FC sales
        'bid_date': 'bg-info',                  // Cyan - bid deadlines
        'settlement_date': 'bg-dark',           // Dark - settlements
        'milestone': 'bg-danger',               // Red - other milestones
      } as Record<string, string>,
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
        height: 'auto',  // Auto-adjust overall calendar height
        aspectRatio: 1.35,  // Width-to-height ratio for consistent cell sizing
        weekends: true,
        droppable: false,  // Disable drag-drop since we removed external events
        editable: true,
        selectable: true,
        dayMaxEvents: 3,  // Show max 3 events, then "+X more" link
        moreLinkClick: 'popover',  // Show remaining events in popover when clicking "+more"
        events: normalizedDemoEvents,
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
    /**
     * Fetch calendar events from Django backend API
     * 
     * What: Loads events from /api/core/calendar/events/ endpoint
     * Why: Display real data from models (ServicerLoanData, TradeLevelAssumption, etc.)
     * Where: Called in mounted() hook on component load
     * How: Fetches JSON, maps event types to colors, formats for FullCalendar
     */
    async fetchCalendarEvents() {
      try {
        // Note: baseURL is already '/api', so we don't include it in the path
        const response = await axios.get('/core/calendar/events/');
        
        // Map backend events to FullCalendar format
        // What: Transforms Django API response to FullCalendar event objects
        // Why: FullCalendar expects specific format (start, classNames, etc.)
        // How: Maps category to color class, formats date, adds metadata
        const backendEvents = response.data.map((event: any) => ({
          id: String(event.id),
          title: event.title,
          start: event.date,  // Backend sends YYYY-MM-DD format
          allDay: true,       // All model-based events are all-day
          classNames: [this.getEventColor(event.category)],  // Apply color based on type
          extendedProps: {
            description: event.description,
            source_model: event.source_model,
            editable: event.editable,
            url: event.url,
          },
        }));
        
        // Set backend events as calendar events
        this.calendarEvents = backendEvents;
        this.calendarOptions.events = this.calendarEvents;
        
        console.log(`Loaded ${backendEvents.length} events from backend`);
      } catch (error) {
        console.error('Failed to fetch calendar events:', error);
        // Empty calendar if API fails
        this.calendarEvents = [];
        this.calendarOptions.events = this.calendarEvents;
      }
    },
    
    /**
     * Get Bootstrap color class for event type
     * 
     * What: Maps semantic event type to Bootstrap class
     * Why: Backend sends types like 'foreclosure', frontend needs 'bg-danger'
     * Where: Called during fetchCalendarEvents() for each event
     * How: Looks up type in eventColorMap, defaults to bg-primary
     */
    getEventColor(eventType: string): string {
      return this.eventColorMap[eventType as keyof typeof this.eventColorMap] || 'bg-primary';
    },
    
    handleSubmit(e: Event) {
      this.submitted = true;
      const title = this.event.title;
      const category = this.event.category;
      if (title == null || category == null) {
        return;
      } else {
        this.calendarEvents.push({
          id: String(this.calendarEvents.length + 1),
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
      this.event = {
        title: "",
        category: "bg-success",
      };
    },

    hideModal(e: Event) {
      this.submitted = false;
      this.showModal = false;
      this.event = {
        title: "",
        category: "bg-success",
      };
    },

    editSubmit(e: Event) {
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
        (x: any) => "" + x.id !== "" + deleteId
      );
      this.eventModal = false;
    },

    dateClicked(info: any) {
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
    // Fetch calendar events from backend API
    // What: Load real events from Django on component mount
    // Why: Display actual data from ServicerLoanData, TradeLevelAssumption, etc.
    // Where: Calls /api/core/calendar/events/ endpoint
    // How: fetchCalendarEvents() handles API call and data mapping
    this.fetchCalendarEvents();
  },
};
</script>

<style scoped>
/* Force consistent minimum height for all day cells */
:deep(.fc-daygrid-day-frame) {
  min-height: 160px !important;
}

/* Ensure event container has proper spacing */
:deep(.fc-daygrid-day-events) {
  min-height: 90px;
}
</style>
