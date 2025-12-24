<template>
  <!-- Calendar with left-side event list -->
  <b-row class="calendar-row">
    <!-- Event List Card (Left Side) -->
    <b-col md="3" class="d-flex">
      <div class="card flex-fill">
        <div class="card-body d-flex flex-column">
          <!-- Loading State -->
          <div v-if="eventsLoading" class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
          </div>
          
          <!-- Event List -->
          <div v-else-if="visibleEvents.length > 0" class="event-list flex-grow-1">
            <div
              v-for="event in visibleEvents"
              :key="event.id"
              class="event-item mb-2 p-2 rounded hover-shadow cursor-pointer"
              @click="editEvent(event)"
            >
              <div>
                <div class="mb-1">
                  <span 
                    class="badge"
                    :class="getEventBadgeClass(event.event_type || event.category || 'milestone')"
                  >
                    {{ getEventTypeLabel(event.event_type || event.category || 'milestone') }}
                  </span>
                </div>
                <h6 class="mb-1 fw-semibold">{{ getEventTitle(event) }}</h6>
                <p class="mb-0 text-muted small">
                  <i class="mdi mdi-clock-outline me-1"></i>{{ event.time }}
                </p>
              </div>
            </div>
          </div>
          
          <!-- No Events State -->
          <div v-else class="text-center py-4 text-muted flex-grow-1 d-flex flex-column justify-content-center">
            <i class="mdi mdi-calendar-blank mdi-48px mb-2"></i>
            <p class="mb-0">No events for this period</p>
          </div>
        </div>
      </div>
    </b-col>
    
    <!-- FullCalendar (Right Side) -->
    <b-col md="9">
      <div class="calendar-widget calendar-widget-inline">
        <FullCalendar
          ref="fullCalendar"
          :options="calendarOptions"
        />
      </div>
    </b-col>
  </b-row>

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
import FullCalendar from '@fullcalendar/vue3';
import dayGridPlugin from '@fullcalendar/daygrid';
import interactionPlugin from '@fullcalendar/interaction';
import { getCalendarEventBadgeTone, getCalendarEventColors } from '@/config/badgeTokens';
import type { BadgeToneKey } from '@/config/badgeTokens';

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
  servicer_id?: string; // Servicer ID for ServicerLoanData events
  address?: string; // Property address for display
  event_type?: string; // Event type for tag display (actual_liquidation, bid_date, etc.)
  url?: string; // URL to navigate to asset detail page
  source_id?: number; // Source record ID
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

  components: {
    FullCalendar,
  },
  
  data() {
    return {
      // FullCalendar configuration
      calendarOptions: {
        plugins: [dayGridPlugin, interactionPlugin],
        initialView: 'dayGridMonth',
        // keep selectedDate in sync when user clicks a day
        dateClick: (arg: any) => this.handleDateClick(arg),
        // events will be synced from this.events in lifecycle hooks
        events: [] as any[],
        // Hide dates from adjacent months (only show current month dates)
        showNonCurrentDates: false,
        fixedWeekCount: false,
        // Custom event content to show tag above title
        eventContent: (arg: any) => {
          const event = arg.event;
          const eventType = event.extendedProps.event_type || 'milestone';
          const eventTypeLabel = this.getEventTypeLabel(eventType);
          const eventTitle = event.title.replace(`${eventTypeLabel}: `, '');
          
          return {
            html: `
              <div style="padding: 2px 4px; line-height: 1.2;">
                <div style="font-size: 0.65em; font-weight: 700; text-transform: uppercase; letter-spacing: 0.3px;">${eventTypeLabel}</div>
                <div style="font-size: 0.75em; margin-top: 2px; white-space: normal; overflow: hidden;">${eventTitle}</div>
              </div>
            `
          };
        },
      },
      // selectedDate: Currently selected date from the datepicker (Date object)
      selectedDate: new Date(),
      
      viewMode: 'week',
      
      // showEventModal: Controls visibility of the add/edit event modal
      showEventModal: false,
      // For now, we are using local data only (no backend fetch)
      eventsLoading: false,
      
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
      
      // events: Array of all calendar events (currently in-memory / localStorage)
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
      ],
      
      // Event type to badge tone mapping (uses centralized badgeTokens.ts)
      // Removed local mapping - now using getCalendarEventBadgeTone() helper
      
      // API base URL (without /api prefix - added in fetch call)
      apiBaseUrl: import.meta.env.VITE_API_BASE_URL || '',
    };
  },
  
  created() {
    // Fetch events from backend API on component creation
    this.fetchCalendarEvents();
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
    },

    visibleEvents(): CalendarEvent[] {
      const selected = this.selectedDate;
      if (!selected) return [];

      if (this.viewMode === 'week') {
        const { start, end } = this.getWeekRange(selected);
        const startTime = start.getTime();
        const endTime = end.getTime();
        return this.events.filter(event => {
          const d = this.parseDateStr(event.date);
          const t = d.getTime();
          return t >= startTime && t <= endTime;
        });
      } else if (this.viewMode === 'month') {
        return this.events.filter(event => {
          const d = this.parseDateStr(event.date);
          return this.isSameMonth(d, selected);
        });
      }

      const selectedDateStr = this.formatDateToString(selected);
      return this.events.filter(event => event.date === selectedDateStr);
    },

    viewTitle(): string {
      if (this.viewMode === 'week') {
        const { start, end } = this.getWeekRange(this.selectedDate);
        const startStr = start.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        const endStr = end.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        const year = this.selectedDate.getFullYear();
        return `${startStr} - ${endStr}, ${year}`;
      } else if (this.viewMode === 'month') {
        return this.selectedDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
      }
      return this.selectedDateFormatted;
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
     * getEventBadgeClass: Maps event type to badge CSS classes using centralized badgeTokens
     * @param eventType - Event type (e.g., 'actual_liquidation')
     * @returns Badge CSS classes from centralized badge system
     */
    getEventBadgeClass(eventType: string): string {
      const tone = getCalendarEventBadgeTone(eventType);
      // Map tone to Bootstrap classes (matches badgeTokens.ts definitions)
      const toneClassMap: Record<BadgeToneKey, string> = {
        'calendar-liquidation': 'bg-success text-white',
        'calendar-projected': 'bg-warning text-dark',
        'calendar-bid': 'bg-info text-white',
        'calendar-settlement': 'bg-danger text-white',
        'calendar-milestone': 'bg-primary text-white',
      } as any;
      return toneClassMap[tone] || 'bg-primary text-white';
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

    getEventTitle(event: any): string {
      if (event.servicer_id && event.address) {
        return `${event.servicer_id} - ${event.address}`;
      }
      return event.title;
    },

    getEventTypeLabel(eventType: string): string {
      const typeMap: Record<string, string> = {
        'actual_liquidation': 'Liquidation',
        'projected_liquidation': 'Projected',
        'bid_date': 'Bid Date',
        'settlement_date': 'Settlement',
        'milestone': 'Milestone'
      };
      return typeMap[eventType] || eventType;
    },
    navigateToAsset(event: any) {
      // Extract asset_hub_id from the event URL or source_id
      const response = this.events.find(e => e.id === event.id);
      if (response) {
        // Backend provides URL in format '/am/loan/{asset_hub_id}/'
        const urlMatch = event.id.match(/servicer_data:(\d+):/);
        if (urlMatch) {
          const servicerDataId = urlMatch[1];
          // Navigate to the asset detail page
          // The backend should provide the correct URL in the event.url field
          window.location.href = `/am/loan/${servicerDataId}/`;
        }
      }
    },
    
    // Map our CalendarEvent objects into FullCalendar's event format
    syncCalendarEvents() {
      if (!this.calendarOptions) return;
      this.calendarOptions.events = this.events.map((event: CalendarEvent) => {
        const eventTypeLabel = this.getEventTypeLabel(event.event_type || event.category || 'milestone');
        const eventTitle = this.getEventTitle(event);
        const colors = getCalendarEventColors(event.event_type || event.category || 'milestone');
        return {
          id: String(event.id),
          title: `${eventTypeLabel}: ${eventTitle}`,
          start: event.date,
          backgroundColor: colors.bg,
          borderColor: colors.border,
          textColor: colors.text,
          extendedProps: {
            originalEvent: event,
            category: event.category,
            event_type: event.event_type,
          },
        };
      });
    },

    // Handle clicks on a date in the FullCalendar grid
    handleDateClick(arg: any) {
      if (arg && arg.dateStr) {
        this.selectedDate = new Date(arg.dateStr);
      }
    },

    parseDateStr(dateStr: string): Date {
      const [y, m, d] = dateStr.split('-').map(Number);
      return new Date(y, m - 1, d);
    },

    getWeekRange(date: Date) {
      const day = date.getDay();
      const start = new Date(date);
      start.setHours(0, 0, 0, 0);
      start.setDate(date.getDate() - day);
      const end = new Date(start);
      end.setDate(start.getDate() + 6);
      end.setHours(23, 59, 59, 999);
      return { start, end };
    },

    isSameMonth(a: Date, b: Date): boolean {
      return a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth();
    },

    saveToLocalStorage() {
      localStorage.setItem('calendarEvents', JSON.stringify(this.events));
      localStorage.setItem('calendarNextId', String(this.nextId));
    },
    
    /**
     * fetchCalendarEvents: Fetches calendar events from backend API
     * Endpoint: GET /api/core/calendar/events/
     * Maps backend event structure to frontend CalendarEvent format
     */
    async fetchCalendarEvents() {
      this.eventsLoading = true;
      try {
        const response = await fetch(`${this.apiBaseUrl}/api/core/calendar/events/`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const backendEvents = await response.json();
        
        // Map backend events to frontend CalendarEvent format
        this.events = backendEvents.map((event: any) => ({
          id: event.id,
          title: event.title,
          date: event.date,
          time: event.time || 'All Day',
          description: event.description || '',
          category: event.category || 'bg-primary',
          servicer_id: event.servicer_id,
          address: event.address,
          event_type: event.event_type || event.category || 'milestone',
          url: event.url,
          source_id: event.source_id,
          editable: event.editable || false,
        }));
        
        // Sync events to FullCalendar
        this.syncCalendarEvents();
      } catch (error) {
        console.error('Failed to fetch calendar events:', error);
        // Fallback to localStorage if API fails
        this.loadFromLocalStorage();
        this.syncCalendarEvents();
      } finally {
        this.eventsLoading = false;
      }
    },
    
    /**
     * loadFromLocalStorage: Loads events from localStorage as fallback
     * NOTE: Only used when backend API is unavailable
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
   * watch: Watchers for reactive data changes
   * Re-render calendar when events array changes to update visual indicators
   */
  watch: {
    events: {
      handler() {
        // Keep FullCalendar's events in sync with our underlying events array
        this.syncCalendarEvents();
      },
      deep: true
    }
  }
};
</script>

<style>
/* 
  FullCalendar container should use the same background as normal .card tiles
  
  HOW TO FIND THE CORRECT CARD BACKGROUND COLOR:
  1. Check which theme is active in your project (saas, creative, or modern)
  2. Open: frontend_vue/src/assets/scss/config/{theme}/_variables.scss
  3. Search for: $body-secondary-bg
  4. This variable defines the card background color
  5. For saas theme: $body-secondary-bg: #FDFBF7 (Warm White)
  6. For creative/modern themes: $body-secondary-bg: $white (#fff)
  
  SCSS CHAIN:
  - Cards use: $card-bg (defined in same _variables.scss file)
  - $card-bg references: var(--#{$prefix}secondary-bg)
  - Which maps to: $body-secondary-bg
  - Final value for saas theme: #FDFBF7
*/
.calendar-widget-inline {
  /* Cards use $body-secondary-bg = #FDFBF7 (Warm White from saas theme) */
  background-color: #FDFBF7;
  border-radius: 0.5rem;
  padding: 16px;
}

/* Let the card background show through FullCalendar itself */
.calendar-widget-inline .fc {
  background-color: transparent;
}

/* Event List Styles */
.event-list {
  max-height: 600px;
  overflow-y: auto;
}

.event-item {
  background-color: var(--bs-tertiary-bg);
  border: 1px solid var(--bs-border-color);
  transition: all 0.2s ease-in-out;
}

.event-item:hover {
  background-color: var(--bs-secondary-bg);
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  border-color: var(--bs-primary);
}

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

/* Make ALL calendar day cells the same height and alignment (legacy styles for old datepicker) */
.calendar-widget .day-content {
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  width: 100% !important;
  height: 100% !important;
}

/* Day number styling - stays at top */
.calendar-widget .day-number {
  display: block !important;
  font-weight: 600 !important;
  font-size: 13px !important;
  margin-bottom: 3px !important;
  flex-shrink: 0 !important;
}

/* Event bands container - flows below day number */
.calendar-widget .event-bands {
  display: flex !important;
  flex-direction: column !important;
  gap: 2px !important;
  width: 100% !important;
  flex-grow: 0 !important;
  align-items: center !important;
}

/* No custom styling for inline calendar badges - use vanilla Bootstrap */

/* "More" indicator for days with 4+ events */
.calendar-widget .event-more {
  font-size: 9px;
  color: #6c757d;
  margin-top: 2px;
  font-weight: 500;
}

/* Enable horizontal scrolling for the calendar table */
.calendar-widget .datepicker {
  width: 100% !important;
}

.calendar-widget .datepicker .table-condensed {
  min-width: 850px !important; /* Force table to be wide enough for badges */
  width: 100% !important;
  table-layout: fixed !important;
}

div.calendar-widget {
  overflow-x: auto !important;
  width: 100% !important;
  display: block !important;
}

/* Make day cells taller and wider to accommodate full event badges */
.calendar-widget .datepicker-days td {
  position: relative;
  height: 100px !important;
  min-width: 120px !important;
  padding: 4px !important;
  vertical-align: top !important;
  overflow: visible !important; /* Allow badges to be fully visible */
  white-space: normal !important;
}

/* Ensure today highlight still works with custom content */
.calendar-widget .datepicker-days td.today {
  background-color: #f1f3fa !important;
}

/* Modern event card styling */
.event-card {
  padding: 10px 12px;
  border-radius: 6px;
  background: #ffffff;
  border: 1px solid #e3e6ef;
  cursor: pointer;
  transition: all 0.2s ease;
}

.event-card:hover {
  background: #f8f9fa;
  border-color: #727cf5;
  box-shadow: 0 2px 8px rgba(114, 124, 245, 0.15);
  transform: translateX(2px);
}

.event-card-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.event-title-centered {
  font-size: 13px;
  font-weight: 500;
  color: #313a46;
  line-height: 1.4;
  text-align: center;
  width: 100%;
}

.event-badge {
  font-size: 10px;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  white-space: nowrap;
  align-self: flex-start;
}

/* REMOVED: Scale down badges inside calendar day cells to fit */
/* Badges will now inherit the standard .event-badge styling */
</style>
