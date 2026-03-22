"""HMWrapper — Python client for the HallMaster venue booking API.

Usage::

    from hmwrapper import HallmasterClient, BookingsAPI, CustomersAPI

    client = HallmasterClient()  # reads HM_EMAIL, HM_PASSWORD, HM_HALL_ID from env
    bookings = BookingsAPI(client)
    for b in bookings.list_bookings(status="Confirmed"):
        print(b.name, b.start, b.end)
"""

from ._version import __version__
from .admin import AdminAPI
from .bookings import BookingsAPI
from .client import HallmasterClient
from .customers import CustomersAPI
from .exceptions import APIError, AuthError, HallmasterError, RateLimitError, TokenError
from .models import (
    ActivityType,
    Booking,
    Customer,
    PriceRate,
    Room,
    SchedulerEvent,
)
from .rooms import RoomsAPI
from .scheduler import SchedulerAPI

__all__ = [
    "__version__",
    "HallmasterClient",
    "BookingsAPI",
    "CustomersAPI",
    "SchedulerAPI",
    "RoomsAPI",
    "AdminAPI",
    "Booking",
    "Customer",
    "Room",
    "SchedulerEvent",
    "ActivityType",
    "PriceRate",
    "HallmasterError",
    "AuthError",
    "TokenError",
    "APIError",
    "RateLimitError",
]
