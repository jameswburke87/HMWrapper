"""Tests for BookingsAPI."""

import responses

from hmwrapper.client import HallmasterClient
from hmwrapper.bookings import BookingsAPI


class TestBookingsAPI:
    def test_list_bookings(self, mock_auth):
        mock_auth.add(
            responses.GET,
            "https://v2.hallmaster.co.uk/api/bookings/GetForHallgrid",
            json=[
                {
                    "BookingId": 1,
                    "BookingName": "Test",
                    "StartDateTime": "2026-03-22T10:00:00",
                    "EndDateTime": "2026-03-22T12:00:00",
                    "Status": "Confirmed",
                    "CustomerName": "John",
                    "CustomerId": "abc",
                    "RoomsUsed": "Hall",
                    "ActivityType": "Meeting",
                    "IsRecurring": False,
                }
            ],
            status=200,
        )
        client = HallmasterClient(email="test@example.com", password="pw", hall_id=1234)
        api = BookingsAPI(client)
        bookings = api.list_bookings(status="Confirmed")
        assert len(bookings) == 1
        assert bookings[0].name == "Test"
        assert bookings[0].status == "Confirmed"
        client.close()

    def test_list_bookings_wrapped_response(self, mock_auth):
        mock_auth.add(
            responses.GET,
            "https://v2.hallmaster.co.uk/api/bookings/GetForHallgrid",
            json={"Data": [{"BookingId": 2, "BookingName": "Wrapped"}]},
            status=200,
        )
        client = HallmasterClient(email="test@example.com", password="pw", hall_id=1234)
        api = BookingsAPI(client)
        bookings = api.list_bookings()
        assert len(bookings) == 1
        assert bookings[0].id == 2
        client.close()

    def test_get_booking_counts(self, mock_auth):
        mock_auth.add(
            responses.GET,
            "https://v2.hallmaster.co.uk/api/Bookings/GetBookingCountsForHall",
            json={"Confirmed": 10, "Requested": 3},
            status=200,
        )
        client = HallmasterClient(email="test@example.com", password="pw", hall_id=1234)
        api = BookingsAPI(client)
        counts = api.get_booking_counts()
        assert counts["Confirmed"] == 10
        client.close()
