"""Rooms API — list rooms, descriptions, and color-to-room mapping."""

from __future__ import annotations

import re
from typing import Any

from bs4 import BeautifulSoup

from .client import HallmasterClient
from .models import Room

_BG_COLOR_RE = re.compile(r"background-color:\s*([^;]+)")
_ROOM_ONCLICK_RE = re.compile(r"filterRoom\((\d+)\)")


def _normalise_color(color_str: str) -> str:
    """Convert color strings (hex or rgb) to normalized uppercase hex."""
    if not color_str:
        return ""
    color_str = color_str.strip()
    if color_str.startswith("#"):
        return color_str.upper()
    if color_str.lower().startswith("rgb"):
        try:
            inside = color_str[color_str.index("(") + 1 : color_str.index(")")]
            r, g, b = [int(v.strip()) for v in inside.split(",")[:3]]
            return f"#{r:02X}{g:02X}{b:02X}"
        except (ValueError, IndexError):
            return ""
    return color_str.upper()


class RoomsAPI:
    """Interface to Hallmaster room endpoints."""

    def __init__(self, client: HallmasterClient):
        self.client = client
        self.hall_id = client.hall_id
        self._room_cache: dict[int, Room] | None = None
        self._color_map: dict[str, str] | None = None

    def list_rooms(self) -> list[Room]:
        """Get rooms available for booking."""
        data = self.client.get(
            "/api/Rooms/GetForHallForBooking",
            params={"hallid": self.hall_id},
        )
        rows = data if isinstance(data, list) else data.get("Data", data.get("data", []))
        rooms = [Room.from_api(row) for row in rows]
        self._room_cache = {r.id: r for r in rooms}
        return rooms

    def list_rooms_grid(self) -> list[Room]:
        """Get rooms from the admin grid endpoint."""
        data = self.client.get(
            "/api/rooms/GetForHallGrid",
            params={"id": self.hall_id},
        )
        rows = data if isinstance(data, list) else data.get("Data", data.get("data", []))
        return [Room.from_api(row) for row in rows]

    def get_descriptions(self) -> Any:
        """Get room descriptions."""
        return self.client.get("/api/rooms/getroomdescriptions")

    def get_room_lookup(self) -> dict[int, str]:
        """Build a {room_id: room_name} lookup dict.

        Fetches rooms if not already cached.
        """
        if self._room_cache is None:
            self.list_rooms()
        return {rid: room.name for rid, room in (self._room_cache or {}).items()}

    def get_color_map(self) -> dict[str, str]:
        """Build a {color_hex: room_name} mapping from the scheduler page.

        HallMaster identifies rooms by CSS color in scheduler/booking views.
        This scrapes the scheduler HTML to extract the color-to-room mapping.

        Returns:
            Dict mapping normalized uppercase hex colors (e.g. "#FF6600")
            to room names (e.g. "Main Hall").
        """
        if self._color_map is not None:
            return self._color_map

        html = self.client.get_html(f"/Scheduler/View/{self.hall_id}")
        soup = BeautifulSoup(html, "html.parser")
        color_map: dict[str, str] = {}

        for label in soup.select("#RoomColorList .room-label"):
            style = label.get("style", "")
            bg_match = _BG_COLOR_RE.search(style)
            if not bg_match:
                continue
            color = _normalise_color(bg_match.group(1).strip())
            if color:
                color_map[color] = label.text.strip()

        self._color_map = color_map
        return color_map

    def resolve_room(self, color: str) -> str:
        """Resolve a booking color to a room name.

        Args:
            color: Hex color string from a booking/event (e.g. "#ff6600").

        Returns:
            Room name, or "Unknown Room" if no match.
        """
        color_map = self.get_color_map()
        return color_map.get(_normalise_color(color), "Unknown Room")
