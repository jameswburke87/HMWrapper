"""Tests for the HallmasterClient."""

import json
import tempfile
from pathlib import Path

import pytest
import responses

from hmwrapper.client import HallmasterClient
from hmwrapper.exceptions import AuthError, TokenError


class TestClientAuth:
    def test_login_success(self, mock_auth):
        client = HallmasterClient(
            email="test@example.com",
            password="password",
            hall_id=1234,
        )
        assert client.email == "test@example.com"
        assert client.hall_id == 1234
        client.close()

    def test_missing_credentials(self):
        with pytest.raises(AuthError, match="Credentials required"):
            HallmasterClient()

    def test_missing_hall_id(self):
        with pytest.raises(AuthError, match="Hall ID required"):
            HallmasterClient(email="test@example.com", password="pass")

    def test_login_failure(self):
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                "https://v2.hallmaster.co.uk/Account/Login",
                body='<input name="__RequestVerificationToken" value="tok" />',
                status=200,
            )
            rsps.add(
                responses.POST,
                "https://v2.hallmaster.co.uk/Account/Login",
                status=200,
                # URL still contains /Account/Login = failed login
                headers={"Location": ""},
            )
            with pytest.raises(AuthError, match="Login failed"):
                HallmasterClient(email="bad@example.com", password="wrong", hall_id=1234)

    def test_context_manager(self, mock_auth):
        with HallmasterClient(
            email="test@example.com", password="password", hall_id=1234
        ) as client:
            assert client.hall_id == 1234

    def test_repr(self, mock_auth):
        client = HallmasterClient(email="test@example.com", password="password", hall_id=1234)
        assert "test@example.com" in repr(client)
        assert "1234" in repr(client)
        client.close()


class TestSessionPersistence:
    def test_save_and_load_session(self, mock_auth):
        with tempfile.TemporaryDirectory() as tmpdir:
            session_file = str(Path(tmpdir) / "session.json")
            client = HallmasterClient(
                email="test@example.com",
                password="password",
                hall_id=1234,
                session_file=session_file,
            )
            client.close()

            # Verify session file is valid JSON
            data = json.loads(Path(session_file).read_text())
            assert isinstance(data, list)


class TestGetRequest:
    def test_get_json(self, mock_auth):
        mock_auth.add(
            responses.GET,
            "https://v2.hallmaster.co.uk/api/test",
            json={"Data": [{"id": 1}]},
            status=200,
        )
        client = HallmasterClient(email="test@example.com", password="password", hall_id=1234)
        result = client.get("/api/test")
        assert result == {"Data": [{"id": 1}]}
        client.close()
