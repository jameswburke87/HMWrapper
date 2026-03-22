# HallMaster API Overview

This section documents the internal REST API used by [HallMaster](https://www.hallmaster.co.uk/) (v2). This API is **not officially documented** — everything here was reverse-engineered by observing browser traffic.

## Base URL

```
https://v2.hallmaster.co.uk
```

## Tech Stack

HallMaster v2 is built on:

- **ASP.NET MVC** — Server-side rendering with Razor views
- **jQuery + KnockoutJS** — Client-side interactivity
- **Kendo UI** — Grids, schedulers, and form widgets
- **FullCalendar** — Calendar/scheduler view

## API Pattern

The API uses two distinct patterns:

### JSON Endpoints (`/api/...`)

Read operations and some write operations use JSON endpoints:

```
GET /api/bookings/GetForHallgrid?id={hall_id}&statusType=All
```

These return JSON, typically either a bare array or an object with a `Data` key.

### MVC Form Posts (`/Admin/...`)

Create and edit operations use traditional HTML form submissions:

1. GET the form page to extract current field values
2. Extract the `__RequestVerificationToken` from a hidden input
3. POST the form with all fields and the token

## Important Gotchas

1. **No official API** — Endpoints may change without notice
2. **Anti-forgery tokens** — All POST requests require a `__RequestVerificationToken`
3. **Cookie-based auth** — No API keys or Bearer tokens; sessions are ASP.NET cookies
4. **Room identification** — Some views identify rooms by CSS color, not by ID
5. **Rate limiting** — The server enforces rate limits; keep concurrent requests to 2-3
6. **Session expiry** — Sessions expire after inactivity; use keepalive checks
