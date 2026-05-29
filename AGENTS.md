# AGENTS

Guidance for agents working on `pyromhacking`.

## What this is

A typed scraper client for romhacking.net (RHDN). Four sections (`hacks`,
`translations`, `utilities`, `documents`) share one detail and one listing
skeleton, so a single parser and a single listing module cover all four.

## Layout

| Path | Role |
| --- | --- |
| `pyromhacking/__init__.py` | public API surface (`__all__`) |
| `pyromhacking/transport.py` | `unblock_requests.CloudflareSession` via FlareSolverr |
| `pyromhacking/_clean.py` | string-cleaning + id/number extraction helpers |
| `pyromhacking/_parse.py` | BeautifulSoup parsing of detail + listing pages |
| `pyromhacking/models.py` | typed dataclasses (`Hack`, `Translation`, ...) |
| `pyromhacking/hacks.py` | listing enumeration + detail fetch (entity module) |
| `pyromhacking/ids.py` | `ExternalIds.extra` converters; anchor + ref parsing |
| `pyromhacking/dataset.py` | HF JSONL builders (4 configs, `export_jsonl`) |
| `docs/` | per-topic documentation |
| `examples/` | runnable scripts |
| `tests/` | offline fixture tests + a live smoke test (`-m live`) |

## Hard rules

- **FlareSolverr is mandatory.** All HTTP goes through `transport`; never add a
  bare `requests`/`curl_cffi` path. The endpoint is `PYROMHACKING_FLARESOLVERR_URL`.
- Keep the parser **page-structure tolerant**: RHDN reuses the
  `newsitem`/`topbar` skeleton for sidebar chrome, so the content entry is
  identified as the `newsitem` wrapping the `entryinfo` table — not the first one.
- New fields go on the model **and** its `.as_dict`, the matching `*_to_extra`
  converter, and `docs/models.md`.
- Be polite: respect the transport throttle; bulk crawls are homelab jobs.

## Testing

```bash
pytest -m "not live"
PYROMHACKING_FLARESOLVERR_URL=http://192.168.1.116:8191 pytest -m live
```

Offline fixtures live in `tests/fixtures/`. Re-capture them with the transport
when the site markup changes; keep one fixture per section.

## TODO

CI wiring (`gh-automations` reusable workflows) is intentionally absent — see
[TODO.md](TODO.md).
