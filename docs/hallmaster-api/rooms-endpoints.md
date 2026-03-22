# Rooms Endpoints

## List Rooms (Booking)

```http
GET /api/Rooms/GetForHallForBooking?hallid={hall_id}
```

Returns rooms available for booking.

**Response:**

```json
[
  {
    "ID": 1,
    "Name": "Main Hall",
    "HallId": {hall_id},
    "rowNumber": 0,
    "Description": "Large community hall"
  }
]
```

Note: The `ID` field may appear as `Id` in some responses.

## List Rooms (Grid)

```http
GET /api/rooms/GetForHallGrid?id={hall_id}
```

Admin grid view of rooms. Same response format.

## Room Descriptions

```http
GET /api/rooms/getroomdescriptions
```

## Room Identification by Color

In the scheduler view, rooms are identified by CSS color rather than by ID. To build a color-to-room mapping, parse the scheduler HTML:

```http
GET /Scheduler/View/{hall_id}
```

Look for elements matching `#RoomColorList .room-label` and extract the background color and text content.
