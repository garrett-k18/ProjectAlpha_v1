<template>
  <!-- Calendar Widget for Home Dashboard -->
  <!-- Uses Hyper UI calendar component pattern -->
  <!-- Based on: frontend_vue/src/views/dashboards/projects/calendar.vue -->
  <!-- Enhanced with event management: add, edit, delete events on specific dates -->
  <div class="card">
    <div class="card-header d-flex justify-content-between align-items-center">
      <h4 class="header-title">Calendar</h4>
      <div class="float-end">
        <!-- Add New Event Button -->
        <button 
          class="btn btn-sm btn-primary me-2" 
          type="button"
          @click="openAddEventModal"
        >
          <i class="mdi mdi-plus"></i>
          Add Event
        </button>
        <b-dropdown toggle-class="arrow-none card-drop p-0" variant="link" right>
          <template v-slot:button-content>
            <i class="mdi mdi-dots-vertical"></i>
          </template>
          <b-dropdown-item @click="clearAllEvents">Clear All Events</b-dropdown-item>
          <b-dropdown-item @click="exportEvents">Export Events</b-dropdown-item>
        </b-dropdown>
      </div>
    </div>

    <div class="card-body pt-0">
      <b-row class="calendar-widget calendar-widget-inline">
        <b-col md="7">
          <!--Calendar-->
          <!-- Bootstrap datepicker inline calendar widget -->
          <!-- Ref allows us to access the DOM element and bind events -->
          <div 
            ref="datepickerEl"
            data-provide="datepicker-inline" 
            data-date-today-highlight="true" 
            class="calendar-widget"
          >
          </div>
        </b-col>

        <b-col md="5">
          <!-- Events List for Selected Date -->
          <div class="d-flex justify-content-between align-items-center mb-2">
            <h6 class="mb-0">
              {{ selectedDateFormatted }}
            </h6>
            <small class="text-muted">{{ filteredEvents.length }} event(s)</small>
          </div>
          
          <!-- Display events for the selected date -->
          <ul class="list-unstyled mt-1" v-if="filteredEvents.length > 0">
            <li 
              v-for="event in filteredEvents" 
              :key="event.id" 
              class="mb-3 p-2 border rounded hover-shadow cursor-pointer"
              @click="editEvent(event)"
            >
              <div class="d-flex justify-content-between align-items-start">
                <div class="flex-grow-1">
                  <p class="text-muted mb-1 font-13">
                    <i class="mdi mdi-calendar"></i> {{ event.time }}
                  </p>
                  <h6 class="mb-0">{{ event.title }}</h6>
                  <small class="text-muted" v-if="event.description">{{ event.description }}</small>
                </div>
                <!-- Color indicator based on event category -->
                <span 
                  class="badge ms-2" 
                  :class="event.category"
                >
                  {{ getCategoryName(event.category) }}
                </span>
              </div>
            </li>
          </ul>
          
          <!-- Empty state when no events for selected date -->
          <div v-else class="text-center text-muted py-4">
            <i class="mdi mdi-calendar-blank-outline" style="font-size: 2rem;"></i>
            <p class="mb-0 mt-2">No events for this date</p>
            <button 
              class="btn btn-sm btn-outline-primary mt-2"
              @click="openAddEventModal"
            >
              Add Event
            </button>
          </div>
        </b-col>
      </b-row>
    </div>
  </div>

  <!-- Add/Edit Event Modal -->
  <!-- Uses BootstrapVue3 modal component (project standard) -->
  <b-modal
    v-model="showEventModal"
    :title="isEditMode ? 'Edit Event' : 'Add New Event'"
    hide-footer
    header-class="px-4 pb-0 border-bottom-0"
    body-class="px-4 pb-4 pt-3"
  >
    <b-form @submit.prevent="saveEvent">
      <b-row>
        <!-- Event Title Input -->
        <b-col cols="12">
          <b-form-group label="Event Title" class="mb-3">
            <b-form-input
              v-model="eventForm.title"
              placeholder="Enter event title"
              required
              type="text"
            />
          </b-form-group>
        </b-col>

        <!-- Event Time Input -->
        <b-col cols="12">
          <b-form-group label="Time" class="mb-3">
            <b-form-input
              v-model="eventForm.time"
              placeholder="e.g., 9:00 AM - 10:00 AM"
              required
              type="text"
            />
          </b-form-group>
        </b-col>

        <!-- Event Description (Optional) -->
        <b-col cols="12">
          <b-form-group label="Description (Optional)" class="mb-3">
            <b-form-textarea
              v-model="eventForm.description"
              placeholder="Add event details..."
              rows="3"
            />
          </b-form-group>
        </b-col>

        <!-- Event Category (Color) -->
        <b-col cols="12">
          <b-form-group label="Category" class="mb-3">
            <b-form-select v-model="eventForm.category" required>
              <b-form-select-option 
                v-for="cat in categories" 
                :key="cat.value" 
                :value="cat.value"
              >
                {{ cat.name }}
              </b-form-select-option>
            </b-form-select>
          </b-form-group>
        </b-col>
      </b-row>

      <!-- Modal Footer Actions -->
      <b-row class="mt-3">
        <b-col cols="6">
          <!-- Delete button only shows in edit mode -->
          <b-button 
            v-if="isEditMode" 
            variant="danger" 
            @click="deleteEvent"
          >
            <i class="mdi mdi-delete"></i> Delete
          </b-button>
        </b-col>
        <b-col cols="6" class="text-end">
          <b-button variant="light" class="me-2" @click="closeEventModal">
            Cancel
          </b-button>
          <b-button variant="primary" type="submit">
            <i class="mdi mdi-check"></i> Save
          </b-button>
        </b-col>
      </b-row>
    </b-form>
  </b-modal>
</template>

<script lang="ts">
// Import bootstrap-datepicker for inline calendar functionality
import "bootstrap-datepicker";
// Import jQuery (required by bootstrap-datepicker)
import $ from "jquery";

/**
 * Interface for calendar event data structure
 * Each event has a unique ID, title, date, time, optional description, and category (color)
 * Exported to satisfy TypeScript module requirements
 */
export interface CalendarEvent {
  id: number;
  title: string;
  date: string; // Format: YYYY-MM-DD for consistency
  time: string; // Display string like "9:00 AM - 10:00 AM"
  description?: string;
  category: string; // Bootstrap class like 'bg-primary', 'bg-success', etc.
}

/**
 * Extend JQuery interface to include bootstrap-datepicker methods
 * This prevents TypeScript errors when calling .datepicker()
 */
declare global {
  interface JQuery {
    datepicker(options?: any): JQuery;
  }
}

export default {
  name: 'HomeCalendarWidget',
  
  data() {
    return {
      // selectedDate: Currently selected date from the datepicker (Date object)
      selectedDate: new Date(),
      
      // showEventModal: Controls visibility of the add/edit event modal
      showEventModal: false,
      
      // isEditMode: Flag to determine if we're editing an existing event or creating new
      isEditMode: false,
      
      // eventForm: Form data for the event being created/edited
      eventForm: {
        title: '',
        time: '',
        description: '',
        category: 'bg-primary',
        date: ''
      },
      
      // editingEventId: ID of the event being edited (null when creating new event)
      editingEventId: null as number | null,
      
      // events: Array of all calendar events (stored in component state)
      // In production, this should sync with backend API or localStorage
      events: [] as CalendarEvent[],
      
      // nextId: Counter for generating unique event IDs
      nextId: 1,
      
      // categories: Available event categories (colors) matching Hyper UI theme
      categories: [
        { name: 'Primary', value: 'bg-primary' },
        { name: 'Success', value: 'bg-success' },
        { name: 'Info', value: 'bg-info' },
        { name: 'Warning', value: 'bg-warning' },
        { name: 'Danger', value: 'bg-danger' },
        { name: 'Secondary', value: 'bg-secondary' },
      ]
    };
  },
  
  computed: {
    /**
     * filteredEvents: Returns events matching the currently selected date
     * Filters the events array by comparing date strings
     */
    filteredEvents(): CalendarEvent[] {
      const selectedDateStr = this.formatDateToString(this.selectedDate);
      return this.events.filter(event => event.date === selectedDateStr);
    },
    
    /**
     * selectedDateFormatted: Human-readable format of the selected date
     * Example: "Wednesday, January 15, 2025"
     */
    selectedDateFormatted(): string {
      return this.selectedDate.toLocaleDateString('en-US', { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      });
    }
  },
  
  methods: {
    /**
     * formatDateToString: Converts Date object to YYYY-MM-DD string format
     * @param date - JavaScript Date object
     * @returns Formatted date string for consistent storage
     */
    formatDateToString(date: Date): string {
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    },
    
    /**
     * openAddEventModal: Opens the modal to create a new event
     * Resets the form and sets the date to currently selected date
     */
    openAddEventModal() {
      this.isEditMode = false;
      this.editingEventId = null;
      this.eventForm = {
        title: '',
        time: '',
        description: '',
        category: 'bg-primary',
        date: this.formatDateToString(this.selectedDate)
      };
      this.showEventModal = true;
    },
    
    /**
     * editEvent: Opens the modal to edit an existing event
     * @param event - The event object to edit
     * Populates the form with existing event data
     */
    editEvent(event: CalendarEvent) {
      this.isEditMode = true;
      this.editingEventId = event.id;
      this.eventForm = {
        title: event.title,
        time: event.time,
        description: event.description || '',
        category: event.category,
        date: event.date
      };
      this.showEventModal = true;
    },
    
    /**
     * saveEvent: Saves the event (create new or update existing)
     * Validates form data and adds/updates event in the events array
     */
    saveEvent() {
      // Validation: Ensure required fields are filled
      if (!this.eventForm.title || !this.eventForm.time) {
        alert('Please fill in all required fields');
        return;
      }
      
      if (this.isEditMode && this.editingEventId !== null) {
        // Edit mode: Update existing event
        const index = this.events.findIndex(e => e.id === this.editingEventId);
        if (index !== -1) {
          this.events[index] = {
            id: this.editingEventId,
            title: this.eventForm.title,
            time: this.eventForm.time,
            description: this.eventForm.description,
            category: this.eventForm.category,
            date: this.eventForm.date
          };
        }
      } else {
        // Create mode: Add new event
        const newEvent: CalendarEvent = {
          id: this.nextId++,
          title: this.eventForm.title,
          time: this.eventForm.time,
          description: this.eventForm.description,
          category: this.eventForm.category,
          date: this.eventForm.date
        };
        this.events.push(newEvent);
      }
      
      // Save to localStorage for persistence across page reloads
      this.saveToLocalStorage();
      
      // Close modal and reset form
      this.closeEventModal();
    },
    
    /**
     * deleteEvent: Removes the currently edited event
     * Confirms deletion and removes from events array
     */
    deleteEvent() {
      if (!confirm('Are you sure you want to delete this event?')) {
        return;
      }
      
      if (this.editingEventId !== null) {
        this.events = this.events.filter(e => e.id !== this.editingEventId);
        this.saveToLocalStorage();
        this.closeEventModal();
      }
    },
    
    /**
     * closeEventModal: Closes the event modal and resets state
     */
    closeEventModal() {
      this.showEventModal = false;
      this.isEditMode = false;
      this.editingEventId = null;
    },
    
    /**
     * getCategoryName: Gets the display name for a category value
     * @param categoryValue - The category class name (e.g., 'bg-primary')
     * @returns Human-readable category name (e.g., 'Primary')
     */
    getCategoryName(categoryValue: string): string {
      const category = this.categories.find(c => c.value === categoryValue);
      return category ? category.name : 'Default';
    },
    
    /**
     * clearAllEvents: Removes all events after confirmation
     */
    clearAllEvents() {
      if (!confirm('Are you sure you want to delete all events?')) {
        return;
      }
      this.events = [];
      this.saveToLocalStorage();
    },
    
    /**
     * exportEvents: Exports events as JSON for backup/sharing
     */
    exportEvents() {
      const dataStr = JSON.stringify(this.events, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'calendar-events.json';
      link.click();
      URL.revokeObjectURL(url);
    },
    
    /**
     * saveToLocalStorage: Persists events to browser localStorage
     * Allows events to survive page reloads
     */
    saveToLocalStorage() {
      localStorage.setItem('calendarEvents', JSON.stringify(this.events));
      localStorage.setItem('calendarNextId', String(this.nextId));
    },
    
    /**
     * loadFromLocalStorage: Loads events from localStorage on component mount
     */
    loadFromLocalStorage() {
      const stored = localStorage.getItem('calendarEvents');
      const storedNextId = localStorage.getItem('calendarNextId');
      
      if (stored) {
        try {
          this.events = JSON.parse(stored);
        } catch (e) {
          console.error('Failed to load events from localStorage', e);
        }
      }
      
      if (storedNextId) {
        this.nextId = parseInt(storedNextId, 10);
      }
    }
  },
  
  /**
   * mounted: Lifecycle hook called when component is mounted to DOM
   * Sets up the datepicker and loads saved events
   */
  mounted() {
    // Load events from localStorage
    this.loadFromLocalStorage();
    
    // Initialize bootstrap-datepicker and bind changeDate event
    // The changeDate event fires when user clicks a date in the calendar
    const $datepicker = $(this.$refs.datepickerEl as HTMLElement);
    $datepicker.datepicker({
      todayHighlight: true,
      // beforeShowDay callback: Customizes each day cell in the calendar
      // Adds visual indicators (colored bands with event titles) to dates that have events
      beforeShowDay: (date: Date) => {
        const dateStr = this.formatDateToString(date);
        const eventsOnDate = this.events.filter(e => e.date === dateStr);
        
        if (eventsOnDate.length > 0) {
          // Build event bands HTML - show up to 3 events as colored bars with titles
          const eventBandsHtml = eventsOnDate.slice(0, 3).map(event => {
            // Get background color class from category
            const colorClass = event.category.replace('bg-', '');
            // Truncate title if too long
            const truncatedTitle = event.title.length > 15 ? event.title.substring(0, 12) + '...' : event.title;
            return `<div class="event-band event-band-${colorClass}" title="${event.title}">${truncatedTitle}</div>`;
          }).join('');
          
          // Add "more" indicator if there are more than 3 events
          const moreIndicator = eventsOnDate.length > 3 
            ? `<div class="event-more">+${eventsOnDate.length - 3} more</div>` 
            : '';
          
          // Return custom content with day number and event bands
          return {
            enabled: true,
            classes: 'has-events',
            tooltip: eventsOnDate.map(e => e.title).join(', '),
            content: `<div class="day-content"><span class="day-number">${date.getDate()}</span><div class="event-bands">${eventBandsHtml}${moreIndicator}</div></div>`
          };
        }
        
        // No events on this date, show default
        return {
          enabled: true
        };
      }
    }).on('changeDate', (e: any) => {
      // Update selectedDate when user clicks a different date
      this.selectedDate = e.date;
    });
  },
  
  /**
   * watch: Watchers for reactive data changes
   * Re-render calendar when events array changes to update visual indicators
   */
  watch: {
    events: {
      handler() {
        // Refresh the datepicker to update visual indicators when events change
        this.$nextTick(() => {
          const $datepicker = $(this.$refs.datepickerEl as HTMLElement);
          // Get current date to maintain the view
          const currentDate = $datepicker.datepicker('getDate');
          // Update the datepicker to re-render with new event badges
          $datepicker.datepicker('update');
        });
      },
      deep: true
    }
  }
};
</script>

<style scoped>
/* Cursor pointer for clickable event items */
.cursor-pointer {
  cursor: pointer;
}

/* Hover effect for event list items */
.hover-shadow {
  transition: box-shadow 0.2s ease-in-out;
}

.hover-shadow:hover {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

/* Calendar day cell customization for dates with events */
:deep(.datepicker .datepicker-days td.has-events) {
  position: relative;
  vertical-align: top;
  padding: 4px 2px;
}

/* Day content wrapper */
:deep(.datepicker .day-content) {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  height: 100%;
}

/* Day number styling */
:deep(.datepicker .day-number) {
  display: block;
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 3px;
}

/* Event bands container */
:deep(.datepicker .event-bands) {
  display: flex;
  flex-direction: column;
  gap: 2px;
  width: 100%;
}

/* Individual event band - colored bar with title */
:deep(.datepicker .event-band) {
  padding: 2px 4px;
  border-radius: 3px;
  color: #fff;
  font-size: 10px;
  font-weight: 600;
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.3;
}

/* Event band color variations matching Bootstrap theme */
:deep(.datepicker .event-band-primary) {
  background-color: #727cf5;
}

:deep(.datepicker .event-band-success) {
  background-color: #0acf97;
}

:deep(.datepicker .event-band-info) {
  background-color: #39afd1;
}

:deep(.datepicker .event-band-warning) {
  background-color: #ffbc00;
}

:deep(.datepicker .event-band-danger) {
  background-color: #fa5c7c;
}

:deep(.datepicker .event-band-secondary) {
  background-color: #6c757d;
}

/* "More" indicator for days with 4+ events */
:deep(.datepicker .event-more) {
  font-size: 9px;
  color: #6c757d;
  margin-top: 2px;
  font-weight: 500;
}

/* Make day cells taller to accommodate event bands */
:deep(.datepicker .datepicker-days td) {
  position: relative;
  height: 60px;
  width: 42px;
  padding: 2px;
}

/* Ensure today highlight still works with custom content */
:deep(.datepicker .datepicker-days td.today) {
  background-color: #f1f3fa !important;
}
</style>
