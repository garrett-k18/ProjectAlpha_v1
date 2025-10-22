# Calendar Integration - Feature Documentation

**Last Updated**: January 9, 2025  
**Status**: Backend Complete, Frontend Pending  
**Version**: 1.0

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Backend Implementation](#backend-implementation)
4. [API Endpoints](#api-endpoints)
5. [Frontend Integration](#frontend-integration)
6. [Data Sources](#data-sources)
7. [Setup Instructions](#setup-instructions)
8. [Usage Examples](#usage-examples)
9. [Future Enhancements](#future-enhancements)

---

## Overview

### What This Feature Does

The Calendar Integration provides a unified calendar view that aggregates important dates from across the application:

- **Model-Based Dates** (Read-Only): Automatically pulls dates from existing models like foreclosure sales, bid dates, settlement dates, etc.
- **Custom Events** (Editable): Allows users to create, edit, and delete custom calendar events like meetings, deadlines, and reminders
- **Visual Calendar Widget**: Displays events as colored bands on calendar dates with event titles
- **Filtering**: Filter events by date range, seller, trade, or category

### Key Benefits

- **Single Source of Truth**: All important dates in one place
- **No Duplication**: Reads directly from existing models (no data copying)
- **Flexible**: Easy to add new date fields from any model
- **User-Friendly**: Visual calendar with color-coded events
- **Extensible**: Custom events for user-specific needs

---

## Architecture

### System Design

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Calendar Widget                  │
│  (HomeCalendarWidget.vue - Bootstrap Datepicker + Vue)      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ HTTP GET/POST/PUT/DELETE
                     │
┌────────────────────▼────────────────────────────────────────┐
│                   Django REST API Layer                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ GET /api/core/calendar/events/                      │   │
│  │ - Aggregates all events (model + custom)            │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ CRUD /api/core/calendar/events/custom/              │   │
│  │ - Create/Update/Delete custom events                │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼────────┐    ┌──────────▼──────────┐
│  Model Dates   │    │  Custom Events      │
│  (Read-Only)   │    │  (CalendarEvent)    │
├────────────────┤    ├─────────────────────┤
│ • TradeLevelA  │    │ • User-created      │
│   - bid_date   │    │ • Meetings          │
│   - settlement │    │ • Deadlines         │
│ • ServicerData │    │ • Reminders         │
│   - fc_sale    │    │ • Follow-ups        │
│ • (More...)    │    └─────────────────────┘
└────────────────┘
```

### Data Flow

1. **Frontend Request**: User opens calendar widget
2. **API Call**: `GET /api/core/calendar/events/`
3. **Backend Aggregation**: 
   - Query TradeLevelAssumption for bid/settlement dates
   - Query ServicerData for FC sale dates
   - Query CalendarEvent for custom events
   - Combine all into unified response
4. **Frontend Display**: Render events as colored bands on calendar
5. **User Interaction**: Click date → Add/Edit custom event → POST/PUT to API

---

## Backend Implementation

### File Structure

```
projectalphav1/
├── core/
│   ├── models/
│   │   └── calendar_events.py          # CalendarEvent model
│   ├── serializers/
│   │   └── calendar_serializer.py      # Event serializers
│   ├── views/
│   │   └── calendar_api.py             # API views & logic
│   ├── admin_calendar.py               # Django admin config
│   └── urls.py                         # URL routing
```

### Models

#### CalendarEvent Model
**Location**: `projectalphav1/core/models/calendar_events.py`

```python
class CalendarEvent(models.Model):
    # Event details
    title = models.CharField(max_length=255)
    date = models.DateField()
    time = models.CharField(max_length=50, default="All Day")
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    
    # User tracking
    created_by = models.ForeignKey(User, ...)
    
    # Optional relationships
    seller = models.ForeignKey('acq_module.Seller', null=True, blank=True)
    trade = models.ForeignKey('acq_module.Trade', null=True, blank=True)
    asset_hub = models.ForeignKey('core.AssetIdHub', null=True, blank=True)
    
    # Flags
    is_reminder = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Key Features**:
- Optional links to Seller, Trade, or AssetHub for context
- Category field for color-coding (bg-primary, bg-success, etc.)
- Tracks who created the event
- Reminder flag for future notifications

### Serializers

**Location**: `projectalphav1/core/serializers/calendar_serializer.py`

Three serializers handle different use cases:

1. **CalendarEventReadSerializer**: Read-only for model dates
2. **CustomCalendarEventSerializer**: Full CRUD for CalendarEvent
3. **UnifiedCalendarEventSerializer**: Combined view for GET endpoint

### API Views

**Location**: `projectalphav1/core/views/calendar_api.py`

#### Main Functions

- `get_calendar_events()`: Aggregates all events from all sources
- `_get_seller_raw_data_events()`: Extracts dates from SellerRawData
- `_get_servicer_data_events()`: Extracts dates from ServicerData
- `_get_trade_events()`: Extracts Trade creation dates
- `_get_trade_assumption_events()`: Extracts bid/settlement dates
- `_get_custom_calendar_events()`: Fetches user-created events
- `CustomCalendarEventViewSet`: Full CRUD for custom events

---

## API Endpoints

### 1. Get All Calendar Events

**Endpoint**: `GET /api/core/calendar/events/`

**Description**: Returns all events (model dates + custom events)

**Query Parameters**:
- `start_date` (optional): Filter events on/after this date (YYYY-MM-DD)
- `end_date` (optional): Filter events on/before this date (YYYY-MM-DD)
- `seller_id` (optional): Filter by seller
- `trade_id` (optional): Filter by trade
- `categories` (optional): Comma-separated categories (e.g., "bg-danger,bg-warning")

**Example Request**:
```bash
GET /api/core/calendar/events/?start_date=2025-01-01&end_date=2025-12-31
```

**Example Response**:
```json
[
  {
    "id": "trade_assumption:45:bid_date",
    "title": "Bid Date: Trade ABC",
    "date": "2025-01-15",
    "time": "All Day",
    "description": "Bid submitted for Trade ABC",
    "category": "bg-primary",
    "source_model": "TradeLevelAssumption",
    "editable": false,
    "url": "/acq/trade/12/"
  },
  {
    "id": "custom:123",
    "title": "Meeting with Broker",
    "date": "2025-01-20",
    "time": "2:00 PM - 3:00 PM",
    "description": "Discuss new portfolio opportunities",
    "category": "bg-success",
    "source_model": "CalendarEvent",
    "editable": true,
    "url": ""
  }
]
```

### 2. Create Custom Event

**Endpoint**: `POST /api/core/calendar/events/custom/`

**Request Body**:
```json
{
  "title": "Follow-up Call",
  "date": "2025-01-25",
  "time": "10:00 AM - 10:30 AM",
  "description": "Follow up on bid submission",
  "category": "bg-warning",
  "trade": 12,
  "is_reminder": true
}
```

**Response**: Created event object with ID

### 3. Update Custom Event

**Endpoint**: `PUT /api/core/calendar/events/custom/{id}/`

**Request Body**: Same as create (all fields)

**Endpoint**: `PATCH /api/core/calendar/events/custom/{id}/`

**Request Body**: Partial update (only changed fields)

### 4. Delete Custom Event

**Endpoint**: `DELETE /api/core/calendar/events/custom/{id}/`

**Response**: 204 No Content

### 5. Get Single Custom Event

**Endpoint**: `GET /api/core/calendar/events/custom/{id}/`

**Response**: Event object

---

## Frontend Integration

### Current Implementation

**Location**: `frontend_vue/src/components/widgets/HomeCalendarWidget.vue`

**Features**:
- Bootstrap datepicker for calendar display
- Event bands displayed on calendar dates
- Color-coded by category
- Click date to add event
- Click event to edit/delete
- LocalStorage persistence (temporary)

### Event Display

Events appear as colored horizontal bands under the day number:

```
┌─────────────┐
│     15      │  ← Day number
├─────────────┤
│ Bid Date... │  ← Blue band (bg-primary)
│ Meeting...  │  ← Green band (bg-success)
│ +1 more     │  ← More indicator
└─────────────┘
```

### Color Scheme

- **bg-primary** (Blue #727cf5): Bid dates, origination, general events
- **bg-success** (Green #0acf97): Settlement, payments received, completions
- **bg-info** (Cyan #39afd1): Informational events
- **bg-warning** (Yellow #ffbc00): Payment due, pending actions
- **bg-danger** (Red #fa5c7c): Foreclosure sales, maturity dates, critical deadlines
- **bg-secondary** (Gray #6c757d): Historical/reference dates

### Pending Frontend Updates

**To integrate with backend API**:

1. Replace localStorage with API calls
2. Add loading states
3. Handle editable vs read-only events
4. Add error handling
5. Implement real-time updates

**Recommended Pinia Store Structure**:
```typescript
// stores/calendar.ts
export const useCalendarStore = defineStore('calendar', {
  state: () => ({
    events: [],
    loading: false,
    error: null
  }),
  actions: {
    async fetchEvents(startDate, endDate) { ... },
    async createEvent(eventData) { ... },
    async updateEvent(id, eventData) { ... },
    async deleteEvent(id) { ... }
  }
})
```

---

## Data Sources

### Currently Configured

#### 1. TradeLevelAssumption
**Model**: `acq_module.models.TradeLevelAssumption`

| Field | Event Title | Category | Description |
|-------|-------------|----------|-------------|
| `bid_date` | "Bid Date: {trade_name}" | bg-primary | Date bid was submitted |
| `settlement_date` | "Settlement: {trade_name}" | bg-success | Settlement/closing date |

#### 2. ServicerData
**Model**: `am_module.models.ServicerData`

| Field | Event Title | Category | Description |
|-------|-------------|----------|-------------|
| `actual_fc_sale_date` | "FC Sale: {address}" | bg-danger | Actual foreclosure sale date |

#### 3. Trade
**Model**: `acq_module.models.Trade`

| Field | Event Title | Category | Description |
|-------|-------------|----------|-------------|
| `created_at` | "Trade Created: {trade_name}" | bg-primary | Trade creation date |

#### 4. CalendarEvent (Custom)
**Model**: `core.models.CalendarEvent`

All user-created events with full CRUD capabilities.

### Ready to Add (Commented Out)

The following date fields are ready to be enabled in `calendar_api.py`:

**SellerRawData** (13 fields):
- `current_maturity_date`
- `original_maturity_date`
- `next_due_date`
- `last_paid_date`
- `fc_scheduled_sale_date`
- `fc_sale_date`
- `fc_first_legal_date`
- `fc_referred_date`
- `fc_judgement_date`
- `mod_date`
- `mod_maturity_date`
- `origination_date`
- `first_pay_date`

**ServicerData** (additional fields):
- `maturity_date`
- `next_due_date`
- `last_paid_date`
- `bk_filed_date`
- `bk_discharge_date`
- `bk_dismissed_date`
- `scheduled_fc_sale_date`
- And 10+ more bankruptcy/foreclosure dates

### How to Add More Date Fields

**Step 1**: Open `projectalphav1/core/views/calendar_api.py`

**Step 2**: Find the appropriate helper function (e.g., `_get_seller_raw_data_events`)

**Step 3**: Add to the `date_fields` list:

```python
date_fields = [
    ('field_name', 'Event Title: {address}', 'bg-category', 'Description'),
    # Example:
    ('fc_scheduled_sale_date', 'FC Sale: {address}', 'bg-danger', 'Foreclosure sale scheduled'),
]
```

**Step 4**: Restart Django server - changes take effect immediately!

---

## Setup Instructions

### Backend Setup

**1. Run Migrations**:
```bash
cd projectalphav1
python manage.py makemigrations core
python manage.py migrate
```

**2. Create Superuser** (if needed):
```bash
python manage.py createsuperuser
```

**3. Start Django Server**:
```bash
python manage.py runserver
```

**4. Verify API**:
```bash
# Test the endpoint
curl http://localhost:8000/api/core/calendar/events/

# Or visit in browser
http://localhost:8000/api/core/calendar/events/
```

### Frontend Setup

**1. Install Dependencies** (if not already):
```bash
cd frontend_vue
npm install
```

**2. Start Dev Server**:
```bash
npm run dev
```

**3. Access Calendar**:
- Navigate to `/home` route
- Calendar widget should be visible on homepage

### Django Admin Access

**1. Login to Admin**:
```
http://localhost:8000/admin/
```

**2. Manage Calendar Events**:
- Navigate to **Core → Calendar Events**
- View, create, edit, delete custom events
- Filter by date, category, seller, trade

---

## Usage Examples

### Example 1: View All Events for a Trade

```bash
GET /api/core/calendar/events/?trade_id=12
```

Returns all events (bid dates, settlement, FC sales, custom events) for Trade #12.

### Example 2: Create a Meeting Event

```bash
POST /api/core/calendar/events/custom/
Content-Type: application/json

{
  "title": "Quarterly Review Meeting",
  "date": "2025-03-15",
  "time": "9:00 AM - 11:00 AM",
  "description": "Review Q1 performance and Q2 strategy",
  "category": "bg-primary",
  "seller": 5,
  "is_reminder": true
}
```

### Example 3: Get Events for Date Range

```bash
GET /api/core/calendar/events/?start_date=2025-01-01&end_date=2025-01-31
```

Returns all January 2025 events.

### Example 4: Filter by Category

```bash
GET /api/core/calendar/events/?categories=bg-danger,bg-warning
```

Returns only critical/warning events (FC sales, maturity dates, payment due).

### Example 5: Update Event Time

```bash
PATCH /api/core/calendar/events/custom/123/
Content-Type: application/json

{
  "time": "10:00 AM - 12:00 PM"
}
```

---

## Future Enhancements

### Phase 2: Enhanced Features

- [ ] **Email Reminders**: Send email notifications for upcoming events
- [ ] **Recurring Events**: Support for weekly/monthly recurring events
- [ ] **Event Attachments**: Link documents/photos to calendar events
- [ ] **Team Calendar**: Share events across users/teams
- [ ] **Calendar Sync**: Export to Google Calendar, Outlook, iCal
- [ ] **Event Comments**: Discussion threads on events
- [ ] **Mobile App**: Native mobile calendar view

### Phase 3: Advanced Analytics

- [ ] **Timeline View**: Gantt-style timeline for trades
- [ ] **Deadline Tracking**: Dashboard of upcoming deadlines
- [ ] **Event Reports**: Analytics on event types, frequencies
- [ ] **Automated Events**: Auto-create events based on model changes
- [ ] **Smart Suggestions**: AI-suggested events based on patterns

### Phase 4: Integration

- [ ] **Workflow Integration**: Trigger workflows from calendar events
- [ ] **Notification System**: In-app notifications for events
- [ ] **Task Management**: Convert events to tasks
- [ ] **Reporting Integration**: Include calendar data in reports

---

## Technical Notes

### Performance Considerations

- **Caching**: Consider caching frequently accessed date ranges
- **Pagination**: For large date ranges, implement pagination
- **Indexing**: Database indexes on date fields for fast queries
- **Lazy Loading**: Load events only for visible month

### Security

- **Authentication**: Currently set to `AllowAny` - **TODO: Add auth**
- **Permissions**: Add user-based permissions for custom events
- **Data Validation**: All inputs validated by serializers
- **SQL Injection**: Protected by Django ORM

### Testing

**Recommended Test Cases**:
1. Create/Read/Update/Delete custom events
2. Filter events by date range
3. Filter events by seller/trade
4. Verify read-only model dates cannot be edited
5. Test date range edge cases
6. Verify category filtering
7. Test event count limits (3+ events per day)

---

## Troubleshooting

### Common Issues

**Issue**: "CalendarEvent model not found"
- **Solution**: Run `python manage.py migrate core`

**Issue**: "No events showing in calendar"
- **Solution**: Check that you have data in TradeLevelAssumption or create custom events

**Issue**: "Cannot edit model-based events"
- **Solution**: This is by design - model dates are read-only. Create custom events instead.

**Issue**: "API returns 500 error"
- **Solution**: Check Django logs for details. Ensure all related models exist.

---

## Support & Maintenance

### Code Owners

- **Backend**: Calendar API, Models, Serializers
- **Frontend**: Calendar Widget, Pinia Store
- **Database**: Migrations, Admin

### Documentation Updates

Update this document when:
- Adding new date fields to calendar
- Changing API endpoints
- Adding new features
- Modifying data sources

### Related Documentation

- [API Documentation](../APIDoc/)
- [Database Schema](../Database/)
- [Frontend Components](../../frontend_vue/README.md)

---

## Changelog

### Version 1.0 (January 9, 2025)
- ✅ Initial implementation
- ✅ CalendarEvent model created
- ✅ API endpoints implemented
- ✅ Frontend calendar widget with visual event bands
- ✅ TradeLevelAssumption dates integrated (bid_date, settlement_date)
- ✅ ServicerData dates integrated (actual_fc_sale_date)
- ✅ Custom event CRUD operations
- ✅ Django admin interface
- ⏸️ Frontend API integration pending

---

**End of Documentation**
