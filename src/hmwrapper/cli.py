"""CLI tool for common HallMaster operations."""

from __future__ import annotations

import json
import sys
from datetime import datetime

try:
    import click
except ImportError:
    print("CLI requires click: pip install hmwrapper[cli]", file=sys.stderr)
    sys.exit(1)

from .client import HallmasterClient
from .exceptions import HallmasterError


def _get_client(**kwargs) -> HallmasterClient:
    """Create a client from CLI options or environment variables."""
    opts = {k: v for k, v in kwargs.items() if v is not None}
    return HallmasterClient(**opts)


@click.group()
@click.option("--email", envvar="HM_EMAIL", help="Hallmaster email")
@click.option("--password", envvar="HM_PASSWORD", help="Hallmaster password")
@click.option("--hall-id", envvar="HM_HALL_ID", type=int, help="Hall ID")
@click.option("--session-file", default=None, help="Session file path")
@click.pass_context
def main(ctx, email, password, hall_id, session_file):
    """HMWrapper — interact with the HallMaster API."""
    ctx.ensure_object(dict)
    ctx.obj["client_opts"] = {
        "email": email,
        "password": password,
        "hall_id": hall_id,
        "session_file": session_file,
    }


@main.command()
@click.pass_context
def login(ctx):
    """Test authentication credentials."""
    try:
        client = _get_client(**ctx.obj["client_opts"])
        click.echo(f"Logged in as {client.email} (hall {client.hall_id})")
        client.close()
    except HallmasterError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.group()
def bookings():
    """Booking operations."""


@bookings.command("list")
@click.option("--status", default="All", help="Filter: All, Confirmed, Requested, Cancelled")
@click.option("--timerange", default=5, type=int, help="0=Today 1=7d 2=Mo 3=3mo 4=Yr 5=All")
@click.option("--format", "fmt", default="table", type=click.Choice(["table", "json"]))
@click.pass_context
def bookings_list(ctx, status, timerange, fmt):
    """List bookings."""
    try:
        from .bookings import BookingsAPI
        from .rooms import RoomsAPI

        client = _get_client(**ctx.obj["client_opts"])
        api = BookingsAPI(client)
        rooms_api = RoomsAPI(client)
        results = api.list_bookings(status=status, timerange=timerange)

        # Pre-fetch color-to-room map so resolve_room() uses cache
        rooms_api.get_color_map()

        if fmt == "json":
            out = []
            for b in results:
                d = b.to_dict()
                if b.color and not b.rooms_used:
                    d["rooms_used"] = rooms_api.resolve_room(b.color)
                out.append(d)
            click.echo(json.dumps(out, indent=2))
        else:
            click.echo(f"Found {len(results)} bookings:\n")
            for b in results:
                room = b.rooms_used or (rooms_api.resolve_room(b.color) if b.color else "")
                click.echo(f"  [{b.id}] {b.name}")
                click.echo(f"    {b.start} -> {b.end}  [{b.status}]")
                if room:
                    click.echo(f"    Room: {room}")
                if b.customer_name:
                    click.echo(f"    Customer: {b.customer_name}")
                click.echo()
        client.close()
    except HallmasterError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.group()
def rooms():
    """Room operations."""


@rooms.command("list")
@click.option("--format", "fmt", default="table", type=click.Choice(["table", "json"]))
@click.pass_context
def rooms_list(ctx, fmt):
    """List rooms."""
    try:
        from .rooms import RoomsAPI

        client = _get_client(**ctx.obj["client_opts"])
        api = RoomsAPI(client)
        results = api.list_rooms()

        if fmt == "json":
            click.echo(json.dumps([r.to_dict() for r in results], indent=2))
        else:
            click.echo(f"Found {len(results)} rooms:\n")
            for r in results:
                click.echo(f"  {r.id}: {r.name}")
        client.close()
    except HallmasterError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.group()
def calendar():
    """Calendar/scheduler operations."""


@calendar.command("export")
@click.option("--month", default=None, help="Month to export (YYYY-MM), default current")
@click.option("--output", "-o", default=None, help="Output file (default stdout)")
@click.pass_context
def calendar_export(ctx, month, output):
    """Export scheduler events as JSON."""
    try:
        from .rooms import RoomsAPI
        from .scheduler import SchedulerAPI

        client = _get_client(**ctx.obj["client_opts"])
        api = SchedulerAPI(client)
        rooms_api = RoomsAPI(client)
        rooms_api.get_color_map()

        if month:
            try:
                year, mon = map(int, month.split("-"))
            except ValueError:
                raise click.BadParameter(
                    f"Invalid month format: {month!r} (expected YYYY-MM)", param_hint="--month"
                )
        else:
            now = datetime.now()
            year, mon = now.year, now.month

        start = f"{year}-{mon:02d}-01T00:00:00Z"
        if mon == 12:
            end = f"{year + 1}-01-01T00:00:00Z"
        else:
            end = f"{year}-{mon + 1:02d}-01T00:00:00Z"

        events = api.get_bookings(start=start, end=end)
        out = []
        for e in events:
            d = e.to_dict()
            if e.color and not e.rooms_used:
                d["rooms_used"] = rooms_api.resolve_room(e.color)
            out.append(d)
        result = json.dumps(out, indent=2)

        if output:
            with open(output, "w") as f:
                f.write(result)
            click.echo(f"Exported {len(out)} events to {output}")
        else:
            click.echo(result)
        client.close()
    except HallmasterError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
