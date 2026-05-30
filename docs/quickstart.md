# Quickstart

`pyromhacking` is a typed client for [romhacking.net](https://www.romhacking.net)
(RHDN): ROM hacks, fan translations, patching utilities, and documents.

## Install

```bash
pip install -e .
```

Dependencies: `requests`, `beautifulsoup4`, `unblock_requests`.

## FlareSolverr is required

romhacking.net sits behind Cloudflare. Every request is routed through a
[FlareSolverr](https://github.com/FlareSolverr/FlareSolverr) instance; without
one, requests resolve to a Cloudflare challenge page instead of entry data.

Point the client at your instance:

```bash
export PYROMHACKING_FLARESOLVERR_URL=http://localhost:8191
```

## Fetch an entry

```python
from pyromhacking import get_hack, get_translation

hack = get_hack("1")
print(hack.title)        # Dragoon X Omega - Gold Edition
print(hack.game)         # Dragon Warrior
print(hack.system)       # NES
print(hack.downloads)    # 6523

tr = get_translation("1")
print(tr.title, tr.language)
```

## Enumerate a section

```python
from pyromhacking import list_hacks, iter_ids

print(list_hacks())                       # one listing page of ids
for entry_id in iter_ids("hacks", max_pages=2):
    print(entry_id)
```

See [transport.md](transport.md), [models.md](models.md), [listing.md](listing.md),
[ids.md](ids.md), and [dataset.md](dataset.md).
