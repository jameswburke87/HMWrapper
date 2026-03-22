# HMWrapper

A Python client for the [HallMaster](https://www.hallmaster.co.uk/) venue booking API.

HallMaster is a widely-used platform for managing community hall and venue bookings. While it provides no official public API, HMWrapper offers a clean, typed Python interface built on reverse-engineered internal endpoints.

## Features

- **Full authentication** — Cookie-based login with anti-forgery token management
- **Session persistence** — Save/restore sessions to avoid repeated logins
- **Bookings** — List, create, edit, delete, check availability, calculate costs
- **Customers** — List, search, view details, block users
- **Rooms** — List available rooms, build lookup dictionaries
- **Scheduler** — Fetch calendar events in FullCalendar format
- **Admin** — Activity types, pricing, charge matrices, audit logs, reports
- **Typed models** — Dataclass models for all API responses
- **CLI tool** — Command-line interface for common operations
- **Retry logic** — Automatic retry with backoff for rate limits and server errors

## Quick Start

```python
from hmwrapper import HallmasterClient, BookingsAPI

# Credentials from args or HM_EMAIL/HM_PASSWORD/HM_HALL_ID env vars
client = HallmasterClient()  # reads HM_EMAIL, HM_PASSWORD, HM_HALL_ID from env

bookings = BookingsAPI(client)
for b in bookings.list_bookings(status="Confirmed"):
    print(f"{b.name}: {b.start} -> {b.end}")

client.close()
```

## Installation

```bash
pip install hmwrapper
```

With CLI support:

```bash
pip install hmwrapper[cli]
```
