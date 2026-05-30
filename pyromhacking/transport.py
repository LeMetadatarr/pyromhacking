"""HTTP transport for romhacking.net via FlareSolverr.

romhacking.net sits behind Cloudflare. A bare HTTP client (including
``curl_cffi`` impersonation) receives an interactive Cloudflare challenge and
never reaches the content. The site is reliably cleared by routing requests
through a FlareSolverr instance.

The transport uses :class:`unblock_requests.CloudflareSession` with
``env_prefix="PYROMHACKING"``. The FlareSolverr endpoint is supplied either as
an explicit kwarg or via the ``PYROMHACKING_FLARESOLVERR_URL`` environment
variable. FlareSolverr is **required**: without it requests resolve to a
Cloudflare challenge page rather than entry data.

Example::

    export PYROMHACKING_FLARESOLVERR_URL=http://localhost:8191
"""
from __future__ import annotations

import os
import time
from typing import Any, Optional

BASE_URL = "https://www.romhacking.net"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": BASE_URL + "/",
}

_session: Optional[Any] = None
_last_request: float = 0.0
_min_delay: float = 2.0


def set_delay(seconds: float) -> None:
    """Set the minimum delay between HTTP requests (default: 2.0 s)."""
    global _min_delay
    _min_delay = max(0.0, seconds)


def _make_session() -> Any:
    from unblock_requests import CloudflareSession

    flaresolverr_url = os.environ.get("PYROMHACKING_FLARESOLVERR_URL", "").strip()
    session = CloudflareSession(
        flaresolverr_url=flaresolverr_url or None,
        env_prefix="PYROMHACKING",
        wayback_fallback=True,
    )
    session.headers.update(_HEADERS)
    return session


def get_session() -> Any:
    """Return the shared, lazily created CloudflareSession."""
    global _session
    if _session is None:
        _session = _make_session()
    return _session


def reset_session() -> None:
    """Drop the cached session so the next call rebuilds it."""
    global _session
    _session = None


def _throttle() -> None:
    global _last_request
    elapsed = time.time() - _last_request
    if elapsed < _min_delay:
        time.sleep(_min_delay - elapsed)
    _last_request = time.time()


def get_html(path: str, params: Optional[dict] = None, **kwargs: Any) -> str:
    """Fetch a page and return the HTML text.

    Args:
        path: Absolute URL or path relative to :data:`BASE_URL`.
        params: Optional query-string parameters.

    Returns:
        Response body as a string.
    """
    _throttle()
    url = path if path.startswith("http") else f"{BASE_URL}{path}"
    resp = get_session().get(url, params=params, **kwargs)
    resp.raise_for_status()
    return resp.text
