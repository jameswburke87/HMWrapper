# Bookings Endpoints

## List Bookings

```http
GET /api/bookings/GetForHallgrid
```

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `id` | int | Yes | Hall ID |
| `statusType` | string | No | `All`, `Requested`, `Confirmed`, `Cancelled`, `NotCancelled`, `HasPending` |
| `timerange` | int | No | `0`=Today, `1`=Last7Days, `2`=LastMonth, `3`=Last3Months, `4`=LastYear, `5`=All |
| `year` | int | No | Filter by year |
| `startDateFrom` | string | No | Start date lower bound (`YYYY/MM/DDT00:00:00`) |
| `startDateTo` | string | No | Start date upper bound |

**Response:** Array of booking objects or `{"Data": [...]}`.

```json
[
  {
    "BookingId": 12345,
    "BookingName": "Community Meeting",
    "StartDateTime": "2026-03-22T10:00:00",
    "EndDateTime": "2026-03-22T12:00:00",
    "Status": "Confirmed",
    "CustomerName": "John Doe",
    "CustomerId": "guid-string",
    "RoomsUsed": "Main Hall",
    "ActivityType": "Meeting",
    "IsRecurring": false
  }
]
```

## Booking Counts

```http
GET /api/Bookings/GetBookingCountsForHall?id={hall_id}&timerange={timerange}
GET /api/Bookings/GetBookingTimeRangeCountsForHall?id={hall_id}
GET /api/Bookings/GetRequestedBookingsCount?hallid={hall_id}
GET /api/Bookings/HasPendingBookingChanges?hallid={hall_id}
```

## Recurring Booking Children

```http
GET /api/bookings/getforparentgrid?id={booking_id}
```

Returns child bookings of a recurring series in the same format as the grid endpoint.

## Check Availability

```http
POST /api/Bookings/CheckAvailability
Content-Type: application/json
RequestVerificationToken: {token}
```

**Body:**

```json
{
  "Rooms": [1, 2],
  "StartDateTime": "2026-04-01T10:00:00",
  "EndDateTime": "2026-04-01T12:00:00",
  "HallId": {hall_id}
}
```

## Calculate Cost

```http
POST /api/Bookings/GetCostOfBooking
Content-Type: application/json
RequestVerificationToken: {token}
```

**Body:**

```json
{
  "Rooms": [1],
  "StartDateTime": "2026-04-01T10:00:00",
  "EndDateTime": "2026-04-01T12:00:00",
  "PriceRateId": 3,
  "HallId": {hall_id}
}
```

## Create Booking (MVC Form)

This uses HTML form submission, not a JSON API.

### Step 1: Get the Form

```http
GET /Admin/Bookings/Create
```

Parse the HTML to extract field names and the anti-forgery token.

### Step 2: Submit the Form

```http
POST /Admin/Bookings/Create
Content-Type: application/x-www-form-urlencoded
```

**Required fields:** `Name`, `StartDate`, `EndDate`, `CustomerId`, `ActivityTypeId`, `PriceRateId`, `BookingStatusId`, `__RequestVerificationToken`

**Room selection:** Rooms use ASP.NET MVC indexed model binding. For each room available at the venue, include `BookingRoom[i].RoomId` with the room ID. For the room(s) being booked, also include `BookingRoom[i].Selected=true`.

**Important:** Bracket characters in field names (`[`, `]`) must be percent-encoded as `%5B`/`%5D` in the POST body, or the server's WAF will reject the request with a connection reset. The `sec-fetch-*` browser headers should also be included.

## Edit Booking (MVC Form)

```http
GET  /Admin/Bookings/Edit/{booking_id}     # Get current values
POST /Admin/Bookings/Edit/{booking_id}     # Submit changes
```

Same form-based flow as creation.

## View Booking

```http
GET /Admin/Bookings/View/{booking_id}
```

Returns HTML of the read-only booking view.

## Delete Booking

```http
GET /Admin/Bookings/Delete/{booking_id}
```

## Request/Confirm Changes

```http
GET /Admin/Bookings/RequestChanges/{booking_id}
GET /Admin/Bookings/ConfirmChanges/{booking_id}
```

## Preview Email

```http
POST /api/Bookings/PreviewEmailContent
Content-Type: application/json
RequestVerificationToken: {token}
```
