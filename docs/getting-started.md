# Getting Started

## Installation

```bash
pip install hmwrapper
```

For CLI support:
```bash
pip install hmwrapper[cli]
```

For development:
```bash
pip install hmwrapper[dev,cli]
```

## Authentication

HMWrapper requires HallMaster admin credentials (email + password) and your venue's Hall ID.

### Option 1: Environment Variables

```bash
export HM_EMAIL="admin@example.com"
export HM_PASSWORD="your-password"
export HM_HALL_ID="{hall_id}"
```

Then create a client with no arguments:

```python
from hmwrapper import HallmasterClient

client = HallmasterClient()
```

### Option 2: Explicit Credentials

```python
client = HallmasterClient(
    email="admin@example.com",
    password="your-password",
    hall_id={hall_id},
)
```

### Session Persistence

To avoid logging in on every script run, use a session file:

```python
client = HallmasterClient(session_file=".hm_session")
```

The session cookies are saved as JSON. On next run, the client will try the saved session first and only re-authenticate if it has expired.

### Context Manager

```python
with HallmasterClient() as client:
    # ... use the client
    pass
# session is automatically closed
```

## Finding Your Hall ID

Your Hall ID is visible in the HallMaster URL when logged in:

```
https://v2.hallmaster.co.uk/Admin/Dashboard/Index/{hall_id}
                                                  ^^^^
```

## Basic Usage

```python
from hmwrapper import HallmasterClient, BookingsAPI, RoomsAPI, CustomersAPI

client = HallmasterClient()

# List rooms
rooms = RoomsAPI(client)
for r in rooms.list_rooms():
    print(f"{r.id}: {r.name}")

# List confirmed bookings
bookings = BookingsAPI(client)
for b in bookings.list_bookings(status="Confirmed", timerange=2):
    print(f"{b.name} ({b.start} -> {b.end})")

# List customers
customers = CustomersAPI(client)
for c in customers.list_customers():
    print(f"{c.name} - {c.email}")

client.close()
```

## CLI Usage

```bash
# Test credentials
hmwrapper login

# List bookings
hmwrapper bookings list
hmwrapper bookings list --status Confirmed --format json

# List rooms
hmwrapper rooms list

# Export calendar events
hmwrapper calendar export --month 2026-03
hmwrapper calendar export --month 2026-03 -o events.json
```
