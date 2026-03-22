"""Dataclasses for typed Hallmaster API responses."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Optional


@dataclass
class Room:
    id: int
    name: str
    hall_id: int
    row_number: int = 0
    description: str = ""

    @classmethod
    def from_api(cls, data: dict) -> Room:
        return cls(
            id=data.get("ID") or data.get("Id", 0),
            name=data.get("Name", ""),
            hall_id=data.get("HallId", 0),
            row_number=data.get("rowNumber", 0),
            description=data.get("Description", ""),
        )

    def __str__(self) -> str:
        return f"{self.name} (id={self.id})"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Booking:
    id: int
    name: str
    start: Optional[str] = None
    end: Optional[str] = None
    status: str = ""
    customer_name: str = ""
    customer_id: str = ""
    rooms_used: str = ""
    activity_type: str = ""
    is_recurring: bool = False
    color: str = ""
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict) -> Booking:
        # rooms_used can be a string, list, or missing depending on endpoint
        rooms_raw = (
            data.get("RoomsDisplayFormat")
            or data.get("RoomsUsed")
            or data.get("rooms_used")
            or ""
        )
        if isinstance(rooms_raw, list):
            rooms_raw = ", ".join(str(r) for r in rooms_raw) if rooms_raw else ""

        return cls(
            id=(
                data.get("BookingId")
                or data.get("ID")
                or data.get("Id")
                or data.get("id", 0)
            ),
            name=(
                data.get("BookingName")
                or data.get("Name")
                or data.get("title", "")
            ),
            start=(
                data.get("StartDateTime")
                or data.get("StartDate")
                or data.get("start")
            ),
            end=(
                data.get("EndDateTime")
                or data.get("EndDate")
                or data.get("end")
            ),
            status=(
                data.get("Status")
                or data.get("BookingStatusId", "")
            ),
            customer_name=data.get("CustomerName", ""),
            customer_id=data.get("CustomerId", ""),
            rooms_used=rooms_raw,
            activity_type=data.get("ActivityType", ""),
            is_recurring=(
                data.get("IsRecurring")
                or data.get("IsRecurringBooking", False)
            ),
            color=data.get("color", ""),
            raw=data,
        )

    def __str__(self) -> str:
        return f"{self.name} ({self.start} → {self.end}) [{self.status}]"

    def to_dict(self) -> dict:
        d = asdict(self)
        d.pop("raw", None)
        return d


@dataclass
class Customer:
    id: str
    name: str
    email: str = ""
    phone: str = ""
    organisation: str = ""
    is_blocked: bool = False
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict) -> Customer:
        return cls(
            id=data.get("UserId") or data.get("ID") or data.get("Id", ""),
            name=data.get("Name") or data.get("FullName", ""),
            email=data.get("Email", ""),
            phone=data.get("Phone") or data.get("PhoneNumber", ""),
            organisation=data.get("Organisation", ""),
            is_blocked=data.get("IsBlocked", False),
            raw=data,
        )

    def __str__(self) -> str:
        org = f" ({self.organisation})" if self.organisation else ""
        return f"{self.name}{org}"

    def to_dict(self) -> dict:
        d = asdict(self)
        d.pop("raw", None)
        return d


@dataclass
class SchedulerEvent:
    id: int
    title: str
    start: str
    end: str
    color: str = ""
    all_day: bool = False
    rooms_used: str = ""
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict) -> SchedulerEvent:
        rooms_raw = data.get("RoomsUsed") or data.get("rooms_used") or ""
        if isinstance(rooms_raw, list):
            rooms_raw = ", ".join(str(r) for r in rooms_raw) if rooms_raw else ""

        return cls(
            id=data.get("id") or data.get("Id") or data.get("ID", 0),
            title=data.get("title", ""),
            start=data.get("start", ""),
            end=data.get("end", ""),
            color=data.get("color", ""),
            all_day=data.get("allDay", False),
            rooms_used=rooms_raw,
            raw=data,
        )

    def __str__(self) -> str:
        return f"{self.title} ({self.start} → {self.end})"

    def to_dict(self) -> dict:
        d = asdict(self)
        d.pop("raw", None)
        return d


@dataclass
class ActivityType:
    id: int
    name: str
    hall_id: int = 0
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict) -> ActivityType:
        return cls(
            id=data.get("ID") or data.get("Id", 0),
            name=data.get("Name", ""),
            hall_id=data.get("HallId", 0),
            raw=data,
        )

    def __str__(self) -> str:
        return self.name

    def to_dict(self) -> dict:
        d = asdict(self)
        d.pop("raw", None)
        return d


@dataclass
class PriceRate:
    id: int
    name: str
    hall_id: int = 0
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict) -> PriceRate:
        return cls(
            id=data.get("ID") or data.get("Id", 0),
            name=data.get("Name", ""),
            hall_id=data.get("HallId", 0),
            raw=data,
        )

    def __str__(self) -> str:
        return self.name

    def to_dict(self) -> dict:
        d = asdict(self)
        d.pop("raw", None)
        return d
