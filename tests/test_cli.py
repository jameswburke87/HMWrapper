"""Tests for CLI commands."""

import responses
from click.testing import CliRunner

from hmwrapper.cli import main

LOGIN_HTML = '<input name="__RequestVerificationToken" value="test-token" />'

SCHEDULER_HTML = """<html><body>
<div id="RoomColorList">
  <span class="room-label" style="background-color: #FF6600;"
        onclick="filterRoom(1)">Main Hall</span>
  <span class="room-label" style="background-color: rgb(0, 128, 0);"
        onclick="filterRoom(2)">Studio</span>
</div>
</body></html>"""


def _setup_auth(rsps):
    """Register mock auth responses."""
    rsps.add(responses.GET, "https://v2.hallmaster.co.uk/Account/Login", body=LOGIN_HTML, status=200)
    rsps.add(
        responses.POST,
        "https://v2.hallmaster.co.uk/Account/Login",
        status=302,
        headers={"Location": "/Admin/Dashboard"},
    )
    rsps.add(responses.GET, "https://v2.hallmaster.co.uk/Admin/Dashboard", body="OK", status=200)
    rsps.add(
        responses.GET,
        "https://v2.hallmaster.co.uk/Admin/Dashboard/Index/1234",
        body=LOGIN_HTML,
        status=200,
    )
    rsps.add(
        responses.GET,
        "https://v2.hallmaster.co.uk/Scheduler/View/1234",
        body=SCHEDULER_HTML,
        status=200,
    )


class TestLoginCommand:
    @responses.activate
    def test_login_success(self):
        _setup_auth(responses)
        runner = CliRunner()
        result = runner.invoke(
            main,
            ["--email", "test@example.com", "--password", "pw", "--hall-id", "1234", "login"],
        )
        assert result.exit_code == 0
        assert "Logged in" in result.output


class TestBookingsCommand:
    @responses.activate
    def test_list_table(self):
        _setup_auth(responses)
        responses.add(
            responses.GET,
            "https://v2.hallmaster.co.uk/api/bookings/GetForHallgrid",
            json=[{"BookingId": 1, "BookingName": "Test Event", "Status": "Confirmed"}],
            status=200,
        )
        runner = CliRunner()
        result = runner.invoke(
            main,
            ["--email", "t@e.com", "--password", "pw", "--hall-id", "1234", "bookings", "list"],
        )
        assert result.exit_code == 0
        assert "Test Event" in result.output

    @responses.activate
    def test_list_json(self):
        _setup_auth(responses)
        responses.add(
            responses.GET,
            "https://v2.hallmaster.co.uk/api/bookings/GetForHallgrid",
            json=[{"BookingId": 1, "BookingName": "Test"}],
            status=200,
        )
        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "--email", "t@e.com", "--password", "pw", "--hall-id", "1234",
                "bookings", "list", "--format", "json",
            ],
        )
        assert result.exit_code == 0
        assert '"id": 1' in result.output
