# Examples

## List Bookings

```python
from hmwrapper import HallmasterClient, BookingsAPI, RoomsAPI

client = HallmasterClient(session_file=".hm_session")

# Build room lookup for reference
rooms_api = RoomsAPI(client)
room_lookup = rooms_api.get_room_lookup()

# List confirmed bookings from last month
bookings_api = BookingsAPI(client)
bookings = bookings_api.list_bookings(status="Confirmed", timerange=2)

for b in bookings:
    print(f"[{b.id}] {b.name}")
    print(f"  {b.start} -> {b.end}")
    print(f"  Customer: {b.customer_name}")
    print(f"  Rooms: {b.rooms_used}")
    print()

client.close()
```

## Check Availability and Cost

```python
from hmwrapper import HallmasterClient, BookingsAPI, RoomsAPI, AdminAPI

client = HallmasterClient()

rooms_api = RoomsAPI(client)
admin_api = AdminAPI(client)
bookings_api = BookingsAPI(client)

# Get rooms and price rates
rooms = rooms_api.list_rooms()
price_rates = admin_api.get_price_rates()

# Check availability
room_id = rooms[0].id
start = "2026-04-01T10:00:00"
end = "2026-04-01T12:00:00"

avail = bookings_api.check_availability([room_id], start, end)
print(f"Available: {avail}")

# Calculate cost
if price_rates:
    cost = bookings_api.get_cost([room_id], start, end, price_rates[0].id)
    print(f"Cost: {cost}")

client.close()
```

## Export Calendar Events

```python
import json
from datetime import datetime
from hmwrapper import HallmasterClient, SchedulerAPI

client = HallmasterClient()
scheduler = SchedulerAPI(client)

# Fetch current month
now = datetime.now()
start = now.replace(day=1).strftime("%Y-%m-%dT00:00:00Z")
if now.month == 12:
    end = now.replace(year=now.year + 1, month=1, day=1).strftime("%Y-%m-%dT00:00:00Z")
else:
    end = now.replace(month=now.month + 1, day=1).strftime("%Y-%m-%dT00:00:00Z")

events = scheduler.get_bookings(start=start, end=end)

# Export as JSON
with open("calendar.json", "w") as f:
    json.dump([e.to_dict() for e in events], f, indent=2)

print(f"Exported {len(events)} events")
client.close()
```

## Audit Log

```python
from hmwrapper import HallmasterClient, AdminAPI

client = HallmasterClient()
admin = AdminAPI(client)

# Get today's audit log
log = admin.get_audit_log(timerange=0)
for entry in log if isinstance(log, list) else log.get("Data", []):
    print(entry)

client.close()
```
