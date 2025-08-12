const categories = [
    {
        name: 'Danger',
        value: 'bg-danger'
    },
    {
        name: 'Success',
        value: 'bg-success'
    },
    {
        name: 'Primary',
        value: 'bg-primary'
    },
    {
        name: 'Info',
        value: 'bg-info'
    },
    {
        name: 'Dark',
        value: 'bg-dark'
    },
    {
        name: 'Warning',
        value: 'bg-warning'
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

const calendarEvents: CalendarEvent[] = [
    {
        id:1,
        title: "Meeting with Mr. Shreyu",
        start: new Date(today + 158000000),
        end: new Date(today + 338000000),
        className: "bg-warning",
    },
    {
        id:2,
        title: "Interview - Backend Engineer",
        start: today,
        end: today,
        className: "bg-success",
    },
    {
        id:3,
        title: "Phone Screen - Frontend Engineer",
        start: new Date(today + 168000000),
        className: "bg-info",
    },
    {
        id:4,
        title: "Buy Design Assets",
        start: new Date(today + 338000000),
        end: new Date(today + 338000000 * 1.2),
        className: "bg-primary",
    },
];

export {categories, calendarEvents};
