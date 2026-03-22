"""Tests for data models."""

from hmwrapper.models import Booking, Customer, Room, SchedulerEvent, ActivityType, PriceRate


class TestRoom:
    def test_from_api(self):
        data = {"ID": 1, "Name": "Main Hall", "HallId": 1234, "rowNumber": 0, "Description": "Large hall"}
        room = Room.from_api(data)
        assert room.id == 1
        assert room.name == "Main Hall"
        assert room.hall_id == 1234

    def test_str(self):
        room = Room(id=1, name="Main Hall", hall_id=1234)
        assert str(room) == "Main Hall (id=1)"

    def test_to_dict(self):
        room = Room(id=1, name="Main Hall", hall_id=1234)
        d = room.to_dict()
        assert d["id"] == 1
        assert d["name"] == "Main Hall"


class TestBooking:
    def test_from_api_grid_format(self):
        data = {
            "BookingId": 42,
            "BookingName": "Test Event",
            "StartDateTime": "2026-03-22T10:00:00",
            "EndDateTime": "2026-03-22T12:00:00",
            "Status": "Confirmed",
            "CustomerName": "John Doe",
            "CustomerId": "abc-123",
            "RoomsUsed": "Main Hall",
            "ActivityType": "Meeting",
            "IsRecurring": False,
        }
        b = Booking.from_api(data)
        assert b.id == 42
        assert b.name == "Test Event"
        assert b.status == "Confirmed"
        assert b.customer_name == "John Doe"

    def test_from_api_scheduler_format(self):
        data = {
            "id": 42,
            "title": "Test Event",
            "start": "2026-03-22T10:00:00",
            "end": "2026-03-22T12:00:00",
            "color": "#ff0000",
        }
        b = Booking.from_api(data)
        assert b.id == 42
        assert b.name == "Test Event"

    def test_str(self):
        b = Booking(id=1, name="Meeting", start="10:00", end="12:00", status="Confirmed")
        assert "Meeting" in str(b)
        assert "Confirmed" in str(b)

    def test_to_dict_excludes_raw(self):
        b = Booking(id=1, name="Test", raw={"lots": "of data"})
        d = b.to_dict()
        assert "raw" not in d
        assert d["id"] == 1


class TestCustomer:
    def test_from_api(self):
        data = {
            "UserId": "guid-123",
            "Name": "Jane Doe",
            "Email": "jane@example.com",
            "Phone": "01onal234",
            "Organisation": "Test Org",
            "IsBlocked": False,
        }
        c = Customer.from_api(data)
        assert c.id == "guid-123"
        assert c.name == "Jane Doe"
        assert c.organisation == "Test Org"

    def test_str_with_org(self):
        c = Customer(id="1", name="Jane", organisation="Acme")
        assert str(c) == "Jane (Acme)"

    def test_str_without_org(self):
        c = Customer(id="1", name="Jane")
        assert str(c) == "Jane"


class TestSchedulerEvent:
    def test_from_api(self):
        data = {
            "id": 10,
            "title": "Yoga Class",
            "start": "2026-03-22T09:00:00",
            "end": "2026-03-22T10:00:00",
            "color": "#00ff00",
            "allDay": False,
            "RoomsUsed": "Studio",
        }
        e = SchedulerEvent.from_api(data)
        assert e.id == 10
        assert e.title == "Yoga Class"
        assert e.rooms_used == "Studio"


class TestActivityType:
    def test_from_api(self):
        data = {"Id": 5, "Name": "Community Event", "HallId": 1234}
        at = ActivityType.from_api(data)
        assert at.id == 5
        assert str(at) == "Community Event"


class TestPriceRate:
    def test_from_api(self):
        data = {"Id": 3, "Name": "Standard Rate", "HallId": 1234}
        pr = PriceRate.from_api(data)
        assert pr.id == 3
        assert str(pr) == "Standard Rate"
