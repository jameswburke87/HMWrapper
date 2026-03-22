"""Example: Export scheduler events as JSON."""

import json
import os
from datetime import datetime

from hmwrapper import HallmasterClient, SchedulerAPI, RoomsAPI

client = HallmasterClient(
    email=os.environ.get("HM_EMAIL"),
    password=os.environ.get("HM_PASSWORD"),
    hall_id=int(os.environ["HM_HALL_ID"]),
    session_file=".hm_session",
)

# Fetch current month's events
scheduler = SchedulerAPI(client)
now = datetime.now()
start = now.replace(day=1).strftime("%Y-%m-%dT00:00:00Z")
if now.month == 12:
    end = now.replace(year=now.year + 1, month=1, day=1).strftime("%Y-%m-%dT00:00:00Z")
else:
    end = now.replace(month=now.month + 1, day=1).strftime("%Y-%m-%dT00:00:00Z")

print(f"Fetching events: {start} -> {end}\n")

events = scheduler.get_bookings(start=start, end=end)
print(f"Found {len(events)} events:\n")

for e in events:
    print(f"  {e.title}")
    print(f"    {e.start} -> {e.end}")
    if e.rooms_used:
        print(f"    Rooms: {e.rooms_used}")
    print()

# Export to JSON
output = [e.to_dict() for e in events]

with open("calendar_export.json", "w") as f:
    json.dump(output, f, indent=2)

print(f"Exported {len(output)} events to calendar_export.json")

client.close()
