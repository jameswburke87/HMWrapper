"""Shared test fixtures."""

import pytest
import responses

LOGIN_HTML = """
<html><body>
<form>
<input name="__RequestVerificationToken" value="test-token-123" />
</form>
</body></html>
"""

DASHBOARD_HTML = """
<html><body>
<form>
<input name="__RequestVerificationToken" value="fresh-token-456" />
</form>
</body></html>
"""


@pytest.fixture
def mock_auth():
    """Set up mocked authentication flow."""
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        # Login page GET
        rsps.add(
            responses.GET,
            "https://v2.hallmaster.co.uk/Account/Login",
            body=LOGIN_HTML,
            status=200,
        )
        # Login POST — redirect to dashboard
        rsps.add(
            responses.POST,
            "https://v2.hallmaster.co.uk/Account/Login",
            status=302,
            headers={"Location": "/Admin/Dashboard"},
        )
        rsps.add(
            responses.GET,
            "https://v2.hallmaster.co.uk/Admin/Dashboard",
            body="<html>Dashboard</html>",
            status=200,
        )
        # Dashboard for token refresh
        rsps.add(
            responses.GET,
            "https://v2.hallmaster.co.uk/Admin/Dashboard/Index/1234",
            body=DASHBOARD_HTML,
            status=200,
        )
        yield rsps
