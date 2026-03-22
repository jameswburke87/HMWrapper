# HMWrapper

Python client for the [HallMaster](https://www.hallmaster.co.uk/) venue booking API.

HallMaster is a widely-used platform for managing community hall and venue bookings. While it provides no official public API, HMWrapper offers a clean, typed Python interface built on reverse-engineered internal endpoints.

## Features

- Full authenticated access (cookie-based ASP.NET session + anti-forgery tokens)
- Session persistence to avoid repeated logins
- Bookings — list, create, edit, delete, check availability, calculate costs
- Customers — list, details, notes, block users
- Rooms — list, lookup, descriptions
- Scheduler — calendar events in FullCalendar format
- Admin — activity types, pricing, charge matrices, audit logs, reports
- Typed dataclass models for all responses
- CLI tool for common operations
- Automatic retry with exponential backoff for rate limits

## Installation

```bash
pip install hmwrapper
```

With CLI support:

```bash
pip install hmwrapper[cli]
```

## Quick Start

### Python

```python
from hmwrapper import HallmasterClient, BookingsAPI

# Credentials from args or HM_EMAIL/HM_PASSWORD/HM_HALL_ID env vars
client = HallmasterClient()  # reads HM_EMAIL, HM_PASSWORD, HM_HALL_ID from env

bookings = BookingsAPI(client)
for b in bookings.list_bookings(status="Confirmed"):
    print(f"{b.name}: {b.start} -> {b.end}")

client.close()
```

Or with environment variables and context manager:

```python
from hmwrapper import HallmasterClient, BookingsAPI

with HallmasterClient() as client:  # reads HM_EMAIL, HM_PASSWORD, HM_HALL_ID
    for b in BookingsAPI(client).list_bookings(status="Confirmed"):
        print(b)
```

### CLI

```bash
export HM_EMAIL="admin@example.com"
export HM_PASSWORD="your-password"
export HM_HALL_ID="your-hall-id"

hmwrapper login
hmwrapper bookings list --status Confirmed
hmwrapper bookings list --format json
hmwrapper rooms list
hmwrapper calendar export --month 2026-03
```

## API Modules

| Module | Class | Description |
|--------|-------|-------------|
| `bookings` | `BookingsAPI` | List, create, edit, delete bookings; check availability; calculate costs |
| `customers` | `CustomersAPI` | List customers, view details/notes, block users |
| `rooms` | `RoomsAPI` | List rooms, build lookup dicts |
| `scheduler` | `SchedulerAPI` | Fetch calendar events, session keepalive |
| `admin` | `AdminAPI` | Activity types, pricing, audit logs, reports |

## Documentation

Full documentation including reverse-engineered API reference available at the [docs site](https://jameswburke87.github.io/HMWrapper/).

## License

MIT
