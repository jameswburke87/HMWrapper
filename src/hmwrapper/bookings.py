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

    def create_booking(
        self,
        name: str,
        start: str,
        end: str,
        room_ids: list[int],
        customer_id: str,
        activity_type_id: int,
        price_rate_id: int,
        status: str = "Requested",
        send_emails: bool = False,
        **extra: Any,
    ) -> Any:
        """Create a new booking.

        Fetches the create form for the anti-forgery token and room list,
        then submits with browser-compatible field encoding.

        Args:
            name: Booking name/title.
            start: Start datetime (ISO format, e.g. "2026-03-22T14:00:00").
            end: End datetime (ISO format).
            room_ids: List of room IDs to book.
            customer_id: Customer GUID.
            activity_type_id: Activity type ID.
            price_rate_id: Price rate ID.
            status: Booking status — "Requested" or "Confirmed".
            send_emails: Whether to send notification emails.
            **extra: Additional form fields (e.g. Description, AdminNotes).
        """
        from .rooms import RoomsAPI

        # Get form for token and session state
        form = self.get_create_form()

        # Get all rooms to build indexed room fields
        all_rooms = RoomsAPI(self.client).list_rooms()
        selected = set(room_ids)

        # Build room fields with ASP.NET MVC indexed binding
        room_fields = {}
        for i, room in enumerate(all_rooms):
            room_fields[f"BookingRoom[{i}].RoomId"] = str(room.id)
            if room.id in selected:
                room_fields[f"BookingRoom[{i}].Selected"] = "true"

        form.update(room_fields)
        form.update({
            "Name": name,
            "StartDate": start,
            "EndDate": end,
            "CustomerId": customer_id,
            "ActivityTypeId": str(activity_type_id),
            "PriceRateId": str(price_rate_id),
            "BookingStatusId": status,
            "SendEmails": str(send_emails).lower(),
            **extra,
        })

        # Submit using the token already in the form (don't fetch a new one)
        from urllib.parse import quote
        url = f"{self.client.BASE}/Admin/Bookings/Create"
        parts = []
        for key, val in form.items():
            encoded_key = quote(str(key), safe=".")
            parts.append(f"{encoded_key}={quote(str(val), safe='')}")
        body = "&".join(parts)

        r = self.client.session.post(
            url,
            data=body,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": url,
                "Origin": self.client.BASE,
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1",
            },
            allow_redirects=True,
        )
        return r

    def get_edit_form(self, booking_id: int) -> dict[str, str]:
        """Fetch the booking edit form and return current field values."""
        html = self.client.get_html(f"/Admin/Bookings/Edit/{booking_id}")
        return self._parse_form_fields(html)

    def edit_booking(self, booking_id: int, updates: dict) -> Any:
        """Edit an existing booking.

        Fetches the current form values, merges in updates, and submits
        with browser-compatible encoding to avoid WAF rejection.

        Args:
            booking_id: ID of the booking to edit.
            updates: Dict of fields to change (e.g. Name, StartDate, EndDate,
                     BookingStatusId). Unspecified fields keep their current values.
        """
        # Get current form values (includes token)
        form = self.get_edit_form(booking_id)
        form.update(updates)

        from urllib.parse import quote
        url = f"{self.client.BASE}/Admin/Bookings/Edit/{booking_id}"
        parts = []
        for key, val in form.items():
            encoded_key = quote(str(key), safe=".")
            parts.append(f"{encoded_key}={quote(str(val), safe='')}")
        body = "&".join(parts)

        r = self.client.session.post(
            url,
            data=body,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": url,
                "Origin": self.client.BASE,
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1",
            },
            allow_redirects=True,
        )
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
