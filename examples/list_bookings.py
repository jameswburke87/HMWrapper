"""Example: List confirmed bookings."""

import os

from hmwrapper import HallmasterClient, BookingsAPI, RoomsAPI

# Credentials from environment or explicit values
client = HallmasterClient(
    email=os.environ.get("HM_EMAIL"),
    password=os.environ.get("HM_PASSWORD"),
    hall_id=int(os.environ["HM_HALL_ID"]),
    session_file=".hm_session",
)

# Build room lookup
rooms_api = RoomsAPI(client)
room_lookup = rooms_api.get_room_lookup()
print(f"Rooms: {room_lookup}\n")

# List confirmed bookings from last month
bookings_api = BookingsAPI(client)
bookings = bookings_api.list_bookings(status="Confirmed", timerange=2)

print(f"Found {len(bookings)} confirmed bookings:\n")
for b in bookings:
    print(f"  [{b.id}] {b.name}")
    print(f"    {b.start} -> {b.end}")
    print(f"    Customer: {b.customer_name}")
    print(f"    Rooms: {b.rooms_used}")
    print()

client.close()
