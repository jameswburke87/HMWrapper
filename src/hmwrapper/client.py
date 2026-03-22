"""Core Hallmaster session client with authentication and request helpers."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Optional

import requests
from bs4 import BeautifulSoup

from .exceptions import APIError, AuthError, RateLimitError, TokenError


class HallmasterClient:
    """Authenticated HTTP client for the Hallmaster internal API.

    Handles login, session persistence, and anti-forgery token management.

    Credentials can be provided directly or via environment variables:
        HM_EMAIL, HM_PASSWORD, HM_HALL_ID

    Supports use as a context manager::

        with HallmasterClient() as client:
            bookings = BookingsAPI(client)
            ...
    """

    BASE = "https://v2.hallmaster.co.uk"

    def __init__(
        self,
        email: str | None = None,
        password: str | None = None,
        hall_id: int | None = None,
        session_file: str | None = None,
        base_url: str | None = None,
        max_retries: int = 3,
        retry_backoff: float = 1.0,
    ):
        self.email = email or os.environ.get("HM_EMAIL")
        _password = password or os.environ.get("HM_PASSWORD")
        _hall_id = hall_id or os.environ.get("HM_HALL_ID")

        if not self.email or not _password:
            raise AuthError(
                "Credentials required. Pass email/password or set HM_EMAIL/HM_PASSWORD."
            )
        if not _hall_id:
            raise AuthError(
                "Hall ID required. Pass hall_id or set HM_HALL_ID."
            )

        self.hall_id = int(_hall_id)
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff

        if base_url:
            self.BASE = base_url

        self.session = requests.Session()
        self.session.headers["User-Agent"] = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
        self._token_cache: Optional[str] = None
        self._session_file = Path(session_file) if session_file else None

        if self._session_file and self._session_file.exists():
            self._load_session()
            if not self._is_authenticated():
                self._login(_password)
        else:
            self._login(_password)

    def __enter__(self) -> HallmasterClient:
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    def __repr__(self) -> str:
        return f"HallmasterClient(email={self.email!r}, hall_id={self.hall_id})"

    def close(self) -> None:
        """Close the underlying HTTP session."""
        self.session.close()

    def _login(self, password: str) -> None:
        """Authenticate via the login form."""
        r = self.session.get(f"{self.BASE}/Account/Login")
        r.raise_for_status()

        token = self._extract_token(r.text)

        r = self.session.post(
            f"{self.BASE}/Account/Login",
            data={
                "Email": self.email,
                "Password": password,
                "__RequestVerificationToken": token,
            },
            allow_redirects=True,
        )
        r.raise_for_status()

        if "/Account/Login" in r.url:
            raise AuthError("Login failed — check email/password")

        self._token_cache = None
        if self._session_file:
            self._save_session()

    def _is_authenticated(self) -> bool:
        """Check if the current session is still valid."""
        try:
            r = self.session.get(
                f"{self.BASE}/api/Scheduler/HasJustLoggedIn",
                allow_redirects=False,
            )
            return r.status_code == 200
        except requests.RequestException:
            return False

    def _extract_token(self, html: str) -> str:
        """Extract __RequestVerificationToken from HTML."""
        soup = BeautifulSoup(html, "html.parser")
        tag = soup.find("input", {"name": "__RequestVerificationToken"})
        if not tag or not tag.get("value"):
            raise TokenError("Could not find anti-forgery token in page")
        return tag["value"]

    def _get_token(self) -> str:
        """Get a fresh anti-forgery token for POST requests."""
        r = self.session.get(f"{self.BASE}/Admin/Dashboard/Index/{self.hall_id}")
        r.raise_for_status()
        return self._extract_token(r.text)

    def _save_session(self) -> None:
        """Persist session cookies to disk as JSON."""
        if self._session_file:
            self._session_file.parent.mkdir(parents=True, exist_ok=True)
            cookies = [
                {"name": c.name, "value": c.value, "domain": c.domain, "path": c.path}
                for c in self.session.cookies
            ]
            self._session_file.write_text(json.dumps(cookies, indent=2))

    def _load_session(self) -> None:
        """Load session cookies from disk."""
        if self._session_file and self._session_file.exists():
            try:
                cookies = json.loads(self._session_file.read_text())
                for c in cookies:
                    self.session.cookies.set(
                        c["name"], c["value"], domain=c.get("domain", ""), path=c.get("path", "/")
                    )
            except (json.JSONDecodeError, KeyError):
                pass

    def _request_with_retry(self, method: str, url: str, **kwargs: Any) -> requests.Response:
        """Make an HTTP request with retry logic for rate limits and server errors."""
        attempts = max(self.max_retries, 1)
        last_exc: Exception | None = None
        for attempt in range(attempts):
            try:
                r = self.session.request(method, url, **kwargs)
                if r.status_code == 429:
                    if attempt < attempts - 1:
                        time.sleep(self.retry_backoff * (2 ** attempt))
                        continue
                    raise RateLimitError(
                        f"Rate limited after {attempts} attempts",
                        status_code=429,
                        response=r,
                    )
                if r.status_code >= 500 and attempt < attempts - 1:
                    time.sleep(self.retry_backoff * (2 ** attempt))
                    continue
                return r
            except requests.ConnectionError as e:
                last_exc = e
                if attempt < attempts - 1:
                    time.sleep(self.retry_backoff * (2 ** attempt))
                    continue
                raise
        raise last_exc  # type: ignore[misc]

    def get(self, path: str, **kwargs: Any) -> Any:
        """GET request, returning parsed JSON."""
        r = self._request_with_retry("GET", f"{self.BASE}{path}", **kwargs)
        r.raise_for_status()
        try:
            return r.json()
        except ValueError:
            raise APIError(
                f"Non-JSON response from GET {path}",
                status_code=r.status_code,
                response=r,
            )

    def get_html(self, path: str, **kwargs: Any) -> str:
        """GET request, returning raw HTML text."""
        r = self._request_with_retry("GET", f"{self.BASE}{path}", **kwargs)
        r.raise_for_status()
        return r.text

    def post(self, path: str, **kwargs: Any) -> requests.Response:
        """POST request with automatic anti-forgery token."""
        token = self._get_token()
        headers = kwargs.pop("headers", {})
        headers["RequestVerificationToken"] = token
        r = self._request_with_retry(
            "POST", f"{self.BASE}{path}", headers=headers, **kwargs
        )
        r.raise_for_status()
        return r

    def post_form(self, path: str, data: dict, **kwargs: Any) -> requests.Response:
        """POST an MVC form with anti-forgery token embedded in form data."""
        token = self._get_token()
        data = {**data, "__RequestVerificationToken": token}
        r = self._request_with_retry("POST", f"{self.BASE}{path}", data=data, **kwargs)
        r.raise_for_status()
        return r
