# Transport

All HTTP goes through `pyromhacking.transport`, which wraps
`unblock_requests.CloudflareSession` and routes every request through
FlareSolverr.

## Why FlareSolverr

romhacking.net serves an interactive Cloudflare challenge to bare HTTP
clients. Even `curl_cffi` impersonation does not clear it. A FlareSolverr
instance solves the challenge in a real browser and returns the resolved
HTML. FlareSolverr is mandatory for this client.

## Configuration

| Environment variable | Meaning |
| --- | --- |
| `PYROMHACKING_FLARESOLVERR_URL` | FlareSolverr endpoint, e.g. `http://localhost:8191` |

The transport uses `env_prefix="PYROMHACKING"`. Any other `unblock_requests`
knob is read from a `PYROMHACKING_*` variable.

```python
from pyromhacking import transport

transport.set_delay(3.0)        # minimum seconds between requests (default 2.0)
transport.reset_session()       # drop the cached session (e.g. after changing env)
```

## Politeness

A throttle enforces a minimum delay between requests (default 2.0s). Raise it
for bulk crawls with `set_delay`, or pass `--delay` to the dataset CLI.

## Wayback fallback

The session is created with `wayback_fallback=True`. If a live fetch fails,
it falls back to the Internet Archive snapshot where available.

---
[← Quickstart](quickstart.md) · [Home](../README.md) · [Models →](models.md)
