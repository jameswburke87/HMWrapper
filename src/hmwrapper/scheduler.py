"""Scheduler (calendar) API — fetch calendar events."""

from __future__ import annotations

from typing import Any

from .client import HallmasterClient
from .models import SchedulerEvent


class SchedulerAPI:
    """Interface to Hallmaster scheduler/calendar endpoints."""

    def __init__(self, client: HallmasterClient):
        self.client = client
        self.hall_id = client.hall_id

    def get_bookings(
        self,
        start: str,
        end: str,
        room_id: int = 0,
        group_rooms: bool = False,
        cust_view: bool = False,
    ) -> list[SchedulerEvent]:
        """Fetch calendar events in FullCalendar format.

        Args:
            start: Start date ISO8601 (e.g. "2026-03-01T00:00:00Z").
            end: End date ISO8601.
            room_id: Room ID filter (0 = all rooms).
            group_rooms: Whether to group by room.
            cust_view: Customer view mode.
        """
        data = self.client.get(
            "/api/Scheduler/GetBookings",
            params={
                "roomId": room_id,
                "custView": str(cust_view).lower(),
                "HallId": self.hall_id,
                "groupRooms": str(group_rooms).lower(),
                "start": start,
                "end": end,
            },
        )
        rows = data if isinstance(data, list) else data.get("Data", data.get("data", []))
        return [SchedulerEvent.from_api(row) for row in rows]

    def has_just_logged_in(self) -> Any:
        """Session keepalive check."""
        return self.client.get("/api/Scheduler/HasJustLoggedIn")

    def view_booking(self, booking_id: int) -> str:
        """Quick booking view from the scheduler."""
        return self.client.get_html(f"/Scheduler/ViewBooking/{booking_id}")
