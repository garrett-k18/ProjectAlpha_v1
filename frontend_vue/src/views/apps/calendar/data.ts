// Calendar event type categories with color coding
// What: Defines visual legend for calendar event types
// Why: Users need to understand what each color represents
// Where: Displayed in calendar sidebar legend
// How: Maps event types to Bootstrap color classes
const categories = [
    {
        name: 'Realized Liquidation',
        value: 'realized_liquidation'  // Semantic event type - frontend maps to colors
    },
    {
        name: 'Projected Liquidation',
        value: 'projected_liquidation'  // Semantic event type - frontend maps to colors
    },
    {
        name: 'Trade',
        value: 'trade'  // Semantic event type - frontend maps to colors
    },
    {
        name: 'Follow-up Task',
        value: 'follow_up'  // Semantic event type - frontend maps to colors
    },
    {
        name: 'Bid Date',
        value: 'bid_date'  // Semantic event type - frontend maps to colors
    },
    {
        name: 'Settlement Date',
        value: 'settlement_date'  // Semantic event type - frontend maps to colors
    },
    {
        name: 'Milestone',
        value: 'milestone'  // Semantic event type - frontend maps to colors
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
