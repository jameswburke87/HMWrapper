# Scheduler Endpoints

## Get Bookings (Calendar)

```http
GET /api/Scheduler/GetBookings
```

Returns events in [FullCalendar](https://fullcalendar.io/) format.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `HallId` | int | Yes | Hall ID |
| `start` | string | Yes | Start date ISO8601 (e.g. `2026-03-01T00:00:00Z`) |
| `end` | string | Yes | End date ISO8601 |
| `roomId` | int | No | Room filter (0 = all rooms) |
| `groupRooms` | string | No | `"true"` or `"false"` |
| `custView` | string | No | `"true"` for customer view mode |

**Response:**

```json
[
  {
    "id": 12345,
    "title": "Community Meeting",
    "start": "2026-03-22T10:00:00",
    "end": "2026-03-22T12:00:00",
    "color": "#ff6600",
    "allDay": false,
    "RoomsUsed": "Main Hall"
  }
]
```

## Session Keepalive

```http
GET /api/Scheduler/HasJustLoggedIn
```

Returns **200** if the session is still valid. Useful as a keepalive/health check.

## Quick Booking View

```http
GET /Scheduler/ViewBooking/{booking_id}
```

Returns HTML for a quick booking popup in the scheduler view.
