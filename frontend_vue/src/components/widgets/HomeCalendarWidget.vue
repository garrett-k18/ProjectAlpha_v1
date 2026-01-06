<template>
  <!-- WHAT: Container for calendar widget with shared filter bar and two-column layout -->
  <!-- WHY: Filters should control both the event list and calendar simultaneously -->
  <!-- HOW: Single unified card containing filter bar and calendar/event grid -->
  <div class="calendar-section">
    <!-- Unified Card for entire Calendar Section -->
    <div class="card">
      <!-- Filter Bar (Header-like toolbar) -->
      <!-- WHAT: Filter buttons to show/hide events by tag type -->
      <!-- WHY: Users need to filter events by type across both calendar and event list -->
      <!-- HOW: Always display filter bar to prevent layout shifts during month navigation -->
      <!-- NOTE: Always rendered (no v-if) to prevent flicker and layout rearrangement -->
      <div class="card-header py-2 border-bottom" style="min-height: 48px; display: block;">
        <div class="d-flex flex-wrap gap-2 align-items-center">
          <span class="small text-muted fw-semibold me-2">Filter:</span>
          <!-- All Events Button -->
          <button
            type="button"
            class="btn btn-sm"
            :class="selectedEventTypeFilters.length === 0 ? 'btn-light border border-2 border-secondary' : 'btn-outline-secondary'"
            :disabled="eventsLoading"
            @click="selectedEventTypeFilters = []"
          >
            All
          </button>
          <!-- Event Type Filter Buttons (Multi-select) -->
          <button
            v-for="eventType in availableEventTypes"
            :key="eventType"
            type="button"
            class="btn btn-sm"
            :class="selectedEventTypeFilters.includes(eventType) ? 'btn-light border border-2 border-secondary' : 'btn-outline-secondary'"
            :disabled="eventsLoading"
            @click="toggleEventTypeFilter(eventType)"
          >
            {{ getEventTypeLabel(eventType) }}
          </button>
        </div>
      </div>
      
      <!-- Card Body - Event List + Calendar Grid -->
      <div class="card-body p-0 d-flex">
        <!-- Calendar with left-side event list -->
        <!-- WHAT: Row container for calendar widget with equal-height columns -->
        <!-- WHY: Event list and calendar should have same height for visual consistency -->
        <!-- HOW: Use align-items-stretch to make both columns same height -->
        <b-row class="calendar-row align-items-start g-0 flex-grow-1 w-100">
      <!-- Event List Panel (Left Side) -->
      <!-- WHAT: Event list that displays all events for the currently visible month -->
      <!-- WHY: Users need to see a scrollable list of events matching the calendar -->
      <!-- HOW: Left border separates from calendar, fills full height with scroll -->
      <b-col md="3" class="event-list-panel border-end d-flex flex-column" :style="eventListPanelStyle">
        <!-- Loading State -->
        <div v-if="eventsLoading" class="text-center py-4 px-3 flex-grow-1 d-flex align-items-center justify-content-center">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>
        
        <!-- Event List -->
        <!-- WHAT: Container for event items -->
        <!-- WHY: Events should fill the entire panel height with scroll if needed -->
        <!-- HOW: overflow-auto for scrolling within fixed height -->
        <div v-if="!eventsLoading && visibleEvents.length > 0" class="event-list p-3 overflow-auto">
          <div
            v-for="event in visibleEvents"
            :key="event.id"
            class="event-item mb-2 p-2 rounded hover-shadow"
            :class="{ 'cursor-pointer': isLiquidationEvent(event) }"
            @click="handleEventClick(event)"
          >
            <div>
              <div class="mb-1 d-flex justify-content-between align-items-center">
                <span 
                  class="badge"
                  :class="getEventBadgeClass(event.event_type || event.category || 'milestone')"
                  :style="getEventBadgeStyle(event.event_type || event.category || 'milestone')"
                >
                  {{ getEventTypeLabel(event.event_type || event.category || 'milestone') }}
                </span>
                <!-- WHAT: Display formatted date for each event -->
                <!-- WHY: Users need to see which day of the month each event occurs -->
                <!-- HOW: Parse event.date string and format as "Day, Month D" (e.g., "Mon, Dec 1") -->
                <span class="text-muted small fw-semibold">
                  {{ formatEventDate(event.date) }}
                </span>
              </div>
              <h6 class="mb-0 fw-semibold small">{{ getEventTitle(event) }}</h6>
              <!-- WHAT: Display city and state for follow-up, realized liquidation, and projected liquidation events -->
              <!-- WHY: Users need location context for these event types -->
              <!-- HOW: Show city and state if available and event type matches -->
              <div 
                v-if="shouldShowLocation(event)" 
                class="text-muted small mt-1"
              >
                {{ getLocationDisplay(event) }}
              </div>
            </div>
          </div>
        </div>
        
        <!-- No Events State -->
        <div v-else-if="!eventsLoading && visibleEvents.length === 0" class="text-center py-4 px-3 text-muted d-flex flex-column justify-content-center align-items-center flex-grow-1">
          <i class="mdi mdi-calendar-blank mdi-36px mb-2 opacity-50"></i>
          <p class="mb-0 small">No events for this period</p>
        </div>
      </b-col>
      
      <!-- FullCalendar (Right Side) -->
      <b-col md="9" class="p-3">
        <div ref="calendarWrapper" class="calendar-widget calendar-widget-inline">
          <FullCalendar
            ref="fullCalendar"
            :options="calendarOptions"
          />
        </div>
      </b-col>
    </b-row>
      </div><!-- End card-body -->
    </div><!-- End unified card -->
  </div><!-- End calendar-section -->

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
import { getCalendarEventBadgeTone, getCalendarEventColors, resolveBadgeTokens } from '@/config/badgeTokens';
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
  source_id?: number; // Source record ID (e.g., ServicerLoanData.id)
  asset_hub_id?: number; // AssetIdHub ID for opening modal
  editable?: boolean; // Whether the event can be edited
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
  
  // Declare emits so parent can listen to open-asset-modal event
  emits: ['open-asset-modal'],
  
  data() {
    return {
      // FullCalendar configuration
      calendarOptions: {
        plugins: [dayGridPlugin, interactionPlugin],
        initialView: 'dayGridMonth',
        height: 'auto',
        contentHeight: 'auto',
        expandRows: false,
        // WHAT: Disable event dragging - events are read-only from backend
        // WHY: Calendar events come from database models and shouldn't be moved by dragging
        // HOW: Set editable and eventStartEditable to false
        editable: false,
        eventStartEditable: false,
        eventDurationEditable: false,
        // keep selectedDate in sync when user clicks a day
        dateClick: (arg: any) => this.handleDateClick(arg),
        // Handle clicks on calendar events - only liquidation events open modal
        eventClick: (arg: any) => {
          const originalEvent = arg.event.extendedProps.originalEvent;
          if (originalEvent) {
            this.handleEventClick(originalEvent);
          }
        },
        // WHAT: Callback fired when calendar view changes (e.g., month navigation)
        // WHY: Updates currentViewDate and fetches events for the visible date range
        // HOW: FullCalendar passes date information when user navigates months
        datesSet: (arg: any) => {
          // WHAT: Update currentViewDate to the start of the displayed month
          // WHY: Event list needs to know which month to filter for
          // HOW: Use FullCalendar's start date (first day of visible month)
          if (arg.start) {
            const newViewDate = new Date(arg.start);
            // WHAT: Set to first day of the month to ensure consistent month comparison
            newViewDate.setDate(1);
            (this as any).currentViewDate = newViewDate;
            console.log('[HomeCalendarWidget] datesSet - Updated currentViewDate to:', (this as any).currentViewDate.toISOString());
          }
          // WHAT: Fetch events for the visible date range to avoid loading all events
          // WHY: Only fetch events for months being displayed, not all events ever
          // HOW: Use FullCalendar's start/end dates with small buffer to ensure edge events are included
          if (arg.start && arg.end) {
            // WHAT: Add 7-day buffer before start and after end to catch events near edges
            // WHY: FullCalendar might cut off events on month boundaries
            const bufferedStart = new Date(arg.start);
            bufferedStart.setDate(bufferedStart.getDate() - 7);
            const bufferedEnd = new Date(arg.end);
            bufferedEnd.setDate(bufferedEnd.getDate() + 7);
            this.fetchCalendarEventsForRange(bufferedStart, bufferedEnd);
          }
        },
        // events will be synced from this.events in lifecycle hooks
        events: [] as any[],
        // Hide dates from adjacent months (only show current month dates)
        showNonCurrentDates: false,
        fixedWeekCount: false,
        // Limit events shown per day cell; render built-in "+n more" expander
        dayMaxEvents: 3,
        // Custom event content to show tag above title
        eventContent: (arg: any) => {
          const event = arg.event;
          const eventType = event.extendedProps.event_type || 'milestone';
          const eventTypeLabel = this.getEventTypeLabel(eventType);
          const eventTitle = event.title.replace(`${eventTypeLabel}: `, '');
          
          return {
            html: `
              <div style="padding: 4px 6px; line-height: 1.25; max-width: 100%;">
                <div style="font-size: 0.75em; font-weight: 700; text-transform: uppercase; letter-spacing: 0.3px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${eventTypeLabel}</div>
                <div style="font-size: 0.85em; margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${eventTitle}</div>
              </div>
            `
          };
        },
        // WHAT: Add tooltip on hover for all events
        // WHY: Tiles are clamped to 2 lines, so users need hover to see full text
        // HOW: Set native title attribute on the rendered event element
        // NOTE: Removed updateEventListMaxHeight call from here to prevent layout shifts during month navigation
        eventDidMount: (arg: any) => {
          const originalEvent = arg?.event?.extendedProps?.originalEvent;
          const eventType = arg?.event?.extendedProps?.event_type || 'milestone';
          const eventTypeLabel = this.getEventTypeLabel(eventType);
          const fullTitle = originalEvent ? this.getEventTitle(originalEvent) : (arg?.event?.title || '');
          if (arg?.el) {
            arg.el.setAttribute('title', `${eventTypeLabel}: ${fullTitle}`);
          }
          // NOTE: Height updates are now handled only in syncCalendarEvents with debouncing to prevent flicker
        },
      },
      // selectedDate: Currently selected date from the datepicker (Date object)
      selectedDate: new Date(),
      
      // currentViewDate: The currently displayed month/year in the calendar view
      // WHAT: Tracks which month is being displayed in FullCalendar
      // WHY: Event list needs to know which month to filter for
      // HOW: Updated via FullCalendar's datesSet callback when user navigates months
      currentViewDate: new Date(),
      
      viewMode: 'month', // Changed default to 'month' to match calendar display
      
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
      
      // selectedEventTypeFilters: Array of selected event type filters (empty = show all)
      // WHAT: Tracks which event types are selected for filtering (supports multiple selections)
      // WHY: Users need to filter events by multiple tag types simultaneously (e.g., Liquidation AND Bid Date)
      // HOW: Array of event_type strings, empty array means show all events
      selectedEventTypeFilters: [] as string[],
      
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
      
      // Event list panel should not exceed the calendar's rendered height
      eventListMaxHeightPx: null as number | null,
      
      // WHAT: Debounce timer for height updates to prevent layout shifts
      // WHY: Multiple rapid height updates cause flicker and layout rearrangement
      // HOW: Store timeout ID to cancel previous updates if new one is triggered
      heightUpdateTimeout: null as ReturnType<typeof setTimeout> | null,
    };
  },
  
  created() {
    // WHAT: Initial setup - events will be fetched when FullCalendar fires datesSet
    // WHY: FullCalendar determines the initial month to display, we need to wait for it
    // HOW: datesSet callback will fetch events for the correct month
    // NOTE: Don't fetch here - let datesSet handle it to ensure we fetch for the correct month
  },
  
  mounted() {
    // WHAT: Restore filter state from localStorage on component mount
    // WHY: Users expect filter selection to persist across page reloads and month navigation
    // HOW: Load filter from localStorage before doing anything else
    this.loadFromLocalStorage();
    
    // WHAT: After component is mounted, ensure we have events for the displayed month
    // WHY: FullCalendar might not fire datesSet immediately, so we need a fallback
    // HOW: Use nextTick to wait for FullCalendar to initialize, then check if we need to fetch
    this.$nextTick(() => {
      // If FullCalendar hasn't fired datesSet yet, fetch for current month as fallback
      if (this.events.length === 0) {
        const now = new Date();
        const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
        const endOfMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0);
        (this as any).currentViewDate = startOfMonth; // Set to match what we're fetching
        this.fetchCalendarEventsForRange(startOfMonth, endOfMonth);
      }
    });

    window.addEventListener('resize', this.updateEventListMaxHeight);
  },

  beforeUnmount() {
    window.removeEventListener('resize', this.updateEventListMaxHeight);
    // WHAT: Clear any pending height update timers to prevent memory leaks
    // WHY: Component cleanup should clear all timers
    if (this.heightUpdateTimeout) {
      clearTimeout(this.heightUpdateTimeout);
    }
  },

  computed: {
    eventListPanelStyle(): Record<string, string> {
      if (!this.eventListMaxHeightPx) {
        console.log('[Height Debug] eventListPanelStyle: No height set, returning empty object');
        return {};
      }
      const style = {
        maxHeight: `${this.eventListMaxHeightPx}px`,
        height: `${this.eventListMaxHeightPx}px`,
      };
      console.log('[Height Debug] eventListPanelStyle returning:', style);
      return style;
    },

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

    /**
     * availableEventTypes: Returns all possible event types defined in the system
     * WHAT: Returns all event types that can appear in the calendar, not just those in current month
     * WHY: Filter buttons should always show all available types, even if none exist in current month
     * HOW: Return all event types defined in getEventTypeLabel typeMap
     */
    availableEventTypes(): string[] {
      // WHAT: Return all event types that are defined in the system
      // WHY: Users should be able to filter by any event type, even if none exist in current month
      // HOW: Use the same types defined in getEventTypeLabel function
      return [
        'actual_liquidation',
        'projected_liquidation',
        'bid_date',
        'settlement_date',
        'follow_up',
        'milestone'
      ];
    },
    
    /**
     * visibleEvents: Returns events for the currently displayed month in the calendar
     * WHAT: Filters events to show only those in the month currently being displayed, optionally filtered by event type, sorted by date
     * WHY: Event list should match what's visible in the calendar widget and be easy to scan
     * HOW: Uses currentViewDate (updated via FullCalendar's datesSet callback) to filter events, then applies event type filter if selected, then sorts by date
     */
    visibleEvents(): CalendarEvent[] {
      console.log('[HomeCalendarWidget] visibleEvents - Total events:', this.events.length, 
        'Current view date:', (this as any).currentViewDate?.toISOString());
      
      // WHAT: Start with all events - we'll filter by month and type
      // WHY: Need to see all events first, then apply filters
      let filtered = [...this.events];
      
      // WHAT: Filter events to show only those in the month currently displayed in FullCalendar
      // WHY: Keep event list synchronized with calendar widget view
      // HOW: Compare each event's date with currentViewDate to check if same month/year
      if ((this as any).currentViewDate) {
        const beforeMonthFilter = filtered.length;
        filtered = filtered.filter(event => {
          const eventDate = this.parseDateStr(event.date);
          const isSame = this.isSameMonth(eventDate, (this as any).currentViewDate);
          if (!isSame && beforeMonthFilter < 20) { // Only log if we have few events
            console.log('[HomeCalendarWidget] Event filtered out by month:', event.date, 
              'Event:', eventDate.toISOString(), 'View:', (this as any).currentViewDate.toISOString(),
              'Event month:', eventDate.getMonth() + 1, 'View month:', (this as any).currentViewDate.getMonth() + 1);
          }
          return isSame;
        });
        console.log('[HomeCalendarWidget] After month filter:', filtered.length, 
          'events (was', beforeMonthFilter, ')');
      } else {
        console.warn('[HomeCalendarWidget] currentViewDate is not set, showing all events');
      }
      
      console.log('[HomeCalendarWidget] Before type filter:', filtered.length, 
        'events. Selected filters:', this.selectedEventTypeFilters);
      
      // WHAT: Apply event type filters if any are selected
      // WHY: Users can filter to see multiple specific event types simultaneously (e.g., Liquidations AND Bid Dates)
      // HOW: Check if event's event_type is included in selectedEventTypeFilters array
      if (this.selectedEventTypeFilters.length > 0) {
        const beforeFilter = filtered.length;
        filtered = filtered.filter(event => {
          const eventType = event.event_type || event.category || 'milestone';
          const matches = this.selectedEventTypeFilters.includes(eventType);
          return matches;
        });
        console.log('[HomeCalendarWidget] After type filter:', filtered.length, 'events (was', beforeFilter, ')');
      }
      
      // WHAT: Sort events by date (earliest first) for easier reading
      // WHY: Users expect chronological order in event lists
      // HOW: Parse date strings and compare timestamps
      return filtered.sort((a, b) => {
        const dateA = this.parseDateStr(a.date).getTime();
        const dateB = this.parseDateStr(b.date).getTime();
        return dateA - dateB;
      });
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
    updateEventListMaxHeight(): void {
      // WHAT: Debounce height updates to prevent layout shifts during month navigation
      // WHY: Multiple rapid updates cause flicker and window rearrangement
      // HOW: Clear previous timeout and set new one with delay
      if (this.heightUpdateTimeout) {
        clearTimeout(this.heightUpdateTimeout);
      }
      
      this.heightUpdateTimeout = setTimeout(() => {
        this.$nextTick(() => {
          const wrapperEl = (this.$refs.calendarWrapper as HTMLElement | undefined);
          if (!wrapperEl) {
            console.log('[Height Debug] No calendarWrapper ref found');
            return;
          }

          const gridEl =
            (wrapperEl.querySelector?.('.fc-scrollgrid') as HTMLElement | null) ||
            (wrapperEl.querySelector?.('.fc-daygrid-body') as HTMLElement | null) ||
            (wrapperEl.querySelector?.('.fc-view-harness') as HTMLElement | null) ||
            (wrapperEl.querySelector?.('.fc') as HTMLElement | null);

          const wrapperRect = wrapperEl.getBoundingClientRect();
          const gridRect = (gridEl || wrapperEl).getBoundingClientRect();

          // Height from top of calendar widget to bottom of the month grid
          const nextHeight = Math.round(gridRect.bottom - wrapperRect.top);
          
          // WHAT: Only update if height actually changed to prevent unnecessary re-renders
          // WHY: Avoid triggering Vue reactivity if value is the same
          if (nextHeight > 0 && nextHeight !== this.eventListMaxHeightPx) {
            this.eventListMaxHeightPx = nextHeight;
          }
        });
      }, 300); // WHAT: 300ms debounce delay to allow layout to settle
    },

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
      // NOTE: All calendar event types now use inline styles for custom palette colors
      const toneClassMap: Record<BadgeToneKey, string> = {
        'calendar-liquidation': 'text-white',
        'calendar-projected': 'text-white',
        'calendar-bid': 'text-white',
        'calendar-settlement': 'text-white',
        'calendar-follow-up': 'text-white',
        'calendar-milestone': 'text-white',
      } as any;
      return toneClassMap[tone] || 'text-white';
    },
    
    /**
     * getEventBadgeStyle: Returns inline styles for badges that need custom colors
     * @param eventType - Event type (e.g., 'actual_liquidation')
     * @returns Inline style string for custom badge colors
     */
    getEventBadgeStyle(eventType: string): string | undefined {
      const tone = getCalendarEventBadgeTone(eventType);
      // WHAT: Return inline styles for custom colors (purple for projected, orange for follow-up)
      // WHY: These colors aren't available as Bootstrap classes
      // HOW: Use inline styles from badgeTokens configuration
      const badgeTokens = resolveBadgeTokens(tone, 'md');
      return badgeTokens.inlineStyles || undefined;
    },
    
    /**
     * shouldShowLocation: Determines if city/state should be displayed for an event
     * @param event - Calendar event object
     * @returns True if location should be shown (follow-up, realized liquidation, projected liquidation)
     */
    shouldShowLocation(event: any): boolean {
      const eventType = event.event_type || event.category || '';
      const locationEvents = ['follow_up', 'actual_liquidation', 'projected_liquidation'];
      return locationEvents.includes(eventType) && (event.city || event.state);
    },
    
    /**
     * getLocationDisplay: Formats city and state for display
     * @param event - Calendar event object
     * @returns Formatted city, state string
     */
    getLocationDisplay(event: any): string {
      const parts: string[] = [];
      if (event.city) {
        parts.push(event.city);
      }
      if (event.state) {
        parts.push(event.state);
      }
      return parts.join(', ') || '';
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
      const eventType = event.event_type || event.category || '';
      // WHAT: Format follow_up events as "servicer_id - address"
      // WHY: Consistent format for follow-up events
      if (eventType === 'follow_up' && event.servicer_id) {
        if (event.address) {
          return `${event.servicer_id} - ${event.address}`;
        }
        return String(event.servicer_id);
      }
      // WHAT: Format projected_liquidation events same as follow_up: "servicer_id - address"
      // WHY: Consistent format across event types
      if (eventType === 'projected_liquidation' && event.servicer_id) {
        if (event.address) {
          return `${event.servicer_id} - ${event.address}`;
        }
        return String(event.servicer_id);
      }
      if (eventType === 'follow_up' && typeof event.title === 'string') {
        const trimmed = event.title.trim();
        if (trimmed.toLowerCase().startsWith('follow-up:')) {
          return trimmed.slice('follow-up:'.length).trim();
        }
      }
      // WHAT: Fallback for other event types with servicer_id and address
      // WHY: Maintain consistent format when possible
      if (event.servicer_id && event.address) {
        return `${event.servicer_id} - ${event.address}`;
      }
      return event.title;
    },

    getEventTypeLabel(eventType: string): string {
      const typeMap: Record<string, string> = {
        'actual_liquidation': 'Realized Liquidation',
        'projected_liquidation': 'Projected Liquidation',
        'bid_date': 'Bid Date',
        'settlement_date': 'Settlement',
        'follow_up': 'Follow-up',
        'milestone': 'Milestone'
      };
      return typeMap[eventType] || eventType;
    },
    
    // Check if event is a liquidation or follow-up event (both should be clickable)
    isLiquidationEvent(event: any): boolean {
      const eventType = event.event_type || event.category || '';
      return eventType.includes('liquidation') || eventType.includes('follow');
    },
    
    /**
     * toggleEventTypeFilter: Toggle an event type filter on/off
     * WHAT: Adds or removes an event type from the selected filters array
     * WHY: Users can select multiple filters simultaneously
     * HOW: If filter is already selected, remove it; otherwise add it
     * @param eventType - The event type to toggle (e.g., 'actual_liquidation')
     */
    toggleEventTypeFilter(eventType: string): void {
      const index = this.selectedEventTypeFilters.indexOf(eventType);
      if (index > -1) {
        // WHAT: Filter is already selected, remove it
        // WHY: Allow users to deselect filters by clicking again
        this.selectedEventTypeFilters.splice(index, 1);
      } else {
        // WHAT: Filter is not selected, add it
        // WHY: Allow users to select multiple filters
        this.selectedEventTypeFilters.push(eventType);
      }
      // NOTE: Watcher will automatically save to localStorage
    },
    
    // Handle event click - liquidation and follow-up events open asset modal
    handleEventClick(event: any): void {
      console.log('[HomeCalendarWidget] handleEventClick called', event);
      
      if (!this.isLiquidationEvent(event)) {
        return; // Do nothing for non-clickable events
      }
      
      // WHAT: The backend returns asset_hub_id directly in the event object (see view_co_calendar.py)
      // WHY: Both liquidation and follow-up events have asset_hub_id FK
      // HOW: Use event.asset_hub_id (the correct AssetIdHub ID)
      const assetHubId = event?.asset_hub_id || event?.extendedProps?.asset_hub_id;
      
      console.log('[HomeCalendarWidget] Using asset_hub_id:', assetHubId, 'from event:', event);
      
      if (assetHubId) {
        console.log('[HomeCalendarWidget] Emitting open-asset-modal with assetHubId:', assetHubId);
        // Emit to parent to open modal
        this.$emit('open-asset-modal', {
          id: assetHubId,
          row: event,
          addr: event.address || event.extendedProps?.address || this.getEventTitle(event)
        });
      } else {
        console.warn('[HomeCalendarWidget] No asset_hub_id found for event:', event);
      }
    },
    
    // Map our CalendarEvent objects into FullCalendar's event format
    syncCalendarEvents() {
      if (!this.calendarOptions) return;
      
      // WHAT: Filter events based on selectedEventTypeFilters before mapping to FullCalendar format
      // WHY: Calendar view should respect the same filters as the event list
      // HOW: Filter events array, then map filtered results to FullCalendar format
      let filteredEvents = [...this.events];
      
      // WHAT: Apply event type filters if any are selected
      // WHY: Users expect calendar to show only events matching selected filters
      // HOW: Check if event's event_type is included in selectedEventTypeFilters array
      if (this.selectedEventTypeFilters.length > 0) {
        filteredEvents = filteredEvents.filter(event => {
          const eventType = event.event_type || event.category || 'milestone';
          return this.selectedEventTypeFilters.includes(eventType);
        });
      }
      
      // WHAT: Map filtered events to FullCalendar's event format
      // WHY: FullCalendar expects events in a specific format with styling and metadata
      // HOW: Transform each filtered event to include title, colors, and extended properties
      this.calendarOptions.events = filteredEvents.map((event: CalendarEvent) => {
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
          editable: false,  // WHAT: Disable dragging for all events (read-only from backend)
          extendedProps: {
            originalEvent: event,
            category: event.category,
            event_type: event.event_type,
            asset_hub_id: event.asset_hub_id,  // Pass through the AssetIdHub ID
            address: event.address,  // Pass through the address
          },
        };
      });

      // WHAT: Update height only once after all events are synced, with debouncing
      // WHY: Prevent layout shifts during month navigation
      // HOW: Debounced update will wait for layout to settle before calculating
      this.updateEventListMaxHeight();
    },

    // Handle clicks on a date in the FullCalendar grid
    handleDateClick(arg: any) {
      if (arg && arg.dateStr) {
        this.selectedDate = new Date(arg.dateStr);
      }
    },

    /**
     * parseDateStr: Converts YYYY-MM-DD string to Date object
     * WHAT: Parses a date string in YYYY-MM-DD format into a JavaScript Date object
     * WHY: Backend returns dates as strings, but we need Date objects for comparisons/formatting
     * HOW: Split string by dashes, convert to numbers, create Date (month is 0-indexed in JS)
     * @param dateStr - Date string in YYYY-MM-DD format
     * @returns JavaScript Date object
     */
    parseDateStr(dateStr: string): Date {
      const [y, m, d] = dateStr.split('-').map(Number);
      return new Date(y, m - 1, d);
    },
    
    /**
     * formatEventDate: Formats event date for display in event list
     * WHAT: Converts YYYY-MM-DD date string to readable format like "Mon, Dec 1"
     * WHY: Users need a clear indication of which day each event occurs
     * HOW: Parse date string and use toLocaleDateString with abbreviated day/month names
     * @param dateStr - Date string in YYYY-MM-DD format
     * @returns Formatted date string (e.g., "Mon, Dec 1")
     */
    formatEventDate(dateStr: string): string {
      const date = this.parseDateStr(dateStr);
      return date.toLocaleDateString('en-US', { 
        weekday: 'short', 
        month: 'short', 
        day: 'numeric' 
      });
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

    /**
     * isSameMonth: Checks if two dates are in the same month and year
     * WHAT: Compares two Date objects to determine if they fall in the same calendar month
     * WHY: Used to filter events for the displayed month in the event list
     * HOW: Compares year and month properties of both dates
     * @param a - First date to compare
     * @param b - Second date to compare
     * @returns True if both dates are in the same month and year
     */
    isSameMonth(a: Date, b: Date): boolean {
      return a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth();
    },

    saveToLocalStorage() {
      localStorage.setItem('calendarEvents', JSON.stringify(this.events));
      localStorage.setItem('calendarNextId', String(this.nextId));
      // WHAT: Save selected filters array to localStorage for persistence across month navigation
      // WHY: Users expect filter selection to persist when changing months
      // HOW: Store filters array as JSON string, empty array means "All" selected
      if (this.selectedEventTypeFilters.length > 0) {
        localStorage.setItem('calendarEventTypeFilters', JSON.stringify(this.selectedEventTypeFilters));
      } else {
        localStorage.removeItem('calendarEventTypeFilters'); // Clear if "All" is selected
      }
    },
    
    /**
     * fetchCalendarEventsForRange: Fetches calendar events for a specific date range
     * WHAT: Retrieves calendar events from Django backend for the visible date range
     * WHY: Only fetch events for months being displayed to improve performance
     * HOW: Makes GET request with start_date and end_date query parameters
     * @param startDate - Start of date range (Date object)
     * @param endDate - End of date range (Date object)
     */
    async fetchCalendarEventsForRange(startDate: Date, endDate: Date) {
      // WHAT: Set loading state to show spinner in event list
      this.eventsLoading = true;
      try {
        // WHAT: Format dates as YYYY-MM-DD for API
        // WHY: Backend expects date strings in ISO format
        const formatDate = (date: Date) => {
          const year = date.getFullYear();
          const month = String(date.getMonth() + 1).padStart(2, '0');
          const day = String(date.getDate()).padStart(2, '0');
          return `${year}-${month}-${day}`;
        };
        
        const startDateStr = formatDate(startDate);
        const endDateStr = formatDate(endDate);
        
        // WHAT: Fetch events from backend API endpoint with date range filter
        // WHY: Only fetch events for visible months, not all events ever
        const url = `${this.apiBaseUrl}/core/calendar/events/?start_date=${startDateStr}&end_date=${endDateStr}`;
        console.log('[HomeCalendarWidget] Fetching events for range:', startDateStr, 'to', endDateStr);
        
        const response = await fetch(url);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        // WHAT: Parse JSON response from backend
        const backendEvents = await response.json();
        console.log('[HomeCalendarWidget] Received', backendEvents.length, 'events');
        
        // WHAT: Transform backend event structure to match frontend CalendarEvent interface
        // WHY: Backend and frontend may use different field names/structures
        // HOW: Map each backend event to frontend format with all required fields
        // NOTE: Backend sends 'category' field containing the event_type value (e.g., 'actual_liquidation')
        //       This is the semantic event type, NOT a Bootstrap class
        this.events = backendEvents.map((event: any) => {
          // WHAT: Backend 'category' field IS the event_type (e.g., 'actual_liquidation', 'bid_date')
          // WHY: Backend uses 'category' to store the semantic event type from CALENDAR_DATE_FIELDS
          // HOW: Use category directly as event_type
          const eventType = event.event_type || event.category || 'milestone';
          
          return {
            id: event.id,
            title: event.title,
            date: event.date,
            time: event.time || '', // WHAT: Time field kept for compatibility but not displayed
            description: event.description || '',
            category: 'bg-primary', // WHAT: Bootstrap class for badge (derived from event_type by getEventBadgeClass)
            servicer_id: event.servicer_id,
            address: event.address,
            event_type: eventType, // WHAT: Semantic event type from backend 'category' field
            url: event.url,
            source_id: event.source_id,
            editable: event.editable || false,
            asset_hub_id: event.asset_hub_id,  // CRITICAL: Include AssetIdHub ID for modal
          };
        });
        
        console.log('[HomeCalendarWidget] Mapped', this.events.length, 'events. Event types:', 
          [...new Set(this.events.map(e => e.event_type))]);
        
        // WHAT: Ensure currentViewDate is set to match the first event's month if not already set
        // WHY: If datesSet hasn't fired yet, we need currentViewDate to match the loaded events
        // HOW: Use the first event's date to set currentViewDate if it's not already set
        if (this.events.length > 0 && (!(this as any).currentViewDate || (this as any).currentViewDate.getTime() === new Date().getTime())) {
          const firstEventDate = this.parseDateStr(this.events[0].date);
          (this as any).currentViewDate = new Date(firstEventDate.getFullYear(), firstEventDate.getMonth(), 1);
          console.log('[HomeCalendarWidget] Set currentViewDate to first event month:', (this as any).currentViewDate.toISOString());
        }
        
        // WHAT: Sync events to FullCalendar widget so they appear on the calendar grid
        // WHY: FullCalendar needs events in its own format
        this.syncCalendarEvents();
      } catch (error) {
        // WHAT: Log error and fallback to localStorage if API fails
        console.error('Failed to fetch calendar events:', error);
        // WHAT: Load events from browser localStorage as fallback
        this.loadFromLocalStorage();
        // WHAT: Sync loaded events to FullCalendar
        this.syncCalendarEvents();
      } finally {
        // WHAT: Clear loading state regardless of success/failure
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
      
      // WHAT: Load selected filters array from localStorage to restore user's filter preference
      // WHY: Users expect filter selection to persist when changing months or reloading page
      // HOW: Read filters array from localStorage, validate all items are valid event types, then apply
      const storedFiltersStr = localStorage.getItem('calendarEventTypeFilters');
      // WHAT: Also check for old single-filter format for backward compatibility
      const oldStoredFilter = localStorage.getItem('calendarEventTypeFilter');
      
      if (storedFiltersStr) {
        try {
          // WHAT: Parse stored filters array from JSON
          const storedFilters = JSON.parse(storedFiltersStr);
          // WHAT: Validate all stored filters are valid event types
          // WHY: Prevent errors if localStorage contains invalid data
          // HOW: Check against hardcoded list of valid event types
          const validEventTypes = [
            'actual_liquidation',
            'projected_liquidation',
            'bid_date',
            'settlement_date',
            'follow_up',
            'milestone'
          ];
          // WHAT: Filter out any invalid event types and keep only valid ones
          const validFilters = storedFilters.filter((filter: string) => validEventTypes.includes(filter));
          if (validFilters.length > 0) {
            this.selectedEventTypeFilters = validFilters;
            console.log('[HomeCalendarWidget] Restored filters from localStorage:', validFilters);
          } else {
            // All filters were invalid, clear and default to "All"
            localStorage.removeItem('calendarEventTypeFilters');
            this.selectedEventTypeFilters = [];
          }
        } catch (e) {
          console.error('[HomeCalendarWidget] Failed to parse stored filters from localStorage', e);
          localStorage.removeItem('calendarEventTypeFilters');
          this.selectedEventTypeFilters = [];
        }
      } else if (oldStoredFilter) {
        // WHAT: Backward compatibility - migrate old single filter to new array format
        // WHY: Support users who had the old single-filter format saved
        // HOW: Convert single filter string to array, then remove old key
        const validEventTypes = [
          'actual_liquidation',
          'projected_liquidation',
          'bid_date',
          'settlement_date',
          'follow_up',
          'milestone'
        ];
        if (validEventTypes.includes(oldStoredFilter)) {
          this.selectedEventTypeFilters = [oldStoredFilter];
          localStorage.setItem('calendarEventTypeFilters', JSON.stringify([oldStoredFilter]));
          localStorage.removeItem('calendarEventTypeFilter'); // Remove old key
          console.log('[HomeCalendarWidget] Migrated old single filter to array format:', oldStoredFilter);
        } else {
          localStorage.removeItem('calendarEventTypeFilter');
          this.selectedEventTypeFilters = [];
        }
      } else {
        // No stored filters, default to "All" (empty array)
        this.selectedEventTypeFilters = [];
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
    },
    // WHAT: Watch for changes to selectedEventTypeFilters and update calendar view
    // WHY: Calendar should update immediately when filters change
    // HOW: Call syncCalendarEvents to re-filter and re-render calendar events
    selectedEventTypeFilters: {
      handler() {
        // WHAT: Re-sync calendar events when filters change
        // WHY: Calendar view needs to reflect current filter selection
        // HOW: syncCalendarEvents will apply filters before mapping to FullCalendar format
        this.syncCalendarEvents();
      },
      deep: true // Watch for changes inside the array (when items are added/removed)
    },
    // WHAT: Watch for changes to selectedEventTypeFilters array and persist to localStorage + update calendar
    // WHY: Users expect filter selection to persist when changing months or reloading page, and calendar should update
    // HOW: Save filters array to localStorage AND re-sync calendar events when filters change
    selectedEventTypeFilters: {
      handler(newValue: string[]) {
        // WHAT: Save filters array to localStorage whenever it changes
        // WHY: Persist user's filter preference across month navigation
        // HOW: Store filters array as JSON or remove from localStorage if "All" is selected (empty array)
        if (newValue.length > 0) {
          localStorage.setItem('calendarEventTypeFilters', JSON.stringify(newValue));
          console.log('[HomeCalendarWidget] Saved filters to localStorage:', newValue);
        } else {
          localStorage.removeItem('calendarEventTypeFilters');
          console.log('[HomeCalendarWidget] Cleared filters from localStorage (All selected)');
        }
        
        // WHAT: Re-sync calendar events when filters change
        // WHY: Calendar view needs to reflect current filter selection immediately
        // HOW: syncCalendarEvents will apply filters before mapping to FullCalendar format
        this.syncCalendarEvents();
      },
      deep: true, // Watch for changes inside the array (when items are added/removed)
      immediate: false // Don't run on initial mount (we load from localStorage in mounted)
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

.calendar-widget-inline .fc-view-harness {
  height: auto !important;
}

.calendar-widget-inline .fc-scroller-harness {
  height: auto !important;
}

.calendar-widget-inline .fc-scroller {
  height: auto !important;
  overflow: hidden !important;
}

.calendar-widget-inline .fc .fc-daygrid-day-frame {
  min-height: 190px;
}

/* Event List Styles */
/* WHAT: Event list container that takes up full available height with scrolling */
/* WHY: Events should fill the entire card body and scroll when content overflows */
/* HOW: Use flex-grow-1 to take available space, min-height 0 allows proper flexbox scrolling */
/* NOTE: Background color inherited from parent card - no explicit color needed */
.event-list {
  min-height: 0; /* WHAT: Required for flexbox scrolling to work properly */
  overflow-y: auto; /* WHAT: Enable vertical scrolling when content exceeds container */
  flex: 1 1 auto; /* WHAT: Grow to fill available space in flex container */
}

/* WHAT: Individual event item styling */
/* WHY: Events need to match the background color of the event list */
/* HOW: Use same color as event-list-column and calendar-widget-inline */
.event-item {
  background-color: #FDFBF7; /* WHAT: Same warm white as the container */
  border: 1px solid var(--bs-border-color);
  transition: all 0.2s ease-in-out;
}

/* WHAT: Hover state for event items - subtle highlight effect */
/* WHY: Provides visual feedback that items are clickable */
/* HOW: Lighten background, add shadow, and accent border color */
.event-item:hover {
  background-color: #f0ebe3; /* WHAT: Slightly darker warm tone on hover */
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
