"""Example: Check availability and cost before creating a booking.

NOTE: This example does NOT submit the booking — it only checks availability
and calculates cost. Uncomment the final section to actually create.
"""

import os

from hmwrapper import HallmasterClient, BookingsAPI, RoomsAPI, AdminAPI, CustomersAPI

client = HallmasterClient(
    email=os.environ.get("HM_EMAIL"),
    password=os.environ.get("HM_PASSWORD"),
    hall_id=int(os.environ["HM_HALL_ID"]),
    session_file=".hm_session",
)

rooms_api = RoomsAPI(client)
admin_api = AdminAPI(client)
bookings_api = BookingsAPI(client)
customers_api = CustomersAPI(client)

# 1. List available rooms and pick one
rooms = rooms_api.list_rooms()
print("Available rooms:")
for r in rooms:
    print(f"  {r.id}: {r.name}")

# 2. List activity types and price rates
activity_types = admin_api.get_activity_types()
print("\nActivity types:")
for at in activity_types:
    print(f"  {at.id}: {at.name}")

price_rates = admin_api.get_price_rates()
print("\nPrice rates:")
for pr in price_rates:
    print(f"  {pr.id}: {pr.name}")

# 3. Check availability
room_id = rooms[0].id if rooms else 0
start = "2026-04-01T10:00:00"
end = "2026-04-01T12:00:00"

print(f"\nChecking availability for room {room_id}: {start} -> {end}")
avail = bookings_api.check_availability([room_id], start, end)
print(f"  Result: {avail}")

# 4. Get cost
if price_rates:
    cost = bookings_api.get_cost([room_id], start, end, price_rates[0].id)
    print(f"  Cost: {cost}")

# 5. Create booking (UNCOMMENT TO ACTUALLY CREATE)
# customers = customers_api.list_customers()
# booking_data = {
#     "BookingName": "Test Booking",
#     "StartDateTime": start,
#     "EndDateTime": end,
#     "CustomerId": customers[0].id,
#     "Rooms": [room_id],
#     "ActivityTypeId": activity_types[0].id,
#     "PriceRateId": price_rates[0].id,
#     "StatusId": "Requested",
#     "IsRecurring": False,
# }
# result = bookings_api.create_booking(booking_data)
# print(f"  Created: {result.status_code}")

client.close()
