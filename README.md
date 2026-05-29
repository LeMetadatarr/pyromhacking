# pyromhacking

Python scraper / API client for [romhacking.net](https://www.romhacking.net)
(RHDN) — the community database of ROM hacks, fan translations, patching
utilities, and documentation.

It returns typed dataclasses for the four catalogued sections, enumerates their
listing pages, and exports HF-publishable datasets.

## FlareSolverr required

romhacking.net is behind Cloudflare. Every request is routed through a
[FlareSolverr](https://github.com/FlareSolverr/FlareSolverr) instance — without
one, requests resolve to a challenge page rather than data.

```bash
export PYROMHACKING_FLARESOLVERR_URL=http://192.168.1.116:8191
```

## Install

```bash
pip install -e .
```

## Usage

```python
from pyromhacking import get_hack, list_hacks, iter_entries

hack = get_hack("1")
print(hack.title, hack.game, hack.system, hack.downloads)

for entry_id in list_hacks():
    print(entry_id)

for h in iter_entries("hacks", max_pages=2):
    print(h)
```

### Sections

`hacks`, `translations`, `utilities`, `documents` — fetched with
`get_hack` / `get_translation` / `get_utility` / `get_document` or the generic
`get_entry(section, id)`.

### Dataset export

```bash
python -m pyromhacking.dataset all --out romhacking_dataset --limit 5
```

## Documentation

- [Quickstart](docs/quickstart.md)
- [Transport / FlareSolverr](docs/transport.md)
- [Models](docs/models.md)
- [Listing & fetch](docs/listing.md)
- [Cross-reference ids](docs/ids.md)
- [Dataset](docs/dataset.md)

See [`examples/`](examples) for runnable scripts and [PROVENANCE.md](PROVENANCE.md)
for data provenance.

## Tests

```bash
pytest -m "not live"     # offline, fixture-based
PYROMHACKING_FLARESOLVERR_URL=... pytest -m live   # live smoke
```

## License

Apache-2.0. Scraped content is © the romhacking.net community.
