// Calendar event type categories with color coding
// What: Defines visual legend for calendar event types
// Why: Users need to understand what each color represents
// Where: Displayed in calendar sidebar legend
// How: Maps event types to Bootstrap color classes
const categories = [
    {
        name: 'Liquidation',
        value: 'bg-success'  // Green - actual foreclosure sales
    },
    {
        name: 'Projected Liquidation',
        value: 'bg-warning'  // Yellow - projected/scheduled FC sales
    },
    {
        name: 'Bid Date',
        value: 'bg-info'  // Cyan - bid submission deadlines
    },
    {
        name: 'Settlement Date',
        value: 'bg-dark'  // Dark/Purple - successful settlements
    },
    {
        name: 'Asset Milestone',
        value: 'bg-danger'  // Red - other important milestones
    },
];

const today = Date.now();

interface CalendarEvent {
    id: number,
    title: string,
    start: Date | number,
    end?: Date | number,
    allDay?: any,
    className?: string,
    classNames?: string[],
}

// Empty demo events - all events now come from backend API
// What: Placeholder for demo/local events (currently empty)
// Why: All calendar events are fetched from Django backend
// Where: Backend API at /api/core/calendar/events/
// How: Component fetches on mount and populates calendar
const calendarEvents: CalendarEvent[] = [];

export {categories, calendarEvents};
