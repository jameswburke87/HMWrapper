"""Bookings API — list, create, edit, delete, availability, and cost."""

from __future__ import annotations

from typing import Any, Optional

from .client import HallmasterClient
from .models import Booking


class BookingsAPI:
    """Interface to Hallmaster booking endpoints."""

    def __init__(self, client: HallmasterClient):
        self.client = client
        self.hall_id = client.hall_id

    def list_bookings(
        self,
        status: str = "All",
        timerange: int = 5,
        year: Optional[int] = None,
        start_date_from: Optional[str] = None,
        start_date_to: Optional[str] = None,
    ) -> list[Booking]:
        """List bookings from the hall grid.

        Args:
            status: Filter — All, Requested, Confirmed, Cancelled,
                    NotCancelled, HasPending.
            timerange: 0=Today, 1=Last7Days, 2=LastMonth, 3=Last3Months,
                       4=LastYear, 5=All.
            year: Optional year filter.
            start_date_from: Optional start date lower bound (YYYY/MM/DDT00:00:00).
            start_date_to: Optional start date upper bound.
        """
        params: dict[str, Any] = {
            "id": self.hall_id,
            "statusType": status,
            "timerange": timerange,
        }
        if year is not None:
            params["year"] = year
        if start_date_from:
            params["startDateFrom"] = start_date_from
        if start_date_to:
            params["startDateTo"] = start_date_to

        data = self.client.get("/api/bookings/GetForHallgrid", params=params)
        rows = data if isinstance(data, list) else data.get("Data", data.get("data", []))
        return [Booking.from_api(row) for row in rows]

    def get_booking_counts(self, timerange: int = 0) -> dict:
        """Get booking count summary."""
        return self.client.get(
            "/api/Bookings/GetBookingCountsForHall",
            params={"id": self.hall_id, "timerange": timerange},
        )

    def get_time_range_counts(self) -> dict:
        """Get booking counts per time range."""
        return self.client.get(
            "/api/Bookings/GetBookingTimeRangeCountsForHall",
            params={"id": self.hall_id},
        )

    def get_requested_count(self) -> int:
        """Get count of bookings pending approval."""
        return self.client.get(
            "/api/Bookings/GetRequestedBookingsCount",
            params={"hallid": self.hall_id},
        )

    def has_pending_changes(self) -> bool:
        """Check if there are pending booking change requests."""
        return self.client.get(
            "/api/Bookings/HasPendingBookingChanges",
            params={"hallid": self.hall_id},
        )

    def get_recurring_children(self, booking_id: int) -> list[Booking]:
        """Get child bookings of a recurring series."""
        data = self.client.get(
            "/api/bookings/getforparentgrid",
            params={"id": booking_id},
        )
        rows = data if isinstance(data, list) else data.get("Data", data.get("data", []))
        return [Booking.from_api(row) for row in rows]

    def check_availability(
        self,
        room_ids: list[int],
        start: str,
        end: str,
        **extra: Any,
    ) -> Any:
        """Check room availability for a time slot.

        Args:
            room_ids: List of room IDs to check.
            start: Start datetime string.
            end: End datetime string.
        """
        payload = {
            "Rooms": room_ids,
            "StartDateTime": start,
            "EndDateTime": end,
            "HallId": self.hall_id,
            **extra,
        }
        r = self.client.post("/api/Bookings/CheckAvailability", json=payload)
        try:
            return r.json()
        except ValueError:
            return r.text

    def get_cost(
        self,
        room_ids: list[int],
        start: str,
        end: str,
        price_rate_id: int,
        **extra: Any,
    ) -> Any:
        """Calculate the hire cost for a booking.

        Args:
            room_ids: List of room IDs.
            start: Start datetime.
            end: End datetime.
            price_rate_id: Price rate ID to apply.
        """
        payload = {
            "Rooms": room_ids,
            "StartDateTime": start,
            "EndDateTime": end,
            "PriceRateId": price_rate_id,
            "HallId": self.hall_id,
            **extra,
        }
        r = self.client.post("/api/Bookings/GetCostOfBooking", json=payload)
        try:
            return r.json()
        except ValueError:
            return r.text

    def get_create_form(self) -> dict[str, str]:
        """Fetch the booking creation form and return hidden field values."""
        html = self.client.get_html("/Admin/Bookings/Create")
        return self._parse_form_fields(html)

    def create_booking(self, data: dict) -> Any:
        """Create a new booking via MVC form POST.

        Args:
            data: Form field dict — must include BookingName, StartDateTime,
                  EndDateTime, CustomerId, Rooms, ActivityTypeId,
                  PriceRateId, StatusId, etc.
        """
        r = self.client.post_form("/Admin/Bookings/Create", data=data)
        return r

    def get_edit_form(self, booking_id: int) -> dict[str, str]:
        """Fetch the booking edit form and return current field values."""
        html = self.client.get_html(f"/Admin/Bookings/Edit/{booking_id}")
        return self._parse_form_fields(html)

    def edit_booking(self, booking_id: int, data: dict) -> Any:
        """Edit an existing booking via MVC form POST."""
        r = self.client.post_form(f"/Admin/Bookings/Edit/{booking_id}", data=data)
        return r

    def view_booking(self, booking_id: int) -> str:
        """Get the read-only booking view HTML."""
        return self.client.get_html(f"/Admin/Bookings/View/{booking_id}")

    def delete_booking(self, booking_id: int) -> str:
        """Delete a booking. Returns the response HTML."""
        return self.client.get_html(f"/Admin/Bookings/Delete/{booking_id}")

    def request_changes(self, booking_id: int) -> str:
        """Request changes on a booking."""
        return self.client.get_html(f"/Admin/Bookings/RequestChanges/{booking_id}")

    def confirm_changes(self, booking_id: int) -> str:
        """Confirm pending changes on a booking."""
        return self.client.get_html(f"/Admin/Bookings/ConfirmChanges/{booking_id}")

    def preview_email(self, data: dict) -> Any:
        """Preview the notification email content."""
        r = self.client.post("/api/Bookings/PreviewEmailContent", json=data)
        try:
            return r.json()
        except ValueError:
            return r.text

    @staticmethod
    def _parse_form_fields(html: str) -> dict[str, str]:
        """Extract all input/select/textarea values from an HTML form."""
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")
        fields: dict[str, str] = {}
        for inp in soup.find_all("input"):
            name = inp.get("name")
            if name:
                fields[name] = inp.get("value", "")
        for sel in soup.find_all("select"):
            name = sel.get("name")
            if name:
                opt = sel.find("option", selected=True)
                fields[name] = opt.get("value", "") if opt else ""
        for ta in soup.find_all("textarea"):
            name = ta.get("name")
            if name:
                fields[name] = ta.get_text()
        return fields
